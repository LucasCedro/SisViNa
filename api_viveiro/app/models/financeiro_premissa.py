from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class FinanceiroPremissa(Base):
    __tablename__ = "financeiro_premissas"

    id = Column(Integer, primary_key=True, index=True)
    chave = Column(String(60), unique=True, nullable=False)
    nome = Column(String(120), nullable=False)
    descricao = Column(Text)
    # CUSTO → compõe CMV (lote/muda) | DESPESA → DRE (OPEX/comercial)
    natureza = Column(String(20), nullable=False, default="CUSTO")
    # insumo_medio | por_muda | por_lote | mensal | percentual_receita
    tipo_calculo = Column(String(30), nullable=False, default="por_muda")
    unidade = Column(String(40))
    valor = Column(Numeric(12, 4), nullable=False, default=0)
    quantidade = Column(Numeric(12, 4))
    id_insumo = Column(Integer, ForeignKey("insumos.id"), nullable=True)
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    data_atualizacao = Column(DateTime, server_default=func.now(), onupdate=func.now())

    insumo = relationship("Insumo", foreign_keys=[id_insumo])
