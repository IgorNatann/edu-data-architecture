from sqlalchemy import Column, Integer, String, Date
from config.database import Base

class DimTempo(Base):
    """
    DIMENSAO: Tempo
    DESCRICAO: Dimensao fundamental para analises temporais ricas e performaticas.
    CAMADA: DW (Analitica) / Schema: dw

    REGRAS:
    - Nao possui Natural Key (NK) vinda do OLTP.
    - Eh gerada artificialmente para evitar calculos de data em tempo de execucao nas queries.
    """
    __tablename__ = "dim_tempo"
    __table_args__ = {"schema": "dw"}

    # Surrogate Key
    sk_tempo = Column(Integer, primary_key=True, autoincrement=True)
    
    # Atributos de Data
    data_completa = Column(Date, nullable=False, unique=True, index=True)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    dia = Column(Integer, nullable=False)
    trimestre = Column(Integer, nullable=False)
    
    # Atributos Descritivos (Para nomes amigaveis em graficos)
    nome_mes = Column(String(20), nullable=False)   # Ex: Janeiro, Fevereiro
    dia_semana = Column(String(20), nullable=False) # Ex: Segunda-feira

    def __repr__(self):
        return f"<DimTempo(sk={self.sk_tempo}, data='{self.data_completa}')>"
