import json
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.viveiro_layout import ViveiroLayout


async def get_layout(db: AsyncSession, id_viveiro: Optional[int] = None) -> Dict[str, Any]:
    if id_viveiro is None:
        return {}
    result = await db.execute(select(ViveiroLayout).where(ViveiroLayout.id_viveiro == id_viveiro))
    row = result.scalars().first()
    if not row or not row.layout_json:
        return {}
    try:
        return json.loads(row.layout_json)
    except json.JSONDecodeError:
        return {}


async def save_layout(
    db: AsyncSession, layout: Dict[str, Any], id_viveiro: Optional[int] = None
) -> ViveiroLayout:
    if id_viveiro is None:
        raise ValueError("id_viveiro é obrigatório para salvar layout")
    result = await db.execute(select(ViveiroLayout).where(ViveiroLayout.id_viveiro == id_viveiro))
    row = result.scalars().first()
    payload = json.dumps(layout, ensure_ascii=False)
    if row:
        row.layout_json = payload
    else:
        row = ViveiroLayout(id_viveiro=id_viveiro, layout_json=payload)
        db.add(row)
    await db.commit()
    await db.refresh(row)
    return row
