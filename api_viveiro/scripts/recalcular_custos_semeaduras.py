"""Recalcula CMV de semeaduras/plantas após correção do rateio mensal."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import AsyncSessionLocal
from app.services.custeio import redistribuir_cif_parque


async def main() -> int:
    async with AsyncSessionLocal() as db:
        resultado = await redistribuir_cif_parque(db)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
