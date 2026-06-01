from datetime import date
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.arvores_matriz import ArvoreMatriz
from app.models.coletas_sementes import ColetaSementes
from app.models.lotes_sementes import LoteSementes
from app.models.testes_sementes import TesteSementes
from app.schemas.lotes_sementes import LoteSementesCreate, LoteSementesUpdate
from app.utils.especies_display import formatar_nome_popular


def _codigo_lote(matriz_id: int, coleta_id: int) -> str:
    return f"LS-{date.today().year}-{matriz_id:03d}-{coleta_id:04d}"


def _para_resposta(lote: LoteSementes, ultimo_teste: Optional[float] = None) -> dict:
    arvore = lote.arvore_matriz
    coleta = lote.coleta
    especie = lote.especie or (arvore.especie if arvore else None)
    nome_especie = None
    if especie:
        nome_especie = formatar_nome_popular(especie.nome_popular) or especie.nome_cientifico
    return {
        "id": lote.id,
        "codigo_lote": lote.codigo_lote,
        "id_coleta_sementes": lote.id_coleta_sementes,
        "id_arvore_matriz": lote.id_arvore_matriz,
        "origem_lote": getattr(lote, "origem_lote", "coleta") or "coleta",
        "matriz_nome": arvore.nome if arvore else None,
        "id_especie": lote.id_especie,
        "especie_nome": nome_especie,
        "quantidade_inicial": lote.quantidade_inicial,
        "quantidade_disponivel": lote.quantidade_disponivel,
        "valor_total": float(lote.valor_total) if lote.valor_total is not None else None,
        "custo_unitario": float(lote.custo_unitario) if lote.custo_unitario is not None else None,
        "data_formacao_lote": lote.data_formacao_lote,
        "data_coleta": coleta.data_coleta if coleta else None,
        "beneficiamento": lote.beneficiamento,
        "condicoes_armazenamento": lote.condicoes_armazenamento,
        "status": lote.status,
        "observacoes": lote.observacoes,
        "data_registro": lote.data_registro,
        "ultimo_teste_germinacao": ultimo_teste,
    }


async def _ultimo_teste_germinacao(db: AsyncSession, id_lote: int) -> Optional[float]:
    mapa = await _mapa_ultimos_testes_germinacao(db, [id_lote])
    return mapa.get(id_lote)


async def _mapa_ultimos_testes_germinacao(
    db: AsyncSession, ids_lotes: List[int]
) -> dict[int, float]:
    if not ids_lotes:
        return {}
    ranked = (
        select(
            TesteSementes.id_lote_sementes,
            TesteSementes.percentual_resultado,
            func.row_number()
            .over(
                partition_by=TesteSementes.id_lote_sementes,
                order_by=(TesteSementes.data_teste.desc(), TesteSementes.id.desc()),
            )
            .label("rn"),
        )
        .where(
            TesteSementes.id_lote_sementes.in_(ids_lotes),
            TesteSementes.tipo_teste == "germinacao",
        )
        .subquery()
    )
    result = await db.execute(
        select(ranked.c.id_lote_sementes, ranked.c.percentual_resultado).where(ranked.c.rn == 1)
    )
    return {
        int(row.id_lote_sementes): float(row.percentual_resultado)
        for row in result
        if row.percentual_resultado is not None
    }


async def get_lote(db: AsyncSession, lote_id: int) -> Optional[LoteSementes]:
    result = await db.execute(
        select(LoteSementes)
        .options(
            joinedload(LoteSementes.arvore_matriz).joinedload(ArvoreMatriz.especie),
            joinedload(LoteSementes.coleta),
            joinedload(LoteSementes.especie),
        )
        .where(LoteSementes.id == lote_id)
    )
    return result.scalars().first()


async def get_lotes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 2000,
    id_arvore_matriz: Optional[int] = None,
    id_coleta_sementes: Optional[int] = None,
    status: Optional[str] = None,
) -> List[dict]:
    query = (
        select(LoteSementes)
        .options(
            joinedload(LoteSementes.arvore_matriz).joinedload(ArvoreMatriz.especie),
            joinedload(LoteSementes.coleta),
            joinedload(LoteSementes.especie),
        )
        .order_by(LoteSementes.data_formacao_lote.desc(), LoteSementes.id.desc())
    )
    if id_arvore_matriz:
        query = query.where(LoteSementes.id_arvore_matriz == id_arvore_matriz)
    if id_coleta_sementes:
        query = query.where(LoteSementes.id_coleta_sementes == id_coleta_sementes)
    if status:
        query = query.where(LoteSementes.status == status)

    result = await db.execute(query.offset(skip).limit(limit))
    lotes = result.scalars().unique().all()
    testes = await _mapa_ultimos_testes_germinacao(db, [l.id for l in lotes])
    return [_para_resposta(lote, testes.get(lote.id)) for lote in lotes]


