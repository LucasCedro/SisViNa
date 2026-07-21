from typing import Any, Dict, List, Optional

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
    opex_comissao: float = 0
    opex_fixo: float = 0
    compras_insumos: float = 0
    capex: float = 0
    resultado_operacional: float = 0
    mudas_vendidas: int = 0
    ticket_medio: Optional[float] = None


class EstoqueFinanceiroOut(BaseModel):
    valor_mudas_vivas: float = 0
    mudas_vivas: int = 0
    custo_medio_muda_viva: float = 0
    valor_mudas_comercial: float = 0
    mudas_comercial: int = 0
    custo_medio_muda_comercial: float = 0
    valor_insumos: float = 0
    total_insumos: int = 0
    valor_sementes: float = 0


class IntegridadeFinanceiraOut(BaseModel):
    lotes_sementes_sem_custo: int = 0
    coletas_sem_horas_campo: int = 0
    lotes_armazem_sem_coleta: int = 0
    premissa_coleta_campo_ok: bool = True
    valor_hora_coleta_campo: float = 0
    mudas_vivas_sem_custo: int = 0


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


class EvolucaoCaixaOut(BaseModel):
    mes: int
    ano: int
    label: str
    entradas: float = 0
    saidas: float = 0
    saldo: float = 0


class DfcGrupoOut(BaseModel):
    entradas: float = 0
    saidas: float = 0
    subtotal: float = 0


class DfcPeriodoOut(BaseModel):
    operacional: DfcGrupoOut
    investimento: DfcGrupoOut
    variacao_caixa: float = 0
    qtd_recebimentos: int = 0
    qtd_compras: int = 0
    ticket_medio_recebido: Optional[float] = None
    a_receber_aberto: float = 0
    qtd_vendas_pendentes: int = 0
    a_receber_periodo: float = 0
    qtd_pendentes_periodo: int = 0
    a_pagar_aberto: float = 0
    qtd_compras_pendentes: int = 0
    a_pagar_periodo: float = 0
    qtd_pendentes_compras_periodo: int = 0
    entradas: List[Dict[str, Any]] = Field(default_factory=list)
    saidas_operacionais: List[Dict[str, Any]] = Field(default_factory=list)
    saidas: List[Dict[str, Any]] = Field(default_factory=list)


class ReceitaVendaOut(BaseModel):
    id: int
    data_venda: str
    data_pagamento: Optional[str] = None
    comprador_nome: Optional[str] = None
    total_itens: int = 0
    valor_total: float = 0
    status: str
    forma_pagamento: Optional[str] = None


class DistribuicaoCategoriaOut(BaseModel):
    categoria: str
    valor: float
    porcentagem: float


class DespesaPremissaItemOut(BaseModel):
    nome: str
    chave: str
    valor: float = 0
    tipo: str
    formula: Optional[str] = None
    base_valor: Optional[float] = None
    base_unidade: Optional[str] = None


class PassoCalculoOut(BaseModel):
    label: str
    valor: float
    operador: Optional[str] = None


class DetalheBlocoOut(BaseModel):
    titulo: str
    formula: str
    total: float = 0
    explicacao: Optional[str] = None
    passos: List[PassoCalculoOut] = Field(default_factory=list)


class CmvItemVendaOut(BaseModel):
    id_item: int
    id_venda: int
    data_venda: str
    comprador_nome: Optional[str] = None
    codigo_rastreio: Optional[str] = None
    especie_nome: str
    quantidade: int = 1
    receita_linha: float = 0
    custo_unitario: float = 0
    cmv_linha: float = 0
    origem_custo: str = "planta_atual"


class DetalheCmvOut(DetalheBlocoOut):
    itens: List[CmvItemVendaOut] = Field(default_factory=list)
    total_itens: int = 0
    truncado: bool = False
    resumo_origem: Dict[str, int] = Field(default_factory=dict)


class DetalheOpexOut(DetalheBlocoOut):
    faturamento_base: float = 0
    itens: List[DespesaPremissaItemOut] = Field(default_factory=list)


class InsumoEstoqueItemOut(BaseModel):
    id: int
    nome: str
    tipo: str
    quantidade_estoque: float = 0
    preco_unitario: float = 0
    valor_estoque: float = 0
    unidade_medida: Optional[str] = None


class LoteSementeItemOut(BaseModel):
    id: int
    codigo_lote: str
    especie_nome: str
    quantidade_disponivel: int = 0
    valor_total: float = 0
    custo_unitario: Optional[float] = None


class LancamentoResumoOut(BaseModel):
    id: int
    descricao: str
    categoria: str
    data_lancamento: str
    valor: float = 0
    forma_pagamento: Optional[str] = None


class CompraInsumoItemOut(BaseModel):
    id: int
    id_insumo: int
    insumo_nome: str
    data_movimento: str
    data_pagamento: Optional[str] = None
    valor_total: float = 0
    status_pagamento: str = "PAGO"
    quantidade: float = 0
    observacao: Optional[str] = None


class DetalheComprasInsumosOut(DetalheBlocoOut):
    itens: List[CompraInsumoItemOut] = Field(default_factory=list)


class DetalheCapexOut(DetalheBlocoOut):
    itens: List[LancamentoResumoOut] = Field(default_factory=list)


class EstoqueDetalhesOut(BaseModel):
    parque: DetalheBlocoOut
    comercial: DetalheBlocoOut
    insumos: DetalheBlocoOut
    insumos_itens: List[InsumoEstoqueItemOut] = Field(default_factory=list)
    sementes: DetalheBlocoOut
    sementes_itens: List[LoteSementeItemOut] = Field(default_factory=list)


class PainelDetalhesOut(BaseModel):
    faturamento: DetalheBlocoOut
    cmv: DetalheCmvOut
    lucro_bruto: DetalheBlocoOut
    compras_insumos: DetalheComprasInsumosOut
    opex: DetalheOpexOut
    resultado: DetalheBlocoOut
    estoque: EstoqueDetalhesOut
    capex: DetalheCapexOut


class DespesasEstimadasOut(BaseModel):
    comissao_estimada: float = 0
    despesas_fixas_mes: float = 0
    total_despesas_estimadas: float = 0
    itens: List[DespesaPremissaItemOut] = Field(default_factory=list)


class PainelFinanceiroOut(BaseModel):
    regime: str = "caixa"
    regime_descricao: Optional[str] = None
    periodo: PeriodoOut
    dre: DrePeriodoOut
    estoque: EstoqueFinanceiroOut
    integridade: IntegridadeFinanceiraOut = Field(default_factory=IntegridadeFinanceiraOut)
    margem_especies: List[MargemEspecieOut] = Field(default_factory=list)
    avisos: List[AvisoFinanceiroOut] = Field(default_factory=list)
    evolucao_mensal: List[EvolucaoMensalOut] = Field(default_factory=list)
    receitas: List[ReceitaVendaOut] = Field(default_factory=list)
    opex_por_categoria: List[DistribuicaoCategoriaOut] = Field(default_factory=list)
    capex_por_categoria: List[DistribuicaoCategoriaOut] = Field(default_factory=list)
    despesas_estimadas: DespesasEstimadasOut = Field(default_factory=DespesasEstimadasOut)
    detalhes: Optional[PainelDetalhesOut] = Field(default=None)
    detalhes_dfc: Optional[Dict[str, Any]] = Field(default=None)
    dfc: Optional[DfcPeriodoOut] = Field(default=None)
    evolucao_caixa: List[EvolucaoCaixaOut] = Field(default_factory=list)
