import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import coletas_sementes as crud_coletas
from app.crud import lotes_sementes as crud_lotes
from app.crud import arvores_matriz as crud_matriz
from app.database import get_db
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()


def _csv_response(rows: list, filename: str) -> StreamingResponse:
    if not rows:
        rows = [{}]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()), extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        flat = {k: ("" if v is None else v) for k, v in row.items()}
        writer.writerow(flat)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/matrizes.csv")
async def export_matrizes(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    matrizes = await crud_matriz.get_arvores_matriz(db, limit=5000)
    return _csv_response(matrizes, "matrizes.csv")


@router.get("/export/coletas.csv")
async def export_coletas(
    id_arvore_matriz: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    coletas = await crud_coletas.get_coletas(db, limit=5000, id_arvore_matriz=id_arvore_matriz)
    flat = []
    for c in coletas:
        row = {k: v for k, v in c.items() if k != "lotes"}
        flat.append(row)
    return _csv_response(flat, "coletas.csv")


@router.get("/export/lotes.csv")
async def export_lotes(
    id_arvore_matriz: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    lotes = await crud_lotes.get_lotes(db, limit=5000, id_arvore_matriz=id_arvore_matriz)
    return _csv_response(lotes, "lotes.csv")


@router.get("/export/rastreabilidade-matriz.csv")
async def export_rastreabilidade_matriz(
    id_arvore_matriz: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    matriz = await crud_matriz.get_arvore_matriz_out(db, id_arvore_matriz)
    coletas = await crud_coletas.get_coletas(db, id_arvore_matriz=id_arvore_matriz, limit=5000)
    lotes = await crud_lotes.get_lotes(db, id_arvore_matriz=id_arvore_matriz, limit=5000)
    rows = []
    if matriz:
        rows.append({"secao": "MATRIZ", **matriz})
    for c in coletas:
        rows.append({"secao": "COLETA", **{k: v for k, v in c.items() if k != "lotes"}})
    for l in lotes:
        rows.append({"secao": "LOTE", **l})
    return _csv_response(rows, f"rastreabilidade-matriz-{id_arvore_matriz}.csv")
