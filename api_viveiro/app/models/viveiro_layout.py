from sqlalchemy import Column, ForeignKey, Integer, DateTime, Text, func

from app.database import Base


class ViveiroLayout(Base):
    """Layout SVG/planta baixa do viveiro (registro único por instalação)."""

    __tablename__ = "viveiro_layout"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_viveiro = Column(Integer, ForeignKey("viveiros.id"), nullable=False, unique=True, index=True)
    layout_json = Column(Text, nullable=False, default="{}")
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
