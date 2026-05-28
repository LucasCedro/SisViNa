"""Imagens de ocorrências via API pública do GBIF."""

from __future__ import annotations

import logging
from typing import List, Optional
from urllib.parse import quote

from app.config import settings
from app.services.specieslink_service import (
    _get_json,
    filtrar_urls_imagem,
    normalizar_nome_cientifico_para_busca,
)

logger = logging.getLogger(__name__)


def _urls_de_ocorrencia(record: dict) -> List[str]:
    urls: List[str] = []
    for item in record.get("media") or []:
        if not isinstance(item, dict):
            continue
        ident = item.get("identifier")
        if isinstance(ident, str) and ident.startswith("http"):
            urls.append(ident)
    return urls


async def buscar_imagens_gbif(
    nome_cientifico: str,
    *,
    timeout: Optional[float] = None,
    max_imagens: Optional[int] = None,
    country: Optional[str] = None,
) -> List[str]:
    if not settings.GBIF_FALLBACK_ENABLED:
        return []

    nome = normalizar_nome_cientifico_para_busca(nome_cientifico)
    if not nome:
        return []

    limite = max_imagens or settings.GBIF_MAX_IMAGENS_POR_ESPECIE
    pais = country or settings.GBIF_COUNTRY_FILTER
    base = settings.GBIF_API_BASE_URL.rstrip("/")
    params = (
        f"scientificName={quote(nome)}"
        f"&mediaType=StillImage"
        f"&limit={min(settings.GBIF_SEARCH_LIMIT, limite * 5)}"
    )
    if pais:
        params += f"&country={quote(pais)}"

    url = f"{base}/occurrence/search?{params}"
    timeout_val = timeout if timeout is not None else settings.SPECIESLINK_REQUEST_TIMEOUT

    payload = await _get_json(url, timeout=timeout_val, verify_ssl=True)
    if not isinstance(payload, dict):
        return []

    urls: List[str] = []
    for record in payload.get("results") or []:
        if not isinstance(record, dict):
            continue
        for candidate in _urls_de_ocorrencia(record):
            if candidate not in urls:
                urls.append(candidate)
            if len(urls) >= limite:
                return filtrar_urls_imagem(urls)

    return filtrar_urls_imagem(urls)[:limite]
