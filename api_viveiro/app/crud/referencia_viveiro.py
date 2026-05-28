from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.referencia_embrapa_viveiro import REGRAS_GLOBAIS_CHAVES, FONTE_SISTEMA
from app.models.referencia_viveiro import EspecieFichaEmbrapa, ViveiroRegraGlobal


async def get_regra_numerica(db: AsyncSession, chave: str) -> Optional[float]:
    row = await db.get(ViveiroRegraGlobal, chave)
    if row and row.valor_numerico is not None and row.ativo:
        return float(row.valor_numerico)
    fallback = REGRAS_GLOBAIS_CHAVES.get(chave)
    return float(fallback) if fallback is not None else None


async def listar_regras_globais(db: AsyncSession) -> List[Dict[str, Any]]:
    rows = (
        await db.execute(
            select(ViveiroRegraGlobal)
            .where(ViveiroRegraGlobal.ativo == True)
            .order_by(ViveiroRegraGlobal.chave)
        )
    ).scalars().all()
    return [
        {
            "chave": r.chave,
            "valor_numerico": float(r.valor_numerico) if r.valor_numerico is not None else None,
            "valor_texto": r.valor_texto,
            "descricao": r.descricao,
            "fonte": r.fonte,
        }
        for r in rows
    ]


async def get_ficha_especie(
    db: AsyncSession, id_especie: int
) -> Optional[Dict[str, Any]]:
    ficha = await db.get(EspecieFichaEmbrapa, id_especie)
    if not ficha:
        return None
    return _ficha_para_dict(ficha)


def _ficha_para_dict(ficha: EspecieFichaEmbrapa) -> Dict[str, Any]:
    return {
        "id_especie": ficha.id_especie,
        "nome_cientifico_ref": ficha.nome_cientifico_ref,
        "fitofisionomia": ficha.fitofisionomia,
        "mes_coleta_inicio": ficha.mes_coleta_inicio,
        "mes_coleta_fim": ficha.mes_coleta_fim,
        "armazenamento_tipo": ficha.armazenamento_tipo,
        "armazenamento_obs": ficha.armazenamento_obs,
        "profundidade_semeadura_cm_min": float(ficha.profundidade_semeadura_cm_min)
        if ficha.profundidade_semeadura_cm_min is not None
        else None,
        "profundidade_semeadura_cm_max": float(ficha.profundidade_semeadura_cm_max)
        if ficha.profundidade_semeadura_cm_max is not None
        else None,
        "dias_inicio_germinacao": ficha.dias_inicio_germinacao,
        "pct_germinacao_tipico": float(ficha.pct_germinacao_tipico)
        if ficha.pct_germinacao_tipico is not None
        else None,
        "substrato_tipo": ficha.substrato_tipo,
        "conduz_pleno_sol": ficha.conduz_pleno_sol,
        "meses_permanencia_viveiro": ficha.meses_permanencia_viveiro,
        "meses_permanencia_viveiro_max": ficha.meses_permanencia_viveiro_max,
        "dias_rustificacao_minimo": ficha.dias_rustificacao_minimo,
        "altura_campo_cm_min": float(ficha.altura_campo_cm_min)
        if ficha.altura_campo_cm_min is not None
        else None,
        "altura_campo_cm_max": float(ficha.altura_campo_cm_max)
        if ficha.altura_campo_cm_max is not None
        else None,
        "adubacao_obs": ficha.adubacao_obs,
        "observacoes_gerais": ficha.observacoes_gerais,
        "fonte": ficha.fonte or FONTE_SISTEMA,
    }
