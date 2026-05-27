<template>
  <PageLayout full-height>
    <p v-if="store.carregando" class="status-msg">Carregando viveiro...</p>
    <p v-else-if="store.erro" class="alert alert-error">{{ store.erro }}</p>

    <PageSection tabs flush-body>
      <div class="guias-container">
        <div class="guias-navegacao">
          <button class="guia" :class="{ ativa: guiaAtiva === 'gestao' }" @click="guiaAtiva = 'gestao'">
            Gestão
          </button>
          <button class="guia" :class="{ ativa: guiaAtiva === 'cadastro' }" @click="guiaAtiva = 'cadastro'">
            Cadastro de Mudas
          </button>
        </div>

        <div class="guia-conteudo">
          <div v-if="guiaAtiva === 'gestao'" class="gestao-stack">
            <article class="block-card">
              <header class="block-card__header">
                <h2 class="block-card__title">
                  <span class="block-card__icon" aria-hidden="true">📍</span>
                  Planta baixa do viveiro
                </h2>
                <button type="button" class="btn btn-primary btn-sm" @click="editarPlantaBaixa">
                  Editar planta baixa
                </button>
              </header>
              <div class="block-card__body block-card__body--map">
                <p v-if="!store.carregando && !store.layout.elementos.length" class="empty-hint">
                  Cadastre canteiros e plantas para visualizar o layout.
                </p>
                <PlantaBaixa v-else />
              </div>
            </article>

            <div class="layout-colunas">
              <article class="block-card">
                <header class="block-card__header">
                  <h2 class="block-card__title">Detalhes</h2>
                </header>
                <div class="block-card__body">
                  <PainelDetalhes />
                </div>
              </article>

              <article class="block-card">
                <header class="block-card__header">
                  <h2 class="block-card__title">Dashboard</h2>
                </header>
                <div class="block-card__body">
                  <DashboardViveiro />
                </div>
              </article>
            </div>
          </div>

          <div v-else class="block-card__body">
            <CadastroMudas />
          </div>
        </div>
      </div>
    </PageSection>
  </PageLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageLayout from '@/components/layout/PageLayout.vue'
import PageSection from '@/components/layout/PageSection.vue'
import PlantaBaixa from '@/components/viveiro/PlantaBaixa.vue'
import PainelDetalhes from '@/components/viveiro/PainelDetalhes.vue'
import DashboardViveiro from '@/components/viveiro/DashboardViveiro.vue'
import CadastroMudas from '@/components/viveiro/CadastroMudas.vue'
import { useViveiroStore } from '@/store/viveiro'

const store = useViveiroStore()
const router = useRouter()
const guiaAtiva = ref('gestao')

function editarPlantaBaixa() {
  router.push('/viveiro/planta-editor')
}

onMounted(() => store.carregar())
</script>

<style scoped>
.status-msg {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.guias-container {
  width: 100%;
}

.guias-navegacao {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--spacing-lg);
  padding: 0 var(--spacing-lg);
  padding-top: var(--spacing-md);
}

.guia {
  padding: var(--spacing-md) var(--spacing-lg);
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-family: inherit;
}

.guia:hover {
  color: var(--color-primary);
}

.guia.ativa {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 600;
}

.guia-conteudo {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
}

.gestao-stack {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.block-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.block-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-subtle);
}

.block-card__title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.block-card__body {
  padding: var(--spacing-lg);
  min-height: 280px;
}

.block-card__body--map {
  min-height: 520px;
}

.layout-colunas {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
}

.empty-hint {
  text-align: center;
  color: var(--color-text-muted);
  padding: 2rem;
}

.btn-sm {
  padding: 0.4rem 0.85rem;
  font-size: 0.8125rem;
}

@media (max-width: 1200px) {
  .layout-colunas {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .guias-navegacao {
    flex-direction: column;
    padding-left: var(--spacing-md);
    padding-right: var(--spacing-md);
  }

  .guia {
    width: 100%;
    text-align: left;
    border-left: 3px solid transparent;
    border-bottom: none;
  }

  .guia.ativa {
    border-left-color: var(--color-primary);
  }
}
</style>
