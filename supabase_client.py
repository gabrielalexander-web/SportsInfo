"""
Cliente de conexión a Supabase.
Lee las credenciales desde el archivo .env (ver .env.example).
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client | None = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print(
        "⚠️  No se encontraron SUPABASE_URL / SUPABASE_KEY en el entorno.\n"
        "   Copia .env.example a .env y completa tus credenciales de Supabase."
    )
