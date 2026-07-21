<template>
    <PageLayout>
        <div class="coleta-page">
            <section class="coleta-panel coleta-toolbar">
                <div class="toolbar-info">
                    <p class="coleta-desc">
                        Matrizes, coletas de sementes, lotes, qualidade e teste de germinação.
                    </p>
                    <p v-if="store.carregando" class="status-carregando">Carregando dados...</p>
                    <p v-else class="status-resumo">
                        <span>{{ store.arvoresMatriz.length }} matrizes</span>
                        <span class="sep">·</span>
                        <span>{{ store.coletas.length }} coletas</span>
                        <span class="sep">·</span>
                        <span>{{ store.lotes.length }} lotes</span>
                    </p>
                </div>
                <div class="toolbar-acoes">
                    <ExportacaoColeta />
                    <CanAccess permission="coleta.create">
                      <button type="button" class="btn btn-outline" @click="abrirCadastroColeta()">
                          <span class="btn-icon">+</span>
                          Cadastrar coleta
                      </button>
                    </CanAccess>
                    <CanAccess permission="coleta.create">
                      <button type="button" class="btn btn-primary" @click="abrirCadastro">
                          <span class="btn-icon">+</span>
                          Cadastrar matriz
                      </button>
                    </CanAccess>
                </div>
            </section>

            <p v-if="store.erro" class="coleta-alerta coleta-alerta-erro" role="alert">
                {{ store.erro }}
            </p>

            <ColetaFiltros />

            <div class="coleta-body">
                <section class="coleta-secao" aria-label="Mapa de matrizes">
                    <MapaColeta
                        @editar="abrirEdicao"
                        @coletar="abrirCadastroColeta"
                        @editar-coleta="abrirEditarColeta"
                        @teste="abrirTeste"
                        @semeadura="abrirSemeadura"
                    />
                </section>

                <section class="coleta-secao" aria-label="Painéis operacionais">
                    <GraficosColeta
                        @coletar="abrirCadastroColeta"
                        @editar="abrirEdicao"
                        @registrar-teste="abrirTeste"
                        @ir-aba="(aba) => (abaTabelaAtiva = aba)"
                        @focar-matriz="focarMatrizNoMapa"
                    />
                </section>

                <section class="coleta-secao" aria-label="Listagens">
                    <div class="abas-listagem" role="tablist" aria-label="Listagens de coleta">
                        <button
                            type="button"
                            role="tab"
                            class="aba-listagem"
                            :class="{ ativa: abaTabelaAtiva === 'matrizes' }"
                            :aria-selected="abaTabelaAtiva === 'matrizes'"
                            @click="abaTabelaAtiva = 'matrizes'"
                        >
                            Matrizes
                        </button>
                        <button
                            type="button"
                            role="tab"
                            class="aba-listagem"
                            :class="{ ativa: abaTabelaAtiva === 'coletas' }"
                            :aria-selected="abaTabelaAtiva === 'coletas'"
                            @click="abaTabelaAtiva = 'coletas'"
                        >
                            Coletas
                        </button>
                        <button
                            type="button"
                            role="tab"
                            class="aba-listagem"
                            :class="{ ativa: abaTabelaAtiva === 'lotes' }"
                            :aria-selected="abaTabelaAtiva === 'lotes'"
                            @click="abaTabelaAtiva = 'lotes'"
                        >
                            Teste de germinação
                            <span v-if="lotesSemGerminacao > 0" class="aba-badge">{{ lotesSemGerminacao }}</span>
                        </button>
                    </div>

                    <TabelaColeta
                        v-show="abaTabelaAtiva === 'matrizes'"
                        @editar="abrirEdicao"
                        @coletar="abrirCadastroColeta"
                    />
                    <TabelaHistoricoColetas
                        v-show="abaTabelaAtiva === 'coletas'"
                        @editar-coleta="abrirEditarColeta"
                        @registrar-teste="abrirTeste"
                    />
                    <TabelaLotesColeta
                        v-show="abaTabelaAtiva === 'lotes'"
                        @registrar-teste="abrirTeste"
                    />
                </section>
            </div>
        </div>

        <RelatorioColetaPdf />

        <FormCadastroMatriz
            :aberto="modalMatrizAberto"
            :matriz="matrizEmEdicao"
            @fechar="fecharModalMatriz"
            @salvo="aoSalvarMatriz"
        />

        <FormCadastroColeta
            :aberto="modalColetaAberto"
            :matriz="matrizParaColeta"
            @fechar="fecharModalColeta"
            @salvo="aoSalvarColeta"
            @registrar-teste="aoRegistrarTesteAposColeta"
        />

        <FormEditarColeta
            :aberto="modalEditarColetaAberto"
            :coleta="coletaEmEdicao"
            @fechar="fecharEditarColeta"
            @salvo="aoSalvarColeta"
        />

        <FormTesteSemente
            :aberto="modalTesteAberto"
            :lote="loteParaTeste"
            @fechar="fecharTeste"
            @salvo="aoSalvarTeste"
        />

        <FormSemeadura
            :aberto="modalSemeaduraAberto"
            :lote="loteParaSemeadura"
            @fechar="fecharSemeadura"
            @salvo="aoSalvarSemeadura"
        />
    </PageLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import PageLayout from '@/components/layout/PageLayout.vue'
