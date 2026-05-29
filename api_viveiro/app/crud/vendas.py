# app/crud/vendas.py
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime

from app.models.vendas import Venda, ItemVenda
from app.models.compradores import Comprador
from app.models.funcionarios import Funcionario
from app.models.plantas import Planta
from app.models.especies import Especie
from app.models.canteiros import Canteiro
from app.constants.estagios_producao import APTA_VENDA
from app.schemas.vendas import VendaCreate, VendaUpdate, ItemVendaCreate, ItemVendaUpdate
from app.services.validacao_producao import avisos_vender_planta

# Funções CRUD para Venda
async def get_venda(db: AsyncSession, venda_id: int) -> Optional[Venda]:
    result = await db.execute(select(Venda).where(Venda.id == venda_id))
    return result.scalars().first()

async def get_venda_detalhe(db: AsyncSession, venda_id: int) -> Optional[Dict[str, Any]]:
    query = select(
        Venda,
        Comprador.nome.label("comprador_nome"),
        Funcionario.nome.label("funcionario_nome")
    ).join(
        Comprador, Venda.id_comprador == Comprador.id
    ).join(
        Funcionario, Venda.id_funcionario == Funcionario.id
    ).where(
        Venda.id == venda_id
    )
    
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        return None
    
    venda, comprador_nome, funcionario_nome = row
    
    # Buscar itens da venda
    itens_query = select(
        ItemVenda,
        Planta.codigo_rastreio.label("codigo_planta"),
        Especie.nome_cientifico.label("nome_especie"),
        Planta.status.label("status_planta")
    ).join(
        Planta, ItemVenda.id_planta == Planta.id
    ).join(
        Especie, Planta.id_especie == Especie.id
    ).where(
        ItemVenda.id_venda == venda_id
    )
    
    itens_result = await db.execute(itens_query)
    itens = []
    
    for item_row in itens_result:
        item, codigo_planta, nome_especie, status_planta = item_row
        
        item_dict = item.__dict__
        if "_sa_instance_state" in item_dict:
            del item_dict["_sa_instance_state"]
        
        # Converter Decimal para float
        if "valor_unitario" in item_dict:
            item_dict["valor_unitario"] = float(item_dict["valor_unitario"])
        if "valor_total" in item_dict:
            item_dict["valor_total"] = float(item_dict["valor_total"])
        if "desconto" in item_dict:
            item_dict["desconto"] = float(item_dict["desconto"])
        
        item_dict.update({
            "codigo_planta": codigo_planta,
            "nome_especie": nome_especie,
            "status_planta": status_planta
        })
        
        itens.append(item_dict)
    
    venda_dict = venda.__dict__
    if "_sa_instance_state" in venda_dict:
        del venda_dict["_sa_instance_state"]
    
    # Converter Decimal para float
    if "valor_total" in venda_dict:
        venda_dict["valor_total"] = float(venda_dict["valor_total"])
    
    return {
        **venda_dict,
        "comprador_nome": comprador_nome,
        "funcionario_nome": funcionario_nome,
        "itens": itens
    }

