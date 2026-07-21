from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.financeiro import DrePeriodoOut, EstoqueFinanceiroOut, PeriodoOut


class BalancoGrupoOut(BaseModel):
    estoque_mudas: Optional[float] = None
    estoque_insumos: Optional[float] = None
    estoque_sementes: Optional[float] = None
    contas_receber: Optional[float] = None
    total: float = 0


class BalancoPatrimonialOut(BaseModel):
    periodo: PeriodoOut
    data_referencia: str
    ativo: Dict[str, object]
    passivo: Dict[str, object]
    patrimonio_liquido_grupo: Optional[Dict[str, object]] = None
    patrimonio_liquido: float = 0
    passivo_mais_pl: float = 0
    resultado_periodo: float = 0
    estoque_detalhe: EstoqueFinanceiroOut
    detalhes: Optional[Dict[str, object]] = None
    observacoes: List[str] = Field(default_factory=list)


class LivroCaixaMovimentoOut(BaseModel):
    id: int
    data: str
    descricao: str
    valor: float = 0
    forma_pagamento: Optional[str] = None
    status: Optional[str] = None
    categoria: Optional[str] = None


class LivroCaixaOut(BaseModel):
    periodo: PeriodoOut
    entradas: List[LivroCaixaMovimentoOut] = Field(default_factory=list)
    saidas_operacionais: List[LivroCaixaMovimentoOut] = Field(default_factory=list)
    saidas: List[LivroCaixaMovimentoOut] = Field(default_factory=list)
    total_entradas: float = 0
    total_saidas_operacionais: float = 0
    total_saidas_investimento: float = 0
    total_saidas: float = 0
    saldo_periodo: float = 0
    detalhes: Optional[Dict[str, object]] = None
    observacoes: List[str] = Field(default_factory=list)


class LivroInventarioOut(BaseModel):
    periodo: PeriodoOut
    data_referencia: str
    resumo: Dict[str, object]
    insumos: List[Dict[str, object]] = Field(default_factory=list)
    sementes: List[Dict[str, object]] = Field(default_factory=list)
    detalhes: Optional[Dict[str, object]] = None
    observacoes: List[str] = Field(default_factory=list)


class NotaExplicativaSecaoOut(BaseModel):
    titulo: str
    texto: str


class NotasExplicativasOut(BaseModel):
    periodo: PeriodoOut
    regime: str = "competencia"
    secoes: List[NotaExplicativaSecaoOut] = Field(default_factory=list)
    dre_resumo: DrePeriodoOut
    balanco_resumo: Dict[str, float] = Field(default_factory=dict)
