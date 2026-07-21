import uuid
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.arvores_matriz import ArvoreMatriz
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta
from app.models.semeaduras import Semeadura
from app.schemas.semeaduras import (
    SemeaduraCreate,
    SemeaduraLoteCreate,
    SemeaduraUpdate,
)

_PLANTAS_CHUNK = 500


def _codigo_rastreio_semeadura(semeadura_id: int, indice: int) -> str:
    """Código único dentro do limite de 20 caracteres (plantas.codigo_rastreio)."""
    codigo = f"M-S{semeadura_id:05d}-{indice:04d}"
    if len(codigo) > 20:
        codigo = f"M{semeadura_id:05d}{indice:04d}"
    return codigo[:20]


def _para_resposta(semeadura: Semeadura, plantas_count: int = 0) -> dict:
    lote = semeadura.lote
    arvore = lote.arvore_matriz if lote else None
    coleta = lote.coleta if lote else None
    especie = arvore.especie if arvore else None
    nome_especie = None
    if especie:
        nome_especie = especie.nome_popular or especie.nome_cientifico
    return {
        "id": semeadura.id,
        "id_lote_sementes": semeadura.id_lote_sementes,
        "codigo_lote": lote.codigo_lote if lote else "",
        "id_arvore_matriz": lote.id_arvore_matriz if lote else 0,
        "matriz_nome": arvore.nome if arvore else "",
        "id_especie": lote.id_especie if lote else 0,
        "especie_nome": nome_especie,
        "id_canteiro": semeadura.id_canteiro,
        "canteiro_nome": semeadura.canteiro.nome if semeadura.canteiro else None,
        "data_semeadura": semeadura.data_semeadura,
        "data_coleta": coleta.data_coleta if coleta else None,
        "quantidade_sementes_usadas": semeadura.quantidade_sementes_usadas,
        "quantidade_mudas_obtidas": semeadura.quantidade_mudas_obtidas,
        "observacoes": semeadura.observacoes,
        "id_funcionario": semeadura.id_funcionario,
        "funcionario_nome": semeadura.funcionario.nome if semeadura.funcionario else "",
        "data_registro": semeadura.data_registro,
        "plantas_vinculadas": plantas_count,
        "custo_sementes": float(semeadura.custo_sementes or 0),
        "custo_insumos": float(semeadura.custo_insumos or 0),
        "custo_indireto": float(semeadura.custo_indireto or 0),
        "custo_total": float(semeadura.custo_total or 0),
        "custo_unitario_muda": float(semeadura.custo_unitario_muda) if semeadura.custo_unitario_muda else None,
    }


async def get_semeadura(db: AsyncSession, semeadura_id: int) -> Optional[Semeadura]:
    result = await db.execute(
        select(Semeadura)
        .options(
            joinedload(Semeadura.lote).joinedload(LoteSementes.arvore_matriz).joinedload(ArvoreMatriz.especie),
            joinedload(Semeadura.lote).joinedload(LoteSementes.coleta),
            joinedload(Semeadura.canteiro),
            joinedload(Semeadura.funcionario),
        )
        .where(Semeadura.id == semeadura_id)
    )
    return result.scalars().first()


async def _count_plantas(db: AsyncSession, semeadura_id: int) -> int:
    result = await db.execute(
        select(func.count(Planta.id)).where(Planta.id_semeadura == semeadura_id)
    )
    return int(result.scalar() or 0)


