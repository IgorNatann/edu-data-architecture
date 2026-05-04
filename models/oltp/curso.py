from sqlalchemy import Column, Integer, String, Text, Decimal, Date, func
from sqlalchemy.orm import relationship
from config.database import Base

class Curso(Base):
    """
    ENTIDADE: Curso
    DESCRICAO: Representa uma formacao ou disciplina oferecida pela escola.
    CAMADA: OLTP (Operacional) / Schema: oltp

    REGRAS DE NEGOCIO:
    1. O preco definido aqui eh o valor de catalogo (atual).
    2. A carga horaria eh fundamental para calculos de ticket medio por hora no DW.
    3. Um curso pode estar associado a infinitos itens de matricula de alunos diferentes.
    """
    __tablename__ = "curso"
    __table_args__ = {"schema": "oltp"}

    # Identificacao unica do curso
    id_curso = Column(Integer, primary_key=True, autoincrement=True)
    
    # Detalhes do Curso
    nome_curso = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Valores Monetarios e Metricas
    # Decimal(10,2) eh obrigatorio para evitar erros de precisao de ponto flutuante em dados financeiros.
    preco = Column(Decimal(10, 2), nullable=False)
    carga_horaria = Column(Integer, nullable=False)
    
    # Auditoria
    data_criacao = Column(Date, server_default=func.current_date())

    # RELACIONAMENTOS (SQLAlchemy ORM)
    # Relacionamento com a tabela pivot 'ItemMatricula'
    itens_matricula = relationship("ItemMatricula", back_populates="curso")

    def __repr__(self):
        """Representacao legivel do objeto."""
        return f"<Curso(id={self.id_curso}, nome='{self.nome_curso}')>"
