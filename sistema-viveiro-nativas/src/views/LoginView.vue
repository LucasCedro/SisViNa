<template>
  <div class="login-page">
    <div class="login-page__pattern" aria-hidden="true" />
    <div class="login-page__glow" aria-hidden="true" />

    <div class="login-card">
      <header class="login-card__head">
        <img :src="LOGO" alt="Brotare" class="login-card__logo" width="168" />
        <h1>Acesso ao painel</h1>
        <p>Entre com seu usuário para continuar.</p>
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
          {{ loading ? 'Entrando…' : 'Entrar' }}
        </button>
      </form>

      <aside class="login-dev" aria-label="Credenciais de desenvolvimento">
        <p class="login-dev__text">Demonstração: <code>admin</code> · <code>Admin@123</code></p>
      </aside>

      <footer class="login-card__foot">
        <a :href="siteUrl" class="login-back">← Voltar ao site</a>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

const LOGO = '/assets/branding/logo_comp_verde.jpg'

const siteUrl = computed(
  () => (import.meta.env.VITE_SITE_URL || 'http://localhost:3000').replace(/\/$/, '')
)

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
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl) var(--spacing-md);
  background: linear-gradient(
    160deg,
    var(--color-primary-50) 0%,
    var(--color-background) 45%,
    var(--color-complement-light) 100%
  );
  overflow: hidden;
}

.login-page__pattern {
  position: absolute;
  inset: 0;
  opacity: 0.06;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 8c4 8 12 10 12 18s-8 14-12 22c-4-8-12-10-12-18s8-14 12-22z' fill='%23596247'/%3E%3C/svg%3E");
  background-size: 56px 56px;
  pointer-events: none;
}

.login-page__glow {
  position: absolute;
  top: -20%;
  left: 50%;
  transform: translateX(-50%);
  width: min(36rem, 90vw);
  aspect-ratio: 1;
  background: radial-gradient(circle, rgba(89, 98, 71, 0.12) 0%, transparent 70%);
  pointer-events: none;
}

.login-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  padding: 2rem 1.75rem 1.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  animation: login-in 0.45s ease-out both;
}

.login-card__head {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.login-card__logo {
  display: block;
  margin: 0 auto var(--spacing-lg);
  max-width: 168px;
  height: auto;
}

.login-card__head h1 {
  margin: 0 0 0.35rem;
  font-size: 1.375rem;
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
  transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
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
  padding: 0.875rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 600;
  font-family: inherit;
  color: var(--color-text-inverse);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(53, 61, 43, 0.2);
  transition: background 0.15s, transform 0.12s, box-shadow 0.15s;
}

.login-submit:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(53, 61, 43, 0.25);
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
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-subtle);
  text-align: center;
}

.login-dev__text {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.login-dev__text code {
  font-size: 0.8125rem;
  font-weight: 600;
  font-family: var(--font-mono);
  color: var(--color-primary-700);
  background: var(--color-primary-50);
  padding: 0.1rem 0.35rem;
  border-radius: var(--radius-sm);
}

.login-card__foot {
  margin-top: var(--spacing-md);
  text-align: center;
}

.login-back {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.login-back:hover {
  color: var(--color-primary);
}

@keyframes login-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes login-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-card {
    animation: none;
  }
}
</style>
