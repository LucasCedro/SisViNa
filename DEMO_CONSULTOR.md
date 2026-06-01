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

**Protótipo v0.1** — o site vende a visão; o app mostra coleta, produção, estoques, vendas e financeiro. Textos do site (NF-e, WhatsApp, app mobile, etc.) são **roadmap**; nem tudo existe no app ainda.

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

docker network create viveiro_network
# (ignore erro se a rede já existir)

# .env NÃO vêm no Git — copiar dos exemplos na 1ª vez:
copy api_viveiro\.env.example api_viveiro\.env

docker compose up -d --build postgres api web
# NÃO precisa subir `site` se usar Lovable — só web + api + postgres

# Migrations (1ª vez ou após pull com migrations novas):
docker exec viveiro_api alembic upgrade head
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
docker compose up -d --build site web api postgres
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
   - Vendas (venda paga, se existir)
   - Financeiro (DRE / premissas)
6. Frase-chave para o consultor:

   > *"O site é a vitrine comercial. O sistema é o protótipo funcional do fluxo do viveiro. Não é produto final — nem tudo que o site promete já está implementado."*

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
| Entrar abre localhost e não carrega | Docker não subiu | `docker compose up -d web api postgres` |
| Erro ao logar | API off ou migration pendente | `docker compose logs api` + `docker exec viveiro_api alembic upgrade head` |
| Botão Entrar vai para URL errada | `VITE_APP_URL` incorreto no build Lovable | Rebuild com `http://localhost:5173` |
| Front não atualiza | Normal no Docker + Windows | F5; containers rodando bastam |
| Erro de rede Docker | `viveiro_network` inexistente | `docker network create viveiro_network` |

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
└── site/
    ├── INTEGRACAO.md          ← Detalhes site ↔ app
    └── DEMO_CONSULTOR.md      ← Este arquivo
```
