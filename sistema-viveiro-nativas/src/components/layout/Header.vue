<template>
    <header class="app-header">
        <div class="header-content">
            <h1 v-if="!hideTitle" class="page-title">{{ title }}</h1>
            <span v-else class="page-title page-title--subtle">SisViNa</span>
            <div class="header-actions">
                <span v-if="auth.user" class="user-label">{{ auth.user.nome }}</span>
                <button v-if="auth.isAuthenticated" type="button" class="logout-btn" @click="onLogout">
                    Sair
                </button>
                <button class="icon-button">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                </button>
                <button class="icon-button">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                </button>
            </div>
        </div>
    </header>
</template>

<script setup>
import { defineProps } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'

const router = useRouter()
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

function onLogout() {
    auth.logout()
    router.push({ name: 'login' })
}
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

.page-title--subtle {
    font-size: 1rem;
    font-weight: 500;
    color: var(--color-text-muted);
}

.header-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.user-label {
    font-size: 0.875rem;
    color: var(--color-text-secondary);
}

.logout-btn {
    padding: 0.4rem 0.75rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-surface);
    cursor: pointer;
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    font-family: inherit;
    transition: background-color 0.2s;
}

.logout-btn:hover {
    background: var(--color-background);
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

.icon-button:hover {
    background-color: var(--color-background);
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
}
</style>