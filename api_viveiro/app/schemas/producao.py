from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator, validator

MAX_OPERACAO_LOTE_PLANTAS = 25_000
MAX_GRUPOS_OPERACAO_LOTE = 100

ETAPAS_OPERACAO_LOTE = (
    "sementeira_desenvolvimento",
    "sementeira_apta_transferencia",
    "canteiro_crescimento",
    "canteiro_apta_rustificacao",
    "rustificacao",
    "rustificacao_pronta_venda",
    "rustificacao_antes_prazo",
)


class PromoverMudasRequest(BaseModel):
    ids_plantas: List[int] = Field(..., min_items=1)
    id_canteiro_destino: int
    data_germinacao: Optional[date] = None
    observacoes: Optional[str] = None


class BaixaSubstratoResumo(BaseModel):
    insumo_id: int
    insumo_nome: str
    quantidade: float
    unidade: str
    por_muda: float
    detalhe: str


class PromoverMudasResponse(BaseModel):
    transferidas: int
    ids_plantas: List[int]
    avisos: List[str] = Field(default_factory=list)
    baixa_substrato: Optional[BaixaSubstratoResumo] = None


class TransferirRustificacaoRequest(BaseModel):
    ids_plantas: List[int] = Field(..., min_items=1)
    observacoes: Optional[str] = None


class TransferirRustificacaoResponse(BaseModel):
    transferidas: int
    ids_plantas: List[int]
    avisos: List[str] = Field(default_factory=list)


class PlantaPendenteTransferencia(BaseModel):
    id: int
    codigo_rastreio: Optional[str] = None
    id_especie: int
    especie_nome: Optional[str] = None
    id_canteiro: Optional[int] = None
    nome_canteiro: Optional[str] = None
    id_lote_sementes: Optional[int] = None
    codigo_lote: Optional[str] = None
    matriz_nome: Optional[str] = None
    data_plantio: Optional[date] = None
    estagio_producao: Optional[str] = None
    origem: str
    observacoes: Optional[str] = None

    class Config:
        orm_mode = True


class PlantaEmCrescimento(BaseModel):
    id: int
    codigo_rastreio: Optional[str] = None
    id_especie: int
    especie_nome: Optional[str] = None
    id_canteiro: Optional[int] = None
    nome_canteiro: Optional[str] = None
    data_plantio: Optional[date] = None
    data_germinacao: Optional[date] = None
    status: Optional[str] = None
    estagio_producao: Optional[str] = None
    origem: str
    observacoes: Optional[str] = None
    dias_rustificacao: Optional[int] = None
    rustificacao_ok: Optional[bool] = None

    class Config:
        orm_mode = True


class AtualizarEstagioRequest(BaseModel):
    ids_plantas: List[int] = Field(..., min_items=1)
    estagio_producao: str = Field(
        ...,
        description="apta_transferencia | apta_rustificacao | apta_venda",
    )

    @validator("estagio_producao")
    def validate_estagio(cls, v):
        allowed = ["apta_transferencia", "apta_rustificacao", "apta_venda"]
        if v not in allowed:
            raise ValueError(f"Estágio deve ser um de: {', '.join(allowed)}")
        return v


class AtualizarEstagioResponse(BaseModel):
    atualizadas: int
    ids_plantas: List[int]
    avisos: List[str] = Field(
        default_factory=list,
        description="Alertas de parâmetros do viveiro (não bloqueiam a operação).",
    )


class CadastroLotePlantasRequest(BaseModel):
    id_especie: int
    id_canteiro: int
    quantidade: int = Field(..., gt=0, le=500)
    status: str = "MUDA"
    origem: str = "compra"
    id_lote_sementes: Optional[int] = None
    data_plantio: Optional[date] = None
    data_germinacao: Optional[date] = None
    preco_venda: Optional[float] = None
    custo_unitario_compra: Optional[float] = Field(
        None, ge=0, description="Custo unitário na compra de muda (origem=compra)"
    )
    observacoes: Optional[str] = None
    prefixo_codigo: Optional[str] = None

    @validator("status")
    def validate_status(cls, v):
        allowed = ["SEMENTE", "MUDA", "JOVEM", "ADULTA"]
        if v not in allowed:
            raise ValueError(f"Status deve ser um de: {', '.join(allowed)}")
        return v

    @validator("origem")
    def validate_origem(cls, v):
        allowed = ["semeadura", "compra", "doacao", "ajuste"]
        if v not in allowed:
            raise ValueError(f"Origem deve ser um de: {', '.join(allowed)}")
        return v


