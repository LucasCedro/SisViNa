# app/crud/pragas.py
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime

from app.models.pragas import TipoPraga, MetodoCombate, PragaPlanta, CombateRealizado
from app.models.plantas import Planta
from app.models.especies import Especie
from app.models.funcionarios import Funcionario
from app.schemas.pragas import (
    TipoPragaCreate, TipoPragaUpdate,
    MetodoCombateCreate, MetodoCombateUpdate,
    PragaPlantaCreate, PragaPlantaUpdate,
    CombateRealizadoCreate, CombateRealizadoUpdate
)

# Funções CRUD para TipoPraga
async def get_tipo_praga(db: AsyncSession, tipo_id: int) -> Optional[TipoPraga]:
    result = await db.execute(select(TipoPraga).where(TipoPraga.id == tipo_id))
    return result.scalars().first()

async def get_tipo_praga_by_nome(db: AsyncSession, nome: str) -> Optional[TipoPraga]:
    result = await db.execute(select(TipoPraga).where(TipoPraga.nome == nome))
    return result.scalars().first()

async def get_tipos_pragas(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[TipoPraga]:
    result = await db.execute(select(TipoPraga).offset(skip).limit(limit))
    return result.scalars().all()

async def create_tipo_praga(db: AsyncSession, tipo_praga: TipoPragaCreate) -> TipoPraga:
    db_tipo = TipoPraga(**tipo_praga.dict())
    db.add(db_tipo)
    await db.commit()
    await db.refresh(db_tipo)
    return db_tipo

async def update_tipo_praga(
    db: AsyncSession, tipo_id: int, tipo_update: TipoPragaUpdate
) -> Optional[TipoPraga]:
    db_tipo = await get_tipo_praga(db, tipo_id)
    if not db_tipo:
        return None
    
    update_data = tipo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tipo, field, value)
    
    await db.commit()
    await db.refresh(db_tipo)
    return db_tipo

async def delete_tipo_praga(db: AsyncSession, tipo_id: int) -> Optional[TipoPraga]:
    db_tipo = await get_tipo_praga(db, tipo_id)
    if not db_tipo:
        return None
    
    # Verificar se há pragas usando este tipo
    query = select(func.count(PragaPlanta.id)).where(PragaPlanta.id_tipo_praga == tipo_id)
    result = await db.execute(query)
    count = result.scalar_one()
    
    if count > 0:
        return None  # Não pode excluir tipos com pragas associadas
    
    await db.delete(db_tipo)
    await db.commit()
    return db_tipo

# Funções CRUD para MetodoCombate
async def get_metodo_combate(db: AsyncSession, metodo_id: int) -> Optional[MetodoCombate]:
    result = await db.execute(select(MetodoCombate).where(MetodoCombate.id == metodo_id))
    return result.scalars().first()

async def get_metodos_combate(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[MetodoCombate]:
    result = await db.execute(select(MetodoCombate).offset(skip).limit(limit))
    return result.scalars().all()

async def create_metodo_combate(db: AsyncSession, metodo_combate: MetodoCombateCreate) -> MetodoCombate:
    db_metodo = MetodoCombate(**metodo_combate.dict())
    db.add(db_metodo)
    await db.commit()
    await db.refresh(db_metodo)
    return db_metodo

async def update_metodo_combate(
    db: AsyncSession, metodo_id: int, metodo_update: MetodoCombateUpdate
) -> Optional[MetodoCombate]:
    db_metodo = await get_metodo_combate(db, metodo_id)
    if not db_metodo:
        return None
    
    update_data = metodo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_metodo, field, value)
    
    await db.commit()
    await db.refresh(db_metodo)
    return db_metodo

async def delete_metodo_combate(db: AsyncSession, metodo_id: int) -> Optional[MetodoCombate]:
    db_metodo = await get_metodo_combate(db, metodo_id)
    if not db_metodo:
        return None
    
    # Verificar se há combates usando este método
    query = select(func.count(CombateRealizado.id)).where(CombateRealizado.id_metodo_combate == metodo_id)
    result = await db.execute(query)
    count = result.scalar_one()
    
    if count > 0:
        return None  # Não pode excluir métodos com combates associados
    
    await db.delete(db_metodo)
    await db.commit()
    return db_metodo

# Funções CRUD para PragaPlanta
async def get_praga_planta(db: AsyncSession, praga_id: int) -> Optional[PragaPlanta]:
    result = await db.execute(select(PragaPlanta).where(PragaPlanta.id == praga_id))
    return result.scalars().first()