async def criar_lote_de_coleta(
    db: AsyncSession,
    coleta: ColetaSementes,
    beneficiamento: Optional[str] = None,
    condicoes_armazenamento: Optional[str] = None,
    codigo_lote: Optional[str] = None,
) -> LoteSementes:
    arvore = coleta.arvore_matriz or await db.get(ArvoreMatriz, coleta.id_arvore_matriz)
    codigo = codigo_lote or _codigo_lote(coleta.id_arvore_matriz, coleta.id)
    qtd = coleta.quantidade_sementes
    db_lote = LoteSementes(
        codigo_lote=codigo,
        id_coleta_sementes=coleta.id,
        id_arvore_matriz=coleta.id_arvore_matriz,
        id_especie=arvore.id_especie,
        quantidade_inicial=qtd,
        quantidade_disponivel=qtd,
        data_formacao_lote=coleta.data_coleta,
        beneficiamento=beneficiamento,
        condicoes_armazenamento=condicoes_armazenamento,
        status="ativo",
    )
    db.add(db_lote)
    await db.flush()
    return db_lote


async def create_lote(db: AsyncSession, payload: LoteSementesCreate) -> dict:
    coleta = await db.get(ColetaSementes, payload.id_coleta_sementes)
    if not coleta:
        raise ValueError("Coleta não encontrada")

    qtd = payload.quantidade_inicial or coleta.quantidade_sementes
    if qtd <= 0:
        raise ValueError("Quantidade do lote deve ser maior que zero")

    codigo = payload.codigo_lote or _codigo_lote(coleta.id_arvore_matriz, coleta.id)
    arvore = await db.get(ArvoreMatriz, coleta.id_arvore_matriz)
    db_lote = LoteSementes(
        codigo_lote=codigo,
        id_coleta_sementes=coleta.id,
        id_arvore_matriz=coleta.id_arvore_matriz,
        id_especie=arvore.id_especie,
        quantidade_inicial=qtd,
        quantidade_disponivel=qtd,
        data_formacao_lote=payload.data_formacao_lote or coleta.data_coleta,
        beneficiamento=payload.beneficiamento,
        condicoes_armazenamento=payload.condicoes_armazenamento,
        status=payload.status or "ativo",
        observacoes=payload.observacoes,
    )
    db.add(db_lote)
    await db.commit()
    lote = await get_lote(db, db_lote.id)
    ultimo = await _ultimo_teste_germinacao(db, lote.id)
    return _para_resposta(lote, ultimo)


async def criar_lote_armazem(db: AsyncSession, payload) -> dict:
    from app.models.especies import Especie

    especie = await db.get(Especie, payload.id_especie)
    if not especie:
        raise ValueError("Espécie não encontrada")

    id_matriz = payload.id_arvore_matriz
    if id_matriz:
        arvore = await db.get(ArvoreMatriz, id_matriz)
        if not arvore:
            raise ValueError("Árvore matriz não encontrada")
        if arvore.id_especie != payload.id_especie:
            raise ValueError("Matriz não pertence à espécie informada")

    origem = payload.origem_lote or "armazem"
    codigo = payload.codigo_lote or f"LS-{origem.upper()[:3]}-{date.today().year}-{payload.id_especie:04d}"

    db_lote = LoteSementes(
        codigo_lote=codigo,
        id_coleta_sementes=None,
        id_arvore_matriz=id_matriz,
        id_especie=payload.id_especie,
        quantidade_inicial=payload.quantidade,
        quantidade_disponivel=payload.quantidade,
        data_formacao_lote=date.today(),
        beneficiamento=payload.beneficiamento,
        condicoes_armazenamento=payload.condicoes_armazenamento,
        observacoes=payload.observacoes,
        origem_lote=origem,
        status="ativo",
    )
    from app.services.custeio import definir_valor_lote_entrada

    definir_valor_lote_entrada(db_lote, getattr(payload, "valor_total", None))
    db.add(db_lote)
    await db.commit()
    lote = await get_lote(db, db_lote.id)
    ultimo = await _ultimo_teste_germinacao(db, lote.id)
    return _para_resposta(lote, ultimo)


async def update_lote(db: AsyncSession, lote_id: int, payload: LoteSementesUpdate) -> Optional[dict]:
    db_lote = await get_lote(db, lote_id)
    if not db_lote:
        return None
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_lote, field, value)
    if db_lote.quantidade_disponivel <= 0 and db_lote.status == "ativo":
        db_lote.status = "esgotado"
    await db.commit()
    db_lote = await get_lote(db, lote_id)
    ultimo = await _ultimo_teste_germinacao(db, lote_id)
    return _para_resposta(db_lote, ultimo)
