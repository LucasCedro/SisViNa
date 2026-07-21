"""CRUD do módulo florestal — lotes por quantidade."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.florestal_estagios import (
    DESCARTADO,
    ENTRADA_MATERIAL,
    ESTAGIO_LABELS,
    ESTAGIOS_ATIVOS,
    EXPEDICAO,
    TRANSICOES_VALIDAS,
)
from app.models.canteiros import Canteiro
from app.models.genotipos import Genotipo
from app.models.lotes_producao import LoteProducao
from app.models.movimentacoes_lote import MovimentacaoLote
from app.schemas.florestal import (
    FlorestalResumoOut,
    GenotipoCreate,
    GenotipoOut,
    GenotipoUpdate,
    LotePerdaRequest,
    LoteProducaoCreate,
    LoteProducaoOut,
    LoteTransferenciaRequest,
    MovimentacaoLoteOut,
)
from app.security.viveiro_context import ViveiroContext, assert_record_belongs_to_viveiro


def _lote_out(row: LoteProducao, genotipo: Optional[Genotipo] = None) -> LoteProducaoOut:
    g = genotipo or row.genotipo
    return LoteProducaoOut(
        id=row.id,
        id_viveiro=row.id_viveiro,
        id_genotipo=row.id_genotipo,
        genotipo_codigo=g.codigo if g else None,
        genotipo_nome=g.nome if g else None,
        codigo_lote=row.codigo_lote,
        data_entrada=row.data_entrada,
        quantidade_inicial=row.quantidade_inicial,
        quantidade_atual=row.quantidade_atual,
        estagio=row.estagio,
        estagio_label=ESTAGIO_LABELS.get(row.estagio, row.estagio),
        id_canteiro=row.id_canteiro,
        observacoes=row.observacoes,
        data_registro=row.data_registro,
    )


async def list_genotipos(db: AsyncSession, ctx: ViveiroContext, *, ativo: Optional[bool] = True) -> List[GenotipoOut]:
    stmt = select(Genotipo).where(Genotipo.id_viveiro == ctx.id).order_by(Genotipo.codigo)
    if ativo is not None:
        stmt = stmt.where(Genotipo.ativo.is_(ativo))
    rows = (await db.execute(stmt)).scalars().all()
    return [GenotipoOut.from_orm(r) for r in rows]


async def create_genotipo(db: AsyncSession, ctx: ViveiroContext, payload: GenotipoCreate) -> GenotipoOut:
    dup = await db.execute(
        select(Genotipo).where(
            Genotipo.id_viveiro == ctx.id,
            func.lower(Genotipo.codigo) == payload.codigo.strip().lower(),
        )
    )
    if dup.scalars().first():
        raise ValueError("Código de genótipo já cadastrado nesta unidade.")

    row = Genotipo(
        id_viveiro=ctx.id,
        codigo=payload.codigo.strip().upper(),
        nome=payload.nome,
        fornecedor=payload.fornecedor,
        material_genetico=payload.material_genetico,
        observacoes=payload.observacoes,
        ativo=True,
    )
    db.add(row)
    await db.flush()
    return GenotipoOut.from_orm(row)


async def update_genotipo(
    db: AsyncSession, ctx: ViveiroContext, genotipo_id: int, payload: GenotipoUpdate
) -> Optional[GenotipoOut]:
    row = await db.get(Genotipo, genotipo_id)
    if row is None:
        return None
    assert_record_belongs_to_viveiro(row.id_viveiro, ctx, "genotipo")
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    await db.flush()
    return GenotipoOut.from_orm(row)


async def list_lotes(
    db: AsyncSession,
    ctx: ViveiroContext,
    *,
    estagio: Optional[str] = None,
    id_genotipo: Optional[int] = None,
) -> List[LoteProducaoOut]:
    stmt = (
        select(LoteProducao, Genotipo)
        .join(Genotipo, LoteProducao.id_genotipo == Genotipo.id)
        .where(LoteProducao.id_viveiro == ctx.id)
        .order_by(LoteProducao.data_entrada.desc(), LoteProducao.id.desc())
    )
    if estagio:
        stmt = stmt.where(LoteProducao.estagio == estagio)
    if id_genotipo:
        stmt = stmt.where(LoteProducao.id_genotipo == id_genotipo)
    rows = (await db.execute(stmt)).all()
    return [_lote_out(lote, gen) for lote, gen in rows]


async def create_lote(
    db: AsyncSession,
    ctx: ViveiroContext,
    payload: LoteProducaoCreate,
    id_funcionario: int,
) -> LoteProducaoOut:
    gen = await db.get(Genotipo, payload.id_genotipo)
    if gen is None or not gen.ativo:
        raise ValueError("Genótipo não encontrado ou inativo.")
    assert_record_belongs_to_viveiro(gen.id_viveiro, ctx, "genotipo")

    dup = await db.execute(
        select(LoteProducao).where(
            LoteProducao.id_viveiro == ctx.id,
            func.lower(LoteProducao.codigo_lote) == payload.codigo_lote.strip().lower(),
        )
    )
    if dup.scalars().first():
        raise ValueError("Código de lote já existe nesta unidade.")

    if payload.id_canteiro:
        c = await db.get(Canteiro, payload.id_canteiro)
        if c is None:
            raise ValueError("Área/canteiro não encontrado.")
        assert_record_belongs_to_viveiro(c.id_viveiro, ctx, "canteiro")

    row = LoteProducao(
        id_viveiro=ctx.id,
        id_genotipo=payload.id_genotipo,
        codigo_lote=payload.codigo_lote.strip().upper(),
        data_entrada=payload.data_entrada,
        quantidade_inicial=payload.quantidade_inicial,
        quantidade_atual=payload.quantidade_inicial,
        estagio=ENTRADA_MATERIAL,
        id_canteiro=payload.id_canteiro,
        observacoes=payload.observacoes,
    )
    db.add(row)
    await db.flush()

    db.add(
        MovimentacaoLote(
            id_lote_producao=row.id,
            tipo="entrada",
            quantidade=payload.quantidade_inicial,
            estagio_destino=ENTRADA_MATERIAL,
            id_canteiro_destino=payload.id_canteiro,
            id_funcionario=id_funcionario,
            observacoes=payload.observacoes,
        )
    )
    await db.flush()
    return _lote_out(row, gen)


async def transferir_lote(
    db: AsyncSession,
    ctx: ViveiroContext,
    lote_id: int,
    payload: LoteTransferenciaRequest,
    id_funcionario: int,
) -> LoteProducaoOut:
    row = await db.get(LoteProducao, lote_id)
    if row is None:
        raise ValueError("Lote não encontrado.")
    assert_record_belongs_to_viveiro(row.id_viveiro, ctx, "lote_producao")

    if row.estagio not in ESTAGIOS_ATIVOS:
        raise ValueError("Lote não está em estágio ativo.")
    if payload.estagio_destino not in TRANSICOES_VALIDAS.get(row.estagio, frozenset()):
        raise ValueError(f"Transição inválida: {row.estagio} → {payload.estagio_destino}")
    if payload.quantidade > row.quantidade_atual:
        raise ValueError("Quantidade maior que o saldo do lote.")

    if payload.id_canteiro_destino:
        c = await db.get(Canteiro, payload.id_canteiro_destino)
        if c is None:
            raise ValueError("Área destino não encontrada.")
        assert_record_belongs_to_viveiro(c.id_viveiro, ctx, "canteiro")

    origem = row.estagio
    if payload.quantidade == row.quantidade_atual:
        row.estagio = payload.estagio_destino
        row.id_canteiro = payload.id_canteiro_destino or row.id_canteiro
        if payload.estagio_destino == EXPEDICAO:
            row.quantidade_atual = 0
    else:
        # split parcial — novo lote filho no destino
        gen = await db.get(Genotipo, row.id_genotipo)
        suffix = f"-T{row.id}"
        filho = LoteProducao(
            id_viveiro=ctx.id,
            id_genotipo=row.id_genotipo,
            codigo_lote=f"{row.codigo_lote}{suffix}"[:30],
            data_entrada=row.data_entrada,
            quantidade_inicial=payload.quantidade,
            quantidade_atual=0 if payload.estagio_destino == EXPEDICAO else payload.quantidade,
            estagio=payload.estagio_destino,
            id_canteiro=payload.id_canteiro_destino,
            observacoes=f"Split de {row.codigo_lote}",
        )
        db.add(filho)
        row.quantidade_atual -= payload.quantidade
        await db.flush()
        db.add(
            MovimentacaoLote(
                id_lote_producao=filho.id,
                tipo="transferencia",
                quantidade=payload.quantidade,
                estagio_origem=origem,
                estagio_destino=payload.estagio_destino,
                id_canteiro_origem=row.id_canteiro,
                id_canteiro_destino=payload.id_canteiro_destino,
                id_funcionario=id_funcionario,
                observacoes=payload.observacoes,
            )
        )

    db.add(
        MovimentacaoLote(
            id_lote_producao=row.id,
            tipo="expedicao" if payload.estagio_destino == EXPEDICAO else "transferencia",
            quantidade=payload.quantidade,
            estagio_origem=origem,
            estagio_destino=payload.estagio_destino,
            id_canteiro_origem=row.id_canteiro,
            id_canteiro_destino=payload.id_canteiro_destino,
            id_funcionario=id_funcionario,
            observacoes=payload.observacoes,
        )
    )
    await db.flush()
    gen = await db.get(Genotipo, row.id_genotipo)
    return _lote_out(row, gen)


async def registrar_perda(
    db: AsyncSession,
    ctx: ViveiroContext,
    lote_id: int,
    payload: LotePerdaRequest,
    id_funcionario: int,
) -> LoteProducaoOut:
    row = await db.get(LoteProducao, lote_id)
    if row is None:
        raise ValueError("Lote não encontrado.")
    assert_record_belongs_to_viveiro(row.id_viveiro, ctx, "lote_producao")
    if row.estagio not in ESTAGIOS_ATIVOS:
        raise ValueError("Lote não está em estágio ativo.")
    if payload.quantidade > row.quantidade_atual:
        raise ValueError("Quantidade de perda maior que saldo.")

    row.quantidade_atual -= payload.quantidade
    if row.quantidade_atual == 0:
        row.estagio = DESCARTADO

    db.add(
        MovimentacaoLote(
            id_lote_producao=row.id,
            tipo="perda",
            quantidade=payload.quantidade,
            estagio_origem=row.estagio,
            id_funcionario=id_funcionario,
            observacoes=payload.observacoes,
        )
    )
    await db.flush()
    gen = await db.get(Genotipo, row.id_genotipo)
    return _lote_out(row, gen)


async def list_movimentacoes(db: AsyncSession, ctx: ViveiroContext, lote_id: int) -> List[MovimentacaoLoteOut]:
    row = await db.get(LoteProducao, lote_id)
    if row is None:
        return []
    assert_record_belongs_to_viveiro(row.id_viveiro, ctx, "lote_producao")
    result = await db.execute(
        select(MovimentacaoLote)
        .where(MovimentacaoLote.id_lote_producao == lote_id)
        .order_by(MovimentacaoLote.data_movimento.desc())
    )
    return [MovimentacaoLoteOut.from_orm(r) for r in result.scalars().all()]


async def resumo_florestal(db: AsyncSession, ctx: ViveiroContext) -> FlorestalResumoOut:
    genotipos = await db.scalar(
        select(func.count()).select_from(Genotipo).where(Genotipo.id_viveiro == ctx.id, Genotipo.ativo.is_(True))
    )
    lotes_ativos = await db.scalar(
        select(func.count())
        .select_from(LoteProducao)
        .where(LoteProducao.id_viveiro == ctx.id, LoteProducao.estagio.in_(tuple(ESTAGIOS_ATIVOS)))
    )
    mudas = await db.scalar(
        select(func.coalesce(func.sum(LoteProducao.quantidade_atual), 0))
        .where(LoteProducao.id_viveiro == ctx.id, LoteProducao.estagio.in_(tuple(ESTAGIOS_ATIVOS - {EXPEDICAO})))
    )
    expedicao = await db.scalar(
        select(func.coalesce(func.sum(LoteProducao.quantidade_inicial), 0))
        .where(LoteProducao.id_viveiro == ctx.id, LoteProducao.estagio == EXPEDICAO)
    )
    return FlorestalResumoOut(
        genotipos_ativos=int(genotipos or 0),
        lotes_ativos=int(lotes_ativos or 0),
        mudas_em_producao=int(mudas or 0),
        mudas_expedicao=int(expedicao or 0),
        estagios=list(ESTAGIOS_ATIVOS),
    )
