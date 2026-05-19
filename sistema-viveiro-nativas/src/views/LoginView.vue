<template>
  <div class="login-page">
    <div class="login-card">
      <h1>SisViNa</h1>
      <p class="subtitle">Gestão de Viveiro de Plantas Nativas</p>

      <form @submit.prevent="onSubmit">
        <label>
          Usuário
          <input v-model="username" type="text" autocomplete="username" required />
        </label>
        <label>
          Senha
          <input v-model="password" type="password" autocomplete="current-password" required />
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">
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
  background: linear-gradient(135deg, #e8f4fc 0%, #f5f7fa 100%);
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  padding: 2rem;
}

h1 {
  font-size: 1.75rem;
  margin-bottom: 0.25rem;
  color: #2c3e50;
}

.subtitle {
  color: #6c7a89;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #2c3e50;
}

input {
  padding: 0.65rem 0.75rem;
  border: 1px solid #e1e5eb;
  border-radius: 8px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #3498db;
}

button {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #3498db;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error {
  color: #e74c3c;
  font-size: 0.875rem;
  margin: 0;
}

.hint {
  margin-top: 1.25rem;
  font-size: 0.8rem;
  color: #6c7a89;
  text-align: center;
}

code {
  background: #f0f2f5;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}
</style>
