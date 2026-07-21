<template>
  <div class="empresa-usuarios">
    <p v-if="erro" class="alert alert-error">{{ erro }}</p>
    <p v-if="msg" class="alert alert-success">{{ msg }}</p>

    <form class="empresa-usuarios__form" @submit.prevent="criar">
      <h4>Novo usuário</h4>
      <div class="empresa-usuarios__grid">
        <label>Nome<input v-model="form.nome" required /></label>
        <label>CPF<input v-model="form.cpf" required placeholder="000.000.000-00" /></label>
        <label>Usuário<input v-model="form.usuario" required /></label>
        <label>E-mail<input v-model="form.email" type="email" /></label>
        <label>Cargo<input v-model="form.cargo" /></label>
        <label>Senha<input v-model="form.senha" type="password" required /></label>
        <label class="empresa-usuarios__full">Perfis
          <select v-model="form.perfis" multiple size="4">
            <option v-for="p in perfisDisponiveis" :key="p.id" :value="p.id">{{ p.label }}</option>
          </select>
        </label>
      </div>
      <button type="submit" class="btn btn-primary btn-sm" :disabled="salvando">Criar usuário</button>
    </form>

    <table v-if="usuarios.length" class="empresa-usuarios__table">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Usuário</th>
          <th>Perfis</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in usuarios" :key="u.id">
          <td>{{ u.nome }}</td>
          <td>{{ u.usuario }}</td>
          <td>{{ (u.perfis || []).join(', ') }}</td>
          <td>{{ u.ativo ? 'Ativo' : 'Inativo' }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else-if="!carregando" class="empresa-usuarios__empty">Nenhum usuário cadastrado.</p>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { listEmpresaUsuarios, createEmpresaUsuario } from '@/services/empresa'

const perfisDisponiveis = [
  { id: 'gestor', label: 'Gestor' },
  { id: 'campo', label: 'Campo' },
  { id: 'financeiro', label: 'Financeiro' },
  { id: 'rh', label: 'RH' },
  { id: 'consulta', label: 'Consulta' },
  { id: 'empresa_admin', label: 'Admin da empresa' },
]

const usuarios = ref([])
const carregando = ref(false)
const salvando = ref(false)
const erro = ref('')
const msg = ref('')

const form = reactive({
  nome: '',
  cpf: '',
  usuario: '',
  email: '',
  cargo: '',
  senha: '',
  perfis: ['gestor'],
})

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    usuarios.value = await listEmpresaUsuarios({ ativo: true, limit: 200 })
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha ao carregar usuários.'
  } finally {
    carregando.value = false
  }
}

async function criar() {
  salvando.value = true
  erro.value = ''
  msg.value = ''
  try {
    await createEmpresaUsuario({ ...form, ativo: true })
    msg.value = 'Usuário criado.'
    Object.assign(form, { nome: '', cpf: '', usuario: '', email: '', cargo: '', senha: '', perfis: ['gestor'] })
    await carregar()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha ao criar usuário.'
  } finally {
    salvando.value = false
  }
}

onMounted(carregar)
</script>

<style scoped>
.empresa-usuarios__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.empresa-usuarios__full { grid-column: 1 / -1; }
.empresa-usuarios__grid label { display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.875rem; }
.empresa-usuarios__grid input,
.empresa-usuarios__grid select { padding: 0.4rem 0.5rem; border: 1px solid var(--color-border); border-radius: 6px; }
.empresa-usuarios__table { width: 100%; border-collapse: collapse; margin-top: 1.5rem; font-size: 0.875rem; }
.empresa-usuarios__table th,
.empresa-usuarios__table td { border-bottom: 1px solid var(--color-border); padding: 0.5rem; text-align: left; }
.empresa-usuarios__empty { color: var(--color-text-muted); margin-top: 1rem; }
</style>
