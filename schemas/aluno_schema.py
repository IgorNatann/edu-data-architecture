from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional
import re

class AlunoBase(BaseModel):
    """
    Schema base para Aluno com as validacoes fundamentais.
    """
    nome: str = Field(..., min_length=3, max_length=100, description="Nome completo do aluno")
    email: EmailStr = Field(..., description="E-mail unico do aluno")
    cpf: str = Field(..., description="CPF do aluno (formato: 000.000.000-00)")
    data_nascimento: Optional[date] = Field(None, description="Data de nascimento do aluno")

    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        """
        Valida o formato do CPF e remove caracteres nao numericos.
        """
        # Remove caracteres especiais
        cpf_clean = re.sub(r'\D', '', v)
        
        if len(cpf_clean) != 11:
            raise ValueError('CPF deve conter 11 digitos numericos')
        
        # Validacao basica de CPFs repetidos
        if cpf_clean == cpf_clean[0] * 11:
            raise ValueError('CPF invalido (digitos repetidos)')
            
        return v

class AlunoCreate(AlunoBase):
    """Schema para criacao de novos alunos (Input)."""
    pass

class AlunoSchema(AlunoBase):
    """Schema completo incluindo campos gerados pelo banco (Output)."""
    id_aluno: int
    data_cadastro: date

    class Config:
        from_attributes = True # Permite converter do SQLAlchemy para Pydantic
