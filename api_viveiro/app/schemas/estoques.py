from typing import List, Optional

from pydantic import BaseModel


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
    valor_estoque: float = 0
    estoque_minimo: float = 0
    estoque_maximo: Optional[float] = None
    fornecedor: Optional[str] = None
    alerta_estoque: Optional[str] = None  # abaixo_minimo | acima_maximo


class EstoqueComercialItem(BaseModel):
    id_especie: int
    nome_popular: Optional[str] = None
    nome_cientifico: str
    quantidade: int
    valor_unitario: float
    localizacao: Optional[str] = None
    status_predominante: Optional[str] = None
    estagio_comercial: str = "apta_venda"


class MudasPipelineResumo(BaseModel):
    dias_minimos_rustificacao: int = 30
    em_desenvolvimento_sementeira: int = 0
    em_desenvolvimento_canteiro: int = 0
    em_desenvolvimento_total: int = 0
    em_rustificacao: int = 0
    aptas_venda_aguardando_tempo: int = 0
    prontas_para_venda: int = 0


class EstoqueResumoGeral(BaseModel):
    total_lotes_sementes_ativos: int
    total_sementes_disponiveis: int
    total_plantas_sementeira: int
    total_plantas_canteiro: int
    total_insumos: int
    total_mudas_aptas_venda: int = 0
    valor_total_insumos: float = 0
    mudas_pipeline: MudasPipelineResumo
    estoque_comercial: List[EstoqueComercialItem] = []
    lotes_sementes: List[EstoqueSementesItem]
    insumos: List[EstoqueInsumoItem]