class CadastroLotePlantasResponse(BaseModel):
    criadas: int
    ids_plantas: List[int]


class GrupoOperacaoLote(BaseModel):
    id_especie: int
    quantidade: int = Field(..., gt=0)
    id_canteiro_origem: Optional[int] = Field(
        None, description="Sementeira ou canteiro de origem (quando há mais de um local)"
    )


class ResumoGrupoOperacao(BaseModel):
    id_especie: int
    especie_nome: str
    id_canteiro: Optional[int] = None
    nome_canteiro: Optional[str] = None
    disponivel: int


class AtualizarEstagioLoteRequest(BaseModel):
    estagio_producao: str = Field(
        ...,
        description="apta_transferencia | apta_rustificacao | apta_venda",
    )
    grupos: List[GrupoOperacaoLote] = Field(..., min_items=1)
    etapa_origem: Optional[str] = Field(
        None,
        description=(
            "Etapa de resolução dos IDs (ex.: rustificacao_pronta_venda, "
            "rustificacao_antes_prazo). Se omitido, usa o padrão do estágio destino."
        ),
    )

    @validator("estagio_producao")
    def validate_estagio(cls, v):
        allowed = ["apta_transferencia", "apta_rustificacao", "apta_venda"]
        if v not in allowed:
            raise ValueError(f"Estágio deve ser um de: {', '.join(allowed)}")
        return v

    @validator("etapa_origem")
    def validate_etapa_origem(cls, v):
        if v is None:
            return v
        if v not in ETAPAS_OPERACAO_LOTE:
            raise ValueError(f"Etapa origem inválida: {v}")
        return v

    @root_validator
    def validar_totais(cls, values):
        grupos = values.get("grupos") or []
        if len(grupos) > MAX_GRUPOS_OPERACAO_LOTE:
            raise ValueError(f"Máximo de {MAX_GRUPOS_OPERACAO_LOTE} grupos por operação.")
        total = sum(g.quantidade for g in grupos)
        if total > MAX_OPERACAO_LOTE_PLANTAS:
            raise ValueError(
                f"Total de plantas ({total}) excede o limite de "
                f"{MAX_OPERACAO_LOTE_PLANTAS:,} por operação."
            )
        return values


class PromoverMudasLoteRequest(BaseModel):
    id_canteiro_destino: int
    data_germinacao: Optional[date] = None
    observacoes: Optional[str] = None
    grupos: List[GrupoOperacaoLote] = Field(..., min_items=1)

    @root_validator
    def validar_totais(cls, values):
        grupos = values.get("grupos") or []
        if len(grupos) > MAX_GRUPOS_OPERACAO_LOTE:
            raise ValueError(f"Máximo de {MAX_GRUPOS_OPERACAO_LOTE} grupos por operação.")
        total = sum(g.quantidade for g in grupos)
        if total > MAX_OPERACAO_LOTE_PLANTAS:
            raise ValueError(
                f"Total de plantas ({total}) excede o limite de "
                f"{MAX_OPERACAO_LOTE_PLANTAS:,} por operação."
            )
        return values


class TransferirRustificacaoLoteRequest(BaseModel):
    observacoes: Optional[str] = None
    grupos: List[GrupoOperacaoLote] = Field(..., min_items=1)

    @root_validator
    def validar_totais(cls, values):
        grupos = values.get("grupos") or []
        if len(grupos) > MAX_GRUPOS_OPERACAO_LOTE:
            raise ValueError(f"Máximo de {MAX_GRUPOS_OPERACAO_LOTE} grupos por operação.")
        total = sum(g.quantidade for g in grupos)
        if total > MAX_OPERACAO_LOTE_PLANTAS:
            raise ValueError(
                f"Total de plantas ({total}) excede o limite de "
                f"{MAX_OPERACAO_LOTE_PLANTAS:,} por operação."
            )
        return values


class OperacaoLoteItemOut(BaseModel):
    id_especie: int
    especie_nome: Optional[str] = None
    quantidade: int
    ids_plantas: List[int] = Field(default_factory=list)


class OperacaoLoteResponse(BaseModel):
    total: int
    itens: List[OperacaoLoteItemOut]
    avisos: List[str] = Field(default_factory=list)
    baixa_substrato: Optional[BaixaSubstratoResumo] = None
