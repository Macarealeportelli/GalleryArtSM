from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from .config import DATABASE_URL, EN_VERCEL

opciones = {}
if DATABASE_URL.startswith("sqlite"):
    opciones["connect_args"] = {"check_same_thread": False}
else:
    opciones["pool_pre_ping"] = True
if EN_VERCEL:
    # Cada función de Vercel vive poco: abrir y cerrar la conexión en cada pedido
    opciones["poolclass"] = NullPool

engine = create_engine(DATABASE_URL, **opciones)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
