from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from config.database import Base

class DimCurso(Base):
    """
    DIMENSAO: Curso
    DESCRICAO: Armazena as informacoes dos cursos para fins analiticos.
    CAMADA: DW (Analitica) / Schema: dw

    ESTRUTURA:
    - sk_curso (Surrogate Key): Chave primaria gerada para o DW.
    - nk_curso (Natural Key): ID original proveniente do sistema operacional (OLTP).
    - preco_catalogo: Preco atual do curso no catalogo (util para analise de variacao).
    """
    __tablename__ = "dim_curso"
    __table_args__ = {"schema": "dw"}

    # Surrogate Key
    sk_curso = Column(Integer, primary_key=True, autoincrement=True)
    
    # Natural Key
    nk_curso = Column(Integer, nullable=False, index=True)
    
    # Atributos Descritivos e Metricas de Catalogo
    nome_curso = Column(String(100), nullable=False)
    carga_horaria = Column(Integer, nullable=False)
    preco_catalogo = Column(Numeric(10, 2), nullable=False)
    
    # Metadata para auditoria
    data_carga = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<DimCurso(sk={self.sk_curso}, nome='{self.nome_curso}')>"
