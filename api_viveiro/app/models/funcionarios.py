# app/models/funcionarios.py
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, Boolean, JSON, func
from sqlalchemy.orm import relationship

from app.database import Base

class Funcionario(Base):
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    rg = Column(String(20))
    data_nascimento = Column(Date)
    telefone = Column(String(20))
    email = Column(String(100), unique=True)
    endereco = Column(String(200))
    cargo = Column(String(50))
    data_contratacao = Column(Date)
    salario = Column(Numeric(10, 2))
    usuario = Column(String(50), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    perfis = Column(JSON, nullable=True)
    data_cadastro = Column(DateTime, default=func.now())

    # Relacionamentos
    atividades = relationship("Atividade", back_populates="funcionario")
    vendas = relationship("Venda", back_populates="funcionario")
    combates = relationship("CombateRealizado", back_populates="funcionario")
    coletas_sementes = relationship("ColetaSementes", back_populates="funcionario")
    testes_sementes = relationship("TesteSementes", back_populates="funcionario")
    semeaduras = relationship("Semeadura", back_populates="funcionario")