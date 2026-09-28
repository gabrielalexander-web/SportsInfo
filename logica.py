"""
Lógica de negocio del proyecto (nombres en español, snake_case, según el
estándar de codificación del equipo).

Cubre: comparador, motor de recomendación, cálculo de costos, calculadora
de calorías por nivel deportivo y planificador de tiempo de entrenamiento.
Todo es determinista y basado en reglas simples, sin dependencias externas.
"""

# Plantilla base de rutina semanal por categoría de deporte
RUTINA_BASE = {
    "Equipo": [
        ("Lunes", "Técnica + táctica", 60),
        ("Martes", "Fuerza y core", 45),
        ("Miércoles", "Movilidad / descanso activo", 25),
        ("Jueves", "Resistencia específica", 60),
        ("Viernes", "Estiramiento y recuperación", 25),
        ("Sábado", "Partido o scrimmage", 80),
        ("Domingo", "Descanso completo", 0),
    ],
    "Individual": [
        ("Lunes", "Sesión principal (técnica)", 50),
        ("Martes", "Fuerza general", 40),
        ("Miércoles", "Sesión ligera / movilidad", 30),
        ("Jueves", "Sesión principal (intensidad)", 55),
        ("Viernes", "Descanso activo", 20),
        ("Sábado", "Sesión larga", 70),
        ("Domingo", "Descanso completo", 0),
    ],
    "Acuático": [
        ("Lunes", "Técnica en piscina", 50),
        ("Martes", "Fuerza en seco", 35),
        ("Miércoles", "Resistencia acuática", 45),
        ("Jueves", "Descanso activo", 20),
        ("Viernes", "Velocidad / series", 50),
        ("Sábado", "Sesión larga continua", 60),
        ("Domingo", "Descanso completo", 0),
    ],
    "Combate": [
        ("Lunes", "Técnica y sombra", 50),
        ("Martes", "Fuerza y potencia", 40),
        ("Miércoles", "Cardio + saco", 35),
        ("Jueves", "Sparring técnico (supervisado)", 45),
        ("Viernes", "Movilidad y recuperación", 25),
        ("Sábado", "Circuito de resistencia", 50),
        ("Domingo", "Descanso completo", 0),
    ],
}

# Información descriptiva por rango de IMC
INFO_IMC = {
    "bajo": {"etiqueta": "Bajo peso", "nota": "Prioriza ejercicios de fuerza y asegúrate de comer lo suficiente para acompañar tu actividad."},
    "normal": {"etiqueta": "Normal", "nota": "Buen punto de partida: mantén variedad entre cardio y fuerza, y ajusta la intensidad según cómo te sientas."},
    "sobrepeso": {"etiqueta": "Sobrepeso", "nota": "Puedes sumar caminatas o cardio suave extra en tus días de descanso, subiendo la intensidad de a poco."},
    "obesidad": {"etiqueta": "Obesidad", "nota": "Empieza con sesiones cortas y de bajo impacto, aumentando el tiempo gradualmente. Hablar con un profesional de salud antes de intensificar es una buena idea."},
}

NIVELES_EXPERIENCIA = {"Principiante": 1, "Intermedio": 2, "Avanzado": 3}

# Nivel deportivo del usuario -> multiplicador de actividad para el cálculo
# calórico (fórmula de Mifflin-St Jeor). Se simplifica a 3 niveles, como
# pidió el equipo: Principiante/Amateur, Medio y Profesional.
NIVELES_CALORICOS = {
    "Principiante / Amateur": {"multiplicador": 1.375, "descripcion": "Entrena de 1 a 3 días por semana, de forma recreativa."},
    "Medio": {"multiplicador": 1.55, "descripcion": "Entrena de 3 a 5 días por semana, con constancia."},
    "Profesional": {"multiplicador": 1.725, "descripcion": "Entrena casi a diario, con exigencia competitiva."},
}

