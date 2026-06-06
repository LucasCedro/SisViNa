"""Integração NF-e (modelo 55) — adapter Focus NFe + modo mock sem token."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings
from app.models.compradores import Comprador
from app.models.emitente_fiscal import EmitenteFiscal
from app.services.tributacao_nfe import ContextoTributario, LinhaFiscal, local_destino_operacao
from app.utils.fiscal import only_digits

logger = logging.getLogger(__name__)


class NfeProvedorError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


from app.services.nfe_ambiente import producao_permitida


def _base_url(ambiente: str) -> str:
    """URL Focus — se produção não liberada no servidor, força homologação sempre."""
    if not producao_permitida():
        return settings.FOCUS_NFE_URL_HOMOLOGACAO.rstrip("/")
    if ambiente == "producao":
        return settings.FOCUS_NFE_URL_PRODUCAO.rstrip("/")
    return settings.FOCUS_NFE_URL_HOMOLOGACAO.rstrip("/")


def _mensagem_erro_provedor(body: Any, status_code: int) -> str:
    """Extrai texto útil da resposta Focus (JSON ou corpo bruto)."""
    if isinstance(body, dict):
        for key in ("mensagem", "message", "mensagem_sefaz", "erro", "erros"):
            val = body.get(key)
            if val:
                if isinstance(val, list):
                    return "; ".join(str(x) for x in val)
                return str(val).strip()
        raw = body.get("raw")
        if raw:
            txt = str(raw).strip()
            if "access denied" in txt.lower():
                return (
                    "Token Focus NFe inválido ou sem permissão (HTTP Basic: Access denied). "
                    "Confira FOCUS_NFE_TOKEN no .env — use o token de homologação se ambiente=homologacao."
                )
            return txt
    if isinstance(body, str) and body.strip():
        return body.strip()
    return f"Rejeição do provedor NF-e (HTTP {status_code})"


def _indicador_ie(comprador: Comprador) -> str:
    ie = only_digits(comprador.inscricao_estadual or "")
    if comprador.indicador_ie in ("1", "2", "9"):
        return comprador.indicador_ie
    if len(ie) > 0:
        return "1"
    return "9"


def montar_payload_focus(
    emitente: EmitenteFiscal,
    comprador: Comprador,
    ctx: ContextoTributario,
    *,
    numero: int,
    serie: int,
    ref_externa: str,
) -> Dict[str, Any]:
    """Mapeia dados internos → JSON Focus NFe (CRT=1 → CSOSN em icms_situacao_tributaria)."""
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    if len(now) > 22:
        now = now[:-2] + ":" + now[-2:]

    doc_dest = only_digits(comprador.cpf_cnpj or "")
    regra = ctx.regra
    ld = regra.local_destino or local_destino_operacao(
        ctx.uf_origem, ctx.uf_destino, getattr(ctx, "tipo_operacao", "domestica")
    )
    inf_compl_parts = []
    if regra.fundamento_legal:
        txt = regra.fundamento_legal.strip()
        if regra.isento_icms:
            inf_compl_parts.append(f"Isenção de ICMS — {txt}")
        else:
            inf_compl_parts.append(txt)
    if regra.informacoes_complementares:
        inf_compl_parts.append(regra.informacoes_complementares.strip())
    if ctx.difal:
        inf_compl_parts.append(
            f"DIFAL EC 87/2015 — ver parametrização do contador (UF destino {ctx.uf_destino})."
        )
    if ctx.importacao:
        imp = ctx.importacao
        io = imp.get("icms_origem", 1)
        aliq = imp.get("aliquota_referencia")
        txt_imp = f"Origem mercadoria estrangeira (icms_origem={io})"
        if aliq:
            txt_imp += f" — ICMS importação SN ref. {aliq:g}%"
        inf_compl_parts.append(txt_imp)

    payload: Dict[str, Any] = {
        "natureza_operacao": ctx.linhas[0].natureza_operacao if ctx.linhas else "Venda de mudas",
        "data_emissao": now,
        "tipo_documento": 1,
        "finalidade_emissao": 1,
        "local_destino": ld,
        "consumidor_final": 1 if comprador.tipo == "PF" or _indicador_ie(comprador) == "9" else 0,
        "presenca_comprador": 9,
        "modalidade_frete": 9,
        "cnpj_emitente": only_digits(emitente.cnpj),
        "nome_emitente": emitente.razao_social,
        "nome_fantasia_emitente": emitente.nome_fantasia or emitente.razao_social,
        "inscricao_estadual_emitente": emitente.inscricao_estadual,
        "regime_tributario_emitente": emitente.crt,
        "logradouro_emitente": emitente.logradouro,
        "numero_emitente": emitente.numero,
        "bairro_emitente": emitente.bairro,
        "municipio_emitente": emitente.municipio,
        "uf_emitente": emitente.uf,
        "cep_emitente": only_digits(emitente.cep),
        "telefone_emitente": only_digits(emitente.telefone or "") or None,
        "email_emitente": emitente.email,
        "nome_destinatario": comprador.nome,
        "inscricao_estadual_destinatario": comprador.inscricao_estadual or "",
        "indicador_inscricao_estadual_destinatario": int(_indicador_ie(comprador)),
        "logradouro_destinatario": comprador.endereco,
        "numero_destinatario": comprador.numero,
        "bairro_destinatario": comprador.bairro,
        "municipio_destinatario": comprador.cidade,
        "uf_destinatario": comprador.estado,
        "cep_destinatario": only_digits(comprador.cep or ""),
        "codigo_municipio_destinatario": only_digits(comprador.codigo_municipio_ibge or ""),
        "numero": numero,
        "serie": serie,
        "items": [],
    }

    if comprador.tipo == "PF":
        payload["cpf_destinatario"] = doc_dest
    else:
        payload["cnpj_destinatario"] = doc_dest

    total = Decimal("0")
    for idx, linha in enumerate(ctx.linhas, start=1):
        total += linha.valor_total
        item: Dict[str, Any] = {
            "numero_item": idx,
            "codigo_produto": f"MUDA-{linha.ncm}",
            "descricao": linha.descricao[:120],
            "cfop": int(linha.cfop),
            "unidade_comercial": linha.unidade,
            "quantidade_comercial": float(linha.quantidade),
            "valor_unitario_comercial": float(linha.valor_unitario),
            "valor_bruto": float(linha.valor_total),
            "codigo_ncm": linha.ncm,
            # Simples Nacional: CSOSN (nunca CST)
            "icms_situacao_tributaria": linha.csosn,
            "icms_origem": int(regra.icms_origem or 0),
        }
        if regra.reducao_bc_icms_percent is not None:
            item["icms_percentual_reducao_bc"] = float(regra.reducao_bc_icms_percent)
        if regra.cbenef:
            item["codigo_beneficio_fiscal"] = regra.cbenef
        if regra.pis_situacao_tributaria:
            item["pis_situacao_tributaria"] = regra.pis_situacao_tributaria
        if regra.cofins_situacao_tributaria:
            item["cofins_situacao_tributaria"] = regra.cofins_situacao_tributaria
        payload["items"].append(item)

    payload["valor_produtos"] = float(total)
    payload["valor_total"] = float(total)

    if ctx.difal:
        payload["_difal_snapshot"] = ctx.difal
    if ctx.importacao:
        payload["_importacao_snapshot"] = ctx.importacao

    if inf_compl_parts:
        payload["informacoes_adicionais_contribuinte"] = " | ".join(inf_compl_parts)[:5000]

    payload["_regra_fiscal_id"] = regra.id
    payload["_ref_externa"] = ref_externa
    return payload


async def enviar_nfe(
    emitente: EmitenteFiscal,
    ref_externa: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    token = (settings.FOCUS_NFE_TOKEN or "").strip()
    if not token:
        return _mock_resposta(ref_externa, payload, emitente.ambiente)

    url = f"{_base_url(emitente.ambiente)}/v2/nfe"
    params = {"ref": ref_externa}
    headers = {"Content-Type": "application/json"}

    clean_payload = {k: v for k, v in payload.items() if not str(k).startswith("_")}

    try:
        async with httpx.AsyncClient(timeout=settings.FOCUS_NFE_TIMEOUT) as client:
            response = await client.post(
                url,
                params=params,
                json=clean_payload,
                auth=(token, ""),
                headers=headers,
            )
    except httpx.TimeoutException as exc:
        raise NfeProvedorError("Timeout ao comunicar com provedor NF-e") from exc
    except httpx.HTTPError as exc:
        raise NfeProvedorError(f"Erro de rede NF-e: {exc}") from exc

    try:
        body = response.json()
    except ValueError:
        body = {"raw": response.text}

    if response.status_code >= 400:
        raise NfeProvedorError(
            _mensagem_erro_provedor(body, response.status_code),
            status_code=response.status_code,
            body=body,
        )
    return body


async def consultar_nfe(
    emitente: EmitenteFiscal,
    ref_externa: str,
) -> Dict[str, Any]:
    token = (settings.FOCUS_NFE_TOKEN or "").strip()
    if not token:
        return {
            "status": "simulacao",
            "status_sefaz": "100",
            "mensagem_sefaz": "SIMULAÇÃO LOCAL — configure FOCUS_NFE_TOKEN",
            "ref": ref_externa,
            "mock": True,
        }

    url = f"{_base_url(emitente.ambiente)}/v2/nfe/{ref_externa}"
    try:
        async with httpx.AsyncClient(timeout=settings.FOCUS_NFE_TIMEOUT) as client:
            response = await client.get(url, auth=(token, ""))
    except httpx.TimeoutException as exc:
        raise NfeProvedorError("Timeout na consulta NF-e") from exc
    except httpx.HTTPError as exc:
        raise NfeProvedorError(f"Erro de rede na consulta NF-e: {exc}") from exc

    try:
        body = response.json()
    except ValueError:
        body = {"raw": response.text}

    if response.status_code >= 400:
        raise NfeProvedorError(
            _mensagem_erro_provedor(body, response.status_code),
            status_code=response.status_code,
            body=body,
        )
    return body


def interpretar_resposta_emissao(body: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza resposta Focus → campos internos."""
    status = (body.get("status") or "processando").lower()
    cstat = body.get("status_sefaz") or body.get("codigo_status_sefaz")
    if cstat:
        cstat = str(cstat)

    if cstat == "100" or status in ("autorizado", "autorizada"):
        status = "autorizada"
    elif status == "simulacao":
        status = "simulacao"
    elif status in ("processando", "processando_autorizacao"):
        status = "processando"
    elif status in ("erro_autorizacao", "rejeitada", "denegada"):
        status = "rejeitada"
    elif status in ("cancelado", "cancelada"):
        status = "cancelada"

    return {
        "status": status,
        "cstat": cstat,
        "xmotivo": body.get("mensagem_sefaz") or body.get("mensagem"),
        "chave_acesso": body.get("chave_nfe") or body.get("chave_acesso"),
        "recibo": body.get("recibo") or body.get("numero_recibo"),
        "url_xml": body.get("caminho_xml_nota_fiscal") or body.get("url_xml"),
        "url_danfe": body.get("caminho_danfe") or body.get("url_danfe"),
        "numero": body.get("numero"),
        "serie": body.get("serie"),
    }


def _mock_resposta(ref: str, payload: Dict[str, Any], ambiente: str) -> Dict[str, Any]:
    """Homologação local sem certificado/token — útil para demo."""
    numero = payload.get("numero", 1)
    serie = payload.get("serie", 1)
    chave = "3526050000000000000055001000000001" + str(numero).zfill(9) + "000000000"
    logger.info("NF-e mock (sem FOCUS_NFE_TOKEN) ref=%s ambiente=%s", ref, ambiente)
    return {
        "status": "simulacao",
        "status_sefaz": "100",
        "mensagem_sefaz": "SIMULAÇÃO LOCAL — configure FOCUS_NFE_TOKEN e reinicie a API (sem validade fiscal)",
        "ref": ref,
        "chave_nfe": chave[:44],
        "numero": numero,
        "serie": serie,
        "caminho_xml_nota_fiscal": None,
        "caminho_danfe": None,
        "mock": True,
    }
