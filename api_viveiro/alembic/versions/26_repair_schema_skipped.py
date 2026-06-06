"""Repara schema quando alembic foi stampado sem rodar migrations 06–20.

Revision ID: 26_repair_schema_skipped
Revises: 25_regra_fiscal_importacao_sn
"""

from alembic import op

revision = "26_repair_schema_skipped"
down_revision = "25_regra_fiscal_importacao_sn"
branch_labels = None
depends_on = None


def _run(sql: str) -> None:
    op.execute(sql)


def upgrade() -> None:
    _run("ALTER TABLE funcionarios ADD COLUMN IF NOT EXISTS perfis JSONB")
    _run(
        """
        UPDATE funcionarios SET perfis = '["admin","gestor","campo","financeiro","rh","consulta"]'::jsonb
        WHERE usuario = 'admin' AND (perfis IS NULL OR perfis::text = 'null')
        """
    )

    _run("ALTER TABLE insumos ADD COLUMN IF NOT EXISTS estoque_minimo NUMERIC(10,2) DEFAULT 0")
    _run("ALTER TABLE insumos ADD COLUMN IF NOT EXISTS estoque_maximo NUMERIC(10,2)")
    _run("ALTER TABLE insumos ADD COLUMN IF NOT EXISTS valor_estoque NUMERIC(12,2) DEFAULT 0")
    _run(
        """
        UPDATE insumos
        SET valor_estoque = COALESCE(quantidade_estoque, 0) * COALESCE(preco_unitario, 0)
        WHERE valor_estoque IS NULL OR valor_estoque = 0
        """
    )

    _run(
        """
        CREATE TABLE IF NOT EXISTS insumo_movimentacoes (
            id SERIAL PRIMARY KEY,
            id_insumo INTEGER NOT NULL REFERENCES insumos(id) ON DELETE CASCADE,
            tipo VARCHAR(20) NOT NULL,
            quantidade NUMERIC(10,2) NOT NULL,
            valor_total NUMERIC(12,2),
            preco_unitario NUMERIC(10,4),
            saldo_quantidade NUMERIC(10,2) NOT NULL,
            data_movimento DATE NOT NULL,
            observacao TEXT,
            criado_em TIMESTAMP DEFAULT now()
        )
        """
    )
    _run("CREATE INDEX IF NOT EXISTS ix_insumo_mov_id_insumo ON insumo_movimentacoes(id_insumo)")
    _run("CREATE INDEX IF NOT EXISTS ix_insumo_mov_data ON insumo_movimentacoes(data_movimento)")

    _run(
        """
        CREATE TABLE IF NOT EXISTS viveiro_layout (
            id INTEGER PRIMARY KEY,
            layout_json TEXT NOT NULL DEFAULT '{}',
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    _run(
        """
        INSERT INTO viveiro_layout (id, layout_json)
        VALUES (1, '{}')
        ON CONFLICT (id) DO NOTHING
        """
    )

    _run(
        """
        CREATE TABLE IF NOT EXISTS especies_biblioteca (
            id_especie INTEGER PRIMARY KEY REFERENCES especies(id) ON DELETE CASCADE,
            pagina_manual INTEGER,
            origem_manual VARCHAR(200) NOT NULL DEFAULT 'SisViNa',
            resumo_manejo TEXT,
            imagem_arvore VARCHAR(255),
            imagem_semente VARCHAR(255),
            imagem_folha VARCHAR(255),
            imagens_externas JSONB,
            cache_imagens_em TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    _run("ALTER TABLE especies_biblioteca ADD COLUMN IF NOT EXISTS imagens_externas JSONB")
    _run("ALTER TABLE especies_biblioteca ADD COLUMN IF NOT EXISTS cache_imagens_em TIMESTAMP")
    _run("ALTER TABLE itens_venda ADD COLUMN IF NOT EXISTS custo_unitario NUMERIC(10,2)")
    _run("ALTER TABLE lotes_sementes ADD COLUMN IF NOT EXISTS valor_total NUMERIC(14,2)")
    _run("ALTER TABLE lotes_sementes ADD COLUMN IF NOT EXISTS custo_unitario NUMERIC(12,4)")
    _run("ALTER TABLE semeaduras ADD COLUMN IF NOT EXISTS custo_sementes NUMERIC(12,2) DEFAULT 0")
    _run("ALTER TABLE semeaduras ADD COLUMN IF NOT EXISTS custo_insumos NUMERIC(12,2) DEFAULT 0")
    _run("ALTER TABLE semeaduras ADD COLUMN IF NOT EXISTS custo_indireto NUMERIC(12,2) DEFAULT 0")
    _run("ALTER TABLE semeaduras ADD COLUMN IF NOT EXISTS custo_total NUMERIC(12,2) DEFAULT 0")
    _run("ALTER TABLE semeaduras ADD COLUMN IF NOT EXISTS custo_unitario_muda NUMERIC(12,2)")


def downgrade() -> None:
    pass
