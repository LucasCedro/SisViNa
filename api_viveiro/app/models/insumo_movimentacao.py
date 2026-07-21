from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func

from app.database import Base


class InsumoMovimentacao(Base):
    __tablename__ = "insumo_movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    id_insumo = Column(Integer, ForeignKey("insumos.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(String(20), nullable=False)  # entrada | saida | ajuste
    quantidade = Column(Numeric(10, 2), nullable=False)
    valor_total = Column(Numeric(12, 2))
    preco_unitario = Column(Numeric(10, 4))
    saldo_quantidade = Column(Numeric(10, 2), nullable=False)
    data_movimento = Column(Date, nullable=False, index=True)
    status_pagamento = Column(String(20))  # PAGO | PENDENTE (entradas = compra)
    data_pagamento = Column(Date, nullable=True)
    observacao = Column(Text)
    criado_em = Column(DateTime, server_default=func.now())
