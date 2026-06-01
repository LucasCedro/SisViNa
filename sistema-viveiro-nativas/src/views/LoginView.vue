<template>
  <div class="login-page">
    <aside class="login-showcase">
      <div class="login-showcase__pattern" aria-hidden="true" />
      <div class="login-showcase__glow" aria-hidden="true" />

      <div class="login-showcase__content">
        <img
          :src="LOGO_ESCURA"
          alt="Brotare"
          class="login-showcase__logo"
          width="220"
          height="auto"
        />

        <p class="login-showcase__eyebrow">Software para viveiros de plantas nativas</p>

        <h1 class="login-showcase__title">
          Gestão completa do seu <span>viveiro de nativas</span>
        </h1>

        <p class="login-showcase__lead">
          Da semente à venda: veja o que tem no viveiro, quanto gastou e quanto pode faturar.
        </p>

        <ul class="login-pillars">
          <li v-for="p in pilares" :key="p.titulo">
            <span class="login-pillars__check" aria-hidden="true">
              <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M16.5 5.5L8.25 14.5L4 10.25"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
            <div>
              <strong>{{ p.titulo }}</strong>
              <span>{{ p.texto }}</span>
            </div>
          </li>
        </ul>

        <div class="login-showcase__modules" aria-label="Módulos do sistema">
          <span v-for="m in modulos" :key="m">{{ m }}</span>
        </div>
      </div>

      <p class="login-showcase__foot">Brotare — tecnologia a serviço da restauração</p>
    </aside>

    <main class="login-main">
      <div class="login-card">
        <header class="login-card__head">
          <img
            :src="LOGO_CLARA"
            alt="Brotare"
            class="login-card__logo login-card__logo--compact"
            width="148"
          />
          <h2>Bem-vindo de volta</h2>
          <p>Acesse o painel do seu viveiro.</p>
        </header>

        <form class="login-form" @submit.prevent="onSubmit">
          <label class="login-field">
            <span class="login-field__label">Usuário</span>
            <span class="login-field__wrap">
              <svg class="login-field__svg" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4 0-7 2-7 4v1h14v-1c0-2-3-4-7-4Z"
                  fill="currentColor"
                />
              </svg>
              <input
                v-model="username"
                type="text"
                class="login-field__input"
                autocomplete="username"
                placeholder="Seu usuário"
                required
              />
            </span>
          </label>

          <label class="login-field">
            <span class="login-field__label">Senha</span>
            <span class="login-field__wrap">
              <svg class="login-field__svg" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M17 9h-1V7a4 4 0 0 0-8 0v2H7a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2Zm-3 0H10V7a2 2 0 1 1 4 0Z"
                  fill="currentColor"
                />
              </svg>
              <input
                v-model="password"
                type="text"
                class="login-field__input"
                autocomplete="current-password"
                placeholder="Sua senha"
                required
              />
            </span>
          </label>

          <p v-if="error" class="login-alert" role="alert">{{ error }}</p>

          <button type="submit" class="login-submit" :disabled="loading">
            <span v-if="loading" class="login-submit__spinner" aria-hidden="true" />
            {{ loading ? 'Entrando…' : 'Entrar no painel' }}
          </button>
        </form>

        <aside class="login-dev" aria-label="Credenciais de desenvolvimento">
          <div class="login-dev__top">
            <span class="login-dev__dot" aria-hidden="true" />
            <span class="login-dev__badge">Desenvolvimento</span>
          </div>
          <p class="login-dev__text">Acesso de teste até publicar em produção:</p>
          <div class="login-dev__creds">
            <code>admin</code>
            <span class="login-dev__sep" aria-hidden="true">·</span>
            <code>Admin@123</code>
          </div>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

/** Fundo escuro → letras brancas. Fundo claro (card) → versão verde. */
const LOGO_ESCURA = '/assets/branding/logo_comp_branco.jpg'
const LOGO_CLARA = '/assets/branding/logo_comp_verde.jpg'

const pilares = [
  {
    titulo: 'O que tem no viveiro',
    texto: 'Sementes no armazém, mudas em produção e prontas para vender — tudo visível e atualizado.',
  },
  {
    titulo: 'Quanto custa produzir',
    texto: 'Cada lote com substrato, energia, água e equipe já somados — você vê o gasto de verdade.',
  },
  {
    titulo: 'Como fechou o faturamento',
    texto: 'Vendas, contas do período e se o viveiro está no azul ou no vermelho, no mesmo painel.',
  },
]

const modulos = ['Coleta', 'Produção', 'Estoques', 'Vendas', 'Financeiro']

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const username = ref('admin')
const password = ref('Admin@123')
const loading = ref(false)
const error = ref(null)

