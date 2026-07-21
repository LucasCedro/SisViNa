from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financeiro_premissa import FinanceiroPremissa
from app.models.insumos import Insumo
from app.schemas.premissas_financeiras import PremissaCreate, PremissaUpdate
from app.services.custeio import preco_medio_insumo, redistribuir_cif_parque

_TIPOS_CIF_PARQUE = frozenset({"mensal_rateio", "pessoas_x_salario_rateio"})


def _premissa_tipo_cif_parque(prem: FinanceiroPremissa) -> bool:
    if (prem.natureza or "").upper() != "CUSTO":
        return False
    return (prem.tipo_calculo or "").lower() in _TIPOS_CIF_PARQUE


async def _recalcular_cmv_se_premissa_cif(db: AsyncSession, prem: FinanceiroPremissa) -> None:
    if _premissa_tipo_cif_parque(prem):
        await redistribuir_cif_parque(db, commit=False)


def _para_out(p: FinanceiroPremissa, insumo: Optional[Insumo] = None) -> dict:
    return {
        "id": p.id,
        "chave": p.chave,
        "nome": p.nome,
        "descricao": p.descricao,
        "natureza": p.natureza,
        "tipo_calculo": p.tipo_calculo,
        "unidade": p.unidade,
        "valor": float(p.valor or 0),
        "quantidade": float(p.quantidade) if p.quantidade is not None else None,
        "id_insumo": p.id_insumo,
        "ordem": p.ordem or 0,
        "ativo": bool(p.ativo),
        "insumo_nome": insumo.nome if insumo else None,
        "preco_medio_insumo": preco_medio_insumo(insumo) if insumo else None,
    }


async def list_premissas(
    db: AsyncSession,
    natureza: Optional[str] = None,
    apenas_ativas: bool = False,
) -> List[dict]:
    q = select(FinanceiroPremissa).order_by(FinanceiroPremissa.ordem, FinanceiroPremissa.id)
    if natureza:
        q = q.where(FinanceiroPremissa.natureza == natureza.upper())
    if apenas_ativas:
        q = q.where(FinanceiroPremissa.ativo.is_(True))
    rows = (await db.execute(q)).scalars().all()
    out = []
    for p in rows:
        insumo = await db.get(Insumo, p.id_insumo) if p.id_insumo else None
        out.append(_para_out(p, insumo))
    return out


async def get_premissa(db: AsyncSession, premissa_id: int) -> Optional[dict]:
    p = await db.get(FinanceiroPremissa, premissa_id)
    if not p:
        return None
    insumo = await db.get(Insumo, p.id_insumo) if p.id_insumo else None
    return _para_out(p, insumo)


async def create_premissa(db: AsyncSession, payload: PremissaCreate) -> dict:
    existente = (
        await db.execute(select(FinanceiroPremissa).where(FinanceiroPremissa.chave == payload.chave))
    ).scalars().first()
    if existente:
        raise ValueError(f"Já existe premissa com chave '{payload.chave}'")
    db_p = FinanceiroPremissa(**payload.dict())
    db.add(db_p)
    await db.flush()
    await _recalcular_cmv_se_premissa_cif(db, db_p)
    await db.commit()
    await db.refresh(db_p)
    insumo = await db.get(Insumo, db_p.id_insumo) if db_p.id_insumo else None
    return _para_out(db_p, insumo)


async def update_premissa(
    db: AsyncSession, premissa_id: int, payload: PremissaUpdate
) -> Optional[dict]:
    db_p = await db.get(FinanceiroPremissa, premissa_id)
    if not db_p:
        return None
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_p, field, value)
    await db.flush()
    await _recalcular_cmv_se_premissa_cif(db, db_p)
    await db.commit()
    await db.refresh(db_p)
    insumo = await db.get(Insumo, db_p.id_insumo) if db_p.id_insumo else None
    return _para_out(db_p, insumo)


async def delete_premissa(db: AsyncSession, premissa_id: int) -> bool:
    db_p = await db.get(FinanceiroPremissa, premissa_id)
    if not db_p:
        return False
    era_cif = _premissa_tipo_cif_parque(db_p)
    await db.delete(db_p)
    await db.flush()
    if era_cif:
        await redistribuir_cif_parque(db, commit=False)
    await db.commit()
    return True
