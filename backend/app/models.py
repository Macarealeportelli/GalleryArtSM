from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def ahora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    # Colegio del invitado: solo puede gestionar obras de este colegio.
    colegio: Mapped[str | None] = mapped_column(String(150), nullable=True)
    # Un administrador puede desactivar una cuenta para bloquearla.
    habilitado: Mapped[bool] = mapped_column(default=True)
    # Los administradores se definen en admins.json, no desde la web.
    es_admin: Mapped[bool] = mapped_column(default=False)
    creado: Mapped[datetime] = mapped_column(default=ahora)

    @property
    def puede_editar(self) -> bool:
        """Puede subir obras (las de su colegio si es invitado)."""
        return self.es_admin or (self.habilitado and bool(self.colegio))

    def puede_gestionar(self, colegio: str) -> bool:
        """Puede editar/borrar una obra del colegio indicado."""
        if self.es_admin:
            return True
        return self.puede_editar and mismo_colegio(self.colegio, colegio)


def mismo_colegio(a: str | None, b: str | None) -> bool:
    return bool(a and b) and " ".join(a.split()).casefold() == " ".join(b.split()).casefold()


class Obra(Base):
    __tablename__ = "obras"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    autor_nombre: Mapped[str] = mapped_column(String(100))
    autor_apellido: Mapped[str] = mapped_column(String(100), index=True)
    anio: Mapped[int] = mapped_column(index=True)
    tecnica: Mapped[str] = mapped_column(String(150), index=True)
    colegio: Mapped[str] = mapped_column(String(150), index=True)
    imagen: Mapped[str] = mapped_column(String(255))
    miniatura: Mapped[str] = mapped_column(String(255))
    subido_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    creado: Mapped[datetime] = mapped_column(default=ahora)
    actualizado: Mapped[datetime] = mapped_column(default=ahora, onupdate=ahora)

    subido_por: Mapped[Usuario | None] = relationship()
