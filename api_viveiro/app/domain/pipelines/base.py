"""Contrato de pipeline de produção por modo de operação."""

from __future__ import annotations

from typing import FrozenSet, Protocol

from app.security.viveiro_context import ViveiroContext


class ProductionPipeline(Protocol):
  @property
  def modo_operacao(self) -> str: ...

  def modulos_habilitados(self) -> FrozenSet[str]: ...

  def modulos_nav_desabilitados(self) -> FrozenSet[str]:
    """Paths de navegação ocultos para este modo (complemento ao RBAC)."""
    ...


class PipelineBase:
    def __init__(self, viveiro: ViveiroContext):
        self.viveiro = viveiro

    @property
    def modo_operacao(self) -> str:
        return self.viveiro.modo_operacao
