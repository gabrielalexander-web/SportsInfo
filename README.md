# 🏆 SportsInfo — Plataforma de Deportes

Plataforma web de información deportiva con perfil personalizado, recomendaciones a medida, comparador, calculadora de costos, calculadora de calorías por nivel deportivo y control de entrenamiento adaptado a tu tiempo real.

**Stack:** HTML5 · CSS3 · Python 3.12 · Flask 3.1 · Jinja2 3.1 · Supabase (PostgreSQL 15+)

---

## 1. Historias de usuario cubiertas

| HU | Descripción | Dónde está en el código |
|---|---|---|
| HU1 | Comparar dos o más deportes (costo, equipamiento, tiempo, dificultad, beneficios) | `/comparar`, `comparar.html` |
| HU2 | Recomendación personalizada según perfil | `/recomendacion`, `logica.recomendar_deportes()` |
| HU3 | Calculadora de calorías por nivel + registro de alimentación | `/calculadora-calorias`, `logica.calcular_gasto_calorico()`, `logica.resumir_alimentos()` |
| HU4 | Cálculo del costo de practicar un deporte | `/costo`, `logica.calcular_costo()` |
| HU5 | Planificación del tiempo de entrenamiento | `/entrenamiento`, `logica.planificar_rutina()` |
| HU6 | Perfil deportivo personalizado | `/perfil` |

## 2. Estándar de codificación del equipo

Los nombres de variables, funciones y comentarios están en español, en `snake_case`, siguiendo PEP 8 (ver `obtener_deportes()`, `calcular_costo()`, `clasificar_imc()`, etc. en `app.py` y `logica.py`). Las plantillas usan nombres de archivo en minúsculas y kebab-case y descriptivos (`detalle-deporte.html`, `calculadora-calorias.html`). Las clases CSS son kebab-case (`card-img`, `btn-amber`).

## 3. Requisitos previos

