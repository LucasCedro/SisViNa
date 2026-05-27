"""Estágios operacionais da muda — independentes do status biológico (SEMENTE, MUDA…)."""

EM_DESENVOLVIMENTO = "em_desenvolvimento"
APTA_TRANSFERENCIA = "apta_transferencia"
EM_CRESCIMENTO = "em_crescimento"
APTA_RUSTIFICACAO = "apta_rustificacao"
EM_RUSTIFICACAO = "em_rustificacao"
APTA_VENDA = "apta_venda"

ESTAGIOS_VALIDOS = (
    EM_DESENVOLVIMENTO,
    APTA_TRANSFERENCIA,
    EM_CRESCIMENTO,
    APTA_RUSTIFICACAO,
    EM_RUSTIFICACAO,
    APTA_VENDA,
)

ESTAGIO_INICIAL_SEMENTEIRA = EM_DESENVOLVIMENTO
ESTAGIO_INICIAL_CANTEIRO = EM_CRESCIMENTO
ESTAGIO_INICIAL_RUSTIFICACAO = EM_RUSTIFICACAO

TIPOS_LOCAL_PRODUCAO = ("sementeira", "canteiro", "rustificacao", "armazem")
