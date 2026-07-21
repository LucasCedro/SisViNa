<template>
  <PageLayout full-height class="viveiro-page-root">
    <div class="viveiro-page">
      <header class="viveiro-hero">
        <div class="viveiro-hero__texto">
          <p class="viveiro-hero__eyebrow">Operação</p>
          <h1 class="viveiro-hero__titulo">Planta do viveiro</h1>
          <p class="viveiro-hero__desc">
            Mapa em escala real, ocupação ao vivo e pendências por local.
          </p>
        </div>
        <button v-if="podeEditarLayout" type="button" class="btn btn-primary viveiro-hero__cta" @click="editarPlantaBaixa">
          Editar / Montar layout
        </button>
      </header>

      <p v-if="store.carregando" class="viveiro-status">Carregando viveiro…</p>
      <p v-else-if="store.erro" class="alert alert-error viveiro-erro">{{ store.erro }}</p>

      <template v-else>
        <div class="viveiro-chrome">
          <ViveiroResumoKpis class="viveiro-kpis-wrap" />

          <nav class="viveiro-tabs" aria-label="Seções do viveiro">
            <button type="button" class="viveiro-tab" :class="{ 'viveiro-tab--on': guiaAtiva === 'gestao' }" @click="guiaAtiva = 'gestao'">
              Mapa
            </button>
            <button type="button" class="viveiro-tab" :class="{ 'viveiro-tab--on': guiaAtiva === 'cadastro' }" @click="guiaAtiva = 'cadastro'">
              Cadastro
            </button>
            <button type="button" class="viveiro-tab" :class="{ 'viveiro-tab--on': guiaAtiva === 'locais' }" @click="guiaAtiva = 'locais'">
              Locais
            </button>
          </nav>
        </div>

        <div v-if="guiaAtiva === 'gestao'" class="viveiro-workspace">
          <section class="viveiro-mapa" aria-label="Planta baixa">
            <div v-if="!store.layout.elementos.length" class="viveiro-empty">
              <div class="viveiro-empty__icon" aria-hidden="true">
                <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25">
                  <rect x="3" y="3" width="7" height="7" rx="1" />
                  <rect x="14" y="3" width="7" height="7" rx="1" />
                  <rect x="3" y="14" width="7" height="7" rx="1" />
                  <rect x="14" y="14" width="7" height="7" rx="1" />
                </svg>
              </div>
              <h2 class="viveiro-empty__titulo">Monte a planta do viveiro</h2>
              <p class="viveiro-empty__texto">
                Desenhe sementeiras, canteiros e rustificação. Ao salvar, os locais entram na produção.
              </p>
              <button v-if="podeEditarLayout" type="button" class="btn btn-primary" @click="editarPlantaBaixa">
                Abrir editor
              </button>
            </div>
            <PlantaBaixa v-else />
          </section>

          <aside class="viveiro-sidebar" aria-label="Detalhes e atalhos">
            <div class="viveiro-sidebar__scroll">
              <PainelDetalhes />
              <ViveiroAlertasLista />
            </div>

            <div v-if="store.layout.elementos.length" class="viveiro-atalhos">
              <div class="viveiro-atalhos__head">
                <h3 class="viveiro-atalhos__titulo">Locais</h3>
                <span class="viveiro-atalhos__qtd">{{ store.layout.elementos.length }}</span>
              </div>
              <div class="viveiro-atalhos__lista">
                <button
                  v-for="el in store.layout.elementos"
                  :key="el.id"
                  type="button"
                  class="viveiro-atalho"
                  :class="{ 'viveiro-atalho--on': store.elementoSelecionado?.id === el.id }"
                  @click="store.selecionarElemento(el.id)"
                >
                  <span class="viveiro-atalho__swatch" :style="{ background: el.cor }" />
                  <span class="viveiro-atalho__corpo">
                    <span class="viveiro-atalho__nome">{{ el.nome }}</span>
                    <span class="viveiro-atalho__meta">
                      <span v-if="pendenciasChip(el).length" class="viveiro-atalho__pend" :title="tituloPendenciasChip(el)">
                        {{ pendenciasChip(el).map((p) => p.icone).join('') }}
                      </span>
                      <span v-if="el.badgeOcupacao != null && el.apiId">{{ el.badgeOcupacao }}</span>
                    </span>
                  </span>
                </button>
              </div>
            </div>
          </aside>
        </div>

        <section v-else-if="guiaAtiva === 'cadastro'" class="viveiro-tab-panel">
          <CadastroMudas />
        </section>

        <ViveiroLocaisPanel v-else-if="guiaAtiva === 'locais'" class="viveiro-tab-panel" />
      </template>
    </div>
  </PageLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePermissions } from '@/composables/usePermissions'
import { usePageTab } from '@/composables/usePageTab'
import PageLayout from '@/components/layout/PageLayout.vue'
import PlantaBaixa from '@/components/viveiro/PlantaBaixa.vue'
import PainelDetalhes from '@/components/viveiro/PainelDetalhes.vue'
import CadastroMudas from '@/components/viveiro/CadastroMudas.vue'
import ViveiroResumoKpis from '@/components/viveiro/ViveiroResumoKpis.vue'
import ViveiroAlertasLista from '@/components/viveiro/ViveiroAlertasLista.vue'
import ViveiroLocaisPanel from '@/components/viveiro/ViveiroLocaisPanel.vue'
import { useViveiroStore } from '@/store/viveiro'
import { pendenciasDoCanteiro } from '@/utils/viveiroPendenciasMapa'

