"""especies_master: chave normalizada, GIN populares, ultima_atualizacao."""

from alembic import op
import sqlalchemy as sa

revision = "30_especies_master_chave_gin"
down_revision = "29_especies_master"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("especies_master", sa.Column("nome_cientifico_chave", sa.Text(), nullable=True))

    op.execute(
        """
        UPDATE especies_master
        SET nome_cientifico_chave = lower(regexp_replace(trim(nome_cientifico), '\\s+', ' ', 'g'))
        WHERE nome_cientifico_chave IS NULL
        """
    )

    op.alter_column("especies_master", "nome_cientifico_chave", nullable=False)
    op.alter_column(
        "especies_master",
        "nome_cientifico",
        type_=sa.Text(),
        existing_type=sa.String(150),
        existing_nullable=False,
    )
    op.alter_column(
        "especies_master",
        "familia",
        type_=sa.Text(),
        existing_type=sa.String(80),
        existing_nullable=True,
    )

    op.drop_index("ix_especies_master_nome_cientifico", table_name="especies_master")
    op.create_index(
        "ix_especies_master_nome_cientifico_chave",
        "especies_master",
        ["nome_cientifico_chave"],
        unique=True,
    )
    op.create_index(
        "idx_especies_populares",
        "especies_master",
        ["nomes_populares"],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_especies_nome",
        "especies_master",
        ["nome_cientifico"],
        unique=False,
    )

    op.alter_column("especies_master", "sincronizado_em", new_column_name="ultima_atualizacao")


def downgrade() -> None:
    op.alter_column("especies_master", "ultima_atualizacao", new_column_name="sincronizado_em")
    op.drop_index("idx_especies_nome", table_name="especies_master")
    op.drop_index("idx_especies_populares", table_name="especies_master")
    op.drop_index("ix_especies_master_nome_cientifico_chave", table_name="especies_master")
    op.create_index(
        "ix_especies_master_nome_cientifico",
        "especies_master",
        ["nome_cientifico"],
        unique=True,
    )
    op.drop_column("especies_master", "nome_cientifico_chave")
