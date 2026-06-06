# app/routes/plantas.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.plantas import (
    Planta,
    PlantaCreate,
    PlantaUpdate,
    PlantaWithEspecie,
    EstoqueResumoItem,
    AtualizarPrecoEspecie,
    PlantaDisponivelVenda,
)
from app.schemas.producao import (
    PromoverMudasRequest,
    PromoverMudasResponse,
    PlantaPendenteTransferencia,
    PlantaEmCrescimento,
    AtualizarEstagioRequest,
    AtualizarEstagioResponse,
    TransferirRustificacaoRequest,
    TransferirRustificacaoResponse,
    CadastroLotePlantasRequest,
    CadastroLotePlantasResponse,
)
from app.crud import plantas as crud_plantas
from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

@router.get("/", response_model=List[Planta])
async def read_plantas(
    skip: int = 0,
    limit: int = 100,
    id_especie: Optional[int] = None,
    id_canteiro: Optional[int] = None,
    status: Optional[str] = None,
    estagio_producao: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.view"))
):
    """
    Recupera todas as plantas com opção de filtrar por espécie, canteiro, status e estágio.
    """
    plantas = await crud_plantas.get_plantas(
        db, 
        skip=skip, 
        limit=limit, 
        id_especie=id_especie,
        id_canteiro=id_canteiro,
        status=status,
        estagio_producao=estagio_producao,
    )
    return plantas

@router.get("/with-relations", response_model=List[PlantaWithEspecie])
async def read_plantas_with_relations(
    skip: int = 0,
    limit: int = 100,
    id_especie: Optional[int] = None,
    id_canteiro: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.view"))
):
    """
    Recupera todas as plantas com informações de espécie e canteiro.
    """
    plantas = await crud_plantas.get_plantas_with_relations(
        db, 
        skip=skip, 
        limit=limit, 
        id_especie=id_especie,
        id_canteiro=id_canteiro,
        status=status
    )
    return plantas

