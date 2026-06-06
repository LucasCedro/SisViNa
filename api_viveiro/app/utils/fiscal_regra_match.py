"""Correspondência de UF destino em regras fiscais — padrões além de UF fixa."""

from __future__ import annotations

from typing import Iterable, List, Tuple


def _ufs_lista(raw: str) -> List[str]:
    return [p.strip().upper() for p in raw.split(",") if p.strip()]


def uf_destino_regra_aplica(padrao: str, uf_origem: str, uf_destino: str) -> bool:
    """
    Padrões em uf_destino da regra:
    - UF de 2 letras (SP) — destino exato
    - SP,MG,ES — lista de UFs
    - * — qualquer destino
    - INTERNA — mesma UF que origem (venda dentro do estado)
    - INTERESTADUAL — UF destino diferente da origem
    - EXTERIOR — exportação (UF destino EX ou EXTERIOR)
    """
    p = (padrao or "").upper().strip()
    uo = (uf_origem or "").upper().strip()
    ud = (uf_destino or "").upper().strip()
    if p == "EXTERIOR":
        return ud in ("EX", "EXTERIOR")
    if not ud or not uo:
        return False
    interno = uo == ud

    if p == "*":
        return True
    if p == "INTERNA":
        return interno
    if p == "INTERESTADUAL":
        return not interno
    if "," in p:
        return ud in _ufs_lista(p)
    if len(p) == 2 and p.isalpha():
        return ud == p
    return False


def especificidade_uf_destino(padrao: str, uf_origem: str, uf_destino: str) -> int:
    """Menor = mais específico (prioridade na escolha da regra)."""
    p = (padrao or "").upper().strip()
    ud = (uf_destino or "").upper().strip()
    uo = (uf_origem or "").upper().strip()
    interno = uo == ud

    if len(p) == 2 and p.isalpha() and p == ud:
        return 0
    if "," in p and ud in _ufs_lista(p):
        return 1
    if p == "INTERNA" and interno:
        return 2
    if p == "EXTERIOR":
        return 2
    if p == "INTERESTADUAL" and not interno:
        return 3
    if p == "*":
        return 4
    return 99


def escolher_melhor_regra(regras: Iterable, uf_origem: str, uf_destino: str):
    """Filtra regras cujo padrão de destino aplica e retorna a mais específica."""
    candidatas: List[Tuple[int, object]] = []
    for regra in regras:
        if not uf_destino_regra_aplica(regra.uf_destino, uf_origem, uf_destino):
            continue
        score = especificidade_uf_destino(regra.uf_destino, uf_origem, uf_destino)
        candidatas.append((score, regra))
    if not candidatas:
        return None
    candidatas.sort(key=lambda x: (x[0], x[1].ordem, x[1].id))
    return candidatas[0][1]


def label_operacao(uf_origem: str, uf_destino: str, tipo_operacao: str = "domestica") -> str:
    if (tipo_operacao or "").lower() == "importacao":
        return "importação (origem estrangeira)"
    ud = (uf_destino or "").upper()
    if ud in ("EX", "EXTERIOR") or (tipo_operacao or "").lower() == "exterior":
        return "exterior"
    if uf_origem.upper() == ud:
        return "interna"
    return "interestadual"
