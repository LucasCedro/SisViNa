"""Conversão de unidades para CMV — volume (substrato) e peso (hidrogel)."""

from __future__ import annotations

from typing import Optional, Tuple

from app.models.insumos import Insumo


def normalizar_unidade_insumo(unidade: Optional[str]) -> str:
    u = (unidade or "").strip().lower().replace(" ", "")
    aliases = {
        "litro": "l",
        "litros": "l",
        "lt": "l",
        "mililitro": "ml",
        "mililitros": "ml",
        "m³": "m3",
        "metro³": "m3",
        "grama": "g",
        "gramas": "g",
        "quilo": "kg",
        "quilos": "kg",
        "quilograma": "kg",
        "quilogramas": "kg",
    }
    return aliases.get(u, u)


def volume_substrato_litros(quantidade: float, recipiente: str) -> float:
    """Premissa em ml (tubete) ou L (saquinho) → litros para custo."""
    qtd = float(quantidade or 0)
    if qtd <= 0:
        return 0.0
    if (recipiente or "").lower() == "saquinho":
        return qtd
    return qtd / 1000.0


def custo_insumo_volume(
    qtd_litros: float,
    insumo: Insumo,
    preco_unitario: float,
    densidade_kg_l: float = 0,
) -> Tuple[float, str]:
    """Custo de substrato: consumo em litros × preço do estoque (com conversão se kg)."""
    if qtd_litros <= 0 or preco_unitario <= 0:
        return 0.0, ""

    un = normalizar_unidade_insumo(insumo.unidade_medida)
    pu = float(preco_unitario)

    if un in ("l",):
        total = qtd_litros * pu
        return round(total, 4), f"{qtd_litros:.3f} L × R$ {pu:.4f}/L"

    if un == "ml":
        total = qtd_litros * 1000 * pu
        return round(total, 4), f"{qtd_litros:.3f} L ({qtd_litros * 1000:.0f} ml) × R$ {pu:.4f}/ml"

    if un == "m3":
        total = (qtd_litros / 1000) * pu
        return round(total, 4), f"{qtd_litros:.3f} L ÷ 1000 × R$ {pu:.4f}/m³"

    if un == "kg":
        dens = float(densidade_kg_l or 0)
        if dens <= 0:
            return (
                0.0,
                "cadastre o substrato em litros (L) no estoque ou informe a densidade aparente (kg/L)",
            )
        qtd_kg = qtd_litros * dens
        total = qtd_kg * pu
        return (
            round(total, 4),
            f"{qtd_litros:.3f} L × {dens:.3f} kg/L × R$ {pu:.4f}/kg",
        )

    return (
        0.0,
        f"unidade do estoque ({insumo.unidade_medida or '?'}) incompatível — use L ou kg com densidade",
    )


def custo_insumo_peso(
    qtd_gramas: float,
    insumo: Insumo,
    preco_unitario: float,
) -> Tuple[float, str]:
    """Custo de hidrogel/aditivo sólido: consumo em gramas × preço do estoque."""
    qtd_g = float(qtd_gramas or 0)
    if qtd_g <= 0 or preco_unitario <= 0:
        return 0.0, ""

    un = normalizar_unidade_insumo(insumo.unidade_medida)
    pu = float(preco_unitario)

    if un == "g":
        total = qtd_g * pu
        return round(total, 4), f"{qtd_g:.2f} g × R$ {pu:.4f}/g"

    if un == "kg":
        total = (qtd_g / 1000) * pu
        return round(total, 4), f"{qtd_g:.2f} g ÷ 1000 × R$ {pu:.4f}/kg"

    if un in ("l", "ml"):
        return (
            0.0,
            "hidrogel no estoque deve estar em g ou kg — não em volume",
        )

    total = qtd_g * pu
    return round(total, 4), f"{qtd_g:.2f} × R$ {pu:.4f}/{insumo.unidade_medida or 'un'}"


def substrato_medicao_por_peso(insumo: Insumo) -> bool:
    """Estoque em kg/g → premissa em gramas por recipiente (sem densidade)."""
    return normalizar_unidade_insumo(insumo.unidade_medida) in ("kg", "g")


def consumo_substrato_por_muda(
    qtd_premissa: float,
    recipiente: str,
    insumo: Insumo,
) -> Tuple[float, str]:
    """
    Converte dosagem da premissa para a unidade do estoque, por muda.

    Estoque em kg/g: qtd_premissa = gramas por recipiente (estimativa operacional).
    Estoque em L/ml/m³: qtd_premissa = ml (tubete) ou litros (saquinho).
    """
    qtd = float(qtd_premissa or 0)
    if qtd <= 0:
        return 0.0, "dosagem zerada na premissa de substrato"

    un = normalizar_unidade_insumo(insumo.unidade_medida)

    if substrato_medicao_por_peso(insumo):
        gramas = qtd
        if un == "g":
            return round(gramas, 4), f"{gramas:.2f} g"
        kg = gramas / 1000
        return round(kg, 4), f"{gramas:.2f} g ({kg:.4f} kg)"

    litros = volume_substrato_litros(qtd, recipiente)
    if litros <= 0:
        return 0.0, "dosagem zerada na premissa de substrato"

    if un == "l":
        return round(litros, 4), f"{litros:.4f} L"
    if un == "ml":
        ml = litros * 1000
        return round(ml, 4), f"{ml:.2f} ml"
    if un == "m3":
        m3 = litros / 1000
        return round(m3, 6), f"{m3:.6f} m³"

    return (
        0.0,
        f"unidade do estoque ({insumo.unidade_medida or '?'}) incompatível — use kg ou L",
    )


def custo_substrato_por_recipiente(
    qtd_premissa: float,
    recipiente: str,
    insumo: Insumo,
    preco_unitario: float,
) -> Tuple[float, str]:
    """Custo de substrato por recipiente — sem densidade aparente."""
    qtd_estoque, det_q = consumo_substrato_por_muda(qtd_premissa, recipiente, insumo)
    if qtd_estoque <= 0:
        return 0.0, det_q
    pu = float(preco_unitario)
    if pu <= 0:
        return 0.0, "registre entrada do substrato em Estoques"
    total = round(qtd_estoque * pu, 4)
    un = insumo.unidade_medida or "un"
    return total, f"{det_q} × R$ {pu:.4f}/{un}"


def quantidade_substrato_em_unidade_estoque(
    qtd_premissa: float,
    recipiente: str,
    insumo: Insumo,
    densidade_kg_l: float = 0,
) -> Tuple[float, str]:
    """Compatibilidade — ignora densidade; use consumo_substrato_por_muda."""
    return consumo_substrato_por_muda(qtd_premissa, recipiente, insumo)
