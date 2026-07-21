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
    valor_total: Optional[float] = None
    custo_unitario: Optional[float] = None
    status: str
    condicoes_armazenamento: Optional[str] = None
    data_formacao_lote: Optional[str] = None
    data_coleta: Optional[str] = None
    dias_armazenamento: Optional[int] = None
    percentual_consumido: Optional[float] = None
    ultimo_teste_germinacao: Optional[float] = None
    beneficiamento: Optional[str] = None
    observacoes: Optional[str] = None


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
    descricao: Optional[str] = None
    data_ultima_compra: Optional[str] = None
    ultima_movimentacao: Optional[str] = None
    qtd_movimentacoes: int = 0
    alerta_estoque: Optional[str] = None  # abaixo_minimo | acima_maximo


class EstoquePorEspecieItem(BaseModel):
    id_especie: int
    nome_popular: Optional[str] = None
    nome_cientifico: str
    quantidade_total: int
    quantidade_comercial: int = 0
    quantidade_desenvolvimento: int = 0
    quantidade_rustificacao: int = 0
    custo_medio: float = 0
    valor_custo_total: float = 0
    dias_viveiro_medio: Optional[float] = None
    dias_viveiro_min: Optional[int] = None
    dias_viveiro_max: Optional[int] = None
    dias_rustificacao_medio: Optional[float] = None
    dias_rustificacao_min: Optional[int] = None
    dias_rustificacao_max: Optional[int] = None


class EstoquePorIdadeItem(BaseModel):
    faixa: str
    quantidade: int
    percentual: float = 0
    custo_medio: float = 0
    valor_custo_total: float = 0


class EstoqueEspecieIdadeItem(BaseModel):
    id_especie: int
    nome_popular: Optional[str] = None
    nome_cientifico: str
    faixa: str
    quantidade: int
    custo_medio: float = 0
    valor_custo_total: float = 0


class EstoqueAnaliticoMudas(BaseModel):
    metrica_idade: str = "viveiro"
    faixas: List[str] = []
    totais: dict = {}
    por_especie: List[EstoquePorEspecieItem] = []
    por_idade: List[EstoquePorIdadeItem] = []
    especie_idade: List[EstoqueEspecieIdadeItem] = []


class CmvIntegridadeResumo(BaseModel):
    insumos_metodo: str
    mudas_metodo: str
    sementes_metodo: str
    venda_cmv: str
    plantas_vivas: int = 0
    plantas_com_custo: int = 0
    plantas_sem_custo: int = 0
    alertas: List[str] = []


class EstoqueAnaliticoPlantaDetalhe(BaseModel):
    id: int
    codigo_rastreio: Optional[str] = None
    id_especie: int
    nome_popular: Optional[str] = None
    nome_cientifico: Optional[str] = None
    id_lote_sementes: Optional[int] = None
    codigo_lote: Optional[str] = None
    canteiro_nome: Optional[str] = None
    tipo_local: Optional[str] = None
    estagio_producao: Optional[str] = None
    status: Optional[str] = None
    data_plantio: Optional[str] = None
    dias_viveiro: int = 0
    dias_rustificacao: Optional[int] = None
    dias_metrica: Optional[int] = None
    faixa_idade: Optional[str] = None
    custo_atual: float = 0
    preco_venda: float = 0
    comercial: bool = False


class EstoqueAnaliticoLoteDetalhe(BaseModel):
    id_lote_sementes: Optional[int] = None
    codigo_lote: str
    quantidade: int
    dias_metrica_min: Optional[int] = None
    dias_metrica_max: Optional[int] = None
    dias_metrica_medio: Optional[float] = None
    valor_custo_total: float = 0
    plantas: List[EstoqueAnaliticoPlantaDetalhe] = []


class EstoqueAnaliticoDetalheOut(BaseModel):
    metrica_idade: str
    agrupar: str
    total_mudas: int
    total_lotes: Optional[int] = None
    titulo_filtro: Optional[str] = None
    itens_muda: List[EstoqueAnaliticoPlantaDetalhe] = []
    itens_lote: List[EstoqueAnaliticoLoteDetalhe] = []


