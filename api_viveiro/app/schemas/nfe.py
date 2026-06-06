from datetime import datetime
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, Field, validator, root_validator

from app.utils.fiscal import normalize_ncm, validate_ncm


class RegraFiscalBase(BaseModel):
    """Parâmetros definidos pelo contador — o sistema só executa."""

    nome: Optional[str] = Field(None, description="Rótulo para o cockpit (ex.: GO interno muda)")
    ncm: str
    uf_origem: str = Field(..., min_length=2, max_length=2)
    uf_destino: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description="UF, *, INTERNA, INTERESTADUAL ou lista SP,MG,ES",
    )
    tipo_cliente: str = "ANY"
    cfop_base: str = Field(
        ...,
        min_length=4,
        max_length=4,
        description="CFOP escolhido pelo contador (5101, 6101, etc.)",
    )
    ajustar_cfop_por_uf: bool = Field(
        True,
        description="Se True, ajusta 1º dígito 5/6 conforme UF origem×destino",
    )
    csosn: str = Field(..., min_length=3, max_length=3)
    descricao_produto: Optional[str] = None
    unidade_comercial: str = "UN"
    natureza_operacao: str = "Venda de mudas"
    isento_icms: bool = False
    reducao_bc_icms_percent: Optional[float] = Field(
        None, ge=0, le=100, description="Ex.: 60 para Conv. ICMS 100/97 interestadual"
    )
    fundamento_legal: Optional[str] = None
    informacoes_complementares: Optional[str] = None
    pis_situacao_tributaria: Optional[str] = None
    cofins_situacao_tributaria: Optional[str] = None
    local_destino: Optional[int] = Field(None, description="1 interna, 2 interestadual, 3 exterior")
    cbenef: Optional[str] = None
    aplicar_difal: bool = False
    aliquota_icms_inter: Optional[float] = None
    aliquota_icms_intra: Optional[float] = None
    tipo_operacao: str = Field(
        "domestica",
        description="domestica | importacao (origem estrangeira SN) | exterior",
    )
    icms_origem: int = Field(
        0,
        ge=0,
        le=8,
        description="0=nacional; 1=importação direta; 2=adquirida no mercado interno; …",
    )
    aliquota_icms_importacao: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Alíquota referência ICMS importação SN (exceção ao DAS)",
    )
    observacao: Optional[str] = None
    ativo: bool = True
    ordem: int = 0

    @validator("cfop_base")
    def cfop_digitos(cls, v):
        if not v.isdigit() or len(v) != 4:
            raise ValueError("CFOP deve ter 4 dígitos numéricos")
        return v

    @validator("local_destino")
    def local_destino_ok(cls, v):
        if v is not None and v not in (1, 2, 3):
            raise ValueError("local_destino deve ser 1, 2 ou 3")
        return v

    @validator("ncm")
    def validar_ncm(cls, v):
        if not validate_ncm(v):
            raise ValueError("NCM inválido — 8 dígitos numéricos")
        return normalize_ncm(v)

    @validator("uf_origem", "uf_destino")
    def uf_upper(cls, v):
        if not v:
            return v
        v = v.strip()
        if v == "*":
            return v
        if v.upper() in ("INTERNA", "INTERESTADUAL"):
            return v.upper()
        if "," in v:
            return ",".join(p.strip().upper() for p in v.split(",") if p.strip())
        return v.upper()

    @validator("tipo_cliente")
    def tipo_ok(cls, v):
        v = (v or "ANY").upper()
        if v not in ("PF", "PJ", "ANY"):
            raise ValueError("tipo_cliente deve ser PF, PJ ou ANY")
        return v

    @validator("csosn")
    def csosn_ok(cls, v):
        if not v.isdigit() or len(v) != 3:
            raise ValueError("CSOSN deve ter 3 dígitos (Simples Nacional)")
        return v

    @validator("tipo_operacao")
    def tipo_operacao_ok(cls, v):
        v = (v or "domestica").lower()
        if v not in ("domestica", "importacao", "exterior"):
            raise ValueError("tipo_operacao deve ser domestica, importacao ou exterior")
        return v

    @root_validator
    def validar_cenario_operacao(cls, values):
        top = (values.get("tipo_operacao") or "domestica").lower()
        if top == "importacao" and int(values.get("icms_origem") or 0) < 1:
            raise ValueError("Importação exige icms_origem >= 1 (origem estrangeira na NF-e)")
        if top == "exterior" and (values.get("uf_destino") or "").upper() not in (
            "EX",
            "EXTERIOR",
            "INTERNA",
            "INTERESTADUAL",
            "*",
        ):
            pass  # contador pode usar EXTERIOR como padrão ao salvar template
        return values

    @root_validator
    def fundamento_quando_isento_ou_reducao(cls, values):
        isento = values.get("isento_icms")
        reducao = values.get("reducao_bc_icms_percent")
        fund = (values.get("fundamento_legal") or "").strip()
        if isento and not fund:
            raise ValueError(
                "Isenção de ICMS exige Fundamento legal (informações complementares da NF-e)."
            )
        if reducao is not None and float(reducao) > 0 and not fund:
            raise ValueError(
                "Redução de BC ICMS exige Fundamento legal nas informações complementares da NF-e."
            )
        return values


