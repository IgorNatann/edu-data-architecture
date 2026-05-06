"""
Schemas Pydantic para Matricula, Item de Matricula e Pagamento.

Este modulo centraliza a validacao das tres entidades que compõem o fluxo
transacional de uma matricula. Estao agrupadas em um unico arquivo pois
compartilham o mesmo contexto de negocio e possuem dependencia direta
(MatriculaSchema contem ItemMatriculaSchema e PagamentoSchema).
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from decimal import Decimal


class ItemMatriculaBase(BaseModel):
    """
    Schema base para Item de Matricula.
    Representa um curso especifico incluido em uma matricula.

    REGRA DE NEGOCIO:
    - 'preco_momento' registra o valor do curso no ato da venda,
      independente de alteracoes futuras no catalogo.
    """
    id_curso: int
    preco_momento: Decimal = Field(..., gt=0, decimal_places=2)
    data_inicio_prevista: Optional[date] = None

class ItemMatriculaCreate(ItemMatriculaBase):
    """Schema para criacao de novos itens de matricula (Input)."""
    pass

class ItemMatriculaSchema(ItemMatriculaBase):
    """Schema completo do item incluindo campos gerados pelo banco (Output)."""
    id_item_matricula: int
    id_matricula: int

    class Config:
        from_attributes = True


class PagamentoBase(BaseModel):
    """
    Schema base para Pagamento.
    Representa a quitacao financeira vinculada a uma matricula.

    REGRA DE NEGOCIO:
    - O status inicial padrao eh 'Pendente'.
    - Formas de pagamento aceitas: Cartao, Boleto, PIX (validacao flexivel).
    """
    forma_pagamento: Optional[str] = Field(None, description="Ex: Cartao, Boleto, PIX")
    valor_pago: Optional[Decimal] = Field(None, gt=0)
    data_pagamento: Optional[date] = None
    status_pagamento: str = Field("Pendente")

class PagamentoSchema(PagamentoBase):
    """Schema completo do pagamento incluindo campos gerados pelo banco (Output)."""
    id_pagamento: int
    id_matricula: int

    class Config:
        from_attributes = True


class MatriculaBase(BaseModel):
    """
    Schema base para Matricula.
    Representa o vinculo formal de um aluno com a instituicao.

    REGRA DE NEGOCIO:
    - O status inicial padrao eh 'Ativa'.
    - O valor_total pode ser nulo na criacao (calculado via ETL a partir dos itens).
    """
    id_aluno: int
    data_matricula: date = Field(default_factory=date.today)
    status: str = Field("Ativa")
    valor_total: Optional[Decimal] = Field(None, ge=0)

class MatriculaCreate(MatriculaBase):
    """Schema para criacao de novas matriculas com seus itens (Input)."""
    itens: List[ItemMatriculaCreate]

class MatriculaSchema(MatriculaBase):
    """
    Schema completo da matricula incluindo itens e pagamento aninhados (Output).
    Utiliza 'from_attributes = True' para converter diretamente do SQLAlchemy.
    """
    id_matricula: int
    itens: List[ItemMatriculaSchema] = []
    pagamento: Optional[PagamentoSchema] = None

    class Config:
        from_attributes = True
