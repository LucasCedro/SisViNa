<template>
  <PageLayout>
    <PageSection>
      <template #header>
        <div class="cfg-head">
          <div class="cfg-head__avatar" aria-hidden="true">
            {{ iniciais }}
          </div>
          <div>
            <h2 class="cfg-head__nome">{{ auth.user?.nome || '—' }}</h2>
            <p class="cfg-head__meta">
              <span>@{{ auth.user?.usuario }}</span>
              <span v-if="perfisLabel" class="cfg-head__perfis">{{ perfisLabel }}</span>
            </p>
          </div>
        </div>
      </template>

      <nav class="cfg-tabs" role="tablist" aria-label="Seções de configurações">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          role="tab"
          class="cfg-tab"
          :class="{ 'cfg-tab--active': abaAtiva === tab.id }"
          :aria-selected="abaAtiva === tab.id"
          @click="selecionarAba(tab.id)"
        >
          {{ tab.label }}
        </button>
      </nav>

      <!-- Perfil -->
      <section v-show="abaAtiva === 'perfil'" class="cfg-panel" aria-label="Dados do perfil">
        <p class="cfg-panel__lead">
          Informações editáveis do seu cadastro. CPF, usuário de login e perfis de acesso são gerenciados pelo administrador.
        </p>

        <form class="cfg-form" @submit.prevent="salvarPerfil">
          <div class="cfg-grid">
            <label class="cfg-field cfg-field--full">
              <span class="cfg-field__label">Nome completo</span>
              <input v-model="formPerfil.nome" type="text" required maxlength="100" />
            </label>

            <label class="cfg-field">
              <span class="cfg-field__label">E-mail</span>
              <input v-model="formPerfil.email" type="email" maxlength="100" />
            </label>

            <label class="cfg-field">
              <span class="cfg-field__label">Telefone</span>
              <MaskedInput v-model="formPerfil.telefone" mask="telefone" bare />
            </label>

            <label class="cfg-field">
              <span class="cfg-field__label">RG</span>
              <MaskedInput v-model="formPerfil.rg" mask="rg" bare />
            </label>

            <label class="cfg-field cfg-field--full">
              <span class="cfg-field__label">Endereço</span>
              <input v-model="formPerfil.endereco" type="text" maxlength="200" />
            </label>
          </div>

          <fieldset class="cfg-readonly">
            <legend>Dados administrativos (somente leitura)</legend>
            <dl class="cfg-dl">
              <div><dt>Usuário</dt><dd>{{ auth.user?.usuario || '—' }}</dd></div>
              <div><dt>CPF</dt><dd>{{ auth.user?.cpf || '—' }}</dd></div>
              <div><dt>Cargo</dt><dd>{{ auth.user?.cargo || '—' }}</dd></div>
              <div><dt>Contratação</dt><dd>{{ fmtData(auth.user?.data_contratacao) }}</dd></div>
              <div><dt>Cadastro no sistema</dt><dd>{{ fmtDataHora(auth.user?.data_cadastro) }}</dd></div>
            </dl>
          </fieldset>

          <p v-if="msgPerfil" class="cfg-msg" :class="msgPerfilTipo === 'erro' ? 'cfg-msg--erro' : 'cfg-msg--ok'">
            {{ msgPerfil }}
          </p>

          <div class="cfg-actions">
            <button type="button" class="cfg-btn cfg-btn--ghost" :disabled="salvandoPerfil" @click="resetFormPerfil">
              Desfazer
            </button>
            <button type="submit" class="cfg-btn cfg-btn--primary" :disabled="salvandoPerfil || !perfilAlterado">
              {{ salvandoPerfil ? 'Salvando…' : 'Salvar perfil' }}
            </button>
          </div>
        </form>
      </section>

      <!-- Configurações (conta) -->
      <section v-show="abaAtiva === 'configuracoes'" class="cfg-panel" aria-label="Configurações da conta">
        <p class="cfg-panel__lead">
          Segurança e preferências da sua conta no SisViNa.
        </p>

        <div class="cfg-subsection">
          <h3 class="cfg-subsection__title">Segurança</h3>
          <p class="cfg-subsection__lead">
            Altere sua senha de acesso. Use pelo menos 8 caracteres, com maiúsculas, minúsculas, número e caractere especial.
          </p>

          <form class="cfg-form" @submit.prevent="salvarSenha">
            <div class="cfg-grid cfg-grid--narrow">
              <label class="cfg-field cfg-field--full">
                <span class="cfg-field__label">Senha atual</span>
                <input v-model="formSenha.atual" type="password" autocomplete="current-password" required />
              </label>
              <label class="cfg-field cfg-field--full">
                <span class="cfg-field__label">Nova senha</span>
                <span class="cfg-field__pw">
                  <input
                    v-model="formSenha.nova"
                    :type="mostrarNovaSenha ? 'text' : 'password'"
                    autocomplete="new-password"
                    required
                    @input="validarNovaSenhaDebounced"
                  />
                  <button
                    type="button"
                    class="cfg-field__pw-toggle"
                    :aria-label="mostrarNovaSenha ? 'Ocultar senha' : 'Mostrar senha'"
                    :aria-pressed="mostrarNovaSenha"
                    @click="mostrarNovaSenha = !mostrarNovaSenha"
                  >
                    <svg v-if="mostrarNovaSenha" viewBox="0 0 24 24" aria-hidden="true" width="20" height="20">
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
                <span v-if="validacaoSenha.mensagem" class="cfg-field__hint" :class="{ 'cfg-field__hint--erro': !validacaoSenha.valida }">
                  {{ validacaoSenha.mensagem }}
                </span>
              </label>
              <label class="cfg-field cfg-field--full">
                <span class="cfg-field__label">Confirmar nova senha</span>
                <input v-model="formSenha.confirmacao" type="password" autocomplete="new-password" required />
                <span
                  v-if="formSenha.confirmacao && formSenha.nova !== formSenha.confirmacao"
                  class="cfg-field__hint cfg-field__hint--erro"
                >
                  As senhas não coincidem
                </span>
              </label>
            </div>

            <p v-if="msgSenha" class="cfg-msg" :class="msgSenhaTipo === 'erro' ? 'cfg-msg--erro' : 'cfg-msg--ok'">
              {{ msgSenha }}
            </p>

            <div class="cfg-actions">
              <button
                type="submit"
                class="cfg-btn cfg-btn--primary"
                :disabled="salvandoSenha || !podeSalvarSenha"
              >
                {{ salvandoSenha ? 'Atualizando…' : 'Atualizar senha' }}
              </button>
            </div>
          </form>
        </div>

        <div class="cfg-subsection">
          <h3 class="cfg-subsection__title">Preferências</h3>
          <p class="cfg-subsection__lead cfg-subsection__lead--muted">
            Notificações, idioma e aparência — disponível em breve.
          </p>
        </div>

        <div v-if="podeGodMode" class="cfg-subsection cfg-subsection--godmode">
          <h3 class="cfg-subsection__title">Administração do sistema</h3>
          <p class="cfg-subsection__lead">
            Cockpit exclusivo do administrador — visão overseer, usuários e matriz RBAC.
          </p>
          <router-link :to="{ name: 'admin-god-mode' }" class="cfg-godmode-btn">
            <span class="cfg-godmode-btn__icon" aria-hidden="true">◆</span>
            Abrir God Mode
          </router-link>
        </div>
      </section>
    </PageSection>
  </PageLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PageLayout from '@/components/layout/PageLayout.vue'
