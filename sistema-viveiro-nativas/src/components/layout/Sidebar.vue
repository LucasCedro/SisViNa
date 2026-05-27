<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2 class="sidebar-title">Viveiro Nativas</h2>
    </div>
    <nav class="sidebar-nav">
      <router-link
        v-for="item in itensVisiveis"
        :key="item.path"
        :to="item.path"
        class="nav-item"
      >
        <span class="nav-icon" aria-hidden="true">{{ item.iconChar }}</span>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { NAV_ITEMS } from '@/constants/navigation'
import { usePermissions } from '@/composables/usePermissions'

const ICON_CHARS = {
  home: '⌂',
  viveiro: '▣',
  fitossanidade: '✿',
  fertilizacao: 'N',
  vendas: '¤',
  prescricao: '≡',
  producao: '⇄',
  estoques: '▤',
  coleta: '❋',
  biblioteca: '☰',
  financeiro: '$',
}

const { can } = usePermissions()

const itensVisiveis = computed(() =>
  NAV_ITEMS.filter((item) => can(item.permission)).map((item) => ({
    ...item,
    iconChar: ICON_CHARS[item.icon] || '•',
  }))
)
</script>

<style>
.sidebar {
  width: 230px;
  min-width: 230px;
  height: 100%;
  background-color: var(--color-sidebar-bg);
  color: var(--color-sidebar-text-active);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-sidebar-text-active);
  letter-spacing: -0.01em;
}

.sidebar-nav {
  padding: var(--spacing-md) 0;
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  color: var(--color-sidebar-text);
  text-decoration: none;
  transition: background-color 0.2s, color 0.2s;
}

.nav-item:hover {
  background-color: var(--color-sidebar-hover);
  color: var(--color-sidebar-text-active);
}

.nav-item.router-link-active {
  background-color: var(--color-sidebar-hover);
  color: var(--color-sidebar-text-active);
  border-left: 3px solid var(--color-sidebar-active-accent);
}

.nav-icon {
  width: 1.5rem;
  margin-right: var(--spacing-md);
  text-align: center;
  font-size: 1rem;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
    min-width: 60px;
  }

  .sidebar-title {
    display: none;
  }

  .nav-item span:not(.nav-icon) {
    display: none;
  }

  .nav-icon {
    margin-right: 0;
  }

  .sidebar-header {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: var(--spacing-md);
  }
}
</style>
