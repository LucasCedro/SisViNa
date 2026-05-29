"""Rótulos curtos de espécies para listagens e gráficos."""

from typing import Optional


def formatar_nome_popular(nome: Optional[str]) -> Optional[str]:
    """Primeiro sinônimo, sem vírgulas extras; hífens viram espaço (melhor em gráficos)."""
    if not nome:
        return nome
    parte = nome.split(",")[0].strip()
    return parte.replace("-", " ") if parte else nome