import PageSection from '@/components/layout/PageSection.vue'
import MaskedInput from '@/components/form/MaskedInput.vue'
import { useAuthStore } from '@/store/auth'
import { usePageTab } from '@/composables/usePageTab'
import { validatePassword } from '@/services/auth'
import { onlyDigits, parseRg } from '@/utils/inputMasks'

const auth = useAuthStore()
const router = useRouter()

const ABAS_VALIDAS = ['perfil', 'configuracoes']

const tabs = [
  { id: 'perfil', label: 'Perfil' },
  { id: 'configuracoes', label: 'Configurações' },
]
const abaAtiva = usePageTab('configuracoes', 'perfil', {
  valid: ABAS_VALIDAS,
  queryResolver: (r) => {
    const aba = r.query.aba
    return typeof aba === 'string' && ABAS_VALIDAS.includes(aba) ? aba : null
  },
})

const formPerfil = reactive({
  nome: '',
  email: '',
  telefone: '',
  rg: '',
  endereco: '',
})
const perfilOriginal = ref(null)
const salvandoPerfil = ref(false)
const msgPerfil = ref('')
const msgPerfilTipo = ref('ok')

const formSenha = reactive({ atual: '', nova: '', confirmacao: '' })
const validacaoSenha = reactive({ valida: false, mensagem: '' })
const salvandoSenha = ref(false)
const msgSenha = ref('')
const msgSenhaTipo = ref('ok')
const mostrarNovaSenha = ref(false)

let debounceValidacao = null

const iniciais = computed(() => {
  const nome = auth.user?.nome?.trim() || '?'
  const partes = nome.split(/\s+/).filter(Boolean)
  if (partes.length >= 2) return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
  return nome.slice(0, 2).toUpperCase()
})

