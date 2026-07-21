"""Agregações do cockpit Admin."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.security.rbac import ALL_PERMISSIONS, ROLE_PERMISSIONS, VALID_ROLE_IDS

ROLE_LABELS = {
    "admin": "Administrador",
    "gestor": "Gestor do Viveiro",
    "campo": "Operação de Campo",
    "financeiro": "Financeiro",
    "consulta": "Consulta",
    "rh": "Recursos Humanos",
}

from app.constants.viveiro_modo import MODO_FLORESTAL, MODO_LABELS
from app.models.especies import Especie
from app.models.funcionarios import Funcionario
from app.models.plantas import Planta
from app.models.vendas import Venda
from app.models.viveiros import Viveiro
from app.models.funcionario_viveiro import FuncionarioViveiro
from app.models.lotes_producao import LoteProducao
from app.constants.florestal_estagios import ESTAGIOS_ATIVOS


async def _scalar_count(db: AsyncSession, stmt) -> int:
    result = await db.execute(stmt)
    return int(result.scalar_one() or 0)


async def get_overview(db: AsyncSession) -> dict[str, Any]:
    total = await _scalar_count(db, select(func.count()).select_from(Funcionario))
    ativos = await _scalar_count(
        db, select(func.count()).select_from(Funcionario).where(Funcionario.ativo.is_(True))
    )
    sem_perfis = await _scalar_count(
        db,
        select(func.count())
        .select_from(Funcionario)
        .where(text("(perfis IS NULL OR perfis::text = '[]')")),
    )

    por_perfil: dict[str, int] = {role: 0 for role in VALID_ROLE_IDS}
    rows = await db.execute(select(Funcionario.perfis).where(Funcionario.ativo.is_(True)))
    for (perfis,) in rows.all():
        lista = perfis if isinstance(perfis, list) else []
        for p in lista:
            if p in por_perfil:
                por_perfil[p] += 1

    alembic_rev: str | None = None
    try:
        rev_row = await db.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
        alembic_rev = rev_row.scalar_one_or_none()
    except Exception:
        alembic_rev = None

    viveiros_rows = (await db.execute(select(Viveiro).order_by(Viveiro.id))).scalars().all()
    viveiros_resumo = []
    for v in viveiros_rows:
        fn = await db.scalar(
            select(func.count())
            .select_from(FuncionarioViveiro)
            .where(FuncionarioViveiro.id_viveiro == v.id)
        )
        lotes = 0
        if v.modo_operacao == MODO_FLORESTAL:
            lotes = await db.scalar(
                select(func.count())
                .select_from(LoteProducao)
                .where(
                    LoteProducao.id_viveiro == v.id,
                    LoteProducao.estagio.in_(tuple(ESTAGIOS_ATIVOS)),
                )
            )
        viveiros_resumo.append(
            {
                "id": v.id,
                "nome": v.nome,
                "slug": v.slug,
                "modo_operacao": v.modo_operacao,
                "modo_label": MODO_LABELS.get(v.modo_operacao, v.modo_operacao),
                "ativo": bool(v.ativo),
                "funcionarios_vinculados": int(fn or 0),
                "lotes_producao_ativos": int(lotes or 0),
            }
        )

    return {
        "funcionarios_total": total,
        "funcionarios_ativos": ativos,
        "funcionarios_inativos": total - ativos,
        "funcionarios_sem_perfis": sem_perfis,
        "plantas_total": await _scalar_count(db, select(func.count()).select_from(Planta)),
        "vendas_total": await _scalar_count(db, select(func.count()).select_from(Venda)),
        "especies_total": await _scalar_count(db, select(func.count()).select_from(Especie)),
        "viveiros_total": len(viveiros_rows),
        "viveiros_florestal": sum(1 for v in viveiros_rows if v.modo_operacao == MODO_FLORESTAL),
        "permissoes_catalogo": len(ALL_PERMISSIONS),
        "perfis_rbac": len(ROLE_PERMISSIONS),
        "alembic_revision": alembic_rev,
        "por_perfil": por_perfil,
        "viveiros": viveiros_resumo,
    }


def get_rbac_matrix() -> dict[str, Any]:
    roles = []
    for role_id in sorted(VALID_ROLE_IDS):
        roles.append(
            {
                "id": role_id,
                "label": ROLE_LABELS.get(role_id, role_id),
                "permissoes": sorted(ROLE_PERMISSIONS.get(role_id, frozenset())),
            }
        )
    return {"roles": roles, "catalogo": sorted(ALL_PERMISSIONS)}
