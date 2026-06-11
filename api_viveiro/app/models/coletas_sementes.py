from sqlalchemy import Column, Integer, Numeric, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class ColetaSementes(Base):
    __tablename__ = "coletas_sementes"

    id = Column(Integer, primary_key=True, index=True)
    id_arvore_matriz = Column(Integer, ForeignKey("arvores_matriz.id", ondelete="CASCADE"), nullable=False)
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    data_coleta = Column(Date, nullable=False)
    quantidade_sementes = Column(Integer, nullable=False)
    sementes_reservadas_teste = Column(Integer, nullable=False, default=0, server_default="0")
    horas_campo = Column(Numeric(8, 2))
    custo_campo_total = Column(Numeric(12, 2))
    observacoes = Column(Text)
    data_registro = Column(DateTime, server_default=func.now())

    arvore_matriz = relationship("ArvoreMatriz", back_populates="coletas")
    funcionario = relationship("Funcionario", back_populates="coletas_sementes")
    lotes = relationship("LoteSementes", back_populates="coleta", cascade="all, delete-orphan")
