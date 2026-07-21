"""Pipeline de produção — viveiro florestal (mudas plantadas)."""

from __future__ import annotations

from typing import FrozenSet

from app.constants.viveiro_modo import MODO_FLORESTAL
from app.domain.pipelines.base import PipelineBase

_MODULOS = frozenset(
    {
        "florestal",
        "viveiro",
        "fitossanidade",
        "fertilizacao",
        "estoques",
        "vendas",
        "financeiro",
        "contabilidade",
        "home",
    }
)


class FlorestalPipeline(PipelineBase):
    @property
    def modo_operacao(self) -> str:
        return MODO_FLORESTAL

    def modulos_habilitados(self) -> FrozenSet[str]:
        return _MODULOS

    def modulos_nav_desabilitados(self) -> FrozenSet[str]:
        return frozenset({"coleta", "producao", "biblioteca", "prescricao"})
