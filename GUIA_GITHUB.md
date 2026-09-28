# 🐙 Guía paso a paso: subir SportsInfo a GitHub

Esto sirve para dos cosas: tener un respaldo del código (por si las moscas, como decías) y que el equipo de 5 pueda trabajar sobre el mismo proyecto.

## Paso 1 — Crear la cuenta y el repositorio

1. Entrá a [github.com](https://github.com) y creá una cuenta gratis si no tenés.
2. Arriba a la derecha, click en el **+** → **New repository**.
3. Ponele un nombre (por ejemplo `sportsinfo`), dejalo en **Private** si querés que solo el equipo lo vea, o **Public** si no importa que se vea.
4. **No marques** "Add a README" ni ".gitignore" (ya los tenemos en el proyecto) — dejá el repositorio vacío.
5. Click en **Create repository**. GitHub te va a mostrar una pantalla con comandos — los vas a usar en el Paso 3.

## Paso 2 — Instalar Git (si no lo tenés)

- **Windows**: descargá [git-scm.com](https://git-scm.com/downloads) e instalalo con las opciones por defecto.
- **Mac**: abrí la Terminal y escribí `git --version` — si no lo tenés, macOS te va a ofrecer instalarlo solo.
- **Linux**: `sudo apt install git` (Ubuntu/Debian) o el gestor de paquetes de tu distro.

## Paso 3 — Subir el proyecto por primera vez

Parado en la carpeta del proyecto (`deportes-app`), en la terminal:

```bash
git init
git add .
git commit -m "Primera versión de SportsInfo"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/sportsinfo.git
git push -u origin main
```

Reemplazá `TU-USUARIO` por tu nombre de usuario de GitHub (o el de quien creó el repositorio). Si te pide iniciar sesión, seguí las instrucciones en pantalla (GitHub suele abrir el navegador para confirmar).

Verificá entrando a tu repositorio en github.com — deberías ver todos los archivos ahí, **excepto** `.env` (ese se queda solo en tu computadora, a propósito).

## Paso 4 — Cómo trabaja el equipo de 5 sobre el mismo repositorio

1. El dueño del repositorio va a **Settings** → **Collaborators** → **Add people**, y agrega a los 4 compañeros por su usuario o correo de GitHub.
2. Cada compañero clona el proyecto una sola vez:
   ```bash
   git clone https://github.com/TU-USUARIO/sportsinfo.git
   cd sportsinfo
   cp .env.example .env   # y completa sus propias credenciales de Supabase
   ```
3. Para cada funcionalidad nueva, cada uno crea su propia rama (como ya dice la guía de estándares del equipo):
   ```bash
   git checkout -b feature/nombre-de-la-funcionalidad
   # ...hace cambios...
   git add .
   git commit -m "agregar tal cosa"
   git push -u origin feature/nombre-de-la-funcionalidad
   ```
4. Desde GitHub, se abre un **Pull Request** de esa rama hacia `main`, alguien más del equipo lo revisa, y recién ahí se mezcla (**Merge**).

## Paso 5 — (Opcional) Conectar el repositorio a un hosting gratuito

Si después quieren que la página funcione en internet gratis (sin comprar dominio):

1. Creá una cuenta en [Render](https://render.com) (podés entrar directo con tu cuenta de GitHub).
2. **New** → **Web Service** → elegí el repositorio `sportsinfo`.
3. Render detecta que es Python; como *Start Command* poné: `gunicorn app:app` (vas a necesitar agregar `gunicorn` a `requirements.txt` primero: `pip install gunicorn` y agregarlo al archivo).
4. En **Environment Variables**, cargá `SUPABASE_URL`, `SUPABASE_KEY` y `SECRET_KEY` — los mismos valores de tu `.env`.
5. Click en **Create Web Service**. En un par de minutos te da una URL gratuita tipo `sportsinfo.onrender.com`.

## Problemas comunes

| Síntoma | Causa probable |
|---|---|
| "remote origin already exists" | Ya habías corrido `git remote add origin` antes — usá `git remote set-url origin <URL>` en su lugar |
| Git pide usuario y contraseña y falla | GitHub ya no acepta contraseña común; te va a pedir loguearte por navegador o usar un token — seguí las instrucciones que te muestra la terminal |
| El `.env` casi se sube por error | Revisá que `.gitignore` tenga la línea `.env` — ya viene incluida en este proyecto |
