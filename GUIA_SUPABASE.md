# 🗄️ Guía paso a paso: conectar SportsInfo a Supabase

Esta guía asume que no tocaste Supabase nunca. Vas a terminar con tu base de datos real, conectada a tu proyecto.

## Paso 1 — Crear la cuenta y el proyecto

1. Entra a [supabase.com](https://supabase.com) y creá una cuenta gratis (podés usar tu cuenta de GitHub para entrar más rápido).
2. Click en **New Project**.
3. Ponele un nombre (por ejemplo `sportsinfo`), elegí una contraseña para la base de datos (guárdala, la vas a necesitar si alguna vez te conectás directo a Postgres) y elegí una región cercana a Bolivia (por ejemplo *South America (São Paulo)* si aparece, o la más cercana disponible).
4. Click en **Create new project** y esperá 1-2 minutos mientras Supabase prepara todo.

## Paso 2 — Crear las tablas

1. En el menú de la izquierda, entrá a **SQL Editor**.
2. Click en **New query**.
3. Abrí el archivo `schema.sql` de este proyecto, copiá **todo** su contenido, y pegalo en el editor.
4. Click en **Run** (o `Ctrl+Enter`). Deberías ver un mensaje de éxito. Esto crea las tablas `users`, `sports`, `training_logs` y `cost_estimates`.
5. Para confirmar que se crearon: andá a **Table Editor** en el menú lateral y deberías ver las 4 tablas listadas.

## Paso 3 — Obtener tu URL y tu clave

1. En el menú lateral, entrá a **Settings** (el ícono de engranaje) → **API Keys** (en proyectos más nuevos) o **API** (en proyectos más antiguos).
2. Copiá el **Project URL** (se ve algo como `https://abcdefgh.supabase.co`).
3. Copiá la clave llamada **Publishable key** (`sb_publishable_...`). Si tu proyecto es más antiguo y no ves esa opción, copiá la que dice **anon public** o **anon key** en su lugar — sirve exactamente igual para este proyecto.
4. **Nunca copies la clave "secret" ni la "service_role"** — esas dan acceso total y no deben usarse en el código del sitio web.

## Paso 4 — Configurar tu proyecto local

1. En la carpeta del proyecto, copiá `.env.example` y renombralo a `.env`.
2. Abrí `.env` y completá:
   ```
   SUPABASE_URL=https://abcdefgh.supabase.co
   SUPABASE_KEY=sb_publishable_xxxxxxxxxxxx
   SECRET_KEY=cualquier-texto-largo-y-aleatorio-que-quieras
   ```
3. Guardá el archivo. **Este archivo `.env` nunca se sube a GitHub** (ya está excluido en `.gitignore`).

## Paso 5 — Instalar dependencias y probar

```bash
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py           # opcional: carga 10 deportes de ejemplo
python app.py
```

Abrí **http://localhost:5000** en tu navegador. Si ves el catálogo de deportes sin errores, ¡ya estás conectado a Supabase de verdad!

## Paso 6 — Probar que el registro funciona

1. Click en **Crear cuenta**, completá el formulario y enviá.
2. Andá a Supabase → **Table Editor** → tabla **users**. Deberías ver tu usuario nuevo ahí, con la contraseña ya cifrada (nunca en texto plano).
3. Si algo falla, el mensaje de error en la página suele decir exactamente qué columna o tabla está fallando — revisá que hayas corrido `schema.sql` completo en el Paso 2.

## Problemas comunes

| Síntoma | Causa probable |
|---|---|
| "No hay conexión con Supabase" | El archivo `.env` no existe o `SUPABASE_URL`/`SUPABASE_KEY` están vacíos o mal copiados |
| Error al registrar un usuario | La tabla `users` no existe todavía — repetí el Paso 2 |
| "Ya existe una cuenta con ese correo" apenas empezás | Alguien (quizás vos, probando) ya se registró con ese correo — usá otro o borrá la fila en Table Editor |
