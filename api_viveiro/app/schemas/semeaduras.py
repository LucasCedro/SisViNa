from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator

MAX_SEMEADURA_LOTE_ITENS = 100
MAX_SEMEADURA_LOTE_TOTAL_SEMENTES = 25_000


class SemeaduraBase(BaseModel):
    id_lote_sementes: int
    id_canteiro: Optional[int] = None
    data_semeadura: date
    quantidade_sementes_usadas: int = Field(..., gt=0)
    quantidade_mudas_obtidas: Optional[int] = Field(None, ge=0)
    observacoes: Optional[str] = None
    registrar_plantas: bool = False
    quantidade_plantas_registrar: Optional[int] = Field(None, ge=0)

    @root_validator
    def validar_plantas_iguais_sementes(cls, values):
        registrar = values.get("registrar_plantas")
        qtd_sem = values.get("quantidade_sementes_usadas") or 0
        qtd_plantas = values.get("quantidade_plantas_registrar")

        if registrar:
            if not values.get("id_canteiro"):
                raise ValueError("Informe a sementeira para criar plantas.")
            if qtd_plantas is None or qtd_plantas <= 0:
                raise ValueError(
                    "Com criar plantas ativo, a quantidade de plantas deve ser informada."
                )
            if qtd_plantas != qtd_sem:
                raise ValueError(
                    "A quantidade de plantas deve ser igual à de sementes usadas "
                    f"({qtd_sem}). Cada semente gera um registro SEMENTE na sementeira."
                )
        elif qtd_plantas and qtd_plantas > 0:
            raise ValueError(
                "quantidade_plantas_registrar só pode ser informada com registrar_plantas ativo."
            )

        return values


class SemeaduraCreate(SemeaduraBase):
    pass


class SemeaduraLoteItem(BaseModel):
    id_lote_sementes: int
    quantidade_sementes_usadas: int = Field(..., gt=0)
    observacoes: Optional[str] = None


class SemeaduraLoteCreate(BaseModel):
    data_semeadura: date
    id_canteiro: int
    registrar_plantas: bool = True
    observacoes_gerais: Optional[str] = None
    itens: List[SemeaduraLoteItem] = Field(..., min_items=1)

    @root_validator
    def validar_lote(cls, values):
        itens = values.get("itens") or []
        if len(itens) > MAX_SEMEADURA_LOTE_ITENS:
            raise ValueError(
                f"Máximo de {MAX_SEMEADURA_LOTE_ITENS} lotes por operação."
            )
        ids = [i.id_lote_sementes for i in itens]
        if len(ids) != len(set(ids)):
            raise ValueError("Não repita o mesmo lote na lista.")
        total = sum(i.quantidade_sementes_usadas for i in itens)
        if total > MAX_SEMEADURA_LOTE_TOTAL_SEMENTES:
            raise ValueError(
                f"Total de sementes ({total}) excede o limite de "
                f"{MAX_SEMEADURA_LOTE_TOTAL_SEMENTES:,} por operação."
            )
        if values.get("registrar_plantas") and not values.get("id_canteiro"):
            raise ValueError("Informe a sementeira para criar plantas.")
        return values


class SemeaduraLoteItemOut(BaseModel):
    id_lote_sementes: int
    codigo_lote: str
    especie_nome: Optional[str] = None
    quantidade_sementes_usadas: int
    id_semeadura: int
    plantas_criadas: int


class SemeaduraLoteOut(BaseModel):
    data_semeadura: date
    id_canteiro: int
    canteiro_nome: Optional[str] = None
    total_sementes: int
    total_plantas: int
    itens: List[SemeaduraLoteItemOut]


class SemeaduraUpdate(BaseModel):
    id_canteiro: Optional[int] = None
    data_semeadura: Optional[date] = None
    quantidade_mudas_obtidas: Optional[int] = Field(None, ge=0)
    observacoes: Optional[str] = None


class SemeaduraOut(BaseModel):
    id: int
    id_lote_sementes: int
    codigo_lote: str
    id_arvore_matriz: int
    matriz_nome: str
    id_especie: int
    especie_nome: Optional[str] = None
    id_canteiro: Optional[int] = None
    canteiro_nome: Optional[str] = None
    data_semeadura: date
    data_coleta: Optional[date] = None
    quantidade_sementes_usadas: int
    quantidade_mudas_obtidas: Optional[int] = None
    observacoes: Optional[str] = None
    id_funcionario: int
    funcionario_nome: str
    data_registro: datetime
    plantas_vinculadas: int = 0
    custo_sementes: float = 0
    custo_insumos: float = 0
    custo_indireto: float = 0
    custo_total: float = 0
    custo_unitario_muda: Optional[float] = None

    class Config:
        orm_mode = True


class RastreabilidadePlantaOut(BaseModel):
    id_planta: int
    codigo_rastreio: Optional[str] = None
    status_planta: Optional[str] = None
    data_plantio: Optional[date] = None
    especie_nome: Optional[str] = None
    codigo_lote: Optional[str] = None
    id_lote: Optional[int] = None
    id_coleta: Optional[int] = None
    data_coleta: Optional[date] = None
    id_arvore_matriz: Optional[int] = None
    matriz_nome: Optional[str] = None
    imovel_nome: Optional[str] = None
    municipio: Optional[str] = None
    tipo_origem: Optional[str] = None
    numero_autorizacao: Optional[str] = None
    id_semeadura: Optional[int] = None
    data_semeadura: Optional[date] = None
    quantidade_sementes_usadas: Optional[int] = None
    id_venda: Optional[int] = None
    data_venda: Optional[date] = None
    comprador_nome: Optional[str] = None
    valor_venda: Optional[float] = None
