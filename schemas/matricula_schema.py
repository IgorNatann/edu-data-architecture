from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from decimal import Decimal

class ItemMatriculaBase(BaseModel):
    id_curso: int
    preco_momento: Decimal = Field(..., gt=0, decimal_places=2)
    data_inicio_prevista: Optional[date] = None

class ItemMatriculaCreate(ItemMatriculaBase):
    pass

class ItemMatriculaSchema(ItemMatriculaBase):
    id_item_matricula: int
    id_matricula: int

    class Config:
        from_attributes = True

class PagamentoBase(BaseModel):
    forma_pagamento: Optional[str] = Field(None, description="Ex: Cartao, Boleto, PIX")
    valor_pago: Optional[Decimal] = Field(None, gt=0)
    data_pagamento: Optional[date] = None
    status_pagamento: str = Field("Pendente")

class PagamentoSchema(PagamentoBase):
    id_pagamento: int
    id_matricula: int

    class Config:
        from_attributes = True

class MatriculaBase(BaseModel):
    id_aluno: int
    data_matricula: date = Field(default_factory=date.today)
    status: str = Field("Ativa")
    valor_total: Optional[Decimal] = Field(None, ge=0)

class MatriculaCreate(MatriculaBase):
    itens: List[ItemMatriculaCreate]

class MatriculaSchema(MatriculaBase):
    id_matricula: int
    itens: List[ItemMatriculaSchema] = []
    pagamento: Optional[PagamentoSchema] = None

    class Config:
        from_attributes = True
