"""Estágios do pipeline de produção florestal (mudas plantadas)."""

ENTRADA_MATERIAL = "entrada_material"
CASA_VEGETACAO = "casa_vegetacao"
ENDURECIMENTO = "endurecimento"
EXPEDICAO = "expedicao"
DESCARTADO = "descartado"

ESTAGIOS_FLORESTAL = (
    ENTRADA_MATERIAL,
    CASA_VEGETACAO,
    ENDURECIMENTO,
    EXPEDICAO,
    DESCARTADO,
)

ESTAGIOS_ATIVOS = frozenset({ENTRADA_MATERIAL, CASA_VEGETACAO, ENDURECIMENTO, EXPEDICAO})

TRANSICOES_VALIDAS: dict[str, frozenset[str]] = {
    ENTRADA_MATERIAL: frozenset({CASA_VEGETACAO, DESCARTADO}),
    CASA_VEGETACAO: frozenset({ENDURECIMENTO, DESCARTADO}),
    ENDURECIMENTO: frozenset({EXPEDICAO, DESCARTADO}),
    EXPEDICAO: frozenset(),
    DESCARTADO: frozenset(),
}

ESTAGIO_LABELS = {
    ENTRADA_MATERIAL: "Entrada de material",
    CASA_VEGETACAO: "Casa de vegetação",
    ENDURECIMENTO: "Endurecimento",
    EXPEDICAO: "Expedição",
    DESCARTADO: "Descartado",
}

TIPOS_MOVIMENTACAO = frozenset(
    {"entrada", "transferencia", "perda", "expedicao", "ajuste", "descarte"}
)
