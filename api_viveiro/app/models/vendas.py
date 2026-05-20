# app/models/vendas.py
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base

class Venda(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    id_comprador = Column(Integer, ForeignKey("compradores.id"), nullable=False)
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    data_venda = Column(DateTime, nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    forma_pagamento = Column(String(20))
    status = Column(String(20))
    observacoes = Column(Text)
    data_registro = Column(DateTime, default=func.now())

    # Relacionamentos
    comprador = relationship("Comprador", back_populates="vendas")
    funcionario = relationship("Funcionario", back_populates="vendas")
    itens = relationship("ItemVenda", back_populates="venda")

class ItemVenda(Base):
    __tablename__ = "itens_venda"

    id = Column(Integer, primary_key=True, index=True)
    id_venda = Column(Integer, ForeignKey("vendas.id"), nullable=False)
    id_planta = Column(Integer, ForeignKey("plantas.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    valor_unitario = Column(Numeric(10, 2), nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    desconto = Column(Numeric(10, 2), default=0.00)
    data_entrega = Column(Date)
    status_entrega = Column(String(20), default='PENDENTE')
    data_registro = Column(DateTime, default=func.now())

    # Relacionamentos
    venda = relationship("Venda", back_populates="itens")
    planta = relationship("Planta", back_populates="itens_venda")