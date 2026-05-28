"""
Remove URLs inválidas (páginas de herbário etc.) do cache JSON.

Uso: python scripts/limpar_imagens_cache_invalidas.py
"""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.especie_biblioteca import EspecieBiblioteca
from app.services.specieslink_service import filtrar_urls_imagem


async def main() -> None:
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(EspecieBiblioteca))).scalars().all()
        alterados = 0
        for bib in rows:
            brutas = bib.imagens_externas if isinstance(bib.imagens_externas, list) else []
            limpas = filtrar_urls_imagem([u for u in brutas if isinstance(u, str)])
            if limpas != brutas:
                bib.imagens_externas = limpas if limpas else None
                alterados += 1
        await db.commit()
    print({"registros_ajustados": alterados, "total": len(rows)})


if __name__ == "__main__":
    asyncio.run(main())
