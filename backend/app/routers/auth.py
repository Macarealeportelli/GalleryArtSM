from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Obra, Usuario
from ..schemas import LoginIn, RegistroIn, TokenOut, UsuarioOut
from ..security import crear_token, hash_password, usuario_actual, verify_password

router = APIRouter(prefix="/api/auth", tags=["autenticación"])


def normalizar_colegio(colegio: str) -> str:
    return " ".join(colegio.split())


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registro(datos: RegistroIn, db: Session = Depends(get_db)):
    email = datos.email.strip().lower()
    if db.scalar(select(Usuario).where(func.lower(Usuario.email) == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una cuenta con ese email")
    # Las cuentas creadas desde la web son siempre invitados de un colegio.
    usuario = Usuario(
        nombre=datos.nombre.strip(),
        email=email,
        colegio=normalizar_colegio(datos.colegio),
        password_hash=hash_password(datos.password),
        es_admin=False,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn, db: Session = Depends(get_db)):
    email = datos.email.strip().lower()
    usuario = db.scalar(select(Usuario).where(func.lower(Usuario.email) == email))
    if usuario is None or not verify_password(datos.password, usuario.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email o contraseña incorrectos")
    return TokenOut(access_token=crear_token(usuario.id), usuario=UsuarioOut.model_validate(usuario))


@router.get("/yo", response_model=UsuarioOut)
def yo(usuario: Usuario = Depends(usuario_actual)):
    return usuario


@router.get("/colegios", response_model=list[str])
def colegios(db: Session = Depends(get_db)):
    """Colegios ya cargados, para sugerirlos al registrarse y evitar variantes del mismo nombre."""
    nombres = set(db.scalars(select(Obra.colegio).distinct()))
    nombres |= set(db.scalars(select(Usuario.colegio).where(Usuario.colegio.is_not(None)).distinct()))
    unicos = {n.casefold(): n for n in sorted(nombres)}
    return sorted(unicos.values(), key=str.casefold)
