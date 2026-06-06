"""Validações de regras fiscais cadastradas pelo contador."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional


def validar_fundamento_regra(data: Mapping[str, Any]) -> None:
    """Isenção ou redução de BC exigem fundamento legal (infCpl na NF-e)."""
    isento = bool(data.get("isento_icms"))
    reducao = data.get("reducao_bc_icms_percent")
    fund = (data.get("fundamento_legal") or "").strip()
    if isento and not fund:
        raise ValueError(
            "Isenção de ICMS exige Fundamento legal — o texto aparece nas informações complementares da NF-e."
        )
    if reducao is not None and float(reducao) > 0 and not fund:
        raise ValueError(
            "Redução de BC ICMS exige Fundamento legal nas informações complementares da NF-e."
        )


def validar_cenario_importacao(data: Mapping[str, Any]) -> None:
    """Importação SN — origem estrangeira + parâmetros mínimos."""
    top = (data.get("tipo_operacao") or "domestica").lower()
    if top != "importacao":
        return
    io = int(data.get("icms_origem") or 0)
    if io < 1:
        raise ValueError(
            "Regra de importação exige icms_origem >= 1 (1=direta, 2=adquirida no mercado interno, …)."
        )
    fund = (data.get("fundamento_legal") or "").strip()
    if not fund:
        raise ValueError(
            "Importação SN exige Fundamento legal — ICMS de importação é exceção ao DAS unificado."
        )


def validar_regra_fiscal(data: Mapping[str, Any]) -> None:
    validar_fundamento_regra(data)
    validar_cenario_importacao(data)


def merged_regra_dict(regra: Any, patch: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Estado completo da regra após update parcial."""
    keys = (
        "isento_icms",
        "reducao_bc_icms_percent",
        "fundamento_legal",
        "tipo_operacao",
        "icms_origem",
        "aliquota_icms_importacao",
    )
    out = {k: getattr(regra, k, None) for k in keys}
    if patch:
        out.update({k: v for k, v in patch.items() if k in keys or k in patch})
    return out
