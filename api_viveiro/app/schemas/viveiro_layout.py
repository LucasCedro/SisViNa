from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ViveiroLayoutOut(BaseModel):
    layout: Dict[str, Any]
    atualizado_em: Optional[datetime] = None

    class Config:
        orm_mode = True


class ViveiroLayoutSave(BaseModel):
    layout: Dict[str, Any]
