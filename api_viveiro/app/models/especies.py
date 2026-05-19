# app/models/especies.py
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, func
from sqlalchemy.orm import relationship

from app.database import Base

class Especie(Base):
    __tablename__ = "especies"

    id = Column(Integer, primary_key=True, index=True)
    nome_cientifico = Column(String(100), nullable=False, unique=True)
    nome_popular = Column(String(100))
    familia = Column(String(50))
    descricao = Column(Text)
    tempo_germinacao = Column(Integer)  # em dias
    tempo_crescimento = Column(Integer)  # em dias
    altura_maxima = Column(Numeric(5, 2))  # em metros
    data_cadastro = Column(DateTime, default=func.now())

    # Relacionamentos
    plantas = relationship("Planta", back_populates="especie")