PALABRAS_CLAVE_OBJETIVO = {
    "perder peso": ["cardio", "resistencia", "grasa"],
    "ganar masa muscular": ["fuerza", "músculo", "potencia"],
    "salud general": ["salud", "bienestar", "flexibilidad", "movilidad"],
    "competir": ["competitivo", "rendimiento", "técnica"],
}


def clasificar_imc(imc: float) -> dict:
    """Devuelve la etiqueta y nota orientativa según el rango de IMC."""
    if imc < 18.5:
        return INFO_IMC["bajo"]
    if imc < 25:
        return INFO_IMC["normal"]
    if imc < 30:
        return INFO_IMC["sobrepeso"]
    return INFO_IMC["obesidad"]


# ---------------------------------------------------------------
# HU5 — Planificación del tiempo de entrenamiento
# ---------------------------------------------------------------
def planificar_rutina(categoria: str, dias_disponibles: int, horas_disponibles: float) -> dict:
    """Ajusta la rutina base para que no supere el tiempo real disponible del usuario."""
    plantilla = RUTINA_BASE.get(categoria, RUTINA_BASE["Individual"])
    minutos_disponibles = max(0, int(dias_disponibles) * float(horas_disponibles) * 60)

    dias_activos = [d for d in plantilla if d[2] > 0]
    seleccionados = dias_activos[: max(1, int(dias_disponibles))]
    total_plantilla = sum(m for _, _, m in seleccionados)

    ajustado = False
    if total_plantilla > minutos_disponibles and total_plantilla > 0:
        factor = max(0.4, minutos_disponibles / total_plantilla)
        seleccionados = [(dia, actividad, round(minutos * factor)) for dia, actividad, minutos in seleccionados]
        ajustado = True

    total_minutos = sum(m for _, _, m in seleccionados)
    return {
        "rutina": seleccionados, "total_minutos": total_minutos,
        "minutos_disponibles": int(minutos_disponibles), "sesiones": len(seleccionados), "ajustado": ajustado,
    }


# ---------------------------------------------------------------
# HU2 — Recomendación personalizada de deporte
# ---------------------------------------------------------------
def _nivel_presupuesto(presupuesto_mensual: float) -> int:
    if presupuesto_mensual is None:
        return 3
    if presupuesto_mensual < 100:
        return 1
    if presupuesto_mensual < 250:
        return 2
    if presupuesto_mensual < 450:
        return 3
    if presupuesto_mensual < 700:
        return 4
    return 5


def recomendar_deportes(perfil: dict, deportes: list, cantidad: int = 3) -> list:
    """Devuelve los deportes más afines al perfil del usuario, con motivos."""
    nivel_presupuesto = _nivel_presupuesto(perfil.get("budget_monthly"))
    experiencia_usuario = NIVELES_EXPERIENCIA.get(perfil.get("experience_level"), 1)
    objetivo = (perfil.get("goal") or "").strip().lower()
    palabras_objetivo = PALABRAS_CLAVE_OBJETIVO.get(objetivo, [])

    resultados = []
    for deporte in deportes:
        motivos = []
        puntaje = 0

        diferencia_costo = (deporte.get("cost_score") or 3) - nivel_presupuesto
        if diferencia_costo <= 0:
            puntaje += 5
            motivos.append("encaja con tu presupuesto")
        else:
            puntaje += max(0, 5 - diferencia_costo * 2)

        plan = planificar_rutina(deporte.get("category"), perfil.get("available_days") or 3, perfil.get("available_hours") or 1)
        if not plan["ajustado"]:
            puntaje += 5
            motivos.append("se adapta a tu tiempo disponible")
        else:
            total_plantilla = sum(m for _, _, m in RUTINA_BASE.get(deporte.get("category"), RUTINA_BASE["Individual"]))
            puntaje += round(5 * min(1, plan["minutos_disponibles"] / max(1, total_plantilla)))

        dificultad_deporte = NIVELES_EXPERIENCIA.get(deporte.get("difficulty_level"), 1)
        if dificultad_deporte <= experiencia_usuario:
            puntaje += 5
            if dificultad_deporte == experiencia_usuario:
                motivos.append("nivel de dificultad acorde a tu experiencia")
        else:
            puntaje += max(0, 5 - (dificultad_deporte - experiencia_usuario) * 2)

        texto_beneficios = (deporte.get("physical_benefits") or "").lower()
        if any(palabra in texto_beneficios for palabra in palabras_objetivo):
            puntaje += 4
            motivos.append(f'sus beneficios se alinean con tu objetivo ("{perfil.get("goal")}")')

        if not motivos:
            motivos.append("es una opción equilibrada según tus datos")

        resultados.append({"sport": deporte, "score": puntaje, "motivos": motivos})

    resultados.sort(key=lambda r: r["score"], reverse=True)
    return resultados[:cantidad]