async function onSubmit() {
  loading.value = true
  error.value = null
  try {
    await auth.login(username.value, password.value)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch {
    error.value = auth.error || 'Usuário ou senha inválidos'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr;
  background: var(--color-background);
}

@media (min-width: 960px) {
  .login-page {
    grid-template-columns: 1.15fr 0.85fr;
  }
}

/* ── Showcase (marca + proposta de valor) ── */
.login-showcase {
  position: relative;
  display: none;
  flex-direction: column;
  justify-content: space-between;
  padding: clamp(2rem, 4vw, 3.5rem) clamp(1.5rem, 4vw, 3rem);
  overflow: hidden;
  color: var(--color-text-inverse);
  background: linear-gradient(
    165deg,
    var(--color-primary-900) 0%,
    var(--color-primary-700) 45%,
    var(--color-analog-1) 100%
  );
}

@media (min-width: 960px) {
  .login-showcase {
    display: flex;
  }
}

.login-showcase__pattern {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  background-image: radial-gradient(circle at 20% 80%, #fff 1px, transparent 1px),
    radial-gradient(circle at 75% 25%, #fff 1px, transparent 1px);
  background-size: 48px 48px, 64px 64px;
  pointer-events: none;
}

.login-showcase__glow {
  position: absolute;
  top: -15%;
  right: -5%;
  width: 50%;
  aspect-ratio: 1;
  background: radial-gradient(circle, rgba(200, 168, 75, 0.15) 0%, transparent 65%);
  pointer-events: none;
}

.login-showcase__content {
  position: relative;
  z-index: 1;
  max-width: 32rem;
  animation: login-fade-up 0.55s ease-out both;
}

.login-showcase__logo {
  display: block;
  width: min(220px, 72%);
  height: auto;
  margin-bottom: var(--spacing-xl);
}

.login-showcase__eyebrow {
  margin: 0 0 var(--spacing-md);
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-attention);
}

.login-showcase__title {
  margin: 0 0 var(--spacing-md);
  font-size: clamp(1.75rem, 3.2vw, 2.35rem);
  font-weight: 700;
  line-height: 1.12;
  letter-spacing: -0.03em;
  color: #fff;
}

.login-showcase__title span {
  color: var(--color-attention);
}

.login-showcase__lead {
  margin: 0 0 var(--spacing-xl);
  font-size: 1.0625rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.82);
  max-width: 28rem;
}

.login-pillars {
  list-style: none;
  margin: 0 0 var(--spacing-xl);
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.login-pillars li {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-start;
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(8px);
}

.login-pillars__check {
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--color-success);
  color: var(--color-text-inverse);
}

.login-pillars__check svg {
  width: 0.9rem;
  height: 0.9rem;
}

.login-pillars strong {
  display: block;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 0.15rem;
}

.login-pillars span {
  font-size: 0.8125rem;
  line-height: 1.45;
  color: rgba(255, 255, 255, 0.68);
}

.login-showcase__modules {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.login-showcase__modules span {
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: var(--radius-full);
}

.login-showcase__foot {
  position: relative;
  z-index: 1;
  margin: var(--spacing-xl) 0 0;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.45);
  animation: login-fade-up 0.55s ease-out 0.12s both;
}

/* ── Formulário ── */
.login-main {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl) var(--spacing-md);
  min-height: 100vh;
  background: var(--color-background);
}

@media (min-width: 960px) {
  .login-main {
    padding: var(--spacing-2xl);
    background: linear-gradient(180deg, var(--color-surface-muted) 0%, var(--color-background) 100%);
  }
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-xl);
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  animation: login-fade-up 0.5s ease-out 0.08s both;
}

@media (min-width: 960px) {
  .login-card {
    max-width: 420px;
    padding: 2.25rem 2rem 1.75rem;
    box-shadow:
      var(--shadow-lg),
      0 0 0 1px rgba(255, 255, 255, 0.6) inset;
  }
}

.login-card__head {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.login-card__logo--compact {
  display: block;
  margin: 0 auto var(--spacing-lg);
  max-width: 148px;
  height: auto;
}

@media (min-width: 960px) {
  .login-card__logo--compact {
    max-width: 132px;
    margin-bottom: var(--spacing-md);
  }
}

.login-card__head h2 {
  margin: 0 0 0.35rem;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
}

.login-card__head p {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-text-muted);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
}

.login-field__label {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.login-field__wrap {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  transition:
    border-color 0.15s,
    box-shadow 0.15s,
    background 0.15s;
}

.login-field__wrap:focus-within {
  border-color: var(--color-primary);
  background: var(--color-surface);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
}

.login-field__svg {
  flex-shrink: 0;
  width: 1.125rem;
  height: 1.125rem;
  margin-left: 0.85rem;
  color: var(--color-primary);
  opacity: 0.75;
}

.login-field__input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  padding: 0.8rem 0.85rem 0.8rem 0.65rem;
  font-size: 0.9375rem;
  font-family: inherit;
  color: var(--color-text-primary);
  outline: none;
}

.login-field__input::placeholder {
  color: var(--color-neutral-medium);
}

.login-alert {
  margin: 0;
  padding: 0.65rem 0.85rem;
  font-size: 0.875rem;
  color: var(--color-error-dark);
  background: var(--color-error-bg);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-error);
}

.login-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  margin-top: 0.25rem;
  padding: 0.9rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 600;
  font-family: inherit;
  color: var(--color-text-inverse);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(53, 61, 43, 0.25);
  transition:
    background 0.15s,
    transform 0.12s,
    box-shadow 0.15s;
}

.login-submit:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(53, 61, 43, 0.28);
}

.login-submit:disabled {
  opacity: 0.7;
  cursor: wait;
}

.login-submit__spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: login-spin 0.65s linear infinite;
}

.login-dev {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-subtle);
}

.login-dev__top {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.35rem;
}

.login-dev__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-attention);
  box-shadow: 0 0 0 3px var(--color-attention-bg);
}

.login-dev__badge {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.login-dev__text {
  margin: 0 0 0.4rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.login-dev__creds {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.login-dev__creds code {
  font-size: 0.8125rem;
  font-weight: 600;
  font-family: var(--font-mono);
  color: var(--color-primary-700);
  background: var(--color-primary-50);
  padding: 0.2rem 0.45rem;
  border-radius: var(--radius-sm);
}

.login-dev__sep {
  color: var(--color-border);
  font-weight: 700;
}

@keyframes login-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes login-fade-up {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-showcase__content,
  .login-card,
  .login-showcase__foot {
    animation: none;
  }
}
</style>
