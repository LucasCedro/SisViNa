from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.arvores_matriz import ArvoreMatriz
from app.models.coletas_sementes import ColetaSementes
from app.models.lotes_sementes import LoteSementes
from app.models.testes_sementes import TesteSementes
from app.schemas.testes_sementes import TesteSementesCreate, TesteSementesUpdate


def _para_resposta(teste: TesteSementes, taxa_especie: Optional[float] = None) -> dict:
    lote = teste.lote
    arvore = lote.arvore_matriz if lote else None
    especie = lote.especie if lote else None
    from app.utils.especies_display import formatar_nome_popular

    nome_especie = None
    if especie:
        nome_especie = formatar_nome_popular(especie.nome_popular) or especie.nome_cientifico
    return {
        "id": teste.id,
        "id_lote_sementes": teste.id_lote_sementes,
        "codigo_lote": lote.codigo_lote if lote else "",
        "id_arvore_matriz": lote.id_arvore_matriz if lote else 0,
        "matriz_nome": arvore.nome if arvore else "",
        "id_especie": lote.id_especie if lote else None,
        "especie_nome": nome_especie,
        "data_teste": teste.data_teste,
        "tipo_teste": teste.tipo_teste,
        "metodologia": teste.metodologia,
        "repeticoes": teste.repeticoes or 1,
        "sementes_avaliadas": teste.sementes_avaliadas,
        "percentual_resultado": float(teste.percentual_resultado),
        "observacoes": teste.observacoes,
        "id_funcionario": teste.id_funcionario,
        "funcionario_nome": teste.funcionario.nome if teste.funcionario else "",
        "data_registro": teste.data_registro,
        "taxa_germinacao_especie_media": taxa_especie,
    }


async def calcular_taxa_germinacao_especie(
    db: AsyncSession, id_especie: int
) -> Optional[float]:
    """Média do último teste de germinação por lote ativo da espécie."""
    result = await db.execute(
        select(LoteSementes.id).where(
            LoteSementes.id_especie == id_especie,
            LoteSementes.status != "descartado",
        )
    )
    lot_ids = [row[0] for row in result.all()]
    if not lot_ids:
        return None
    valores: List[float] = []
    for lid in lot_ids:
        r = await db.execute(
            select(TesteSementes.percentual_resultado)
            .where(
                TesteSementes.id_lote_sementes == lid,
                TesteSementes.tipo_teste == "germinacao",
            )
            .order_by(TesteSementes.data_teste.desc(), TesteSementes.id.desc())
            .limit(1)
        )
        v = r.scalar_one_or_none()
        if v is not None:
            valores.append(float(v))
    if not valores:
        return None
    return round(sum(valores) / len(valores), 2)


async def _sync_taxa_matriz(db: AsyncSession, id_arvore_matriz: int) -> None:
    result = await db.execute(
        select(TesteSementes.percentual_resultado)
        .join(LoteSementes, TesteSementes.id_lote_sementes == LoteSementes.id)
        .where(
            LoteSementes.id_arvore_matriz == id_arvore_matriz,
            TesteSementes.tipo_teste == "germinacao",
        )
        .order_by(TesteSementes.data_teste.desc(), TesteSementes.id.desc())
        .limit(1)
    )
    valor = result.scalar_one_or_none()
    arvore = await db.get(ArvoreMatriz, id_arvore_matriz)
    if arvore:
        arvore.taxa_germinacao = float(valor) if valor is not None else None


async def get_teste(db: AsyncSession, teste_id: int) -> Optional[TesteSementes]:
    result = await db.execute(
        select(TesteSementes)
        .options(
            joinedload(TesteSementes.lote).joinedload(LoteSementes.arvore_matriz),
            joinedload(TesteSementes.lote).joinedload(LoteSementes.especie),
            joinedload(TesteSementes.funcionario),
        )
        .where(TesteSementes.id == teste_id)
    )
    return result.scalars().first()


async def get_testes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 2000,
    id_lote_sementes: Optional[int] = None,
    id_arvore_matriz: Optional[int] = None,
) -> List[TesteSementes]:
    query = (
        select(TesteSementes)
        .join(LoteSementes, TesteSementes.id_lote_sementes == LoteSementes.id)
        .options(
            joinedload(TesteSementes.lote).joinedload(LoteSementes.arvore_matriz),
            joinedload(TesteSementes.lote).joinedload(LoteSementes.especie),
            joinedload(TesteSementes.funcionario),
        )
        .order_by(TesteSementes.data_teste.desc(), TesteSementes.id.desc())
    )
    if id_lote_sementes:
        query = query.where(TesteSementes.id_lote_sementes == id_lote_sementes)
    if id_arvore_matriz:
        query = query.where(LoteSementes.id_arvore_matriz == id_arvore_matriz)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().unique().all()


async def _devolver_sobra_reserva_ao_lote(
    db: AsyncSession, lote: LoteSementes, sementes_avaliadas: Optional[int]
) -> int:
    """Liquida a reserva da coleta: sobra retorna ao lote comercial."""
    if not lote.id_coleta_sementes:
        return 0
    coleta = await db.get(ColetaSementes, lote.id_coleta_sementes)
    if not coleta:
        return 0
    reserva = int(coleta.sementes_reservadas_teste or 0)
    if reserva <= 0:
        return 0
    usadas = int(sementes_avaliadas or 0)
    if usadas > reserva:
        raise ValueError(
            f"Sementes avaliadas ({usadas}) não podem exceder a reserva da coleta ({reserva})"
        )
    sobra = reserva - usadas
    if sobra > 0:
        lote.quantidade_disponivel = int(lote.quantidade_disponivel or 0) + sobra
        lote.quantidade_inicial = int(lote.quantidade_inicial or 0) + sobra
    coleta.sementes_reservadas_teste = 0
    return sobra


async def create_teste(db: AsyncSession, payload: TesteSementesCreate, id_funcionario: int) -> dict:
    """Registra qualidade do lote. Sobra da reserva (coleta) volta ao estoque do lote."""
    lote = await db.get(LoteSementes, payload.id_lote_sementes)
    if not lote:
        raise ValueError("Lote não encontrado")

    dados = payload.dict()
    db_teste = TesteSementes(
        id_lote_sementes=dados["id_lote_sementes"],
        data_teste=dados["data_teste"],
        tipo_teste=dados["tipo_teste"],
        metodologia=dados.get("metodologia"),
        repeticoes=dados.get("repeticoes") or 1,
        sementes_avaliadas=dados.get("sementes_avaliadas"),
        percentual_resultado=dados["percentual_resultado"],
        observacoes=dados.get("observacoes"),
        id_funcionario=id_funcionario,
    )
    db.add(db_teste)
    if dados["tipo_teste"] == "germinacao":
        await _devolver_sobra_reserva_ao_lote(db, lote, dados.get("sementes_avaliadas"))
    await db.commit()
    if dados["tipo_teste"] == "germinacao":
        await _sync_taxa_matriz(db, lote.id_arvore_matriz)
        await db.commit()
    teste = await get_teste(db, db_teste.id)
    taxa = None
    if lote.id_especie and dados["tipo_teste"] == "germinacao":
        taxa = await calcular_taxa_germinacao_especie(db, lote.id_especie)
    return _para_resposta(teste, taxa)


async def update_teste(
    db: AsyncSession, teste_id: int, payload: TesteSementesUpdate
) -> Optional[dict]:
    db_teste = await get_teste(db, teste_id)
    if not db_teste:
        return None
    id_matriz = db_teste.lote.id_arvore_matriz
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_teste, field, value)
    await db.commit()
    await _sync_taxa_matriz(db, id_matriz)
    await db.commit()
    db_teste = await get_teste(db, teste_id)
    taxa = None
    if db_teste.lote.id_especie:
        taxa = await calcular_taxa_germinacao_especie(db, db_teste.lote.id_especie)
    return _para_resposta(db_teste, taxa)


async def delete_teste(db: AsyncSession, teste_id: int) -> Optional[dict]:
    db_teste = await get_teste(db, teste_id)
    if not db_teste:
        return None
    id_matriz = db_teste.lote.id_arvore_matriz
    resp = _para_resposta(db_teste)
    await db.delete(db_teste)
    await db.commit()
    await _sync_taxa_matriz(db, id_matriz)
    await db.commit()
    return resp
