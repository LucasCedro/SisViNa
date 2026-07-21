from sqlalchemy import Column, Integer, Text, Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import relationship

from app.database import Base


class Semeadura(Base):
    __tablename__ = "semeaduras"

    id = Column(Integer, primary_key=True, index=True)
    id_viveiro = Column(Integer, ForeignKey("viveiros.id"), nullable=False, index=True)
    id_lote_sementes = Column(Integer, ForeignKey("lotes_sementes.id"), nullable=False)
    id_canteiro = Column(Integer, ForeignKey("canteiros.id"))
    data_semeadura = Column(Date, nullable=False)
    quantidade_sementes_usadas = Column(Integer, nullable=False)
    quantidade_mudas_obtidas = Column(Integer)
    observacoes = Column(Text)
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    custo_sementes = Column(Numeric(12, 2), default=0)
    custo_insumos = Column(Numeric(12, 2), default=0)
    custo_indireto = Column(Numeric(12, 2), default=0)
    custo_total = Column(Numeric(12, 2), default=0)
    custo_unitario_muda = Column(Numeric(12, 2))
    data_registro = Column(DateTime, server_default=func.now())

    lote = relationship("LoteSementes", back_populates="semeaduras")
    canteiro = relationship("Canteiro")
    funcionario = relationship("Funcionario", back_populates="semeaduras")
    plantas = relationship("Planta", back_populates="semeadura")
