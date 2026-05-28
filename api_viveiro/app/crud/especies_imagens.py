"""Cache de imagens externas (speciesLink) na biblioteca de espécies."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.especie_biblioteca import EspecieBiblioteca
from app.models.especies import Especie
from app.services.imagens_externas_service import buscar_imagens_para_especie
from app.services.specieslink_service import filtrar_urls_imagem, url_parece_imagem
from app.utils.biblioteca_assets import url_local_biblioteca_existe


def _parse_urls_cache(valor: Any) -> List[str]:
    if valor is None:
        return []
    if isinstance(valor, list):
        brutas = [u for u in valor if isinstance(u, str) and u.strip().startswith("http")]
        return filtrar_urls_imagem(brutas)
    if isinstance(valor, str):
        try:
            parsed = json.loads(valor)
            if isinstance(parsed, list):
                return _parse_urls_cache(parsed)
        except json.JSONDecodeError:
            pass
    return []


def _urls_locais_biblioteca(bib: EspecieBiblioteca) -> List[str]:
    out: List[str] = []
    for attr in ("imagem_arvore", "imagem_semente", "imagem_folha"):
        val = getattr(bib, attr, None)
        if not val or val in out:
            continue
        if val.strip().startswith("http"):
            if url_parece_imagem(val):
                out.append(val)
        elif url_local_biblioteca_existe(val):
            out.append(val)
    return out


def imagem_capa_biblioteca(bib: Optional[EspecieBiblioteca]) -> Optional[str]:
    if bib is None:
        return None
    urls = _parse_urls_cache(bib.imagens_externas)
    if urls:
        return urls[0]
    locais = _urls_locais_biblioteca(bib)
    return locais[0] if locais else None


def total_fotos_biblioteca(bib: Optional[EspecieBiblioteca]) -> int:
    if bib is None:
        return 0
    locais = _urls_locais_biblioteca(bib)
    externas = _parse_urls_cache(bib.imagens_externas)
    vistos = set(locais)
    for u in externas:
        if u not in vistos:
            vistos.add(u)
    return len(vistos)


def cache_valido(atualizado_em: Optional[datetime]) -> bool:
    if atualizado_em is None:
        return False
    ttl = timedelta(days=settings.SPECIESLINK_CACHE_DIAS)
    return datetime.utcnow() - atualizado_em.replace(tzinfo=None) < ttl


async def obter_imagens_externas(
    db: AsyncSession,
    id_especie: int,
    *,
    refresh: bool = False,
) -> List[str]:
    row = await db.execute(
        select(EspecieBiblioteca, Especie.nome_cientifico)
        .join(Especie, Especie.id == EspecieBiblioteca.id_especie)
        .where(EspecieBiblioteca.id_especie == id_especie)
    )
    item = row.first()
    if not item:
        return []
    bib, nome_cientifico = item
    urls = _parse_urls_cache(bib.imagens_externas)
    if urls and not refresh and cache_valido(bib.imagens_externas_atualizado_em):
        return urls
    return await atualizar_cache_imagens_externas(db, id_especie, nome_cientifico, bib)


async def atualizar_cache_imagens_externas(
    db: AsyncSession,
    id_especie: int,
    nome_cientifico: str,
    bib: Optional[EspecieBiblioteca] = None,
) -> List[str]:
    if bib is None:
        bib = await db.get(EspecieBiblioteca, id_especie)
    if bib is None:
        return []

    urls = await buscar_imagens_para_especie(nome_cientifico)
    bib.imagens_externas = urls if urls else None
    bib.imagens_externas_atualizado_em = datetime.utcnow()
    await db.commit()
    await db.refresh(bib)
    return urls


async def sincronizar_imagens_biblioteca(
    db: AsyncSession,
    *,
    apenas_sem_cache: bool = True,
    limite: int = 500,
    forcar: bool = False,
) -> Dict[str, Any]:
    query = (
        select(EspecieBiblioteca, Especie.nome_cientifico)
        .join(Especie, Especie.id == EspecieBiblioteca.id_especie)
        .order_by(Especie.id)
        .limit(limite)
    )
    rows = (await db.execute(query)).all()

    processadas = 0
    com_imagem = 0
    sem_imagem = 0
    erros = 0

    for bib, nome_cientifico in rows:
        if apenas_sem_cache and not forcar:
            if bib.imagens_externas_atualizado_em and cache_valido(
                bib.imagens_externas_atualizado_em
            ):
                continue
        try:
            urls = await atualizar_cache_imagens_externas(
                db, bib.id_especie, nome_cientifico, bib
            )
            processadas += 1
            if urls:
                com_imagem += 1
            else:
                sem_imagem += 1
            await asyncio.sleep(0.35)
        except Exception:
            erros += 1
            await db.rollback()

    return {
        "processadas": processadas,
        "com_imagem": com_imagem,
        "sem_imagem": sem_imagem,
        "erros": erros,
    }
