"""
Sincroniza URLs de imagens speciesLink para todas as espécies da biblioteca.

Uso (dentro do container ou com DATABASE_URL no .env):
  python scripts/sync_specieslink_imagens.py
  python scripts/sync_specieslink_imagens.py --forcar
"""

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import AsyncSessionLocal
from app.crud.especies_imagens import sincronizar_imagens_biblioteca


async def main(forcar: bool) -> None:
    async with AsyncSessionLocal() as db:
        resultado = await sincronizar_imagens_biblioteca(
            db,
            apenas_sem_cache=not forcar,
            forcar=forcar,
            limite=500,
        )
    print(resultado)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--forcar", action="store_true", help="Ignora cache e reconsulta tudo")
    args = parser.parse_args()
    asyncio.run(main(args.forcar))
