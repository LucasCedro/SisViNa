from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class EspecieContagemOut(BaseModel):
    id_especie: int
    especie: str
    quantidade: int


class VendaRecenteOut(BaseModel):
    id: int
    data_venda: datetime
    comprador_nome: Optional[str] = None
    total_itens: int
    status: str


class ProducaoResumoOut(BaseModel):
    sementes_armazem: int
    lotes_com_estoque: int
    na_sementeira: int
    em_desenvolvimento_sementeira: int
    aptas_transferencia: int
    nos_canteiros: int
    em_crescimento_canteiro: int
    aptas_rustificacao_canteiro: int
    na_rustificacao: int
    em_rustificacao: int
    prontas_venda: int
    prontas_venda_canteiro: int
    prontas_venda_rustificacao: int
    estoque_comercial_unidades: int
    aguardando_transferencia: int
    vendidas_mtd: int
    vendidas_ytd: int
    dias_medios_armazem: Optional[float] = None
    dias_medios_sementeira: Optional[float] = None
    dias_medios_canteiro: Optional[float] = None
    dias_medios_rustificacao: Optional[float] = None
    por_especie_sementeira: List[EspecieContagemOut]
    por_especie_desenvolvimento: List[EspecieContagemOut]
    por_especie_aptas_transferencia: List[EspecieContagemOut]
    por_especie_canteiro: List[EspecieContagemOut]
    por_especie_em_crescimento: List[EspecieContagemOut]
    por_especie_aptas_rustificacao: List[EspecieContagemOut]
    por_especie_rustificacao: List[EspecieContagemOut]
    por_especie_prontas_venda: List[EspecieContagemOut]
    vendas_recentes: List[VendaRecenteOut]
