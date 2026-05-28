"""
Extrai fichas técnicas do texto-fonte interno e gera JSON para seed da biblioteca.

Uso (na raiz api_viveiro):
  python scripts/parse_manual_especies.py
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL_TXT = ROOT / "data" / "manual_viveiro_cerrado.txt"
OUT_JSON = ROOT / "data" / "especies_manual_enriched.json"

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

MESES = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _aliases_tabela(text: str) -> dict[str, list[str]]:
    """Mapa nome científico -> sinônimos populares da tabela resumo (ex.: Urucurana)."""
    aliases: dict[str, list[str]] = {}
    for line in text.splitlines():
        m = re.match(
            r"^(\d+)\s+([A-Z][^\n]+?)\s+([A-Z][a-zA-Z]+(?:aceae|eae))\s+(.+)$",
            line.strip(),
        )
        if not m:
            continue
        sci = m.group(2).strip()
        pop_tab = m.group(4).strip()
        if pop_tab and pop_tab[0].isupper():
            aliases.setdefault(sci, [])
            if pop_tab not in aliases[sci]:
                aliases[sci].append(pop_tab)
    return aliases


def parse_lista(text: str):
    aliases_map = _aliases_tabela(text)
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
        populares = [p.strip() for p in re.split(r",\s*", nome_popular.strip())]
        nc = nome_cientifico.strip()
        for alias in aliases_map.get(nc, []):
            if alias not in populares:
                populares.append(alias)
        out.append(
            {
                "ordem": ordem,
                "nome_cientifico": nc,
                "nome_popular": nome_popular.strip(),
                "populares": populares,
            }
        )
    return sorted(out, key=lambda x: x["ordem"])


def extract_ficha_blocks(text: str) -> list[str]:
    """Divide pelo início de cada ficha (Fitofisionomia / Fisionomia)."""
    parts = re.split(
        r"(?=(?:Fitofisionomias?|Fisionomia) de ocorr[eê]ncia)",
        text,
        flags=re.I,
    )
    blocks = []
    for part in parts:
        part = part.strip()
        if len(part) < 80:
            continue
        low = part.lower()
        if "sementes" not in low or ("obten" not in low and "época" not in low and "epoca" not in low):
            continue
        # Remove lixo de rodapé/cabeçalho após observações ou adubação
        m = re.search(
            r"(Observa[cç][oõ]es gerais.+?)(?=\nManual de Viveiro|\n\d+\s+\d+\s*$|\Z)",
            part,
            flags=re.I | re.S,
        )
        if m:
            end = m.end()
            tail = part[end : end + 400]
            if re.search(r"^\d+\.\s+[A-Z]", tail, re.M):
                part = part[:end]
        blocks.append(part.strip())
    return blocks


def epoca_popular_hint(block: str) -> str:
    m = re.search(
        r"(?:[ÉE]poca de obten[cç][aã]o|Obten[cç][aã]o)(?:\s+(?:das?|de))?\s+sementes.+?"
        r"(?:frutos|sementes|vagens|n[oó]dulos|cap[sí]sulas|aqu[eê]nios)"
        r"(?:\s+da|\s+de|\s+do|\s+das|\s+dos)?\s+([^,\.\n]+)",
        block,
        flags=re.I,
    )
    if m:
        return norm(m.group(1))
    return ""


def match_block_to_species(block: str, especies: list[dict]) -> dict | None:
    hint = epoca_popular_hint(block)
    if not hint:
        return None
    tokens = set(hint.split())
    best = None
    best_score = 0
    for sp in especies:
        for pop in sp["populares"]:
            pn = norm(pop)
            if not pn:
                continue
            score = 0
            if hint == pn:
                score = 100 + len(pn)
            elif hint in pn or pn in hint:
                score = 50 + len(pn)
            else:
                pop_tokens = set(pn.split())
                overlap = len(tokens & pop_tokens)
                if overlap >= max(1, len(pop_tokens) - 1):
                    score = 20 + overlap * 5
            if score > best_score:
                best_score = score
                best = sp
    return best if best_score >= 20 else None


def _mes_num(nome: str) -> int | None:
    n = norm(nome)
    for k, v in MESES.items():
        if norm(k) == n:
            return v
    return None


def parse_meses_coleta(block: str) -> tuple[int | None, int | None]:
    m = re.search(
        r"entre os meses de\s+([a-zçãéíóú]+)\s+e\s+([a-zçãéíóú]+)",
        block,
        flags=re.I,
    )
    if m:
        return _mes_num(m.group(1)), _mes_num(m.group(2))
    m = re.search(r"\bem\s+([a-zçãéíóú]+)\b", block, flags=re.I)
    if m:
        v = _mes_num(m.group(1))
        return v, v
    m = re.search(
        r"pico.+?(?:meses de\s+)?([a-zçãéíóú]+)\s+a\s+([a-zçãéíóú]+)",
        block,
        flags=re.I,
    )
    if m:
        return _mes_num(m.group(1)), _mes_num(m.group(2))
    if re.search(r"durante todo o ano", block, re.I):
        return 1, 12
    return None, None


def _num(s: str) -> float:
    return float(s.replace(",", "."))


def parse_profundidade(block: str) -> tuple[float | None, float | None]:
    m = re.search(
        r"profundidade de\s*([\d,]+)\s*cm\s*a\s*([\d,]+)\s*cm",
        block,
        flags=re.I,
    )
    if m:
        return _num(m.group(1)), _num(m.group(2))
    m = re.search(
        r"enterradas a uma\s+profundidade de\s*([\d,]+)\s*cm\s*a\s*([\d,]+)\s*cm",
        block,
        flags=re.I,
    )
    if m:
        return _num(m.group(1)), _num(m.group(2))
    m = re.search(r"([\d,]+)\s*cm\s*a\s*([\d,]+)\s*cm", block, flags=re.I)
    if m and "profund" in block.lower()[: m.start() + 200]:
        return _num(m.group(1)), _num(m.group(2))
    return None, None


def parse_germinacao_dias(block: str) -> int | None:
    for pat in [
        r"come[cç]am a germinar entre\s+(\d+)\s+a\s+(\d+)\s+dias",
        r"germinar entre\s+(\d+)\s+a\s+(\d+)\s+dias",
        r"germinar de\s+(\d+)\s+a\s+(\d+)\s+dias",
        r"de\s+(\d+)\s+a\s+(\d+)\s+dias.+?germina",
        r"germinar a partir de\s+(\d+)\s+dias",
        r"germinar ap[oó]s\s+(\d+)\s+dias",
        r"ap[oó]s\s+(\d+)\s+a\s+(\d+)\s+dias.+?germina",
    ]:
        m = re.search(pat, block, flags=re.I | re.S)
        if m:
            return int(m.group(1))
    return None


def parse_pct_germinacao(block: str) -> float | None:
    m = re.search(
        r"(?:porcentagem de )?germina[cç][aã]o\s+(?:[eé]\s+)?entre\s+(\d+)\s*%?\s+e\s+(\d+)\s*%",
        block,
        flags=re.I,
    )
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2
    m = re.search(
        r"germina[cç][aã]o\s+(?:[eé]\s+)?(?:maior|menor|superior)\s+que\s+(\d+)\s*%",
        block,
        flags=re.I,
    )
    if m:
        return float(m.group(1))
    m = re.search(
        r"germina[cç][aã]o\s+(?:[eé]\s+)?(?:de\s+)?(?:apenas\s+)?(\d+)\s*%",
        block,
        flags=re.I,
    )
    if m:
        return float(m.group(1))
    m = re.search(r"alcan[cç]ar\s+(\d+)\s*%", block, flags=re.I)
    if m:
        return float(m.group(1))
    return None


def parse_substrato(block: str) -> int | None:
    m = re.search(r"Substrato\s*[-–]\s*Tipo\s*(\d)", block, flags=re.I)
    return int(m.group(1)) if m else None


def parse_permanencia(block: str) -> tuple[int | None, int | None]:
    m = re.search(
        r"entre\s+(\d+)\s+e\s+(\d+)\s+meses",
        block,
        flags=re.I,
    )
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(
        r"em\s+(\d+)\s+meses\s+ap[oó]s",
        block,
        flags=re.I,
    )
    if m:
        v = int(m.group(1))
        return v, v
    m = re.search(r"prontas.+?(\d+)\s+meses", block, flags=re.I)
    if m:
        v = int(m.group(1))
        return v, v
    return None, None


def parse_armazenamento(block: str) -> tuple[str | None, str | None]:
    m = re.search(r"Armazenamento\s*[-–]\s*(.+?)(?=\n[A-Z]|\nSemeadura|\Z)", block, flags=re.I | re.S)
    obs = m.group(1).strip() if m else None
    if not obs:
        return None, None
    low = obs.lower()
    if "recalcitrante" in low:
        tipo = "recalcitrante"
    elif "ortodoxa" in low:
        tipo = "ortodoxa"
    elif "câmara fria" in low or "camara fria" in low:
        tipo = "camara_fria"
    elif "ambiente seco" in low or "local fresco" in low:
        tipo = "ortodoxa"
    elif "sem informação" in low or "sem informacao" in low:
        tipo = None
    else:
        tipo = "ortodoxa"
    return tipo, obs[:2000] if obs else None


def trim_junk(text: str | None) -> str | None:
    if not text:
        return text
    text = text.replace("\x02", "")
    text = re.sub(r"\s+", " ", text).strip()
    m = re.search(r"\s+\d{1,2}\.\s+[A-Z][a-zA-Z]+", text)
    if m:
        text = text[: m.start()].strip()
    m = re.search(r"\s+Fam[ií]lia:\s*", text, re.I)
    if m and m.start() > 40:
        text = text[: m.start()].strip()
    return text[:3000] if text else None


def section_text(block: str, label_pattern: str) -> str | None:
    m = re.search(
        rf"({label_pattern})\s*[-–]\s*(.+?)(?=\n[A-Za-zÀ-ÿ][^\n]*\s*[-–]\s*|\Z)",
        block,
        flags=re.I | re.S,
    )
    if not m:
        return None
    return trim_junk(m.group(2).strip())


def parse_familia_tabela(text: str, nome_cientifico: str) -> str | None:
    genus = nome_cientifico.split()[0]
    for line in text.splitlines():
        if genus not in line:
            continue
        m = re.match(
            rf"^\d+\s+{re.escape(genus)}.+?\s+([A-Z][a-zA-Z]+(?:aceae|eae))\s+",
            line,
        )
        if m:
            return m.group(1)
    return None


def build_resumo(block: str, sections: dict) -> str:
    lines = []
    labels = [
        ("fitofisionomia", "Fitofisionomia"),
        ("epoca", "Época de coleta"),
        ("processamento", "Processamento"),
        ("armazenamento", "Armazenamento"),
        ("semeadura", "Semeadura e germinação"),
        ("repicagem", "Repicagem"),
        ("conducao", "Condução no viveiro"),
        ("substrato", "Substrato"),
        ("permanencia", "Permanência no viveiro"),
        ("adubacao", "Adubação"),
        ("observacoes", "Observações"),
    ]
    for key, label in labels:
        val = sections.get(key)
        if val:
            lines.append(f"{label}: {val}")
    if not lines:
        return re.sub(r"\s+", " ", block)[:4000]
    return "\n\n".join(lines)


def parse_block(block: str, especie: dict, full_text: str) -> dict:
    fito = section_text(
        block,
        r"Fitofisionomias? de ocorr[eê]ncia|Fisionomia de ocorr[eê]ncia",
    )
    epoca = section_text(
        block,
        r"(?:[ÉE]poca de obten[cç][aã]o|Obten[cç][aã]o)(?:\s+(?:das?|de))?\s+sementes",
    )
    proc = section_text(block, r"Processamento do fruto e limpeza das sementes")
    arm_txt = section_text(block, r"Armazenamento")
    sem = section_text(block, r"Semeadura e germina[cç][aã]o")
    rep = section_text(block, r"Repicagem")
    cond = section_text(block, r"Condu[cç][aã]o da muda no viveiro")
    sub_txt = section_text(block, r"Substrato")
    perm = section_text(
        block,
        r"Tempo de perman[eê]ncia no viveiro|Perman[eê]ncia no viveiro",
    )
    adub = section_text(block, r"Aduba[cç][aã]o(?: de cobertura)?")
    obs = section_text(block, r"Observa[cç][oõ]es gerais")

    mes_i, mes_f = parse_meses_coleta(block)
    prof_min, prof_max = parse_profundidade(block)
    dias_g = parse_germinacao_dias(block)
    pct_g = parse_pct_germinacao(block)
    substrato = parse_substrato(block)
    meses_min, meses_max = parse_permanencia(block)
    arm_tipo, arm_obs = parse_armazenamento(block)
    pleno_sol = bool(re.search(r"pleno sol", block, re.I))

    familia = parse_familia_tabela(full_text, especie["nome_cientifico"])
    if not familia:
        fm = re.search(r"Fam[ií]lia:\s*([^\n]+)", full_text, re.I)
        if fm:
            familia = fm.group(1).strip()

    sections = {
        "fitofisionomia": fito,
        "epoca": epoca,
        "processamento": proc,
        "armazenamento": arm_txt or arm_obs,
        "semeadura": sem,
        "repicagem": rep,
        "conducao": cond,
        "substrato": sub_txt or (f"Tipo {substrato}" if substrato else None),
        "permanencia": perm,
        "adubacao": adub,
        "observacoes": obs,
    }
    resumo = trim_junk(build_resumo(block, sections)) or ""
    descricao = (trim_junk(fito) or resumo)[:500]
    tempo_germ = dias_g
    tempo_cresc = None
    if meses_min:
        avg_m = meses_min if not meses_max else (meses_min + meses_max) // 2
        tempo_cresc = avg_m * 30

    return {
        "ordem": especie["ordem"],
        "nome_cientifico": especie["nome_cientifico"],
        "nome_popular": especie["nome_popular"],
        "familia": familia,
        "descricao": descricao,
        "tempo_germinacao": tempo_germ,
        "tempo_crescimento": tempo_cresc,
        "resumo_manejo": resumo,
        "ficha_embrapa": {
            "nome_cientifico_ref": especie["nome_cientifico"],
            "fitofisionomia": fito,
            "mes_coleta_inicio": mes_i,
            "mes_coleta_fim": mes_f,
            "armazenamento_tipo": arm_tipo,
            "armazenamento_obs": arm_obs,
            "profundidade_semeadura_cm_min": prof_min,
            "profundidade_semeadura_cm_max": prof_max,
            "dias_inicio_germinacao": dias_g,
            "pct_germinacao_tipico": pct_g,
            "substrato_tipo": substrato,
            "conduz_pleno_sol": pleno_sol,
            "meses_permanencia_viveiro": meses_min,
            "meses_permanencia_viveiro_max": meses_max,
            "adubacao_obs": trim_junk(adub),
            "observacoes_gerais": trim_junk(obs),
            "fonte": "SisViNa",
        },
        "secoes": {k: v for k, v in sections.items() if v},
    }


def main():
    text = MANUAL_TXT.read_text(encoding="utf-8", errors="ignore")
    especies = parse_lista(text)
    blocks = extract_ficha_blocks(text)

    matched: dict[int, str] = {}
    unmatched_blocks = []

    for blk in blocks:
        sp = match_block_to_species(blk, especies)
        if sp:
            prev = matched.get(sp["ordem"])
            if not prev or len(blk) > len(prev):
                matched[sp["ordem"]] = blk
        else:
            unmatched_blocks.append(blk[:120])

    fichas = []
    missing = []
    for sp in especies:
        blk = matched.get(sp["ordem"])
        if not blk:
            missing.append(sp["nome_cientifico"])
            continue
        fichas.append(parse_block(blk, sp, text))

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(fichas, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Blocos extraídos: {len(blocks)}")
    print(f"Fichas geradas: {len(fichas)} / {len(especies)}")
    if missing:
        print("Sem match:", ", ".join(missing[:15]), "..." if len(missing) > 15 else "")
    if unmatched_blocks:
        print(f"Blocos órfãos: {len(unmatched_blocks)}")


if __name__ == "__main__":
    main()
