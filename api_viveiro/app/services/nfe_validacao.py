"""Validações fiscais do destinatário (exigências MOC NF-e)."""

from __future__ import annotations

from app.models.compradores import Comprador
from app.utils.fiscal import only_digits, validate_cpf, validate_cnpj


def validar_comprador_para_nfe(comprador: Comprador) -> None:
    erros = erros_comprador_nfe(comprador)
    if erros:
        raise ValueError("Destinatário incompleto para NF-e: " + "; ".join(erros))


def erros_comprador_nfe(comprador: Comprador) -> list[str]:
    erros: list[str] = []

    doc = only_digits(comprador.cpf_cnpj or "")
    if comprador.tipo == "PF":
        if not validate_cpf(comprador.cpf_cnpj or ""):
            erros.append("CPF do comprador inválido")
    else:
        if not validate_cnpj(comprador.cpf_cnpj or ""):
            erros.append("CNPJ do comprador inválido")

    if not (comprador.endereco or "").strip():
        erros.append("Endereço do comprador obrigatório")
    if not (comprador.numero or "").strip():
        erros.append("Número do endereço do comprador obrigatório")
    if not (comprador.bairro or "").strip():
        erros.append("Bairro do comprador obrigatório")
    if not (comprador.cidade or "").strip():
        erros.append("Município do comprador obrigatório")
    if not (comprador.estado or "").strip() or len(comprador.estado) != 2:
        erros.append("UF do comprador obrigatória (2 letras)")
    if len(only_digits(comprador.cep or "")) != 8:
        erros.append("CEP do comprador inválido (8 dígitos)")
    if len(only_digits(comprador.codigo_municipio_ibge or "")) != 7:
        erros.append("Código IBGE do município do comprador obrigatório (7 dígitos)")

    return erros


def validar_emitente_configurado(emitente) -> None:
    if not emitente or not emitente.ativo:
        raise ValueError("Cadastre o emitente fiscal em /api/v1/nfe/emitente")
