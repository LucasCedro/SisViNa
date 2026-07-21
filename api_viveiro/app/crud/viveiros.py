"""CRUD de unidades viveiro."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.viveiro_modo import MODO_LABELS
from app.models.funcionario_viveiro import FuncionarioViveiro
from app.models.viveiros import Viveiro
from app.schemas.viveiros import ViveiroCreate, ViveiroOut


def viveiro_to_out(v: Viveiro) -> ViveiroOut:
    return ViveiroOut(
        id=v.id,
        nome=v.nome,
        slug=v.slug,
        modo_operacao=v.modo_operacao,
        modo_label=MODO_LABELS.get(v.modo_operacao, v.modo_operacao),
        ativo=bool(v.ativo),
        data_cadastro=v.data_cadastro,
    )


async def list_viveiros(
    db: AsyncSession, *, ativo: Optional[bool] = True, id_empresa: Optional[int] = None
) -> List[Viveiro]:
    stmt = select(Viveiro).order_by(Viveiro.id)
    if ativo is not None:
        stmt = stmt.where(Viveiro.ativo.is_(ativo))
    if id_empresa is not None:
        stmt = stmt.where(Viveiro.id_empresa == id_empresa)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_viveiro(
    db: AsyncSession, viveiro_id: int, id_empresa: Optional[int] = None
) -> Optional[Viveiro]:
    row = await db.get(Viveiro, viveiro_id)
    if row is None:
        return None
    if id_empresa is not None and row.id_empresa != id_empresa:
        return None
    return row


async def get_viveiro_by_slug(
    db: AsyncSession, slug: str, id_empresa: Optional[int] = None
) -> Optional[Viveiro]:
    stmt = select(Viveiro).where(Viveiro.slug == slug)
    if id_empresa is not None:
        stmt = stmt.where(Viveiro.id_empresa == id_empresa)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_viveiro(
    db: AsyncSession, payload: ViveiroCreate, id_empresa: Optional[int] = None
) -> Viveiro:
    row = Viveiro(
        nome=payload.nome.strip(),
        slug=payload.slug.strip().lower(),
        modo_operacao=payload.modo_operacao,
        id_empresa=id_empresa,
        ativo=True,
    )
    db.add(row)
    await db.flush()
    return row


async def link_funcionario_viveiro(db: AsyncSession, id_funcionario: int, id_viveiro: int) -> None:
    exists = await db.execute(
        select(FuncionarioViveiro).where(
            FuncionarioViveiro.id_funcionario == id_funcionario,
            FuncionarioViveiro.id_viveiro == id_viveiro,
        )
    )
    if exists.scalar_one_or_none() is None:
        db.add(FuncionarioViveiro(id_funcionario=id_funcionario, id_viveiro=id_viveiro))
