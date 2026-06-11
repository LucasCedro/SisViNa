#!/usr/bin/env python3
"""
ETL Flora do Brasil (JBRJ) → tabela especies_master.

Standalone: não depende do FastAPI. Popula referência taxonômica imutável.

Uso:
  cd api_viveiro/scripts/jbrj_flora_etl
  pip install -r requirements.txt
  copy especies_input.example.txt especies_input.txt
  python import_species_master.py

Variável de ambiente: DATABASE_URL (postgresql://...)
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import requests
from tenacity import RetryError

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from db import connect, ensure_table, save_to_db  # noqa: E402
from jbrj_client import JbrjFloraClient  # noqa: E402
from normalizacao import normalize_key, sanitize_input_name  # noqa: E402

INPUT_FILE = SCRIPT_DIR / "especies_input.txt"
FAILED_LOG = SCRIPT_DIR / "failed_species.log"


def load_input_names() -> list[str]:
    if not INPUT_FILE.exists():
        print(f"[ERRO] Arquivo não encontrado: {INPUT_FILE}")
        print("       Copie especies_input.example.txt → especies_input.txt")
        sys.exit(1)

    names: list[str] = []
    seen: set[str] = set()
    for line in INPUT_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("#"):
            continue
        limpo = sanitize_input_name(line)
        if not limpo:
            continue
        chave = normalize_key(limpo)
        if chave in seen:
            continue
        seen.add(chave)
        names.append(limpo)
    if not names:
        print(f"[ERRO] {INPUT_FILE} está vazio.")
        sys.exit(1)
    return names


def log_failed(name: str, reason: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    with FAILED_LOG.open("a", encoding="utf-8") as f:
        f.write(f"{ts}\t{name}\t{reason}\n")


def main() -> None:
    names = load_input_names()
    total = len(names)
    client = JbrjFloraClient(delay_ok=2.0)

    print("=" * 60)
    print(" SisViNa - ETL Flora do Brasil -> especies_master")
    print(f" Entradas: {total} | API: servicos.jbrj.gov.br/v2/flora")
    print("=" * 60)

    conn = connect()
    try:
        ensure_table(conn)
    except Exception as exc:
        print(f"[ERRO] Banco: {exc}")
        sys.exit(1)

    ok = 0
    fail = 0

    for idx, name in enumerate(names, start=1):
        prefix = f"{idx}/{total} - {name}"
        print(f"{prefix}...", end=" ", flush=True)
        try:
            payload = client.fetch_and_transform(name)
            save_to_db(conn, payload)
            ok += 1
            extras = []
            if payload.get("estados_ocorrencia"):
                extras.append(f"UFs={len(payload['estados_ocorrencia'])}")
            if payload.get("meses_frutificacao"):
                extras.append(f"frut={payload['meses_frutificacao']}")
            suffix = f" ({', '.join(extras)})" if extras else ""
            print(f"[OK] -> {payload['nome_cientifico']}{suffix}")
        except RetryError as exc:
            fail += 1
            reason = f"retry esgotado: {exc.last_attempt.exception()}"
            log_failed(name, reason)
            print(f"[FALHA] {reason}")
        except requests.HTTPError as exc:
            fail += 1
            code = exc.response.status_code if exc.response is not None else "?"
            reason = f"HTTP {code}: {exc}"
            log_failed(name, reason)
            print(f"[FALHA] {reason}")
        except Exception as exc:
            fail += 1
            reason = str(exc)
            log_failed(name, reason)
            print(f"[FALHA] {reason}")

    conn.close()

    print("-" * 60)
    print(f"Concluído: {ok} OK, {fail} falhas.")
    if fail:
        print(f"Detalhes em: {FAILED_LOG}")
    print("=" * 60)


if __name__ == "__main__":
    main()
