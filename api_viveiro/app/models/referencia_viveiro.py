from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ViveiroRegraGlobal(Base):
    """Parâmetros globais do viveiro (configuráveis)."""

    __tablename__ = "viveiro_regras_globais"

    chave = Column(String(80), primary_key=True)
    valor_numerico = Column(Numeric(12, 4))
    valor_texto = Column(Text)
    descricao = Column(Text)
    fonte = Column(String(200), nullable=False, default="SisViNa")
    ativo = Column(Boolean, nullable=False, default=True)


class EspecieFichaEmbrapa(Base):
    """Ficha técnica de produção por espécie."""

    __tablename__ = "especies_ficha_embrapa"

    id_especie = Column(
        Integer,
        ForeignKey("especies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    nome_cientifico_ref = Column(String(150))
    fitofisionomia = Column(Text)
    mes_coleta_inicio = Column(SmallInteger)  # 1-12
    mes_coleta_fim = Column(SmallInteger)
    armazenamento_tipo = Column(String(40))  # recalcitrante, ortodoxa, etc.
    armazenamento_obs = Column(Text)
    profundidade_semeadura_cm_min = Column(Numeric(4, 2))
    profundidade_semeadura_cm_max = Column(Numeric(4, 2))
    dias_inicio_germinacao = Column(Integer)
    pct_germinacao_tipico = Column(Numeric(5, 2))
    substrato_tipo = Column(SmallInteger)  # 1, 2 ou 3
    conduz_pleno_sol = Column(Boolean)
    meses_permanencia_viveiro = Column(Integer)
    meses_permanencia_viveiro_max = Column(Integer)
    dias_rustificacao_minimo = Column(Integer)  # sobrescreve global se preenchido
    altura_campo_cm_min = Column(Numeric(5, 2))
    altura_campo_cm_max = Column(Numeric(5, 2))
    adubacao_obs = Column(Text)
    observacoes_gerais = Column(Text)
    fonte = Column(String(200), nullable=False, default="SisViNa")
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())

    especie = relationship("Especie", back_populates="ficha_embrapa")
