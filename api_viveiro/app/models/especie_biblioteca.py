from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class EspecieBiblioteca(Base):
    __tablename__ = "especies_biblioteca"

    id_especie = Column(Integer, ForeignKey("especies.id", ondelete="CASCADE"), primary_key=True)
    resumo_manejo = Column(Text)
    imagem_arvore = Column(String(255))
    imagem_semente = Column(String(255))
    imagem_folha = Column(String(255))
    imagens_externas = Column(JSON)
    imagens_externas_atualizado_em = Column(DateTime)
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())

    especie = relationship("Especie", back_populates="biblioteca")
