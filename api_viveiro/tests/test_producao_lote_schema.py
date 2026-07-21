from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.producao import (
    AtualizarEstagioLoteRequest,
    GrupoOperacaoLote,
    PromoverMudasLoteRequest,
)


def test_estagio_lote_limite_total():
    grupos = [GrupoOperacaoLote(id_especie=1, quantidade=25_001)]
    with pytest.raises(ValidationError):
        AtualizarEstagioLoteRequest(estagio_producao="apta_transferencia", grupos=grupos)


def test_promover_lote_aceita_varios_grupos():
    payload = PromoverMudasLoteRequest(
        id_canteiro_destino=1,
        grupos=[
            GrupoOperacaoLote(id_especie=1, quantidade=5000),
            GrupoOperacaoLote(id_especie=2, quantidade=3000),
        ],
    )
    assert sum(g.quantidade for g in payload.grupos) == 8000