async def get_praga_planta_detalhe(db: AsyncSession, praga_id: int) -> Optional[Dict[str, Any]]:
    query = select(
        PragaPlanta,
        TipoPraga,
        Planta.codigo_rastreio.label("planta_codigo"),
        Especie.nome_cientifico.label("especie_nome"),
        func.count(CombateRealizado.id).label("total_combates")
    ).join(
        TipoPraga, PragaPlanta.id_tipo_praga == TipoPraga.id
    ).join(
        Planta, PragaPlanta.id_planta == Planta.id
    ).join(
        Especie, Planta.id_especie == Especie.id
    ).outerjoin(
        CombateRealizado, PragaPlanta.id == CombateRealizado.id_praga_planta
    ).where(
        PragaPlanta.id == praga_id
    ).group_by(
        PragaPlanta.id,
        TipoPraga.id,
        Planta.codigo_rastreio,
        Especie.nome_cientifico
    )
    
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        return None
    
    praga_planta, tipo_praga, planta_codigo, especie_nome, total_combates = row
    
    praga_dict = praga_planta.__dict__
    if "_sa_instance_state" in praga_dict:
        del praga_dict["_sa_instance_state"]
    
    tipo_dict = tipo_praga.__dict__
    if "_sa_instance_state" in tipo_dict:
        del tipo_dict["_sa_instance_state"]
    
    return {
        **praga_dict,
        "tipo_praga": tipo_dict,
        "planta_codigo": planta_codigo,
        "especie_nome": especie_nome,
        "total_combates": total_combates or 0
    }

async def get_pragas_plantas(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    id_planta: Optional[int] = None,
    id_tipo_praga: Optional[int] = None,
    nivel_infestacao: Optional[str] = None
) -> List[Dict[str, Any]]:
    query = select(
        PragaPlanta,
        TipoPraga.nome.label("tipo_praga_nome"),
        Planta.codigo_rastreio.label("planta_codigo"),
        Especie.nome_cientifico.label("especie_nome"),
        func.count(CombateRealizado.id).label("total_combates")
    ).join(
        TipoPraga, PragaPlanta.id_tipo_praga == TipoPraga.id
    ).join(
        Planta, PragaPlanta.id_planta == Planta.id
    ).join(
        Especie, Planta.id_especie == Especie.id
    ).outerjoin(
        CombateRealizado, PragaPlanta.id == CombateRealizado.id_praga_planta
    )
    
    # Aplicar filtros
    if id_planta:
        query = query.where(PragaPlanta.id_planta == id_planta)
    
    if id_tipo_praga:
        query = query.where(PragaPlanta.id_tipo_praga == id_tipo_praga)
    
    if nivel_infestacao:
        query = query.where(PragaPlanta.nivel_infestacao == nivel_infestacao)
    
    query = query.group_by(
        PragaPlanta.id,
        TipoPraga.nome,
        Planta.codigo_rastreio,
        Especie.nome_cientifico
    ).order_by(
        PragaPlanta.data_identificacao.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    pragas_plantas = []
    for row in result:
        praga_planta, tipo_nome, planta_codigo, especie_nome, total_combates = row
        
        praga_dict = praga_planta.__dict__
        if "_sa_instance_state" in praga_dict:
            del praga_dict["_sa_instance_state"]
        
        pragas_plantas.append({
            **praga_dict,
            "tipo_praga_nome": tipo_nome,
            "planta_codigo": planta_codigo,
            "especie_nome": especie_nome,
            "total_combates": total_combates or 0
        })
    
    return pragas_plantas

async def create_praga_planta(db: AsyncSession, praga_planta: PragaPlantaCreate) -> PragaPlanta:
    db_praga = PragaPlanta(**praga_planta.dict())
    db.add(db_praga)
    await db.commit()
    await db.refresh(db_praga)
    return db_praga

async def update_praga_planta(
    db: AsyncSession, praga_id: int, praga_update: PragaPlantaUpdate
) -> Optional[PragaPlanta]:
    db_praga = await get_praga_planta(db, praga_id)
    if not db_praga:
        return None
    
    update_data = praga_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_praga, field, value)
    
    await db.commit()
    await db.refresh(db_praga)
    return db_praga

async def delete_praga_planta(db: AsyncSession, praga_id: int) -> Optional[PragaPlanta]:
    db_praga = await get_praga_planta(db, praga_id)
    if not db_praga:
        return None
    
    # Verificar se existem combates realizados
    query = select(func.count(CombateRealizado.id)).where(CombateRealizado.id_praga_planta == praga_id)
    result = await db.execute(query)
    count = result.scalar_one()
    
    if count > 0:
        return None  # Não pode excluir se houver combates associados
    
    await db.delete(db_praga)
    await db.commit()
    return db_praga

# Funções CRUD para CombateRealizado
async def get_combate_realizado(db: AsyncSession, combate_id: int) -> Optional[CombateRealizado]:
    result = await db.execute(select(CombateRealizado).where(CombateRealizado.id == combate_id))
    return result.scalars().first()

