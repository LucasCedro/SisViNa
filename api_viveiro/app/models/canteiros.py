# app/models/canteiros.py
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Numeric, Boolean, func
from sqlalchemy.orm import relationship

from app.database import Base

class Canteiro(Base):
    __tablename__ = "canteiros"

    id = Column(Integer, primary_key=True, index=True)
    id_viveiro = Column(Integer, ForeignKey("viveiros.id"), nullable=False, index=True)
    nome = Column(String(50), nullable=False)
    descricao = Column(Text)
    area_total = Column(Numeric(10, 2))  # em metros quadrados
    localizacao = Column(String(100))
    tipo_solo = Column(String(50))
    tipo_local = Column(String(20), nullable=False, default="canteiro")
    data_criacao = Column(DateTime, default=func.now())
    ativo = Column(Boolean, default=True)

    # Relacionamentos
    plantas = relationship("Planta", back_populates="canteiro")