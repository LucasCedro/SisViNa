"""Enriquece biblioteca e fichas Embrapa a partir do manual (JSON parseado).

Revision ID: 11_biblioteca_enriquecer_manual
Revises: 10_biblioteca_manual_90_especies
Create Date: 2026-05-28
"""

import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "11_biblioteca_enriquecer_manual"
down_revision = "10_biblioteca_manual_90_especies"
branch_labels = None
depends_on = None

def _data_file() -> Path:
    base = Path(__file__).resolve().parents[1]
    for candidate in (
        base / "seed" / "especies_manual_enriched.json",
        Path(__file__).resolve().parents[2] / "data" / "especies_manual_enriched.json",
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("especies_manual_enriched.json não encontrado em alembic/seed ou data/")


def _load_fichas():
    return json.loads(_data_file().read_text(encoding="utf-8"))


def upgrade() -> None:
    bind = op.get_bind()
    fichas = _load_fichas()

    for item in fichas:
        nome = item["nome_cientifico"]
        especie_id = bind.execute(
            sa.text("SELECT id FROM especies WHERE nome_cientifico = :nome"),
            {"nome": nome},
        ).scalar()
        if especie_id is None:
            continue

        bind.execute(
            sa.text(
                """
                UPDATE especies SET
                    nome_popular = COALESCE(:nome_popular, nome_popular),
                    familia = COALESCE(:familia, familia),
                    descricao = :descricao,
                    tempo_germinacao = :tempo_germinacao,
                    tempo_crescimento = :tempo_crescimento
                WHERE id = :id
                """
            ),
            {
                "id": especie_id,
                "nome_popular": item.get("nome_popular"),
                "familia": item.get("familia"),
                "descricao": item.get("descricao"),
                "tempo_germinacao": item.get("tempo_germinacao"),
                "tempo_crescimento": item.get("tempo_crescimento"),
            },
        )

        bind.execute(
            sa.text(
                """
                UPDATE especies_biblioteca SET
                    resumo_manejo = :resumo_manejo
                WHERE id_especie = :id_especie
                """
            ),
            {
                "id_especie": especie_id,
                "resumo_manejo": item.get("resumo_manejo"),
            },
        )

        fe = item.get("ficha_embrapa") or {}
        bind.execute(
            sa.text(
                """
                INSERT INTO especies_ficha_embrapa (
                    id_especie,
                    nome_cientifico_ref,
                    fitofisionomia,
                    mes_coleta_inicio,
                    mes_coleta_fim,
                    armazenamento_tipo,
                    armazenamento_obs,
                    profundidade_semeadura_cm_min,
                    profundidade_semeadura_cm_max,
                    dias_inicio_germinacao,
                    pct_germinacao_tipico,
                    substrato_tipo,
                    conduz_pleno_sol,
                    meses_permanencia_viveiro,
                    meses_permanencia_viveiro_max,
                    adubacao_obs,
                    observacoes_gerais,
                    fonte
                ) VALUES (
                    :id_especie,
                    :nome_cientifico_ref,
                    :fitofisionomia,
                    :mes_coleta_inicio,
                    :mes_coleta_fim,
                    :armazenamento_tipo,
                    :armazenamento_obs,
                    :profundidade_semeadura_cm_min,
                    :profundidade_semeadura_cm_max,
                    :dias_inicio_germinacao,
                    :pct_germinacao_tipico,
                    :substrato_tipo,
                    :conduz_pleno_sol,
                    :meses_permanencia_viveiro,
                    :meses_permanencia_viveiro_max,
                    :adubacao_obs,
                    :observacoes_gerais,
                    :fonte
                )
                ON CONFLICT (id_especie) DO UPDATE SET
                    nome_cientifico_ref = EXCLUDED.nome_cientifico_ref,
                    fitofisionomia = EXCLUDED.fitofisionomia,
                    mes_coleta_inicio = EXCLUDED.mes_coleta_inicio,
                    mes_coleta_fim = EXCLUDED.mes_coleta_fim,
                    armazenamento_tipo = EXCLUDED.armazenamento_tipo,
                    armazenamento_obs = EXCLUDED.armazenamento_obs,
                    profundidade_semeadura_cm_min = EXCLUDED.profundidade_semeadura_cm_min,
                    profundidade_semeadura_cm_max = EXCLUDED.profundidade_semeadura_cm_max,
                    dias_inicio_germinacao = EXCLUDED.dias_inicio_germinacao,
                    pct_germinacao_tipico = EXCLUDED.pct_germinacao_tipico,
                    substrato_tipo = EXCLUDED.substrato_tipo,
                    conduz_pleno_sol = EXCLUDED.conduz_pleno_sol,
                    meses_permanencia_viveiro = EXCLUDED.meses_permanencia_viveiro,
                    meses_permanencia_viveiro_max = EXCLUDED.meses_permanencia_viveiro_max,
                    adubacao_obs = EXCLUDED.adubacao_obs,
                    observacoes_gerais = EXCLUDED.observacoes_gerais,
                    fonte = EXCLUDED.fonte
                """
            ),
            {
                "id_especie": especie_id,
                "nome_cientifico_ref": fe.get("nome_cientifico_ref"),
                "fitofisionomia": fe.get("fitofisionomia"),
                "mes_coleta_inicio": fe.get("mes_coleta_inicio"),
                "mes_coleta_fim": fe.get("mes_coleta_fim"),
                "armazenamento_tipo": fe.get("armazenamento_tipo"),
                "armazenamento_obs": fe.get("armazenamento_obs"),
                "profundidade_semeadura_cm_min": fe.get("profundidade_semeadura_cm_min"),
                "profundidade_semeadura_cm_max": fe.get("profundidade_semeadura_cm_max"),
                "dias_inicio_germinacao": fe.get("dias_inicio_germinacao"),
                "pct_germinacao_tipico": fe.get("pct_germinacao_tipico"),
                "substrato_tipo": fe.get("substrato_tipo"),
                "conduz_pleno_sol": fe.get("conduz_pleno_sol"),
                "meses_permanencia_viveiro": fe.get("meses_permanencia_viveiro"),
                "meses_permanencia_viveiro_max": fe.get("meses_permanencia_viveiro_max"),
                "adubacao_obs": fe.get("adubacao_obs"),
                "observacoes_gerais": fe.get("observacoes_gerais"),
                "fonte": fe.get("fonte") or "SisViNa",
            },
        )


def downgrade() -> None:
    bind = op.get_bind()
    for item in _load_fichas():
        nome = item["nome_cientifico"]
        bind.execute(
            sa.text(
                """
                DELETE FROM especies_ficha_embrapa
                WHERE id_especie = (SELECT id FROM especies WHERE nome_cientifico = :nome)
                """
            ),
            {"nome": nome},
        )
