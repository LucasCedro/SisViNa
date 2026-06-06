"""CRUD NF-e — emissão a partir de Venda."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, not_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.compradores import Comprador
from app.models.emitente_fiscal import EmitenteFiscal
from app.models.nota_fiscal import NotaFiscal, NotaFiscalItem
from app.models.plantas import Planta
from app.models.especies import Especie
from app.models.vendas import Venda, ItemVenda
from app.services.nfe_service import (
    NfeProvedorError,
    consultar_nfe,
    enviar_nfe,
    interpretar_resposta_emissao,
    montar_payload_focus,
)
from app.services.nfe_validacao import validar_comprador_para_nfe, validar_emitente_configurado
from app.services.nfe_ambiente import validar_ambiente_emissao
from app.services.tributacao_nfe import montar_contexto_tributario
from app.services.validacao_regra_fiscal import validar_fundamento_regra


async def get_emitente(db: AsyncSession) -> Optional[EmitenteFiscal]:
    result = await db.execute(
        select(EmitenteFiscal).where(EmitenteFiscal.ativo.is_(True)).limit(1)
    )
    return result.scalars().first()


async def upsert_emitente(db: AsyncSession, data: Dict[str, Any]) -> EmitenteFiscal:
    emitente = await get_emitente(db)
    if emitente:
        for k, v in data.items():
            setattr(emitente, k, v)
    else:
        emitente = EmitenteFiscal(**data)
        db.add(emitente)
    validar_ambiente_emissao(emitente)
    await db.commit()
    await db.refresh(emitente)
    return emitente


async def get_nota(db: AsyncSession, nota_id: int) -> Optional[NotaFiscal]:
    result = await db.execute(
        select(NotaFiscal)
        .options(selectinload(NotaFiscal.itens))
        .where(NotaFiscal.id == nota_id)
    )
    return result.scalars().first()


async def list_notas_venda(db: AsyncSession, venda_id: int) -> List[NotaFiscal]:
    result = await db.execute(
        select(NotaFiscal)
        .options(selectinload(NotaFiscal.itens))
        .where(NotaFiscal.id_venda == venda_id)
        .order_by(NotaFiscal.id.desc())
    )
    return list(result.scalars().all())


async def _itens_agregados(db: AsyncSession, venda_id: int) -> List[Dict[str, Any]]:
    q = (
        select(
            Especie.nome_cientifico,
            Especie.nome_popular,
            ItemVenda.quantidade,
            ItemVenda.valor_unitario,
            ItemVenda.valor_total,
        )
        .join(Planta, ItemVenda.id_planta == Planta.id)
        .join(Especie, Planta.id_especie == Especie.id)
        .where(ItemVenda.id_venda == venda_id)
    )
    rows = (await db.execute(q)).all()
    if not rows:
        raise ValueError("Venda sem itens")

    agregado: Dict[str, Dict[str, Any]] = {}
    for nome_cientifico, nome_popular, qtd, vu, vt in rows:
        chave = nome_cientifico or "Muda"
        if chave not in agregado:
            agregado[chave] = {
                "descricao": f"Muda — {nome_popular or nome_cientifico}",
                "quantidade": Decimal("0"),
                "valor_unitario": Decimal(str(vu)),
                "valor_total": Decimal("0"),
            }
        agregado[chave]["quantidade"] += Decimal(str(qtd))
        agregado[chave]["valor_total"] += Decimal(str(vt))

    return list(agregado.values())


async def emitir_nfe_venda(db: AsyncSession, venda_id: int) -> Dict[str, Any]:
    venda = await db.get(Venda, venda_id)
    if not venda:
        raise ValueError("Venda não encontrada")
    if venda.status == "CANCELADO":
        raise ValueError("Não é possível emitir NF-e de venda cancelada")

    emitente = await get_emitente(db)
    validar_emitente_configurado(emitente)
    validar_ambiente_emissao(emitente)

    comprador = await db.get(Comprador, venda.id_comprador)
    if not comprador:
        raise ValueError("Comprador não encontrado")
    validar_comprador_para_nfe(comprador)

    nota_existente = await db.execute(
        select(NotaFiscal).where(
            NotaFiscal.id_venda == venda_id,
            NotaFiscal.status.in_(("processando", "autorizada")),
        )
    )
    if nota_existente.scalars().first():
        raise ValueError("Já existe NF-e em processamento ou autorizada para esta venda")

    itens = await _itens_agregados(db, venda_id)
    ctx = await montar_contexto_tributario(
        db, emitente, comprador, itens, tipo_operacao_fiscal=venda.tipo_operacao_fiscal
    )
    validar_fundamento_regra(
        {
            "isento_icms": ctx.regra.isento_icms,
            "reducao_bc_icms_percent": ctx.regra.reducao_bc_icms_percent,
            "fundamento_legal": ctx.regra.fundamento_legal,
        }
    )

    numero = emitente.proximo_numero_nfe
    serie = emitente.serie_nfe
    ref_externa = f"venda-{venda_id}-{uuid.uuid4().hex[:12]}"

    payload = montar_payload_focus(
        emitente,
        comprador,
        ctx,
        numero=numero,
        serie=serie,
        ref_externa=ref_externa,
    )

    nota = NotaFiscal(
        id_venda=venda_id,
        ref_externa=ref_externa,
        numero=numero,
        serie=serie,
        status="processando",
        payload_enviado=payload,
        difal_snapshot=ctx.difal,
        importacao_snapshot=ctx.importacao,
        data_emissao=datetime.utcnow(),
    )
    db.add(nota)
    await db.flush()

    for idx, linha in enumerate(ctx.linhas, start=1):
        db.add(
            NotaFiscalItem(
                id_nota=nota.id,
                numero_item=idx,
                descricao=linha.descricao,
                ncm=linha.ncm,
                cfop=linha.cfop,
                csosn=linha.csosn,
                unidade=linha.unidade,
                quantidade=linha.quantidade,
                valor_unitario=linha.valor_unitario,
                valor_total=linha.valor_total,
            )
        )

    try:
        resposta = await enviar_nfe(emitente, ref_externa, payload)
    except NfeProvedorError as exc:
        nota.status = "rejeitada"
        nota.xmotivo = str(exc)
        nota.resposta_provedor = exc.body if isinstance(exc.body, dict) else {"erro": str(exc)}
        await db.commit()
        await db.refresh(nota)
        raise

    nota.resposta_provedor = resposta
    parsed = interpretar_resposta_emissao(resposta)
    nota.status = parsed["status"]
    nota.cstat = parsed["cstat"]
    nota.xmotivo = parsed["xmotivo"]
    nota.chave_acesso = parsed["chave_acesso"]
    nota.recibo = parsed["recibo"]
    nota.url_xml = parsed["url_xml"]
    nota.url_danfe = parsed["url_danfe"]
    if parsed.get("numero"):
        nota.numero = parsed["numero"]
    if parsed.get("serie"):
        nota.serie = parsed["serie"]

    if nota.status == "autorizada":
        emitente.proximo_numero_nfe = numero + 1

    await db.commit()
    await db.refresh(nota)
    return {"nota": nota, "mensagem": nota.xmotivo or "NF-e enviada"}


async def atualizar_status_nota(db: AsyncSession, nota_id: int) -> Optional[NotaFiscal]:
    nota = await get_nota(db, nota_id)
    if not nota:
        return None
    emitente = await get_emitente(db)
    if not emitente:
        return nota

    try:
        body = await consultar_nfe(emitente, nota.ref_externa)
    except NfeProvedorError:
        return nota

    parsed = interpretar_resposta_emissao(body)
    nota.status = parsed["status"]
    nota.cstat = parsed["cstat"]
    nota.xmotivo = parsed["xmotivo"]
    nota.chave_acesso = parsed["chave_acesso"] or nota.chave_acesso
    nota.url_xml = parsed["url_xml"] or nota.url_xml
    nota.url_danfe = parsed["url_danfe"] or nota.url_danfe
    nota.resposta_provedor = body
    await db.commit()
    await db.refresh(nota)
    return nota


async def list_notas_fiscais(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    q = (
        select(
            NotaFiscal,
            Venda.data_venda,
            Venda.valor_total,
            Venda.status.label("status_venda"),
            Comprador.nome.label("comprador_nome"),
        )
        .join(Venda, NotaFiscal.id_venda == Venda.id)
        .join(Comprador, Venda.id_comprador == Comprador.id)
        .options(selectinload(NotaFiscal.itens))
        .order_by(NotaFiscal.id.desc())
        .offset(skip)
        .limit(limit)
    )
    if status:
        q = q.where(NotaFiscal.status == status)

    rows = (await db.execute(q)).all()
    out: List[Dict[str, Any]] = []
    for nota, data_venda, valor_total, status_venda, comprador_nome in rows:
        d = {
            "id": nota.id,
            "id_venda": nota.id_venda,
            "ref_externa": nota.ref_externa,
            "chave_acesso": nota.chave_acesso,
            "numero": nota.numero,
            "serie": nota.serie,
            "status": nota.status,
            "cstat": nota.cstat,
            "xmotivo": nota.xmotivo,
            "recibo": nota.recibo,
            "url_xml": nota.url_xml,
            "url_danfe": nota.url_danfe,
            "difal_snapshot": nota.difal_snapshot,
            "data_emissao": nota.data_emissao,
            "data_venda": data_venda,
            "valor_venda": float(valor_total or 0),
            "status_venda": status_venda,
            "comprador_nome": comprador_nome,
            "itens": [],
        }
        out.append(d)
    return out


async def resumo_fiscal(db: AsyncSession) -> Dict[str, Any]:
    total = await db.scalar(select(func.count(NotaFiscal.id))) or 0
    por_status = (
        await db.execute(
            select(NotaFiscal.status, func.count(NotaFiscal.id)).group_by(NotaFiscal.status)
        )
    ).all()

    nota_autorizada = exists(
        select(NotaFiscal.id).where(
            NotaFiscal.id_venda == Venda.id,
            NotaFiscal.status.in_(("autorizada", "processando")),
        )
    ).correlate(Venda)
    pendentes = (
        await db.scalar(
            select(func.count(Venda.id)).where(
                Venda.status != "CANCELADO",
                not_(nota_autorizada),
            )
        )
        or 0
    )

    valor_autorizado = (
        await db.scalar(
            select(func.coalesce(func.sum(Venda.valor_total), 0))
            .select_from(NotaFiscal)
            .join(Venda, NotaFiscal.id_venda == Venda.id)
            .where(NotaFiscal.status == "autorizada")
        )
        or 0
    )

    return {
        "total_notas": total,
        "por_status": {s: c for s, c in por_status},
        "vendas_sem_nfe": pendentes,
        "valor_autorizado": float(valor_autorizado),
    }


async def vendas_pendentes_nfe(db: AsyncSession, limit: int = 50) -> List[Dict[str, Any]]:
    nota_ok = exists(
        select(NotaFiscal.id).where(
            NotaFiscal.id_venda == Venda.id,
            NotaFiscal.status.in_(("autorizada", "processando")),
        )
    ).correlate(Venda)
    q = (
        select(Venda, Comprador.nome.label("comprador_nome"))
        .join(Comprador, Venda.id_comprador == Comprador.id)
        .where(Venda.status != "CANCELADO", not_(nota_ok))
        .order_by(Venda.data_venda.desc())
        .limit(limit)
    )
    rows = (await db.execute(q)).all()
    return [
        {
            "id": v.id,
            "data_venda": v.data_venda,
            "valor_total": float(v.valor_total or 0),
            "status": v.status,
            "comprador_nome": comprador_nome,
        }
        for v, comprador_nome in rows
    ]


async def processar_webhook(db: AsyncSession, payload: Dict[str, Any]) -> Optional[NotaFiscal]:
    ref = payload.get("ref") or payload.get("referencia")
    if not ref:
        return None

    result = await db.execute(select(NotaFiscal).where(NotaFiscal.ref_externa == ref))
    nota = result.scalars().first()
    if not nota:
        return None

    parsed = interpretar_resposta_emissao(payload)
    nota.status = parsed["status"]
    nota.cstat = parsed["cstat"]
    nota.xmotivo = parsed["xmotivo"]
    nota.chave_acesso = parsed["chave_acesso"] or nota.chave_acesso
    nota.recibo = parsed["recibo"] or nota.recibo
    nota.url_xml = parsed["url_xml"] or nota.url_xml
    nota.url_danfe = parsed["url_danfe"] or nota.url_danfe
    nota.resposta_provedor = payload
    await db.commit()
    await db.refresh(nota)
    return nota