async def get_semeaduras(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 2000,
    id_lote_sementes: Optional[int] = None,
    id_arvore_matriz: Optional[int] = None,
) -> List[dict]:
    query = (
        select(Semeadura)
        .join(LoteSementes, Semeadura.id_lote_sementes == LoteSementes.id)
        .options(
            joinedload(Semeadura.lote).joinedload(LoteSementes.arvore_matriz).joinedload(ArvoreMatriz.especie),
            joinedload(Semeadura.lote).joinedload(LoteSementes.coleta),
            joinedload(Semeadura.canteiro),
            joinedload(Semeadura.funcionario),
        )
        .order_by(Semeadura.data_semeadura.desc(), Semeadura.id.desc())
    )
    if id_lote_sementes:
        query = query.where(Semeadura.id_lote_sementes == id_lote_sementes)
    if id_arvore_matriz:
        query = query.where(LoteSementes.id_arvore_matriz == id_arvore_matriz)

    result = await db.execute(query.offset(skip).limit(limit))
    semeaduras = result.scalars().unique().all()
    saida = []
    for s in semeaduras:
        cnt = await _count_plantas(db, s.id)
        saida.append(_para_resposta(s, cnt))
    return saida


async def _validar_canteiro_sementeira(db: AsyncSession, id_canteiro: Optional[int]) -> None:
    from app.models.canteiros import Canteiro

    if not id_canteiro:
        return
    cant = await db.get(Canteiro, id_canteiro)
    if not cant:
        raise ValueError("Canteiro não encontrado")
    if cant.tipo_local != "sementeira":
        raise ValueError("Semeadura deve ser registrada em local tipo sementeira")


def _qtd_plantas_semeadura(dados: dict) -> int:
    qtd_sem = int(dados["quantidade_sementes_usadas"])
    registrar = bool(dados.get("registrar_plantas"))
    if registrar:
        qtd_plantas_informada = int(dados.get("quantidade_plantas_registrar") or 0)
        if qtd_plantas_informada != qtd_sem:
            raise ValueError(
                f"Quantidade de plantas ({qtd_plantas_informada}) deve ser igual às "
                f"sementes usadas ({qtd_sem})."
            )
        return qtd_sem
    if dados.get("quantidade_mudas_obtidas"):
        return int(dados["quantidade_mudas_obtidas"])
    return 0


async def _criar_plantas_semeadura(
    db: AsyncSession,
    *,
    semeadura_id: int,
    lote: LoteSementes,
    id_canteiro: int,
    data_semeadura,
    quantidade: int,
    custo_unitario: float,
) -> int:
    if quantidade <= 0:
        return 0
    cu = float(custo_unitario or 0)
    codigo_lote = lote.codigo_lote
    criadas = 0
    for offset in range(0, quantidade, _PLANTAS_CHUNK):
        batch_qtd = min(_PLANTAS_CHUNK, quantidade - offset)
        batch = []
        for j in range(batch_qtd):
            indice = offset + j + 1
            batch.append(
                Planta(
                    id_especie=lote.id_especie,
                    id_canteiro=id_canteiro,
                    id_lote_sementes=lote.id,
                    id_semeadura=semeadura_id,
                    codigo_rastreio=_codigo_rastreio_semeadura(semeadura_id, indice),
                    data_plantio=data_semeadura,
                    data_inicio_estagio_atual=data_semeadura,
                    status="SEMENTE",
                    estagio_producao="em_desenvolvimento",
                    origem="semeadura",
                    custo_inicial=cu,
                    custo_atual=cu,
                    observacoes=f"Origem lote {codigo_lote}",
                )
            )
        db.add_all(batch)
        await db.flush()
        criadas += batch_qtd
    return criadas


