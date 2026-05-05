from pydantic import BaseModel, Field, computed_field
from datetime import date
from typing import List
from decimal import Decimal

class FatoMatriculaTransform(BaseModel):
    """
    Schema de transformacao para a Fato Matricula.
    Este schema recebe os dados brutos do OLTP e calcula as metricas 
    necessarias para a camada analitica (DW).
    """
    nk_matricula: int
    nk_aluno: int
    nk_curso: int
    data_matricula: date
    status_matricula: str
    
    # Precos dos itens para calculo de metricas agregadas
    # Recebemos a lista de precos de todos os cursos da matricula para calculo do total
    precos_itens: List[Decimal] = Field(..., description="Lista de precos (preco_momento) de todos os itens da matricula")

    @computed_field
    @property
    def valor_total(self) -> Decimal:
        """Soma total dos cursos na matricula."""
        return sum(self.precos_itens) if self.precos_itens else Decimal('0.00')

    @computed_field
    @property
    def qtd_cursos(self) -> int:
        """Quantidade total de cursos na matricula."""
        return len(self.precos_itens)

    @computed_field
    @property
    def valor_medio_curso(self) -> Decimal:
        """Valor medio por curso na matricula (Ticket Medio)."""
        if self.qtd_cursos == 0:
            return Decimal('0.00')
        return self.valor_total / Decimal(str(self.qtd_cursos))

class FatoMatriculaSchema(BaseModel):
    """
    Schema final que representa a estrutura da tabela fato no DW.
    Contem as SKs (Surrogate Keys) e as Metricas ja calculadas.
    """
    nk_matricula: int
    sk_aluno: int
    sk_curso: int
    sk_tempo: int
    sk_status: int
    
    valor_total: Decimal
    qtd_cursos: int
    valor_medio_curso: Decimal

    class Config:
        from_attributes = True
