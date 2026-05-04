from sqlalchemy import Column, Integer, String, Date, Decimal, ForeignKey, func
from sqlalchemy.orm import relationship
from config.database import Base

class Pagamento(Base):
    """
    ENTIDADE: Pagamento
    DESCRICAO: Registra a quitação financeira de uma matricula.
    CAMADA: OLTP (Operacional) / Schema: oltp

    REGRAS DE NEGOCIO:
    1. Uma matricula so pode ter UM registro de pagamento (Garantido pelo UNIQUE na FK).
    2. O status inicial padrao eh 'Pendente'.
    3. Permite rastrear a forma de pagamento para analises de ticket medio e performance de canais.
    """
    __tablename__ = "pagamento"
    __table_args__ = {"schema": "oltp"}

    # Identificacao unica da transacao financeira
    id_pagamento = Column(Integer, primary_key=True, autoincrement=True)
    
    # FK com restricao UNIQUE: Transforma o relacionamento em 1:1 no nivel do banco de dados.
    id_matricula = Column(Integer, ForeignKey("oltp.matricula.id_matricula"), unique=True, nullable=False)
    
    # Detalhes Financeiros
    forma_pagamento = Column(String(50), nullable=True) # Ex: Cartao, Boleto, PIX
    valor_pago = Column(Decimal(10, 2), nullable=True)
    data_pagamento = Column(Date, nullable=True)
    status_pagamento = Column(String(30), default="Pendente") # Ex: Pendente, Pago, Estornado

    # RELACIONAMENTOS (SQLAlchemy ORM)
    # Lado 'One' do relacionamento 1:1 com Matricula
    matricula = relationship("Matricula", back_populates="pagamento")

    def __repr__(self):
        """Representacao legivel do objeto."""
        return f"<Pagamento(id={self.id_pagamento}, matricula={self.id_matricula}, status='{self.status_pagamento}')>"
