# app/schemas/funcionarios.py
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator

VALID_PERFIS = frozenset({"admin", "gestor", "campo", "financeiro", "rh", "consulta"})


class FuncionarioBase(BaseModel):
    nome: str
    cpf: str
    rg: Optional[str] = None
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    cargo: Optional[str] = None
    data_contratacao: Optional[date] = None
    salario: Optional[float] = None
    usuario: str
    ativo: Optional[bool] = True
    perfis: Optional[List[str]] = None

    @validator("perfis")
    def validate_perfis(cls, v):
        if v is None:
            return v
        invalid = [p for p in v if p not in VALID_PERFIS]
        if invalid:
            raise ValueError(f"Perfis inválidos: {', '.join(invalid)}")
        return list(dict.fromkeys(v))

class FuncionarioCreate(FuncionarioBase):
    senha: str

    @validator('cpf')
    def validate_cpf(cls, v):
        # Remover caracteres não numéricos
        v_clean = ''.join(c for c in v if c.isdigit())
        
        if len(v_clean) != 11:
            raise ValueError('CPF deve conter 11 dígitos')
        
        # Formato básico XXX.XXX.XXX-XX
        return f"{v_clean[:3]}.{v_clean[3:6]}.{v_clean[6:9]}-{v_clean[9:]}"

class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    cargo: Optional[str] = None
    data_contratacao: Optional[date] = None
    salario: Optional[float] = None
    usuario: Optional[str] = None
    senha: Optional[str] = None
    ativo: Optional[bool] = None
    perfis: Optional[List[str]] = None

    @validator("perfis")
    def validate_perfis_update(cls, v):
        if v is None:
            return v
        invalid = [p for p in v if p not in VALID_PERFIS]
        if invalid:
            raise ValueError(f"Perfis inválidos: {', '.join(invalid)}")
        return list(dict.fromkeys(v))

    @validator('cpf')
    def validate_cpf(cls, v):
        if v is None:
            return v
            
        # Remover caracteres não numéricos
        v_clean = ''.join(c for c in v if c.isdigit())
        
        if len(v_clean) != 11:
            raise ValueError('CPF deve conter 11 dígitos')
        
        # Formato básico XXX.XXX.XXX-XX
        return f"{v_clean[:3]}.{v_clean[3:6]}.{v_clean[6:9]}-{v_clean[9:]}"

class FuncionarioInDBBase(FuncionarioBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

class FuncionarioOut(FuncionarioInDBBase):
    perfis: List[str] = []

class FuncionarioWithStats(FuncionarioInDBBase):
    total_atividades: int = 0
    custo_atividades: float = 0