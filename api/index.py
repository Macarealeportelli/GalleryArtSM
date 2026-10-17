"""Punto de entrada del backend en Vercel.

Vercel ejecuta este archivo como una función de Python y le envía todos los pedidos a /api/...
(ver las reglas "rewrites" en vercel.json). El código del backend está en backend/app.
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app, inicializar  # noqa: E402

try:
    inicializar()
except Exception:
    # Se reintenta en el próximo arranque; el error queda en los registros de Vercel
    logging.getLogger("uvicorn.error").exception("Error al inicializar la base de datos")

__all__ = ["app"]
