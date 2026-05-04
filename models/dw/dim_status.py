from sqlalchemy import Column, Integer, String
from config.database import Base

class DimStatus(Base):
    """
    DIMENSAO: Status
    DESCRICAO: Categoriza os possiveis estados de uma matricula.
    CAMADA: DW (Analitica) / Schema: dw

    ESTRUTURA:
    - sk_status (Surrogate Key): Identificador unico do status no DW.
    - codigo_status: O texto do status vindo do OLTP (Ex: Ativa, Trancada).
    - descricao_status: Uma descricao mais amigavel ou longa para relatorios.
    """
    __tablename__ = "dim_status"
    __table_args__ = {"schema": "dw"}

    # Surrogate Key
    sk_status = Column(Integer, primary_key=True, autoincrement=True)
    
    # Atributos
    codigo_status = Column(String(30), nullable=False, unique=True)
    descricao_status = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<DimStatus(sk={self.sk_status}, codigo='{self.codigo_status}')>"
