"""Administradores fijos, definidos en admins.json.

Al arrancar el servidor:
- se crea cada administrador de la lista que no exista (o se convierte en admin si ya tenía cuenta),
- se actualiza su nombre y contraseña según el archivo,
- cualquier otro usuario que figure como admin pasa a ser invitado.
"""

import json
import logging

from sqlalchemy import func, select

from .config import ADMINS_FILE
from .database import SessionLocal
from .models import Usuario
from .security import hash_password, verify_password

log = logging.getLogger("uvicorn.error")


def leer_admins() -> list[dict]:
    if not ADMINS_FILE.exists():
        log.warning("No existe %s: no hay administradores definidos", ADMINS_FILE)
        return []
    datos = json.loads(ADMINS_FILE.read_text(encoding="utf-8"))
    admins = []
    for a in datos:
        email = str(a.get("email", "")).strip().lower()
        password = str(a.get("password", ""))
        if not email or not password:
            raise ValueError(f"{ADMINS_FILE.name}: cada administrador necesita email y password")
        admins.append({"email": email, "password": password, "nombre": a.get("nombre") or email})
    return admins


def sincronizar_admins() -> None:
    admins = leer_admins()
    emails = {a["email"] for a in admins}
    with SessionLocal() as db:
        for a in admins:
            usuario = db.scalar(select(Usuario).where(func.lower(Usuario.email) == a["email"]))
            if usuario is None:
                usuario = Usuario(email=a["email"], password_hash="")
                db.add(usuario)
            usuario.nombre = a["nombre"]
            usuario.es_admin = True
            usuario.habilitado = True
            if not verify_password(a["password"], usuario.password_hash):
                usuario.password_hash = hash_password(a["password"])

        for usuario in db.scalars(select(Usuario).where(Usuario.es_admin.is_(True))):
            if usuario.email.lower() not in emails:
                usuario.es_admin = False
        db.commit()
    log.info("Administradores sincronizados: %s", ", ".join(sorted(emails)) or "ninguno")
