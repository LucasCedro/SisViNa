"""Referência Embrapa: regras globais, ficha por espécie, data_inicio_estagio_atual

Revision ID: 09_embrapa_referencia_viveiro
Revises: 08_rustificacao_estagio
Create Date: 2026-05-27
"""
from alembic import op
import sqlalchemy as sa

revision = "09_embrapa_referencia_viveiro"
down_revision = "08_rustificacao_estagio"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "viveiro_regras_globais",
        sa.Column("chave", sa.String(80), primary_key=True),
        sa.Column("valor_numerico", sa.Numeric(12, 4)),
        sa.Column("valor_texto", sa.Text()),
        sa.Column("descricao", sa.Text()),
        sa.Column(
            "fonte",
            sa.String(200),
            nullable=False,
            server_default="Embrapa/RSC 2016",
        ),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "especies_ficha_embrapa",
        sa.Column(
            "id_especie",
            sa.Integer(),
            sa.ForeignKey("especies.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("nome_cientifico_ref", sa.String(150)),
        sa.Column("fitofisionomia", sa.Text()),
        sa.Column("mes_coleta_inicio", sa.SmallInteger()),
        sa.Column("mes_coleta_fim", sa.SmallInteger()),
        sa.Column("armazenamento_tipo", sa.String(40)),
        sa.Column("armazenamento_obs", sa.Text()),
        sa.Column("profundidade_semeadura_cm_min", sa.Numeric(4, 2)),
        sa.Column("profundidade_semeadura_cm_max", sa.Numeric(4, 2)),
        sa.Column("dias_inicio_germinacao", sa.Integer()),
        sa.Column("pct_germinacao_tipico", sa.Numeric(5, 2)),
        sa.Column("substrato_tipo", sa.SmallInteger()),
        sa.Column("conduz_pleno_sol", sa.Boolean()),
        sa.Column("meses_permanencia_viveiro", sa.Integer()),
        sa.Column("meses_permanencia_viveiro_max", sa.Integer()),
        sa.Column("dias_rustificacao_minimo", sa.Integer()),
        sa.Column("altura_campo_cm_min", sa.Numeric(5, 2)),
        sa.Column("altura_campo_cm_max", sa.Numeric(5, 2)),
        sa.Column("adubacao_obs", sa.Text()),
        sa.Column("observacoes_gerais", sa.Text()),
        sa.Column(
            "fonte",
            sa.String(200),
            nullable=False,
            server_default="Embrapa/RSC 2016",
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.add_column(
        "plantas",
        sa.Column("data_inicio_estagio_atual", sa.Date(), nullable=True),
    )

    # Inicializa estágio atual para plantas existentes (não quebra métricas)
    op.execute(
        """
        UPDATE plantas
        SET data_inicio_estagio_atual = COALESCE(data_germinacao, data_plantio, CURRENT_DATE)
        WHERE data_inicio_estagio_atual IS NULL
        """
    )

    op.bulk_insert(
        sa.table(
            "viveiro_regras_globais",
            sa.column("chave", sa.String),
            sa.column("valor_numerico", sa.Numeric),
            sa.column("descricao", sa.Text),
            sa.column("fonte", sa.String),
        ),
        [
            {
                "chave": "rustificacao_dias_minimo",
                "valor_numerico": 30,
                "descricao": "Permanência mínima na área de rustificação antes do campo.",
                "fonte": "Embrapa/RSC 2016",
            },
            {
                "chave": "rustificacao_inicio_antes_plantio_dias",
                "valor_numerico": 60,
                "descricao": "Início da retirada gradual de sombreamento antes do plantio definitivo.",
                "fonte": "Embrapa/RSC 2016",
            },
            {
                "chave": "altura_campo_cerrado_cm_min",
                "valor_numerico": 20,
                "descricao": "Altura mínima recomendada (Cerrado sentido amplo).",
                "fonte": "Embrapa/RSC 2016",
            },
            {
                "chave": "altura_campo_cerrado_cm_max",
                "valor_numerico": 30,
                "descricao": "Altura máxima típica (Cerrado sentido amplo).",
                "fonte": "Embrapa/RSC 2016",
            },
            {
                "chave": "altura_campo_floresta_cm_min",
                "valor_numerico": 50,
                "descricao": "Altura mínima recomendada (ambientes florestais).",
                "fonte": "Embrapa/RSC 2016",
            },
            {
                "chave": "permanencia_viveiro_meses_tipico",
                "valor_numerico": 5,
                "descricao": "Tempo médio de permanência no viveiro (varia por espécie).",
                "fonte": "Embrapa/RSC 2016",
            },
            {
                "chave": "permanencia_viveiro_meses_max",
                "valor_numerico": 12,
                "descricao": "Tempo máximo citado para algumas espécies (ex.: faveira, barbatimão).",
                "fonte": "Embrapa/RSC 2016",
            },
            {
                "chave": "rega_germinacao_vezes_dia",
                "valor_numerico": 2,
                "descricao": "Regas diárias na emergência (manhã e fim da tarde).",
                "fonte": "Embrapa/RSC 2016",
            },
            {
                "chave": "rega_rustificacao_vezes_dia",
                "valor_numerico": 1,
                "descricao": "Rega diária durante rustificação.",
                "fonte": "Embrapa/RSC 2016",
            },
            {
                "chave": "coleta_fracao_maxima_arvore",
                "valor_numerico": 0.5,
                "descricao": "Fração máxima de frutos por árvore (coleta sustentável).",
                "fonte": "Embrapa/RSC 2016",
            },
        ],
    )

    # Ficha exemplo: Ipê-amarelo (se espécie existir no cadastro)
    op.execute(
        """
        INSERT INTO especies_ficha_embrapa (
            id_especie, nome_cientifico_ref, fitofisionomia,
            mes_coleta_inicio, mes_coleta_fim, armazenamento_tipo, armazenamento_obs,
            profundidade_semeadura_cm_min, profundidade_semeadura_cm_max,
            dias_inicio_germinacao, pct_germinacao_tipico, substrato_tipo, conduz_pleno_sol,
            meses_permanencia_viveiro, adubacao_obs, observacoes_gerais
        )
        SELECT
            e.id,
            'Handroanthus serratifolius (Vahl.) S. Grose',
            'Cerradão e Cerrado sentido restrito.',
            9, 11,
            'recalcitrante',
            'Pouco tempo de armazenamento em câmara fria.',
            0.5, 1.0,
            7, 80.0,
            3, TRUE,
            8,
            'Geralmente desnecessária; consultar especialista se deficiência.',
            'Manual Embrapa/RSC — espécie 47 da Tabela 3.'
        FROM especies e
        WHERE LOWER(e.nome_popular) LIKE '%ipê-amarelo%'
           OR LOWER(e.nome_popular) LIKE '%ipe-amarelo%'
           OR LOWER(e.nome_cientifico) LIKE '%handroanthus serratifolius%'
        ON CONFLICT (id_especie) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_column("plantas", "data_inicio_estagio_atual")
    op.drop_table("especies_ficha_embrapa")
    op.drop_table("viveiro_regras_globais")