import MapaColeta from '@/components/coleta/MapaColeta.vue'
import GraficosColeta from '@/components/coleta/GraficosColeta.vue'
import TabelaColeta from '@/components/coleta/TabelaColeta.vue'
import TabelaHistoricoColetas from '@/components/coleta/TabelaHistoricoColetas.vue'
import TabelaLotesColeta from '@/components/coleta/TabelaLotesColeta.vue'
import FormCadastroMatriz from '@/components/coleta/FormCadastroMatriz.vue'
import FormCadastroColeta from '@/components/coleta/FormCadastroColeta.vue'
import FormEditarColeta from '@/components/coleta/FormEditarColeta.vue'
import FormTesteSemente from '@/components/coleta/FormTesteSemente.vue'
import FormSemeadura from '@/components/coleta/FormSemeadura.vue'
import ExportacaoColeta from '@/components/coleta/ExportacaoColeta.vue'
import RelatorioColetaPdf from '@/components/coleta/RelatorioColetaPdf.vue'
import ColetaFiltros from '@/components/coleta/ColetaFiltros.vue'
import CanAccess from '@/components/shared/CanAccess.vue'
import { useColetaStore } from '@/store/coleta'
import { usePermissions } from '@/composables/usePermissions'
import { usePageTab } from '@/composables/usePageTab'

import { lotePrecisaTesteGerminacao } from '@/utils/coletaKpi'

const store = useColetaStore()
const { can, canAny } = usePermissions()

const ABAS_COLETA = ['matrizes', 'coletas', 'lotes']

function coletaTabFromQuery(route) {
  const q = String(route.query.aba || '')
  if (q === 'germinacao' || q === 'teste-germinacao' || q === 'lotes') return 'lotes'
  if (ABAS_COLETA.includes(q)) return q
  return null
}

const abaTabelaAtiva = usePageTab('coleta', 'matrizes', {
  valid: ABAS_COLETA,
  queryResolver: coletaTabFromQuery,
})
const matrizEmEdicao = ref(null)
const modalMatrizAberto = ref(false)
const modalColetaAberto = ref(false)
const modalEditarColetaAberto = ref(false)
const modalTesteAberto = ref(false)
const modalSemeaduraAberto = ref(false)
const matrizParaColeta = ref(null)
const coletaEmEdicao = ref(null)
const loteParaTeste = ref(null)
const loteParaSemeadura = ref(null)

const lotesSemGerminacao = computed(() =>
  store.lotesFiltrados.filter((l) => lotePrecisaTesteGerminacao(l, store.testes)).length
)

onMounted(() => {
  store.carregar()
})

function abrirCadastro() {
    if (!can('coleta.create')) return
    matrizEmEdicao.value = null
    modalMatrizAberto.value = true
    abaTabelaAtiva.value = 'matrizes'
}

function abrirEdicao(matriz) {
    if (!can('coleta.edit')) return
    matrizEmEdicao.value = matriz
    modalMatrizAberto.value = true
}

function abrirCadastroColeta(matriz = null) {
    if (!can('coleta.create')) return
    matrizParaColeta.value = matriz
    modalColetaAberto.value = true
}

