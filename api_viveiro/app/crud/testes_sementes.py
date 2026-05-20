from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.arvores_matriz import ArvoreMatriz
from app.models.lotes_sementes import LoteSementes
from app.models.testes_sementes import TesteSementes
from app.schemas.testes_sementes import TesteSementesCreate, TesteSementesUpdate


def _para_resposta(teste: TesteSementes) -> dict:
    lote = teste.lote
    arvore = lote.arvore_matriz if lote else None
    return {
        "id": teste.id,
        "id_lote_sementes": teste.id_lote_sementes,
        "codigo_lote": lote.codigo_lote if lote else "",
        "id_arvore_matriz": lote.id_arvore_matriz if lote else 0,
        "matriz_nome": arvore.nome if arvore else "",
        "data_teste": teste.data_teste,
        "tipo_teste": teste.tipo_teste,
        "metodologia": teste.metodologia,
        "repeticoes": teste.repeticoes or 1,
        "sementes_avaliadas": teste.sementes_avaliadas,
        "percentual_resultado": float(teste.percentual_resultado),
        "observacoes": teste.observacoes,
        "id_funcionario": teste.id_funcionario,
        "funcionario_nome": teste.funcionario.nome if teste.funcionario else "",
        "data_registro": teste.data_registro,
    }


async def _sync_taxa_matriz(db: AsyncSession, id_arvore_matriz: int) -> None:
    result = await db.execute(
        select(TesteSementes.percentual_resultado)
        .join(LoteSementes, TesteSementes.id_lote_sementes == LoteSementes.id)
        .where(
            LoteSementes.id_arvore_matriz == id_arvore_matriz,
            TesteSementes.tipo_teste == "germinacao",
        )
        .order_by(TesteSementes.data_teste.desc(), TesteSementes.id.desc())
        .limit(1)
    )
    valor = result.scalar_one_or_none()
    arvore = await db.get(ArvoreMatriz, id_arvore_matriz)
    if arvore:
        arvore.taxa_germinacao = float(valor) if valor is not None else None


async def get_teste(db: AsyncSession, teste_id: int) -> Optional[TesteSementes]:
    result = await db.execute(
        select(TesteSementes)
        .options(
            joinedload(TesteSementes.lote).joinedload(LoteSementes.arvore_matriz),
            joinedload(TesteSementes.funcionario),
        )
        .where(TesteSementes.id == teste_id)
    )
    return result.scalars().first()


async def get_testes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 2000,
    id_lote_sementes: Optional[int] = None,
    id_arvore_matriz: Optional[int] = None,
) -> List[TesteSementes]:
    query = (
        select(TesteSementes)
        .join(LoteSementes, TesteSementes.id_lote_sementes == LoteSementes.id)
        .options(
            joinedload(TesteSementes.lote).joinedload(LoteSementes.arvore_matriz),
            joinedload(TesteSementes.funcionario),
        )
        .order_by(TesteSementes.data_teste.desc(), TesteSementes.id.desc())
    )
    if id_lote_sementes:
        query = query.where(TesteSementes.id_lote_sementes == id_lote_sementes)
    if id_arvore_matriz:
        query = query.where(LoteSementes.id_arvore_matriz == id_arvore_matriz)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().unique().all()


async def create_teste(db: AsyncSession, payload: TesteSementesCreate, id_funcionario: int) -> dict:
    lote = await db.get(LoteSementes, payload.id_lote_sementes)
    if not lote:
        raise ValueError("Lote não encontrado")

    dados = payload.dict()
    db_teste = TesteSementes(
        id_lote_sementes=dados["id_lote_sementes"],
        data_teste=dados["data_teste"],
        tipo_teste=dados["tipo_teste"],
        metodologia=dados.get("metodologia"),
        repeticoes=dados.get("repeticoes") or 1,
        sementes_avaliadas=dados.get("sementes_avaliadas"),
        percentual_resultado=dados["percentual_resultado"],
        observacoes=dados.get("observacoes"),
        id_funcionario=id_funcionario,
    )
    db.add(db_teste)
    await db.commit()
    if dados["tipo_teste"] == "germinacao":
        await _sync_taxa_matriz(db, lote.id_arvore_matriz)
        await db.commit()
    teste = await get_teste(db, db_teste.id)
    return _para_resposta(teste)


async def update_teste(
    db: AsyncSession, teste_id: int, payload: TesteSementesUpdate
) -> Optional[dict]:
    db_teste = await get_teste(db, teste_id)
    if not db_teste:
        return None
    id_matriz = db_teste.lote.id_arvore_matriz
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_teste, field, value)
    await db.commit()
    await _sync_taxa_matriz(db, id_matriz)
    await db.commit()
    db_teste = await get_teste(db, teste_id)
    return _para_resposta(db_teste)


async def delete_teste(db: AsyncSession, teste_id: int) -> Optional[dict]:
    db_teste = await get_teste(db, teste_id)
    if not db_teste:
        return None
    id_matriz = db_teste.lote.id_arvore_matriz
    resp = _para_resposta(db_teste)
    await db.delete(db_teste)
    await db.commit()
    await _sync_taxa_matriz(db, id_matriz)
    await db.commit()
    return resp
