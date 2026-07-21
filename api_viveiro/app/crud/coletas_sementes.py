from datetime import date
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.lotes_sementes import _para_resposta as lote_para_resposta, _ultimo_teste_germinacao, criar_lote_de_coleta
from app.models.arvores_matriz import ArvoreMatriz
from app.models.coletas_sementes import ColetaSementes
from app.models.lotes_sementes import LoteSementes
from app.models.viveiros import Viveiro
from app.schemas.coletas_sementes import ColetaSementesCreate, ColetaSementesUpdate
from app.services.custeio import (
    aplicar_custo_campo_no_lote,
    calcular_custo_coleta_campo,
    obter_valor_hora_coleta_campo,
)
from app.utils.especies_display import formatar_nome_popular


def _validar_reserva_teste(quantidade: int, reservadas: int) -> None:
    reservadas = int(reservadas or 0)
    if reservadas < 0:
        raise ValueError("Reserva para teste não pode ser negativa")
    if reservadas >= quantidade:
        raise ValueError(
            "As sementes reservadas para teste devem ser menores que a quantidade coletada "
            "(o lote de armazém precisa de ao menos 1 semente)"
        )


def quantidade_lote_armazem(coleta: ColetaSementes) -> int:
    """Quantidade que entra no lote — exclui sementes já separadas para teste."""
    reservadas = int(getattr(coleta, "sementes_reservadas_teste", 0) or 0)
    return int(coleta.quantidade_sementes) - reservadas


def _para_resposta(coleta: ColetaSementes, lotes: Optional[list] = None) -> dict:
    arvore = coleta.arvore_matriz
    especie = arvore.especie if arvore else None
    nome_especie = None
    if especie:
        nome_especie = formatar_nome_popular(especie.nome_popular) or especie.nome_cientifico
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
        "sementes_reservadas_teste": int(coleta.sementes_reservadas_teste or 0),
        "horas_campo": float(coleta.horas_campo) if coleta.horas_campo is not None else None,
        "custo_campo_total": float(coleta.custo_campo_total)
        if coleta.custo_campo_total is not None
        else None,
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


async def _id_empresa_da_coleta(db: AsyncSession, coleta: ColetaSementes) -> Optional[int]:
    arvore = coleta.arvore_matriz
    if arvore is None:
        arvore = await db.get(ArvoreMatriz, coleta.id_arvore_matriz)
    if arvore is None:
        return None
    viveiro = await db.get(Viveiro, arvore.id_viveiro)
    return int(viveiro.id_empresa) if viveiro else None


async def sanear_custos_coleta_campo_pendentes(
    db: AsyncSession,
    *,
    id_viveiro: Optional[int] = None,
    id_empresa: Optional[int] = None,
) -> int:
    """Recalcula lotes quando a coleta já tem horas mas o valor não foi propagado ao lote."""
    stmt = (
        select(ColetaSementes)
        .join(LoteSementes, LoteSementes.id_coleta_sementes == ColetaSementes.id)
        .options(joinedload(ColetaSementes.lotes))
        .where(
            LoteSementes.status == "ativo",
            LoteSementes.quantidade_disponivel > 0,
            ColetaSementes.horas_campo.isnot(None),
            ColetaSementes.horas_campo > 0,
            func.coalesce(LoteSementes.valor_total, 0) <= 0,
        )
    )
    if id_viveiro is not None:
        stmt = stmt.where(LoteSementes.id_viveiro == id_viveiro)
    elif id_empresa is not None:
        stmt = stmt.where(
            LoteSementes.id_viveiro.in_(
                select(Viveiro.id).where(Viveiro.id_empresa == id_empresa)
            )
        )
    result = await db.execute(stmt.distinct())
    coletas = result.scalars().unique().all()
    if not coletas:
        return 0
    for coleta in coletas:
        await _recalcular_custo_lotes_coleta(db, coleta)
    await db.commit()
    return len(coletas)


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
    id_viveiro: Optional[int] = None,
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
    if id_viveiro is not None:
        query = query.where(ArvoreMatriz.id_viveiro == id_viveiro)
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


