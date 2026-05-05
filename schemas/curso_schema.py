from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional
from decimal import Decimal

class CursoBase(BaseModel):
    """
    Schema base para Curso.
    """
    nome_curso: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = Field(None)
    preco: Decimal = Field(..., gt=0, decimal_places=2)
    carga_horaria: int = Field(..., gt=0, description="Carga horaria em horas")

    @field_validator('preco')
    @classmethod
    def validate_preco(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('O preco deve ser maior que zero')
        return v

class CursoCreate(CursoBase):
    """Schema para criacao de novos cursos."""
    pass

class CursoSchema(CursoBase):
    """Schema completo do curso."""
    id_curso: int
    data_criacao: date

    class Config:
        from_attributes = True
