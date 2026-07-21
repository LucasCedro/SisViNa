# app/crud/funcionarios.py
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.funcionarios import Funcionario
from app.models.atividades import Atividade
from app.schemas.funcionarios import FuncionarioCreate, FuncionarioUpdate, FuncionarioPerfilUpdate
from app.auth.utils import gerar_senha_hash

async def get_funcionario(
    db: AsyncSession, funcionario_id: int, id_empresa: Optional[int] = None
) -> Optional[Funcionario]:
    query = select(Funcionario).where(Funcionario.id == funcionario_id)
    if id_empresa is not None:
        query = query.where(Funcionario.id_empresa == id_empresa)
    result = await db.execute(query)
    return result.scalars().first()

async def get_funcionario_by_usuario(db: AsyncSession, usuario: str) -> Optional[Funcionario]:
    result = await db.execute(select(Funcionario).where(Funcionario.usuario == usuario))
    return result.scalars().first()

async def get_funcionario_by_cpf(
    db: AsyncSession, cpf: str, id_empresa: Optional[int] = None
) -> Optional[Funcionario]:
    query = select(Funcionario).where(Funcionario.cpf == cpf)
    if id_empresa is not None:
        query = query.where(Funcionario.id_empresa == id_empresa)
    result = await db.execute(query)
    return result.scalars().first()

async def get_funcionarios(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    id_empresa: Optional[int] = None,
) -> List[Funcionario]:
    query = select(Funcionario)

    if id_empresa is not None:
        query = query.where(Funcionario.id_empresa == id_empresa)
    if ativo is not None:
        query = query.where(Funcionario.ativo == ativo)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_funcionarios_with_stats(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    id_empresa: Optional[int] = None,
) -> List[Dict[str, Any]]:
    query = select(
        Funcionario,
        func.count(Atividade.id).label("total_atividades"),
        func.sum(Atividade.custo_atividade).label("custo_atividades")
    ).outerjoin(
        Atividade, Funcionario.id == Atividade.id_funcionario
    )
    
    if id_empresa is not None:
        query = query.where(Funcionario.id_empresa == id_empresa)
    if ativo is not None:
        query = query.where(Funcionario.ativo == ativo)
    
    query = query.group_by(
        Funcionario.id
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    funcionarios_with_stats = []
    for row in result:
        funcionario_dict = row[0].__dict__
        funcionario_dict["total_atividades"] = row[1] or 0
        funcionario_dict["custo_atividades"] = float(row[2] or 0)
        
        # Remover senha e _sa_instance_state
        if "senha" in funcionario_dict:
            del funcionario_dict["senha"]
        if "_sa_instance_state" in funcionario_dict:
            del funcionario_dict["_sa_instance_state"]
        
        funcionarios_with_stats.append(funcionario_dict)
    
    return funcionarios_with_stats

async def create_funcionario(
    db: AsyncSession, funcionario: FuncionarioCreate, id_empresa: Optional[int] = None
) -> Funcionario:
    funcionario_dict = funcionario.dict()
    empresa_payload = funcionario_dict.pop("id_empresa", None)
    if id_empresa is not None:
        funcionario_dict["id_empresa"] = id_empresa
    elif empresa_payload is not None:
        funcionario_dict["id_empresa"] = empresa_payload
    senha_hash = gerar_senha_hash(funcionario_dict.pop("senha"))
    
    db_funcionario = Funcionario(**funcionario_dict, senha=senha_hash)
    db.add(db_funcionario)
    await db.commit()
    await db.refresh(db_funcionario)
    return db_funcionario

async def update_funcionario_perfil(
    db: AsyncSession, funcionario_id: int, perfil: FuncionarioPerfilUpdate
) -> Optional[Funcionario]:
    db_funcionario = await get_funcionario(db, funcionario_id)
    if not db_funcionario:
        return None

    update_data = perfil.dict(exclude_unset=True)
    if "email" in update_data and update_data["email"]:
        existing = await db.execute(
            select(Funcionario).where(
                Funcionario.email == update_data["email"],
                Funcionario.id != funcionario_id,
            )
        )
        if existing.scalars().first():
            raise ValueError("E-mail já registrado por outro usuário")

    for field, value in update_data.items():
        setattr(db_funcionario, field, value)

    await db.commit()
    await db.refresh(db_funcionario)
    return db_funcionario


async def update_funcionario(
    db: AsyncSession, funcionario_id: int, funcionario_update: FuncionarioUpdate
) -> Optional[Funcionario]:
    db_funcionario = await get_funcionario(db, funcionario_id)
    if not db_funcionario:
        return None
    
    update_data = funcionario_update.dict(exclude_unset=True)
    
    # Hash da senha se ela for atualizada
    if "senha" in update_data:
        update_data["senha"] = gerar_senha_hash(update_data["senha"])
    
    for field, value in update_data.items():
        setattr(db_funcionario, field, value)
    
    await db.commit()
    await db.refresh(db_funcionario)
    return db_funcionario

async def delete_funcionario(db: AsyncSession, funcionario_id: int) -> Optional[Funcionario]:
    db_funcionario = await get_funcionario(db, funcionario_id)
    if not db_funcionario:
        return None
    
    # Soft delete - apenas marca como inativo
    db_funcionario.ativo = False
    await db.commit()
    await db.refresh(db_funcionario)
    return db_funcionario