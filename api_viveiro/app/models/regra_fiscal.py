from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, func

from app.database import Base


class RegraFiscal(Base):
    """
    Parâmetros fiscais definidos pelo contador (cockpit).
    O sistema aplica a regra; não define tributação por conta própria.
    CRT Simples: CSOSN no item (nunca CST de ICMS).
    """

    __tablename__ = "regras_fiscais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120))
    ncm = Column(String(8), nullable=False, index=True)
    uf_origem = Column(String(2), nullable=False)
    uf_destino = Column(String(80), nullable=False)  # UF | * | INTERNA | INTERESTADUAL | SP,MG,ES
    tipo_cliente = Column(String(10), nullable=False, default="ANY")  # PF | PJ | ANY
    cfop_base = Column(String(4), nullable=False)  # CFOP escolhido pelo contador (ex.: 5101, 6101)
    ajustar_cfop_por_uf = Column(Boolean, default=True)  # se True, ajusta 5↔6 conforme UF orig/dest
    csosn = Column(String(3), nullable=False)
    descricao_produto = Column(String(200))
    unidade_comercial = Column(String(6), nullable=False, default="UN")
    natureza_operacao = Column(String(60), default="Venda de mudas")
    isento_icms = Column(Boolean, default=False)
    reducao_bc_icms_percent = Column(Numeric(5, 2))  # ex.: 60 Conv. 100/97 interestadual
    fundamento_legal = Column(Text)
    informacoes_complementares = Column(Text)  # infAdic / observações na NF-e
    pis_situacao_tributaria = Column(String(3))
    cofins_situacao_tributaria = Column(String(3))
    local_destino = Column(Integer)  # 1 interna, 2 interestadual, 3 exterior (Focus/MOC)
    cbenef = Column(String(10))
    aplicar_difal = Column(Boolean, default=False)
    aliquota_icms_inter = Column(Numeric(5, 2))
    aliquota_icms_intra = Column(Numeric(5, 2))
    # Simples Nacional — exceções ao ICMS unificado: importação (origem estrangeira)
    tipo_operacao = Column(String(20), nullable=False, default="domestica")
    # 0=nacional; 1=importação direta; 2=adquirida mercado interno; … (NF-e)
    icms_origem = Column(Integer, nullable=False, default=0)
    aliquota_icms_importacao = Column(Numeric(5, 2))
    observacao = Column(Text)
    ativo = Column(Boolean, default=True)
    ordem = Column(Integer, default=0)
    data_atualizacao = Column(DateTime, server_default=func.now(), onupdate=func.now())
