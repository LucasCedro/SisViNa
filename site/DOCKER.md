# Deploy com Docker

Este projeto está pronto para rodar em produção via Docker usando o preset
`node-server` do Nitro (servidor Node.js standalone com SSR).

## Pré-requisitos
- Docker 24+ e (opcional) Docker Compose v2

## Build & run rápido

```bash
docker build -t viveiro-site .
docker run --rm -p 3000:3000 viveiro-site
```

Acesse: http://localhost:3000

## Usando docker compose

```bash
docker compose up -d --build
docker compose logs -f
docker compose down
```

## Variáveis de ambiente

| Var        | Default       | Descrição                              |
|------------|---------------|----------------------------------------|
| `PORT`     | `3000`        | Porta do servidor HTTP                 |
| `HOST`     | `0.0.0.0`     | Interface de bind                      |
| `NODE_ENV` | `production`  | Modo de execução                       |
| `VITE_APP_URL` | `http://localhost:5173` | URL do app Vue (botões **Entrar** → `/login`) |

Para variáveis públicas do frontend, crie um `.env` na raiz com prefixo
`VITE_` ANTES do build (elas são embutidas no bundle):

```
VITE_APP_URL=http://localhost:5173
```

Ver também `../RODAR.md` (fluxo site → login → painel).

## Deploy em produção (atrás de proxy reverso)

Recomenda-se rodar atrás de Nginx/Caddy/Traefik com HTTPS terminado no
proxy. Exemplo Nginx mínimo:

```nginx
server {
  listen 443 ssl http2;
  server_name seu-dominio.com;

  ssl_certificate     /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

  location / {
    proxy_pass http://127.0.0.1:3000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

## Atualizar a aplicação

```bash
git pull
docker compose up -d --build
```

## Estrutura do build

- `dist/server/index.mjs` — servidor Node (entrypoint)
- `dist/client/` — assets estáticos servidos pelo próprio servidor
