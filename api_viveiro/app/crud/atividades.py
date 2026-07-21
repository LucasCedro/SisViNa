# app/crud/atividades.py
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime

from app.models.atividades import TipoAtividade, Atividade, InsumoAtividade
from app.models.plantas import Planta
from app.models.especies import Especie
from app.models.funcionarios import Funcionario
from app.models.insumos import Insumo
from app.schemas.atividades import (
    TipoAtividadeCreate, TipoAtividadeUpdate,
    AtividadeCreate, AtividadeUpdate,
    InsumoAtividadeCreate, InsumoAtividadeUpdate
)
from app.crud.insumos import baixar_insumo_por_media_movel

# Funções CRUD para TipoAtividade
async def get_tipo_atividade(
    db: AsyncSession, tipo_id: int, id_empresa: Optional[int] = None
) -> Optional[TipoAtividade]:
    query = select(TipoAtividade).where(TipoAtividade.id == tipo_id)
    if id_empresa is not None:
        query = query.where(TipoAtividade.id_empresa == id_empresa)
    result = await db.execute(query)
    return result.scalars().first()

async def get_tipo_atividade_by_nome(
    db: AsyncSession, nome: str, id_empresa: Optional[int] = None
) -> Optional[TipoAtividade]:
    query = select(TipoAtividade).where(TipoAtividade.nome == nome)
    if id_empresa is not None:
        query = query.where(TipoAtividade.id_empresa == id_empresa)
    result = await db.execute(query)
    return result.scalars().first()

async def get_tipos_atividades(
    db: AsyncSession, skip: int = 0, limit: int = 100, id_empresa: Optional[int] = None
) -> List[TipoAtividade]:
    query = select(TipoAtividade)
    if id_empresa is not None:
        query = query.where(TipoAtividade.id_empresa == id_empresa)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def create_tipo_atividade(
    db: AsyncSession, tipo_atividade: TipoAtividadeCreate, id_empresa: Optional[int] = None
) -> TipoAtividade:
    db_tipo = TipoAtividade(**tipo_atividade.dict(), id_empresa=id_empresa)
    db.add(db_tipo)
    await db.commit()
    await db.refresh(db_tipo)
    return db_tipo

async def update_tipo_atividade(
    db: AsyncSession, tipo_id: int, tipo_update: TipoAtividadeUpdate, id_empresa: Optional[int] = None
) -> Optional[TipoAtividade]:
    db_tipo = await get_tipo_atividade(db, tipo_id, id_empresa)
    if not db_tipo:
        return None
    
    update_data = tipo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tipo, field, value)
    
    await db.commit()
    await db.refresh(db_tipo)
    return db_tipo

async def delete_tipo_atividade(
    db: AsyncSession, tipo_id: int, id_empresa: Optional[int] = None
) -> Optional[TipoAtividade]:
    db_tipo = await get_tipo_atividade(db, tipo_id, id_empresa)
    if not db_tipo:
        return None
    
    # Verificar se há atividades usando este tipo
    query = select(func.count(Atividade.id)).where(Atividade.id_tipo_atividade == tipo_id)
    result = await db.execute(query)
    count = result.scalar_one()
    
    if count > 0:
        return None  # Não pode excluir tipos com atividades associadas
    
    await db.delete(db_tipo)
    await db.commit()
    return db_tipo

# Funções CRUD para Atividade
async def get_atividade(
    db: AsyncSession, atividade_id: int, id_viveiro: Optional[int] = None
) -> Optional[Atividade]:
    if id_viveiro is None:
        result = await db.execute(select(Atividade).where(Atividade.id == atividade_id))
        return result.scalars().first()
    result = await db.execute(
        select(Atividade)
        .join(Planta, Atividade.id_planta == Planta.id)
        .where(Atividade.id == atividade_id, Planta.id_viveiro == id_viveiro)
    )
    return result.scalars().first()

