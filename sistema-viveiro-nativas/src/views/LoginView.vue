<template>
  <div class="login-page">
    <!-- Painel de marca (desktop) -->
    <aside class="login-brand" aria-hidden="false">
      <div class="login-brand__inner">
        <div class="login-brand__glow" aria-hidden="true" />
        <div class="login-brand__pattern" aria-hidden="true" />

        <img
          :src="LOGO_BRANCO"
          alt="Brotare"
          class="login-brand__logo"
          width="220"
          height="48"
        />

        <p class="login-brand__viveiro">{{ nomeViveiro }}</p>
        <p class="login-brand__tagline">
          Gestão integrada de coleta, produção, estoques e comercialização de mudas nativas.
        </p>

        <ul class="login-brand__features">
          <li>
            <span class="login-brand__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path fill="currentColor" d="M10.59 13.41a1 1 0 0 1 0-1.42l2.17-2.17H7a1 1 0 0 1 0-2h5.76l-2.17-2.17a1 1 0 1 1 1.42-1.42l4 4a1 1 0 0 1 0 1.42l-4 4a1 1 0 0 1-1.42 0Z" transform="rotate(180 12 12)"/></svg>
            </span>
            Rastreabilidade da semente à venda
          </li>
          <li>
            <span class="login-brand__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 22c4.42-3.5 7-7.06 7-11.5A7 7 0 0 0 5 10.5C5 15 7.58 18.5 12 22Zm0-4.8C9.5 15.5 8 13.4 8 10.5a4 4 0 0 1 8 0c0 2.9-1.5 5-4 6.7Z"/></svg>
            </span>
            Operação de campo e viveiro unificadas
          </li>
          <li>
            <span class="login-brand__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path fill="currentColor" d="M4 19h16v2H4Zm2-2h12l1-9H5Zm3-11h6l1 4H8Z"/></svg>
            </span>
            Indicadores financeiros e comerciais
          </li>
        </ul>
      </div>

      <p class="login-brand__foot">© {{ ano }} Brotare · SisViNa</p>
    </aside>

    <!-- Formulário -->
    <main class="login-main">
      <div class="login-shell">
        <header class="login-shell__head">
          <img
            :src="LOGO_VERDE"
            alt="Brotare"
            class="login-shell__logo login-shell__logo--mobile"
            width="180"
          />
          <img
            :src="LOGO_SYMBOL"
            alt=""
            class="login-shell__symbol login-shell__symbol--desktop"
            width="48"
            height="48"
          />
          <div class="login-shell__titles">
            <h1>Entrar no painel</h1>
            <p>Use suas credenciais de acesso ao sistema.</p>
          </div>
        </header>

        <form
          class="login-form"
          method="post"
          action="/login"
          autocomplete="on"
          @submit.prevent="onSubmit"
        >
          <div class="login-field">
            <label class="login-field__label" for="login-username">Usuário</label>
            <span class="login-field__wrap">
              <svg class="login-field__svg" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4 0-7 2-7 4v1h14v-1c0-2-3-4-7-4Z"
                  fill="currentColor"
                />
              </svg>
              <input
                id="login-username"
                v-model="username"
                name="username"
                type="text"
                class="login-field__input"
                autocomplete="username"
                autocapitalize="none"
                spellcheck="false"
                placeholder="Digite seu usuário"
                required
              />
            </span>
          </div>

          <div class="login-field">
            <label class="login-field__label" for="login-password">Senha</label>
            <span class="login-field__wrap">
              <svg class="login-field__svg" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M17 9h-1V7a4 4 0 0 0-8 0v2H7a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2Zm-3 0H10V7a2 2 0 1 1 4 0Z"
                  fill="currentColor"
                />
              </svg>
              <input
                id="login-password"
                v-model="password"
                name="password"
                :type="mostrarSenha ? 'text' : 'password'"
                class="login-field__input login-field__input--password"
                autocomplete="current-password"
                placeholder="Digite sua senha"
                required
              />
              <button
                type="button"
                class="login-field__toggle"
                :aria-label="mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'"
                :aria-pressed="mostrarSenha"
                @click="mostrarSenha = !mostrarSenha"
              >
                <svg v-if="mostrarSenha" viewBox="0 0 24 24" aria-hidden="true" width="20" height="20">
                  <path
                    fill="currentColor"
                    d="M3.27 3.27 2 4.54l2.82 2.82A11.8 11.8 0 0 0 1 12c1.73 4.39 6 7.5 11 7.5 2.25 0 4.34-.61 6.08-1.68l2.57 2.57 1.27-1.27L3.27 3.27ZM12 17.5c-2.76 0-5.18-1.49-6.5-3.71a7.75 7.75 0 0 1 1.56-1.96l1.46 1.46A4.5 4.5 0 0 0 12 15.5a4.5 4.5 0 0 0 3.17-1.3l1.41 1.41A5 5 0 0 1 12 17.5Zm6.72-3.8-1.55-1.55A4.51 4.51 0 0 0 16.5 12a4.5 4.5 0 0 0-6.17-4.13L8.77 6.05A11.77 11.77 0 0 1 12 6.5c4.27 0 8.09 2.7 9.73 6.5a10.45 10.45 0 0 1-2.14 2.87l-1.87-1.67Z"
                  />
                </svg>
                <svg v-else viewBox="0 0 24 24" aria-hidden="true" width="20" height="20">
                  <path
                    fill="currentColor"
                    d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5C21.27 7.61 17 4.5 12 4.5Zm0 12.5a5 5 0 1 1 5-5 5 5 0 0 1-5 5Zm0-8a3 3 0 1 0 3 3 3 3 0 0 0-3-3Z"
                  />
                </svg>
              </button>
            </span>
          </div>

          <div v-if="error" class="login-alert" role="alert">
            <svg viewBox="0 0 24 24" aria-hidden="true" width="18" height="18">
              <path
                fill="currentColor"
                d="M12 2 1 21h22L12 2Zm0 4.5 7.5 13h-15L12 6.5ZM11 10v4h2v-4h-2Zm0 6v2h2v-2h-2Z"
              />
            </svg>
            <span>{{ error }}</span>
          </div>

          <button type="submit" class="login-submit" :disabled="loading">
            <span v-if="loading" class="login-submit__spinner" aria-hidden="true" />
            <span v-else class="login-submit__arrow" aria-hidden="true">→</span>
            {{ loading ? 'Entrando…' : 'Acessar painel' }}
          </button>
        </form>

        <footer class="login-shell__foot">
          <a :href="siteUrl" class="login-back">
            <svg viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
              <path fill="currentColor" d="M15.41 7.41 14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
            </svg>
            Voltar ao site institucional
          </a>
        </footer>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

