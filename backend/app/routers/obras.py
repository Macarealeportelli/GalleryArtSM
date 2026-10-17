import io
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .. import almacenamiento
from ..config import MAX_UPLOAD_MB
from ..database import get_db
from ..models import Obra, Usuario
from ..schemas import FiltrosOut, ObraOut
from ..security import usuario_habilitado

router = APIRouter(prefix="/api/obras", tags=["obras"])

FORMATOS = {
    "JPEG": (".jpg", "image/jpeg"),
    "PNG": (".png", "image/png"),
    "WEBP": (".webp", "image/webp"),
    "GIF": (".gif", "image/gif"),
}
TAMANO_MINIATURA = (900, 900)


def a_salida(obra: Obra) -> ObraOut:
    return ObraOut(
        id=obra.id,
        titulo=obra.titulo,
        autor_nombre=obra.autor_nombre,
        autor_apellido=obra.autor_apellido,
        anio=obra.anio,
        tecnica=obra.tecnica,
        colegio=obra.colegio,
        imagen_url=almacenamiento.url_publica(obra.imagen),
        miniatura_url=almacenamiento.url_publica(obra.miniatura),
        subido_por=obra.subido_por.nombre if obra.subido_por else None,
        creado=obra.creado,
        actualizado=obra.actualizado,
    )


def limpiar(valor: str | None, campo: str, obligatorio: bool = True) -> str | None:
    valor = (valor or "").strip()
    if not valor:
        if obligatorio:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"El campo «{campo}» es obligatorio")
        return None
    return valor


def guardar_imagen(archivo: UploadFile) -> tuple[str, str]:
    """Valida la imagen, guarda el original y genera una miniatura liviana para la grilla."""
    limite = MAX_UPLOAD_MB * 1024 * 1024
    datos = archivo.file.read(limite + 1)
    if len(datos) > limite:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, f"La imagen supera los {MAX_UPLOAD_MB} MB")
    try:
        Image.open(io.BytesIO(datos)).verify()
        img = Image.open(io.BytesIO(datos))
        formato = img.format
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El archivo no es una imagen válida")
    if formato not in FORMATOS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Formato no admitido (usar JPG, PNG, WEBP o GIF)")

    base = uuid.uuid4().hex
    extension, tipo = FORMATOS[formato]

    img = ImageOps.exif_transpose(img)
    img.thumbnail(TAMANO_MINIATURA)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        fondo = Image.new("RGB", img.size, "white")
        fondo.paste(img, mask=img.getchannel("A"))
        img = fondo
    elif img.mode != "RGB":
        img = img.convert("RGB")
    salida = io.BytesIO()
    img.save(salida, "JPEG", quality=82, optimize=True)

    try:
        original = almacenamiento.guardar(f"{base}{extension}", datos, tipo)
        miniatura = almacenamiento.guardar(f"{base}_mini.jpg", salida.getvalue(), "image/jpeg")
    except (RuntimeError, OSError):
        almacenamiento.log.exception("Error al guardar la imagen")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "No se pudo guardar la imagen. Probá de nuevo en unos minutos")
    return original, miniatura


def borrar_archivos(*referencias: str) -> None:
    almacenamiento.borrar(*referencias)


def obtener(db: Session, obra_id: int) -> Obra:
    obra = db.get(Obra, obra_id)
    if obra is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Obra no encontrada")
    return obra


def verificar_permiso(usuario: Usuario, obra: Obra) -> None:
    if not usuario.puede_gestionar(obra.colegio):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo podés modificar obras de tu colegio")


def colegio_para(usuario: Usuario, colegio: str) -> str:
    """Los invitados siempre publican con el colegio de su perfil; el admin elige libremente."""
    if usuario.es_admin:
        return limpiar(colegio, "Colegio")
    return usuario.colegio


