# app/crud/insumos.py
from typing import List, Optional, Dict, Any
from datetime import date, datetime

from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insumos import Insumo
from app.models.insumo_movimentacao import InsumoMovimentacao
from app.models.atividades import InsumoAtividade
from app.schemas.insumos import InsumoCreate, InsumoUpdate, InsumoMovimentacaoCreate

async def get_insumo(db: AsyncSession, insumo_id: int) -> Optional[Insumo]:
    """
    Obtém um insumo pelo ID
    """
    result = await db.execute(select(Insumo).where(Insumo.id == insumo_id))
    return result.scalars().first()

async def get_insumo_by_nome(db: AsyncSession, nome: str) -> Optional[Insumo]:
    """
    Obtém um insumo pelo nome
    """
    result = await db.execute(select(Insumo).where(Insumo.nome == nome))
    return result.scalars().first()

async def get_insumos(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    tipo: Optional[str] = None,
    fornecedor: Optional[str] = None,
    estoque_minimo: Optional[float] = None
) -> List[Insumo]:
    """
    Obtém lista de insumos com filtros opcionais
    """
    query = select(Insumo)
    
    if tipo:
        query = query.where(Insumo.tipo == tipo)
    
    if fornecedor:
        query = query.where(Insumo.fornecedor == fornecedor)
    
    if estoque_minimo is not None:
        query = query.where(Insumo.quantidade_estoque >= estoque_minimo)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_insumos_com_usos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Obtém insumos com informações de uso
    """
    query = select(
        Insumo,
        func.count(InsumoAtividade.id).label("total_usos"),
        func.sum(InsumoAtividade.quantidade_usada).label("quantidade_total_usada"),
        func.sum(InsumoAtividade.custo_total).label("valor_total_usado")
    ).outerjoin(
        InsumoAtividade, Insumo.id == InsumoAtividade.id_insumo
    )
    
    if tipo:
        query = query.where(Insumo.tipo == tipo)
    
    query = query.group_by(
        Insumo.id
    ).order_by(
        Insumo.nome
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    insumos_com_usos = []
    for row in result:
        insumo, total_usos, quantidade_total_usada, valor_total_usado = row
        
        insumo_dict = insumo.__dict__
        if "_sa_instance_state" in insumo_dict:
            del insumo_dict["_sa_instance_state"]
        
        # Converter Decimal para float
        if "quantidade_estoque" in insumo_dict and insumo_dict["quantidade_estoque"] is not None:
            insumo_dict["quantidade_estoque"] = float(insumo_dict["quantidade_estoque"])
        
        if "preco_unitario" in insumo_dict and insumo_dict["preco_unitario"] is not None:
            insumo_dict["preco_unitario"] = float(insumo_dict["preco_unitario"])
        
        insumos_com_usos.append({
            **insumo_dict,
            "total_usos": total_usos or 0,
            "quantidade_total_usada": float(quantidade_total_usada or 0),
            "valor_total_usado": float(valor_total_usado or 0)
        })
    
    return insumos_com_usos

async def create_insumo(db: AsyncSession, insumo: InsumoCreate) -> Insumo:
    """
    Cria um novo insumo
    """
    db_insumo = Insumo(**insumo.dict())
    db.add(db_insumo)
    await db.commit()
    await db.refresh(db_insumo)
    return db_insumo

async def update_insumo(
    db: AsyncSession, insumo_id: int, insumo_update: InsumoUpdate
) -> Optional[Insumo]:
    """
    Atualiza um insumo existente
    """
    db_insumo = await get_insumo(db, insumo_id)
    if not db_insumo:
        return None
    
    update_data = insumo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_insumo, field, value)
    
    await db.commit()
    await db.refresh(db_insumo)
    return db_insumo

async def delete_insumo(db: AsyncSession, insumo_id: int) -> Optional[Insumo]:
    """
    Deleta um insumo se não estiver em uso
    """
    db_insumo = await get_insumo(db, insumo_id)
    if not db_insumo:
        return None
    
    # Verificar se há usos do insumo
    query = select(func.count(InsumoAtividade.id)).where(InsumoAtividade.id_insumo == insumo_id)
    result = await db.execute(query)
    count = result.scalar_one()
    
    if count > 0:
        return None  # Não pode excluir insumos com usos registrados
    
    await db.delete(db_insumo)
    await db.commit()
    return db_insumo

def _recalcular_preco_medio(
    qtd_atual: float, valor_atual: float, qtd_entrada: float, valor_entrada: float
) -> tuple[float, float]:
    nova_qtd = qtd_atual + qtd_entrada
    if nova_qtd <= 0:
        return 0.0, 0.0
    novo_valor = valor_atual + valor_entrada
    return nova_qtd, novo_valor / nova_qtd


async def baixar_insumo_por_media_movel(
    db: AsyncSession, insumo_id: int, quantidade: float
) -> float:
    """Baixa estoque pelo custo médio móvel. Retorna o valor (R$) da baixa."""
    insumo = await get_insumo(db, insumo_id)
    if not insumo:
        raise ValueError(f"Insumo {insumo_id} não encontrado")
    qtd_atual = float(insumo.quantidade_estoque or 0)
    valor_atual = float(insumo.valor_estoque or 0)
    if valor_atual <= 0 and insumo.preco_unitario:
        valor_atual = qtd_atual * float(insumo.preco_unitario)
    if quantidade > qtd_atual:
        raise ValueError("Quantidade maior que estoque disponível")
    preco_medio = (valor_atual / qtd_atual) if qtd_atual > 0 else float(insumo.preco_unitario or 0)
    custo_baixa = round(quantidade * preco_medio, 2)
    saldo = qtd_atual - quantidade
    insumo.quantidade_estoque = saldo
    insumo.valor_estoque = round(saldo * preco_medio, 2) if saldo > 0 else 0
    if saldo <= 0:
        insumo.preco_unitario = 0
    return custo_baixa


async def registrar_movimentacao(
    db: AsyncSession, insumo_id: int, payload: InsumoMovimentacaoCreate
) -> Optional[InsumoMovimentacao]:
    db_insumo = await get_insumo(db, insumo_id)
    if not db_insumo:
        return None

    tipo = payload.tipo.strip().lower()
    if tipo not in ("entrada", "saida", "ajuste"):
        raise ValueError("tipo deve ser entrada, saida ou ajuste")

    qtd_atual = float(db_insumo.quantidade_estoque or 0)
    valor_atual = float(db_insumo.valor_estoque or 0)
    if valor_atual <= 0 and db_insumo.preco_unitario:
        valor_atual = qtd_atual * float(db_insumo.preco_unitario)

    qtd_mov = float(payload.quantidade)
    data_mov = payload.data_movimento or date.today()
    valor_total_mov: Optional[float] = None
    preco_unit_mov: Optional[float] = None

    if tipo == "entrada":
        valor_total_mov = float(payload.valor_total or 0)
        if valor_total_mov <= 0:
            preco_ref = float(db_insumo.preco_unitario or 0)
            if preco_ref <= 0 and qtd_atual <= 0:
                raise ValueError(
                    "Informe o valor total pago na compra (NF) para calcular o preço médio do estoque."
                )
            valor_total_mov = qtd_mov * preco_ref if preco_ref > 0 else 0
        preco_unit_mov = valor_total_mov / qtd_mov if qtd_mov else 0
        nova_qtd, preco_medio = _recalcular_preco_medio(
            qtd_atual, valor_atual, qtd_mov, valor_total_mov
        )
        db_insumo.quantidade_estoque = nova_qtd
        db_insumo.valor_estoque = nova_qtd * preco_medio
        db_insumo.preco_unitario = preco_medio
        db_insumo.data_ultima_compra = data_mov
        saldo = nova_qtd
    elif tipo == "saida":
        if qtd_mov > qtd_atual:
            raise ValueError("Quantidade de saída maior que o estoque disponível")
        preco_medio = (valor_atual / qtd_atual) if qtd_atual > 0 else float(db_insumo.preco_unitario or 0)
        valor_total_mov = qtd_mov * preco_medio
        preco_unit_mov = preco_medio
        saldo = qtd_atual - qtd_mov
        db_insumo.quantidade_estoque = saldo
        db_insumo.valor_estoque = saldo * preco_medio if saldo > 0 else 0
        if saldo <= 0:
            db_insumo.preco_unitario = 0
    else:
        saldo = qtd_mov
        db_insumo.quantidade_estoque = saldo
        if payload.valor_total is not None:
            db_insumo.valor_estoque = float(payload.valor_total)
            db_insumo.preco_unitario = float(payload.valor_total) / saldo if saldo > 0 else 0
        elif saldo > 0 and qtd_atual > 0:
            preco_medio = valor_atual / qtd_atual
            db_insumo.valor_estoque = saldo * preco_medio
        valor_total_mov = float(db_insumo.valor_estoque or 0)

    mov = InsumoMovimentacao(
        id_insumo=insumo_id,
        tipo=tipo,
        quantidade=qtd_mov,
        valor_total=valor_total_mov,
        preco_unitario=preco_unit_mov,
        saldo_quantidade=float(db_insumo.quantidade_estoque or 0),
        data_movimento=data_mov,
        observacao=payload.observacao,
    )
    db.add(mov)
    await db.commit()
    await db.refresh(mov)
    await db.refresh(db_insumo)
    return mov


async def listar_movimentacoes(
    db: AsyncSession, insumo_id: int, limit: int = 60
) -> List[InsumoMovimentacao]:
    result = await db.execute(
        select(InsumoMovimentacao)
        .where(InsumoMovimentacao.id_insumo == insumo_id)
        .order_by(InsumoMovimentacao.data_movimento.desc(), InsumoMovimentacao.id.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def get_tipos_insumos(db: AsyncSession) -> List[str]:
    result = await db.execute(
        select(distinct(Insumo.tipo)).where(Insumo.tipo.isnot(None)).order_by(Insumo.tipo)
    )
    return [row[0] for row in result if row[0]]


async def get_fornecedores(db: AsyncSession) -> List[str]:
    result = await db.execute(
        select(distinct(Insumo.fornecedor))
        .where(Insumo.fornecedor.isnot(None))
        .order_by(Insumo.fornecedor)
    )
    return [row[0] for row in result if row[0]]


async def atualizar_estoque(
    db: AsyncSession, insumo_id: int, quantidade: float, data_compra: Optional[date] = None
) -> Optional[Insumo]:
    """Compatibilidade: delega para movimentação de entrada/saída."""
    if quantidade == 0:
        return await get_insumo(db, insumo_id)
    tipo = "entrada" if quantidade > 0 else "saida"
    await registrar_movimentacao(
        db,
        insumo_id,
        InsumoMovimentacaoCreate(
            tipo=tipo,
            quantidade=abs(quantidade),
            data_movimento=data_compra,
            observacao="Atualização legada via /estoque",
        ),
    )
    return await get_insumo(db, insumo_id)