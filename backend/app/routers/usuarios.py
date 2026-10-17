from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import UsuarioOut, UsuarioUpdate
from ..security import usuario_admin
from .auth import normalizar_colegio

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


def obtener_invitado(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    if usuario.es_admin:
        # Los administradores se gestionan en admins.json
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Los administradores no se pueden modificar desde la web")
    return usuario


@router.get("", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(usuario_admin)):
    return db.scalars(select(Usuario).order_by(Usuario.es_admin.desc(), Usuario.creado.desc())).all()


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def actualizar(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(usuario_admin),
):
    usuario = obtener_invitado(db, usuario_id)
    if datos.habilitado is not None:
        usuario.habilitado = datos.habilitado
    if datos.colegio is not None:
        usuario.colegio = normalizar_colegio(datos.colegio)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(usuario_id: int, db: Session = Depends(get_db), _: Usuario = Depends(usuario_admin)):
    db.delete(obtener_invitado(db, usuario_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
