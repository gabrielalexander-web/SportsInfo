"""
SportsInfo — plataforma web de información deportiva.
Backend: Flask + Jinja2 + Supabase (PostgreSQL en la nube).

Nombres de funciones y variables en español, snake_case, según el
estándar de codificación acordado por el equipo (ver documentación).

Cubre las 6 historias de usuario:
  HU1 Comparador de deportes
  HU2 Recomendación personalizada de deporte
  HU3 Calculadora de calorías por nivel + registro de alimentación
  HU4 Cálculo del costo de practicar un deporte
  HU5 Planificación del tiempo de entrenamiento
  HU6 Perfil deportivo personalizado
"""
import os
import base64
import io

from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from PIL import Image

from supabase_client import supabase
from auth import hash_password, verify_password, get_current_user, login_required
from iconos import icono_svg
from datos_deportes import DATOS_DEPORTES
from logica import (
    clasificar_imc, planificar_rutina, recomendar_deportes,
    calcular_costo, calcular_gasto_calorico, resumir_alimentos, NIVELES_CALORICOS,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-cambiame")

TABLA_DEPORTES = "sports"
TABLA_USUARIOS = "users"
TABLA_ENTRENAMIENTOS = "training_logs"
TABLA_COSTOS = "cost_estimates"

CAMPOS_PERFIL = ["age", "weight", "height", "experience_level", "goal", "budget_monthly", "available_days", "available_hours"]


# ---------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------
def hay_conexion_supabase():
    """Verifica la conexión con Supabase y muestra un mensaje si falla."""
    if supabase is None:
        flash("No hay conexión con Supabase. Revisa tu archivo .env (SUPABASE_URL y SUPABASE_KEY).", "error")
        return False
    return True


@app.context_processor
def inyectar_usuario_actual():
    return {"current_user": get_current_user(), "icono_svg": icono_svg}


def perfil_esta_completo(usuario: dict) -> bool:
    if not usuario:
        return False
    return all(usuario.get(campo) not in (None, "") for campo in CAMPOS_PERFIL)


def obtener_deportes() -> list:
    """Obtiene todos los deportes del catálogo, ordenados por nombre."""
    if not hay_conexion_supabase():
        return []
    try:
        return supabase.table(TABLA_DEPORTES).select("*").order("name").execute().data or []
    except Exception as exc:
        flash(f"No se pudieron cargar los deportes: {exc}", "error")
        return []


def estimar_calorias_foto(imagen: Image.Image) -> dict:
    """Heurística simple sin IA real — ver nota en camara-calorias.html."""
    miniatura = imagen.convert("RGB").resize((60, 60))
    pixeles = list(miniatura.getdata())
    n = len(pixeles)
    promedio_r = sum(p[0] for p in pixeles) / n
    promedio_g = sum(p[1] for p in pixeles) / n
    promedio_b = sum(p[2] for p in pixeles) / n
    brillo = (promedio_r + promedio_g + promedio_b) / 3
    kcal = int(250 + (brillo / 255) * 500)
    proteina = int(8 + (promedio_r / 255) * 25)
    carbohidratos = int(15 + (promedio_g / 255) * 55)
    grasas = int(5 + (promedio_b / 255) * 25)
    return {"kcal": kcal, "protein": proteina, "carbs": carbohidratos, "fat": grasas}


# ---------------------------------------------------------------
# DEPORTES (catálogo)
# ---------------------------------------------------------------
@app.route("/")
def index():
    """Muestra el catálogo de deportes con búsqueda y filtros."""
    texto_busqueda = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    genero = request.args.get("genero", "").strip()

    deportes, categorias = [], []
    if hay_conexion_supabase():
        try:
            consulta = supabase.table(TABLA_DEPORTES).select("*").order("name")
            if texto_busqueda:
                consulta = consulta.ilike("name", f"%{texto_busqueda}%")
            if categoria:
                consulta = consulta.eq("category", categoria)
            if genero:
                consulta = consulta.eq("gender", genero)
            deportes = consulta.execute().data or []
            todas = supabase.table(TABLA_DEPORTES).select("category").execute()
            categorias = sorted({fila["category"] for fila in todas.data if fila.get("category")})
        except Exception as exc:
            flash(f"Error al cargar los deportes: {exc}", "error")

    return render_template(
        "index.html", sports=deportes, categories=categorias,
        query_text=texto_busqueda, selected_category=categoria, selected_gender=genero,
    )


@app.route("/deporte/<int:sport_id>")
def detalle_deporte(sport_id):
    """Muestra la información completa de un deporte específico."""
    deporte = None
    if hay_conexion_supabase():
        try:
            deporte = supabase.table(TABLA_DEPORTES).select("*").eq("id", sport_id).single().execute().data
        except Exception as exc:
            flash(f"No se pudo cargar el deporte: {exc}", "error")
    if not deporte:
        flash("Deporte no encontrado.", "error")
        return redirect(url_for("index"))
    return render_template("detalle-deporte.html", sport=deporte)


def _leer_datos_formulario_deporte():
    """Lee y valida los campos del formulario de agregar/editar deporte."""
    return {
        "name": request.form.get("name", "").strip(),
        "category": request.form.get("category", "").strip(),
        "gender": request.form.get("gender", "Mixto").strip(),
        "description": request.form.get("description", "").strip(),
        "how_it_works": request.form.get("how_it_works", "").strip(),
        "average_cost": request.form.get("average_cost", "").strip(),
        "cost_score": int(request.form.get("cost_score", 3) or 3),
        "time_commitment": request.form.get("time_commitment", "").strip(),
        "time_score": int(request.form.get("time_score", 3) or 3),
        "funding_score": int(request.form.get("funding_score", 3) or 3),
        "difficulty_level": request.form.get("difficulty_level", "").strip(),
        "equipment_required": request.form.get("equipment_required", "").strip(),
        "physical_benefits": request.form.get("physical_benefits", "").strip(),
        "recommendations": request.form.get("recommendations", "").strip(),
        "diet_recommendations": request.form.get("diet_recommendations", "").strip(),
        "image_url": request.form.get("image_url", "").strip(),
    }


@app.route("/agregar", methods=["GET", "POST"])
@login_required
def agregar_deporte():
    """Agrega un nuevo deporte al catálogo."""
    if request.method == "POST":
        datos = _leer_datos_formulario_deporte()
        if not datos["name"]:
            flash("El nombre del deporte es obligatorio.", "error")
            return render_template("agregar-deporte.html", sport=datos)
        if hay_conexion_supabase():
            try:
                supabase.table(TABLA_DEPORTES).insert(datos).execute()
                flash(f'"{datos["name"]}" se agregó correctamente.', "success")
                return redirect(url_for("index"))
            except Exception as exc:
                flash(f"Error al guardar: {exc}", "error")
        return render_template("agregar-deporte.html", sport=datos)
    return render_template("agregar-deporte.html", sport={})


@app.route("/editar/<int:sport_id>", methods=["GET", "POST"])
@login_required
def editar_deporte(sport_id):
    """Edita un deporte existente del catálogo."""
    if not hay_conexion_supabase():
        return redirect(url_for("index"))
    if request.method == "POST":
        datos = _leer_datos_formulario_deporte()
        try:
            supabase.table(TABLA_DEPORTES).update(datos).eq("id", sport_id).execute()
            flash("Cambios guardados correctamente.", "success")
            return redirect(url_for("detalle_deporte", sport_id=sport_id))
        except Exception as exc:
            flash(f"Error al actualizar: {exc}", "error")
            return render_template("editar-deporte.html", sport={**datos, "id": sport_id})
    try:
        deporte = supabase.table(TABLA_DEPORTES).select("*").eq("id", sport_id).single().execute().data
    except Exception as exc:
        flash(f"No se pudo cargar el deporte: {exc}", "error")
        return redirect(url_for("index"))
    if not deporte:
        flash("Deporte no encontrado.", "error")
        return redirect(url_for("index"))
    return render_template("editar-deporte.html", sport=deporte)


@app.route("/eliminar/<int:sport_id>", methods=["POST"])
@login_required
def eliminar_deporte(sport_id):
    """Elimina un deporte del catálogo."""
    if hay_conexion_supabase():
        try:
            supabase.table(TABLA_DEPORTES).delete().eq("id", sport_id).execute()
            flash("Deporte eliminado.", "success")
        except Exception as exc:
            flash(f"Error al eliminar: {exc}", "error")
    return redirect(url_for("index"))


# ---------------------------------------------------------------
# AUTENTICACIÓN
# ---------------------------------------------------------------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    """Crea una cuenta nueva de usuario."""
    if request.method == "POST":
        nombre = request.form.get("name", "").strip()
        correo = request.form.get("email", "").strip().lower()
        contrasena = request.form.get("password", "")
        sexo = request.form.get("sex", "").strip()
        if not nombre or not correo or not contrasena:
            flash("Completa nombre, correo y contraseña.", "error")
            return render_template("registro.html")
        if hay_conexion_supabase():
            try:
                existente = supabase.table(TABLA_USUARIOS).select("id").eq("email", correo).execute()
                if existente.data:
                    flash("Ya existe una cuenta con ese correo.", "error")
                    return render_template("registro.html")
                nuevo_usuario = {"name": nombre, "email": correo, "password_hash": hash_password(contrasena), "sex": sexo}
                insertado = supabase.table(TABLA_USUARIOS).insert(nuevo_usuario).execute()
                session["user_id"] = insertado.data[0]["id"]
                flash(f"¡Cuenta creada! Bienvenido/a, {nombre}. Completa tu perfil deportivo para recibir recomendaciones.", "success")
                return redirect(url_for("perfil"))
            except Exception as exc:
                flash(f"Error al crear la cuenta: {exc}", "error")
    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Inicia sesión con correo y contraseña."""
    if request.method == "POST":
        correo = request.form.get("email", "").strip().lower()
        contrasena = request.form.get("password", "")
        if hay_conexion_supabase():
            try:
                usuario = supabase.table(TABLA_USUARIOS).select("*").eq("email", correo).single().execute().data
                if usuario and verify_password(contrasena, usuario["password_hash"]):
                    session["user_id"] = usuario["id"]
                    flash(f'Sesión iniciada. ¡Hola, {usuario["name"]}!', "success")
                    return redirect(url_for("index"))
                flash("Correo o contraseña incorrectos.", "error")
            except Exception:
                flash("Correo o contraseña incorrectos.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Cierra la sesión del usuario."""
    session.pop("user_id", None)
    flash("Sesión cerrada.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------
# HU6 — PERFIL DEPORTIVO PERSONALIZADO
# ---------------------------------------------------------------
@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    """Muestra y actualiza el perfil deportivo del usuario."""
    if request.method == "POST":
        datos = {
            "age": int(request.form.get("age") or 0) or None,
            "weight": float(request.form.get("weight") or 0) or None,
            "height": float(request.form.get("height") or 0) or None,
            "sex": request.form.get("sex", "").strip(),
            "experience_level": request.form.get("experience_level", "").strip(),
            "goal": request.form.get("goal", "").strip(),
            "budget_monthly": float(request.form.get("budget_monthly") or 0) or None,
            "available_days": int(request.form.get("available_days") or 0) or None,
            "available_hours": float(request.form.get("available_hours") or 0) or None,
        }
        if hay_conexion_supabase():
            try:
                supabase.table(TABLA_USUARIOS).update(datos).eq("id", session["user_id"]).execute()
                flash("Perfil actualizado. Ya podés pedir recomendaciones personalizadas.", "success")
                return redirect(url_for("recomendacion"))
            except Exception as exc:
                flash(f"No se pudo actualizar tu perfil: {exc}", "error")
    return render_template("perfil.html", user=get_current_user())


# ---------------------------------------------------------------
# HU2 — RECOMENDACIÓN PERSONALIZADA DE DEPORTE
# ---------------------------------------------------------------
@app.route("/recomendacion")
@login_required
def recomendacion():
    """Genera hasta 3 deportes recomendados según el perfil del usuario."""
    usuario = get_current_user()
    if not perfil_esta_completo(usuario):
        flash("Completa tu perfil deportivo para recibir recomendaciones personalizadas.", "error")
        return redirect(url_for("perfil"))
    deportes = obtener_deportes()
    resultados = recomendar_deportes(usuario, deportes, cantidad=3) if deportes else []
    return render_template("recomendacion.html", resultados=resultados, user=usuario)


# ---------------------------------------------------------------
# HU5 — ENTRENAMIENTO (rutina ajustada al tiempo disponible)
# ---------------------------------------------------------------
@app.route("/entrenamiento", methods=["GET", "POST"])
@login_required
def entrenamiento():
    """Genera una rutina semanal ajustada al tiempo real disponible del usuario."""
    deportes = obtener_deportes()
    resultado = None
    if request.method == "POST":
        try:
            deporte_id = int(request.form.get("sport_id"))
            peso = float(request.form.get("weight"))
            estatura = float(request.form.get("height"))
            sexo = request.form.get("sex", "").strip()
            nivel = request.form.get("level", "Principiante")
            dias_disponibles = int(request.form.get("available_days") or 3)
            horas_disponibles = float(request.form.get("available_hours") or 1)
        except (TypeError, ValueError):
            flash("Revisa que los números ingresados sean válidos.", "error")
            return render_template("entrenamiento.html", sports=deportes, result=None)

        deporte = next((d for d in deportes if d["id"] == deporte_id), None)
        if not deporte:
            flash("Selecciona un deporte válido.", "error")
            return render_template("entrenamiento.html", sports=deportes, result=None)

        estatura_m = estatura / 100
        imc = round(peso / (estatura_m * estatura_m), 1)
        info_imc = clasificar_imc(imc)
        plan = planificar_rutina(deporte["category"], dias_disponibles, horas_disponibles)

        consenso = {"avg_weight": None, "avg_daily_minutes": None, "entries": 0}
        if hay_conexion_supabase():
            try:
                supabase.table(TABLA_ENTRENAMIENTOS).insert({
                    "user_id": session["user_id"], "sport_id": deporte_id,
                    "weight": peso, "height": estatura, "sex": sexo, "level": nivel,
                    "daily_minutes": round(plan["total_minutos"] / max(1, dias_disponibles)),
                    "available_days": dias_disponibles, "imc": imc,
                }).execute()
                registros_mismo_deporte = supabase.table(TABLA_ENTRENAMIENTOS).select("weight,daily_minutes").eq("sport_id", deporte_id).execute().data or []
                if registros_mismo_deporte:
                    pesos = [r["weight"] for r in registros_mismo_deporte if r.get("weight")]
                    minutos = [r["daily_minutes"] for r in registros_mismo_deporte if r.get("daily_minutes")]
                    consenso["entries"] = len(registros_mismo_deporte)
                    if pesos:
                        consenso["avg_weight"] = round(sum(pesos) / len(pesos), 1)
                    if minutos:
                        consenso["avg_daily_minutes"] = round(sum(minutos) / len(minutos), 1)
            except Exception as exc:
                flash(f"No se pudo guardar tu registro: {exc}", "error")

        resultado = {
            "sport": deporte, "imc": imc, "imc_info": {"label": info_imc["etiqueta"], "note": info_imc["nota"]},
            "level": nivel, "available_days": dias_disponibles, "available_hours": horas_disponibles,
            "routine": plan["rutina"], "total_minutes": plan["total_minutos"],
            "available_minutes": plan["minutos_disponibles"], "sessions": plan["sesiones"],
            "ajustado": plan["ajustado"], "consensus": consenso,
            "chart_labels": [d[:3] for d, _, _ in plan["rutina"]],
            "chart_values": [m for _, _, m in plan["rutina"]],
        }

    return render_template("entrenamiento.html", sports=deportes, result=resultado)


@app.route("/entrenamiento/historial")
@login_required
def historial():
    """Muestra el historial de rutinas generadas por el usuario."""
    registros = []
    if hay_conexion_supabase():
        try:
            registros = supabase.table(TABLA_ENTRENAMIENTOS).select("*, sports(name)").eq("user_id", session["user_id"]).order("created_at").execute().data or []
        except Exception as exc:
            flash(f"No se pudo cargar tu historial: {exc}", "error")
    return render_template("historial.html", logs=registros)


# ---------------------------------------------------------------
# HU1 — COMPARADOR DE DEPORTES
# ---------------------------------------------------------------
@app.route("/comparar")
def comparar():
    """Compara dos deportes elegidos por el usuario."""
    deportes = obtener_deportes()
    id1 = request.args.get("d1", type=int)
    id2 = request.args.get("d2", type=int)
    deporte1 = next((d for d in deportes if d["id"] == id1), None) if id1 else None
    deporte2 = next((d for d in deportes if d["id"] == id2), None) if id2 else None
    return render_template("comparar.html", sports=deportes, sport1=deporte1, sport2=deporte2)


# ---------------------------------------------------------------
# HU4 — CÁLCULO DEL COSTO DE PRACTICAR UN DEPORTE
# ---------------------------------------------------------------
@app.route("/costo", methods=["GET", "POST"])
def costo():
    """Calcula el costo mensual y total de practicar un deporte."""
    deportes = obtener_deportes()
    resultado = None
    deporte_seleccionado = None
    if request.method == "POST":
        try:
            deporte_id = int(request.form.get("sport_id"))
            meses = int(request.form.get("months") or 1)
            gastos = {
                "inscripcion": float(request.form.get("inscripcion") or 0),
                "mensualidad": float(request.form.get("mensualidad") or 0),
                "alquiler": float(request.form.get("alquiler") or 0),
                "equipamiento": float(request.form.get("equipamiento") or 0),
                "vestimenta": float(request.form.get("vestimenta") or 0),
                "transporte": float(request.form.get("transporte") or 0),
                "alimentacion": float(request.form.get("alimentacion") or 0),
            }
        except (TypeError, ValueError):
            flash("Revisa que los montos ingresados sean números válidos.", "error")
            return render_template("costo.html", sports=deportes, result=None, selected_sport=None)

        deporte_seleccionado = next((d for d in deportes if d["id"] == deporte_id), None)
        resultado = calcular_costo(meses, gastos)
        resultado["detalle"] = gastos

        if session.get("user_id") and hay_conexion_supabase():
            try:
                supabase.table(TABLA_COSTOS).insert({
                    "user_id": session["user_id"], "sport_id": deporte_id, "months": meses,
                    **gastos, "monthly_total": resultado["monthly_total"], "period_total": resultado["period_total"],
                }).execute()
            except Exception:
                pass  # el cálculo se muestra igual aunque no se pueda guardar el historial

    return render_template("costo.html", sports=deportes, result=resultado, selected_sport=deporte_seleccionado)


# ---------------------------------------------------------------
# HU3 — CALCULADORA DE CALORÍAS POR NIVEL + REGISTRO DE ALIMENTOS
# ---------------------------------------------------------------
@app.route("/calculadora-calorias", methods=["GET", "POST"])
def calculadora_calorias():
    """
    Calcula el límite calórico diario según el nivel deportivo del usuario
    (Principiante/Amateur, Medio, Profesional) y permite ir registrando
    los alimentos del día para ver si está dentro de ese límite.
    """
    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "calcular_perfil":
            try:
                sexo = request.form.get("sex", "Masculino")
                edad = int(request.form.get("age"))
                peso = float(request.form.get("weight"))
                estatura = float(request.form.get("height"))
                nivel = request.form.get("nivel")
                session["calorias_perfil"] = calcular_gasto_calorico(sexo, edad, peso, estatura, nivel)
                session["alimentos_hoy"] = []
                session.modified = True
            except (TypeError, ValueError):
                flash("Revisa que edad, peso y estatura sean números válidos.", "error")

        elif accion == "agregar_alimento":
            nombre_alimento = request.form.get("nombre_alimento", "").strip()
            try:
                kcal_alimento = int(request.form.get("kcal_alimento"))
            except (TypeError, ValueError):
                kcal_alimento = None
            if nombre_alimento and kcal_alimento is not None:
                alimentos = session.get("alimentos_hoy", [])
                alimentos.append({"nombre": nombre_alimento, "kcal": kcal_alimento})
                session["alimentos_hoy"] = alimentos
                session.modified = True
            else:
                flash("Ingresa un nombre y las calorías del alimento.", "error")

        elif accion == "reiniciar_dia":
            session["alimentos_hoy"] = []
            session.modified = True

    perfil_calorico = session.get("calorias_perfil")
    alimentos_hoy = session.get("alimentos_hoy", [])
    resumen = resumir_alimentos(alimentos_hoy, perfil_calorico["limite_diario"]) if perfil_calorico else None

    return render_template(
        "calculadora-calorias.html",
        perfil_calorico=perfil_calorico, alimentos=alimentos_hoy, resumen=resumen,
        niveles=NIVELES_CALORICOS,
    )


# ---------------------------------------------------------------
# SOBRE LOS DEPORTES (contenido educativo/didáctico)
# ---------------------------------------------------------------
@app.route("/sobre-deportes")
def sobre_deportes():
    """Muestra fichas educativas: qué es, cuándo se inventó y un dato curioso de cada deporte."""
    return render_template("sobre-deportes.html", datos=DATOS_DEPORTES)


# ---------------------------------------------------------------
# MEMBRESÍA (a futuro)
# ---------------------------------------------------------------
@app.route("/membresia")
def membresia():
    """Muestra los planes de membresía (vista previa, sin cobros reales)."""
    return render_template("membresia.html")


# ---------------------------------------------------------------
# CÁMARA DE CALORÍAS (foto → estimación heurística)
# ---------------------------------------------------------------
@app.route("/camara-calorias", methods=["GET", "POST"])
def camara_calorias():
    """Estima calorías a partir de una foto de comida (heurística, sin IA real)."""
    resultado = None
    imagen_previa = None
    if request.method == "POST":
        archivo = request.files.get("photo")
        if not archivo or archivo.filename == "":
            flash("Selecciona una foto para analizar.", "error")
        else:
            try:
                imagen = Image.open(io.BytesIO(archivo.read()))
                resultado = estimar_calorias_foto(imagen)
                miniatura = imagen.convert("RGB")
                miniatura.thumbnail((360, 360))
                buffer = io.BytesIO()
                miniatura.save(buffer, format="JPEG", quality=80)
                imagen_previa = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
            except Exception as exc:
                flash(f"No se pudo procesar la imagen: {exc}", "error")
    return render_template("camara-calorias.html", result=resultado, preview_data_url=imagen_previa)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
