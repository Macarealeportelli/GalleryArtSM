import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-esta-clave-en-produccion")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "720"))

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(BASE_DIR / 'galeria.db').as_posix()}")

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
if not UPLOAD_DIR.is_absolute():
    UPLOAD_DIR = (BASE_DIR / UPLOAD_DIR).resolve()
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "15"))

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

# Lista fija de administradores (ver admins.example.json). Se sincroniza al arrancar.
ADMINS_FILE = Path(os.getenv("ADMINS_FILE", BASE_DIR / "admins.json"))

# Si existe el build del frontend, el backend lo sirve en la misma URL.
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
