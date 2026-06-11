"""Normalização de nomes científicos para busca na API e UPSERT no banco."""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import quote

# Espaços Unicode → espaço ASCII; não altera hífens (St. -Hil. permanece literal).
_RE_ESPACOS = re.compile(r"\s+")


def sanitize_input_name(nome: str) -> str:
    """Remove bordas e colapsa espaços internos; preserva hífens e pontuação."""
    if not nome:
        return ""
    texto = unicodedata.normalize("NFC", nome.strip())
    return _RE_ESPACOS.sub(" ", texto)


def normalize_key(nome: str) -> str:
    """
    Chave case-insensitive para UPSERT.
    Dipteryx alata == DIPTERYX ALATA; espaços extras normalizados.
    """
    return sanitize_input_name(nome).casefold()


def normalize_author_abbrev(nome: str) -> str:
    """
    Compacta abreviações de autor para o formato esperado pela JBRJ.
    Ex.: ``A. St. -Hil.`` → ``A.St.-Hil.`` (espaço após ponto e antes do hífen).
    """
    texto = sanitize_input_name(nome)
    texto = re.sub(r"\.\s+", ".", texto)
    texto = re.sub(r"\s+-", "-", texto)
    return texto


def binomial_only(nome: str) -> str:
    """Gênero + epíteto, ignorando autor/infraspecífico."""
    partes = sanitize_input_name(nome).split()
    if len(partes) >= 2:
        return f"{partes[0]} {partes[1]}"
    return sanitize_input_name(nome)


def api_search_variants(nome: str) -> list[str]:
    """Variantes ordenadas para tentativa na API (dedupe preservando ordem)."""
    limpo = sanitize_input_name(nome)
    autor = normalize_author_abbrev(limpo)
    binom = binomial_only(limpo)
    raw = [limpo, autor, limpo.casefold(), autor.casefold(), binom, binom.casefold()]
    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def url_encode_taxon(nome: str) -> str:
    """
    Segmento de path URL-encoded para a API JBRJ.
    Espaços → %20; parênteses e hífens codificados (string literal segura).
    """
    limpo = sanitize_input_name(nome)
    return quote(limpo, safe="")
