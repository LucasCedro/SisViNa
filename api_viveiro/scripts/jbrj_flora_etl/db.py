"""Persistência em especies_master (PostgreSQL)."""

from __future__ import annotations

import os
from typing import Any, Dict

import psycopg2

DEFAULT_DATABASE_URL = "postgresql://viveiro_admin:senha_segura_aqui@localhost:5432/viveiro_db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS especies_master (
    id SERIAL PRIMARY KEY,
    taxon_id_jbrj INTEGER UNIQUE,
    nome_cientifico TEXT NOT NULL,
    nome_cientifico_chave TEXT NOT NULL UNIQUE,
    familia TEXT,
    nomes_populares TEXT[] NOT NULL DEFAULT '{}',
    biomas TEXT[] NOT NULL DEFAULT '{}',
    estados_ocorrencia TEXT[] NOT NULL DEFAULT '{}',
    status_ameaca TEXT,
    meses_floracao INTEGER[] NOT NULL DEFAULT '{}',
    meses_frutificacao INTEGER[] NOT NULL DEFAULT '{}',
    forma_vida TEXT[] NOT NULL DEFAULT '{}',
    habitat TEXT[] NOT NULL DEFAULT '{}',
    notas_origem TEXT,
    fonte TEXT NOT NULL DEFAULT 'JBRJ_FLORA',
    ultima_atualizacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_especies_master_taxon_jbrj ON especies_master (taxon_id_jbrj);
CREATE INDEX IF NOT EXISTS idx_especies_nome ON especies_master (nome_cientifico);
CREATE INDEX IF NOT EXISTS idx_especies_populares ON especies_master USING GIN (nomes_populares);
"""

UPSERT_SQL = """
INSERT INTO especies_master (
    taxon_id_jbrj,
    nome_cientifico,
    nome_cientifico_chave,
    familia,
    nomes_populares,
    biomas,
    estados_ocorrencia,
    status_ameaca,
    meses_floracao,
    meses_frutificacao,
    forma_vida,
    habitat,
    notas_origem,
    fonte,
    ultima_atualizacao
) VALUES (
    %(taxon_id_jbrj)s,
    %(nome_cientifico)s,
    %(nome_cientifico_chave)s,
    %(familia)s,
    %(nomes_populares)s,
    %(biomas)s,
    %(estados_ocorrencia)s,
    %(status_ameaca)s,
    %(meses_floracao)s,
    %(meses_frutificacao)s,
    %(forma_vida)s,
    %(habitat)s,
    %(notas_origem)s,
    'JBRJ_FLORA',
    CURRENT_TIMESTAMP
)
ON CONFLICT (nome_cientifico_chave) DO UPDATE SET
    taxon_id_jbrj = EXCLUDED.taxon_id_jbrj,
    nome_cientifico = EXCLUDED.nome_cientifico,
    familia = EXCLUDED.familia,
    nomes_populares = EXCLUDED.nomes_populares,
    biomas = EXCLUDED.biomas,
    estados_ocorrencia = EXCLUDED.estados_ocorrencia,
    status_ameaca = EXCLUDED.status_ameaca,
    meses_floracao = EXCLUDED.meses_floracao,
    meses_frutificacao = EXCLUDED.meses_frutificacao,
    forma_vida = EXCLUDED.forma_vida,
    habitat = EXCLUDED.habitat,
    notas_origem = EXCLUDED.notas_origem,
    ultima_atualizacao = CURRENT_TIMESTAMP;
"""


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL") or os.environ.get("SISVINA_DATABASE_URL")
    if not url:
        return DEFAULT_DATABASE_URL
    return url.replace("postgresql+asyncpg://", "postgresql://")


def ensure_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
    conn.commit()


def save_to_db(conn, payload: Dict[str, Any]) -> None:
    params = {
        **payload,
        "nomes_populares": payload.get("nomes_populares") or [],
        "biomas": payload.get("biomas") or [],
        "estados_ocorrencia": payload.get("estados_ocorrencia") or [],
        "meses_floracao": payload.get("meses_floracao") or [],
        "meses_frutificacao": payload.get("meses_frutificacao") or [],
        "forma_vida": payload.get("forma_vida") or [],
        "habitat": payload.get("habitat") or [],
    }
    with conn.cursor() as cur:
        cur.execute(UPSERT_SQL, params)
    conn.commit()


def connect():
    return psycopg2.connect(get_database_url())
