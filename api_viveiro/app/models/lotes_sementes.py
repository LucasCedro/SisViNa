from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import relationship

from app.database import Base


class LoteSementes(Base):
    __tablename__ = "lotes_sementes"

    id = Column(Integer, primary_key=True, index=True)
    id_viveiro = Column(Integer, ForeignKey("viveiros.id"), nullable=False, index=True)
    codigo_lote = Column(String(50), unique=True, nullable=False)
    id_coleta_sementes = Column(Integer, ForeignKey("coletas_sementes.id", ondelete="CASCADE"), nullable=True)
    origem_lote = Column(String(30), nullable=False, default="coleta")
    id_arvore_matriz = Column(Integer, ForeignKey("arvores_matriz.id", ondelete="CASCADE"), nullable=True)
    id_especie = Column(Integer, ForeignKey("especies.id"), nullable=False)
    quantidade_inicial = Column(Integer, nullable=False)
    quantidade_disponivel = Column(Integer, nullable=False)
    valor_total = Column(Numeric(14, 2))
    custo_unitario = Column(Numeric(12, 4))
    data_formacao_lote = Column(Date, nullable=False)
    beneficiamento = Column(Text)
    condicoes_armazenamento = Column(Text)
    status = Column(String(20), nullable=False, default="ativo")
    observacoes = Column(Text)
    data_registro = Column(DateTime, server_default=func.now())

    coleta = relationship("ColetaSementes", back_populates="lotes")
    arvore_matriz = relationship("ArvoreMatriz", back_populates="lotes")
    especie = relationship("Especie")
    testes = relationship("TesteSementes", back_populates="lote", cascade="all, delete-orphan")
    semeaduras = relationship("Semeadura", back_populates="lote")
