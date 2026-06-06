"""Testes SoD — vendas.edit vs vendas.approve."""

import pytest
from fastapi import HTTPException

from app.models.vendas import Venda
from app.services.vendas_sod import (
    assert_venda_editavel,
    validate_venda_create_status,
    validate_venda_update,
)


def _venda(status: str = "PENDENTE") -> Venda:
    return Venda(
        id=1,
        id_comprador=1,
        id_funcionario=1,
        data_venda=__import__("datetime").datetime(2026, 1, 1),
        valor_total=100.0,
        status=status,
    )


def test_gestor_nao_pode_marcar_pago_via_put():
    with pytest.raises(HTTPException) as exc:
        validate_venda_update(_venda(), {"status": "PAGO"}, ["gestor"])
    assert exc.value.status_code == 403
    assert "aprovar" in exc.value.detail.lower()


def test_gestor_pode_cancelar_pendente():
    validate_venda_update(_venda("PENDENTE"), {"status": "CANCELADO"}, ["gestor"])


def test_gestor_nao_edita_venda_paga():
    with pytest.raises(HTTPException) as exc:
        assert_venda_editavel(_venda("PAGO"), ["gestor"])
    assert exc.value.status_code == 403


def test_financeiro_nao_edita_pago_sem_approve_permission():
    with pytest.raises(HTTPException):
        assert_venda_editavel(_venda("PAGO"), ["financeiro"])


def test_create_sempre_pendente():
    assert validate_venda_create_status(None, ["gestor"]) == "PENDENTE"
    assert validate_venda_create_status("PENDENTE", ["financeiro"]) == "PENDENTE"
    with pytest.raises(HTTPException):
        validate_venda_create_status("PAGO", ["gestor"])
    with pytest.raises(HTTPException):
        validate_venda_create_status("PAGO", ["financeiro"])
