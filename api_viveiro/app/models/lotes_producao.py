from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class LoteProducao(Base):
    __tablename__ = "lotes_producao"

    id = Column(Integer, primary_key=True, index=True)
    id_viveiro = Column(Integer, ForeignKey("viveiros.id"), nullable=False, index=True)
    id_genotipo = Column(Integer, ForeignKey("genotipos.id"), nullable=False)
    codigo_lote = Column(String(30), nullable=False)
    data_entrada = Column(Date, nullable=False)
    quantidade_inicial = Column(Integer, nullable=False)
    quantidade_atual = Column(Integer, nullable=False)
    estagio = Column(String(30), nullable=False, default="entrada_material")
    id_canteiro = Column(Integer, ForeignKey("canteiros.id"))
    observacoes = Column(Text)
    data_registro = Column(DateTime, server_default=func.now())

    genotipo = relationship("Genotipo", back_populates="lotes")
    canteiro = relationship("Canteiro")
    movimentacoes = relationship("MovimentacaoLote", back_populates="lote")
