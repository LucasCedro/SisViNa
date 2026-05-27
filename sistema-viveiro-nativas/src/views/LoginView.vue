<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <h1>SisViNa</h1>
        <p class="subtitle">Gestão de Viveiro de Plantas Nativas</p>
      </div>

      <form @submit.prevent="onSubmit">
        <label class="form-label">
          Usuário
          <input v-model="username" type="text" class="form-input" autocomplete="username" required />
        </label>
        <label class="form-label">
          Senha
          <input v-model="password" type="password" class="form-input" autocomplete="current-password" required />
        </label>
        <p v-if="error" class="alert alert-error">{{ error }}</p>
        <button type="submit" class="btn btn-primary login-submit" :disabled="loading">
          {{ loading ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>

      <p class="hint">Dev: <code>admin</code> / <code>Admin@123</code></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

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
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, var(--color-primary-subtle) 0%, var(--color-background) 45%, var(--color-complement-light) 100%);
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  padding: 2rem;
  border: 1px solid var(--color-border-subtle);
}

.login-brand {
  margin-bottom: 1.5rem;
}

h1 {
  font-size: 1.75rem;
  margin-bottom: 0.25rem;
  color: var(--color-primary);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-submit {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.75rem;
}

.hint {
  margin-top: 1.25rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
  text-align: center;
}

code {
  background: var(--color-surface-muted);
  padding: 0.1rem 0.35rem;
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
}
</style>
