from sqlalchemy import Column, Integer, Date, Decimal, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class ItemMatricula(Base):
    """
    ENTIDADE: ItemMatricula
    DESCRICAO: Tabela de ligacao (pivot) que detalha os cursos inclusos em uma matricula.
    CAMADA: OLTP (Operacional) / Schema: oltp

    REGRAS DE NEGOCIO (CRITICAS):
    1. Resolve o relacionamento N:N entre Matricula e Curso.
    2. 'preco_momento': Congela o valor do curso no ato da venda. Mesmo que o preco 
       do curso mude no catalogo amanha, o valor desta venda permanece imutavel. 
       Isso eh vital para a integridade financeira e auditoria.
    3. 'data_inicio_prevista': Permite gerenciar a sazonalidade e inicio de turmas.
    """
    __tablename__ = "item_matricula"
    __table_args__ = {"schema": "oltp"}

    # Identificacao unica do item (linha da fatura)
    id_item_matricula = Column(Integer, primary_key=True, autoincrement=True)
    
    # Chaves Estrangeiras (Relacionamento Triangulado)
    id_matricula = Column(Integer, ForeignKey("oltp.matricula.id_matricula"), nullable=False)
    id_curso = Column(Integer, ForeignKey("oltp.curso.id_curso"), nullable=False)
    
    # Historico e Logistica
    preco_momento = Column(Decimal(10, 2), nullable=False) # Valor real transacionado
    data_inicio_prevista = Column(Date, nullable=True)

    # RELACIONAMENTOS (SQLAlchemy ORM)
    matricula = relationship("Matricula", back_populates="itens")
    curso = relationship("Curso", back_populates="itens_matricula")

    def __repr__(self):
        """Representacao legivel do objeto."""
        return f"<ItemMatricula(id={self.id_item_matricula}, matricula={self.id_matricula}, curso={self.id_curso})>"
