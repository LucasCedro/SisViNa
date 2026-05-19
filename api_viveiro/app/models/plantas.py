# app/models/plantas.py
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey, Enum, func
from sqlalchemy.orm import relationship

from app.database import Base

class Planta(Base):
    __tablename__ = "plantas"

    id = Column(Integer, primary_key=True, index=True)
    id_especie = Column(Integer, ForeignKey("especies.id"), nullable=False)
    id_canteiro = Column(Integer, ForeignKey("canteiros.id"))
    codigo_rastreio = Column(String(20), unique=True)
    data_plantio = Column(Date)
    data_germinacao = Column(Date)
    altura_atual = Column(Numeric(5, 2))
    diametro_caule = Column(Numeric(5, 2))
    coordenada_x = Column(Numeric(10, 2))
    coordenada_y = Column(Numeric(10, 2))
    status = Column(Enum('SEMENTE', 'MUDA', 'JOVEM', 'ADULTA', 'VENDIDA', 'MORTA', name='status_planta'))
    observacoes = Column(Text)
    data_cadastro = Column(DateTime, default=func.now())
    preco_venda = Column(Numeric(10, 2))
    custo_atual = Column(Numeric(10, 2), default=0.00)

    # Relacionamentos
    especie = relationship("Especie", back_populates="plantas")
    canteiro = relationship("Canteiro", back_populates="plantas")
    atividades = relationship("Atividade", back_populates="planta")
    pragas_plantas = relationship("PragaPlanta", back_populates="planta")
    itens_venda = relationship("ItemVenda", back_populates="planta")