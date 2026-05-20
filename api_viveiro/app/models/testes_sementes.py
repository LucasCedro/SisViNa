from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class TesteSementes(Base):
    __tablename__ = "testes_sementes"

    id = Column(Integer, primary_key=True, index=True)
    id_lote_sementes = Column(Integer, ForeignKey("lotes_sementes.id", ondelete="CASCADE"), nullable=False)
    data_teste = Column(Date, nullable=False)
    tipo_teste = Column(String(40), nullable=False)
    metodologia = Column(Text)
    repeticoes = Column(Integer, default=1)
    sementes_avaliadas = Column(Integer)
    percentual_resultado = Column(Numeric(5, 2), nullable=False)
    observacoes = Column(Text)
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    data_registro = Column(DateTime, server_default=func.now())

    lote = relationship("LoteSementes", back_populates="testes")
    funcionario = relationship("Funcionario", back_populates="testes_sementes")