async def _aplicar_custo_campo_coleta(
    db: AsyncSession, coleta: ColetaSementes, lote=None, id_empresa: Optional[int] = None
) -> None:
    if id_empresa is None:
        id_empresa = await _id_empresa_da_coleta(db, coleta)
    valor_hora = await obter_valor_hora_coleta_campo(db, id_empresa=id_empresa)
    qtd_lote = quantidade_lote_armazem(coleta)
    total, _ = calcular_custo_coleta_campo(coleta.horas_campo, valor_hora, qtd_lote)
    coleta.custo_campo_total = total if total > 0 else None
    if lote is not None:
        aplicar_custo_campo_no_lote(lote, total, qtd_lote)


async def _recalcular_custo_lotes_coleta(
    db: AsyncSession, coleta: ColetaSementes, id_empresa: Optional[int] = None
) -> None:
    if id_empresa is None:
        id_empresa = await _id_empresa_da_coleta(db, coleta)
    valor_hora = await obter_valor_hora_coleta_campo(db, id_empresa=id_empresa)
    qtd_lote = quantidade_lote_armazem(coleta)
    total, _ = calcular_custo_coleta_campo(coleta.horas_campo, valor_hora, qtd_lote)
    coleta.custo_campo_total = total if total > 0 else None
    for lote in coleta.lotes or []:
        if lote.id_coleta_sementes != coleta.id:
            continue
        if (lote.status or "ativo") != "ativo":
            continue
        aplicar_custo_campo_no_lote(lote, total, qtd_lote)


async def get_custo_campo_referencia(
    db: AsyncSession, id_empresa: Optional[int] = None
) -> dict:
    from app.models.financeiro_premissa import FinanceiroPremissa

    from app.services.custeio import CHAVE_PREMISSA_COLETA_CAMPO

    clauses = [FinanceiroPremissa.chave == CHAVE_PREMISSA_COLETA_CAMPO]
    if id_empresa is not None:
        clauses.append(FinanceiroPremissa.id_empresa == id_empresa)
    result = await db.execute(select(FinanceiroPremissa).where(*clauses))
    prem = result.scalars().first()
    valor = float(prem.valor or 0) if prem and prem.ativo else 0.0
    return {
        "valor_hora": valor,
        "premissa_ativa": bool(prem and prem.ativo and valor > 0),
        "nome": prem.nome if prem else "Mão de obra de coleta",
    }


async def create_coleta(
    db: AsyncSession, payload: ColetaSementesCreate, id_funcionario: int
) -> dict:
    arvore = await db.get(ArvoreMatriz, payload.id_arvore_matriz)
    if not arvore:
        raise ValueError("Árvore matriz não encontrada")

    dados = payload.dict()
    gerar_lote = dados.pop("gerar_lote", True)
    reservadas = int(dados.get("sementes_reservadas_teste") or 0)
    _validar_reserva_teste(dados["quantidade_sementes"], reservadas)
    horas = dados.get("horas_campo")
    db_coleta = ColetaSementes(
        id_arvore_matriz=dados["id_arvore_matriz"],
        id_funcionario=id_funcionario,
        data_coleta=dados["data_coleta"],
        quantidade_sementes=dados["quantidade_sementes"],
        sementes_reservadas_teste=reservadas,
        horas_campo=horas,
        observacoes=dados.get("observacoes"),
    )
    db.add(db_coleta)
    await db.flush()
    coleta_id = db_coleta.id

    coleta = await get_coleta(db, coleta_id)
    if gerar_lote:
        lote = await criar_lote_de_coleta(db, coleta)
        await _aplicar_custo_campo_coleta(db, db_coleta, lote)
    elif horas is not None:
        await _aplicar_custo_campo_coleta(db, db_coleta, None)

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
    update_data = payload.dict(exclude_unset=True)
    qtd = update_data.get("quantidade_sementes", db_coleta.quantidade_sementes)
    reservadas = update_data.get(
        "sementes_reservadas_teste", db_coleta.sementes_reservadas_teste or 0
    )
    if "quantidade_sementes" in update_data or "sementes_reservadas_teste" in update_data:
        _validar_reserva_teste(qtd, reservadas)
    for field, value in update_data.items():
        setattr(db_coleta, field, value)

    if "data_coleta" in update_data:
        nova_data = update_data["data_coleta"]
        for lote in db_coleta.lotes or []:
            if lote.id_coleta_sementes == db_coleta.id:
                lote.data_formacao_lote = nova_data

    if any(
        k in update_data
        for k in ("horas_campo", "quantidade_sementes", "sementes_reservadas_teste")
    ):
        await _recalcular_custo_lotes_coleta(db, db_coleta)

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
