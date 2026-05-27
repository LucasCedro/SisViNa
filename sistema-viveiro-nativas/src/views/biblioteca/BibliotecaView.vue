<template>
    <PageLayout>
            <div class="pesquisa-section">
                <div class="card search-card">
                    <div class="search-container">
                        <input
                            v-model="termoBusca"
                            type="text"
                            class="search-input"
                            placeholder="Buscar por nome científico ou popular..."
                        />
                        <p v-if="carregando" class="status-msg">Carregando espécies da API...</p>
                        <p v-else-if="erro" class="status-msg erro">{{ erro }}</p>
                    </div>
                </div>
            </div>

            <div v-if="especiesFiltradas.length" class="especies-grid">
                <div
                    v-for="especie in especiesFiltradas"
                    :key="especie.id"
                    class="card especie-card"
                >
                    <div class="especie-img placeholder-img" />
                    <div class="especie-content">
                        <h3 class="especie-nome">{{ especie.nome_popular || 'Sem nome popular' }}</h3>
                        <p class="especie-nome-cientifico">{{ especie.nome_cientifico }}</p>
                        <div v-if="especie.familia" class="especie-tags">
                            <span class="especie-tag tipo">{{ especie.familia }}</span>
                        </div>
                        <p class="especie-descricao">
                            {{ especie.descricao || 'Sem descrição cadastrada.' }}
                        </p>
                        <p v-if="especie.tempo_germinacao" class="meta">
                            Germinação: ~{{ especie.tempo_germinacao }} dias
                        </p>
                    </div>
                </div>
            </div>

            <div v-else-if="!carregando && !erro" class="vazio">
                Nenhuma espécie encontrada.
            </div>
    </PageLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PageLayout from '@/components/layout/PageLayout.vue'
import { listEspecies } from '../../services/especies'

const especies = ref([])
const termoBusca = ref('')
const carregando = ref(true)
const erro = ref(null)

const especiesFiltradas = computed(() => {
    const q = termoBusca.value.trim().toLowerCase()
    if (!q) return especies.value
    return especies.value.filter((e) => {
        const c = (e.nome_cientifico || '').toLowerCase()
        const p = (e.nome_popular || '').toLowerCase()
        const f = (e.familia || '').toLowerCase()
        return c.includes(q) || p.includes(q) || f.includes(q)
    })
})

onMounted(async () => {
    try {
        especies.value = await listEspecies()
    } catch (e) {
        erro.value = 'Não foi possível carregar espécies. Verifique se a API está no ar.'
        console.error(e)
    } finally {
        carregando.value = false
    }
})
</script>

<style scoped>
.search-card {
    padding: var(--spacing-lg);
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
}

.search-input {
    width: 100%;
    padding: var(--spacing-md);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    font-size: 1rem;
}

.status-msg {
    margin-top: 0.75rem;
    font-size: 0.875rem;
    color: var(--color-text-secondary);
}

.status-msg.erro {
    color: var(--color-error);
}

.especies-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--spacing-lg);
}

.especie-card {
    overflow: hidden;
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
}

.placeholder-img {
    height: 120px;
    background: linear-gradient(135deg, var(--color-info-bg), var(--color-success-bg));
}

.especie-content {
    padding: var(--spacing-lg);
}

.especie-nome {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.especie-nome-cientifico {
    font-style: italic;
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    margin-bottom: 0.75rem;
}

.especie-tag {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: var(--radius-full);
    background: rgba(76, 175, 80, 0.1);
    color: var(--color-primary);
}

.especie-descricao {
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    line-height: 1.5;
    margin-top: 0.75rem;
}

.meta {
    font-size: 0.8rem;
    color: var(--color-text-secondary);
    margin-top: 0.5rem;
}

.vazio {
    text-align: center;
    color: var(--color-text-secondary);
    padding: 2rem;
}
</style>
