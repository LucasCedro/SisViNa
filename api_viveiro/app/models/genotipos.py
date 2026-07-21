from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class Genotipo(Base):
    __tablename__ = "genotipos"

    id = Column(Integer, primary_key=True, index=True)
    id_viveiro = Column(Integer, ForeignKey("viveiros.id"), nullable=False, index=True)
    codigo = Column(String(50), nullable=False)
    nome = Column(String(100))
    fornecedor = Column(String(100))
    material_genetico = Column(String(100))
    observacoes = Column(Text)
    ativo = Column(Boolean, default=True)
    data_cadastro = Column(DateTime, server_default=func.now())

    viveiro = relationship("Viveiro", back_populates="genotipos")
    lotes = relationship("LoteProducao", back_populates="genotipo")
