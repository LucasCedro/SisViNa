from typing import List, Optional
from pydantic import BaseModel, Field, validator


class EstoqueSementesItem(BaseModel):
    id: int
    codigo_lote: str
    origem_lote: str
    id_especie: int
    especie_nome: Optional[str] = None
    matriz_nome: Optional[str] = None
    quantidade_disponivel: int
    quantidade_inicial: int
    status: str
    condicoes_armazenamento: Optional[str] = None


class EstoqueInsumoItem(BaseModel):
    id: int
    nome: str
    tipo: Optional[str] = None
    unidade_medida: Optional[str] = None
    quantidade_estoque: float
    preco_unitario: Optional[float] = None
    fornecedor: Optional[str] = None


class EstoqueResumoGeral(BaseModel):
    total_lotes_sementes_ativos: int
    total_sementes_disponiveis: int
    total_plantas_sementeira: int
    total_plantas_canteiro: int
    total_insumos: int
    lotes_sementes: List[EstoqueSementesItem]
    insumos: List[EstoqueInsumoItem]