async def get_vendas(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    id_comprador: Optional[int] = None,
    id_funcionario: Optional[int] = None,
    status: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    query = select(
        Venda,
        Comprador.nome.label("comprador_nome"),
        Funcionario.nome.label("funcionario_nome"),
        func.count(ItemVenda.id).label("total_itens")
    ).join(
        Comprador, Venda.id_comprador == Comprador.id
    ).join(
        Funcionario, Venda.id_funcionario == Funcionario.id
    ).outerjoin(
        ItemVenda, Venda.id == ItemVenda.id_venda
    )
    
    # Aplicar filtros
    if id_comprador:
        query = query.where(Venda.id_comprador == id_comprador)
    
    if id_funcionario:
        query = query.where(Venda.id_funcionario == id_funcionario)
    
    if status:
        query = query.where(Venda.status == status)
    
    if data_inicio and data_fim:
        query = query.where(and_(
            Venda.data_venda >= data_inicio,
            Venda.data_venda <= data_fim
        ))
    elif data_inicio:
        query = query.where(Venda.data_venda >= data_inicio)
    elif data_fim:
        query = query.where(Venda.data_venda <= data_fim)

    query = query.group_by(
        Venda.id,
        Comprador.nome,
        Funcionario.nome
    ).order_by(
        Venda.data_venda.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    vendas = []
    for row in result:
        venda, comprador_nome, funcionario_nome, total_itens = row
        
        venda_dict = venda.__dict__
        if "_sa_instance_state" in venda_dict:
            del venda_dict["_sa_instance_state"]
        
        # Converter Decimal para float
        if "valor_total" in venda_dict:
            venda_dict["valor_total"] = float(venda_dict["valor_total"])
        
        vendas.append({
            **venda_dict,
            "comprador_nome": comprador_nome,
            "funcionario_nome": funcionario_nome,
            "total_itens": total_itens or 0
        })
    
    return vendas

async def create_venda(db: AsyncSession, venda: VendaCreate) -> Dict[str, Any]:
    # Verificar se há itens na venda
    if not venda.itens or len(venda.itens) == 0:
        raise ValueError("A venda deve conter pelo menos um item")

    ids_plantas = [item.id_planta for item in venda.itens]
    if len(ids_plantas) != len(set(ids_plantas)):
        raise ValueError("A mesma planta não pode aparecer mais de uma vez na venda")

    # Calcular valor total da venda
    valor_total = 0.0
    itens_dict = []
    
    for item in venda.itens:
        valor_item = (item.valor_unitario * item.quantidade) - (item.desconto or 0)
        valor_total += valor_item
        
        item_dict = item.dict()
        item_dict["valor_total"] = valor_item
        itens_dict.append(item_dict)
    
    # Criar objeto venda
    venda_dict = venda.dict(exclude={"itens"})
    venda_dict["valor_total"] = valor_total
    
    db_venda = Venda(**venda_dict)
    db.add(db_venda)
    await db.flush()

    avisos_venda: List[str] = []
    
    # Adicionar itens da venda
    for item_dict in itens_dict:
        item_dict["id_venda"] = db_venda.id
        db_item = ItemVenda(**item_dict)
        db.add(db_item)
        
        # Atualizar status da planta para VENDIDA
        planta_query = select(Planta).where(Planta.id == item_dict["id_planta"])
        planta_result = await db.execute(planta_query)
        planta = planta_result.scalars().first()
        
        if not planta:
            raise ValueError(f"Planta {item_dict['id_planta']} não encontrada")
        if planta.status == "VENDIDA":
            raise ValueError(f"Planta {planta.codigo_rastreio or planta.id} já foi vendida")
        if planta.status == "MORTA":
            raise ValueError(f"Planta {planta.codigo_rastreio or planta.id} está morta")
        if planta.status not in ("MUDA", "JOVEM", "ADULTA"):
            raise ValueError(
                f"Planta {planta.codigo_rastreio or planta.id} não está em fase comercializável"
            )
        if planta.estagio_producao != APTA_VENDA:
            raise ValueError(
                f"Planta {planta.codigo_rastreio or planta.id} ainda não está apta para venda"
            )
        if planta.id_canteiro:
            cant = await db.get(Canteiro, planta.id_canteiro)
            if cant and cant.tipo_local != "rustificacao":
                raise ValueError(
                    f"Planta {planta.codigo_rastreio or planta.id} não está em local comercializável"
                )
        for aviso in await avisos_vender_planta(db, planta):
            if aviso not in avisos_venda:
                avisos_venda.append(aviso)
        planta.status = "VENDIDA"
    
    await db.commit()
    await db.refresh(db_venda)
    
    # Retornar venda detalhada
    resultado = await get_venda_detalhe(db, db_venda.id)
    if avisos_venda:
        resultado["avisos"] = avisos_venda
    return resultado

async def update_venda(
    db: AsyncSession, venda_id: int, venda_update: VendaUpdate
) -> Optional[Venda]:
    db_venda = await get_venda(db, venda_id)
    if not db_venda:
        return None
    
    update_data = venda_update.dict(exclude_unset=True)
    
    # Verificar se pode cancelar a venda
    if update_data.get("status") == "CANCELADO" and db_venda.status != "CANCELADO":
        # Buscar itens da venda
        itens_query = select(ItemVenda).where(ItemVenda.id_venda == venda_id)
        itens_result = await db.execute(itens_query)
        itens = itens_result.scalars().all()
        
        # Restaurar status das plantas
        for item in itens:
            planta_query = select(Planta).where(Planta.id == item.id_planta)
            planta_result = await db.execute(planta_query)
            planta = planta_result.scalars().first()
            
            if planta and planta.status == "VENDIDA":
                planta.status = "ADULTA"
                planta.estagio_producao = APTA_VENDA
    
    for field, value in update_data.items():
        setattr(db_venda, field, value)
    
    await db.commit()
    await db.refresh(db_venda)
    return db_venda

async def delete_venda(db: AsyncSession, venda_id: int) -> Optional[Dict[str, Any]]:
    db_venda = await get_venda(db, venda_id)
    if not db_venda:
        return None
    
    # Registrar dados para retorno
    venda_detalhe = await get_venda_detalhe(db, venda_id)
    
    # Restaurar status das plantas
    itens_query = select(ItemVenda).where(ItemVenda.id_venda == venda_id)
    itens_result = await db.execute(itens_query)
    itens = itens_result.scalars().all()
    
    for item in itens:
        planta_query = select(Planta).where(Planta.id == item.id_planta)
        planta_result = await db.execute(planta_query)
        planta = planta_result.scalars().first()
        
        if planta and planta.status == "VENDIDA":
            planta.status = "ADULTA"
            planta.estagio_producao = APTA_VENDA
        
        # Excluir item
        await db.delete(item)
    
    # Excluir a venda
    await db.delete(db_venda)
    await db.commit()
    return venda_detalhe

# Funções CRUD para ItemVenda
async def get_item_venda(db: AsyncSession, item_id: int) -> Optional[ItemVenda]:
    result = await db.execute(select(ItemVenda).where(ItemVenda.id == item_id))
    return result.scalars().first()

async def get_item_venda_detalhe(db: AsyncSession, item_id: int) -> Optional[Dict[str, Any]]:
    query = select(
        ItemVenda,
        Planta.codigo_rastreio.label("codigo_planta"),
        Especie.nome_cientifico.label("nome_especie"),
        Planta.status.label("status_planta")
    ).join(
        Planta, ItemVenda.id_planta == Planta.id
    ).join(
        Especie, Planta.id_especie == Especie.id
    ).where(
        ItemVenda.id == item_id
    )
    
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        return None
    
    item, codigo_planta, nome_especie, status_planta = row
    
    item_dict = item.__dict__
    if "_sa_instance_state" in item_dict:
        del item_dict["_sa_instance_state"]
    
    # Converter Decimal para float
    if "valor_unitario" in item_dict:
        item_dict["valor_unitario"] = float(item_dict["valor_unitario"])
    if "valor_total" in item_dict:
        item_dict["valor_total"] = float(item_dict["valor_total"])
    if "desconto" in item_dict:
        item_dict["desconto"] = float(item_dict["desconto"])
    
    return {
        **item_dict,
        "codigo_planta": codigo_planta,
        "nome_especie": nome_especie,
        "status_planta": status_planta
    }

async def update_item_venda(
    db: AsyncSession, item_id: int, item_update: ItemVendaUpdate
) -> Optional[ItemVenda]:
    db_item = await get_item_venda(db, item_id)
    if not db_item:
        return None
    
    update_data = item_update.dict(exclude_unset=True)
    
    # Recalcular valor total se houver alteração em quantidade, valor_unitario ou desconto
    if "quantidade" in update_data or "valor_unitario" in update_data or "desconto" in update_data:
        quantidade = update_data.get("quantidade", db_item.quantidade)
        valor_unitario = update_data.get("valor_unitario", db_item.valor_unitario)
        desconto = update_data.get("desconto", db_item.desconto or 0)
        
        valor_total = (float(valor_unitario) * quantidade) - float(desconto)
        update_data["valor_total"] = valor_total
        
        # Atualizar valor total da venda
        venda_query = select(Venda).where(Venda.id == db_item.id_venda)
        venda_result = await db.execute(venda_query)
        venda = venda_result.scalars().first()
        
        if venda:
            # Buscar todos os itens da venda exceto o atual
            outros_itens_query = select(func.sum(ItemVenda.valor_total)).where(
                and_(
                    ItemVenda.id_venda == db_item.id_venda,
                    ItemVenda.id != item_id
                )
            )
            outros_itens_result = await db.execute(outros_itens_query)
            outros_itens_total = outros_itens_result.scalar_one() or 0
            
            # Calcular novo valor total da venda
            venda.valor_total = float(outros_itens_total) + valor_total
    
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def delete_item_venda(db: AsyncSession, item_id: int) -> Optional[Dict[str, Any]]:
    db_item = await get_item_venda(db, item_id)
    if not db_item:
        return None
    
    # Registrar dados para retorno
    item_detalhe = await get_item_venda_detalhe(db, item_id)
    
    # Restaurar status da planta
    planta_query = select(Planta).where(Planta.id == db_item.id_planta)
    planta_result = await db.execute(planta_query)
    planta = planta_result.scalars().first()
    
    if planta and planta.status == "VENDIDA":
        planta.status = "ADULTA"
        planta.estagio_producao = APTA_VENDA
    
    # Atualizar valor total da venda
    venda_query = select(Venda).where(Venda.id == db_item.id_venda)
    venda_result = await db.execute(venda_query)
    venda = venda_result.scalars().first()
    
    if venda:
        venda.valor_total = venda.valor_total - db_item.valor_total
    
    # Excluir o item
    await db.delete(db_item)
    await db.commit()
    return item_detalhe