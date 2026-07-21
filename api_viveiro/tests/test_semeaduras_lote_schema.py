from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.semeaduras import (
    MAX_SEMEADURA_LOTE_ITENS,
    SemeaduraLoteCreate,
)


def test_lote_rejeita_lote_duplicado():
    with pytest.raises(ValidationError):
        SemeaduraLoteCreate(
            data_semeadura=date.today(),
            id_canteiro=1,
            itens=[
                {"id_lote_sementes": 1, "quantidade_sementes_usadas": 100},
                {"id_lote_sementes": 1, "quantidade_sementes_usadas": 50},
            ],
        )


def test_lote_aceita_varios_itens():
    payload = SemeaduraLoteCreate(
        data_semeadura=date.today(),
        id_canteiro=1,
        itens=[
            {"id_lote_sementes": 1, "quantidade_sementes_usadas": 5000},
            {"id_lote_sementes": 2, "quantidade_sementes_usadas": 2000},
        ],
    )
    assert len(payload.itens) == 2


def test_lote_limite_itens():
    itens = [
        {"id_lote_sementes": i, "quantidade_sementes_usadas": 1}
        for i in range(1, MAX_SEMEADURA_LOTE_ITENS + 2)
    ]
    with pytest.raises(ValidationError):
        SemeaduraLoteCreate(
            data_semeadura=date.today(),
            id_canteiro=1,
            itens=itens,
        )
