"""Extração de meses de floração/frutificação a partir de texto livre (campo notes)."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

MESES_PT: Dict[str, int] = {
    "janeiro": 1,
    "jan": 1,
    "fevereiro": 2,
    "fev": 2,
    "marco": 3,
    "março": 3,
    "mar": 3,
    "abril": 4,
    "abr": 4,
    "maio": 5,
    "mai": 5,
    "junho": 6,
    "jun": 6,
    "julho": 7,
    "jul": 7,
    "agosto": 8,
    "ago": 8,
    "setembro": 9,
    "set": 9,
    "outubro": 10,
    "out": 10,
    "novembro": 11,
    "nov": 11,
    "dezembro": 12,
    "dez": 12,
}

# Meses longos antes dos abreviados (evita "mar" dentro de "janeiro")
_MESES_ORDENADOS = sorted(MESES_PT.keys(), key=len, reverse=True)
_RE_MES = r"\b(?:" + "|".join(re.escape(m) for m in _MESES_ORDENADOS) + r")\b"
_RE_SECAO = re.compile(
    rf"(flora(?:ç|c)ão|frutifica(?:ç|c)ão)\s*:?\s*(.+?)(?=(?:flora(?:ç|c)ão|frutifica(?:ç|c)ão)\s*:|\Z)",
    re.IGNORECASE | re.DOTALL,
)


def _mes_para_int(token: str) -> int | None:
    key = token.strip().lower().strip(".,;")
    return MESES_PT.get(key)


def _expandir_intervalo(inicio: int, fim: int) -> List[int]:
    if inicio == fim:
        return [inicio]
    meses: List[int] = []
    m = inicio
    for _ in range(12):
        meses.append(m)
        if m == fim:
            break
        m = 1 if m == 12 else m + 1
    return meses


def _parse_bloco_meses(bloco: str) -> List[int]:
    """Interpreta 'maio a julho', 'agosto e setembro', 'outubro'."""
    texto = bloco.strip().rstrip(".")
    if not texto:
        return []

    encontrados: List[int] = []

    # Intervalo explícito com " a "
    m_range = re.search(rf"({_RE_MES})\s+a\s+({_RE_MES})", texto, re.IGNORECASE)
    if m_range:
        ini = _mes_para_int(m_range.group(1))
        fim = _mes_para_int(m_range.group(2))
        if ini and fim:
            return _expandir_intervalo(ini, fim)

    # Lista separada por vírgula ou " e "
    partes = re.split(rf",|\s+e\s+", texto, flags=re.IGNORECASE)
    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue
        for m in re.finditer(_RE_MES, parte, re.IGNORECASE):
            num = _mes_para_int(m.group(0))
            if num and num not in encontrados:
                encontrados.append(num)

    return sorted(encontrados)


def extract_fenologia(notes: str | None) -> Tuple[List[int], List[int]]:
    """
    Retorna (meses_floracao, meses_frutificacao).
    Se notes for vazio ou regex falhar, retorna ([], []).
    """
    if not notes or not str(notes).strip():
        return [], []

    texto = str(notes)
    flor: List[int] = []
    frut: List[int] = []

    for match in _RE_SECAO.finditer(texto):
        rotulo = match.group(1).lower()
        bloco = match.group(2)
        meses = _parse_bloco_meses(bloco)
        if "flora" in rotulo:
            flor = meses
        elif "frutifica" in rotulo:
            frut = meses

    return flor, frut
