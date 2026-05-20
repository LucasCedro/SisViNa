from datetime import date
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.lotes_sementes import _para_resposta as lote_para_resposta, _ultimo_teste_germinacao, criar_lote_de_coleta
from app.models.arvores_matriz import ArvoreMatriz
from app.models.coletas_sementes import ColetaSementes
from app.models.lotes_sementes import LoteSementes
from app.schemas.coletas_sementes import ColetaSementesCreate, ColetaSementesUpdate


def _para_resposta(coleta: ColetaSementes, lotes: Optional[list] = None) -> dict:
    arvore = coleta.arvore_matriz
    especie = arvore.especie if arvore else None
    nome_especie = None
    if especie:
        nome_especie = especie.nome_popular or especie.nome_cientifico
    return {
        "id": coleta.id,
        "id_arvore_matriz": coleta.id_arvore_matriz,
        "matriz_nome": arvore.nome if arvore else "",
        "id_especie": arvore.id_especie if arvore else 0,
        "especie_nome": nome_especie,
        "id_funcionario": coleta.id_funcionario,
        "funcionario_nome": coleta.funcionario.nome if coleta.funcionario else "",
        "data_coleta": coleta.data_coleta,
        "quantidade_sementes": coleta.quantidade_sementes,
        "observacoes": coleta.observacoes,
        "data_registro": coleta.data_registro,
        "lotes": lotes or [],
    }


async def _lotes_da_coleta(db: AsyncSession, coleta: ColetaSementes) -> list:
    if not coleta.lotes:
        return []
    saida = []
    for lote in coleta.lotes:
        ultimo = await _ultimo_teste_germinacao(db, lote.id)
        saida.append(lote_para_resposta(lote, ultimo))
    return saida


async def _atualizar_agregados_matriz(db: AsyncSession, id_arvore_matriz: int) -> None:
    result = await db.execute(
        select(
            func.coalesce(func.sum(ColetaSementes.quantidade_sementes), 0),
            func.max(ColetaSementes.data_coleta),
        ).where(ColetaSementes.id_arvore_matriz == id_arvore_matriz)
    )
    total, ultima = result.one()
    arvore = await db.get(ArvoreMatriz, id_arvore_matriz)
    if arvore:
        arvore.sementes_coletadas = int(total or 0)
        arvore.data_ultima_coleta = ultima
        await db.commit()


async def get_coleta(db: AsyncSession, coleta_id: int) -> Optional[ColetaSementes]:
    result = await db.execute(
        select(ColetaSementes)
        .options(
            joinedload(ColetaSementes.arvore_matriz).joinedload(ArvoreMatriz.especie),
            joinedload(ColetaSementes.funcionario),
            joinedload(ColetaSementes.lotes).joinedload(LoteSementes.arvore_matriz),
            joinedload(ColetaSementes.lotes).joinedload(LoteSementes.coleta),
            joinedload(ColetaSementes.lotes).joinedload(LoteSementes.especie),
        )
        .where(ColetaSementes.id == coleta_id)
    )
    return result.scalars().first()


async def get_coleta_out(db: AsyncSession, coleta_id: int) -> Optional[dict]:
    coleta = await get_coleta(db, coleta_id)
    if not coleta:
        return None
    lotes = await _lotes_da_coleta(db, coleta)
    return _para_resposta(coleta, lotes)


async def get_coletas(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 2000,
    id_arvore_matriz: Optional[int] = None,
    id_especie: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> List[dict]:
    query = (
        select(ColetaSementes)
        .join(ArvoreMatriz, ColetaSementes.id_arvore_matriz == ArvoreMatriz.id)
        .options(
            joinedload(ColetaSementes.arvore_matriz).joinedload(ArvoreMatriz.especie),
            joinedload(ColetaSementes.funcionario),
            joinedload(ColetaSementes.lotes),
        )
        .order_by(ColetaSementes.data_coleta.desc(), ColetaSementes.id.desc())
    )
    if id_arvore_matriz:
        query = query.where(ColetaSementes.id_arvore_matriz == id_arvore_matriz)
    if id_especie:
        query = query.where(ArvoreMatriz.id_especie == id_especie)
    if data_inicio:
        query = query.where(ColetaSementes.data_coleta >= data_inicio)
    if data_fim:
        query = query.where(ColetaSementes.data_coleta <= data_fim)

    result = await db.execute(query.offset(skip).limit(limit))
    coletas = result.scalars().unique().all()
    saida = []
    for c in coletas:
        lotes = await _lotes_da_coleta(db, c)
        saida.append(_para_resposta(c, lotes))
    return saida


async def create_coleta(
    db: AsyncSession, payload: ColetaSementesCreate, id_funcionario: int
) -> dict:
    arvore = await db.get(ArvoreMatriz, payload.id_arvore_matriz)
    if not arvore:
        raise ValueError("Árvore matriz não encontrada")

    dados = payload.dict()
    gerar_lote = dados.pop("gerar_lote", True)
    db_coleta = ColetaSementes(
        id_arvore_matriz=dados["id_arvore_matriz"],
        id_funcionario=id_funcionario,
        data_coleta=dados["data_coleta"],
        quantidade_sementes=dados["quantidade_sementes"],
        observacoes=dados.get("observacoes"),
    )
    db.add(db_coleta)
    await db.flush()
    coleta_id = db_coleta.id

    coleta = await get_coleta(db, coleta_id)
    if gerar_lote:
        await criar_lote_de_coleta(db, coleta)

    await db.commit()
    await _atualizar_agregados_matriz(db, dados["id_arvore_matriz"])
    return await get_coleta_out(db, coleta_id)


async def update_coleta(
    db: AsyncSession, coleta_id: int, payload: ColetaSementesUpdate
) -> Optional[dict]:
    db_coleta = await get_coleta(db, coleta_id)
    if not db_coleta:
        return None

    id_matriz = db_coleta.id_arvore_matriz
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_coleta, field, value)

    await db.commit()
    await _atualizar_agregados_matriz(db, id_matriz)
    return await get_coleta_out(db, coleta_id)


async def delete_coleta(db: AsyncSession, coleta_id: int) -> Optional[dict]:
    db_coleta = await get_coleta(db, coleta_id)
    if not db_coleta:
        return None
    id_matriz = db_coleta.id_arvore_matriz
    lotes = await _lotes_da_coleta(db, db_coleta)
    resp = _para_resposta(db_coleta, lotes)
    await db.delete(db_coleta)
    await db.commit()
    await _atualizar_agregados_matriz(db, id_matriz)
    return resp
