<template>
  <nav v-if="itensVisiveis.length" class="mobile-nav" aria-label="Navegação operacional">
    <router-link
      v-for="item in itensVisiveis"
      :key="item.path"
      :to="item.path"
      class="mobile-nav__item"
      :class="{ 'mobile-nav__item--active': isActive(item.path) }"
    >
      <component :is="item.iconComponent" class="mobile-nav__icon" aria-hidden="true" />
      <span class="mobile-nav__label">{{ item.shortLabel }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useMobileNavItems } from '@/composables/useNavItems'

const route = useRoute()
const itensVisiveis = useMobileNavItems()

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path === path || route.path.startsWith(`${path}/`)
}
</script>

<style scoped>
.mobile-nav {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1400;
  display: flex;
  align-items: stretch;
  justify-content: space-around;
  gap: 0.125rem;
  width: 100%;
  max-width: 100vw;
  min-height: var(--mobile-nav-height);
  padding: 0.35rem 0.25rem calc(0.35rem + env(safe-area-inset-bottom, 0px));
  background: var(--color-surface);
  border-top: 1px solid var(--color-border-subtle);
  box-shadow: 0 -4px 12px rgba(34, 42, 28, 0.08);
}

.mobile-nav__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.15rem;
  min-width: 0;
  min-height: var(--touch-target-min);
  padding: 0.2rem 0.15rem;
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-text-muted);
  transition: color 0.15s, background-color 0.15s;
}

.mobile-nav__item:hover {
  color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.mobile-nav__item--active {
  color: var(--color-primary);
  font-weight: 600;
}

.mobile-nav__icon {
  width: 1.35rem;
  height: 1.35rem;
  flex-shrink: 0;
  stroke-width: 1.75;
}

.mobile-nav__label {
  font-size: 0.625rem;
  line-height: 1.1;
  text-align: center;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