const perfisLabel = computed(() => auth.perfilLabels.join(' · '))

const podeGodMode = computed(
  () => auth.can('admin.godmode.view') && auth.user?.perfis?.includes('admin')
)

const perfilAlterado = computed(() => {
  if (!perfilOriginal.value) return false
  return Object.keys(formPerfil).some((k) => (formPerfil[k] || '') !== (perfilOriginal.value[k] || ''))
})

const podeSalvarSenha = computed(() => {
  return (
    formSenha.atual &&
    formSenha.nova &&
    formSenha.confirmacao &&
    formSenha.nova === formSenha.confirmacao &&
    validacaoSenha.valida
  )
})

function snapshotPerfil(user) {
  return {
    nome: user?.nome || '',
    email: user?.email || '',
    telefone: onlyDigits(user?.telefone).slice(0, 11),
    rg: parseRg(user?.rg),
    endereco: user?.endereco || '',
  }
}

function resetFormPerfil() {
  if (perfilOriginal.value) Object.assign(formPerfil, perfilOriginal.value)
  msgPerfil.value = ''
}

function fmtData(v) {
  if (!v) return '—'
  try {
    return new Date(v).toLocaleDateString('pt-BR')
  } catch {
    return String(v)
  }
}

function fmtDataHora(v) {
  if (!v) return '—'
  try {
    return new Date(v).toLocaleString('pt-BR')
  } catch {
    return String(v)
  }
}

async function salvarPerfil() {
  salvandoPerfil.value = true
  msgPerfil.value = ''
  try {
    const payload = {}
    for (const [k, v] of Object.entries(formPerfil)) {
      let val = typeof v === 'string' ? v.trim() : v
      if (k === 'telefone') val = onlyDigits(val).slice(0, 11) || null
      if (k === 'rg') val = parseRg(val) || null
      if (val !== (perfilOriginal.value?.[k] || '')) {
        payload[k] = val || null
      }
    }
    if (!Object.keys(payload).length) return

    await auth.updateProfile(payload)
    perfilOriginal.value = snapshotPerfil(auth.user)
    msgPerfilTipo.value = 'ok'
    msgPerfil.value = 'Perfil atualizado com sucesso.'
  } catch (err) {
    msgPerfilTipo.value = 'erro'
    msgPerfil.value = err.response?.data?.detail || 'Não foi possível salvar o perfil.'
  } finally {
    salvandoPerfil.value = false
  }
}

function validarNovaSenhaDebounced() {
  clearTimeout(debounceValidacao)
  debounceValidacao = setTimeout(async () => {
    if (!formSenha.nova) {
      validacaoSenha.valida = false
      validacaoSenha.mensagem = ''
      return
    }
    try {
      const res = await validatePassword(formSenha.nova)
      validacaoSenha.valida = res.valid
      validacaoSenha.mensagem = res.message
    } catch {
      validacaoSenha.valida = false
      validacaoSenha.mensagem = 'Não foi possível validar a senha.'
    }
  }, 350)
}

async function salvarSenha() {
  if (!podeSalvarSenha.value) return
  salvandoSenha.value = true
  msgSenha.value = ''
  try {
    await auth.changePassword(formSenha.atual, formSenha.nova)
    formSenha.atual = ''
    formSenha.nova = ''
    formSenha.confirmacao = ''
    validacaoSenha.valida = false
    validacaoSenha.mensagem = ''
    mostrarNovaSenha.value = false
    msgSenhaTipo.value = 'ok'
    msgSenha.value = 'Senha alterada com sucesso.'
  } catch (err) {
    msgSenhaTipo.value = 'erro'
    msgSenha.value = err.response?.data?.detail || 'Não foi possível alterar a senha.'
  } finally {
    salvandoSenha.value = false
  }
}

function selecionarAba(id) {
  abaAtiva.value = id
  router.replace({ name: 'configuracoes', query: { aba: id } })
}

watch(
  () => auth.user,
  (user) => {
    if (!user) return
    perfilOriginal.value = snapshotPerfil(user)
    Object.assign(formPerfil, perfilOriginal.value)
  },
  { immediate: true }
)

onMounted(async () => {
  if (!auth.user) await auth.hydrate()
})
</script>

