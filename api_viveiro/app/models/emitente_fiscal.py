from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func

from app.database import Base


class EmitenteFiscal(Base):
    """Cadastro fiscal do viveiro (emitente NF-e). Registro único por instalação."""

    __tablename__ = "emitente_fiscal"

    id = Column(Integer, primary_key=True, index=True)
    razao_social = Column(String(120), nullable=False)
    nome_fantasia = Column(String(120))
    cnpj = Column(String(18), nullable=False, unique=True)
    inscricao_estadual = Column(String(20), nullable=False)
    crt = Column(Integer, nullable=False, default=1)  # 1 = Simples Nacional
    cnae = Column(String(10))
    logradouro = Column(String(120), nullable=False)
    numero = Column(String(20), nullable=False)
    complemento = Column(String(60))
    bairro = Column(String(60), nullable=False)
    codigo_municipio_ibge = Column(String(7), nullable=False)
    municipio = Column(String(60), nullable=False)
    uf = Column(String(2), nullable=False)
    cep = Column(String(9), nullable=False)
    telefone = Column(String(20))
    email = Column(String(100))
    serie_nfe = Column(Integer, nullable=False, default=1)
    proximo_numero_nfe = Column(Integer, nullable=False, default=1)
    ambiente = Column(String(20), nullable=False, default="homologacao")  # homologacao | producao
    ativo = Column(Boolean, default=True)
    data_atualizacao = Column(DateTime, server_default=func.now(), onupdate=func.now())
