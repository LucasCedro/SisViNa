from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.regra_fiscal import RegraFiscal
from app.services.validacao_regra_fiscal import validar_regra_fiscal


async def list_regras(
    db: AsyncSession,
    *,
    ativo: Optional[bool] = None,
    uf_origem: Optional[str] = None,
) -> List[RegraFiscal]:
    q = select(RegraFiscal).order_by(RegraFiscal.ordem, RegraFiscal.id)
    if ativo is not None:
        q = q.where(RegraFiscal.ativo.is_(ativo))
    if uf_origem:
        q = q.where(RegraFiscal.uf_origem == uf_origem.upper())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_regra(db: AsyncSession, regra_id: int) -> Optional[RegraFiscal]:
    return await db.get(RegraFiscal, regra_id)


async def create_regra(db: AsyncSession, data: dict) -> RegraFiscal:
    validar_regra_fiscal(data)
    regra = RegraFiscal(**data)
    db.add(regra)
    await db.commit()
    await db.refresh(regra)
    return regra


async def update_regra(db: AsyncSession, regra_id: int, data: dict) -> Optional[RegraFiscal]:
    regra = await get_regra(db, regra_id)
    if not regra:
        return None
    for k, v in data.items():
        setattr(regra, k, v)
    validar_regra_fiscal(
        {
            "isento_icms": regra.isento_icms,
            "reducao_bc_icms_percent": regra.reducao_bc_icms_percent,
            "fundamento_legal": regra.fundamento_legal,
            "tipo_operacao": regra.tipo_operacao,
            "icms_origem": regra.icms_origem,
            "aliquota_icms_importacao": regra.aliquota_icms_importacao,
        }
    )
    await db.commit()
    await db.refresh(regra)
    return regra


async def delete_regra(db: AsyncSession, regra_id: int) -> bool:
    regra = await get_regra(db, regra_id)
    if not regra:
        return False
    await db.delete(regra)
    await db.commit()
    return True
