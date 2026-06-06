"""Cockpit fiscal — parâmetros definidos pelo contador (não é parecer tributário automático)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import regras_fiscais as crud_regras
from app.crud import nfe as crud_nfe
from app.database import get_db
from app.schemas.emitente_fiscal import EmitenteFiscalOut, EmitenteFiscalUpdate
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.nfe import (
    RegraFiscalOut,
    RegraFiscalBase,
    RegraFiscalUpdate,
    NotaFiscalListOut,
    ResumoFiscalOut,
    VendaPendenteNfeOut,
    AmbienteNfeOut,
    RegraFiscalPreviewOut,
)
from app.services.nfe_ambiente import info_ambiente
from app.services.tributacao_nfe import preview_regra_venda

router = APIRouter()


@router.get("/regras", response_model=List[RegraFiscalOut])
async def listar_regras_fiscais(
    ativo: Optional[bool] = None,
    uf_origem: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("fiscal.view")),
):
    return await crud_regras.list_regras(db, ativo=ativo, uf_origem=uf_origem)


@router.get("/regras/preview", response_model=RegraFiscalPreviewOut)
async def preview_regra_fiscal(
    uf_destino: str,
    tipo_cliente: str = "PF",
    ncm: str = "06029090",
    tipo_operacao: str = "domestica",
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("fiscal.view")),
):
    """Pré-visualiza regra fiscal para UF do comprador (vendedor ou contador)."""
    emitente = await crud_nfe.get_emitente(db)
    data = await preview_regra_venda(
        db,
        emitente,
        uf_destino=uf_destino,
        tipo_cliente=tipo_cliente,
        ncm=ncm,
        tipo_operacao=tipo_operacao,
    )
    return RegraFiscalPreviewOut(**data)


@router.post("/regras", response_model=RegraFiscalOut)
async def criar_regra_fiscal(
    body: RegraFiscalBase,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("fiscal.edit")),
):
    try:
        return await crud_regras.create_regra(db, body.dict())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.put("/regras/{regra_id}", response_model=RegraFiscalOut)
async def atualizar_regra_fiscal(
    regra_id: int,
    body: RegraFiscalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("fiscal.edit")),
):
    try:
        regra = await crud_regras.update_regra(db, regra_id, body.dict(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if not regra:
        raise HTTPException(404, "Regra fiscal não encontrada")
    return regra


@router.delete("/regras/{regra_id}")
async def excluir_regra_fiscal(
    regra_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("fiscal.edit")),
):
    if not await crud_regras.delete_regra(db, regra_id):
        raise HTTPException(404, "Regra fiscal não encontrada")
    return {"ok": True}


@router.get("/emitente", response_model=EmitenteFiscalOut)
async def ler_emitente_fiscal(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("fiscal.view")),
):
    emitente = await crud_nfe.get_emitente(db)
    if not emitente:
        raise HTTPException(404, "Emitente fiscal não cadastrado")
    return emitente


@router.put("/emitente", response_model=EmitenteFiscalOut)
async def salvar_emitente_fiscal(
    body: EmitenteFiscalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("fiscal.edit")),
):
    try:
        return await crud_nfe.upsert_emitente(db, body.dict())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/ambiente", response_model=AmbienteNfeOut)
async def ambiente_nfe(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("contabilidade.view")),
):
    emitente = await crud_nfe.get_emitente(db)
    return info_ambiente(emitente)


@router.get("/resumo", response_model=ResumoFiscalOut)
async def resumo_fiscal(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("contabilidade.view")),
):
    return await crud_nfe.resumo_fiscal(db)


@router.get("/notas", response_model=List[NotaFiscalListOut])
async def listar_notas_fiscais(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("contabilidade.view")),
):
    rows = await crud_nfe.list_notas_fiscais(db, skip=skip, limit=limit, status=status)
    return [NotaFiscalListOut(**row) for row in rows]


@router.get("/vendas-pendentes", response_model=List[VendaPendenteNfeOut])
async def vendas_pendentes_nfe(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("contabilidade.view")),
):
    return await crud_nfe.vendas_pendentes_nfe(db, limit=limit)
