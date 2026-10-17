from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from .admins import sincronizar_admins
from .almacenamiento import USA_BLOB
from .config import CORS_ORIGINS, FRONTEND_DIST, UPLOAD_DIR
from .database import Base, engine
from .routers import auth, obras, usuarios


def migrar() -> None:
    """Agrega columnas nuevas a bases de datos creadas con versiones anteriores."""
    columnas = {c["name"] for c in inspect(engine).get_columns("usuarios")}
    if "colegio" not in columnas:
        with engine.begin() as con:
            con.execute(text("ALTER TABLE usuarios ADD COLUMN colegio VARCHAR(150)"))


_inicializado = False


def inicializar() -> None:
    """Crea las tablas, aplica migraciones y sincroniza los administradores (una sola vez)."""
    global _inicializado
    if _inicializado:
        return
    Base.metadata.create_all(engine)
    migrar()
    sincronizar_admins()
    _inicializado = True


@asynccontextmanager
async def lifespan(_: FastAPI):
    inicializar()
    yield


app = FastAPI(title="Galería de Arte – Colegio San Marcos", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials="*" not in CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(obras.router)
app.include_router(usuarios.router)

# Imágenes guardadas en la carpeta local (en Vercel se sirven directamente desde Vercel Blob)
if not USA_BLOB:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# Si el frontend está compilado (frontend/dist), se sirve desde el mismo servidor.
if FRONTEND_DIST.is_dir():
    dist = FRONTEND_DIST.resolve()

    @app.get("/{ruta:path}", include_in_schema=False)
    def frontend(ruta: str):
        if ruta.startswith("api/"):
            raise HTTPException(404, "No encontrado")
        archivo = (dist / ruta).resolve()
        if ruta and archivo.is_file() and archivo.is_relative_to(dist):
            return FileResponse(archivo)
        return FileResponse(dist / "index.html")
