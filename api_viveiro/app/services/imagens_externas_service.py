"""Pipeline de imagens da biblioteca: speciesLink → GBIF → iNaturalist (+ gênero)."""

from __future__ import annotations

import logging
from typing import List, Optional

import httpx

from app.config import settings
from app.services.gbif_service import buscar_imagens_gbif
from app.services.specieslink_service import (
    _api_key,
    _get_json,
    _validar_url_imagem,
    buscar_imagens_inaturalist,
    extrair_urls_imagem,
    filtrar_urls_imagem,
    montar_url_busca,
    normalizar_nome_cientifico_para_busca,
)

logger = logging.getLogger(__name__)


def _adicionar_unicas(destino: List[str], novas: List[str], limite: int) -> None:
    for url in novas:
        if url not in destino:
            destino.append(url)
        if len(destino) >= limite:
            return


async def _buscar_specieslink(nome_busca: str, *, timeout: float, verify: bool, limite: int) -> List[str]:
    if not _api_key():
        return []
    try:
        url = montar_url_busca(nome_busca)
    except ValueError:
        return []

    payload = await _get_json(url, timeout=timeout, verify_ssl=verify)
    if payload is None:
        return []
    return extrair_urls_imagem(payload, max_imagens=limite * 3)


async def buscar_imagens_para_especie(
    nome_cientifico: str,
    *,
    timeout: Optional[float] = None,
    verify_ssl: Optional[bool] = None,
    max_imagens: Optional[int] = None,
) -> List[str]:
    """
    Esteira: speciesLink (URLs diretas) → GBIF → iNaturalist → fallback só pelo gênero.
    """
    nome_busca = normalizar_nome_cientifico_para_busca(nome_cientifico)
    if not nome_busca:
        return []

    timeout_val = timeout if timeout is not None else settings.SPECIESLINK_REQUEST_TIMEOUT
    verify = verify_ssl if verify_ssl is not None else settings.SPECIESLINK_VERIFY_SSL
    limite = max_imagens or settings.SPECIESLINK_MAX_IMAGENS_POR_ESPECIE

    candidatas: List[str] = []
    _adicionar_unicas(
        candidatas,
        await _buscar_specieslink(nome_busca, timeout=timeout_val, verify=verify, limite=limite),
        limite,
    )

    if len(candidatas) < limite and settings.GBIF_FALLBACK_ENABLED:
        _adicionar_unicas(
            candidatas,
            await buscar_imagens_gbif(
                nome_busca, timeout=timeout_val, max_imagens=limite
            ),
            limite,
        )

    if len(candidatas) < limite and settings.INATURALIST_FALLBACK_ENABLED:
        _adicionar_unicas(
            candidatas,
            await buscar_imagens_inaturalist(
                nome_busca, timeout=timeout_val, max_imagens=limite
            ),
            limite,
        )

    if len(candidatas) < limite and settings.IMAGENS_FALLBACK_GENERO_ENABLED:
        genero = nome_busca.split()[0]
        if genero and genero != nome_busca:
            if settings.GBIF_FALLBACK_ENABLED:
                _adicionar_unicas(
                    candidatas,
                    await buscar_imagens_gbif(
                        genero, timeout=timeout_val, max_imagens=1
                    ),
                    limite,
                )
            if len(candidatas) < limite and settings.INATURALIST_FALLBACK_ENABLED:
                _adicionar_unicas(
                    candidatas,
                    await buscar_imagens_inaturalist(
                        genero, timeout=timeout_val, max_imagens=1
                    ),
                    limite,
                )

    candidatas = filtrar_urls_imagem(candidatas)

    if not settings.SPECIESLINK_VALIDAR_URL_IMAGEM:
        return candidatas[:limite]

    validadas: List[str] = []
    async with httpx.AsyncClient(
        timeout=timeout_val, verify=verify, follow_redirects=True
    ) as client:
        for url in candidatas:
            if await _validar_url_imagem(url, client):
                validadas.append(url)
            if len(validadas) >= limite:
                break
    return validadas[:limite]
