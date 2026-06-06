from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, validator

from app.utils.fiscal import only_digits, validate_cnpj


class EmitenteFiscalBase(BaseModel):
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj: str
    inscricao_estadual: str
    crt: int = Field(1, description="1 = Simples Nacional")
    cnae: Optional[str] = None
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    codigo_municipio_ibge: str
    municipio: str
    uf: str = Field(..., min_length=2, max_length=2)
    cep: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    serie_nfe: int = 1
    proximo_numero_nfe: int = 1
    ambiente: str = "homologacao"

    @validator("cnpj")
    def validar_cnpj(cls, v):
        if not validate_cnpj(v):
            raise ValueError("CNPJ do emitente inválido")
        return v

    @validator("codigo_municipio_ibge")
    def validar_ibge(cls, v):
        d = only_digits(v)
        if len(d) != 7:
            raise ValueError("Código IBGE do município deve ter 7 dígitos")
        return d

    @validator("uf")
    def uf_upper(cls, v):
        return v.upper()


class EmitenteFiscalUpdate(EmitenteFiscalBase):
    pass


class EmitenteFiscalOut(EmitenteFiscalBase):
    id: int
    ativo: bool
    data_atualizacao: Optional[datetime]

    class Config:
        orm_mode = True
