<template>
    <header class="app-header">
        <div class="header-content">
            <h1 v-if="!hideTitle" class="page-title">{{ title }}</h1>
            <img
                v-else
                src="/assets/branding/logo_simp.jpg"
                alt="Brotare"
                class="header-brand-logo"
            />
            <div class="header-actions">
                <AdminViveiroSelector v-if="auth.isAuthenticated" />
                <div v-if="auth.isAuthenticated && auth.user" class="user-chip">
                    <span class="user-chip__avatar" aria-hidden="true">{{ iniciais }}</span>
                    <span class="user-chip__nome">{{ auth.user.nome }}</span>
                </div>
                <button
                    type="button"
                    class="icon-button"
                    title="Notificações (em breve)"
                    aria-label="Notificações — em breve"
                    disabled
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                </button>
                <UserAccountMenu v-if="auth.isAuthenticated" />
            </div>
        </div>
    </header>
</template>

<script setup>
import { computed, defineProps } from 'vue'
import { useAuthStore } from '../../store/auth'
import UserAccountMenu from './UserAccountMenu.vue'
import AdminViveiroSelector from './AdminViveiroSelector.vue'

const auth = useAuthStore()

defineProps({
    title: {
        type: String,
        required: true
    },
    hideTitle: {
        type: Boolean,
        default: false
    }
})

const iniciais = computed(() => {
    const nome = auth.user?.nome?.trim() || '?'
    const partes = nome.split(/\s+/).filter(Boolean)
    if (partes.length >= 2) return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
    return nome.slice(0, 2).toUpperCase()
})
</script>

<style>
.app-header {
    width: 100%;
    height: 70px;
    background-color: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow-sm);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
    padding: 0 var(--spacing-xl);
}

.page-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-text-primary);
}

.header-brand-logo {
    display: block;
    height: 2.25rem;
    width: auto;
    object-fit: contain;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.user-chip {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.6rem 0.25rem 0.25rem;
    border-radius: var(--radius-full);
    max-width: 14rem;
}

.user-chip__avatar {
    width: 2rem;
    height: 2rem;
    border-radius: var(--radius-full);
    background: var(--color-primary-muted, #e8f5e9);
    color: var(--color-primary, #2e7d32);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    flex-shrink: 0;
}

.user-chip__nome {
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.icon-button {
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

.icon-button:hover:not(:disabled) {
    background-color: var(--color-background);
}

.icon-button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

.icon-button .icon {
    width: 24px;
    height: 24px;
    color: var(--color-text-secondary);
}

@media (max-width: 768px) {
    .header-content {
        padding: 0 var(--spacing-md);
    }

    .page-title {
        font-size: 1.25rem;
    }

    .user-chip__nome {
        display: none;
    }
}
</style>
