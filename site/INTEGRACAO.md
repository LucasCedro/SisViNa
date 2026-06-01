# Site público ↔ Sistema (SisViNa)

## Arquitetura

| Peça | Pasta | Porta dev | Público? |
|------|--------|-----------|----------|
| Site marketing | `site/` | 3000 | Sim — qualquer visitante |
| App operacional | `sistema-viveiro-nativas/` | 5173 | Não — exige login |
| API | `api_viveiro/` | 8000 | Não (JWT) |

A **Home** do Vue (`http://localhost:5173/`) é o **painel após login**, não substitui o site.

## Como o link funciona

- `site/src/lib/app-url.ts` lê `VITE_APP_URL` (build time).
- Botões **Entrar** usam `AppAccessLink` → `{VITE_APP_URL}/login`.
- Padrão local: `http://localhost:5173/login`.

## Docker (monorepo)

Na raiz `SisViNa/`:

```bash
docker compose up -d --build site web api postgres
```

Rebuilde o serviço `site` se mudar `VITE_APP_URL`:

```bash
docker compose build --no-cache site && docker compose up -d site
```

## Produção (futuro)

Opção A — dois subdomínios (mais simples):

- `www.brotare.com.br` → site :3000
- `app.brotare.com.br` → Vue + `VITE_APP_URL=https://app.brotare.com.br`

Opção B — um domínio com proxy (Nginx/Caddy):

- `/` → site
- `/app/` → Vue (exige `base` no Vite do app)

Para v0.1 e demo ao consultor, **Opção A ou dois links em portas locais** é suficiente.
