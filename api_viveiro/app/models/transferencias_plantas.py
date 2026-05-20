from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class TransferenciaPlanta(Base):
    __tablename__ = "transferencias_plantas"

    id = Column(Integer, primary_key=True, index=True)
    id_planta = Column(Integer, ForeignKey("plantas.id", ondelete="CASCADE"), nullable=False)
    id_canteiro_origem = Column(Integer, ForeignKey("canteiros.id"))
    id_canteiro_destino = Column(Integer, ForeignKey("canteiros.id"), nullable=False)
    status_anterior = Column(String(20))
    status_novo = Column(String(20), nullable=False)
    data_transferencia = Column(DateTime, nullable=False, server_default=func.now())
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"))
    observacoes = Column(Text)

    planta = relationship("Planta", back_populates="transferencias")
    canteiro_origem = relationship("Canteiro", foreign_keys=[id_canteiro_origem])
    canteiro_destino = relationship("Canteiro", foreign_keys=[id_canteiro_destino])
    funcionario = relationship("Funcionario")