const store = useViveiroStore()
const router = useRouter()
const { can } = usePermissions()
const podeEditarLayout = computed(() => can('viveiro.edit'))
const guiaAtiva = usePageTab('viveiro', 'gestao', { valid: ['gestao', 'cadastro', 'locais'] })

function pendenciasChip(el) {
  return pendenciasDoCanteiro(store.pendenciasPorCanteiro, el.apiId)
}

function tituloPendenciasChip(el) {
  return pendenciasChip(el)
    .map((p) => `${p.rotulo}: ${p.count}`)
    .join(' · ')
}

function editarPlantaBaixa() {
  if (!podeEditarLayout.value) return
  router.push('/viveiro/planta-editor')
}

onMounted(() => store.carregar())
</script>

<style scoped>
.viveiro-page-root.page-layout,
.viveiro-page-root.page-layout--full {
  padding: 0;
  gap: 0;
  height: 100%;
  min-height: 0;
  overflow: visible;
}

.viveiro-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.viveiro-hero {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.75rem;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-subtle);
  flex-shrink: 0;
}

.viveiro-hero__eyebrow {
  margin: 0 0 0.125rem;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.viveiro-hero__titulo {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
}

.viveiro-hero__desc {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
  max-width: 36rem;
}

.viveiro-hero__cta {
  flex-shrink: 0;
}

.viveiro-status,
.viveiro-erro {
  padding: 0.75rem 1.5rem;
  flex-shrink: 0;
}

.viveiro-chrome {
  flex-shrink: 0;
  padding: 1.25rem 1.75rem 0;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-subtle);
}

.viveiro-kpis-wrap {
  padding: 0 0 1.25rem;
  margin: 0;
}

.viveiro-kpis-wrap :deep(.viveiro-kpis) {
  margin-bottom: 0;
}

.viveiro-tabs {
  display: flex;
  gap: 0.375rem;
  padding: 0;
  margin: 0;
  border-bottom: none;
  background: transparent;
  flex-shrink: 0;
}

.viveiro-tab {
  padding: 0.75rem 1.125rem;
  margin-bottom: 0;
  border: none;
  border-bottom: 2px solid transparent;
  background: none;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-muted);
  cursor: pointer;
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.viveiro-tab--on {
  color: var(--color-primary);
  font-weight: 600;
  border-bottom-color: var(--color-primary);
  background: var(--color-background);
}

.viveiro-workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 420px);
  grid-template-rows: minmax(560px, auto);
  flex: 1 0 auto;
  min-height: calc(100vh - 280px);
  background: var(--color-background);
}

.viveiro-mapa {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 560px;
  overflow: hidden;
  border-right: 1px solid var(--color-border-subtle);
}

.viveiro-sidebar {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 560px;
  overflow: hidden;
  background: var(--color-surface);
}

.viveiro-sidebar__scroll {
  flex: 0 1 auto;
  max-height: 42%;
  min-height: 140px;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 1.5rem;
}

.viveiro-atalhos {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-height: 300px;
  border-top: 1px solid var(--color-border-subtle);
  background: var(--color-surface-muted);
}

.viveiro-atalhos__head {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 1rem 1.25rem 0.75rem;
  flex-shrink: 0;
}

.viveiro-atalhos__titulo {
  margin: 0;
  flex: 1;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.viveiro-atalhos__lista {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0 1rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.viveiro-atalho {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  transition: border-color 0.12s, box-shadow 0.12s;
}

.viveiro-atalho__swatch {
  width: 12px;
  height: 36px;
  border-radius: 4px;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.viveiro-atalho__nome {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.viveiro-atalho__meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.viveiro-tab:hover {
  color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.viveiro-atalhos__qtd {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-primary);
  background: var(--color-surface);
  padding: 0.2rem 0.625rem;
  border-radius: var(--radius-full);
}

.viveiro-atalho:hover {
  border-color: var(--color-border);
  box-shadow: var(--shadow-sm);
}

.viveiro-atalho--on {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.viveiro-atalho__corpo {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.viveiro-atalho__pend {
  padding: 0 0.375rem;
  border-radius: 3px;
  background: var(--color-attention-bg);
  color: var(--color-complement-dark);
}

.viveiro-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2.5rem 1.5rem;
  background: var(--color-surface-muted);
}

.viveiro-empty__icon {
  color: var(--color-text-muted);
  opacity: 0.65;
  margin-bottom: 1rem;
}

.viveiro-empty__titulo {
  margin: 0 0 0.5rem;
  font-size: 1.125rem;
  font-weight: 600;
}

.viveiro-empty__texto {
  margin: 0 0 1.25rem;
  max-width: 24rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.viveiro-tab-panel {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 1.25rem 1.5rem 1.5rem;
}

@media (max-width: 1024px) {
  .viveiro-mapa {
    border-right: none;
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .viveiro-workspace {
    grid-template-columns: 1fr;
    grid-template-rows: minmax(420px, auto) minmax(360px, auto);
    min-height: auto;
  }

  .viveiro-mapa,
  .viveiro-sidebar {
    min-height: 420px;
  }

  .viveiro-sidebar {
    min-height: 360px;
  }
}

@media (max-width: 640px) {
  .viveiro-hero,
  .viveiro-chrome {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .viveiro-mapa {
    border-right: none;
    border-bottom: 1px solid var(--color-border-subtle);
  }

  .viveiro-tabs {
    overflow-x: auto;
  }

  .viveiro-tab {
    white-space: nowrap;
  }
}
</style>
