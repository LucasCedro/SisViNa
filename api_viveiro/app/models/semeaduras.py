from sqlalchemy import Column, Integer, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class Semeadura(Base):
    __tablename__ = "semeaduras"

    id = Column(Integer, primary_key=True, index=True)
    id_lote_sementes = Column(Integer, ForeignKey("lotes_sementes.id"), nullable=False)
    id_canteiro = Column(Integer, ForeignKey("canteiros.id"))
    data_semeadura = Column(Date, nullable=False)
    quantidade_sementes_usadas = Column(Integer, nullable=False)
    quantidade_mudas_obtidas = Column(Integer)
    observacoes = Column(Text)
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    data_registro = Column(DateTime, server_default=func.now())

    lote = relationship("LoteSementes", back_populates="semeaduras")
    canteiro = relationship("Canteiro")
    funcionario = relationship("Funcionario", back_populates="semeaduras")
    plantas = relationship("Planta", back_populates="semeadura")
