from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class FatoMatricula(Base):
    """
    TABELA FATO: Matricula
    DESCRICAO: Tabela central do DW que armazena os fatos ocorridos (matriculas) 
               e suas métricas associadas.
    CAMADA: DW (Analitica) / Schema: dw

    ESTRUTURA:
    - sk_matricula: Chave primaria da fato.
    - nk_matricula: ID original da matricula no OLTP.
    - sk_aluno, sk_curso, sk_tempo, sk_status: Chaves estrangeiras analiticas.
    - Metricas: valor_total, qtd_cursos, valor_medio_curso.
    """
    __tablename__ = "fato_matricula"
    __table_args__ = {"schema": "dw"}

    # Chaves e Identificadores
    sk_matricula = Column(Integer, primary_key=True, autoincrement=True)
    nk_matricula = Column(Integer, nullable=False) # ID original para rastreabilidade

    # Chaves Estrangeiras (Ligacao com as Dimensoes)
    sk_aluno = Column(Integer, ForeignKey("dw.dim_aluno.sk_aluno"), nullable=False)
    sk_curso = Column(Integer, ForeignKey("dw.dim_curso.sk_curso"), nullable=False)
    sk_tempo = Column(Integer, ForeignKey("dw.dim_tempo.sk_tempo"), nullable=False)
    sk_status = Column(Integer, ForeignKey("dw.dim_status.sk_status"), nullable=False)

    # Metricas (Fatos Quantitativos)
    valor_total = Column(Numeric(10, 2), nullable=False)
    qtd_cursos = Column(Integer, nullable=False)
    valor_medio_curso = Column(Numeric(10, 2), nullable=False) # Ticket medio da matricula

    # RELACIONAMENTOS (Opcional no DW, mas util para o ORM)
    aluno = relationship("DimAluno")
    curso = relationship("DimCurso")
    tempo = relationship("DimTempo")
    status = relationship("DimStatus")

    def __repr__(self):
        return f"<FatoMatricula(sk={self.sk_matricula}, nk={self.nk_matricula}, total={self.valor_total})>"
