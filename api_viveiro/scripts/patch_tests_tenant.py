"""Aplica id_empresa/id_viveiro nos testes legados."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORT_LINE = "from tests.tenant_fixtures import DEFAULT_EMPRESA_ID, DEFAULT_VIVEIRO_ID\n"


def ensure_import(text: str) -> str:
    if "from tests.tenant_fixtures" in text:
        return text
    lines = text.splitlines(True)
    ins = 0
    for i, line in enumerate(lines):
        if line.startswith("from app.") or line.startswith("import pytest"):
            ins = i + 1
    lines.insert(ins, IMPORT_LINE)
    return "".join(lines)


def patch_file(rel: str, transform) -> None:
    p = ROOT / rel
    text = ensure_import(p.read_text(encoding="utf-8"))
    text = transform(text)
    p.write_text(text, encoding="utf-8")
    print("patched", rel)


def main() -> None:
    patch_file(
        "tests/test_auth.py",
        lambda t: t.replace(
            "ativo=True\n    )",
            "ativo=True,\n        id_empresa=DEFAULT_EMPRESA_ID,\n    )",
        ).replace(
            "ativo=False  # Usuário inativo\n    )",
            "ativo=False,\n        id_empresa=DEFAULT_EMPRESA_ID,\n    )",
        ),
    )

    patch_file(
        "tests/test_rbac.py",
        lambda t: t.replace(
            "ativo=True,\n    )",
            "ativo=True,\n        id_empresa=DEFAULT_EMPRESA_ID,\n    )",
        ),
    )

    patch_file(
        "tests/test_funcionarios.py",
        lambda t: t.replace(
            "Funcionario(**funcionario_dict, senha=hashed_password)",
            "Funcionario(**funcionario_dict, senha=hashed_password, id_empresa=DEFAULT_EMPRESA_ID)",
        )
        .replace(
            "Funcionario(**funcionario1_dict)",
            "Funcionario(**funcionario1_dict, id_empresa=DEFAULT_EMPRESA_ID)",
        )
        .replace(
            "Funcionario(**funcionario2_dict)",
            "Funcionario(**funcionario2_dict, id_empresa=DEFAULT_EMPRESA_ID)",
        )
        .replace(
            "Funcionario(**funcionario_dict)",
            "Funcionario(**funcionario_dict, id_empresa=DEFAULT_EMPRESA_ID)",
        ),
    )

    patch_file(
        "tests/test_viveiro_context.py",
        lambda t: t.replace(
            "Viveiro(id=1, nome=",
            "Viveiro(id=1, id_empresa=DEFAULT_EMPRESA_ID, nome=",
        )
        .replace(
            "id=2, nome=",
            "id=2, id_empresa=DEFAULT_EMPRESA_ID, nome=",
        )
        .replace(
            "ativo=True,\n  )",
            "ativo=True,\n      id_empresa=DEFAULT_EMPRESA_ID,\n  )",
        ),
    )

    for rel in (
        "tests/test_plantas.py",
        "tests/test_atividades.py",
        "tests/test_pragas.py",
        "tests/test_vendas.py",
        "tests/test_estoques.py",
        "tests/test_insumos.py",
    ):
        patch_file(
            rel,
            lambda t, _rel=rel: t.replace(
                "Canteiro(**canteiro_test_data)",
                "Canteiro(**canteiro_test_data, id_viveiro=DEFAULT_VIVEIRO_ID, tipo_local='canteiro')",
            )
            .replace(
                'Canteiro(nome="Rust A", tipo_local="rustificacao", ativo=True)',
                'Canteiro(nome="Rust A", tipo_local="rustificacao", ativo=True, id_viveiro=DEFAULT_VIVEIRO_ID)',
            )
            .replace(
                "Planta(id_especie=",
                "Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=",
            )
            .replace(
                "Planta(\n        id_especie=",
                "Planta(\n        id_viveiro=DEFAULT_VIVEIRO_ID,\n        id_especie=",
            )
            .replace(
                "Planta(**planta_test_data, id_especie=",
                "Planta(**planta_test_data, id_viveiro=DEFAULT_VIVEIRO_ID, estagio_producao='em_crescimento', id_especie=",
            )
            .replace(
                "Planta(codigo_rastreio=",
                "Planta(id_viveiro=DEFAULT_VIVEIRO_ID, estagio_producao='em_crescimento', codigo_rastreio=",
            )
            .replace(
                "id_viveiro=DEFAULT_VIVEIRO_ID, id_viveiro=DEFAULT_VIVEIRO_ID",
                "id_viveiro=DEFAULT_VIVEIRO_ID",
            )
            .replace(
                "estagio_producao='em_crescimento', estagio_producao=",
                "estagio_producao=",
            ),
        )

    patch_file(
        "tests/test_insumos.py",
        lambda t: t.replace(
            "db_funcionario = Funcionario(",
            "db_funcionario = Funcionario(\n        id_empresa=DEFAULT_EMPRESA_ID,",
        ),
    )


if __name__ == "__main__":
    main()
