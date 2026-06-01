from typing import List, Optional

from pydantic import BaseModel, Field


class PeriodoOut(BaseModel):
    mes: int
    ano: int
    label: str


class DrePeriodoOut(BaseModel):
    faturamento: float = 0
    cmv: float = 0
    lucro_bruto: float = 0
    margem_bruta_pct: Optional[float] = None
    opex: float = 0
    capex: float = 0
    resultado_operacional: float = 0
    mudas_vendidas: int = 0
    ticket_medio: Optional[float] = None


class EstoqueFinanceiroOut(BaseModel):
    valor_mudas_vivas: float = 0
    mudas_vivas: int = 0
    custo_medio_muda_viva: float = 0
    valor_insumos: float = 0
    total_insumos: int = 0
    valor_sementes: float = 0


class MargemEspecieOut(BaseModel):
    id_especie: int
    nome: str
    quantidade_vendida: int = 0
    receita: float = 0
    cmv: float = 0
    lucro_bruto: float = 0
    margem_pct: Optional[float] = None
    preco_medio: Optional[float] = None
    custo_medio: Optional[float] = None


class AvisoFinanceiroOut(BaseModel):
    tipo: str
    mensagem: str
    id_especie: Optional[int] = None
    codigo_planta: Optional[str] = None


class EvolucaoMensalOut(BaseModel):
    mes: int
    ano: int
    label: str
    faturamento: float = 0
    cmv: float = 0
    lucro_bruto: float = 0


class ReceitaVendaOut(BaseModel):
    id: int
    data_venda: str
    comprador_nome: Optional[str] = None
    total_itens: int = 0
    valor_total: float = 0
    status: str
    forma_pagamento: Optional[str] = None


class DistribuicaoCategoriaOut(BaseModel):
    categoria: str
    valor: float
    porcentagem: float


class DespesasEstimadasOut(BaseModel):
    comissao_estimada: float = 0
    despesas_fixas_mes: float = 0
    total_despesas_estimadas: float = 0
    nota: str = (
        "Despesas (OPEX/comercial) entram na DRE e não compõem o CMV. "
        "Custos de premissas CUSTO entram no custo do lote/muda."
    )


class PainelFinanceiroOut(BaseModel):
    periodo: PeriodoOut
    dre: DrePeriodoOut
    estoque: EstoqueFinanceiroOut
    margem_especies: List[MargemEspecieOut] = Field(default_factory=list)
    avisos: List[AvisoFinanceiroOut] = Field(default_factory=list)
    evolucao_mensal: List[EvolucaoMensalOut] = Field(default_factory=list)
    receitas: List[ReceitaVendaOut] = Field(default_factory=list)
    opex_por_categoria: List[DistribuicaoCategoriaOut] = Field(default_factory=list)
    capex_por_categoria: List[DistribuicaoCategoriaOut] = Field(default_factory=list)
    despesas_estimadas: DespesasEstimadasOut = Field(default_factory=DespesasEstimadasOut)