# ---------------------------------------------------------------
# HU4 — Cálculo del costo de practicar un deporte
# ---------------------------------------------------------------
def calcular_costo(meses: int, gastos: dict) -> dict:
    """
    gastos: inscripcion, mensualidad, alquiler, equipamiento, vestimenta,
    transporte, alimentacion (montos en Bs). Inscripción, equipamiento y
    vestimenta se tratan como gasto único; el resto es mensual.
    """
    gasto_unico = gastos.get("inscripcion", 0) + gastos.get("equipamiento", 0) + gastos.get("vestimenta", 0)
    gasto_mensual = gastos.get("mensualidad", 0) + gastos.get("alquiler", 0) + gastos.get("transporte", 0) + gastos.get("alimentacion", 0)
    total_periodo = gasto_unico + gasto_mensual * meses
    return {
        "monthly_total": round(gasto_mensual, 2), "period_total": round(total_periodo, 2),
        "unico": round(gasto_unico, 2), "mensual": round(gasto_mensual, 2), "months": meses,
    }


# ---------------------------------------------------------------
# HU3 — Calculadora de calorías por nivel + registro de alimentación
# ---------------------------------------------------------------
def calcular_gasto_calorico(sexo: str, edad: int, peso: float, estatura: float, nivel: str) -> dict:
    """
    Estima el gasto calórico diario (TDEE) con la fórmula de Mifflin-St
    Jeor, usando el nivel deportivo (Principiante/Amateur, Medio,
    Profesional) como factor de actividad. Es una estimación general, no
    un diagnóstico médico.
    """
    if sexo == "Femenino":
        tmb = 10 * peso + 6.25 * estatura - 5 * edad - 161
    else:
        tmb = 10 * peso + 6.25 * estatura - 5 * edad + 5

    info_nivel = NIVELES_CALORICOS.get(nivel, NIVELES_CALORICOS["Principiante / Amateur"])
    gasto_diario = tmb * info_nivel["multiplicador"]

    return {
        "tmb": round(tmb), "gasto_diario": round(gasto_diario),
        "limite_diario": round(gasto_diario), "nivel": nivel,
        "descripcion_nivel": info_nivel["descripcion"],
    }


def resumir_alimentos(alimentos: list, limite_diario: int) -> dict:
    """
    Suma las calorías de los alimentos registrados en el día y los compara
    contra el límite diario calculado a partir del perfil del usuario.
    """
    total_consumido = sum(a.get("kcal", 0) for a in alimentos)
    restante = limite_diario - total_consumido
    porcentaje = round((total_consumido / limite_diario) * 100) if limite_diario else 0

    if porcentaje < 90:
        estado = {"clave": "dentro", "mensaje": "Estás dentro de tu límite diario."}
    elif porcentaje <= 100:
        estado = {"clave": "cerca", "mensaje": "Estás cerca de tu límite diario — ve con cuidado en lo que sigue."}
    else:
        estado = {"clave": "superado", "mensaje": "Superaste tu límite diario estimado."}

    return {
        "total_consumido": total_consumido, "restante": restante,
        "porcentaje": min(porcentaje, 999), "estado": estado,
    }
