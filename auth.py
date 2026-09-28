"""
Utilidades de autenticación propia (sin depender de Supabase Auth).
Usa hashing de contraseñas de Werkzeug (ya viene con Flask) y sesiones de Flask.
"""
from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from supabase_client import supabase


def hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password)


def verify_password(raw_password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, raw_password)


def get_current_user():
    """Devuelve el dict completo del usuario en sesión (incluye su perfil deportivo), o None."""
    user_id = session.get("user_id")
    if not user_id or supabase is None:
        return None
    try:
        response = supabase.table("users").select("*").eq("id", user_id).single().execute()
        return response.data
    except Exception:
        return None


def login_required(view_func):
    """Decorador: exige sesión iniciada antes de acceder a la vista."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Necesitas iniciar sesión para acceder a esta sección.", "error")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped
