# app/crud/plantas.py
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import date, datetime

from app.models.plantas import Planta
from app.models.especies import Especie
from app.models.canteiros import Canteiro
from app.models.arvores_matriz import ArvoreMatriz
from app.models.lotes_sementes import LoteSementes
from app.models.transferencias_plantas import TransferenciaPlanta
from app.schemas.plantas import PlantaCreate, PlantaUpdate
from app.schemas.producao import PromoverMudasRequest, CadastroLotePlantasRequest, AtualizarEstagioRequest
from app.constants.estagios_producao import (
    APTA_TRANSFERENCIA,
    APTA_RUSTIFICACAO,
    APTA_VENDA,
    EM_CRESCIMENTO,
    EM_DESENVOLVIMENTO,
    EM_RUSTIFICACAO,
    ESTAGIO_INICIAL_CANTEIRO,
    ESTAGIO_INICIAL_RUSTIFICACAO,
    ESTAGIO_INICIAL_SEMENTEIRA,
)
from app.schemas.producao import TransferirRustificacaoRequest
import uuid

from app.services.validacao_producao import (
    avisos_liberar_venda,
    avisos_transferir_rustificacao,
)


def _marcar_inicio_estagio(planta: Planta, quando: Optional[date] = None) -> None:
    planta.data_inicio_estagio_atual = quando or date.today()


async def get_planta(db: AsyncSession, planta_id: int) -> Optional[Planta]:
    result = await db.execute(select(Planta).where(Planta.id == planta_id))
    return result.scalars().first()

async def get_planta_by_codigo(db: AsyncSession, codigo_rastreio: str) -> Optional[Planta]:
    result = await db.execute(select(Planta).where(Planta.codigo_rastreio == codigo_rastreio))
    return result.scalars().first()

