from sqlalchemy import Column, Integer, String, Date, DateTime, func
from config.database import Base

class DimAluno(Base):
    """
    DIMENSAO: Aluno
    DESCRICAO: Armazena os dados cadastrais dos alunos para fins analiticos.
    CAMADA: DW (Analitica) / Schema: dw

    ESTRUTURA:
    - sk_aluno (Surrogate Key): Chave primaria gerada para o DW.
    - nk_aluno (Natural Key): ID original proveniente do sistema operacional (OLTP).
    - data_carga: Data e hora em que o registro foi inserido no DW.
    """
    __tablename__ = "dim_aluno"
    __table_args__ = {"schema": "dw"}

    # Surrogate Key - Identificador unico e imutavel dentro do DW
    sk_aluno = Column(Integer, primary_key=True, autoincrement=True)
    
    # Natural Key - Elo de ligacao com o sistema operacional
    nk_aluno = Column(Integer, nullable=False, index=True)
    
    # Atributos Descritivos
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    data_nascimento = Column(Date, nullable=True)
    
    # Metadata para auditoria do ETL
    data_carga = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<DimAluno(sk={self.sk_aluno}, nome='{self.nome}')>"
