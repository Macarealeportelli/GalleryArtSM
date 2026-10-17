import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Vercel define esta variable en sus servidores
EN_VERCEL = bool(os.getenv("VERCEL"))

SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-esta-clave-en-produccion")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "720"))

# Local: SQLite. En Vercel: PostgreSQL (Neon), que entrega DATABASE_URL o POSTGRES_URL.
DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("POSTGRES_URL")
    or f"sqlite:///{(BASE_DIR / 'galeria.db').as_posix()}"
)
for prefijo in ("postgres://", "postgresql://"):
    if DATABASE_URL.startswith(prefijo):
        DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len(prefijo):]

# Imágenes: si hay token de Vercel Blob se guardan ahí; si no, en la carpeta local.
BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN", "")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
if not UPLOAD_DIR.is_absolute():
    UPLOAD_DIR = (BASE_DIR / UPLOAD_DIR).resolve()
# Vercel no acepta envíos de más de 4,5 MB (la web achica las fotos antes de subirlas)
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "4" if EN_VERCEL else "15"))

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

# Lista fija de administradores. Se sincroniza al arrancar.
# En Vercel se carga como variable de entorno ADMINS_JSON; localmente, en admins.json.
ADMINS_JSON = os.getenv("ADMINS_JSON", "")
ADMINS_FILE = Path(os.getenv("ADMINS_FILE", BASE_DIR / "admins.json"))

# Si existe el build del frontend, el backend lo sirve en la misma URL.
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
