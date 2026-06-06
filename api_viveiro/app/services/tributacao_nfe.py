"""Motor de regras fiscais — CFOP dinâmico, CSOSN, DIFAL."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compradores import Comprador
from app.models.emitente_fiscal import EmitenteFiscal
from app.models.regra_fiscal import RegraFiscal
from app.utils.fiscal_regra_match import escolher_melhor_regra, label_operacao
from app.utils.fiscal import (
    consumidor_final_nao_contribuinte,
    inferir_tipo_operacao_fiscal,
    normalize_ncm,
    resolve_cfop,
    tipo_cliente_fiscal,
)

NCM_MUDAS_PADRAO = "06029090"


@dataclass
class LinhaFiscal:
    descricao: str
    ncm: str
    quantidade: Decimal
    valor_unitario: Decimal
    valor_total: Decimal
    cfop: str
    csosn: str
    unidade: str
    natureza_operacao: str


@dataclass
class ContextoTributario:
    linhas: List[LinhaFiscal]
    difal: Optional[Dict[str, Any]]
    importacao: Optional[Dict[str, Any]]
    uf_origem: str
    uf_destino: str
    tipo_operacao: str
    regra: RegraFiscal


async def buscar_regra(
    db: AsyncSession,
    *,
    ncm: str,
    uf_origem: str,
    uf_destino: str,
    tipo_cliente: str,
    tipo_operacao: str = "domestica",
) -> Optional[RegraFiscal]:
    ncm = normalize_ncm(ncm)
    uf_o = uf_origem.upper()
    uf_d = uf_destino.upper()
    tipo = tipo_cliente_fiscal(tipo_cliente) if tipo_cliente in ("PF", "PJ") else "ANY"
    top = (tipo_operacao or "domestica").lower()

    for t in (tipo, "ANY"):
        q = (
            select(RegraFiscal)
            .where(
                RegraFiscal.ativo.is_(True),
                RegraFiscal.ncm == ncm,
                RegraFiscal.uf_origem == uf_o,
                RegraFiscal.tipo_cliente == t,
                RegraFiscal.tipo_operacao == top,
            )
            .order_by(RegraFiscal.ordem, RegraFiscal.id)
        )
        result = await db.execute(q)
        regra = escolher_melhor_regra(result.scalars().all(), uf_o, uf_d)
        if regra:
            return regra
    return None


def _calcular_icms_importacao(
    regra: RegraFiscal,
    valor_operacao: Decimal,
) -> Dict[str, Any]:
    """Referência ICMS importação — Simples Nacional (exceção ao DAS unificado)."""
    aliq = float(regra.aliquota_icms_importacao or 0)
    base = float(valor_operacao)
    return {
        "aplicavel": True,
        "icms_origem": int(regra.icms_origem or 1),
        "aliquota_referencia": aliq,
        "base_calculo_referencia": base,
        "valor_referencia": round(base * aliq / 100, 2) if aliq else None,
        "observacao": (
            "ICMS importação no Simples — recolhimento via guia/DAS conforme contador. "
            "Não substitui SPED/EFD."
        ),
    }


def _calcular_difal(
    regra: RegraFiscal,
    valor_operacao: Decimal,
    uf_origem: str,
    uf_destino: str,
) -> Dict[str, Any]:
    """Estrutura prevista para DIFAL (EC 87/2015) — preenchimento na NF-e."""
    aliq_inter = float(regra.aliquota_icms_inter or 12)
    aliq_intra = float(regra.aliquota_icms_intra or 18)
    base = float(valor_operacao)
    return {
        "aplicavel": True,
        "uf_origem": uf_origem,
        "uf_destino": uf_destino,
        "base_calculo": base,
        "aliquota_interestadual": aliq_inter,
        "aliquota_interna_destino": aliq_intra,
        "observacao": "Campos DIFAL devem ser mapeados no payload do provedor NF-e",
    }


async def montar_contexto_tributario(
    db: AsyncSession,
    emitente: EmitenteFiscal,
    comprador: Comprador,
    itens_agregados: List[Dict[str, Any]],
    ncm_padrao: str = NCM_MUDAS_PADRAO,
    tipo_operacao_fiscal: str | None = None,
) -> ContextoTributario:
    uf_origem = emitente.uf.upper()
    uf_destino = (comprador.estado or uf_origem).upper()
    tipo = comprador.tipo
    top = inferir_tipo_operacao_fiscal(uf_destino, tipo_operacao_fiscal)
    if top == "exterior":
        uf_destino = "EX"

    regra = await buscar_regra(
        db,
        ncm=ncm_padrao,
        uf_origem=uf_origem,
        uf_destino=uf_destino,
        tipo_cliente=tipo,
        tipo_operacao=top,
    )
    if not regra:
        raise ValueError(
            f"Sem regra fiscal ({top}) para NCM {ncm_padrao} ({uf_origem} → {uf_destino}, {tipo}). "
            "Cadastre em regras_fiscais."
        )

    cfop_dest = uf_destino if top == "exterior" else (comprador.estado or uf_origem).upper()
    if regra.ajustar_cfop_por_uf:
        cfop = resolve_cfop(regra.cfop_base, uf_origem, cfop_dest)
    else:
        cfop = regra.cfop_base
    unidade = regra.unidade_comercial or "UN"
    natureza = regra.natureza_operacao or "Venda de mudas"

    linhas: List[LinhaFiscal] = []
    total = Decimal("0")
    for idx, item in enumerate(itens_agregados, start=1):
        qtd = Decimal(str(item["quantidade"]))
        vu = Decimal(str(item["valor_unitario"])).quantize(Decimal("0.0001"))
        vt = Decimal(str(item["valor_total"])).quantize(Decimal("0.01"))
        total += vt
        desc = item.get("descricao") or regra.descricao_produto or "Muda de planta"
        linhas.append(
            LinhaFiscal(
                descricao=desc,
                ncm=normalize_ncm(ncm_padrao),
                quantidade=qtd,
                valor_unitario=vu,
                valor_total=vt,
                cfop=cfop,
                csosn=regra.csosn,
                unidade=unidade,
                natureza_operacao=natureza,
            )
        )

    difal = None
    importacao = None
    uf_dest_real = (comprador.estado or uf_origem).upper()
    interestadual = uf_origem != uf_dest_real and top != "exterior"
    nao_contrib = consumidor_final_nao_contribuinte(tipo, comprador.inscricao_estadual)
    if interestadual and nao_contrib and regra.aplicar_difal:
        difal = _calcular_difal(regra, total, uf_origem, uf_dest_real)
    if top == "importacao" or (regra.tipo_operacao or "").lower() == "importacao":
        importacao = _calcular_icms_importacao(regra, total)

    return ContextoTributario(
        linhas=linhas,
        difal=difal,
        importacao=importacao,
        uf_origem=uf_origem,
        uf_destino=uf_dest_real,
        tipo_operacao=top,
        regra=regra,
    )


async def preview_regra_venda(
    db: AsyncSession,
    emitente: Optional[EmitenteFiscal],
    *,
    uf_destino: str,
    tipo_cliente: str = "PF",
    ncm: str = NCM_MUDAS_PADRAO,
    tipo_operacao: str = "domestica",
) -> Dict[str, Any]:
    uf_o = (emitente.uf if emitente else "GO").upper()
    top = inferir_tipo_operacao_fiscal(uf_destino, tipo_operacao)
    uf_d = "EX" if top == "exterior" else uf_destino.upper()
    regra = await buscar_regra(
        db,
        ncm=ncm,
        uf_origem=uf_o,
        uf_destino=uf_d,
        tipo_cliente=tipo_cliente,
        tipo_operacao=top,
    )
    if not regra:
        return {
            "encontrada": False,
            "uf_origem": uf_o,
            "uf_destino": uf_destino.upper(),
            "tipo_operacao": top,
            "operacao": label_operacao(uf_o, uf_destino.upper(), top),
            "cfop_resolvido": None,
            "regra": None,
            "mensagem": (
                f"Nenhuma regra ativa ({top}) para {uf_o} → {uf_destino.upper()} ({tipo_cliente}). "
                "Cadastre em Contabilidade."
            ),
        }
    cfop_dest = uf_d if top == "exterior" else uf_destino.upper()
    if regra.ajustar_cfop_por_uf:
        cfop = resolve_cfop(regra.cfop_base, uf_o, cfop_dest)
    else:
        cfop = regra.cfop_base

    trib_resumo = _resumo_tributario(regra, uf_o, uf_destino.upper(), tipo_cliente, top)

    return {
        "encontrada": True,
        "uf_origem": uf_o,
        "uf_destino": uf_destino.upper(),
        "tipo_operacao": top,
        "operacao": label_operacao(uf_o, uf_destino.upper(), top),
        "cfop_resolvido": cfop,
        "regra": regra,
        "mensagem": f"Regra «{regra.nome or regra.id}» — CFOP {cfop}, CSOSN {regra.csosn}",
        **trib_resumo,
    }


def _resumo_tributario(
    regra: RegraFiscal,
    uf_origem: str,
    uf_destino: str,
    tipo_cliente: str,
    tipo_operacao: str = "domestica",
) -> Dict[str, Any]:
    """Resumo legível de alíquotas / isenção / DIFAL / importação para UI."""
    top = (tipo_operacao or "domestica").lower()
    interestadual = uf_origem != uf_destino and top not in ("exterior", "importacao")
    out: Dict[str, Any] = {
        "isento_icms": bool(regra.isento_icms),
        "reducao_bc_icms_percent": float(regra.reducao_bc_icms_percent or 0) or None,
        "aplicar_difal": bool(regra.aplicar_difal),
        "aliquota_icms_inter": float(regra.aliquota_icms_inter) if regra.aliquota_icms_inter else None,
        "aliquota_icms_intra": float(regra.aliquota_icms_intra) if regra.aliquota_icms_intra else None,
        "icms_origem": int(regra.icms_origem or 0),
        "aliquota_icms_importacao": float(regra.aliquota_icms_importacao)
        if regra.aliquota_icms_importacao
        else None,
        "difal_aplicavel": False,
        "importacao_aplicavel": top == "importacao",
        "tributacao_resumo": "",
    }
    partes = []
    if top == "importacao":
        io = int(regra.icms_origem or 1)
        aliq = out["aliquota_icms_importacao"]
        partes.append(f"Origem estrangeira (icms_origem={io})")
        if aliq:
            partes.append(f"ICMS importação ref. {aliq:g}% (SN — guia/DAS)")
        else:
            partes.append("ICMS importação SN — alíquota ref. a definir pelo contador")
    elif regra.isento_icms:
        partes.append("ICMS isento (CSOSN na regra)")
    elif regra.reducao_bc_icms_percent:
        partes.append(f"Redução BC {float(regra.reducao_bc_icms_percent):g}%")
    else:
        partes.append("ICMS via CSOSN (Simples — DAS unificado)")

    if interestadual and regra.aplicar_difal:
        aliq_inter = float(regra.aliquota_icms_inter or 12)
        aliq_intra = float(regra.aliquota_icms_intra or 18)
        out["aliquota_icms_inter"] = aliq_inter
        out["aliquota_icms_intra"] = aliq_intra
        out["difal_aplicavel"] = True
        partes.append(f"DIFAL {aliq_inter}% inter → {aliq_intra}% intra destino")
    elif interestadual:
        partes.append("Interestadual sem DIFAL na regra")

    out["tributacao_resumo"] = " · ".join(partes)
    return out


def local_destino_operacao(uf_origem: str, uf_destino: str, tipo_operacao: str = "domestica") -> int:
    """1 interna, 2 interestadual, 3 exterior (MOC / Focus)."""
    if (tipo_operacao or "").lower() == "exterior" or (uf_destino or "").upper() in ("EX", "EXTERIOR"):
        return 3
    return 1 if uf_origem.upper() == uf_destino.upper() else 2
