# app/models/pragas.py
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey, Enum, func
from sqlalchemy.orm import relationship

from app.database import Base

class TipoPraga(Base):
    __tablename__ = "tipos_pragas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)
    descricao = Column(Text)
    metodo_identificacao = Column(Text)
    data_cadastro = Column(DateTime, default=func.now())

    # Relacionamentos
    pragas_plantas = relationship("PragaPlanta", back_populates="tipo_praga")

class MetodoCombate(Base):
    __tablename__ = "metodos_combate"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    produto = Column(String(100))
    dosagem = Column(String(50))
    metodo_aplicacao = Column(Text)
    tempo_carencia = Column(Integer)  # em dias
    eficacia = Column(String(20))
    custo_unitario = Column(Numeric(10, 2))
    data_cadastro = Column(DateTime, default=func.now())

    # Relacionamentos
    combates_realizados = relationship("CombateRealizado", back_populates="metodo_combate")

class PragaPlanta(Base):
    __tablename__ = "pragas_plantas"

    id = Column(Integer, primary_key=True, index=True)
    id_planta = Column(Integer, ForeignKey("plantas.id"), nullable=False)
    id_tipo_praga = Column(Integer, ForeignKey("tipos_pragas.id"), nullable=False)
    data_identificacao = Column(Date, nullable=False)
    nivel_infestacao = Column(Enum('BAIXO', 'MEDIO', 'ALTO', 'CRITICO', name='nivel_infestacao'))
    observacoes = Column(Text)
    data_registro = Column(DateTime, default=func.now())

    # Relacionamentos
    planta = relationship("Planta", back_populates="pragas_plantas")
    tipo_praga = relationship("TipoPraga", back_populates="pragas_plantas")
    combates_realizados = relationship("CombateRealizado", back_populates="praga_planta")

class CombateRealizado(Base):
    __tablename__ = "combates_realizados"

    id = Column(Integer, primary_key=True, index=True)
    id_praga_planta = Column(Integer, ForeignKey("pragas_plantas.id"), nullable=False)
    id_metodo_combate = Column(Integer, ForeignKey("metodos_combate.id"), nullable=False)
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    data_aplicacao = Column(DateTime, nullable=False)
    quantidade_aplicada = Column(Numeric(10, 2))
    custo_total = Column(Numeric(10, 2))
    eficacia_observada = Column(String(20))
    observacoes = Column(Text)
    data_registro = Column(DateTime, default=func.now())

    # Relacionamentos
    praga_planta = relationship("PragaPlanta", back_populates="combates_realizados")
    metodo_combate = relationship("MetodoCombate", back_populates="combates_realizados")
    funcionario = relationship("Funcionario", back_populates="combates")