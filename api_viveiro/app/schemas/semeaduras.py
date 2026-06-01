from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class SemeaduraBase(BaseModel):
    id_lote_sementes: int
    id_canteiro: Optional[int] = None
    data_semeadura: date
    quantidade_sementes_usadas: int = Field(..., gt=0)
    quantidade_mudas_obtidas: Optional[int] = Field(None, ge=0)
    observacoes: Optional[str] = None
    registrar_plantas: bool = False
    quantidade_plantas_registrar: Optional[int] = Field(None, ge=0)


class SemeaduraCreate(SemeaduraBase):
    pass


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
