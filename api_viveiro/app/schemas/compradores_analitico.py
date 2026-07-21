from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ClienteAnaliticoResumo(BaseModel):
    periodo_meses: int
    periodo_label: str
    total_clientes_cadastro: int
    clientes_com_compra: int
    clientes_com_compra_periodo: int
    receita_periodo: float = 0
    custo_periodo: float = 0
    lucro_periodo: float = 0
    margem_media_pct: Optional[float] = None
    mudas_vendidas_periodo: int = 0
    ticket_medio_periodo: Optional[float] = None
    receita_pendente: float = 0
    clientes_recorrentes: int = 0
    clientes_atencao: int = 0


class ClienteAnaliticoItem(BaseModel):
    id: int
    nome: str
    tipo: str
    cidade: Optional[str] = None
    estado: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    vendas_periodo: int = 0
    vendas_historico: int = 0
    receita_periodo: float = 0
    custo_periodo: float = 0
    lucro_periodo: float = 0
    margem_pct: Optional[float] = None
    mudas_periodo: int = 0
    ticket_medio: Optional[float] = None
    receita_pendente: float = 0
    ultima_compra: Optional[datetime] = None
    primeira_compra: Optional[datetime] = None
    dias_desde_ultima: Optional[int] = None
    status_relacionamento: str = "lead"


class ClienteRankingItem(BaseModel):
    id: int
    nome: str
    tipo: str
    cidade: Optional[str] = None
    estado: Optional[str] = None
    valor: float
    valor_secundario: Optional[float] = None
    label_secundario: Optional[str] = None


class ClienteGeoItem(BaseModel):
    chave: str
    uf: Optional[str] = None
    clientes: int = 0
    receita: float = 0
    mudas: int = 0


class ClienteTipoItem(BaseModel):
    tipo: str
    clientes: int = 0
    receita: float = 0
    lucro: float = 0


class CompradoresAnaliticoOut(BaseModel):
    mostrar_resumo_financeiro: bool = False
    resumo: ClienteAnaliticoResumo
    rankings: dict = Field(default_factory=dict)
    por_uf: List[ClienteGeoItem] = Field(default_factory=list)
    por_cidade: List[ClienteGeoItem] = Field(default_factory=list)
    por_tipo: List[ClienteTipoItem] = Field(default_factory=list)
    clientes: List[ClienteAnaliticoItem] = Field(default_factory=list)
