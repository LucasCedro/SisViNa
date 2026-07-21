from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class FuncionarioViveiro(Base):
    __tablename__ = "funcionario_viveiros"

    id_funcionario = Column(Integer, ForeignKey("funcionarios.id", ondelete="CASCADE"), primary_key=True)
    id_viveiro = Column(Integer, ForeignKey("viveiros.id", ondelete="CASCADE"), primary_key=True)

    funcionario = relationship("Funcionario", back_populates="viveiros_vinculo")
    viveiro = relationship("Viveiro", back_populates="funcionarios")
