"""Biblioteca: tabela de conteudo e seed de 90 especies do manual.

Revision ID: 10_biblioteca_manual_90_especies
Revises: 09_embrapa_referencia_viveiro
Create Date: 2026-05-27
"""

from alembic import op
import sqlalchemy as sa


revision = "10_biblioteca_manual_90_especies"
down_revision = "09_embrapa_referencia_viveiro"
branch_labels = None
depends_on = None


MANUAL_LISTA_90 = """
1. Acrocomia aculeata (Jacq.) Lodd. ex Mart. – Macaúba 33
2. Albizia niopoides (Spruce ex Benth.) Burkart – Farinha-seca 34
3. Alibertia edulis (Rich.) A.Rich. – Marmelada-de-bezerro 35
4. Anacardium humile A. St. -Hil. – Cajuzinho-do-cerrado 36
5. Anadenanthera colubrina (Vell.) Brenan – Angico-vermelho, angico-branco 37
6. Anadenanthera peregrina (L.) Speg. – Angico-preto 38
7. Annona coriacea Mart. – Marolo-do-cerrado 39
8. Annona crassiflora Mart. – Araticum-do-cerrado 40
9. Apeiba tibourbou Aubl. – Pau-de-balsa, escova-de-macaco 41
10. Apuleia leiocarpa (Vogel) J.F.Macbr. – Garapa 42
11. Aspidosperma macrocarpon Mart. – Guatambu-do-cerrado 43
12. Aspidosperma pyrifolium Mart. – Peroba 44
13. Aspidosperma spruceanum Benth. ex Müll. Arg. – Peroba-cascuda 45
14. Aspidosperma subincanum Mart. – Guatambu-vermelho 46
15. Aspidosperma tomentosum Mart. – Peroba-do-cerrado 47
16. Astronium fraxinifolium Schott – Gonçalo-alves 48
17. Bowdichia virgilioides Kunth – Sucupira-preta 49
18. Brosimum gaudichaudii Trécul – Mama-cadela 50
19. Buchenavia tomentosa Eichler – Mirindiba 51
20. Byrsonima verbascifolia (L.) DC. – Murici-de-tabuleiro 52
21. Cabralea canjerana (Vell.) Mart. – Canjerana 53
22. Calophyllum brasiliense Cambess. – Landim 54
23. Caryocar brasiliense Cambess. – Pequi 55
24. Casearia sylvestris Swartz. – Tiú 56
25. Cecropia pachystachya Trécul. – Embaúba 57
26. Cedrela fissilis Vell. – Cedro-amarelo 58
27. Copaifera langsdorffii Desf. – Copaíba 59
28. Cordia trichotoma (Vell.) Arráb. ex Steud. – Freijó, Louro pardo 60
29. Croton urucurana Baill. – Sangra d’água 61
30. Cybistax antisyphilitica (Mart) Mart. – Ipê-verde 62
31. Dalbergia miscolobium Benth. – Jacarandá-do-cerrado, caviúna 63
32. Dimorphandra mollis Benth. – Faveiro-do-cerrado 64
33. Dipteryx alata Vogel – Baru 65
34. Emmotum nitens (Benth.) Miers – Pau-sobre 66
35. Enterolobium contortisiliquum (Vell.) Morong – Tamboril 67
36. Eriotheca pubescens (Mart. & Zucc.) Schott & Endl. – Paineira-do-cerrado 68
37. Eugenia dysenterica (Mart.) DC. – Cagaita 69
38. Euterpe edulis Mart. – Jussara 70
39. Genipa americana L. – Jenipapo 71
40. Guarea guidonia (L.) Sleumer – Marinheiro-do-mato 72
41. Guazuma ulmifolia Lam. – Mutamba 73
42. Hancornia speciosa Gomes – Mangaba 74
43. Handroanthus chrysotrichus (Mart. Ex DC.) Mattos – Ipê-dourado 75
44. Handroanthus heptaphyllus (Vell.) Mattos – Ipê-roxo 76
45. Handroanthus impetiginosus (Mart. ex. DC.) Mattos – Ipê-roxo-da-mata 77
46. Handroanthus ochraceus (Cham.) Mattos – Ipê-do-cerrado 78
47. Handroanthus serratifolius (Vahl.) S. Grose – Ipê-amarelo 79
48. Hymenaea courbaril L. – Jatobá-da-mata 80
49. Hymenaea stigonocarpa Mart. ex Hayne – Jatobá-do-cerrado 81
50. Inga cylindrica (Vell.) Mart. – Ingá-feijão 82
51. Inga laurina (Sw.) Willd. – Ingá-de-quatro-folhas 83
52. Inga vera Willd. – Ingá 84
53. Jacaranda brasiliana (Lam.) Pers. – Carobão 85
54. Jacaranda cuspidifolia Mart. – Caroba 86
55. Kielmeyera coriaceae Mart. & Zucc. – Pau-santo 87
56. Lafoensia pacari A. St. -Hil. – Pacari 88
57. Luehea paniculata Mart. & Zucc. – Açoita-cavalo 89
58. Magnolia ovata (A.St.-Hil.) Spreng. – Pinha-do-brejo 90
59. Magonia pubescens A. St. -Hil. – Tingui 91
60. Mauritia flexuosa L.f. – Buriti 92
61. Myracrodruon urundeuva Allemão – Aroeira 93
62. Myroxylon peruiferum L. f. – Bálsamo 94
63. Parkia pendula (Willd.) Benth. ex. Walp. – Fava-de-bolota 95
64. Physocalymma scaberrimum Pohl – Cega-machado 96
65. Piptadenia gonoacantha (Mart.) J.F. Macbr. – Pau-jacaré 97
66. Platypodium elegans Vogel – Canzileiro 98
67. Pouteria ramiflora (Mart.) Radlk. – Curriola 99
68. Pouteria torta (Mart.) Radlk. – Guapeva 100
69. Pseudobombax longiflorum (Mart. & Zucc.) A. Robyns – Embiruçu-da-mata 101
70. Pterodon emarginatus Vogel. – Sucupira-branca-da-flor-roxa 102
71. Pterodon pubescens (Benth.) Benth. – Sucupira-branca-da-flor-rosa 103
72. Qualea grandiflora Mart. – Pau-terra-grande 104
73. Qualea parviflora Mart. – Pau-terra-da-mata 105
74. Rhamnidium elaeocarpum Reissek– Cafezinho 106
75. Roupala montana Aubl. – Carne-de-vaca 107
76. Salacia crassifolia (Mart. ex Schult.) G. Don – Bacupari-do-cerrado 108
77. Schinopsis brasiliensis Engl. – Braúna 109
78. Senna macranthera (DC. ex Collad.) H. S. Irwin & Barneby – Fedegosão 110
79. Senna multijuga (Rich.) H. S. Irwin & Barneby – Canafístula 111
80. Simarouba amara Aubl. – Mata-cachorro 112
81. Solanum falsiforme Farruggia – Lobeira 113
82. Stryphondendron adstringens (Mart.) Coville – Barbatimão 114
83. Swartzia langsdorffii Raddi – Banha-de-galinha 115
84. Syagrus oleracea (Mart.) Becc. – Gueroba 116
85. Syagrus romanzoffiana (Cham.) Glassman – Jerivá 117
86. Tabebuia aurea (Silva Manso) Benth. & Hook.f. ex S.Moore – Ipê-caraíba 118
87. Tapirira guianensis Aubl. – Pau-pombo 119
88. Terminalia argentea Mart. – Capitão-do-cerrado 120
89. Tibouchina candolleana (Mart. ex DC.) Cogn. – Quaresmeira 121
90. Xylopia aromatica (Lam.) Mart. – Pimenta-de-macaco 122
"""


