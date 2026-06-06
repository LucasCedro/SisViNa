# app/routes/compradores.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.compradores import Comprador, CompradorCreate, CompradorUpdate, CompradorWithVendas
from app.schemas.nfe import CompradorNfeReadinessOut
from app.services.nfe_validacao import erros_comprador_nfe
from app.crud import compradores as crud_compradores
from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

@router.get("/", response_model=List[Comprador])
async def read_compradores(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    tipo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.view"))
):
    """
    Recupera todos os compradores.
    """
    compradores = await crud_compradores.get_compradores(
        db, skip=skip, limit=limit, ativo=ativo, tipo=tipo
    )
    return compradores

@router.get("/with-vendas", response_model=List[CompradorWithVendas])
async def read_compradores_with_vendas(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    tipo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.view"))
):
    """
    Recupera todos os compradores com informações de vendas.
    """
    compradores = await crud_compradores.get_compradores_with_vendas(
        db, skip=skip, limit=limit, ativo=ativo, tipo=tipo
    )
    return compradores

@router.get("/{comprador_id}", response_model=Comprador)
async def read_comprador(
    comprador_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.view"))
):
    """
    Recupera um comprador específico pelo ID.
    """
    db_comprador = await crud_compradores.get_comprador(db, comprador_id)
    if db_comprador is None:
        raise HTTPException(status_code=404, detail="Comprador não encontrado")
    return db_comprador

@router.get("/{comprador_id}/nfe-readiness", response_model=CompradorNfeReadinessOut)
async def comprador_nfe_readiness(
    comprador_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.view")),
):
    """Campos faltantes para emitir NF-e para este comprador."""
    db_comprador = await crud_compradores.get_comprador(db, comprador_id)
    if db_comprador is None:
        raise HTTPException(status_code=404, detail="Comprador não encontrado")
    faltando = erros_comprador_nfe(db_comprador)
    return CompradorNfeReadinessOut(pronto=len(faltando) == 0, faltando=faltando)

@router.post("/", response_model=Comprador)
async def create_comprador(
    comprador: CompradorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.create"))
):
    """
    Cria um novo comprador.
    """
    # Verificar CPF/CNPJ
    db_comprador_cpf_cnpj = await crud_compradores.get_comprador_by_cpf_cnpj(db, comprador.cpf_cnpj)
    if db_comprador_cpf_cnpj:
        raise HTTPException(
            status_code=400,
            detail=f"{'CPF' if comprador.tipo == 'PF' else 'CNPJ'} já registrado no sistema"
        )
    
    # Verificar usuário se fornecido
    if comprador.usuario:
        db_comprador_usuario = await crud_compradores.get_comprador_by_usuario(db, comprador.usuario)
        if db_comprador_usuario:
            raise HTTPException(
                status_code=400,
                detail="Usuário já registrado no sistema"
            )
    
    return await crud_compradores.create_comprador(db=db, comprador=comprador)

@router.put("/{comprador_id}", response_model=Comprador)
async def update_comprador(
    comprador_id: int,
    comprador: CompradorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.edit"))
):
    """
    Atualiza um comprador existente.
    """
    # Verificar se o comprador existe
    db_comprador = await crud_compradores.get_comprador(db, comprador_id)
    if db_comprador is None:
        raise HTTPException(status_code=404, detail="Comprador não encontrado")
    
    # Verificar CPF/CNPJ se atualizado
    if comprador.cpf_cnpj:
        existing_cpf_cnpj = await crud_compradores.get_comprador_by_cpf_cnpj(db, comprador.cpf_cnpj)
        if existing_cpf_cnpj and existing_cpf_cnpj.id != comprador_id:
            tipo_doc = 'CPF' if comprador.tipo == 'PF' or (comprador.tipo is None and db_comprador.tipo == 'PF') else 'CNPJ'
            raise HTTPException(
                status_code=400,
                detail=f"{tipo_doc} já registrado por outro comprador"
            )
    
    # Verificar usuário se atualizado
    if comprador.usuario:
        existing_user = await crud_compradores.get_comprador_by_usuario(db, comprador.usuario)
        if existing_user and existing_user.id != comprador_id:
            raise HTTPException(
                status_code=400,
                detail="Usuário já registrado por outro comprador"
            )
    
    return await crud_compradores.update_comprador(db, comprador_id, comprador)

@router.delete("/{comprador_id}", response_model=Comprador)
async def delete_comprador(
    comprador_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.edit"))
):
    """
    Deleta um comprador. Se houver vendas associadas, apenas desativa o comprador.
    """
    db_comprador = await crud_compradores.delete_comprador(db, comprador_id)
    if db_comprador is None:
        raise HTTPException(status_code=404, detail="Comprador não encontrado")
    return db_comprador
