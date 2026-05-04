from sqlalchemy import Column, Integer, String, Date, func
from sqlalchemy.orm import relationship
from config.database import Base

class Aluno(Base):
    """
    ENTIDADE: Aluno
    DESCRICAO: Representa um estudante matriculado na instituicao.
    CAMADA: OLTP (Operacional) / Schema: oltp

    REGRAS DE NEGOCIO:
    1. O CPF e o Email devem ser unicos para evitar duplicidade de registros.
    2. O id_aluno eh a chave primaria (PK) e serve como Natural Key (NK) para o DW.
    3. Ao deletar um aluno, suas matriculas sao removidas automaticamente (Cascade).
    """
    __tablename__ = "aluno"
    __table_args__ = {"schema": "oltp"} # Garante o isolamento logico na camada operacional

    # Identificacao unica do aluno no sistema transacional
    id_aluno = Column(Integer, primary_key=True, autoincrement=True)
    
    # Informacoes de Cadastro
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    
    # Dados Temporais
    data_nascimento = Column(Date, nullable=True)
    data_cadastro = Column(Date, server_default=func.current_date()) # Preenchido automaticamente pelo BD

    # RELACIONAMENTOS (SQLAlchemy ORM)
    # back_populates: Mantem o objeto Aluno e Matricula sincronizados em memoria.
    # cascade: 'all, delete-orphan' garante integridade referencial ao excluir o pai.
    matriculas = relationship("Matricula", back_populates="aluno", cascade="all, delete-orphan")

    def __repr__(self):
        """Representacao legivel do objeto para logs e debug."""
        return f"<Aluno(id={self.id_aluno}, nome='{self.nome}')>"