async def _executar_semeadura_item(
    db: AsyncSession,
    *,
    lote: LoteSementes,
    dados: dict,
    id_funcionario: int,
) -> tuple[Semeadura, int]:
    from app.services.custeio import (
        aplicar_baixa_valor_lote,
        calcular_custo_lote_semeadura,
        calcular_custo_sementes_lote,
    )

    qtd_sem = int(dados["quantidade_sementes_usadas"])
    if lote.status == "descartado":
        raise ValueError(f"Lote {lote.codigo_lote} está descartado")
    if qtd_sem > lote.quantidade_disponivel:
        raise ValueError(
            f"Lote {lote.codigo_lote}: quantidade ({qtd_sem}) excede disponível "
            f"({lote.quantidade_disponivel})"
        )

    registrar = bool(dados.get("registrar_plantas"))
    qtd_plantas_criar = _qtd_plantas_semeadura(dados)

    custeio = await calcular_custo_lote_semeadura(db, lote, qtd_sem, qtd_plantas_criar)
    custo_sementes = calcular_custo_sementes_lote(lote, qtd_sem)

    db_sem = Semeadura(
        id_lote_sementes=dados["id_lote_sementes"],
        id_canteiro=dados.get("id_canteiro"),
        data_semeadura=dados["data_semeadura"],
        quantidade_sementes_usadas=qtd_sem,
        quantidade_mudas_obtidas=qtd_plantas_criar or dados.get("quantidade_mudas_obtidas"),
        observacoes=dados.get("observacoes"),
        id_funcionario=id_funcionario,
        custo_sementes=custo_sementes,
        custo_insumos=custeio["custo_insumos"],
        custo_indireto=custeio["custo_indireto"],
        custo_total=custeio["custo_total"],
        custo_unitario_muda=custeio["custo_unitario_muda"],
    )
    aplicar_baixa_valor_lote(lote, qtd_sem, custo_sementes)
    lote.quantidade_disponivel -= qtd_sem
    if lote.quantidade_disponivel <= 0:
        lote.status = "esgotado"
    db.add(db_sem)
    await db.flush()

    plantas_criadas = 0
    if registrar and qtd_plantas_criar > 0:
        plantas_criadas = await _criar_plantas_semeadura(
            db,
            semeadura_id=db_sem.id,
            lote=lote,
            id_canteiro=dados["id_canteiro"],
            data_semeadura=dados["data_semeadura"],
            quantidade=qtd_plantas_criar,
            custo_unitario=custeio["custo_unitario_muda"],
        )

    return db_sem, plantas_criadas


async def create_semeadura(db: AsyncSession, payload: SemeaduraCreate, id_funcionario: int) -> dict:
    lote = await db.get(LoteSementes, payload.id_lote_sementes)
    if not lote:
        raise ValueError("Lote não encontrado")
    await _validar_canteiro_sementeira(db, payload.id_canteiro)

    dados = payload.dict()
    db_sem, plantas_criadas = await _executar_semeadura_item(db, lote=lote, dados=dados, id_funcionario=id_funcionario)

    from app.services.custeio import redistribuir_cif_parque

    await redistribuir_cif_parque(db, commit=False)

    await db.commit()
    sem = await get_semeadura(db, db_sem.id)
    cnt = await _count_plantas(db, db_sem.id)
    return _para_resposta(sem, cnt)


async def create_semeaduras_lote(
    db: AsyncSession, payload: SemeaduraLoteCreate, id_funcionario: int
) -> dict:
    from app.models.canteiros import Canteiro
    from app.models.especies import Especie

    await _validar_canteiro_sementeira(db, payload.id_canteiro)
    cant = await db.get(Canteiro, payload.id_canteiro)
    if not cant:
        raise ValueError("Sementeira não encontrada")

    lotes_por_id: dict[int, LoteSementes] = {}
    for item in payload.itens:
        if item.id_lote_sementes in lotes_por_id:
            continue
        lote = await db.get(LoteSementes, item.id_lote_sementes)
        if not lote:
            raise ValueError(f"Lote id {item.id_lote_sementes} não encontrado")
        lotes_por_id[item.id_lote_sementes] = lote

    especies: dict[int, str] = {}
    for lote in lotes_por_id.values():
        if lote.id_especie not in especies:
            esp = await db.get(Especie, lote.id_especie)
            especies[lote.id_especie] = (
                (esp.nome_popular or esp.nome_cientifico) if esp else ""
            )

    registrar = bool(payload.registrar_plantas)
    saida_itens = []
    total_sem = 0
    total_plantas = 0

    try:
        for item in payload.itens:
            lote = lotes_por_id[item.id_lote_sementes]
            obs = item.observacoes or payload.observacoes_gerais
            dados = {
                "id_lote_sementes": item.id_lote_sementes,
                "id_canteiro": payload.id_canteiro,
                "data_semeadura": payload.data_semeadura,
                "quantidade_sementes_usadas": item.quantidade_sementes_usadas,
                "observacoes": obs,
                "registrar_plantas": registrar,
                "quantidade_plantas_registrar": item.quantidade_sementes_usadas if registrar else None,
            }
            db_sem, plantas_criadas = await _executar_semeadura_item(
                db, lote=lote, dados=dados, id_funcionario=id_funcionario
            )
            total_sem += item.quantidade_sementes_usadas
            total_plantas += plantas_criadas
            saida_itens.append(
                {
                    "id_lote_sementes": lote.id,
                    "codigo_lote": lote.codigo_lote,
                    "especie_nome": especies.get(lote.id_especie),
                    "quantidade_sementes_usadas": item.quantidade_sementes_usadas,
                    "id_semeadura": db_sem.id,
                    "plantas_criadas": plantas_criadas,
                }
            )
        from app.services.custeio import redistribuir_cif_parque

        await redistribuir_cif_parque(db, commit=False)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {
        "data_semeadura": payload.data_semeadura,
        "id_canteiro": payload.id_canteiro,
        "canteiro_nome": cant.nome,
        "total_sementes": total_sem,
        "total_plantas": total_plantas,
        "itens": saida_itens,
    }