async def get_plantas(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    id_especie: Optional[int] = None,
    id_canteiro: Optional[int] = None,
    status: Optional[str] = None,
    estagio_producao: Optional[str] = None,
) -> List[Planta]:
    query = select(Planta)
    
    # Adicionar filtros se fornecidos
    if id_especie is not None:
        query = query.where(Planta.id_especie == id_especie)
    
    if id_canteiro is not None:
        query = query.where(Planta.id_canteiro == id_canteiro)
    
    if status is not None:
        query = query.where(Planta.status == status)

    if estagio_producao is not None:
        query = query.where(Planta.estagio_producao == estagio_producao)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_plantas_with_relations(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    id_especie: Optional[int] = None,
    id_canteiro: Optional[int] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    query = select(
        Planta, 
        Especie.nome_cientifico.label("especie_nome"),
        Canteiro.nome.label("nome_canteiro")
    ).join(
        Especie, Planta.id_especie == Especie.id
    ).outerjoin(
        Canteiro, Planta.id_canteiro == Canteiro.id
    )
    
    # Adicionar filtros se fornecidos
    if id_especie is not None:
        query = query.where(Planta.id_especie == id_especie)
    
    if id_canteiro is not None:
        query = query.where(Planta.id_canteiro == id_canteiro)
    
    if status is not None:
        query = query.where(Planta.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    
    plantas_with_relations = []
    for row in result:
        planta_dict = row[0].__dict__
        planta_dict["especie_nome"] = row[1]
        planta_dict["nome_canteiro"] = row[2]
        
        if "_sa_instance_state" in planta_dict:
            del planta_dict["_sa_instance_state"]
        
        plantas_with_relations.append(planta_dict)
    
    return plantas_with_relations

async def create_planta(db: AsyncSession, planta: PlantaCreate) -> Planta:
    # Gerar código de rastreio se não fornecido
    if not planta.codigo_rastreio:
        planta_dict = planta.dict()
        planta_dict["codigo_rastreio"] = f"PL-{uuid.uuid4().hex[:8].upper()}"
    else:
        planta_dict = planta.dict()
    
    db_planta = Planta(**planta_dict)
    db.add(db_planta)
    await db.commit()
    await db.refresh(db_planta)
    return db_planta

async def create_plantas_bulk(db: AsyncSession, planta_base: PlantaCreate, quantidade: int) -> List[Planta]:
    """Cria múltiplas plantas de uma mesma espécie de uma vez"""
    plantas = []
    
    planta_dict = planta_base.dict()
    for _ in range(quantidade):
        novo_planta_dict = planta_dict.copy()
        novo_planta_dict["codigo_rastreio"] = f"PL-{uuid.uuid4().hex[:8].upper()}"
        db_planta = Planta(**novo_planta_dict)
        db.add(db_planta)
        plantas.append(db_planta)
    
    await db.commit()
    
    for planta in plantas:
        await db.refresh(planta)
    
    return plantas

async def update_planta(
    db: AsyncSession, planta_id: int, planta_update: PlantaUpdate
) -> Optional[Planta]:
    db_planta = await get_planta(db, planta_id)
    if not db_planta:
        return None
    
    update_data = planta_update.dict(exclude_unset=True)
    if update_data.get("status") == "VENDIDA":
        raise ValueError(
            "Baixa de estoque por venda só pelo módulo Vendas e Estoque"
        )
    for field, value in update_data.items():
        setattr(db_planta, field, value)
    
    await db.commit()
    await db.refresh(db_planta)
    return db_planta

DISPONIVEIS_VENDA = ("MUDA", "JOVEM", "ADULTA")
ESTOQUE_VENDAVEL_ESTAGIO = APTA_VENDA


async def get_estoque_resumo(db: AsyncSession) -> List[Dict[str, Any]]:
    from app.crud.plantas_estoque import filtro_prontas_venda

    query = filtro_prontas_venda(
        select(
            Especie.id.label("id_especie"),
            Especie.nome_popular,
            Especie.nome_cientifico,
            func.count(Planta.id).label("quantidade"),
            func.avg(Planta.preco_venda).label("valor_unitario"),
            func.min(Canteiro.nome).label("localizacao"),
            func.max(Planta.status).label("status_predominante"),
        )
        .select_from(Especie)
        .join(Planta, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
    ).group_by(Especie.id, Especie.nome_popular, Especie.nome_cientifico).order_by(
        func.count(Planta.id).desc()
    )
    rows = (await db.execute(query)).all()
    items = []
    for row in rows:
        items.append(
            {
                "id_especie": row.id_especie,
                "nome_popular": row.nome_popular,
                "nome_cientifico": row.nome_cientifico,
                "quantidade": int(row.quantidade or 0),
                "valor_unitario": float(row.valor_unitario or 0),
                "localizacao": row.localizacao,
                "status_predominante": row.status_predominante,
                "estagio_comercial": ESTOQUE_VENDAVEL_ESTAGIO,
            }
        )
    return items


async def atualizar_preco_especie(
    db: AsyncSession, id_especie: int, preco_venda: float
) -> int:
    from sqlalchemy import update
    from app.crud.plantas_estoque import filtro_prontas_venda

    subq = filtro_prontas_venda(
        select(Planta.id).join(Canteiro, Planta.id_canteiro == Canteiro.id).where(
            Planta.id_especie == id_especie
        )
    ).subquery()
    result = await db.execute(
        update(Planta)
        .where(Planta.id.in_(select(subq.c.id)))
        .values(preco_venda=preco_venda)
    )
    await db.commit()
    return result.rowcount or 0


async def listar_plantas_disponiveis_venda(
    db: AsyncSession, id_especie: int, limit: int = 100
) -> List[Planta]:
    from app.crud.plantas_estoque import filtro_prontas_venda

    q = filtro_prontas_venda(
        select(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(Planta.id_especie == id_especie)
    ).order_by(Planta.id).limit(limit)
    return (await db.execute(q)).scalars().all()


async def _validar_canteiro_tipo(
    db: AsyncSession, id_canteiro: int, tipo_esperado: str, label: str
) -> Canteiro:
    canteiro = await db.get(Canteiro, id_canteiro)
    if not canteiro:
        raise ValueError(f"{label} não encontrado")
    if canteiro.tipo_local != tipo_esperado:
        raise ValueError(
            f"{label} deve ser do tipo '{tipo_esperado}' (atual: {canteiro.tipo_local})"
        )
    return canteiro


async def get_plantas_pendentes_transferencia(
    db: AsyncSession,
    id_canteiro: Optional[int] = None,
    id_especie: Optional[int] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    query = (
        select(
            Planta,
            Especie.nome_cientifico.label("especie_nome"),
            Canteiro.nome.label("nome_canteiro"),
            LoteSementes.codigo_lote.label("codigo_lote"),
            ArvoreMatriz.nome.label("matriz_nome"),
        )
        .join(Especie, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .outerjoin(LoteSementes, Planta.id_lote_sementes == LoteSementes.id)
        .outerjoin(ArvoreMatriz, LoteSementes.id_arvore_matriz == ArvoreMatriz.id)
        .where(
            Planta.status == "SEMENTE",
            Planta.estagio_producao == APTA_TRANSFERENCIA,
            Canteiro.tipo_local == "sementeira",
        )
    )
    if id_canteiro:
        query = query.where(Planta.id_canteiro == id_canteiro)
    if id_especie:
        query = query.where(Planta.id_especie == id_especie)
    query = query.order_by(Planta.data_plantio.desc(), Planta.id).limit(limit)
    rows = (await db.execute(query)).all()
    out = []
    for row in rows:
        p = row[0]
        out.append(
            {
                "id": p.id,
                "codigo_rastreio": p.codigo_rastreio,
                "id_especie": p.id_especie,
                "especie_nome": row[1],
                "id_canteiro": p.id_canteiro,
                "nome_canteiro": row[2],
                "id_lote_sementes": p.id_lote_sementes,
                "codigo_lote": row[3],
                "matriz_nome": row[4],
                "data_plantio": p.data_plantio,
                "estagio_producao": p.estagio_producao,
                "origem": p.origem or "semeadura",
                "observacoes": p.observacoes,
            }
        )
    return out


async def get_plantas_em_desenvolvimento_sementeira(
    db: AsyncSession,
    id_canteiro: Optional[int] = None,
    id_especie: Optional[int] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    query = (
        select(
            Planta,
            Especie.nome_cientifico.label("especie_nome"),
            Canteiro.nome.label("nome_canteiro"),
            LoteSementes.codigo_lote.label("codigo_lote"),
            ArvoreMatriz.nome.label("matriz_nome"),
        )
        .join(Especie, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .outerjoin(LoteSementes, Planta.id_lote_sementes == LoteSementes.id)
        .outerjoin(ArvoreMatriz, LoteSementes.id_arvore_matriz == ArvoreMatriz.id)
        .where(
            Planta.status == "SEMENTE",
            Planta.estagio_producao == EM_DESENVOLVIMENTO,
            Canteiro.tipo_local == "sementeira",
        )
    )
    if id_canteiro:
        query = query.where(Planta.id_canteiro == id_canteiro)
    if id_especie:
        query = query.where(Planta.id_especie == id_especie)
    query = query.order_by(Planta.data_plantio.desc(), Planta.id).limit(limit)
    rows = (await db.execute(query)).all()
    out = []
    for row in rows:
        p = row[0]
        out.append(
            {
                "id": p.id,
                "codigo_rastreio": p.codigo_rastreio,
                "id_especie": p.id_especie,
                "especie_nome": row[1],
                "id_canteiro": p.id_canteiro,
                "nome_canteiro": row[2],
                "id_lote_sementes": p.id_lote_sementes,
                "codigo_lote": row[3],
                "matriz_nome": row[4],
                "data_plantio": p.data_plantio,
                "estagio_producao": p.estagio_producao,
                "origem": p.origem or "semeadura",
                "observacoes": p.observacoes,
            }
        )
    return out


async def get_plantas_em_crescimento_canteiro(
    db: AsyncSession,
    id_canteiro: Optional[int] = None,
    id_especie: Optional[int] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    query = (
        select(
            Planta,
            Especie.nome_cientifico.label("especie_nome"),
            Canteiro.nome.label("nome_canteiro"),
        )
        .join(Especie, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            Planta.status.in_(("MUDA", "JOVEM", "ADULTA")),
            Planta.estagio_producao == EM_CRESCIMENTO,
            Canteiro.tipo_local == "canteiro",
        )
    )
    if id_canteiro:
        query = query.where(Planta.id_canteiro == id_canteiro)
    if id_especie:
        query = query.where(Planta.id_especie == id_especie)
    query = query.order_by(Planta.data_germinacao.desc(), Planta.id).limit(limit)
    rows = (await db.execute(query)).all()
    out = []
    for row in rows:
        p = row[0]
        out.append(
            {
                "id": p.id,
                "codigo_rastreio": p.codigo_rastreio,
                "id_especie": p.id_especie,
                "especie_nome": row[1],
                "id_canteiro": p.id_canteiro,
                "nome_canteiro": row[2],
                "data_plantio": p.data_plantio,
                "data_germinacao": p.data_germinacao,
                "status": p.status,
                "estagio_producao": p.estagio_producao,
                "origem": p.origem or "semeadura",
                "observacoes": p.observacoes,
            }
        )
    return out


async def atualizar_estagio_producao(
    db: AsyncSession,
    payload: AtualizarEstagioRequest,
) -> Dict[str, Any]:
    atualizadas = []
    avisos: List[str] = []
    for pid in payload.ids_plantas:
        planta = await get_planta(db, pid)
        if not planta:
            raise ValueError(f"Planta {pid} não encontrada")

        if payload.estagio_producao == APTA_TRANSFERENCIA:
            if planta.status != "SEMENTE":
                raise ValueError(
                    f"Planta {planta.codigo_rastreio or pid} não está em status SEMENTE"
                )
            if planta.estagio_producao != EM_DESENVOLVIMENTO:
                raise ValueError(
                    f"Planta {planta.codigo_rastreio or pid} não está em desenvolvimento na sementeira"
                )
            if planta.id_canteiro:
                await _validar_canteiro_tipo(
                    db, planta.id_canteiro, "sementeira", "Local da planta"
                )
            planta.estagio_producao = APTA_TRANSFERENCIA

        elif payload.estagio_producao == APTA_RUSTIFICACAO:
            # Aptidão para rustificação é definida no canteiro.
            if planta.status not in DISPONIVEIS_VENDA:
                raise ValueError(
                    f"Planta {planta.codigo_rastreio or pid} não está em fase de muda comercializável"
                )
            if not planta.id_canteiro:
                raise ValueError(f"Planta {planta.codigo_rastreio or pid} não possui canteiro associado")
            await _validar_canteiro_tipo(db, planta.id_canteiro, "canteiro", "Local da planta")
            if planta.estagio_producao != EM_CRESCIMENTO:
                raise ValueError(
                    f"Planta {planta.codigo_rastreio or pid} não está em crescimento no canteiro"
                )
            planta.estagio_producao = APTA_RUSTIFICACAO

        elif payload.estagio_producao == APTA_VENDA:
            if planta.status not in DISPONIVEIS_VENDA:
                raise ValueError(
                    f"Planta {planta.codigo_rastreio or pid} não está em fase de muda comercializável"
                )
            # Regra operacional: só vende após concluir rustificação.
            if planta.estagio_producao != EM_RUSTIFICACAO:
                raise ValueError(
                    f"Planta {planta.codigo_rastreio or pid} ainda não concluiu a rustificação"
                )
            if not planta.id_canteiro:
                raise ValueError(f"Planta {planta.codigo_rastreio or pid} não possui canteiro associado")
            await _validar_canteiro_tipo(
                db, planta.id_canteiro, "rustificacao", "Área de rustificação"
            )
            for msg in await avisos_liberar_venda(db, planta):
                if msg not in avisos:
                    avisos.append(msg)
            planta.estagio_producao = APTA_VENDA
        else:
            raise ValueError("Estágio de destino inválido")

        atualizadas.append(planta.id)

    await db.commit()
    return {
        "atualizadas": len(atualizadas),
        "ids_plantas": atualizadas,
        "avisos": avisos,
    }


async def get_plantas_em_rustificacao(
    db: AsyncSession,
    id_canteiro: Optional[int] = None,
    id_especie: Optional[int] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    query = (
        select(
            Planta,
            Especie.nome_cientifico.label("especie_nome"),
            Canteiro.nome.label("nome_canteiro"),
        )
        .join(Especie, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            Planta.status.in_(DISPONIVEIS_VENDA),
            Planta.estagio_producao == EM_RUSTIFICACAO,
            Canteiro.tipo_local == "rustificacao",
        )
    )
    if id_canteiro:
        query = query.where(Planta.id_canteiro == id_canteiro)
    if id_especie:
        query = query.where(Planta.id_especie == id_especie)
    query = query.order_by(Planta.data_germinacao.desc(), Planta.id).limit(limit)
    rows = (await db.execute(query)).all()
    out = []
    for row in rows:
        p = row[0]
        out.append(
            {
                "id": p.id,
                "codigo_rastreio": p.codigo_rastreio,
                "id_especie": p.id_especie,
                "especie_nome": row[1],
                "id_canteiro": p.id_canteiro,
                "nome_canteiro": row[2],
                "data_plantio": p.data_plantio,
                "data_germinacao": p.data_germinacao,
                "status": p.status,
                "estagio_producao": p.estagio_producao,
                "origem": p.origem or "semeadura",
                "observacoes": p.observacoes,
            }
        )
    return out


async def transferir_para_rustificacao(
    db: AsyncSession,
    payload: TransferirRustificacaoRequest,
    id_funcionario: Optional[int] = None,
) -> Dict[str, Any]:
    # Existe apenas uma área de rustificação (pegamos a primeira ativa).
    rust_areas = await db.execute(
        select(Canteiro).where(Canteiro.tipo_local == "rustificacao", Canteiro.ativo == True).order_by(Canteiro.id).limit(1)
    )
    dest = rust_areas.scalars().first()
    if not dest:
        raise ValueError("Nenhuma área de rustificação cadastrada (tipo_local='rustificacao').")

    transferidas = []
    avisos: List[str] = []

    for pid in payload.ids_plantas:
        planta = await get_planta(db, pid)
        if not planta:
            raise ValueError(f"Planta {pid} não encontrada")
        if planta.status not in DISPONIVEIS_VENDA:
            raise ValueError(
                f"Planta {planta.codigo_rastreio or pid} não está em fase de muda"
            )
        if planta.estagio_producao != APTA_RUSTIFICACAO:
            raise ValueError(
                f"Planta {planta.codigo_rastreio or pid} deve estar apta para rustificação"
            )
        if not planta.id_canteiro:
            raise ValueError(f"Planta {planta.codigo_rastreio or pid} não possui canteiro associado")
        await _validar_canteiro_tipo(db, planta.id_canteiro, "canteiro", "Canteiro de origem")
        for msg in await avisos_transferir_rustificacao(db, planta):
            if msg not in avisos:
                avisos.append(msg)

        db.add(
            TransferenciaPlanta(
                id_planta=planta.id,
                id_canteiro_origem=planta.id_canteiro,
                id_canteiro_destino=dest.id,
                status_anterior=planta.status,
                status_novo=planta.status,
                id_funcionario=id_funcionario,
                observacoes=payload.observacoes or "Transferência para rustificação",
            )
        )
        planta.id_canteiro = dest.id
        planta.estagio_producao = ESTAGIO_INICIAL_RUSTIFICACAO
        _marcar_inicio_estagio(planta)
        transferidas.append(planta.id)

    await db.commit()
    return {
        "transferidas": len(transferidas),
        "ids_plantas": transferidas,
        "avisos": avisos,
    }


async def get_plantas_aptas_rustificacao_canteiro(
    db: AsyncSession,
    id_canteiro: Optional[int] = None,
    id_especie: Optional[int] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    query = (
        select(
            Planta,
            Especie.nome_cientifico.label("especie_nome"),
            Canteiro.nome.label("nome_canteiro"),
        )
        .join(Especie, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            Planta.status.in_(DISPONIVEIS_VENDA),
            Planta.estagio_producao == APTA_RUSTIFICACAO,
            Canteiro.tipo_local == "canteiro",
        )
    )
    if id_canteiro:
        query = query.where(Planta.id_canteiro == id_canteiro)
    if id_especie:
        query = query.where(Planta.id_especie == id_especie)
    query = query.order_by(Planta.data_germinacao.desc(), Planta.id).limit(limit)
    rows = (await db.execute(query)).all()
    out = []
    for row in rows:
        p = row[0]
        out.append(
            {
                "id": p.id,
                "codigo_rastreio": p.codigo_rastreio,
                "id_especie": p.id_especie,
                "especie_nome": row[1],
                "id_canteiro": p.id_canteiro,
                "nome_canteiro": row[2],
                "data_plantio": p.data_plantio,
                "data_germinacao": p.data_germinacao,
                "status": p.status,
                "estagio_producao": p.estagio_producao,
                "origem": p.origem or "semeadura",
                "observacoes": p.observacoes,
            }
        )
    return out


async def promover_mudas(
    db: AsyncSession,
    payload: PromoverMudasRequest,
    id_funcionario: Optional[int] = None,
) -> Dict[str, Any]:
    dest = await _validar_canteiro_tipo(
        db, payload.id_canteiro_destino, "canteiro", "Canteiro de destino"
    )
    data_germ = payload.data_germinacao or date.today()
    transferidas = []

    for pid in payload.ids_plantas:
        planta = await get_planta(db, pid)
        if not planta:
            raise ValueError(f"Planta {pid} não encontrada")
        if planta.status != "SEMENTE":
            raise ValueError(
                f"Planta {planta.codigo_rastreio or pid} não está em status SEMENTE"
            )
        if planta.estagio_producao != APTA_TRANSFERENCIA:
            raise ValueError(
                f"Planta {planta.codigo_rastreio or pid} ainda não está apta para transferência"
            )
        if planta.id_canteiro:
            await _validar_canteiro_tipo(
                db, planta.id_canteiro, "sementeira", "Canteiro de origem"
            )

        db.add(
            TransferenciaPlanta(
                id_planta=planta.id,
                id_canteiro_origem=planta.id_canteiro,
                id_canteiro_destino=dest.id,
                status_anterior=planta.status,
                status_novo="MUDA",
                id_funcionario=id_funcionario,
                observacoes=payload.observacoes,
            )
        )
        planta.status = "MUDA"
        planta.estagio_producao = ESTAGIO_INICIAL_CANTEIRO
        planta.id_canteiro = dest.id
        planta.data_germinacao = data_germ
        _marcar_inicio_estagio(planta, data_germ)
        transferidas.append(planta.id)

    await db.commit()
    return {"transferidas": len(transferidas), "ids_plantas": transferidas}


async def cadastro_lote_plantas(
    db: AsyncSession, payload: CadastroLotePlantasRequest
) -> Dict[str, Any]:
    tipo_canteiro = "sementeira" if payload.status == "SEMENTE" else "canteiro"
    await _validar_canteiro_tipo(db, payload.id_canteiro, tipo_canteiro, "Canteiro")

    especie = await db.get(Especie, payload.id_especie)
    if not especie:
        raise ValueError("Espécie não encontrada")

    if payload.id_lote_sementes:
        lote = await db.get(LoteSementes, payload.id_lote_sementes)
        if not lote:
            raise ValueError("Lote de sementes não encontrado")

    prefixo = payload.prefixo_codigo or (
        "COM" if payload.origem == "compra" else payload.origem[:3].upper()
    )
    data_plantio = payload.data_plantio or date.today()
    ids = []

    for i in range(payload.quantidade):
        codigo = f"{prefixo}-{payload.id_especie}-{date.today().year}-{i + 1:04d}"[:20]
        db_planta = Planta(
            id_especie=payload.id_especie,
            id_canteiro=payload.id_canteiro,
            id_lote_sementes=payload.id_lote_sementes,
            codigo_rastreio=codigo,
            data_plantio=data_plantio,
            data_germinacao=payload.data_germinacao,
            data_inicio_estagio_atual=data_plantio,
            status=payload.status,
            estagio_producao=(
                ESTAGIO_INICIAL_SEMENTEIRA
                if payload.status == "SEMENTE"
                else ESTAGIO_INICIAL_CANTEIRO
            ),
            origem=payload.origem,
            preco_venda=payload.preco_venda,
            observacoes=payload.observacoes,
        )
        db.add(db_planta)
        await db.flush()
        ids.append(db_planta.id)

    await db.commit()
    return {"criadas": len(ids), "ids_plantas": ids}


async def delete_planta(db: AsyncSession, planta_id: int) -> Optional[Planta]:
    db_planta = await get_planta(db, planta_id)
    if not db_planta:
        return None
    
    await db.delete(db_planta)
    await db.commit()
    return db_planta