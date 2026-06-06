"""Utilitários fiscais — validação CPF/CNPJ, NCM, CFOP."""

from __future__ import annotations

import re
from typing import Literal


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def validate_cpf(cpf: str) -> bool:
    d = only_digits(cpf)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for i in range(9, 11):
        s = sum(int(d[num]) * ((i + 1) - num) for num in range(0, i))
        dig = (s * 10 % 11) % 10
        if int(d[i]) != dig:
            return False
    return True


def validate_cnpj(cnpj: str) -> bool:
    d = only_digits(cnpj)
    if len(d) != 14 or d == d[0] * 14:
        return False
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for i, weights in ((12, weights1), (13, weights2)):
        s = sum(int(d[j]) * weights[j] for j in range(len(weights)))
        dig = 11 - (s % 11)
        dig = 0 if dig >= 10 else dig
        if int(d[i]) != dig:
            return False
    return True


def validate_ncm(ncm: str) -> bool:
    d = only_digits(ncm)
    return len(d) == 8 and d.isdigit()


def normalize_ncm(ncm: str) -> str:
    d = only_digits(ncm)
    if len(d) != 8:
        raise ValueError("NCM deve ter 8 dígitos numéricos")
    return d


def resolve_cfop(cfop_base: str, uf_origem: str, uf_destino: str) -> str:
    """CFOP 5xxx interno / 6xxx interestadual / 7xxx exterior (MOC / SINIEF)."""
    cfop = (cfop_base or "").strip()
    if len(cfop) != 4 or not cfop.isdigit():
        raise ValueError(f"CFOP inválido: {cfop_base}")
    ud = (uf_destino or "").upper().strip()
    if ud in ("EX", "EXTERIOR"):
        return cfop if cfop[0] == "7" else f"7{cfop[1:]}"
    interno = uf_origem.upper().strip() == ud
    if interno:
        return cfop if cfop[0] == "5" else f"5{cfop[1:]}"
    return cfop if cfop[0] == "6" else f"6{cfop[1:]}"


def inferir_tipo_operacao_fiscal(
    comprador_estado: str | None,
    tipo_operacao_venda: str | None = None,
) -> str:
    """Doméstica, importação (origem estrangeira SN) ou exterior."""
    uf = (comprador_estado or "").upper().strip()
    if uf in ("EX", "EXTERIOR"):
        return "exterior"
    t = (tipo_operacao_venda or "domestica").lower().strip()
    if t in ("domestica", "importacao", "exterior"):
        return t
    return "domestica"


def tipo_cliente_fiscal(tipo: str) -> Literal["PF", "PJ"]:
    t = (tipo or "").upper()
    if t not in ("PF", "PJ"):
        raise ValueError("Tipo de comprador deve ser PF ou PJ")
    return t  # type: ignore[return-value]


def consumidor_final_nao_contribuinte(tipo: str, inscricao_estadual: str | None) -> bool:
    """Pré-requisito DIFAL (EC 87/2015) — CPF ou CNPJ sem IE."""
    if tipo_cliente_fiscal(tipo) == "PF":
        return True
    ie = only_digits(inscricao_estadual or "")
    return len(ie) == 0
