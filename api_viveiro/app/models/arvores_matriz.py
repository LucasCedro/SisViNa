from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class ArvoreMatriz(Base):
    __tablename__ = "arvores_matriz"

    id = Column(Integer, primary_key=True, index=True)
    id_viveiro = Column(Integer, ForeignKey("viveiros.id"), nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    id_especie = Column(Integer, ForeignKey("especies.id"), nullable=False)
    cidade = Column(String(100))
    estado = Column(String(2))
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    tipo_coordenada = Column(String(20), nullable=False, default="geografica")
    utm_zona = Column(Integer)
    utm_easting = Column(Numeric(12, 2))
    utm_northing = Column(Numeric(12, 2))
    sementes_coletadas = Column(Integer, default=0)
    taxa_germinacao = Column(Numeric(5, 2))
    data_ultima_coleta = Column(Date)
    observacoes = Column(Text)
    municipio = Column(String(100))
    imovel_nome = Column(String(200))
    tipo_origem = Column(String(50))
    numero_autorizacao = Column(String(120))
    observacoes_legais = Column(Text)
    mes_inicio_frutificacao = Column(Integer)
    mes_fim_frutificacao = Column(Integer)
    estagio_frutificacao = Column(String(80))
    fenologia_observacoes = Column(Text)
    data_cadastro = Column(DateTime, server_default=func.now())

    especie = relationship("Especie", back_populates="arvores_matriz")
    lotes = relationship("LoteSementes", back_populates="arvore_matriz")
    coletas = relationship(
        "ColetaSementes",
        back_populates="arvore_matriz",
        cascade="all, delete-orphan",
        order_by="ColetaSementes.data_coleta",
    )
