"""Cria o usuário admin padrão (admin / Admin@123) se não existir."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.bootstrap import ensure_default_admin


async def main() -> None:
    await ensure_default_admin()
    print("OK: usuário admin disponível (admin / Admin@123)")


if __name__ == "__main__":
    asyncio.run(main())
