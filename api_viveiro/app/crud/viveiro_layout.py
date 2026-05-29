import json
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.viveiro_layout import ViveiroLayout

LAYOUT_ID = 1


async def get_layout(db: AsyncSession) -> Dict[str, Any]:
    result = await db.execute(select(ViveiroLayout).where(ViveiroLayout.id == LAYOUT_ID))
    row = result.scalars().first()
    if not row or not row.layout_json:
        return {}
    try:
        return json.loads(row.layout_json)
    except json.JSONDecodeError:
        return {}


async def save_layout(db: AsyncSession, layout: Dict[str, Any]) -> ViveiroLayout:
    result = await db.execute(select(ViveiroLayout).where(ViveiroLayout.id == LAYOUT_ID))
    row = result.scalars().first()
    payload = json.dumps(layout, ensure_ascii=False)
    if row:
        row.layout_json = payload
    else:
        row = ViveiroLayout(id=LAYOUT_ID, layout_json=payload)
        db.add(row)
    await db.commit()
    await db.refresh(row)
    return row
