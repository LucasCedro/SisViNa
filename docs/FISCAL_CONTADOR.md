# Parâmetros fiscais — cockpit do contador

## Responsabilidades

| Papel | Responsabilidade |
|-------|------------------|
| **Contador** | CFOP, CSOSN, origem (icms_origem), isenção, redução de BC, DIFAL, ICMS importação SN, fundamento legal, emitente, homologação/produção Focus |
| **SisViNa (software)** | Aplicar regras **ativas**, validar cadastro mínimo do comprador, enviar JSON à [Focus NFe](https://doc.focusnfe.com.br/reference/introducao), guardar status/XML |
| **Fora do escopo** | SPED Fiscal, EFD Contribuições, escrituração contábil, cálculo/apuração do DAS, guias de ICMS importação — o contador usa seus sistemas habituais |

### Token Focus (homologação)

- Variável `FOCUS_NFE_TOKEN` em `api_viveiro/.env` (só backend).
- Com `NFE_ALLOW_PRODUCAO=false`, a API usa **homologação** — o token deve ser o de **homologação** no painel Focus.
- Erro `HTTP Basic: Access denied` = token inválido, revogado ou de produção usado em homologação. Após corrigir: `.\scripts\dev.ps1 restart-api`.
- Venda com NF-e **rejeitada** pode usar **Reemitir** na lista (não bloqueia como autorizada/processando).

O sistema **não substitui** parecer fiscal. Exemplos no banco (GO, Conv. 100/97, RCTE-GO, importação SN) vêm **inativos** até o contador validar.

## Simples Nacional — ICMS

| Cenário | O que o SisViNa faz | Recolhimento (contador) |
|---------|---------------------|-------------------------|
| Venda doméstica (origem nacional) | CSOSN + CFOP na NF-e | ICMS via DAS unificado |
| Interestadual + consumidor final | CSOSN + DIFAL (alíquotas ref.) | DIFAL — exceção ao DAS |
| Mudas origem estrangeira | CSOSN + `icms_origem` ≥ 1 + alíquota ref. importação | ICMS importação SN — exceção ao DAS |
| Exportação | Regra `tipo_operacao=exterior`, CFOP 7xxx | Conforme orientação contábil |

Na **venda**, marque «origem importada» (`tipo_operacao_fiscal=importacao`) quando as mudas forem de procedência estrangeira.

## Onde configurar

- **UI operador:** Vendas → emitir NF-e (`fiscal.view`, `fiscal.emit`)
- **UI contador:** Contabilidade → regras, emitente, consolidado (`contabilidade.view` / `fiscal.edit`)
- **RBAC:** `fiscal.view` ≠ `contabilidade.view` — ver [SEGURANCA_RBAC.md](./SEGURANCA_RBAC.md)

### Telas e API
- **Simulador:** mesma aba — testa UF destino + tipo operação antes de ativar regra
- **API:** `GET/POST/PUT/DELETE /api/v1/fiscal/regras`
- **Preview:** `GET /api/v1/fiscal/regras/preview?uf_destino=SP&tipo_operacao=importacao`
- **Emitente:** `PUT /api/v1/fiscal/emitente`

## Matriz de regras

Cada linha combina:

- `ncm` (ex. 06029090 mudas)
- `uf_origem`, `uf_destino` (`INTERNA`, `INTERESTADUAL`, `*`, listas)
- `tipo_cliente`: PF | PJ | ANY
- **`tipo_operacao`**: `domestica` | `importacao` | `exterior`

Campos definidos pelo contador:

- **cfop_base** — código de 4 dígitos ([tabela CFOP Focus](https://doc.focusnfe.com.br/reference/cfop))
- **ajustar_cfop_por_uf** — se marcado, o sistema troca o 1º dígito 5↔6 conforme interna/interestadual
- **csosn** — Simples Nacional (nunca CST)
- **icms_origem** — tag `orig` na NF-e (0=nacional; 1=importação direta; …)
- **aliquota_icms_importacao** — referência SN para importação (não substitui guia/DAS)
- **isento_icms**, **reducao_bc_icms_percent** (ex. 60% interestadual Conv. 100/97 VIII)
- **fundamento_legal**, **informacoes_complementares** → texto na NF-e
- **aplicar_difal** + alíquotas (quando interestadual + consumidor final)
- **pis_situacao_tributaria**, **cofins_situacao_tributaria** (opcional)
- **local_destino** 1/2/3 ou automático

## Referências legais (exemplo GO — validar com contador)

- Convênio ICMS **100/97**, cl. 1 **VIII** — redução 60% BC em saídas interestaduais de **mudas**
- RCTE-GO **Anexo IX**, art. 7º **h)** — isenção de ICMS para muda (vigência e requisitos)
- ICMS importação SN — recolhimento específico (validar alíquota e fundamento com contador)

## Documentação técnica

- MOC 7.0 + **Anexo I** (leiaute e regras de validação SEFAZ)
- Focus: [Emitir NF-e](https://doc.focusnfe.com.br/reference/emitir_nfe.md), [Campos 4.00](https://campos.focusnfe.com.br/nfe/NotaFiscalXML.html)

## Emissão

1. Contador cadastra regra **ativa** para o cenário da venda (doméstica, DIFAL, importação ou exterior)
2. Operador registra venda (marca origem importada se aplicável) e clica **Emitir NF-e**
3. Sem `FOCUS_NFE_TOKEN` → modo **simulação** (sem validade fiscal)

## O contador consegue usar?

**Sim, para parametrizar NF-e de vendas** — desde que:

- Cadastre emitente (CNPJ, certificado via Focus)
- Ative regras por cenário real do viveiro (não confie nos seeds inativos)
- Use o simulador antes de liberar emissão
- Continue SPED/EFD/DAS nos sistemas de escrituração

**Ainda não cobre:** apuração mensal, conciliação DAS, livros fiscais, obrigações estaduais além da NF-e de saída.
