"""Validações suaves (avisos) — não bloqueiam o fluxo operacional."""

from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.referencia_embrapa_viveiro import (
    RUSTIFICACAO_DIAS_MINIMO,
)
from app.crud.referencia_viveiro import get_regra_numerica
from app.models.plantas import Planta
from app.models.referencia_viveiro import EspecieFichaEmbrapa


def _dias_desde(data_ref: Optional[date]) -> Optional[int]:
    if not data_ref:
        return None
    return (date.today() - data_ref).days


async def dias_minimos_rustificacao(
    db: AsyncSession, id_especie: Optional[int] = None
) -> int:
    if id_especie:
        ficha = await db.get(EspecieFichaEmbrapa, id_especie)
        if ficha and ficha.dias_rustificacao_minimo:
            return int(ficha.dias_rustificacao_minimo)
    minimo = await get_regra_numerica(db, "rustificacao_dias_minimo")
    return int(minimo if minimo is not None else RUSTIFICACAO_DIAS_MINIMO)


async def avisos_liberar_venda(
    db: AsyncSession, planta: Planta
) -> List[str]:
    """Avisos ao marcar apta_venda (especialmente após rustificação)."""
    avisos: List[str] = []
    if planta.estagio_producao != "em_rustificacao":
        return avisos

    min_dias = await dias_minimos_rustificacao(db, planta.id_especie)
    ref = planta.data_inicio_estagio_atual or planta.data_plantio
    dias = _dias_desde(ref)
    if dias is not None and dias < min_dias:
        avisos.append(
            f"Rustificação com {dias} dia(s); recomendado mínimo {min_dias} dia(s) "
            "antes de liberar para venda/campo."
        )

    if planta.altura_atual is not None:
        ficha = await db.get(EspecieFichaEmbrapa, planta.id_especie)
        h_min = float(ficha.altura_campo_cm_min) if ficha and ficha.altura_campo_cm_min else await get_regra_numerica(db, "altura_campo_cerrado_cm_min")
        h_max = float(ficha.altura_campo_cm_max) if ficha and ficha.altura_campo_cm_max else await get_regra_numerica(db, "altura_campo_cerrado_cm_max")
        altura = float(planta.altura_atual)
        if h_min and altura < h_min:
            avisos.append(
                f"Altura atual {altura:.0f} cm abaixo da faixa típica para campo "
                f"({h_min:.0f}–{h_max or '?'} cm)."
            )
    return avisos


async def avisos_transferir_rustificacao(
    db: AsyncSession, planta: Planta
) -> List[str]:
    avisos: List[str] = []
    if planta.altura_atual is not None:
        h_min = await get_regra_numerica(db, "altura_campo_cerrado_cm_min")
        if h_min and float(planta.altura_atual) < float(h_min):
            avisos.append(
                "Muda ainda abaixo da altura típica para campo; rustificação pode "
                "ser antecipada conforme manejo do viveiro."
            )
    return avisos
