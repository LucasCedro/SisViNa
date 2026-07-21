<template>
  <PageLayout>
    <PageSection>
      <template #header>
        <div class="gm-head">
          <div>
            <p class="gm-head__eyebrow">Administração do sistema</p>
            <h2 class="gm-head__title">God Mode</h2>
            <p class="gm-head__sub">Cockpit exclusivo — visão overseer e gestão de usuários.</p>
          </div>
          <router-link :to="{ name: 'configuracoes', query: { aba: 'configuracoes' } }" class="gm-back">
            ← Configurações
          </router-link>
        </div>
      </template>

      <nav class="gm-tabs" role="tablist">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="gm-tab"
          :class="{ 'gm-tab--active': aba === tab.id }"
          @click="aba = tab.id"
        >
          {{ tab.label }}
        </button>
      </nav>

      <p v-if="erro" class="gm-erro">{{ erro }}</p>

      <!-- Overview -->
      <section v-show="aba === 'overview'" class="gm-panel">
        <div v-if="carregandoOverview" class="gm-loading">Carregando panorama…</div>
        <template v-else-if="overview">
          <div class="gm-cards">
            <article v-for="card in cardsOverview" :key="card.label" class="gm-card">
              <span class="gm-card__label">{{ card.label }}</span>
              <strong class="gm-card__value">{{ card.value }}</strong>
            </article>
          </div>

          <div class="gm-grid-2">
            <div class="gm-block">
              <h3>Usuários por perfil (ativos)</h3>
              <ul class="gm-list">
                <li v-for="(qtd, perfil) in overview.por_perfil" :key="perfil">
                  <span>{{ labelPerfil(perfil) }}</span>
                  <strong>{{ qtd }}</strong>
                </li>
              </ul>
            </div>
            <div class="gm-block">
              <h3>Infra & RBAC</h3>
              <dl class="gm-dl">
                <div><dt>Migration Alembic</dt><dd><code>{{ overview.alembic_revision || '—' }}</code></dd></div>
                <div><dt>Permissões no catálogo</dt><dd>{{ overview.permissoes_catalogo }}</dd></div>
                <div><dt>Perfis RBAC</dt><dd>{{ overview.perfis_rbac }}</dd></div>
                <div><dt>Sem perfis atribuídos</dt><dd>{{ overview.funcionarios_sem_perfis }}</dd></div>
              </dl>
            </div>
          </div>

          <div class="gm-block gm-block--wide">
            <h3>Unidades viveiro (cross-tenant)</h3>
            <table class="gm-table gm-table--compact">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Modo</th>
                  <th>Usuários</th>
                  <th>Lotes ativos</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="v in overview.viveiros || []" :key="v.id">
                  <td>{{ v.nome }}</td>
                  <td><span class="gm-tag">{{ v.modo_label }}</span></td>
                  <td>{{ v.funcionarios_vinculados }}</td>
                  <td>{{ v.lotes_producao_ativos }}</td>
                  <td>
                    <span :class="v.ativo ? 'gm-badge gm-badge--ok' : 'gm-badge gm-badge--off'">
                      {{ v.ativo ? 'Ativo' : 'Inativo' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </section>

      <!-- Usuários -->
      <section v-show="aba === 'usuarios'" class="gm-panel">
        <div class="gm-toolbar">
          <label class="gm-filter">
            <span>Status</span>
            <select v-model="filtroAtivo" @change="carregarUsuarios">
              <option :value="null">Todos</option>
              <option :value="true">Ativos</option>
              <option :value="false">Inativos</option>
            </select>
          </label>
          <button v-if="podeGerenciar" type="button" class="gm-btn gm-btn--primary" @click="abrirNovoUsuario">
            + Novo usuário
          </button>
        </div>

        <div v-if="carregandoUsuarios" class="gm-loading">Carregando usuários…</div>
        <div v-else class="gm-table-wrap">
          <table class="gm-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Usuário</th>
                <th>Perfis</th>
                <th>Cargo</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in usuarios" :key="u.id">
                <td>{{ u.nome }}</td>
                <td><code>@{{ u.usuario }}</code></td>
                <td>
                  <span v-for="p in u.perfis || []" :key="p" class="gm-tag">{{ labelPerfil(p) }}</span>
                  <span v-if="!u.perfis?.length" class="gm-muted">—</span>
                </td>
                <td>{{ u.cargo || '—' }}</td>
                <td>
                  <span :class="u.ativo ? 'gm-badge gm-badge--ok' : 'gm-badge gm-badge--off'">
                    {{ u.ativo ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td v-if="podeGerenciar" class="gm-actions">
                  <button type="button" class="gm-btn gm-btn--ghost gm-btn--sm" @click="editarUsuario(u)">Editar</button>
                  <button
                    v-if="u.ativo && u.id !== auth.user?.id"
                    type="button"
                    class="gm-btn gm-btn--danger gm-btn--sm"
                    @click="desativarUsuario(u)"
                  >
                    Desativar
                  </button>
                </td>
                <td v-else />
              </tr>
            </tbody>
          </table>
          <p class="gm-muted gm-table-foot">{{ usuariosTotal }} usuário(s) no total</p>
        </div>
      </section>

      <!-- RBAC -->
      <section v-show="aba === 'rbac'" class="gm-panel">
        <div v-if="carregandoRbac" class="gm-loading">Carregando matriz RBAC…</div>
        <template v-else-if="rbac">
          <p class="gm-lead">Mapa estático de perfis → permissões (backend SSOT).</p>
          <div v-for="role in rbac.roles" :key="role.id" class="gm-block gm-block--rbac">
            <h3>{{ role.label }} <code>{{ role.id }}</code></h3>
            <p class="gm-perms">{{ role.permissoes.join(' · ') }}</p>
          </div>
        </template>
      </section>
    </PageSection>

    <!-- Modal usuário -->
    <AppModalOverlay
      :aberto="modalUsuarioAberto"
      :handlers="overlayUsuario"
      panel-class="app-modal-panel--wide"
      :aria-labelledby="formUsuario.id ? 'gm-editar-titulo' : 'gm-novo-titulo'"
    >
      <form @submit.prevent="salvarUsuario">
        <header class="app-modal-header">
          <div>
            <h3 :id="formUsuario.id ? 'gm-editar-titulo' : 'gm-novo-titulo'">
              {{ formUsuario.id ? 'Editar usuário' : 'Novo usuário' }}
            </h3>
          </div>
          <button type="button" class="app-modal-fechar" aria-label="Fechar" @click="fecharUsuario">×</button>
        </header>
        <div class="gm-modal__body">
        <div class="gm-form-grid">
          <label class="gm-field gm-field--full">
            <span>Nome</span>
            <input v-model="formUsuario.nome" required maxlength="100" />
          </label>
          <label class="gm-field">
            <span>Usuário (login)</span>
            <input v-model="formUsuario.usuario" required maxlength="50" />
          </label>
          <label class="gm-field">
            <span>CPF</span>
            <MaskedInput v-model="formUsuario.cpf" mask="cpf" bare required />
          </label>
          <label class="gm-field">
            <span>E-mail</span>
            <input v-model="formUsuario.email" type="email" maxlength="100" />
          </label>
          <label class="gm-field">
            <span>Cargo</span>
            <input v-model="formUsuario.cargo" maxlength="80" />
          </label>
          <label v-if="!formUsuario.id" class="gm-field">
            <span>Senha inicial</span>
            <span class="gm-field__pw">
              <input
                v-model="formUsuario.senha"
                :type="mostrarSenha ? 'text' : 'password'"
                required
                minlength="8"
              />
              <button
                type="button"
                class="gm-field__pw-toggle"
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
          </label>
          <label v-else class="gm-field">
            <span>Nova senha (opcional)</span>
            <span class="gm-field__pw">
              <input
                v-model="formUsuario.senha"
                :type="mostrarSenha ? 'text' : 'password'"
                minlength="8"
              />
              <button
                type="button"
                class="gm-field__pw-toggle"
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
          </label>
          <fieldset class="gm-field gm-field--full">
            <legend>Perfis de acesso</legend>
            <div class="gm-checks">
              <label v-for="(label, id) in ROLES_LABELS" :key="id" class="gm-check">
                <input v-model="formUsuario.perfis" type="checkbox" :value="id" />
                {{ label }}
              </label>
            </div>
          </fieldset>
          <label v-if="formUsuario.id" class="gm-check gm-field--full">
            <input v-model="formUsuario.ativo" type="checkbox" />
            Conta ativa
          </label>
        </div>
        <p v-if="msgModal" class="gm-erro">{{ msgModal }}</p>
        </div>
        <footer class="app-modal-footer">
          <button type="button" class="gm-btn gm-btn--ghost" @click="fecharUsuario">Cancelar</button>
          <button type="submit" class="gm-btn gm-btn--primary" :disabled="salvandoUsuario">
            {{ salvandoUsuario ? 'Salvando…' : 'Salvar' }}
          </button>
        </footer>
      </form>
    </AppModalOverlay>

    <ConfirmSaidaModal
      :aberto="confirmAberto"
      @confirmar="confirmarSaida"
      @cancelar="cancelarSaida"
    />
  </PageLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch, nextTick } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import ConfirmSaidaModal from '@/components/shared/ConfirmSaidaModal.vue'
import { useModalFormClose } from '@/composables/useModalFormClose'
import { useFormDirty } from '@/utils/formDirty'
import PageLayout from '@/components/layout/PageLayout.vue'
import PageSection from '@/components/layout/PageSection.vue'
import MaskedInput from '@/components/form/MaskedInput.vue'
import { ROLES_LABELS } from '@/constants/roles'
import { useAuthStore } from '@/store/auth'
import { usePermissions } from '@/composables/usePermissions'
import { usePageTab } from '@/composables/usePageTab'
import {
  fetchAdminOverview,
  fetchAdminRbac,
  listAdminFuncionarios,
  createAdminFuncionario,
  updateAdminFuncionario,
  deactivateAdminFuncionario,
} from '@/services/adminCockpit'
import { onlyDigits } from '@/utils/inputMasks'

const auth = useAuthStore()
const { can } = usePermissions()
const podeGerenciar = computed(() => can('admin.godmode.manage'))

const tabs = [
  { id: 'overview', label: 'Visão geral' },
  { id: 'usuarios', label: 'Usuários' },
  { id: 'rbac', label: 'Matriz RBAC' },
]
const aba = usePageTab('admin-god-mode', 'overview', { valid: ['overview', 'usuarios', 'rbac'] })
const erro = ref('')

const overview = ref(null)
const carregandoOverview = ref(false)
const rbac = ref(null)
const carregandoRbac = ref(false)

const usuarios = ref([])
const usuariosTotal = ref(0)
const carregandoUsuarios = ref(false)
const filtroAtivo = ref(null)

const modalUsuarioAberto = ref(false)
const salvandoUsuario = ref(false)
const msgModal = ref('')
const mostrarSenha = ref(false)
const formUsuario = reactive({
  id: null,
  nome: '',
  usuario: '',
  cpf: '',
  email: '',
  cargo: '',
  senha: '',
  perfis: [],
  ativo: true,
})

const { isDirty, rebase } = useFormDirty(formUsuario, () => modalUsuarioAberto.value)

function fecharUsuarioInterno() {
  modalUsuarioAberto.value = false
  mostrarSenha.value = false
}

const overlayUsuario = useModalFormClose(
  fecharUsuarioInterno,
  () => isDirty.value,
  () => modalUsuarioAberto.value
)

const {
  confirmAberto,
  confirmarSaida,
  cancelarSaida,
  sairSemConfirmar,
} = overlayUsuario

function fecharUsuario() {
  overlayUsuario.resetOverlayPress()
  overlayUsuario.requestClose()
}

const cardsOverview = computed(() => {
  if (!overview.value) return []
  const o = overview.value
  return [
    { label: 'Usuários ativos', value: o.funcionarios_ativos },
    { label: 'Unidades viveiro', value: o.viveiros_total },
    { label: 'Florestal', value: o.viveiros_florestal },
    { label: 'Plantas', value: o.plantas_total },
    { label: 'Vendas', value: o.vendas_total },
    { label: 'Permissões', value: o.permissoes_catalogo },
  ]
})

function labelPerfil(id) {
  return ROLES_LABELS[id] || id
}

async function carregarOverview() {
  carregandoOverview.value = true
  erro.value = ''
  try {
    overview.value = await fetchAdminOverview()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Não foi possível carregar o panorama.'
  } finally {
    carregandoOverview.value = false
  }
}

async function carregarRbac() {
  if (rbac.value) return
  carregandoRbac.value = true
  try {
    rbac.value = await fetchAdminRbac()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Não foi possível carregar RBAC.'
  } finally {
    carregandoRbac.value = false
  }
}

async function carregarUsuarios() {
  carregandoUsuarios.value = true
  try {
    const params = { limit: 200 }
    if (filtroAtivo.value !== null) params.ativo = filtroAtivo.value
    const data = await listAdminFuncionarios(params)
    usuarios.value = data.items
    usuariosTotal.value = data.total
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao listar usuários.'
  } finally {
    carregandoUsuarios.value = false
  }
}

function resetForm() {
  Object.assign(formUsuario, {
    id: null,
    nome: '',
    usuario: '',
    cpf: '',
    email: '',
    cargo: '',
    senha: '',
    perfis: [],
    ativo: true,
  })
  msgModal.value = ''
  mostrarSenha.value = false
}

async function abrirNovoUsuario() {
  if (!podeGerenciar.value) return
  resetForm()
  modalUsuarioAberto.value = true
  await nextTick()
  rebase()
}

async function editarUsuario(u) {
  if (!podeGerenciar.value) return
  resetForm()
  Object.assign(formUsuario, {
    id: u.id,
    nome: u.nome,
    usuario: u.usuario,
    cpf: onlyDigits(u.cpf).slice(0, 11),
    email: u.email || '',
    cargo: u.cargo || '',
    senha: '',
    perfis: [...(u.perfis || [])],
    ativo: u.ativo !== false,
  })
  modalUsuarioAberto.value = true
  await nextTick()
  rebase()
}

async function salvarUsuario() {
  salvandoUsuario.value = true
  msgModal.value = ''
  try {
    if (formUsuario.id) {
      const payload = {
        nome: formUsuario.nome.trim(),
        usuario: formUsuario.usuario.trim(),
        cpf: onlyDigits(formUsuario.cpf).slice(0, 11),
        email: formUsuario.email?.trim() || null,
        cargo: formUsuario.cargo?.trim() || null,
        perfis: formUsuario.perfis,
        ativo: formUsuario.ativo,
      }
      if (formUsuario.senha) payload.senha = formUsuario.senha
      await updateAdminFuncionario(formUsuario.id, payload)
    } else {
      await createAdminFuncionario({
        nome: formUsuario.nome.trim(),
        usuario: formUsuario.usuario.trim(),
        cpf: onlyDigits(formUsuario.cpf).slice(0, 11),
        email: formUsuario.email?.trim() || null,
        cargo: formUsuario.cargo?.trim() || null,
        senha: formUsuario.senha,
        perfis: formUsuario.perfis.length ? formUsuario.perfis : ['campo'],
        ativo: true,
      })
    }
    sairSemConfirmar()
    await carregarUsuarios()
    if (aba.value === 'overview') await carregarOverview()
  } catch (e) {
    msgModal.value = e.response?.data?.detail || 'Erro ao salvar usuário.'
  } finally {
    salvandoUsuario.value = false
  }
}

async function desativarUsuario(u) {
  if (!podeGerenciar.value) return
  if (!confirm(`Desativar ${u.nome}?`)) return
  try {
    await deactivateAdminFuncionario(u.id)
    await carregarUsuarios()
    await carregarOverview()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao desativar.'
  }
}

watch(aba, (v) => {
  if (v === 'rbac') carregarRbac()
  if (v === 'usuarios') carregarUsuarios()
})

onMounted(async () => {
  if (!auth.user) await auth.hydrate()
  await carregarOverview()
})
</script>

<style scoped>
.gm-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.gm-head__eyebrow {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #5e35b1;
  font-weight: 600;
}

.gm-head__title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-top: 0.15rem;
}

.gm-head__sub {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-top: 0.35rem;
}

.gm-back {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  text-decoration: none;
}

.gm-back:hover {
  color: #5e35b1;
}

.gm-tabs {
  display: flex;
  gap: 0.25rem;
  border-bottom: 1px solid var(--color-border-subtle);
  margin-bottom: var(--spacing-lg);
}

.gm-tab {
  padding: 0.65rem 1rem;
  border: none;
  background: transparent;
  font-family: inherit;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.gm-tab--active {
  color: #5e35b1;
  border-bottom-color: #5e35b1;
  font-weight: 600;
}

.gm-panel {
  min-height: 12rem;
}

.gm-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(9rem, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.gm-card {
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-subtle);
  background: linear-gradient(145deg, #faf8ff 0%, #fff 100%);
}

.gm-card__label {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: 0.35rem;
}

.gm-card__value {
  font-size: 1.5rem;
  color: #4527a0;
}

.gm-grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: var(--spacing-lg);
}

.gm-block {
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
}

.gm-block h3 {
  font-size: 0.95rem;
  margin-bottom: var(--spacing-md);
}

.gm-block--wide {
  margin-top: var(--spacing-lg);
}

.gm-table--compact th,
.gm-table--compact td {
  font-size: 0.8125rem;
  padding: 0.4rem 0.5rem;
}

.gm-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.gm-list li {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.gm-dl {
  display: grid;
  gap: 0.65rem;
}

.gm-dl dt {
  font-size: 0.72rem;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.gm-dl dd {
  font-size: 0.9rem;
}

.gm-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
}

.gm-filter {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.gm-filter select {
  padding: 0.45rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: inherit;
}

.gm-table-wrap {
  overflow-x: auto;
}

.gm-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.gm-table th,
.gm-table td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid var(--color-border-subtle);
  text-align: left;
  vertical-align: middle;
}

.gm-table th {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.gm-tag {
  display: inline-block;
  font-size: 0.72rem;
  padding: 0.15rem 0.45rem;
  margin: 0.1rem 0.2rem 0.1rem 0;
  border-radius: var(--radius-sm);
  background: #ede7f6;
  color: #4527a0;
}

.gm-badge {
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-full);
}

.gm-badge--ok {
  background: #e8f5e9;
  color: #1b5e20;
}

.gm-badge--off {
  background: #f5f5f5;
  color: #757575;
}

.gm-actions {
  white-space: nowrap;
}

.gm-btn {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: 0.875rem;
  cursor: pointer;
  border: 1px solid transparent;
}

.gm-btn--sm {
  padding: 0.35rem 0.65rem;
  font-size: 0.8rem;
}

.gm-btn--primary {
  background: #5e35b1;
  color: #fff;
}

.gm-btn--ghost {
  background: var(--color-surface);
  border-color: var(--color-border);
  color: var(--color-text-secondary);
}

.gm-btn--danger {
  background: #fff;
  border-color: #ef9a9a;
  color: #c62828;
}

.gm-block--rbac {
  margin-bottom: var(--spacing-md);
}

.gm-perms {
  font-size: 0.78rem;
  line-height: 1.6;
  color: var(--color-text-secondary);
  word-break: break-word;
}

.gm-lead {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
}

.gm-muted {
  color: var(--color-text-muted);
  font-size: 0.8rem;
}

.gm-table-foot {
  margin-top: 0.5rem;
}

.gm-loading {
  padding: var(--spacing-xl);
  text-align: center;
  color: var(--color-text-muted);
}

.gm-erro {
  color: #c62828;
  font-size: 0.875rem;
  margin-bottom: var(--spacing-md);
}

.gm-modal__body {
  padding: 0 1.5rem 1.25rem;
}

.gm-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.gm-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.gm-field--full {
  grid-column: 1 / -1;
}

.gm-field input {
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: inherit;
}

.gm-field__pw {
  position: relative;
  display: block;
}

.gm-field__pw input {
  width: 100%;
  padding-right: 2.75rem;
}

.gm-field__pw-toggle {
  position: absolute;
  top: 50%;
  right: 0.35rem;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  padding: 0;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
}

.gm-field__pw-toggle:hover {
  color: var(--color-text-secondary);
  background: var(--color-background);
}

.gm-field__pw-toggle:focus-visible {
  outline: 2px solid #d1c4e9;
}

.gm-checks {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
  gap: 0.35rem;
  margin-top: 0.35rem;
}

.gm-check {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: var(--color-text-primary);
}

</style>