def _parse_lista():
    import re

    out = []
    for raw in MANUAL_LISTA_90.strip().splitlines():
        line = raw.strip()
        m = re.match(r"^(\d+)\.\s*(.+)$", line)
        if not m:
            continue
        ordem = int(m.group(1))
        restante = re.sub(r"\s+\d+\s*$", "", m.group(2)).strip()

        if " – " in restante:
            nome_cientifico, nome_popular = restante.split(" – ", 1)
        elif "– " in restante:
            nome_cientifico, nome_popular = restante.split("– ", 1)
        elif " –" in restante:
            nome_cientifico, nome_popular = restante.split(" –", 1)
        else:
            nome_cientifico, nome_popular = restante.split("–", 1)
        out.append((ordem, nome_cientifico.strip(), nome_popular.strip()))
    return sorted(out, key=lambda x: x[0])


def upgrade() -> None:
    op.create_table(
        "especies_biblioteca",
        sa.Column(
            "id_especie",
            sa.Integer(),
            sa.ForeignKey("especies.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("pagina_manual", sa.Integer()),
        sa.Column(
            "origem_manual",
            sa.String(200),
            nullable=False,
            server_default="Manual RSC/Embrapa 2016",
        ),
        sa.Column("resumo_manejo", sa.Text()),
        sa.Column("imagem_arvore", sa.String(255)),
        sa.Column("imagem_semente", sa.String(255)),
        sa.Column("imagem_folha", sa.String(255)),
        sa.Column("atualizado_em", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    bind = op.get_bind()

    for ordem, nome_cientifico, nome_popular in _parse_lista():
        especie_id = bind.execute(
            sa.text("SELECT id FROM especies WHERE nome_cientifico = :nome"),
            {"nome": nome_cientifico},
        ).scalar()

        if especie_id is None:
            especie_id = bind.execute(
                sa.text(
                    """
                    INSERT INTO especies (
                        nome_cientifico,
                        nome_popular,
                        familia,
                        descricao,
                        tempo_germinacao,
                        tempo_crescimento
                    )
                    VALUES (:nome_cientifico, :nome_popular, 'Nativa do Cerrado', :descricao, NULL, NULL)
                    RETURNING id
                    """
                ),
                {
                    "nome_cientifico": nome_cientifico,
                    "nome_popular": nome_popular,
                    "descricao": (
                        f"Espécie listada no Manual de Viveiro e Produção de Mudas "
                        f"(RSC/Embrapa 2016), item {ordem}."
                    ),
                },
            ).scalar()
        else:
            bind.execute(
                sa.text(
                    """
                    UPDATE especies
                    SET nome_popular = COALESCE(nome_popular, :nome_popular)
                    WHERE id = :id
                    """
                ),
                {"id": especie_id, "nome_popular": nome_popular},
            )

        bind.execute(
            sa.text(
                """
                INSERT INTO especies_biblioteca (
                    id_especie,
                    pagina_manual,
                    origem_manual,
                    resumo_manejo,
                    imagem_arvore,
                    imagem_semente,
                    imagem_folha
                )
                VALUES (
                    :id_especie,
                    :pagina_manual,
                    'Manual RSC/Embrapa 2016',
                    :resumo_manejo,
                    :imagem_arvore,
                    :imagem_semente,
                    :imagem_folha
                )
                ON CONFLICT (id_especie) DO UPDATE SET
                    pagina_manual = EXCLUDED.pagina_manual,
                    resumo_manejo = COALESCE(especies_biblioteca.resumo_manejo, EXCLUDED.resumo_manejo),
                    origem_manual = EXCLUDED.origem_manual
                """
            ),
            {
                "id_especie": especie_id,
                "pagina_manual": ordem + 32,
                "resumo_manejo": (
                    f"Ficha técnica da espécie no manual (item {ordem}). "
                    "Completar campos de manejo detalhado (coleta, semeadura, substrato, germinação, "
                    "rustificação e expedição) conforme capítulo da espécie."
                ),
                "imagem_arvore": f"/assets/biblioteca/especies/arvores/{especie_id}.jpg",
                "imagem_semente": f"/assets/biblioteca/especies/sementes/{especie_id}.jpg",
                "imagem_folha": f"/assets/biblioteca/especies/folhas/{especie_id}.jpg",
            },
        )


def downgrade() -> None:
    op.drop_table("especies_biblioteca")