class TimelineEtapaItem(BaseModel):
    dias_medio: Optional[float] = None
    amostras: int = 0
    label: str
    cor: str
    percentual_timeline: float = 0


class TimelineEspecieItem(BaseModel):
    id_especie: int
    nome_popular: Optional[str] = None
    nome_cientifico: str
    quantidade_plantas: int = 0
    onde_agora: dict = {}
    etapas: dict = {}
    ciclo_total_medio: Optional[float] = None


class EstoqueTimelineOut(BaseModel):
    etapas_ordem: List[str]
    filtro_id_especie: Optional[int] = None
    resumo_global: dict
    especies: List[TimelineEspecieItem] = []


class EstoqueComercialItem(BaseModel):
    id_especie: int
    nome_popular: Optional[str] = None
    nome_cientifico: str
    quantidade: int
    valor_unitario: float
    custo_medio: float = 0
    valor_estoque_especie: float = 0
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


class CmvDetalheEstagioItem(BaseModel):
    estagio: str
    estagio_label: str
    quantidade: int
    valor_total: float
    custo_medio: float


class CmvDetalheComposicaoUnitario(BaseModel):
    sementes: float = 0
    insumos: float = 0
    indireto: float = 0


class CmvDetalheItemCusteio(BaseModel):
    origem: str
    chave: str
    descricao: str
    valor_total: float
    valor_unitario: float = 0


class CmvDetalheSemeaduraItem(BaseModel):
    id_semeadura: int
    data_semeadura: Optional[str] = None
    codigo_lote: Optional[str] = None
    quantidade_no_escopo: int
    quantidade_semeadura: int
    custo_unitario_muda: float = 0
    valor_total: float = 0
    composicao_unitario: CmvDetalheComposicaoUnitario
    composicao_total_escopo: CmvDetalheComposicaoUnitario
    mudas_base_rateio: Optional[int] = None
    itens_custeio: List[CmvDetalheItemCusteio] = []


class CmvDetalheComposicaoAgregada(BaseModel):
    chave: str
    origem: str
    descricao: str
    valor_total: float
    valor_unitario_medio: float = 0


class CmvDetalheResumoCalculo(BaseModel):
    custo_base_semeadura: float = 0
    ajustes_pos_semeadura: float = 0
    valor_total: float = 0


class CmvDetalheAjustes(BaseModel):
    atividades: float = 0
    outros: float = 0
    total: float = 0


class EstoqueCmvDetalheOut(BaseModel):
    id_especie: int
    nome_popular: Optional[str] = None
    nome_cientifico: str
    escopo: str
    escopo_label: str
    quantidade: int
    valor_total: float
    custo_medio: float
    formula: str
    resumo_calculo: CmvDetalheResumoCalculo
    por_estagio: List[CmvDetalheEstagioItem] = []
    por_semeadura: List[CmvDetalheSemeaduraItem] = []
    composicao_agregada: List[CmvDetalheComposicaoAgregada] = []
    ajustes_pos_semeadura: CmvDetalheAjustes
    observacoes: List[str] = []


class EstoqueResumoGeral(BaseModel):
    total_lotes_sementes_ativos: int
    total_sementes_disponiveis: int
    total_plantas_sementeira: int
    total_plantas_canteiro: int
    total_insumos: int
    total_mudas_aptas_venda: int = 0
    valor_total_insumos: float = 0
    valor_total_sementes: float = 0
    valor_total_mudas: float = 0
    valor_mudas_comercial: float = 0
    mudas_pipeline: MudasPipelineResumo
    capacidades_viveiro: dict = {}
    estoque_comercial: List[EstoqueComercialItem] = []
    analitico_mudas: EstoqueAnaliticoMudas
    analitico_mudas_rustificacao: EstoqueAnaliticoMudas
    cmv_integridade: CmvIntegridadeResumo
    timeline_especies: EstoqueTimelineOut
    lotes_sementes: List[EstoqueSementesItem]
    insumos: List[EstoqueInsumoItem]
