import uuid
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.arvores_matriz import ArvoreMatriz
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta
from app.models.semeaduras import Semeadura
from app.schemas.semeaduras import SemeaduraCreate, SemeaduraUpdate


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


async def create_semeadura(db: AsyncSession, payload: SemeaduraCreate, id_funcionario: int) -> dict:
    from app.models.canteiros import Canteiro

    lote = await db.get(LoteSementes, payload.id_lote_sementes)
    if not lote:
        raise ValueError("Lote não encontrado")
    if payload.id_canteiro:
        cant = await db.get(Canteiro, payload.id_canteiro)
        if not cant:
            raise ValueError("Canteiro não encontrado")
        if cant.tipo_local != "sementeira":
            raise ValueError("Semeadura deve ser registrada em local tipo sementeira")
    if lote.status == "descartado":
        raise ValueError("Lote descartado não pode ser semeado")
    if payload.quantidade_sementes_usadas > lote.quantidade_disponivel:
        raise ValueError("Quantidade usada excede o disponível no lote")

    dados = payload.dict()
    db_sem = Semeadura(
        id_lote_sementes=dados["id_lote_sementes"],
        id_canteiro=dados.get("id_canteiro"),
        data_semeadura=dados["data_semeadura"],
        quantidade_sementes_usadas=dados["quantidade_sementes_usadas"],
        quantidade_mudas_obtidas=dados.get("quantidade_mudas_obtidas"),
        observacoes=dados.get("observacoes"),
        id_funcionario=id_funcionario,
    )
    lote.quantidade_disponivel -= dados["quantidade_sementes_usadas"]
    if lote.quantidade_disponivel <= 0:
        lote.status = "esgotado"
    db.add(db_sem)
    await db.flush()

    if dados.get("registrar_plantas") and dados.get("quantidade_plantas_registrar", 0) > 0:
        qtd_plantas = dados["quantidade_plantas_registrar"]
        for i in range(qtd_plantas):
            codigo = f"M-{lote.codigo_lote}-{db_sem.id}-{i + 1:03d}"
            db.add(
                Planta(
                    id_especie=lote.id_especie,
                    id_canteiro=dados.get("id_canteiro"),
                    id_lote_sementes=lote.id,
                    id_semeadura=db_sem.id,
                    codigo_rastreio=codigo[:20],
                    data_plantio=dados["data_semeadura"],
                    data_inicio_estagio_atual=dados["data_semeadura"],
                    status="SEMENTE",
                    estagio_producao="em_desenvolvimento",
                    origem="semeadura",
                    observacoes=f"Origem lote {lote.codigo_lote}",
                )
            )

    await db.commit()
    sem = await get_semeadura(db, db_sem.id)
    cnt = await _count_plantas(db, db_sem.id)
    return _para_resposta(sem, cnt)


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
