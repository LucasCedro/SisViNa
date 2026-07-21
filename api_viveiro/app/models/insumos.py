# app/models/insumos.py
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base

class Insumo(Base):
    __tablename__ = "insumos"
    __table_args__ = (UniqueConstraint("id_empresa", "nome", name="uq_insumos_empresa_nome"),)

    id = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    descricao = Column(Text)
    unidade_medida = Column(String(20))
    quantidade_estoque = Column(Numeric(10, 2))
    preco_unitario = Column(Numeric(10, 2))
    valor_estoque = Column(Numeric(12, 2), default=0)
    estoque_minimo = Column(Numeric(10, 2), default=0)
    estoque_maximo = Column(Numeric(10, 2))
    data_ultima_compra = Column(Date)
    fornecedor = Column(String(100))
    data_cadastro = Column(DateTime, default=func.now())

    # Relacionamentos
    usos_atividades = relationship("InsumoAtividade", back_populates="insumo")