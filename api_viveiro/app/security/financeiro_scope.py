"""Escopo financeiro por request (ContextVar) — evita threading em 90+ queries."""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select

from app.models.insumo_movimentacao import InsumoMovimentacao
from app.models.insumos import Insumo
from app.models.lancamentos_financeiros import LancamentoFinanceiro
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta
from app.models.vendas import Venda

_scope_cv: ContextVar[Optional["FinanceiroScope"]] = ContextVar("financeiro_scope", default=None)


@dataclass(frozen=True)
class FinanceiroScope:
    id_viveiro: int
    id_empresa: int


def set_financeiro_scope(scope: FinanceiroScope) -> Token:
    return _scope_cv.set(scope)


def reset_financeiro_scope(token: Token) -> None:
    _scope_cv.reset(token)


def get_fin_scope() -> Optional[FinanceiroScope]:
    return _scope_cv.get()


def venda_scope_clause():
    scope = get_fin_scope()
    if scope is not None:
        return Venda.id_viveiro == scope.id_viveiro
    return None


def planta_scope_clause():
    scope = get_fin_scope()
    if scope is not None:
        return Planta.id_viveiro == scope.id_viveiro
    return None


def lancamento_scope_clause():
    scope = get_fin_scope()
    if scope is not None:
        return LancamentoFinanceiro.id_empresa == scope.id_empresa
    return None


def insumo_scope_clause():
    scope = get_fin_scope()
    if scope is not None:
        return Insumo.id_empresa == scope.id_empresa
    return None


def lote_scope_clause():
    scope = get_fin_scope()
    if scope is not None:
        return LoteSementes.id_viveiro == scope.id_viveiro
    return None


def insumo_movimento_scope_clause():
    ic = insumo_scope_clause()
    if ic is not None:
        return InsumoMovimentacao.id_insumo.in_(select(Insumo.id).where(ic))
    return None
