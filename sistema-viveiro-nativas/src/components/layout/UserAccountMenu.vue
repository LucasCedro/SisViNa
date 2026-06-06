<template>
  <div ref="rootRef" class="account-menu">
    <button
      type="button"
      class="account-menu__trigger icon-button"
      :class="{ 'icon-button--active': aberto || isConfiguracoes }"
      title="Conta e configurações"
      aria-label="Menu da conta"
      aria-haspopup="menu"
      :aria-expanded="aberto"
      @click="toggle"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    </button>

    <Transition name="account-menu-fade">
      <div v-if="aberto" class="account-menu__panel" role="menu" aria-label="Opções da conta">
        <div v-if="auth.user" class="account-menu__head">
          <span class="account-menu__avatar" aria-hidden="true">{{ iniciais }}</span>
          <div class="account-menu__head-text">
            <strong>{{ auth.user.nome }}</strong>
            <span>@{{ auth.user.usuario }}</span>
          </div>
        </div>

        <ul class="account-menu__list">
          <li>
            <button type="button" role="menuitem" class="account-menu__item" @click="irPara('perfil')">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4 0-7 2-7 4v1h14v-1c0-2-3-4-7-4Z"/></svg>
              Perfil
            </button>
          </li>
          <li>
            <button type="button" role="menuitem" class="account-menu__item" @click="irPara('configuracoes')">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M19.14 12.94a7.07 7.07 0 0 0 .05-.94 7.07 7.07 0 0 0-.05-.94l2.03-1.58a.5.5 0 0 0 .12-.64l-1.92-3.32a.5.5 0 0 0-.61-.22l-2.39.96a7.28 7.28 0 0 0-1.63-.94l-.36-2.54a.5.5 0 0 0-.49-.42h-3.84a.5.5 0 0 0-.49.42l-.36 2.54a7.28 7.28 0 0 0-1.63.94l-2.39-.96a.5.5 0 0 0-.61.22L2.74 8.84a.5.5 0 0 0 .12.64l2.03 1.58a7.07 7.07 0 0 0-.05.94c0 .32.02.64.05.94L2.86 14.9a.5.5 0 0 0-.12.64l1.92 3.32a.5.5 0 0 0 .61.22l2.39-.96c.5.39 1.05.71 1.63.94l.36 2.54a.5.5 0 0 0 .49.42h3.84a.5.5 0 0 0 .49-.42l.36-2.54c.58-.23 1.13-.55 1.63-.94l2.39.96a.5.5 0 0 0 .61-.22l1.92-3.32a.5.5 0 0 0-.12-.64l-2.03-1.58ZM12 15.5A3.5 3.5 0 1 1 15.5 12 3.5 3.5 0 0 1 12 15.5Z"/></svg>
              Configurações
            </button>
          </li>
        </ul>

        <div class="account-menu__divider" role="separator" />

        <button type="button" role="menuitem" class="account-menu__item account-menu__item--danger" @click="sair">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M10 17v-2h8v-6h-8V7l-5 5 5 5Zm-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h3v2H5v10h3v2Z"/></svg>
          Sair
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const aberto = ref(false)
const rootRef = ref(null)

const isConfiguracoes = computed(() => route.name === 'configuracoes')

const iniciais = computed(() => {
  const nome = auth.user?.nome?.trim() || '?'
  const partes = nome.split(/\s+/).filter(Boolean)
  if (partes.length >= 2) return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
  return nome.slice(0, 2).toUpperCase()
})

function toggle() {
  aberto.value = !aberto.value
}

function fechar() {
  aberto.value = false
}

function irPara(aba) {
  fechar()
  router.push({ name: 'configuracoes', query: { aba } })
}

function sair() {
  fechar()
  auth.logout()
  router.push({ name: 'login' })
}

function onDocClick(e) {
  if (!aberto.value) return
  if (rootRef.value && !rootRef.value.contains(e.target)) fechar()
}

function onKeydown(e) {
  if (e.key === 'Escape') fechar()
}

onMounted(() => {
  document.addEventListener('click', onDocClick)
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocClick)
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.account-menu {
  position: relative;
}

.account-menu__trigger {
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.account-menu__trigger:hover {
  background-color: var(--color-background);
}

.account-menu__trigger.icon-button--active {
  background-color: var(--color-primary-muted, #e8f5e9);
}

.account-menu__trigger.icon-button--active .icon {
  color: var(--color-primary, #2e7d32);
}

.account-menu__trigger .icon {
  width: 24px;
  height: 24px;
  color: var(--color-text-secondary);
}

.account-menu__panel {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 15rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md, 0 8px 24px rgba(0, 0, 0, 0.12));
  padding: 0.5rem;
  z-index: 200;
}

.account-menu__head {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.5rem 0.65rem 0.75rem;
}

.account-menu__avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-full);
  background: var(--color-primary-muted, #e8f5e9);
  color: var(--color-primary, #2e7d32);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  flex-shrink: 0;
}

.account-menu__head-text {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 0;
}

.account-menu__head-text strong {
  font-size: 0.875rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.account-menu__head-text span {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.account-menu__list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.account-menu__item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 0.65rem;
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  font-family: inherit;
  font-size: 0.875rem;
  color: var(--color-text-primary);
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.account-menu__item svg {
  width: 1.1rem;
  height: 1.1rem;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.account-menu__item:hover {
  background: var(--color-background);
}

.account-menu__item--danger {
  color: #c62828;
}

.account-menu__item--danger svg {
  color: #c62828;
}

.account-menu__divider {
  height: 1px;
  background: var(--color-border-subtle);
  margin: 0.35rem 0;
}

.account-menu-fade-enter-active,
.account-menu-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.account-menu-fade-enter-from,
.account-menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
