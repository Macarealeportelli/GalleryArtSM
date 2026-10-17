from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import SECRET_KEY, TOKEN_EXPIRE_MINUTES
from .database import get_db
from .models import Usuario

ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)


def _bytes(password: str) -> bytes:
    # bcrypt solo considera los primeros 72 bytes
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_bytes(password), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_bytes(password), password_hash.encode())
    except ValueError:
        return False


def crear_token(usuario_id: int) -> str:
    payload = {
        "sub": str(usuario_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def usuario_actual_opcional(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario | None:
    if cred is None:
        return None
    try:
        payload = jwt.decode(cred.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión inválida o vencida")
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión inválida o vencida")
    return usuario


def usuario_actual(usuario: Usuario | None = Depends(usuario_actual_opcional)) -> Usuario:
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Debés iniciar sesión")
    return usuario


def usuario_habilitado(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
    if not usuario.puede_editar:
        motivo = "Tu cuenta está desactivada" if not usuario.habilitado else "Tu perfil no tiene un colegio asignado"
        raise HTTPException(status.HTTP_403_FORBIDDEN, motivo)
    return usuario


def usuario_admin(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
    if not usuario.es_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo administradores")
    return usuario
