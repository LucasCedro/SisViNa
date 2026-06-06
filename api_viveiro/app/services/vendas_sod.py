"""Regras SoD (Segregação de Funções) para vendas."""

from __future__ import annotations

from typing import Iterable, Mapping

from fastapi import HTTPException, status

from app.models.vendas import Venda

_STATUS_EDITAVEL = frozenset({"PENDENTE"})
_STATUS_FECHADO = frozenset({"PAGO", "CANCELADO"})


class VendaSoDError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def assert_venda_editavel(venda: Venda, perfis: Iterable[str] | None) -> None:
    """vendas.edit — somente vendas em PENDENTE."""
    if venda.status in _STATUS_FECHADO:
        raise VendaSoDError(
            f"Venda com status '{venda.status}' não pode ser alterada. "
            "Requer vendas.approve para operações em vendas fechadas."
        )
    if venda.status not in _STATUS_EDITAVEL:
        raise VendaSoDError(f"Status '{venda.status}' não permite edição operacional.")


def validate_venda_update(
    venda: Venda,
    update_data: Mapping[str, object],
    perfis: Iterable[str] | None,
) -> None:
    """Valida PUT /vendas/{id} — bloqueia bypass de vendas.approve."""
    assert_venda_editavel(venda, perfis)

    novo_status = update_data.get("status")
    if novo_status is None:
        return

    if novo_status == "PAGO":
        raise VendaSoDError(
            "Transição para PAGO exige vendas.approve. Use POST /vendas/{id}/aprovar."
        )

    if novo_status not in _STATUS_EDITAVEL | {"CANCELADO"}:
        raise VendaSoDError(f"Transição de status inválida: {novo_status}")

    if novo_status == "CANCELADO" and venda.status != "PENDENTE":
        raise VendaSoDError("Somente vendas PENDENTE podem ser canceladas via edição.")


def validate_venda_create_status(status: str | None, perfis: Iterable[str] | None) -> str:
    """Nova venda sempre nasce PENDENTE (gestor prepara; financeiro aprova)."""
    if status and status != "PENDENTE":
        raise VendaSoDError(
            "Vendas devem ser criadas como PENDENTE. Aprovação via POST /vendas/{id}/aprovar."
        )
    return "PENDENTE"


def assert_pode_aprovar(venda: Venda) -> None:
    if venda.status != "PENDENTE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Somente vendas PENDENTE podem ser aprovadas (atual: {venda.status}).",
        )