async def get_combate_realizado_detalhe(db: AsyncSession, combate_id: int) -> Optional[Dict[str, Any]]:
    query = select(
        CombateRealizado,
        MetodoCombate,
        Funcionario.nome.label("funcionario_nome"),
        Planta.codigo_rastreio.label("planta_codigo"),
        TipoPraga.nome.label("tipo_praga_nome")
    ).join(
        MetodoCombate, CombateRealizado.id_metodo_combate == MetodoCombate.id
    ).join(
        Funcionario, CombateRealizado.id_funcionario == Funcionario.id
    ).join(
        PragaPlanta, CombateRealizado.id_praga_planta == PragaPlanta.id
    ).join(
        Planta, PragaPlanta.id_planta == Planta.id
    ).join(
        TipoPraga, PragaPlanta.id_tipo_praga == TipoPraga.id
    ).where(
        CombateRealizado.id == combate_id
    )
    
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        return None
    
    combate, metodo, funcionario_nome, planta_codigo, tipo_praga_nome = row
    
    combate_dict = combate.__dict__
    if "_sa_instance_state" in combate_dict:
        del combate_dict["_sa_instance_state"]
    
    metodo_dict = metodo.__dict__
    if "_sa_instance_state" in metodo_dict:
        del metodo_dict["_sa_instance_state"]
    
    # Converter Decimal para float
    if "custo_total" in combate_dict and combate_dict["custo_total"] is not None:
        combate_dict["custo_total"] = float(combate_dict["custo_total"])
    
    if "quantidade_aplicada" in combate_dict and combate_dict["quantidade_aplicada"] is not None:
        combate_dict["quantidade_aplicada"] = float(combate_dict["quantidade_aplicada"])
    
    if "custo_unitario" in metodo_dict and metodo_dict["custo_unitario"] is not None:
        metodo_dict["custo_unitario"] = float(metodo_dict["custo_unitario"])
    
    return {
        **combate_dict,
        "metodo_combate": metodo_dict,
        "funcionario_nome": funcionario_nome,
        "planta_codigo": planta_codigo,
        "tipo_praga_nome": tipo_praga_nome
    }

