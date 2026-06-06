from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class NotaFiscal(Base):
    __tablename__ = "notas_fiscais"

    id = Column(Integer, primary_key=True, index=True)
    id_venda = Column(Integer, ForeignKey("vendas.id"), nullable=False, index=True)
    ref_externa = Column(String(60), unique=True, nullable=False)
    chave_acesso = Column(String(44), unique=True)
    numero = Column(Integer)
    serie = Column(Integer)
    status = Column(String(30), nullable=False, default="processando")
    cstat = Column(String(10))
    xmotivo = Column(Text)
    recibo = Column(String(60))
    url_xml = Column(Text)
    url_danfe = Column(Text)
    payload_enviado = Column(JSONB)
    resposta_provedor = Column(JSONB)
    difal_snapshot = Column(JSONB)
    importacao_snapshot = Column(JSONB)
    data_emissao = Column(DateTime)
    data_registro = Column(DateTime, server_default=func.now())
    data_atualizacao = Column(DateTime, server_default=func.now(), onupdate=func.now())

    venda = relationship("Venda", back_populates="notas_fiscais")
    itens = relationship("NotaFiscalItem", back_populates="nota", cascade="all, delete-orphan")


class NotaFiscalItem(Base):
    __tablename__ = "notas_fiscais_itens"

    id = Column(Integer, primary_key=True, index=True)
    id_nota = Column(Integer, ForeignKey("notas_fiscais.id"), nullable=False, index=True)
    numero_item = Column(Integer, nullable=False)
    descricao = Column(String(200), nullable=False)
    ncm = Column(String(8), nullable=False)
    cfop = Column(String(4), nullable=False)
    csosn = Column(String(3), nullable=False)
    unidade = Column(String(6), nullable=False)
    quantidade = Column(Numeric(12, 4), nullable=False)
    valor_unitario = Column(Numeric(12, 4), nullable=False)
    valor_total = Column(Numeric(12, 2), nullable=False)

    nota = relationship("NotaFiscal", back_populates="itens")
