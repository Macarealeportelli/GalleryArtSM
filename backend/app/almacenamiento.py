"""Guardado de las imágenes de las obras.

- Con BLOB_READ_WRITE_TOKEN (Vercel): se suben a Vercel Blob y se guarda su URL pública.
- Sin token (PC o servidor propio): se guardan en la carpeta UPLOAD_DIR y se sirven en /uploads.
"""

import json
import logging
import urllib.error
import urllib.request
from urllib.parse import urlencode

from .config import BLOB_READ_WRITE_TOKEN, UPLOAD_DIR

log = logging.getLogger("uvicorn.error")

USA_BLOB = bool(BLOB_READ_WRITE_TOKEN)
API_BLOB = "https://vercel.com/api/blob"
VERSION_API_BLOB = "13"  # la misma que usa la librería oficial @vercel/blob 2.8


def _pedido_blob(metodo: str, ruta: str, datos: bytes | None = None, headers: dict | None = None) -> dict:
    # El id del almacén está dentro del token: vercel_blob_rw_<storeId>_<secreto>
    store_id = BLOB_READ_WRITE_TOKEN.split("_")[3] if BLOB_READ_WRITE_TOKEN.count("_") >= 3 else ""
    pedido = urllib.request.Request(
        API_BLOB + ruta,
        data=datos,
        method=metodo,
        headers={
            "authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
            "x-api-version": VERSION_API_BLOB,
            "x-vercel-blob-store-id": store_id,
            "user-agent": "galeria-san-marcos",
            **({"x-content-length": str(len(datos))} if datos else {}),
            **(headers or {}),
        },
    )
    try:
        with urllib.request.urlopen(pedido, timeout=60) as respuesta:
            cuerpo = respuesta.read()
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"Vercel Blob respondió {e.code}: {detalle}") from e
    return json.loads(cuerpo) if cuerpo else {}


def guardar(nombre: str, datos: bytes, tipo: str) -> str:
    """Guarda el archivo y devuelve la referencia a guardar en la base (URL o nombre de archivo)."""
    if USA_BLOB:
        respuesta = _pedido_blob(
            "PUT",
            "/?" + urlencode({"pathname": f"obras/{nombre}"}),
            datos,
            {
                "x-vercel-blob-access": "public",
                "x-add-random-suffix": "0",
                "x-content-type": tipo,
                "x-cache-control-max-age": str(60 * 60 * 24 * 365),
            },
        )
        return respuesta["url"]
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / nombre).write_bytes(datos)
    return nombre


def borrar(*referencias: str) -> None:
    urls = [r for r in referencias if r.startswith(("http://", "https://"))]
    if urls and USA_BLOB:
        try:
            _pedido_blob("POST", "/delete", json.dumps({"urls": urls}).encode(), {"content-type": "application/json"})
        except (RuntimeError, OSError) as e:
            # La obra ya se borró de la base; un archivo huérfano no debe impedirlo
            log.warning("No se pudieron borrar imágenes de Vercel Blob: %s", e)
    for nombre in referencias:
        if not nombre.startswith(("http://", "https://")):
            (UPLOAD_DIR / nombre).unlink(missing_ok=True)


def url_publica(referencia: str) -> str:
    if referencia.startswith(("http://", "https://")):
        return referencia
    return f"/uploads/{referencia}"
