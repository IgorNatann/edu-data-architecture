from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base

class Matricula(Base):
    """
    ENTIDADE: Matricula
    DESCRICAO: Representa o vinculo formal de um aluno com a instituicao.
    CAMADA: OLTP (Operacional) / Schema: oltp

    REGRAS DE NEGOCIO:
    1. Uma matricula so existe vinculada a um aluno (FK obrigada).
    2. O status inicial padrao eh 'Ativa'.
    3. O valor_total deve ser a soma dos itens vinculados (calculado via ETL ou trigger).
    4. Possui um relacionamento 1:1 com a tabela de Pagamento.
    """
    __tablename__ = "matricula"
    __table_args__ = {"schema": "oltp"}

    # Identificacao unica da transacao de matricula
    id_matricula = Column(Integer, primary_key=True, autoincrement=True)
    
    # Chave Estrangeira: Referencia explictamente o schema 'oltp' para evitar ambiguidade.
    id_aluno = Column(Integer, ForeignKey("oltp.aluno.id_aluno"), nullable=False)
    
    # Detalhes do Registro
    data_matricula = Column(Date, nullable=False, server_default=func.current_date())
    status = Column(String(30), default="Ativa") # Ex: Ativa, Trancada, Concluida, Cancelada
    valor_total = Column(Numeric(10, 2), nullable=True)

    # RELACIONAMENTOS (SQLAlchemy ORM)
    # Lado 'Many' do relacionamento com Aluno
    aluno = relationship("Aluno", back_populates="matriculas")
    
    # Lado 'One' do relacionamento com Itens (Uma matricula tem N cursos/itens)
    itens = relationship("ItemMatricula", back_populates="matricula", cascade="all, delete-orphan")
    
    # Lado 'One' do relacionamento 1:1 com Pagamento (uselist=False garante a unicidade no ORM)
    pagamento = relationship("Pagamento", back_populates="matricula", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        """Representacao legivel do objeto."""
        return f"<Matricula(id={self.id_matricula}, aluno_id={self.id_aluno}, status='{self.status}')>"
