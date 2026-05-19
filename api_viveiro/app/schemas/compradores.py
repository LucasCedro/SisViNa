# app/schemas/compradores.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator

class CompradorBase(BaseModel):
    tipo: str
    nome: str
    cpf_cnpj: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    usuario: Optional[str] = None
    ativo: Optional[bool] = True

class CompradorCreate(CompradorBase):
    senha: Optional[str] = None

    @validator('tipo')
    def validate_tipo(cls, v):
        if v not in ['PF', 'PJ']:
            raise ValueError('Tipo deve ser PF (Pessoa Física) ou PJ (Pessoa Jurídica)')
        return v
    
    @validator('cpf_cnpj')
    def validate_cpf_cnpj(cls, v, values):
        if 'tipo' in values:
            tipo = values['tipo']
            v_clean = ''.join(c for c in v if c.isdigit())
            
            if tipo == 'PF' and len(v_clean) != 11:
                raise ValueError('CPF deve conter 11 dígitos')
            elif tipo == 'PJ' and len(v_clean) != 14:
                raise ValueError('CNPJ deve conter 14 dígitos')
            
            # Formatar CPF ou CNPJ
            if tipo == 'PF':
                return f"{v_clean[:3]}.{v_clean[3:6]}.{v_clean[6:9]}-{v_clean[9:]}"
            else:  # PJ
                return f"{v_clean[:2]}.{v_clean[2:5]}.{v_clean[5:8]}/{v_clean[8:12]}-{v_clean[12:]}"
        return v

class CompradorUpdate(BaseModel):
    tipo: Optional[str] = None
    nome: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    usuario: Optional[str] = None
    senha: Optional[str] = None
    ativo: Optional[bool] = None

    @validator('tipo')
    def validate_tipo(cls, v):
        if v is not None and v not in ['PF', 'PJ']:
            raise ValueError('Tipo deve ser PF (Pessoa Física) ou PJ (Pessoa Jurídica)')
        return v
    
    @validator('cpf_cnpj')
    def validate_cpf_cnpj(cls, v, values):
        if v is None:
            return v
            
        tipo = values.get('tipo')
        v_clean = ''.join(c for c in v if c.isdigit())
        
        if tipo == 'PF' and len(v_clean) != 11:
            raise ValueError('CPF deve conter 11 dígitos')
        elif tipo == 'PJ' and len(v_clean) != 14:
            raise ValueError('CNPJ deve conter 14 dígitos')
        
        # Formatar CPF ou CNPJ
        if tipo == 'PF':
            return f"{v_clean[:3]}.{v_clean[3:6]}.{v_clean[6:9]}-{v_clean[9:]}"
        elif tipo == 'PJ':
            return f"{v_clean[:2]}.{v_clean[2:5]}.{v_clean[5:8]}/{v_clean[8:12]}-{v_clean[12:]}"
        
        return v

class CompradorInDBBase(CompradorBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

class Comprador(CompradorInDBBase):
    pass

class CompradorWithVendas(CompradorInDBBase):
    total_vendas: int = 0
    valor_total_compras: float = 0