function abrirEditarColeta(coleta) {
    if (!can('coleta.edit')) return
    coletaEmEdicao.value = coleta
    modalEditarColetaAberto.value = true
    abaTabelaAtiva.value = 'coletas'
}

function abrirTeste(lote) {
    if (!can('coleta.create')) return
    loteParaTeste.value = lote
    modalTesteAberto.value = true
    abaTabelaAtiva.value = 'lotes'
}

function focarMatrizNoMapa(matriz) {
    if (matriz) store.selecionar(matriz)
    document
        .querySelector('[aria-label="Mapa de matrizes"]')
        ?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function abrirSemeadura(lote) {
    if (!canAny('producao.create', 'producao.transfer')) return
    loteParaSemeadura.value = lote
    modalSemeaduraAberto.value = true
}

function fecharModalMatriz() {
    modalMatrizAberto.value = false
    matrizEmEdicao.value = null
}

function fecharModalColeta() {
    modalColetaAberto.value = false
    matrizParaColeta.value = null
}

function fecharEditarColeta() {
    modalEditarColetaAberto.value = false
    coletaEmEdicao.value = null
}

function fecharTeste() {
    modalTesteAberto.value = false
    loteParaTeste.value = null
}

function fecharSemeadura() {
    modalSemeaduraAberto.value = false
    loteParaSemeadura.value = null
}

function aoSalvarMatriz() {
    fecharModalMatriz()
}

function aoSalvarColeta() {
    fecharModalColeta()
    fecharEditarColeta()
}

function aoRegistrarTesteAposColeta(lote) {
    fecharModalColeta()
    abaTabelaAtiva.value = 'lotes'
    abrirTeste(lote)
}

function aoSalvarTeste() {
    fecharTeste()
    store.carregar()
}

function aoSalvarSemeadura() {
    fecharSemeadura()
}
</script>

<style scoped>
.coleta-page {
    max-width: 1600px;
    margin: 0 auto;
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.coleta-panel {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
}

.coleta-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-lg);
    padding: 1.125rem 1.375rem;
    flex-wrap: wrap;
}

.toolbar-info {
    flex: 1;
    min-width: 220px;
}

.coleta-desc {
    margin: 0 0 0.35rem;
    font-size: 0.9375rem;
    color: var(--color-text-primary);
    line-height: 1.45;
}

.status-resumo,
.status-carregando {
    margin: 0;
    font-size: 0.8125rem;
    color: var(--color-text-secondary);
}

.status-resumo .sep {
    margin: 0 0.35rem;
    opacity: 0.5;
}

.toolbar-acoes {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.625rem;
    flex-shrink: 0;
}

.btn-icon {
    font-size: 1.05rem;
    line-height: 1;
    font-weight: 700;
}

.coleta-alerta {
    margin: 0;
    padding: 0.75rem 1rem;
    border-radius: var(--radius-lg);
    font-size: 0.875rem;
}

.coleta-alerta-erro {
    background: var(--color-error-bg);
    color: var(--color-error);
    border: 1px solid var(--color-primary-100);
}

.coleta-body {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
}

.coleta-secao {
    width: 100%;
}

.abas-listagem {
    display: inline-flex;
    gap: 0.35rem;
    margin-bottom: var(--spacing-md);
    padding: 0.25rem;
    background: var(--color-surface-muted);
    border-radius: var(--radius-md);
}

.aba-listagem {
    border: none;
    background: transparent;
    color: var(--color-text-secondary);
    padding: 0.45rem 0.85rem;
    border-radius: var(--radius);
    font-size: 0.8125rem;
    font-weight: 600;
    cursor: pointer;
}

.aba-listagem.ativa {
    background: var(--color-primary);
    color: var(--color-text-inverse);
}

.aba-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 1.125rem;
    height: 1.125rem;
    margin-left: 0.35rem;
    padding: 0 0.3rem;
    border-radius: 999px;
    font-size: 0.6875rem;
    font-weight: 700;
    background: var(--color-attention);
    color: var(--color-text-primary);
}

.aba-listagem.ativa .aba-badge {
    background: rgba(255, 255, 255, 0.9);
    color: var(--color-primary-700);
}

@media (max-width: 768px) {
    .coleta-toolbar {
        flex-direction: column;
        align-items: stretch;
    }

    .toolbar-acoes {
        flex-direction: column;
        align-items: stretch;
    }
}
</style>
