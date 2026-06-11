from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, root_validator, validator

TIPOS_ORIGEM = (
    "plantada",
    "fragmento_floresta",
    "app",
    "reserva_legal",
    "rppn",
    "remanescente",
    "plantio_experimental",
    "outro",
)

ESTAGIOS_FRUTIFICACAO = (
    "pre_floracao",
    "floracao",
    "fruto_verde",
    "fruto_maduro",
    "fruto_seco",
    "dispersao",
    "outro",
)


class ArvoreMatrizBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    id_especie: int
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, max_length=2)
    municipio: Optional[str] = None
    imovel_nome: Optional[str] = None
    tipo_origem: Optional[str] = None
    numero_autorizacao: Optional[str] = None
    observacoes_legais: Optional[str] = None
    mes_inicio_frutificacao: Optional[int] = Field(None, ge=1, le=12)
    mes_fim_frutificacao: Optional[int] = Field(None, ge=1, le=12)
    estagio_frutificacao: Optional[str] = None
    fenologia_observacoes: Optional[str] = None
    tipo_coordenada: str = "geografica"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    utm_zona: Optional[int] = Field(None, ge=1, le=60)
    utm_easting: Optional[float] = None
    utm_northing: Optional[float] = None
    observacoes: Optional[str] = None

    @validator("tipo_coordenada")
    def validar_tipo_coordenada(cls, v):
        if v not in ("geografica", "utm"):
            raise ValueError("tipo_coordenada deve ser 'geografica' ou 'utm'")
        return v

    @validator("tipo_origem")
    def validar_tipo_origem(cls, v):
        if v is not None and v not in TIPOS_ORIGEM:
            raise ValueError(f"tipo_origem deve ser um de: {', '.join(TIPOS_ORIGEM)}")
        return v

    @root_validator
    def validar_coordenadas(cls, values):
        tipo = values.get("tipo_coordenada") or "geografica"
        if tipo == "geografica":
            if values.get("latitude") is None or values.get("longitude") is None:
                raise ValueError("Informe latitude e longitude")
        else:
            if not all(values.get(k) is not None for k in ("utm_zona", "utm_easting", "utm_northing")):
                raise ValueError("Informe zona UTM, easting e northing")
        return values


class ArvoreMatrizCreate(ArvoreMatrizBase):
    pass


class ArvoreMatrizUpdate(BaseModel):
    nome: Optional[str] = None
    id_especie: Optional[int] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    municipio: Optional[str] = None
    imovel_nome: Optional[str] = None
    tipo_origem: Optional[str] = None
    numero_autorizacao: Optional[str] = None
    observacoes_legais: Optional[str] = None
    mes_inicio_frutificacao: Optional[int] = Field(None, ge=1, le=12)
    mes_fim_frutificacao: Optional[int] = Field(None, ge=1, le=12)
    estagio_frutificacao: Optional[str] = None
    fenologia_observacoes: Optional[str] = None
    tipo_coordenada: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    utm_zona: Optional[int] = None
    utm_easting: Optional[float] = None
    utm_northing: Optional[float] = None
    observacoes: Optional[str] = None


class ArvoreMatrizOut(BaseModel):
    id: int
    nome: str
    id_especie: int
    especie_nome: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    municipio: Optional[str] = None
    imovel_nome: Optional[str] = None
    tipo_origem: Optional[str] = None
    numero_autorizacao: Optional[str] = None
    observacoes_legais: Optional[str] = None
    mes_inicio_frutificacao: Optional[int] = None
    mes_fim_frutificacao: Optional[int] = None
    estagio_frutificacao: Optional[str] = None
    fenologia_observacoes: Optional[str] = None
    latitude: float
    longitude: float
    tipo_coordenada: str
    utm_zona: Optional[int] = None
    utm_easting: Optional[float] = None
    utm_northing: Optional[float] = None
    sementes_coletadas: int
    taxa_germinacao: Optional[float] = None
    data_ultima_coleta: Optional[date] = None
    observacoes: Optional[str] = None
    data_cadastro: datetime
    total_coletas: int = 0
    total_lotes: int = 0

    class Config:
        orm_mode = True