async def get_rastreabilidade_planta(db: AsyncSession, planta_id: int) -> Optional[dict]:
    from app.models.especies import Especie

    from app.models.vendas import ItemVenda, Venda

    result = await db.execute(
        select(Planta)
        .options(
            joinedload(Planta.semeadura).joinedload(Semeadura.lote).joinedload(LoteSementes.coleta),
            joinedload(Planta.lote_sementes).joinedload(LoteSementes.coleta),
            joinedload(Planta.lote_sementes).joinedload(LoteSementes.arvore_matriz),
            joinedload(Planta.especie),
            joinedload(Planta.itens_venda).joinedload(ItemVenda.venda).joinedload(Venda.comprador),
        )
        .where(Planta.id == planta_id)
    )
    planta = result.scalars().first()
    if not planta:
        return None

    lote = planta.lote_sementes or (planta.semeadura.lote if planta.semeadura else None)
    coleta = lote.coleta if lote else None
    matriz = lote.arvore_matriz if lote else None
    especie = planta.especie
    item_venda = planta.itens_venda[0] if planta.itens_venda else None
    venda = item_venda.venda if item_venda else None
    comprador = venda.comprador if venda else None
    return {
        "id_planta": planta.id,
        "codigo_rastreio": planta.codigo_rastreio,
        "status_planta": planta.status,
        "data_plantio": planta.data_plantio,
        "especie_nome": (especie.nome_popular or especie.nome_cientifico) if especie else None,
        "codigo_lote": lote.codigo_lote if lote else None,
        "id_lote": lote.id if lote else None,
        "id_coleta": coleta.id if coleta else None,
        "data_coleta": coleta.data_coleta if coleta else None,
        "id_arvore_matriz": matriz.id if matriz else None,
        "matriz_nome": matriz.nome if matriz else None,
        "imovel_nome": matriz.imovel_nome if matriz else None,
        "municipio": matriz.municipio if matriz else None,
        "tipo_origem": matriz.tipo_origem if matriz else None,
        "numero_autorizacao": matriz.numero_autorizacao if matriz else None,
        "id_semeadura": planta.id_semeadura,
        "data_semeadura": planta.semeadura.data_semeadura if planta.semeadura else None,
        "quantidade_sementes_usadas": planta.semeadura.quantidade_sementes_usadas if planta.semeadura else None,
        "id_venda": venda.id if venda else None,
        "data_venda": venda.data_venda.date() if venda and venda.data_venda else None,
        "comprador_nome": comprador.nome if comprador else None,
        "valor_venda": float(item_venda.valor_total) if item_venda and item_venda.valor_total is not None else None,
    }
