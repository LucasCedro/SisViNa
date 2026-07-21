from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lancamentos_financeiros import LancamentoFinanceiro
from app.schemas.lancamentos_financeiros import (
    LancamentoFinanceiroCreate,
    LancamentoFinanceiroUpdate,
)


async def list_lancamentos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 500,
    tipo: Optional[str] = None,
    id_empresa: Optional[int] = None,
) -> List[LancamentoFinanceiro]:
    q = select(LancamentoFinanceiro).order_by(LancamentoFinanceiro.data_lancamento.desc())
    if id_empresa is not None:
        q = q.where(LancamentoFinanceiro.id_empresa == id_empresa)
    if tipo:
        q = q.where(LancamentoFinanceiro.tipo == tipo)
    q = q.offset(skip).limit(limit)
    return (await db.execute(q)).scalars().all()


async def get_lancamento(
    db: AsyncSession, lancamento_id: int, id_empresa: Optional[int] = None
) -> Optional[LancamentoFinanceiro]:
    q = select(LancamentoFinanceiro).where(LancamentoFinanceiro.id == lancamento_id)
    if id_empresa is not None:
        q = q.where(LancamentoFinanceiro.id_empresa == id_empresa)
    return (await db.execute(q)).scalars().first()


async def create_lancamento(
    db: AsyncSession,
    dados: LancamentoFinanceiroCreate,
    id_funcionario: int,
    id_empresa: Optional[int] = None,
) -> LancamentoFinanceiro:
    payload = dados.dict()
    if id_empresa is not None:
        payload["id_empresa"] = id_empresa
    obj = LancamentoFinanceiro(**payload, id_funcionario=id_funcionario)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_lancamento(
    db: AsyncSession, lancamento_id: int, dados: LancamentoFinanceiroUpdate
) -> Optional[LancamentoFinanceiro]:
    obj = await get_lancamento(db, lancamento_id)
    if not obj:
        return None
    for k, v in dados.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_lancamento(db: AsyncSession, lancamento_id: int) -> Optional[LancamentoFinanceiro]:
    obj = await get_lancamento(db, lancamento_id)
    if not obj:
        return None
    await db.delete(obj)
    await db.commit()
    return obj