const LOGO_VERDE = '/assets/branding/logo_comp_verde.jpg'
const LOGO_BRANCO = '/assets/branding/logo_comp_branco.jpg'
const LOGO_SYMBOL = '/assets/branding/logo_simp.jpg'

const nomeViveiro = import.meta.env.VITE_VIVEIRO_NOME || 'Viveiro Nativas'
const ano = new Date().getFullYear()

const siteUrl = computed(
  () => (import.meta.env.VITE_SITE_URL || 'http://localhost:3000').replace(/\/$/, '')
)

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const mostrarSenha = ref(false)
const loading = ref(false)
const error = ref(null)

async function onSubmit() {
  loading.value = true
  error.value = null
  try {
    await auth.login(username.value, password.value)
    const redirect = route.query.redirect || '/'
    await router.push(redirect)
  } catch {
    error.value = auth.error || 'Usuário ou senha inválidos. Verifique e tente novamente.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--color-background);
}

/* ── Painel marca ── */
.login-brand {
  position: relative;
  display: none;
  flex: 1 1 44%;
  max-width: 520px;
  flex-direction: column;
  justify-content: space-between;
  padding: clamp(2rem, 5vw, 3.5rem);
  color: var(--color-text-inverse);
  background: linear-gradient(
    155deg,
    var(--color-primary-900) 0%,
    var(--color-primary-700) 42%,
    var(--color-complement-dark) 100%
  );
  overflow: hidden;
}

.login-brand__inner {
  position: relative;
  z-index: 1;
}

.login-brand__glow {
  position: absolute;
  top: -30%;
  right: -20%;
  width: 70%;
  aspect-ratio: 1;
  background: radial-gradient(circle, rgba(200, 168, 75, 0.14) 0%, transparent 68%);
  pointer-events: none;
}

.login-brand__pattern {
  position: absolute;
  inset: 0;
  opacity: 0.07;
  background-image: url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M40 6c6 12 18 14 18 26s-12 20-18 32c-6-12-18-14-18-32s12-20 18-32z' fill='%23ffffff'/%3E%3C/svg%3E");
  background-size: 72px 72px;
  pointer-events: none;
}

.login-brand__logo {
  display: block;
  width: min(220px, 75%);
  height: auto;
  margin-bottom: 1.75rem;
  filter: drop-shadow(0 4px 24px rgba(0, 0, 0, 0.2));
}

.login-brand__viveiro {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-attention);
}

.login-brand__tagline {
  margin: 0 0 2rem;
  max-width: 22rem;
  font-size: 1.0625rem;
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.82);
}

