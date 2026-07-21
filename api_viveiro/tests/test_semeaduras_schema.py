from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.semeaduras import SemeaduraCreate


def test_semeadura_rejeita_plantas_diferentes_de_sementes():
    with pytest.raises(ValidationError) as exc:
        SemeaduraCreate(
            id_lote_sementes=1,
            id_canteiro=1,
            data_semeadura=date.today(),
            quantidade_sementes_usadas=100,
            registrar_plantas=True,
            quantidade_plantas_registrar=202,
        )
    assert "igual" in str(exc.value).lower()


def test_semeadura_aceita_plantas_iguais_sementes():
    payload = SemeaduraCreate(
        id_lote_sementes=1,
        id_canteiro=1,
        data_semeadura=date.today(),
        quantidade_sementes_usadas=100,
        registrar_plantas=True,
        quantidade_plantas_registrar=100,
    )
    assert payload.quantidade_plantas_registrar == 100


def test_semeadura_sem_registrar_plantas_nao_exige_quantidade():
    payload = SemeaduraCreate(
        id_lote_sementes=1,
        data_semeadura=date.today(),
        quantidade_sementes_usadas=50,
        registrar_plantas=False,
    )
    assert payload.quantidade_plantas_registrar is None