async def get_atividade_detalhe(
    db: AsyncSession, atividade_id: int, id_viveiro: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    query = select(
        Atividade, 
        TipoAtividade, 
        Funcionario, 
        Planta, 
        Especie
    ).join(
        TipoAtividade, Atividade.id_tipo_atividade == TipoAtividade.id
    ).join(
        Funcionario, Atividade.id_funcionario == Funcionario.id
    ).join(
        Planta, Atividade.id_planta == Planta.id
    ).join(
        Especie, Planta.id_especie == Especie.id
    ).where(
        Atividade.id == atividade_id
    )
    if id_viveiro is not None:
        query = query.where(Planta.id_viveiro == id_viveiro)
    
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        return None
    
    atividade, tipo, funcionario, planta, especie = row
    
    # Buscar insumos utilizados
    insumos_query = select(
        InsumoAtividade, 
        Insumo
    ).join(
        Insumo, InsumoAtividade.id_insumo == Insumo.id
    ).where(
        InsumoAtividade.id_atividade == atividade_id
    )
    
    insumos_result = await db.execute(insumos_query)
    insumos_utilizados = []
    
    for insumo_row in insumos_result:
        insumo_atividade, insumo = insumo_row
        
        insumo_dict = {
            "id": insumo_atividade.id,
            "id_atividade": insumo_atividade.id_atividade,
            "id_insumo": insumo_atividade.id_insumo,
            "quantidade_usada": float(insumo_atividade.quantidade_usada),
            "custo_total": float(insumo_atividade.custo_total) if insumo_atividade.custo_total else 0,
            "data_registro": insumo_atividade.data_registro,
            "insumo": {
                "id": insumo.id,
                "nome": insumo.nome,
                "tipo": insumo.tipo,
                "unidade_medida": insumo.unidade_medida,
                "preco_unitario": float(insumo.preco_unitario) if insumo.preco_unitario else 0
            }
        }
        insumos_utilizados.append(insumo_dict)
    
    # Montar resposta
    atividade_detalhe = {
        "id": atividade.id,
        "id_tipo_atividade": atividade.id_tipo_atividade,
        "id_planta": atividade.id_planta,
        "id_funcionario": atividade.id_funcionario,
        "data_atividade": atividade.data_atividade,
        "descricao": atividade.descricao,
        "custo_atividade": float(atividade.custo_atividade) if atividade.custo_atividade else 0,
        "observacoes": atividade.observacoes,
        "data_registro": atividade.data_registro,
        "tipo_atividade": {
            "id": tipo.id,
            "nome": tipo.nome,
            "descricao": tipo.descricao,
            "gera_custo": tipo.gera_custo
        },
        "funcionario_nome": funcionario.nome,
        "planta_codigo": planta.codigo_rastreio,
        "especie_nome": especie.nome_cientifico,
        "insumos_utilizados": insumos_utilizados
    }
    
    return atividade_detalhe

async def get_atividades(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    id_tipo_atividade: Optional[int] = None,
    id_planta: Optional[int] = None,
    id_funcionario: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    id_viveiro: Optional[int] = None,
) -> List[Dict[str, Any]]:
    query = select(
        Atividade, 
        TipoAtividade.nome.label("tipo_atividade_nome"),
        Funcionario.nome.label("funcionario_nome"),
        Planta.codigo_rastreio.label("planta_codigo"),
        Especie.nome_cientifico.label("especie_nome"),
        func.count(InsumoAtividade.id).label("total_insumos")
    ).join(
        TipoAtividade, Atividade.id_tipo_atividade == TipoAtividade.id
    ).join(
        Funcionario, Atividade.id_funcionario == Funcionario.id
    ).join(
        Planta, Atividade.id_planta == Planta.id
    ).join(
        Especie, Planta.id_especie == Especie.id
    ).outerjoin(
        InsumoAtividade, Atividade.id == InsumoAtividade.id_atividade
    )
    
    # Adicionar filtros
    if id_tipo_atividade:
        query = query.where(Atividade.id_tipo_atividade == id_tipo_atividade)
    
    if id_planta:
        query = query.where(Atividade.id_planta == id_planta)
    
    if id_funcionario:
        query = query.where(Atividade.id_funcionario == id_funcionario)
    
    if data_inicio and data_fim:
        query = query.where(and_(
            Atividade.data_atividade >= data_inicio,
            Atividade.data_atividade <= data_fim
        ))
    elif data_inicio:
        query = query.where(Atividade.data_atividade >= data_inicio)
    elif data_fim:
        query = query.where(Atividade.data_atividade <= data_fim)
    if id_viveiro is not None:
        query = query.where(Planta.id_viveiro == id_viveiro)
    
    query = query.group_by(
        Atividade.id, 
        TipoAtividade.nome, 
        Funcionario.nome,
        Planta.codigo_rastreio,
        Especie.nome_cientifico
    ).order_by(
        Atividade.data_atividade.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    atividades = []
    for row in result:
        atividade, tipo_nome, func_nome, planta_codigo, especie_nome, total_insumos = row
        
        atividade_dict = atividade.__dict__
        atividade_dict["tipo_atividade_nome"] = tipo_nome
        atividade_dict["funcionario_nome"] = func_nome
        atividade_dict["planta_codigo"] = planta_codigo
        atividade_dict["especie_nome"] = especie_nome
        atividade_dict["total_insumos"] = total_insumos
        
        # Converter valores Decimal para float
        if atividade_dict.get("custo_atividade"):
            atividade_dict["custo_atividade"] = float(atividade_dict["custo_atividade"])
        
        # Remover _sa_instance_state
        if "_sa_instance_state" in atividade_dict:
            del atividade_dict["_sa_instance_state"]
        
        atividades.append(atividade_dict)
    
    return atividades

async def create_atividade(
    db: AsyncSession, atividade: AtividadeCreate, id_viveiro: Optional[int] = None,
    id_empresa: Optional[int] = None,
) -> Dict[str, Any]:
    if id_viveiro is not None:
        planta = await db.get(Planta, atividade.id_planta)
        if planta is None or planta.id_viveiro != id_viveiro:
            raise ValueError("Planta não pertence à unidade viveiro ativa")
    atividade_dict = atividade.dict(exclude={"insumos"})
    db_atividade = Atividade(**atividade_dict)
    db.add(db_atividade)
    await db.flush()
    
    # Adicionar insumos utilizados
    if atividade.insumos:
        for insumo_data in atividade.insumos:
            # Verificar se o insumo existe e buscar seu preço
            insumo_query = select(Insumo).where(Insumo.id == insumo_data.id_insumo)
            if id_empresa is not None:
                insumo_query = insumo_query.where(Insumo.id_empresa == id_empresa)
            insumo_result = await db.execute(insumo_query)
            insumo = insumo_result.scalars().first()

            if not insumo:
                raise ValueError(f"Insumo {insumo_data.id_insumo} não encontrado na empresa")
            
            if insumo:
                # Calcular custo total se não fornecido
                if insumo_data.custo_total is None and insumo.preco_unitario is not None:
                    insumo_data.custo_total = float(insumo.preco_unitario) * insumo_data.quantidade_usada
                
                try:
                    custo_baixa = await baixar_insumo_por_media_movel(
                        db, insumo_data.id_insumo, float(insumo_data.quantidade_usada),
                        id_empresa=id_empresa,
                    )
                    if insumo_data.custo_total is None or insumo_data.custo_total == 0:
                        insumo_data.custo_total = custo_baixa
                except ValueError:
                    if insumo.quantidade_estoque is not None:
                        insumo.quantidade_estoque = insumo.quantidade_estoque - insumo_data.quantidade_usada
                
                insumo_atividade = InsumoAtividade(
                    id_atividade=db_atividade.id,
                    id_insumo=insumo_data.id_insumo,
                    quantidade_usada=insumo_data.quantidade_usada,
                    custo_total=insumo_data.custo_total
                )
                db.add(insumo_atividade)
                
                # Atualizar custo da atividade
                if insumo_data.custo_total:
                    db_atividade.custo_atividade = db_atividade.custo_atividade + insumo_data.custo_total
    
    # Atualizar planta com o custo da atividade
    if db_atividade.custo_atividade > 0:
        planta_query = select(Planta).where(Planta.id == db_atividade.id_planta)
        planta_result = await db.execute(planta_query)
        planta = planta_result.scalars().first()
        
        if planta:
            planta.custo_atual = planta.custo_atual + db_atividade.custo_atividade
    
    await db.commit()
    await db.refresh(db_atividade)
    
    # Retornar atividade detalhada
    return await get_atividade_detalhe(db, db_atividade.id, id_viveiro=id_viveiro)

async def update_atividade(
    db: AsyncSession, atividade_id: int, atividade_update: AtividadeUpdate, id_viveiro: Optional[int] = None
) -> Optional[Atividade]:
    db_atividade = await get_atividade(db, atividade_id, id_viveiro=id_viveiro)
    if not db_atividade:
        return None
    
    # Registrar custo anterior para ajuste na planta
    custo_anterior = float(db_atividade.custo_atividade) if db_atividade.custo_atividade else 0
    
    update_data = atividade_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_atividade, field, value)
    
    # Atualizar custo da planta se o custo da atividade foi alterado
    if "custo_atividade" in update_data:
        custo_novo = float(update_data["custo_atividade"])
        diferenca_custo = custo_novo - custo_anterior
        
        if diferenca_custo != 0:
            planta_query = select(Planta).where(Planta.id == db_atividade.id_planta)
            planta_result = await db.execute(planta_query)
            planta = planta_result.scalars().first()
            
            if planta:
                planta.custo_atual = planta.custo_atual + diferenca_custo
    
    await db.commit()
    await db.refresh(db_atividade)
    return db_atividade

async def delete_atividade(
    db: AsyncSession, atividade_id: int, id_viveiro: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    db_atividade = await get_atividade(db, atividade_id, id_viveiro=id_viveiro)
    if not db_atividade:
        return None
    
    # Registrar detalhes para retorno
    atividade_detalhe = await get_atividade_detalhe(db, atividade_id)
    
    # Remover custo da atividade da planta
    if db_atividade.custo_atividade and float(db_atividade.custo_atividade) > 0:
        planta_query = select(Planta).where(Planta.id == db_atividade.id_planta)
        planta_result = await db.execute(planta_query)
        planta = planta_result.scalars().first()
        
        if planta:
            planta.custo_atual = planta.custo_atual - db_atividade.custo_atividade
    
    # Restaurar estoque dos insumos utilizados
    insumos_query = select(InsumoAtividade).where(InsumoAtividade.id_atividade == atividade_id)
    insumos_result = await db.execute(insumos_query)
    insumos_atividade = insumos_result.scalars().all()
    
    for insumo_atividade in insumos_atividade:
        insumo_query = select(Insumo).where(Insumo.id == insumo_atividade.id_insumo)
        insumo_result = await db.execute(insumo_query)
        insumo = insumo_result.scalars().first()
        
        if insumo and insumo.quantidade_estoque is not None:
            insumo.quantidade_estoque = insumo.quantidade_estoque + insumo_atividade.quantidade_usada
        
        # Excluir registro de uso do insumo
        await db.delete(insumo_atividade)
    
    # Excluir a atividade
    await db.delete(db_atividade)
    await db.commit()
    return atividade_detalhe