from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    colegio: str | None
    habilitado: bool
    es_admin: bool
    puede_editar: bool
    creado: datetime


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=200)
    colegio: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=6, max_length=72)


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


class UsuarioUpdate(BaseModel):
    habilitado: bool | None = None
    colegio: str | None = Field(default=None, min_length=2, max_length=150)


class ObraOut(BaseModel):
    id: int
    titulo: str | None
    autor_nombre: str
    autor_apellido: str
    anio: int
    tecnica: str
    colegio: str
    imagen_url: str
    miniatura_url: str
    subido_por: str | None
    creado: datetime
    actualizado: datetime


class FiltrosOut(BaseModel):
    tecnicas: list[str]
    colegios: list[str]
    anios: list[int]
