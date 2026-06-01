from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class PromoverMudasRequest(BaseModel):
    ids_plantas: List[int] = Field(..., min_items=1)
    id_canteiro_destino: int
    data_germinacao: Optional[date] = None
    observacoes: Optional[str] = None


class PromoverMudasResponse(BaseModel):
    transferidas: int
    ids_plantas: List[int]


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
