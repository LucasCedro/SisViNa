"""Registry único de pipelines — único ponto com if por modo."""

from __future__ import annotations

from app.constants.viveiro_modo import MODO_FLORESTAL, MODO_NATIVO, VALID_MODOS_OPERACAO
from app.domain.pipelines.base import PipelineBase
from app.domain.pipelines.florestal import FlorestalPipeline
from app.domain.pipelines.nativo import NativoPipeline
from app.security.viveiro_context import ViveiroContext

_REGISTRY: dict[str, type[PipelineBase]] = {
    MODO_NATIVO: NativoPipeline,
    MODO_FLORESTAL: FlorestalPipeline,
}


def get_pipeline(viveiro: ViveiroContext) -> PipelineBase:
    modo = viveiro.modo_operacao
    if modo not in VALID_MODOS_OPERACAO:
        raise ValueError(f"modo_operacao inválido: {modo}")
    cls = _REGISTRY.get(modo)
    if cls is None:
        raise ValueError(f"Pipeline não registrado para modo: {modo}")
    return cls(viveiro)