@router.get("/pendentes-transferencia", response_model=List[PlantaPendenteTransferencia])
async def read_pendentes_transferencia(
    id_canteiro: Optional[int] = None,
    id_especie: Optional[int] = None,
    limit: int = Query(500, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.view")),
):
    return await crud_plantas.get_plantas_pendentes_transferencia(
        db, id_canteiro=id_canteiro, id_especie=id_especie, limit=limit
    )


@router.get("/em-desenvolvimento-sementeira", response_model=List[PlantaPendenteTransferencia])
async def read_em_desenvolvimento_sementeira(
    id_canteiro: Optional[int] = None,
    id_especie: Optional[int] = None,
    limit: int = Query(500, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.view")),
):
    return await crud_plantas.get_plantas_em_desenvolvimento_sementeira(
        db, id_canteiro=id_canteiro, id_especie=id_especie, limit=limit
    )


@router.get("/em-crescimento-canteiro", response_model=List[PlantaEmCrescimento])
async def read_em_crescimento_canteiro(
    id_canteiro: Optional[int] = None,
    id_especie: Optional[int] = None,
    limit: int = Query(500, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.view")),
):
    return await crud_plantas.get_plantas_em_crescimento_canteiro(
        db, id_canteiro=id_canteiro, id_especie=id_especie, limit=limit
    )


@router.get("/aptas-rustificacao-canteiro", response_model=List[PlantaEmCrescimento])
async def read_aptas_rustificacao_canteiro(
    id_canteiro: Optional[int] = None,
    id_especie: Optional[int] = None,
    limit: int = Query(500, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.view")),
):
    return await crud_plantas.get_plantas_aptas_rustificacao_canteiro(
        db, id_canteiro=id_canteiro, id_especie=id_especie, limit=limit
    )


@router.post("/atualizar-estagio", response_model=AtualizarEstagioResponse)
async def atualizar_estagio(
    body: AtualizarEstagioRequest,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.transfer")),
):
    try:
        return await crud_plantas.atualizar_estagio_producao(db, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/em-rustificacao", response_model=List[PlantaEmCrescimento])
async def read_em_rustificacao(
    id_canteiro: Optional[int] = None,
    id_especie: Optional[int] = None,
    limit: int = Query(500, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.view")),
):
    return await crud_plantas.get_plantas_em_rustificacao(
        db, id_canteiro=id_canteiro, id_especie=id_especie, limit=limit
    )


@router.post("/transferir-rustificacao", response_model=TransferirRustificacaoResponse)
async def transferir_rustificacao(
    body: TransferirRustificacaoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.transfer")),
):
    try:
        return await crud_plantas.transferir_para_rustificacao(
            db, body, id_funcionario=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/promover-mudas", response_model=PromoverMudasResponse)
async def promover_mudas(
    body: PromoverMudasRequest,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.transfer")),
):
    try:
        return await crud_plantas.promover_mudas(db, body, id_funcionario=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/cadastro-lote", response_model=CadastroLotePlantasResponse, status_code=201)
async def cadastro_lote_plantas(
    body: CadastroLotePlantasRequest,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.create")),
):
    try:
        return await crud_plantas.cadastro_lote_plantas(db, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/estoque-resumo", response_model=List[EstoqueResumoItem])
async def read_estoque_resumo(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.view")),
):
    """Estoque comercial: apenas mudas apta_venda (baixa exclusiva via vendas)."""
    return await crud_plantas.get_estoque_resumo(db)


@router.get("/disponiveis-venda/detalhado", response_model=List[PlantaDisponivelVenda])
async def read_plantas_disponiveis_venda_detalhado(
    id_especie: int = Query(..., description="Espécie para listar unidades expedíveis"),
    id_lote_sementes: Optional[int] = Query(None, description="Filtrar por lote de sementes"),
    limit: int = Query(500, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.view")),
):
    """Mudas aptas à venda com lote, canteiro e dias na rustificação."""
    return await crud_plantas.listar_plantas_disponiveis_venda_detalhado(
        db, id_especie=id_especie, id_lote_sementes=id_lote_sementes, limit=limit
    )


@router.get("/disponiveis-venda", response_model=List[Planta])
async def read_plantas_disponiveis_venda(
    id_especie: int = Query(..., description="Espécie para listar unidades expedíveis"),
    limit: int = Query(500, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.view")),
):
    """Plantas individuais aptas à venda (estagio apta_venda)."""
    return await crud_plantas.listar_plantas_disponiveis_venda(
        db, id_especie=id_especie, limit=limit
    )


@router.patch("/preco-especie/{id_especie}")
async def patch_preco_especie(
    id_especie: int,
    body: AtualizarPrecoEspecie,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("vendas.edit")),
):
    n = await crud_plantas.atualizar_preco_especie(db, id_especie, body.preco_venda)
    return {"atualizadas": n}


@router.get("/{planta_id}", response_model=Planta)
async def read_planta(
    planta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.view"))
):
    """
    Recupera uma planta específica pelo ID.
    """
    db_planta = await crud_plantas.get_planta(db, planta_id)
    if db_planta is None:
        raise HTTPException(status_code=404, detail="Planta não encontrada")
    return db_planta

@router.post("/", response_model=Planta)
async def create_planta(
    planta: PlantaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.create")),
):
    """
    Cria uma nova planta.
    """
    return await crud_plantas.create_planta(db=db, planta=planta)

@router.post("/bulk", response_model=List[Planta])
async def create_plantas_bulk(
    planta: PlantaCreate,
    quantidade: int = Query(..., description="Quantidade de plantas a serem criadas", gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.create")),
):
    """
    Cria múltiplas plantas de uma mesma espécie de uma vez.
    """
    if quantidade > 500:
        raise HTTPException(
            status_code=400, 
            detail="Número máximo de plantas por operação é 500"
        )
    
    return await crud_plantas.create_plantas_bulk(db=db, planta_base=planta, quantidade=quantidade)

@router.put("/{planta_id}", response_model=Planta)
async def update_planta(
    planta_id: int,
    planta: PlantaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.edit")),
):
    """
    Atualiza uma planta existente.
    """
    try:
        db_planta = await crud_plantas.update_planta(db, planta_id, planta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if db_planta is None:
        raise HTTPException(status_code=404, detail="Planta não encontrada")
    return db_planta

@router.delete("/{planta_id}", response_model=Planta)
async def delete_planta(
    planta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.edit")),
):
    """
    Deleta uma planta.
    """
    db_planta = await crud_plantas.delete_planta(db, planta_id)
    if db_planta is None:
        raise HTTPException(status_code=404, detail="Planta não encontrada")
    return db_planta