- Python 3.12+
- Cuenta gratuita en [Supabase](https://supabase.com)

## 4. Configuración de Supabase

1. Crea un proyecto en [supabase.com](https://supabase.com).
2. En **SQL Editor**, ejecuta todo `schema.sql` (crea `users`, `sports`, `training_logs`, `cost_estimates`).
3. En **Project Settings > API**, copia `Project URL` y `anon public key`.

## 5. Instalación local

```bash
cd deportes-app
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Completa SUPABASE_URL, SUPABASE_KEY y un SECRET_KEY propio
python seed_data.py           # opcional: carga 6 deportes de ejemplo
python app.py
```

Abre **http://localhost:5000**

## 6. Estructura del proyecto

```
deportes-app/
├── app.py                          # Rutas (endpoints), en español
├── logica.py                       # Motor de recomendación, costos, calorías y planificador
├── auth.py                         # Registro/login propio
├── supabase_client.py
├── seed_data.py
├── schema.sql                      # users (con perfil), sports, training_logs, cost_estimates
├── templates/
│   ├── base.html                     # navegación con las 8 secciones
│   ├── index.html
│   ├── detalle-deporte.html / agregar-deporte.html / editar-deporte.html / _form-deporte.html
│   ├── registro.html / login.html / perfil.html          (HU6)
│   ├── recomendacion.html                                 (HU2)
│   ├── comparar.html                                      (HU1)
│   ├── costo.html                                          (HU4)
│   ├── calculadora-calorias.html                           (HU3)
│   ├── entrenamiento.html / historial.html                 (HU5)
│   ├── camara-calorias.html          # cámara de calorías (beta, heurística sin IA real)
│   └── membresia.html                # vista de planes, sin cobros reales todavía
└── static/css/style.css
```

## 7. Cómo funciona la calculadora de calorías (HU3)

1. El usuario elige su **nivel deportivo**: Principiante/Amateur, Medio o Profesional. Cada nivel tiene un factor de actividad distinto (definido en `NIVELES_CALORICOS` dentro de `logica.py`), que junto a edad/sexo/peso/estatura calcula el **límite calórico diario** (fórmula de Mifflin-St Jeor).
2. El usuario va agregando los alimentos que come (nombre + calorías, ingresadas por él mismo — ej. "Pollo a la plancha, 250 kcal", "Papas fritas, 180 kcal").
3. El sistema suma el total del día y lo compara contra el límite: **dentro del límite** (verde), **cerca del límite** (ámbar, ≥90%) o **superado** (rojo), con una barra de progreso.
4. El registro del día vive en la sesión del usuario (`session`), sin necesidad de una tabla nueva — ver nota en `schema.sql` si el equipo quiere persistirlo.

## 8. Cómo funciona el motor de recomendación (HU2)

En `logica.py`, `recomendar_deportes()` puntúa cada deporte contra el perfil del usuario en 4 ejes: presupuesto vs. costo, tiempo disponible vs. exigencia (reutiliza el planificador de HU5), experiencia vs. dificultad, y objetivo vs. palabras clave en los beneficios físicos. Reglas explícitas, sin modelo externo.

## 9. Notas importantes

- **Cámara de calorías (beta):** sigue siendo una heurística de colores, no reconocimiento real de comida — el punto de conexión a un modelo de IA de visión está marcado en `app.py`.
- **Costo (HU4):** inscripción, equipamiento y vestimenta se calculan como gasto único; mensualidad, alquiler, transporte y alimentación como gasto mensual recurrente.
- **Seguridad:** las políticas RLS en `schema.sql` están abiertas para facilitar pruebas — ajustarlas antes de producción real.
- Sobre JavaScript: el estándar del equipo pide evitarlo salvo que sea necesario. Se usa Chart.js para los gráficos (comparador, costos, calorías) porque las historias de usuario piden explícitamente estadísticas visuales — es la única razón por la que se mantiene.

## 10. Sección "Sobre los deportes"

`/sobre-deportes` muestra fichas educativas (qué es, cuándo se inventó, un dato curioso) para los 10 deportes populares. El contenido vive en `datos_deportes.py` — para agregar un deporte nuevo a esta sección, solo hay que sumar una entrada al diccionario `DATOS_DEPORTES` con la misma clave (en minúsculas) que usa `iconos.py`.

## 11. Cómo desplegarlo gratis (sin comprar dominio)

1. **Supabase** ya tiene un plan gratuito suficiente para este proyecto — pasos detallados en [`GUIA_SUPABASE.md`](GUIA_SUPABASE.md).
2. Subí el código a un repositorio de GitHub — pasos detallados en [`GUIA_GITHUB.md`](GUIA_GITHUB.md) (incluye cómo conectarlo a Render al final).
3. Creá una cuenta en [Render](https://render.com) (no pide tarjeta) y conectá el repositorio — te da una URL gratuita tipo `tu-proyecto.onrender.com`. Configurá ahí las mismas variables de `.env` (`SUPABASE_URL`, `SUPABASE_KEY`, `SECRET_KEY`).
4. Alternativa: [PythonAnywhere](https://www.pythonanywhere.com), también gratis, con URL tipo `tunombre.pythonanywhere.com`.
5. El plan gratuito de Render "duerme" la app tras un rato sin visitas (el primer ingreso tarda ~1 minuto en despertar) — normal y aceptable para un proyecto de facultad o una demo.

Comprar un dominio propio (`sportsinfo.com`) es opcional y solo hace falta si más adelante quieren una dirección con su propia marca.

## 12. Notas sobre imágenes de deportes

El campo `image_url` de cada deporte (formularios de agregar/editar) queda listo para pegar la URL de una foto de bancos de imágenes gratuitos sin derechos de autor, como Pixabay, Pexels o Unsplash. Por defecto, si no se pone imagen, se usa una ilustración propia en SVG (ver `iconos.py`) para no depender de fotos de terceros dentro del proyecto.

## 13. Próximos pasos sugeridos

- Persistir el registro diario de alimentos en una tabla (`food_log`) si se quiere mantener el historial entre sesiones.
- Conectar un modelo de IA de visión real para la cámara de calorías.
- Conectar una pasarela de pago para la membresía.
- Subir imágenes de deportes a Supabase Storage en vez de URLs externas.
