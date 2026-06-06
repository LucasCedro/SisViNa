"""Rotas NF-e — emissão, status, webhook, emitente."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import nfe as crud_nfe
from app.database import get_db
from app.schemas.emitente_fiscal import EmitenteFiscalOut, EmitenteFiscalUpdate
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.nfe import EmitirNfeOut, NfeWebhookPayload, NotaFiscalOut, AmbienteNfeOut
from app.services.nfe_service import NfeProvedorError
from app.services.nfe_ambiente import info_ambiente

router = APIRouter()


@router.get("/ambiente", response_model=AmbienteNfeOut)
async def ambiente_nfe(
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("fiscal.view")),
):
    emitente = await crud_nfe.get_emitente(db)
    return info_ambiente(emitente)


@router.get("/emitente", response_model=EmitenteFiscalOut)
async def ler_emitente(
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("fiscal.view")),
):
    emitente = await crud_nfe.get_emitente(db)
    if not emitente:
        raise HTTPException(404, "Emitente fiscal não cadastrado")
    return emitente


@router.put("/emitente", response_model=EmitenteFiscalOut)
async def salvar_emitente(
    body: EmitenteFiscalUpdate,
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("fiscal.edit")),
):
    try:
        return await crud_nfe.upsert_emitente(db, body.dict())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/emit/{venda_id}", response_model=EmitirNfeOut)
async def emitir_nfe(
    venda_id: int,
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("fiscal.emit")),
):
    try:
        resultado = await crud_nfe.emitir_nfe_venda(db, venda_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except NfeProvedorError as exc:
        raise HTTPException(502, str(exc)) from exc

    nota = resultado["nota"]
    return EmitirNfeOut(nota=nota, mensagem=resultado["mensagem"])


@router.get("/venda/{venda_id}", response_model=List[NotaFiscalOut])
async def listar_notas_venda(
    venda_id: int,
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("fiscal.view")),
):
    return await crud_nfe.list_notas_venda(db, venda_id)


@router.get("/{nfe_id}/status", response_model=NotaFiscalOut)
async def status_nfe(
    nfe_id: int,
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("fiscal.view")),
):
    nota = await crud_nfe.atualizar_status_nota(db, nfe_id)
    if not nota:
        raise HTTPException(404, "NF-e não encontrada")
    return nota


@router.post("/webhook")
async def webhook_nfe(
    payload: NfeWebhookPayload,
    db: AsyncSession = Depends(get_db),
):
    """Callback do provedor (Focus NFe) — sem auth para permitir POST externo."""
    nota = await crud_nfe.processar_webhook(db, payload.dict(exclude_none=True))
    if not nota:
        raise HTTPException(404, "Referência NF-e não encontrada")
    return {"ok": True, "id": nota.id, "status": nota.status}
