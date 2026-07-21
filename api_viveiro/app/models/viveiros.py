from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class Viveiro(Base):
    __tablename__ = "viveiros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    slug = Column(String(50), nullable=False)
    modo_operacao = Column(String(20), nullable=False, default="nativo")
    ativo = Column(Boolean, nullable=False, default=True)
    id_empresa = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    data_cadastro = Column(DateTime, server_default=func.now())

    empresa = relationship("Empresa", back_populates="viveiros")
    funcionarios = relationship(
        "FuncionarioViveiro",
        back_populates="viveiro",
        cascade="all, delete-orphan",
    )
    genotipos = relationship("Genotipo", back_populates="viveiro")
