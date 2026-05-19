# app/models/atividades.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship

from app.database import Base

class TipoAtividade(Base):
    __tablename__ = "tipos_atividades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(Text)
    gera_custo = Column(Boolean, default=False)

    # Relacionamentos
    atividades = relationship("Atividade", back_populates="tipo_atividade")

class Atividade(Base):
    __tablename__ = "atividades"

    id = Column(Integer, primary_key=True, index=True)
    id_tipo_atividade = Column(Integer, ForeignKey("tipos_atividades.id"), nullable=False)
    id_planta = Column(Integer, ForeignKey("plantas.id"), nullable=False)
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    data_atividade = Column(DateTime, nullable=False)
    descricao = Column(Text)
    custo_atividade = Column(Numeric(10, 2), default=0.00)
    observacoes = Column(Text)
    data_registro = Column(DateTime, default=func.now())

    # Relacionamentos
    tipo_atividade = relationship("TipoAtividade", back_populates="atividades")
    planta = relationship("Planta", back_populates="atividades")
    funcionario = relationship("Funcionario", back_populates="atividades")
    insumos_utilizados = relationship("InsumoAtividade", back_populates="atividade")

class InsumoAtividade(Base):
    __tablename__ = "insumos_atividades"

    id = Column(Integer, primary_key=True, index=True)
    id_atividade = Column(Integer, ForeignKey("atividades.id"), nullable=False)
    id_insumo = Column(Integer, ForeignKey("insumos.id"), nullable=False)
    quantidade_usada = Column(Numeric(10, 2), nullable=False)
    custo_total = Column(Numeric(10, 2))
    data_registro = Column(DateTime, default=func.now())

    # Relacionamentos
    atividade = relationship("Atividade", back_populates="insumos_utilizados")
    insumo = relationship("Insumo", back_populates="usos_atividades")