class RegraFiscalUpdate(BaseModel):
    nome: Optional[str] = None
    ncm: Optional[str] = None
    uf_origem: Optional[str] = None
    uf_destino: Optional[str] = None
    tipo_cliente: Optional[str] = None
    cfop_base: Optional[str] = None
    ajustar_cfop_por_uf: Optional[bool] = None
    csosn: Optional[str] = None
    descricao_produto: Optional[str] = None
    unidade_comercial: Optional[str] = None
    natureza_operacao: Optional[str] = None
    isento_icms: Optional[bool] = None
    reducao_bc_icms_percent: Optional[float] = None
    fundamento_legal: Optional[str] = None
    informacoes_complementares: Optional[str] = None
    pis_situacao_tributaria: Optional[str] = None
    cofins_situacao_tributaria: Optional[str] = None
    local_destino: Optional[int] = None
    cbenef: Optional[str] = None
    aplicar_difal: Optional[bool] = None
    aliquota_icms_inter: Optional[float] = None
    aliquota_icms_intra: Optional[float] = None
    tipo_operacao: Optional[str] = None
    icms_origem: Optional[int] = None
    aliquota_icms_importacao: Optional[float] = None
    observacao: Optional[str] = None
    ativo: Optional[bool] = None
    ordem: Optional[int] = None


class RegraFiscalOut(RegraFiscalBase):
    id: int

    class Config:
        orm_mode = True


class NotaFiscalItemOut(BaseModel):
    numero_item: int
    descricao: str
    ncm: str
    cfop: str
    csosn: str
    unidade: str
    quantidade: float
    valor_unitario: float
    valor_total: float

    class Config:
        orm_mode = True


class NotaFiscalOut(BaseModel):
    id: int
    id_venda: int
    ref_externa: str
    chave_acesso: Optional[str]
    numero: Optional[int]
    serie: Optional[int]
    status: str
    cstat: Optional[str]
    xmotivo: Optional[str]
    recibo: Optional[str]
    url_xml: Optional[str]
    url_danfe: Optional[str]
    difal_snapshot: Optional[Dict[str, Any]]
    data_emissao: Optional[datetime]
    itens: List[NotaFiscalItemOut] = []

    class Config:
        orm_mode = True


class EmitirNfeOut(BaseModel):
    nota: NotaFiscalOut
    mensagem: str


class NotaFiscalListOut(NotaFiscalOut):
    comprador_nome: str
    valor_venda: float
    status_venda: str
    data_venda: Optional[datetime] = None


class ResumoFiscalOut(BaseModel):
    total_notas: int
    por_status: Dict[str, int]
    vendas_sem_nfe: int
    valor_autorizado: float


class VendaPendenteNfeOut(BaseModel):
    id: int
    data_venda: Optional[datetime]
    valor_total: float
    status: str
    comprador_nome: str


class AmbienteNfeOut(BaseModel):
    ambiente_emitente: str
    producao_permitida_sistema: bool
    focus_token_configurado: bool
    modo_mock: bool
    mensagem: str


class RegraFiscalPreviewOut(BaseModel):
    encontrada: bool
    uf_origem: str
    uf_destino: str
    tipo_operacao: str = "domestica"
    operacao: str
    cfop_resolvido: Optional[str] = None
    regra: Optional[RegraFiscalOut] = None
    mensagem: Optional[str] = None
    isento_icms: bool = False
    reducao_bc_icms_percent: Optional[float] = None
    aplicar_difal: bool = False
    aliquota_icms_inter: Optional[float] = None
    aliquota_icms_intra: Optional[float] = None
    icms_origem: int = 0
    aliquota_icms_importacao: Optional[float] = None
    difal_aplicavel: bool = False
    importacao_aplicavel: bool = False
    tributacao_resumo: Optional[str] = None


class CompradorNfeReadinessOut(BaseModel):
    pronto: bool
    faltando: List[str] = []


class NfeWebhookPayload(BaseModel):
    """Payload genérico de callback (Focus NFe e similares)."""
    ref: Optional[str] = None
    status: Optional[str] = None
    status_sefaz: Optional[str] = None
    mensagem_sefaz: Optional[str] = None
    chave_nfe: Optional[str] = None
    caminho_xml_nota_fiscal: Optional[str] = None
    caminho_danfe: Optional[str] = None
    cnpj_emitente: Optional[str] = None

    class Config:
        extra = "allow"
