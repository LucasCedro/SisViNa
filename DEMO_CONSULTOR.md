# Brotare / SisViNa — Guia de demo para o consultor (v0.1)

Documento para quem vai apresentar o protótipo (site + sistema) ao consultor.

---

## Contexto

Monorepo Git com 3 partes:

| Pasta | O quê | Porta local |
|-------|--------|-------------|
| `site/` | Site marketing (Lovable / TanStack Start) | 3000 (só se subir via Docker) |
| `sistema-viveiro-nativas/` | App operacional (Vue 3) — login + painel | 5173 |
| `api_viveiro/` | API FastAPI + Postgres | 8000 / 5432 |

**Integração site → app**

- Botões **Entrar** usam `AppAccessLink` → `{VITE_APP_URL}/login`
- Código: `site/src/lib/app-url.ts`, `site/src/components/app-access-link.tsx`
- Documentação: `site/INTEGRACAO.md` e `RODAR.md` (raiz do monorepo)

**Protótipo v0.1** — o site vende a visão; o app mostra coleta, produção, estoques, vendas, financeiro e **NF-e em homologação**. Textos do site (WhatsApp, app mobile, etc.) podem ser **roadmap**; produção fiscal real só após validação do contador + `NFE_ALLOW_PRODUCAO=true`.

### Papéis: vendedor vs contador

| Quem | Onde | O quê |
|------|------|--------|
| **Vendedor** | Vendas | Fecha venda e emite NF-e na hora (se regra fiscal ativa + emitente OK) |
| **Contador** | **Contabilidade** | Visão geral, todas as NF-e, vendas pendentes, regras CFOP/CSOSN, cadastro emitente |

**Homologação obrigatória por enquanto:** banner amarelo no cockpit; servidor bloqueia `ambiente=producao` enquanto `NFE_ALLOW_PRODUCAO=false` (padrão). Token Focus = ambiente de testes SEFAZ.

---

## Cenário da demo (importante)

- Tudo roda no **notebook de quem apresenta** (Docker + browser).
- O consultor **só assiste** a tela (no máximo opera o PC do apresentador).
- Por isso `VITE_APP_URL=http://localhost:5173` funciona: site e app ficam no **mesmo computador**.

---

## Parte 1 — Deploy do site no Lovable

1. Conectar o repositório Git (monorepo). O projeto do site está na pasta **`site/`**  
   (se o Lovable pedir raiz do projeto, apontar para `site/`).

2. Definir variável de ambiente **antes do build**:

   ```env
   VITE_APP_URL=http://localhost:5173
   ```

   Sem `/login` no final — o código adiciona automaticamente.

3. Publicar e anotar a URL temporária, por exemplo:  
   `https://xxxx.lovable.app`

4. **Rebuild obrigatório** se mudar `VITE_APP_URL` depois.

Não é necessário hospedar app ou API no Lovable — apenas o site marketing.

---

## Parte 2 — Subir app + API no notebook (Docker)

**Pré-requisitos:** Docker Desktop instalado e rodando, Git, internet.

```powershell
cd C:\caminho\SisViNa
git pull
copy api_viveiro\.env.example api_viveiro\.env   # 1ª vez
.\scripts\dev.ps1 start-all
```

Aguardar ~1–2 min no primeiro `npm ci` do front.

### URLs locais (no notebook da apresentação)

| Serviço | URL |
|---------|-----|
| App (login) | http://localhost:5173/login |
| App (painel) | http://localhost:5173/ |
| API (Swagger) | http://localhost:8000/docs |

### Login demo

| Campo | Valor |
|-------|--------|
| Usuário | `admin` |
| Senha | `Admin@123` |

---

## Parte 3 — Plano B (se Lovable não estiver pronto)

Subir o site também via Docker:

```powershell
.\scripts\dev.ps1 start-demo
```

- Site local: http://localhost:3000  
- O build do site usa `VITE_APP_URL=http://localhost:5173` por padrão no `docker-compose` da raiz.

---

## Parte 4 — Roteiro da apresentação (~15 min)

1. Abrir URL Lovable no Chrome (tela cheia ou espelhar para o consultor).
2. Mostrar o site — proposta Brotare.
3. Clicar **Entrar** → abre `localhost:5173/login` (mesmo notebook).
4. Login `admin` → Home / painel.
5. Percorrer módulos (só o que tiver dado cadastrado):
   - Coleta
   - Produção (pipeline / semeadura)
   - Estoques (mudas, insumos)
   - Vendas (criar venda **pendente**; aprovação/pagamento = perfil financeiro — SoD)
   - **Contabilidade** (cockpit contador: consolidar NF-e, pendentes, regras CFOP, emitente)
   - Financeiro (DRE / premissas — sem aba fiscal; fiscal ficou em Contabilidade)
6. Frase-chave para o consultor:

   > *"O site é a vitrine comercial. O sistema é o protótipo funcional do fluxo do viveiro. NF-e está em **homologação** (sem valor fiscal) até o contador validar parâmetros e liberarmos produção conscientemente."*

---

## Parte 5 — Checklist véspera da demo

- [ ] `git pull` + `docker compose up` testado no notebook que vai na reunião
- [ ] Lovable publicado com `VITE_APP_URL=http://localhost:5173`
- [ ] Testar fluxo completo: Lovable → Entrar → login → painel (no **mesmo** notebook)
- [ ] Bateria + carregador
- [ ] Docker Desktop aberto antes de chegar ao local
- [ ] (Opcional) Cadastrar dados demo: 1 semeadura, estoque, 1 venda paga — evita telas vazias
- [ ] Fechar abas extras / desativar notificações

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| Entrar abre localhost e não carrega | Docker não subiu | `.\scripts\dev.ps1 start-all` |
| Erro ao logar | API off ou migration pendente | `docker compose logs api` + `.\scripts\dev.ps1 migrate` |
| Botão Entrar vai para URL errada | `VITE_APP_URL` incorreto no build Lovable | Rebuild com `http://localhost:5173` |
| Front não atualiza | Normal no Docker + Windows | F5; containers rodando bastam |
| Erro de rede Docker | Stack não subiu | `.\scripts\dev.ps1 start` na raiz |

---

## CORS e produção futura

**Demo atual (localhost + Lovable no mesmo PC):** não precisa alterar CORS.

**Quando site e app forem URLs públicas na nuvem:**

- `VITE_APP_URL=https://app.seudominio.com.br` no build do site
- `VITE_API_URL` no build do Vue = URL pública da API
- `BACKEND_CORS_ORIGINS` na API deve incluir domínio Lovable + domínio do app

---

## Arquivos que não vão no Git

`.env` com senhas — apenas `.env.example` é versionado. Após clone, copiar manualmente.

---

## Referência rápida de pastas

```
SisViNa/
├── site/                      ← Site marketing (Lovable)
├── sistema-viveiro-nativas/   ← App Vue (login + painel)
├── api_viveiro/               ← API FastAPI
├── docker-compose.yml         ← Sobe postgres + api + web (+ site opcional)
├── RODAR.md                   ← Como rodar localmente
├── DEMO_CONSULTOR.md          ← Este arquivo (raiz do monorepo)
└── site/INTEGRACAO.md         ← Detalhes site ↔ app
```
