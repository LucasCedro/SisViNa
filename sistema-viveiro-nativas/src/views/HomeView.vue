<template>
    <div class="home-view">
        <div class="hero-section">
            <h1 class="hero-title">Bem-vindo ao Sistema Viveiro Nativas</h1>
            <p class="hero-subtitle">Gerenciamento inteligente para coleta, cultivo e preservação de espécies nativas
            </p>
        </div>

        <div class="features-grid">
            <div class="feature-card" @click="navigateTo('/viveiro')">
                <div class="feature-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                    </svg>
                </div>
                <h2 class="feature-title">Gerenciamento do Viveiro</h2>
                <p class="feature-desc">Acompanhe o desenvolvimento de mudas, controle de estoque e métricas de
                    crescimento.</p>
                <div class="feature-link">Acessar</div>
            </div>

            <div class="feature-card" @click="navigateTo('/coleta')">
                <div class="feature-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                    </svg>
                </div>
                <h2 class="feature-title">Coleta de Sementes</h2>
                <p class="feature-desc">Gerencie árvores matrizes, planeje expedições e registre dados de coleta.</p>
                <div class="feature-link">Acessar</div>
            </div>

            <div class="feature-card" @click="navigateTo('/biblioteca')">
                <div class="feature-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                </div>
                <h2 class="feature-title">Biblioteca de Espécies</h2>
                <p class="feature-desc">Consulte informações detalhadas sobre espécies nativas, métodos de cultivo e
                    usos.</p>
                <div class="feature-link">Acessar</div>
            </div>
        </div>

        <div class="stats-section">
            <div class="stat-card">
                <h3 class="stat-value">{{ stats.especies }}</h3>
                <p class="stat-label">Espécies</p>
            </div>
            <div class="stat-card">
                <h3 class="stat-value">{{ stats.matrizes }}</h3>
                <p class="stat-label">Árvores matrizes</p>
            </div>
            <div class="stat-card">
                <h3 class="stat-value">{{ stats.mudas }}</h3>
                <p class="stat-label">Mudas ativas</p>
            </div>
            <div class="stat-card">
                <h3 class="stat-value">{{ stats.coletas }}</h3>
                <p class="stat-label">Coletas registradas</p>
            </div>
            <div class="stat-card">
                <h3 class="stat-value">{{ stats.vendasMes }}</h3>
                <p class="stat-label">Vendas pagas (mês)</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardResumo } from '../services/dashboard'

const router = useRouter()
const stats = reactive({
  especies: '—',
  matrizes: '—',
  mudas: '—',
  coletas: '—',
  vendasMes: '—'
})

const navigateTo = (path) => {
    router.push(path)
}

function fmtMoeda(v) {
  if (v == null || v === '—') return '—'
  return `R$ ${Number(v).toLocaleString('pt-BR', { maximumFractionDigits: 0 })}`
}

onMounted(async () => {
    try {
        const d = await getDashboardResumo()
        stats.especies = d.especies
        stats.matrizes = d.matrizes
        stats.mudas = d.mudas_ativas
        stats.coletas = d.coletas
        stats.vendasMes = fmtMoeda(d.vendas_mes)
    } catch {
        Object.keys(stats).forEach((k) => { stats[k] = '!' })
    }
})
</script>

<style>
.home-view {
    padding: var(--spacing-xl);
    max-width: 1400px;
    margin: 0 auto;
}

.hero-section {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-md);
}

.hero-subtitle {
    font-size: 1.25rem;
    color: var(--color-text-secondary);
    max-width: 800px;
    margin: 0 auto;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
}

.feature-card {
    background-color: var(--color-surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    padding: var(--spacing-xl);
    transition: transform 0.3s, box-shadow 0.3s;
    cursor: pointer;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
}

.feature-icon {
    width: 60px;
    height: 60px;
    background-color: var(--color-primary-light);
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: var(--spacing-lg);
}

.feature-icon .icon {
    width: 30px;
    height: 30px;
    color: var(--color-primary-dark);
}

.feature-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-md);
}

.feature-desc {
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-lg);
    line-height: 1.6;
}

.feature-link {
    color: var(--color-primary);
    font-weight: 600;
    display: flex;
    align-items: center;
}

.feature-link:after {
    content: "→";
    margin-left: var(--spacing-sm);
    transition: transform 0.2s;
}

.feature-card:hover .feature-link:after {
    transform: translateX(4px);
}

.stats-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-lg);
}

.stat-card {
    background-color: var(--color-surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    padding: var(--spacing-lg);
    text-align: center;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-primary);
    margin-bottom: var(--spacing-xs);
}

.stat-label {
    color: var(--color-text-secondary);
    font-size: 0.875rem;
}

@media (max-width: 768px) {
    .home-view {
        padding: var(--spacing-lg);
    }

    .hero-title {
        font-size: 1.75rem;
    }

    .hero-subtitle {
        font-size: 1rem;
    }

    .features-grid {
        gap: var(--spacing-lg);
    }

    .stat-value {
        font-size: 1.5rem;
    }
}
</style>
