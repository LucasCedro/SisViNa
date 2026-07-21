from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, func

from app.database import Base


class AuditoriaCrossTenant(Base):
    __tablename__ = "auditoria_cross_tenant"

    id = Column(Integer, primary_key=True, index=True)
    data_evento = Column(DateTime, server_default=func.now(), nullable=False)
    id_funcionario = Column(Integer, ForeignKey("funcionarios.id"), nullable=True)
    usuario = Column(String(50))
    id_empresa_origem = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    id_empresa_alvo = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    id_viveiro_alvo = Column(Integer, ForeignKey("viveiros.id"), nullable=True)
    acao = Column(String(80), nullable=False)
    recurso_tipo = Column(String(80))
    recurso_id = Column(Integer)
    detalhes = Column(JSON)
    ip_origem = Column(String(45))
    bloqueado = Column(Boolean, nullable=False, default=False)
