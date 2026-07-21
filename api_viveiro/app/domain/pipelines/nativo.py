"""Pipeline de produção — viveiro de mudas nativas."""

from __future__ import annotations

from typing import FrozenSet

from app.constants.viveiro_modo import MODO_NATIVO
from app.domain.pipelines.base import PipelineBase

_MODULOS = frozenset(
    {
        "coleta",
        "producao",
        "biblioteca",
        "prescricao",
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


class NativoPipeline(PipelineBase):
    @property
    def modo_operacao(self) -> str:
        return MODO_NATIVO

    def modulos_habilitados(self) -> FrozenSet[str]:
        return _MODULOS

    def modulos_nav_desabilitados(self) -> FrozenSet[str]:
        return frozenset({"florestal"})