<style scoped>
.cfg-head {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.cfg-head__avatar {
  width: 3.25rem;
  height: 3.25rem;
  border-radius: var(--radius-full);
  background: var(--color-primary-muted, #e8f5e9);
  color: var(--color-primary, #2e7d32);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.cfg-head__nome {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.cfg-head__meta {
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
}

.cfg-head__perfis {
  color: var(--color-text-muted);
}

.cfg-tabs {
  display: flex;
  gap: 0.25rem;
  border-bottom: 1px solid var(--color-border-subtle);
  margin-bottom: var(--spacing-lg);
}

.cfg-tab {
  padding: 0.65rem 1rem;
  border: none;
  background: transparent;
  font-family: inherit;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color 0.15s, border-color 0.15s;
}

.cfg-tab:hover {
  color: var(--color-text-primary);
}

.cfg-tab--active {
  color: var(--color-primary, #2e7d32);
  border-bottom-color: var(--color-primary, #2e7d32);
  font-weight: 600;
}

.cfg-panel__lead {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
  line-height: 1.5;
  max-width: 52rem;
}

.cfg-form {
  max-width: 40rem;
}

.cfg-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.cfg-grid--narrow {
  max-width: 28rem;
}

.cfg-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.cfg-field--full {
  grid-column: 1 / -1;
}

.cfg-field__label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.cfg-field input {
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: 0.9rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.cfg-field input:focus {
  outline: 2px solid var(--color-primary-muted, #c8e6c9);
  border-color: var(--color-primary, #2e7d32);
}

.cfg-field__pw {
  position: relative;
  display: block;
}

.cfg-field__pw input {
  width: 100%;
  padding-right: 2.75rem;
}

.cfg-field__pw-toggle {
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

.cfg-field__pw-toggle:hover {
  color: var(--color-text-secondary);
  background: var(--color-background);
}

.cfg-field__pw-toggle:focus-visible {
  outline: 2px solid var(--color-primary-muted, #c8e6c9);
}

.cfg-field__hint {
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.cfg-field__hint--erro {
  color: #c62828;
}

.cfg-readonly {
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.cfg-readonly legend {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  padding: 0 0.35rem;
}

.cfg-dl {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr));
  gap: var(--spacing-sm) var(--spacing-lg);
  margin-top: var(--spacing-sm);
}

.cfg-dl dt {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.cfg-dl dd {
  font-size: 0.9rem;
  color: var(--color-text-primary);
  margin-top: 0.15rem;
}

.cfg-msg {
  font-size: 0.875rem;
  margin-bottom: var(--spacing-md);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
}

.cfg-msg--ok {
  background: #e8f5e9;
  color: #1b5e20;
}

.cfg-msg--erro {
  background: #ffebee;
  color: #b71c1c;
}

.cfg-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.cfg-btn {
  padding: 0.55rem 1.1rem;
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.15s, opacity 0.15s;
}

.cfg-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.cfg-btn--primary {
  background: var(--color-primary, #2e7d32);
  color: #fff;
}

.cfg-btn--primary:hover:not(:disabled) {
  filter: brightness(1.05);
}

.cfg-btn--ghost {
  background: var(--color-surface);
  border-color: var(--color-border);
  color: var(--color-text-secondary);
}

.cfg-btn--ghost:hover:not(:disabled) {
  background: var(--color-background);
}

.cfg-btn--danger {
  background: #fff;
  border-color: #ef9a9a;
  color: #c62828;
}

.cfg-btn--danger:hover {
  background: #ffebee;
}

.cfg-subsection {
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-subtle);
}

.cfg-subsection:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.cfg-subsection__title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.35rem;
}

.cfg-subsection__lead {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
  line-height: 1.5;
}

.cfg-subsection__lead--muted {
  color: var(--color-text-muted);
  font-style: italic;
}

.cfg-subsection--godmode {
  padding: var(--spacing-lg);
  border: 1px solid #d1c4e9;
  border-radius: var(--radius-md);
  background: linear-gradient(145deg, #faf8ff 0%, #fff 100%);
}

.cfg-godmode-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.1rem;
  border-radius: var(--radius-md);
  background: #5e35b1;
  color: #fff;
  font-weight: 600;
  font-size: 0.875rem;
  text-decoration: none;
  transition: filter 0.15s;
}

.cfg-godmode-btn:hover {
  filter: brightness(1.08);
  color: #fff;
}

.cfg-godmode-btn__icon {
  font-size: 0.65rem;
  opacity: 0.9;
}

.cfg-sessao-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  max-width: 36rem;
}

.cfg-sessao-card strong {
  display: block;
  margin-bottom: 0.25rem;
}

.cfg-sessao-card p {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.cfg-sessao-card code {
  font-size: 0.85em;
  background: var(--color-background);
  padding: 0.1rem 0.35rem;
  border-radius: var(--radius-sm);
}

@media (max-width: 640px) {
  .cfg-grid {
    grid-template-columns: 1fr;
  }
}
</style>