.login-brand__features {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.login-brand__features li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 0.875rem;
  line-height: 1.45;
  color: rgba(255, 255, 255, 0.78);
}

.login-brand__icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-attention);
}

.login-brand__icon svg {
  width: 1.125rem;
  height: 1.125rem;
}

.login-brand__foot {
  position: relative;
  z-index: 1;
  margin: 0;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.45);
}

/* ── Área do formulário ── */
.login-main {
  flex: 1 1 56%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(1.25rem, 4vw, 2.5rem);
  background:
    radial-gradient(ellipse 80% 60% at 100% 0%, var(--color-primary-subtle) 0%, transparent 55%),
    radial-gradient(ellipse 60% 50% at 0% 100%, var(--color-complement-light) 0%, transparent 50%),
    var(--color-background);
}

.login-shell {
  width: 100%;
  max-width: 420px;
  animation: login-in 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.login-shell__head {
  margin-bottom: 2rem;
}

.login-shell__logo--mobile {
  display: block;
  width: min(180px, 70%);
  height: auto;
  margin: 0 auto 1.5rem;
}

.login-shell__symbol--desktop {
  display: none;
}

.login-shell__titles h1 {
  margin: 0 0 0.4rem;
  font-size: clamp(1.5rem, 4vw, 1.75rem);
  font-weight: 700;
  letter-spacing: -0.025em;
  color: var(--color-text-primary);
}

.login-shell__titles p {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--color-text-muted);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
}

.login-field__label {
  display: block;
  margin-bottom: 0.4rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.login-field__wrap {
  display: flex;
  align-items: center;
  min-height: 3rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  transition: border-color 0.18s, box-shadow 0.18s, background 0.18s;
}

.login-field__wrap:hover {
  border-color: var(--color-primary-200);
}

.login-field__wrap:focus-within {
  border-color: var(--color-primary);
  background: var(--color-surface);
  box-shadow: 0 0 0 4px var(--color-primary-subtle);
}

.login-field__svg {
  flex-shrink: 0;
  width: 1.125rem;
  height: 1.125rem;
  margin-left: 0.9rem;
  color: var(--color-primary);
  opacity: 0.7;
}

.login-field__input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  padding: 0.85rem 0.9rem 0.85rem 0.6rem;
  font-size: 0.9375rem;
  font-family: inherit;
  color: var(--color-text-primary);
  outline: none;
}

.login-field__input--password {
  padding-right: 0.25rem;
}

.login-field__input::placeholder {
  color: var(--color-neutral-medium);
}

.login-field__toggle {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.4rem;
  padding: 0.4rem;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: color 0.15s, background 0.15s;
}

.login-field__toggle:hover {
  color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.login-field__toggle:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 1px;
}

.login-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  margin: 0;
  padding: 0.75rem 0.9rem;
  font-size: 0.875rem;
  line-height: 1.45;
  color: var(--color-error-dark);
  background: var(--color-error-bg);
  border-radius: var(--radius-md);
  border: 1px solid rgba(142, 59, 43, 0.15);
}

.login-alert svg {
  flex-shrink: 0;
  margin-top: 0.1rem;
  color: var(--color-error);
}

.login-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  width: 100%;
  margin-top: 0.15rem;
  padding: 0.9375rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 600;
  font-family: inherit;
  letter-spacing: 0.01em;
  color: var(--color-text-inverse);
  background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(53, 61, 43, 0.22);
  transition: transform 0.14s, box-shadow 0.14s, filter 0.14s;
}

.login-submit:hover:not(:disabled) {
  filter: brightness(1.05);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(53, 61, 43, 0.28);
}

.login-submit:active:not(:disabled) {
  transform: translateY(0);
}

.login-submit:disabled {
  opacity: 0.75;
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

.login-submit__arrow {
  font-size: 1.125rem;
  line-height: 1;
  opacity: 0.9;
}

.login-shell__foot {
  margin-top: 1.5rem;
  text-align: center;
}

.login-back {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.login-back:hover {
  color: var(--color-primary);
}

.login-back svg {
  opacity: 0.7;
}

@keyframes login-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes login-in {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── Desktop: split ── */
@media (min-width: 900px) {
  .login-brand {
    display: flex;
  }

  .login-shell__logo--mobile {
    display: none;
  }

  .login-shell__head {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1.75rem;
  }

  .login-shell__symbol--desktop {
    display: block;
    flex-shrink: 0;
    border-radius: 50%;
    box-shadow: var(--shadow-md);
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-shell {
    animation: none;
  }

  .login-submit:hover:not(:disabled) {
    transform: none;
  }
}
</style>
