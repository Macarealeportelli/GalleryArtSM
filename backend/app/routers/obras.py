import io
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from .. import almacenamiento
from ..config import MAX_UPLOAD_MB
from ..database import get_db
from ..models import ImagenProceso, Obra, Usuario, clave_orden
from ..schemas import FiltrosOut, ImagenProcesoOut, ObraOut, ProcesoUpdate
from ..security import usuario_habilitado

router = APIRouter(prefix="/api/obras", tags=["obras"])

FORMATOS = {
    "JPEG": (".jpg", "image/jpeg"),
    "PNG": (".png", "image/png"),
    "WEBP": (".webp", "image/webp"),
    "GIF": (".gif", "image/gif"),
}
TAMANO_MINIATURA = (900, 900)
MAX_IMAGENES_PROCESO = 12
MAX_TEXTO_PROCESO = 2000


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
        proceso_descripcion=obra.proceso_descripcion,
        proceso=[
            ImagenProcesoOut(
                id=p.id,
                imagen_url=almacenamiento.url_publica(p.imagen),
                miniatura_url=almacenamiento.url_publica(p.miniatura),
                descripcion=p.descripcion,
            )
            for p in obra.proceso
        ],
        creado=obra.creado,
        actualizado=obra.actualizado,
    )


def limpiar(valor: str | None, campo: str, obligatorio: bool = True, maximo: int | None = None) -> str | None:
    valor = (valor or "").strip()
    if not valor:
        if obligatorio:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"El campo «{campo}» es obligatorio")
        return None
    if maximo and len(valor) > maximo:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"El campo «{campo}» admite hasta {maximo} caracteres")
    return valor


def clave_alumno(nombre: str) -> str:
    """Normaliza el nombre del alumno para agrupar sin importar mayúsculas ni espacios."""
    return " ".join(nombre.split()).casefold()


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
    alumno: str | None = None,
    db: Session = Depends(get_db),
):
    consulta = (
        select(Obra)
        .options(selectinload(Obra.proceso), selectinload(Obra.subido_por))
        .order_by(Obra.creado.desc())
    )
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
    obras = db.scalars(consulta).all()
    if alumno:
        # Se filtra en Python para comparar sin distinguir mayúsculas (también con tildes)
        buscado = clave_alumno(alumno)
        obras = [o for o in obras if clave_alumno(o.alumno) == buscado]
    return [a_salida(o) for o in obras]


@router.get("/filtros", response_model=FiltrosOut)
def filtros(db: Session = Depends(get_db)):
    # Se ordena en Python: PostgreSQL no permite DISTINCT con ORDER BY lower(...)
    alumnos = {}
    for nombre, apellido in db.execute(select(Obra.autor_nombre, Obra.autor_apellido).distinct()):
        alumnos.setdefault(clave_alumno(f"{nombre} {apellido}"), (apellido, nombre))
    return FiltrosOut(
        # Ordenados por apellido y nombre, mostrados como "Nombre Apellido"
        alumnos=[f"{n} {a}" for a, n in sorted(alumnos.values(), key=lambda x: (clave_orden(x[0]), clave_orden(x[1])))],
        tecnicas=sorted(db.scalars(select(Obra.tecnica).distinct()), key=clave_orden),
        colegios=sorted(db.scalars(select(Obra.colegio).distinct()), key=clave_orden),
        anios=sorted(db.scalars(select(Obra.anio).distinct()), reverse=True),
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
    proceso_descripcion: str | None = Form(None),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_habilitado),
):
    campos = dict(
        titulo=limpiar(titulo, "Título", obligatorio=False),
        proceso_descripcion=limpiar(proceso_descripcion, "Proceso", obligatorio=False, maximo=MAX_TEXTO_PROCESO),
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
    proceso_descripcion: str | None = Form(None),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_habilitado),
):
    obra = obtener(db, obra_id)
    verificar_permiso(usuario, obra)
    obra.titulo = limpiar(titulo, "Título", obligatorio=False)
    obra.proceso_descripcion = limpiar(proceso_descripcion, "Proceso", obligatorio=False, maximo=MAX_TEXTO_PROCESO)
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
    archivos = [obra.imagen, obra.miniatura]
    for p in obra.proceso:
        archivos += [p.imagen, p.miniatura]
    db.delete(obra)
    db.commit()
    borrar_archivos(*archivos)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------- Proceso de trabajo ----------
# Cada foto se sube en un pedido aparte: Vercel no acepta envíos de más de 4,5 MB.


def obtener_imagen_proceso(obra: Obra, imagen_id: int) -> ImagenProceso:
    imagen = next((p for p in obra.proceso if p.id == imagen_id), None)
    if imagen is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Imagen de proceso no encontrada")
    return imagen


@router.post("/{obra_id}/proceso", response_model=ObraOut, status_code=status.HTTP_201_CREATED)
def agregar_proceso(
    obra_id: int,
    imagen: UploadFile = File(...),
    descripcion: str | None = Form(None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_habilitado),
):
    obra = obtener(db, obra_id)
    verificar_permiso(usuario, obra)
    if len(obra.proceso) >= MAX_IMAGENES_PROCESO:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"Cada obra admite hasta {MAX_IMAGENES_PROCESO} imágenes de proceso"
        )
    texto = limpiar(descripcion, "Descripción", obligatorio=False, maximo=300)
    original, miniatura = guardar_imagen(imagen)
    orden = max((p.orden for p in obra.proceso), default=0) + 1
    obra.proceso.append(ImagenProceso(imagen=original, miniatura=miniatura, descripcion=texto, orden=orden))
    db.commit()
    db.refresh(obra)
    return a_salida(obra)


@router.patch("/{obra_id}/proceso/{imagen_id}", response_model=ObraOut)
def editar_proceso(
    obra_id: int,
    imagen_id: int,
    datos: ProcesoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_habilitado),
):
    obra = obtener(db, obra_id)
    verificar_permiso(usuario, obra)
    imagen = obtener_imagen_proceso(obra, imagen_id)
    imagen.descripcion = limpiar(datos.descripcion, "Descripción", obligatorio=False)
    db.commit()
    db.refresh(obra)
    return a_salida(obra)


@router.delete("/{obra_id}/proceso/{imagen_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_proceso(
    obra_id: int,
    imagen_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(usuario_habilitado),
):
    obra = obtener(db, obra_id)
    verificar_permiso(usuario, obra)
    imagen = obtener_imagen_proceso(obra, imagen_id)
    archivos = (imagen.imagen, imagen.miniatura)
    obra.proceso.remove(imagen)
    db.commit()
    borrar_archivos(*archivos)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
