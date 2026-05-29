from sqlalchemy import Column, Integer, DateTime, Text, func

from app.database import Base


class ViveiroLayout(Base):
    """Layout SVG/planta baixa do viveiro (registro único por instalação)."""

    __tablename__ = "viveiro_layout"

    id = Column(Integer, primary_key=True, default=1)
    layout_json = Column(Text, nullable=False, default="{}")
    atualizado_em = Column(DateTime, default=func.now(), onupdate=func.now())
