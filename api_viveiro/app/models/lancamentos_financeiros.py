from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class LancamentoFinanceiro(Base):
    __tablename__ = "lancamentos_financeiros"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(10), nullable=False)
    descricao = Column(String(200), nullable=False)
    categoria = Column(String(80), nullable=False)
    data_lancamento = Column(Date, nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    forma_pagamento = Column(String(40))
    observacoes = Column(Text)
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"))
    data_registro = Column(DateTime, default=func.now())

    funcionario = relationship("Funcionario")
