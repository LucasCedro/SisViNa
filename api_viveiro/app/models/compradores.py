# app/models/compradores.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, CheckConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base

class Comprador(Base):
    __tablename__ = "compradores"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(10), nullable=False)
    nome = Column(String(100), nullable=False)
    cpf_cnpj = Column(String(18), unique=True, nullable=False)
    telefone = Column(String(20))
    email = Column(String(100), unique=True)
    endereco = Column(String(200))
    cidade = Column(String(50))
    estado = Column(String(2))
    cep = Column(String(10))
    usuario = Column(String(50), unique=True)
    senha = Column(String(255))
    data_cadastro = Column(DateTime, default=func.now())
    ativo = Column(Boolean, default=True)

    # Verificar se o tipo é 'PF' ou 'PJ'
    __table_args__ = (
        CheckConstraint("tipo IN ('PF', 'PJ')", name="check_tipo"),
    )

    # Relacionamentos
    vendas = relationship("Venda", back_populates="comprador")