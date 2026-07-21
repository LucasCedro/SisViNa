"""Seed mínimo de tenant para testes (empresa + viveiro padrão)."""

from __future__ import annotations

from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.viveiro_modo import MODO_NATIVO
from app.models.empresas import Empresa
from app.models.funcionario_viveiro import FuncionarioViveiro
from app.models.funcionarios import Funcionario
from app.models.viveiros import Viveiro

DEFAULT_EMPRESA_ID = 1
DEFAULT_VIVEIRO_ID = 1


async def ensure_tenant_base(db: AsyncSession) -> tuple[Empresa, Viveiro]:
    empresa = await db.get(Empresa, DEFAULT_EMPRESA_ID)
    if empresa is None:
        empresa = Empresa(
            id=DEFAULT_EMPRESA_ID,
            razao_social="Empresa Teste",
            nome_fantasia="Teste",
            slug="empresa-teste",
            ativo=True,
        )
        db.add(empresa)
        await db.flush()

    viveiro = await db.get(Viveiro, DEFAULT_VIVEIRO_ID)
    if viveiro is None:
        viveiro = Viveiro(
            id=DEFAULT_VIVEIRO_ID,
            nome="Viveiro Teste",
            slug="viveiro-teste",
            modo_operacao=MODO_NATIVO,
            id_empresa=DEFAULT_EMPRESA_ID,
            ativo=True,
        )
        db.add(viveiro)
        await db.flush()

    await _sync_serial_sequences(db, ("empresas", "viveiros"))
    return empresa, viveiro


async def _sync_serial_sequences(db: AsyncSession, tables: tuple[str, ...]) -> None:
    """Evita colisão de PK ao inserir IDs explícitos antes de inserts auto-increment."""
    from sqlalchemy import text

    for table in tables:
        await db.execute(
            text(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table}', 'id'),
                    COALESCE((SELECT MAX(id) FROM {table}), 1)
                )
                """
            )
        )


async def link_funcionario_viveiro(
    db: AsyncSession, funcionario_id: int, viveiro_id: int = DEFAULT_VIVEIRO_ID
) -> None:
    from sqlalchemy import select

    exists = (
        await db.execute(
            select(FuncionarioViveiro).where(
                FuncionarioViveiro.id_funcionario == funcionario_id,
                FuncionarioViveiro.id_viveiro == viveiro_id,
            )
        )
    ).scalars().first()
    if exists is None:
        db.add(FuncionarioViveiro(id_funcionario=funcionario_id, id_viveiro=viveiro_id))
        await db.flush()
