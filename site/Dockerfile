# ---- Build stage ----
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies (use bun if lockfile present, fallback to npm)
COPY package.json ./
COPY bun.lock* package-lock.json* ./

RUN if [ -f bun.lock ]; then \
      npm install -g bun && bun install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then \
      npm ci; \
    else \
      npm install; \
    fi

# URL do app Vue — embutida no bundle no build (Vite)
ARG VITE_APP_URL=http://localhost:5173
ENV VITE_APP_URL=$VITE_APP_URL

# Copy source and build
COPY . .
RUN npm run build

# ---- Runtime stage ----
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Nitro node-server preset produces a self-contained bundle in dist/
COPY --from=builder /app/dist ./dist

EXPOSE 3000

# Run a non-root user for security
RUN addgroup -S app && adduser -S app -G app
USER app

CMD ["node", "dist/server/index.mjs"]