@router.get("", response_model=list[ObraOut])
def listar(
    q: str | None = None,
    tecnica: str | None = None,
    colegio: str | None = None,
    anio: int | None = None,
    db: Session = Depends(get_db),
):
    consulta = select(Obra).order_by(Obra.creado.desc())
    if q:
        patron = f"%{q.strip()}%"
        consulta = consulta.where(
            or_(
                Obra.autor_nombre.ilike(patron),
                Obra.autor_apellido.ilike(patron),
                Obra.titulo.ilike(patron),
                Obra.tecnica.ilike(patron),
                Obra.colegio.ilike(patron),
            )
        )
    if tecnica:
        consulta = consulta.where(Obra.tecnica == tecnica)
    if colegio:
        consulta = consulta.where(Obra.colegio == colegio)
    if anio:
        consulta = consulta.where(Obra.anio == anio)
    return [a_salida(o) for o in db.scalars(consulta).all()]


@router.get("/filtros", response_model=FiltrosOut)
def filtros(db: Session = Depends(get_db)):
    return FiltrosOut(
        tecnicas=list(db.scalars(select(Obra.tecnica).distinct().order_by(func.lower(Obra.tecnica)))),
        colegios=list(db.scalars(select(Obra.colegio).distinct().order_by(func.lower(Obra.colegio)))),
        anios=list(db.scalars(select(Obra.anio).distinct().order_by(Obra.anio.desc()))),
    )


@router.get("/{obra_id}", response_model=ObraOut)
def detalle(obra_id: int, db: Session = Depends(get_db)):
    return a_salida(obtener(db, obra_id))


@router.post("", response_model=ObraOut, status_code=status.HTTP_201_CREATED)
def crear(
    autor_nombre: str = Form(...),
    autor_apellido: str = Form(...),
    anio: int = Form(..., ge=1900, le=2100),
    tecnica: str = Form(...),
    colegio: str = Form(""),
    titulo: str | None = Form(None),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_habilitado),
):
    campos = dict(
        titulo=limpiar(titulo, "Título", obligatorio=False),
        autor_nombre=limpiar(autor_nombre, "Nombre"),
        autor_apellido=limpiar(autor_apellido, "Apellido"),
        anio=anio,
        tecnica=limpiar(tecnica, "Técnica"),
        colegio=colegio_para(usuario, colegio),
    )
    original, miniatura = guardar_imagen(imagen)
    obra = Obra(**campos, imagen=original, miniatura=miniatura, subido_por_id=usuario.id)
    db.add(obra)
    db.commit()
    db.refresh(obra)
    return a_salida(obra)


@router.put("/{obra_id}", response_model=ObraOut)
def editar(
    obra_id: int,
    autor_nombre: str = Form(...),
    autor_apellido: str = Form(...),
    anio: int = Form(..., ge=1900, le=2100),
    tecnica: str = Form(...),
    colegio: str = Form(""),
    titulo: str | None = Form(None),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_habilitado),
):
    obra = obtener(db, obra_id)
    verificar_permiso(usuario, obra)
    obra.titulo = limpiar(titulo, "Título", obligatorio=False)
    obra.autor_nombre = limpiar(autor_nombre, "Nombre")
    obra.autor_apellido = limpiar(autor_apellido, "Apellido")
    obra.anio = anio
    obra.tecnica = limpiar(tecnica, "Técnica")
    obra.colegio = colegio_para(usuario, colegio)

    anteriores = None
    if imagen is not None and imagen.filename:
        anteriores = (obra.imagen, obra.miniatura)
        obra.imagen, obra.miniatura = guardar_imagen(imagen)

    db.commit()
    if anteriores:
        borrar_archivos(*anteriores)
    db.refresh(obra)
    return a_salida(obra)


@router.delete("/{obra_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(obra_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_habilitado)):
    obra = obtener(db, obra_id)
    verificar_permiso(usuario, obra)
    archivos = (obra.imagen, obra.miniatura)
    db.delete(obra)
    db.commit()
    borrar_archivos(*archivos)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
