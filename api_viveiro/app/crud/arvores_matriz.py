from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.arvores_matriz import ArvoreMatriz
from app.models.coletas_sementes import ColetaSementes
from app.models.lotes_sementes import LoteSementes
from app.models.especies import Especie
from app.schemas.arvores_matriz import ArvoreMatrizCreate, ArvoreMatrizUpdate
from app.utils.coordenadas import utm_para_latlon

_CAMPOS_MATRIZ = (
    "nome",
    "id_especie",
    "cidade",
    "estado",
    "municipio",
    "imovel_nome",
    "tipo_origem",
    "numero_autorizacao",
    "observacoes_legais",
    "mes_inicio_frutificacao",
    "mes_fim_frutificacao",
    "estagio_frutificacao",
    "fenologia_observacoes",
    "observacoes",
)


def _resolver_lat_lon(dados: dict) -> tuple[float, float]:
    if dados.get("tipo_coordenada") == "utm":
        lat, lon = utm_para_latlon(
            float(dados["utm_easting"]),
            float(dados["utm_northing"]),
            int(dados["utm_zona"]),
            hemisferio_sul=True,
        )
        return lat, lon
    return float(dados["latitude"]), float(dados["longitude"])


async def _contagens(db: AsyncSession, arvore_id: int) -> tuple[int, int]:
    c1 = await db.execute(
        select(func.count(ColetaSementes.id)).where(ColetaSementes.id_arvore_matriz == arvore_id)
    )
    c2 = await db.execute(
        select(func.count(LoteSementes.id)).where(LoteSementes.id_arvore_matriz == arvore_id)
    )
    return int(c1.scalar() or 0), int(c2.scalar() or 0)


def _para_resposta(arvore: ArvoreMatriz, total_coletas: int = 0, total_lotes: int = 0) -> dict:
    especie = arvore.especie
    nome_especie = None
    if especie:
        nome_especie = especie.nome_popular or especie.nome_cientifico
    return {
        "id": arvore.id,
        "nome": arvore.nome,
        "id_especie": arvore.id_especie,
        "especie_nome": nome_especie,
        "cidade": arvore.cidade,
        "estado": arvore.estado,
        "municipio": arvore.municipio,
        "imovel_nome": arvore.imovel_nome,
        "tipo_origem": arvore.tipo_origem,
        "numero_autorizacao": arvore.numero_autorizacao,
        "observacoes_legais": arvore.observacoes_legais,
        "mes_inicio_frutificacao": arvore.mes_inicio_frutificacao,
        "mes_fim_frutificacao": arvore.mes_fim_frutificacao,
        "estagio_frutificacao": arvore.estagio_frutificacao,
        "fenologia_observacoes": arvore.fenologia_observacoes,
        "latitude": float(arvore.latitude),
        "longitude": float(arvore.longitude),
        "tipo_coordenada": arvore.tipo_coordenada,
        "utm_zona": arvore.utm_zona,
        "utm_easting": float(arvore.utm_easting) if arvore.utm_easting is not None else None,
        "utm_northing": float(arvore.utm_northing) if arvore.utm_northing is not None else None,
        "sementes_coletadas": arvore.sementes_coletadas or 0,
        "taxa_germinacao": float(arvore.taxa_germinacao) if arvore.taxa_germinacao is not None else None,
        "data_ultima_coleta": arvore.data_ultima_coleta,
        "observacoes": arvore.observacoes,
        "data_cadastro": arvore.data_cadastro,
        "total_coletas": total_coletas,
        "total_lotes": total_lotes,
    }


async def get_arvore_matriz(db: AsyncSession, arvore_id: int) -> Optional[ArvoreMatriz]:
    result = await db.execute(
        select(ArvoreMatriz)
        .options(joinedload(ArvoreMatriz.especie))
        .where(ArvoreMatriz.id == arvore_id)
    )
    return result.scalars().first()


async def get_arvore_matriz_out(db: AsyncSession, arvore_id: int) -> Optional[dict]:
    arvore = await get_arvore_matriz(db, arvore_id)
    if not arvore:
        return None
    tc, tl = await _contagens(db, arvore_id)
    return _para_resposta(arvore, tc, tl)


async def get_arvores_matriz(db: AsyncSession, skip: int = 0, limit: int = 500) -> List[dict]:
    result = await db.execute(
        select(ArvoreMatriz)
        .options(joinedload(ArvoreMatriz.especie))
        .order_by(ArvoreMatriz.id.desc())
        .offset(skip)
        .limit(limit)
    )
    arvores = result.scalars().all()
    saida = []
    for a in arvores:
        tc, tl = await _contagens(db, a.id)
        saida.append(_para_resposta(a, tc, tl))
    return saida


async def create_arvore_matriz(db: AsyncSession, payload: ArvoreMatrizCreate) -> dict:
    dados = payload.dict()
    lat, lon = _resolver_lat_lon(dados)
    kwargs = {k: dados.get(k) for k in _CAMPOS_MATRIZ}
    db_arvore = ArvoreMatriz(
        **kwargs,
        latitude=lat,
        longitude=lon,
        tipo_coordenada=dados["tipo_coordenada"],
        utm_zona=dados.get("utm_zona"),
        utm_easting=dados.get("utm_easting"),
        utm_northing=dados.get("utm_northing"),
        sementes_coletadas=0,
        taxa_germinacao=None,
        data_ultima_coleta=None,
    )
    db.add(db_arvore)
    await db.flush()
    arvore_id = db_arvore.id
    await db.commit()
    return await get_arvore_matriz_out(db, arvore_id)


async def update_arvore_matriz(
    db: AsyncSession, arvore_id: int, payload: ArvoreMatrizUpdate
) -> Optional[dict]:
    db_arvore = await get_arvore_matriz(db, arvore_id)
    if not db_arvore:
        return None

    update_data = payload.dict(exclude_unset=True)
    merged = {**_para_resposta(db_arvore), **update_data}
    if any(
        k in update_data
        for k in ("tipo_coordenada", "latitude", "longitude", "utm_zona", "utm_easting", "utm_northing")
    ):
        lat, lon = _resolver_lat_lon(merged)
        db_arvore.latitude = lat
        db_arvore.longitude = lon

    for field, value in update_data.items():
        if field in ("latitude", "longitude", "sementes_coletadas", "taxa_germinacao", "data_ultima_coleta"):
            continue
        if hasattr(db_arvore, field):
            setattr(db_arvore, field, value)

    await db.commit()
    return await get_arvore_matriz_out(db, arvore_id)


async def delete_arvore_matriz(db: AsyncSession, arvore_id: int) -> Optional[ArvoreMatriz]:
    db_arvore = await get_arvore_matriz(db, arvore_id)
    if not db_arvore:
        return None
    await db.delete(db_arvore)
    await db.commit()
    return db_arvore
