"""NF-e — tabelas fiscais, regras mudas, emitente demo

Revision ID: 22_nfe_fiscal
Revises: 21_premissas_energia_agua
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "22_nfe_fiscal"
down_revision = "21_premissas_energia_agua"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("compradores", sa.Column("numero", sa.String(20), nullable=True))
    op.add_column("compradores", sa.Column("bairro", sa.String(60), nullable=True))
    op.add_column("compradores", sa.Column("codigo_municipio_ibge", sa.String(7), nullable=True))
    op.add_column("compradores", sa.Column("inscricao_estadual", sa.String(20), nullable=True))
    op.add_column(
        "compradores",
        sa.Column("indicador_ie", sa.String(1), server_default="9", nullable=True),
    )

    op.create_table(
        "emitente_fiscal",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("razao_social", sa.String(120), nullable=False),
        sa.Column("nome_fantasia", sa.String(120)),
        sa.Column("cnpj", sa.String(18), nullable=False, unique=True),
        sa.Column("inscricao_estadual", sa.String(20), nullable=False),
        sa.Column("crt", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("cnae", sa.String(10)),
        sa.Column("logradouro", sa.String(120), nullable=False),
        sa.Column("numero", sa.String(20), nullable=False),
        sa.Column("complemento", sa.String(60)),
        sa.Column("bairro", sa.String(60), nullable=False),
        sa.Column("codigo_municipio_ibge", sa.String(7), nullable=False),
        sa.Column("municipio", sa.String(60), nullable=False),
        sa.Column("uf", sa.String(2), nullable=False),
        sa.Column("cep", sa.String(9), nullable=False),
        sa.Column("telefone", sa.String(20)),
        sa.Column("email", sa.String(100)),
        sa.Column("serie_nfe", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("proximo_numero_nfe", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("ambiente", sa.String(20), nullable=False, server_default="homologacao"),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("data_atualizacao", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "regras_fiscais",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ncm", sa.String(8), nullable=False),
        sa.Column("uf_origem", sa.String(2), nullable=False),
        sa.Column("uf_destino", sa.String(2), nullable=False),
        sa.Column("tipo_cliente", sa.String(10), nullable=False, server_default="ANY"),
        sa.Column("cfop_base", sa.String(4), nullable=False),
        sa.Column("csosn", sa.String(3), nullable=False),
        sa.Column("descricao_produto", sa.String(200)),
        sa.Column("unidade_comercial", sa.String(6), nullable=False, server_default="UN"),
        sa.Column("natureza_operacao", sa.String(60), server_default="Venda de mudas"),
        sa.Column("aplicar_difal", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("aliquota_icms_inter", sa.Numeric(5, 2)),
        sa.Column("aliquota_icms_intra", sa.Numeric(5, 2)),
        sa.Column("observacao", sa.Text()),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("ordem", sa.Integer(), server_default="0"),
        sa.Column("data_atualizacao", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_regras_fiscais_ncm", "regras_fiscais", ["ncm"])

    op.create_table(
        "notas_fiscais",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("id_venda", sa.Integer(), sa.ForeignKey("vendas.id"), nullable=False),
        sa.Column("ref_externa", sa.String(60), nullable=False, unique=True),
        sa.Column("chave_acesso", sa.String(44), unique=True),
        sa.Column("numero", sa.Integer()),
        sa.Column("serie", sa.Integer()),
        sa.Column("status", sa.String(30), nullable=False, server_default="processando"),
        sa.Column("cstat", sa.String(10)),
        sa.Column("xmotivo", sa.Text()),
        sa.Column("recibo", sa.String(60)),
        sa.Column("url_xml", sa.Text()),
        sa.Column("url_danfe", sa.Text()),
        sa.Column("payload_enviado", JSONB()),
        sa.Column("resposta_provedor", JSONB()),
        sa.Column("difal_snapshot", JSONB()),
        sa.Column("data_emissao", sa.DateTime()),
        sa.Column("data_registro", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("data_atualizacao", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_notas_fiscais_id_venda", "notas_fiscais", ["id_venda"])

    op.create_table(
        "notas_fiscais_itens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("id_nota", sa.Integer(), sa.ForeignKey("notas_fiscais.id"), nullable=False),
        sa.Column("numero_item", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.String(200), nullable=False),
        sa.Column("ncm", sa.String(8), nullable=False),
        sa.Column("cfop", sa.String(4), nullable=False),
        sa.Column("csosn", sa.String(3), nullable=False),
        sa.Column("unidade", sa.String(6), nullable=False),
        sa.Column("quantidade", sa.Numeric(12, 4), nullable=False),
        sa.Column("valor_unitario", sa.Numeric(12, 4), nullable=False),
        sa.Column("valor_total", sa.Numeric(12, 2), nullable=False),
    )
    op.create_index("ix_notas_fiscais_itens_id_nota", "notas_fiscais_itens", ["id_nota"])

    # Emitente demo (homologação) — CNPJ fictício para testes
    op.execute(
        """
        INSERT INTO emitente_fiscal (
          razao_social, nome_fantasia, cnpj, inscricao_estadual, crt,
          logradouro, numero, bairro, codigo_municipio_ibge, municipio, uf, cep,
          email, ambiente
        ) VALUES (
          'Viveiro Nativas Demonstração LTDA',
          'Brotare Demo',
          '00.000.000/0001-91',
          'ISENTO',
          1,
          'Rodovia Demo',
          'S/N',
          'Zona Rural',
          '3550308',
          'São Paulo',
          'SP',
          '01000-000',
          'fiscal@demo.local',
          'homologacao'
        )
        """
    )

    # Regras fiscais mudas 0602.90.90 — validar CSOSN/CFOP com contador
    op.execute(
        """
        INSERT INTO regras_fiscais (
          ncm, uf_origem, uf_destino, tipo_cliente, cfop_base, csosn,
          descricao_produto, aplicar_difal, aliquota_icms_inter, aliquota_icms_intra,
          observacao, ordem
        ) VALUES
        (
          '06029090', 'SP', 'SP', 'ANY', '5102', '400',
          'Muda de planta',
          false, NULL, NULL,
          'Operação interna SP — CSOSN 400 (validar isenção agrícola Conv. 100/97 com contador)',
          1
        ),
        (
          '06029090', 'SP', '*', 'ANY', '6102', '400',
          'Muda de planta',
          true, 12.00, 18.00,
          'Interestadual — DIFAL se consumidor final não contribuinte',
          2
        )
        """
    )

    # Comprador demo com endereço fiscal mínimo
    op.execute(
        """
        UPDATE compradores SET
          endereco = COALESCE(endereco, 'Rua Demonstração'),
          numero = COALESCE(numero, '100'),
          bairro = COALESCE(bairro, 'Centro'),
          cidade = COALESCE(cidade, 'São Paulo'),
          estado = COALESCE(estado, 'SP'),
          cep = COALESCE(cep, '01001-000'),
          codigo_municipio_ibge = COALESCE(codigo_municipio_ibge, '3550308'),
          indicador_ie = COALESCE(indicador_ie, '9')
        WHERE endereco IS NULL OR codigo_municipio_ibge IS NULL
        """
    )


def downgrade() -> None:
    op.drop_table("notas_fiscais_itens")
    op.drop_table("notas_fiscais")
    op.drop_table("regras_fiscais")
    op.drop_table("emitente_fiscal")
    op.drop_column("compradores", "indicador_ie")
    op.drop_column("compradores", "inscricao_estadual")
    op.drop_column("compradores", "codigo_municipio_ibge")
    op.drop_column("compradores", "bairro")
    op.drop_column("compradores", "numero")