async def get_combates_realizados(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    id_praga_planta: Optional[int] = None,
    id_metodo_combate: Optional[int] = None,
    id_funcionario: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    query = select(
        CombateRealizado,
        MetodoCombate.nome.label("metodo_nome"),
        Funcionario.nome.label("funcionario_nome"),
        Planta.codigo_rastreio.label("planta_codigo"),
        TipoPraga.nome.label("tipo_praga_nome")
    ).join(
        MetodoCombate, CombateRealizado.id_metodo_combate == MetodoCombate.id
    ).join(
        Funcionario, CombateRealizado.id_funcionario == Funcionario.id
    ).join(
        PragaPlanta, CombateRealizado.id_praga_planta == PragaPlanta.id
    ).join(
        Planta, PragaPlanta.id_planta == Planta.id
    ).join(
        TipoPraga, PragaPlanta.id_tipo_praga == TipoPraga.id
    )
    
    # Aplicar filtros
    if id_praga_planta:
        query = query.where(CombateRealizado.id_praga_planta == id_praga_planta)
    
    if id_metodo_combate:
        query = query.where(CombateRealizado.id_metodo_combate == id_metodo_combate)
    
    if id_funcionario:
        query = query.where(CombateRealizado.id_funcionario == id_funcionario)
    
    if data_inicio and data_fim:
        query = query.where(and_(
            CombateRealizado.data_aplicacao >= data_inicio,
            CombateRealizado.data_aplicacao <= data_fim
        ))
    elif data_inicio:
        query = query.where(CombateRealizado.data_aplicacao >= data_inicio)
    elif data_fim:
        query = query.where(CombateRealizado.data_aplicacao <= data_fim)
    
    query = query.order_by(
        CombateRealizado.data_aplicacao.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    combates = []
    for row in result:
        combate, metodo_nome, funcionario_nome, planta_codigo, tipo_praga_nome = row
        
        combate_dict = combate.__dict__
        if "_sa_instance_state" in combate_dict:
            del combate_dict["_sa_instance_state"]
        
        # Converter Decimal para float
        if "custo_total" in combate_dict and combate_dict["custo_total"] is not None:
            combate_dict["custo_total"] = float(combate_dict["custo_total"])
        
        if "quantidade_aplicada" in combate_dict and combate_dict["quantidade_aplicada"] is not None:
            combate_dict["quantidade_aplicada"] = float(combate_dict["quantidade_aplicada"])
        
        combates.append({
            **combate_dict,
            "metodo_nome": metodo_nome,
            "funcionario_nome": funcionario_nome,
            "planta_codigo": planta_codigo,
            "tipo_praga_nome": tipo_praga_nome
        })
    
    return combates

async def create_combate_realizado(db: AsyncSession, combate: CombateRealizadoCreate) -> CombateRealizado:
    # Calcular custo total se não fornecido
    if combate.custo_total is None and combate.quantidade_aplicada is not None:
        # Buscar custo unitário do método de combate
        metodo_query = select(MetodoCombate.custo_unitario).where(MetodoCombate.id == combate.id_metodo_combate)
        metodo_result = await db.execute(metodo_query)
        custo_unitario = metodo_result.scalar_one_or_none()
        
        if custo_unitario:
            combate_dict = combate.dict()
            combate_dict["custo_total"] = float(custo_unitario) * combate.quantidade_aplicada
        else:
            combate_dict = combate.dict()
    else:
        combate_dict = combate.dict()
    
    db_combate = CombateRealizado(**combate_dict)
    db.add(db_combate)
    
    # Atualizar custo da planta se necessário
    if db_combate.custo_total and float(db_combate.custo_total) > 0:
        # Buscar id_planta através de praga_planta
        praga_query = select(PragaPlanta.id_planta).where(PragaPlanta.id == db_combate.id_praga_planta)
        praga_result = await db.execute(praga_query)
        id_planta = praga_result.scalar_one_or_none()
        
        if id_planta:
            planta_query = select(Planta).where(Planta.id == id_planta)
            planta_result = await db.execute(planta_query)
            planta = planta_result.scalar_one()
            
            if planta:
                planta.custo_atual = planta.custo_atual + db_combate.custo_total
    
    await db.commit()
    await db.refresh(db_combate)
    return db_combate

async def update_combate_realizado(
    db: AsyncSession, combate_id: int, combate_update: CombateRealizadoUpdate
) -> Optional[CombateRealizado]:
    db_combate = await get_combate_realizado(db, combate_id)
    if not db_combate:
        return None
    
    # Registrar custo anterior para ajuste na planta
    custo_anterior = float(db_combate.custo_total) if db_combate.custo_total else 0
    
    update_data = combate_update.dict(exclude_unset=True)
    
    # Recalcular custo total se quantidade alterada mas custo não
    if "quantidade_aplicada" in update_data and "custo_total" not in update_data:
        # Buscar custo unitário do método de combate
        metodo_query = select(MetodoCombate.custo_unitario).where(MetodoCombate.id == db_combate.id_metodo_combate)
        metodo_result = await db.execute(metodo_query)
        custo_unitario = metodo_result.scalar_one_or_none()
        
        if custo_unitario:
            update_data["custo_total"] = float(custo_unitario) * update_data["quantidade_aplicada"]
    
    for field, value in update_data.items():
        setattr(db_combate, field, value)
    
    # Atualizar custo da planta se o custo do combate foi alterado
    if "custo_total" in update_data:
        custo_novo = float(update_data["custo_total"])
        diferenca_custo = custo_novo - custo_anterior
        
        if diferenca_custo != 0:
            # Buscar id_planta através de praga_planta
            praga_query = select(PragaPlanta.id_planta).where(PragaPlanta.id == db_combate.id_praga_planta)
            praga_result = await db.execute(praga_query)
            id_planta = praga_result.scalar_one_or_none()
            
            if id_planta:
                planta_query = select(Planta).where(Planta.id == id_planta)
                planta_result = await db.execute(planta_query)
                planta = planta_result.scalar_one()
                
                if planta:
                    planta.custo_atual = planta.custo_atual + diferenca_custo
    
    await db.commit()
    await db.refresh(db_combate)
    return db_combate

async def delete_combate_realizado(db: AsyncSession, combate_id: int) -> Optional[Dict[str, Any]]:
    db_combate = await get_combate_realizado(db, combate_id)
    if not db_combate:
        return None
    
    # Registrar dados para retorno
    combate_detalhe = await get_combate_realizado_detalhe(db, combate_id)
    
    # Remover custo do combate da planta
    if db_combate.custo_total and float(db_combate.custo_total) > 0:
        # Buscar id_planta através de praga_planta
        praga_query = select(PragaPlanta.id_planta).where(PragaPlanta.id == db_combate.id_praga_planta)
        praga_result = await db.execute(praga_query)
        id_planta = praga_result.scalar_one_or_none()
        
        if id_planta:
            planta_query = select(Planta).where(Planta.id == id_planta)
            planta_result = await db.execute(planta_query)
            planta = planta_result.scalar_one()
            
            if planta:
                planta.custo_atual = planta.custo_atual - db_combate.custo_total
    
    # Excluir o combate
    await db.delete(db_combate)
    await db.commit()
    return combate_detalhe