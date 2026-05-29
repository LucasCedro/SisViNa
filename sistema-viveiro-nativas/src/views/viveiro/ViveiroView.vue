<template>
  <PageLayout full-height>
    <header class="viveiro-page-header">
      <div>
        <h1 class="page-title">Viveiro</h1>
        <p class="page-desc">
          Planta baixa integrada à produção — clique em uma área para ver ocupação e mudas.
        </p>
      </div>
      <button type="button" class="btn btn-primary" @click="editarPlantaBaixa">
        Editar layout
      </button>
    </header>

    <p v-if="store.carregando" class="status-msg">Carregando viveiro…</p>
    <p v-else-if="store.erro" class="alert alert-error">{{ store.erro }}</p>

    <template v-else>
      <ViveiroResumoKpis />

      <nav class="guias-navegacao" aria-label="Seções do viveiro">
        <button type="button" class="guia" :class="{ ativa: guiaAtiva === 'gestao' }" @click="guiaAtiva = 'gestao'">
          Mapa e gestão
        </button>
        <button type="button" class="guia" :class="{ ativa: guiaAtiva === 'cadastro' }" @click="guiaAtiva = 'cadastro'">
          Cadastro de mudas
        </button>
      </nav>

      <div v-if="guiaAtiva === 'gestao'" class="gestao-grid">
        <section class="mapa-panel" aria-label="Planta baixa">
          <div v-if="!store.layout.elementos.length" class="empty-state">
            <div class="empty-icon" aria-hidden="true">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="7" height="7" rx="1" />
                <rect x="14" y="3" width="7" height="7" rx="1" />
                <rect x="3" y="14" width="7" height="7" rx="1" />
                <rect x="14" y="14" width="7" height="7" rx="1" />
              </svg>
            </div>
            <h2 class="empty-title">Nenhuma área desenhada ainda</h2>
            <p class="empty-text">
              Monte sementeiras, canteiros e rustificação no editor. Ao salvar, os locais ficam disponíveis na produção.
            </p>
            <button type="button" class="btn btn-primary" @click="editarPlantaBaixa">
              Começar planta baixa
            </button>
          </div>
          <PlantaBaixa v-else />
        </section>

        <aside class="sidebar-panel" aria-label="Detalhes e alertas">
          <div class="sidebar-card sidebar-card--detalhes">
            <PainelDetalhes />
            <ViveiroAlertasLista />
          </div>
          <nav v-if="store.layout.elementos.length" class="sidebar-card areas-rapidas" aria-label="Ir para área">
            <h3 class="areas-rapidas-titulo">Atalhos</h3>
            <div class="areas-rapidas-lista">
              <button
                v-for="el in store.layout.elementos"
                :key="el.id"
                type="button"
                class="area-chip"
                :class="{ ativo: store.elementoSelecionado?.id === el.id }"
                @click="store.selecionarElemento(el.id)"
              >
                <span class="area-chip-cor" :style="{ background: el.cor }" />
                <span class="area-chip-texto">
                  <span class="area-chip-nome">{{ el.nome }}</span>
                  <span v-if="el.badgeOcupacao != null && el.apiId" class="area-chip-badge">{{ el.badgeOcupacao }}</span>
                </span>
              </button>
            </div>
          </nav>
        </aside>
      </div>

      <section v-else class="cadastro-panel">
        <CadastroMudas />
      </section>
    </template>
  </PageLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageLayout from '@/components/layout/PageLayout.vue'
import PlantaBaixa from '@/components/viveiro/PlantaBaixa.vue'
import PainelDetalhes from '@/components/viveiro/PainelDetalhes.vue'
import CadastroMudas from '@/components/viveiro/CadastroMudas.vue'
import ViveiroResumoKpis from '@/components/viveiro/ViveiroResumoKpis.vue'
import ViveiroAlertasLista from '@/components/viveiro/ViveiroAlertasLista.vue'
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
.viveiro-page-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding: 0 var(--spacing-lg);
  padding-top: var(--spacing-md);
}

.page-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.page-desc {
  margin: 0.35rem 0 0;
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  max-width: 42rem;
}

.status-msg {
  padding: 0 var(--spacing-lg);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.alert-error {
  margin: 0 var(--spacing-lg) var(--spacing-md);
}

.guias-navegacao {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--color-border);
  margin: 0 var(--spacing-lg) var(--spacing-lg);
}

.guia {
  padding: var(--spacing-md) var(--spacing-lg);
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-family: inherit;
  margin-bottom: -1px;
}

.guia:hover {
  color: var(--color-primary);
}

.guia.ativa {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 600;
}

.gestao-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 360px);
  gap: var(--spacing-lg);
  padding: 0 var(--spacing-lg) var(--spacing-xl);
  align-items: stretch;
  min-height: 520px;
}

.mapa-panel {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  min-height: 480px;
  min-width: 0;
}

.sidebar-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  min-width: 0;
  max-height: calc(100vh - 220px);
  position: sticky;
  top: var(--spacing-md);
}

.sidebar-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  min-width: 0;
  overflow: hidden;
}

.sidebar-card--detalhes {
  flex: 1;
  min-height: 200px;
  max-height: min(52vh, 520px);
  overflow-x: hidden;
  overflow-y: auto;
  padding: var(--spacing-lg);
  -webkit-overflow-scrolling: touch;
}

.areas-rapidas {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: var(--spacing-md);
  max-height: min(240px, 32vh);
}

.areas-rapidas-lista {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin: 0 -0.15rem;
  padding: 0 0.15rem;
}

.areas-rapidas-titulo {
  margin: 0 0 var(--spacing-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
}

.area-chip {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 0.45rem 0.55rem;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  background: var(--color-surface-muted, #f5f5f4);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.8125rem;
  text-align: left;
}

.area-chip:hover {
  border-color: var(--color-border);
}

.area-chip.ativo {
  border-color: var(--color-primary);
  background: rgba(74, 124, 42, 0.08);
}

.area-chip-cor {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
}

.area-chip-texto {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem 0.4rem;
}

.area-chip-nome {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
  line-height: 1.3;
}

.area-chip-badge {
  flex-shrink: 0;
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: #fff;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-subtle);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 2rem;
  min-height: 420px;
}

.empty-icon {
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-md);
  opacity: 0.7;
}

.empty-title {
  margin: 0 0 var(--spacing-sm);
  font-size: 1.125rem;
  font-weight: 600;
}

.empty-text {
  margin: 0 0 var(--spacing-lg);
  max-width: 360px;
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.cadastro-panel {
  padding: 0 var(--spacing-lg) var(--spacing-xl);
}

@media (max-width: 1100px) {
  .gestao-grid {
    grid-template-columns: 1fr;
  }

  .sidebar-panel {
    position: static;
    max-height: none;
  }
}

@media (max-width: 768px) {
  .viveiro-page-header,
  .guias-navegacao,
  .gestao-grid,
  .cadastro-panel {
    padding-left: var(--spacing-md);
    padding-right: var(--spacing-md);
  }

  .guias-navegacao {
    overflow-x: auto;
  }

  .guia {
    white-space: nowrap;
  }
}
</style>
