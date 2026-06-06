"""Controle de ambiente NF-e — homologação por padrão."""

from __future__ import annotations

from app.config import settings
from app.models.emitente_fiscal import EmitenteFiscal


def producao_permitida() -> bool:
    return bool(getattr(settings, "NFE_ALLOW_PRODUCAO", False))


def validar_ambiente_emissao(emitente: EmitenteFiscal) -> None:
    amb = (emitente.ambiente or "homologacao").lower()
    if amb == "producao" and not producao_permitida():
        raise ValueError(
            "Emissão em PRODUÇÃO bloqueada neste ambiente. "
            "Mantenha emitente.ambiente=homologacao até liberação explícita (NFE_ALLOW_PRODUCAO)."
        )


def info_ambiente(emitente: EmitenteFiscal | None) -> dict:
    token = (settings.FOCUS_NFE_TOKEN or "").strip()
    amb = (emitente.ambiente if emitente else "homologacao") or "homologacao"
    return {
        "ambiente_emitente": amb,
        "producao_permitida_sistema": producao_permitida(),
        "focus_token_configurado": bool(token),
        "modo_mock": not bool(token),
        "mensagem": (
            "HOMOLOGAÇÃO — notas sem valor fiscal comercial"
            if amb != "producao"
            else ("PRODUÇÃO (liberada)" if producao_permitida() else "PRODUÇÃO BLOQUEADA")
        ),
    }
