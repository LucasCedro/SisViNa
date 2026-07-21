from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class MovimentacaoLote(Base):
    __tablename__ = "movimentacoes_lote"

    id = Column(Integer, primary_key=True, index=True)
    id_lote_producao = Column(Integer, ForeignKey("lotes_producao.id"), nullable=False, index=True)
    tipo = Column(String(30), nullable=False)
    quantidade = Column(Integer, nullable=False)
    estagio_origem = Column(String(30))
    estagio_destino = Column(String(30))
    id_canteiro_origem = Column(Integer, ForeignKey("canteiros.id"))
    id_canteiro_destino = Column(Integer, ForeignKey("canteiros.id"))
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    observacoes = Column(Text)
    data_movimento = Column(DateTime, server_default=func.now())

    lote = relationship("LoteProducao", back_populates="movimentacoes")
    funcionario = relationship("Funcionario")
