from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    razao_social = Column(String(200), nullable=False)
    nome_fantasia = Column(String(100), nullable=False)
    slug = Column(String(50), nullable=False, unique=True)
    cnpj = Column(String(18))
    ativo = Column(Boolean, nullable=False, default=True)
    data_cadastro = Column(DateTime, server_default=func.now())

    viveiros = relationship("Viveiro", back_populates="empresa")
    funcionarios = relationship("Funcionario", back_populates="empresa")
