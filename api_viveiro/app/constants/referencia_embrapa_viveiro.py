"""
Parâmetros operacionais do viveiro (regras globais e fichas por espécie).
Usados em validações suaves (avisos) — não bloqueiam fluxos por padrão.
"""

FONTE_SISTEMA = "SisViNa"

# --- Rustificação / endurecimento ---
RUSTIFICACAO_DIAS_MINIMO = 30
RUSTIFICACAO_INICIO_ANTES_PLANTIO_DIAS = 60

# --- Tamanho para campo ---
ALTURA_CAMPO_CERRADO_CM_MIN = 20
ALTURA_CAMPO_CERRADO_CM_MAX = 30
ALTURA_CAMPO_FLORESTA_CM_MIN = 50

# --- Permanência no viveiro (geral; espécie pode divergir na ficha) ---
PERMANENCIA_VIVEIRO_MESES_TIPICO = 5
PERMANENCIA_VIVEIRO_MESES_MAX = 12

# --- Manejo ---
REGA_GERMINACAO_VEZES_DIA = 2
REGA_RUSTIFICACAO_VEZES_DIA = 1
COLETA_FRACAO_MAXIMA_POR_ARVORE = 0.5

# --- Substratos (tipos 1, 2 e 3) ---
SUBSTRATO_TIPOS = (1, 2, 3)

REGRAS_GLOBAIS_CHAVES = {
    "rustificacao_dias_minimo": RUSTIFICACAO_DIAS_MINIMO,
    "rustificacao_inicio_antes_plantio_dias": RUSTIFICACAO_INICIO_ANTES_PLANTIO_DIAS,
    "altura_campo_cerrado_cm_min": ALTURA_CAMPO_CERRADO_CM_MIN,
    "altura_campo_cerrado_cm_max": ALTURA_CAMPO_CERRADO_CM_MAX,
    "altura_campo_floresta_cm_min": ALTURA_CAMPO_FLORESTA_CM_MIN,
    "permanencia_viveiro_meses_tipico": PERMANENCIA_VIVEIRO_MESES_TIPICO,
    "permanencia_viveiro_meses_max": PERMANENCIA_VIVEIRO_MESES_MAX,
    "rega_germinacao_vezes_dia": REGA_GERMINACAO_VEZES_DIA,
    "rega_rustificacao_vezes_dia": REGA_RUSTIFICACAO_VEZES_DIA,
    "coleta_fracao_maxima_arvore": COLETA_FRACAO_MAXIMA_POR_ARVORE,
}

# Compatibilidade com imports antigos
FONTE_MANUAL = FONTE_SISTEMA
