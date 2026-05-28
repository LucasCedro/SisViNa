"""Verifica se JPGs locais da biblioteca existem no disco (evita capa 404)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from app.config import settings

_LOCAL_TEMPLATE = re.compile(
    r"^/assets/biblioteca/especies/(arvores|sementes|folhas)/\d+\.jpg$",
    re.I,
)


def _public_root() -> Optional[Path]:
    raw = (getattr(settings, "BIBLIOTECA_PUBLIC_ROOT", None) or "").strip()
    if raw:
        p = Path(raw)
        return p if p.is_dir() else None
    # Monorepo: api_viveiro/../sistema-viveiro-nativas/public
    candidate = Path(__file__).resolve().parents[2].parent / "sistema-viveiro-nativas" / "public"
    return candidate if candidate.is_dir() else None


def url_local_biblioteca_existe(url: str) -> bool:
    """
    Caminhos padrão da migração (/assets/biblioteca/especies/.../ID.jpg)
    só entram se o arquivo existir em public/.
    """
    u = (url or "").strip()
    if not u.startswith("/assets/"):
        return False
    if not _LOCAL_TEMPLATE.match(u):
        return True
    root = _public_root()
    if not root:
        return False
    return (root / u.lstrip("/")).is_file()
