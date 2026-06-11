<template>
  <div class="painels-coleta">
    <!-- 1. Janela de coleta -->
    <section class="coleta-panel painel" aria-labelledby="titulo-janela">
      <header class="painel-header">
        <div class="painel-header-texto">
          <h3 id="titulo-janela" class="painel-titulo">Janela de coleta</h3>
          <p class="painel-lead">
            Matrizes na época de frutificação em <strong>{{ mesAtualLabel }}</strong>
          </p>
        </div>
        <span v-if="janela.totalProntas > 0" class="painel-badge painel-badge--ok">
          {{ janela.totalProntas }} pronta{{ janela.totalProntas === 1 ? '' : 's' }}
        </span>
      </header>

      <div v-if="semMatrizes" class="painel-vazio">
        Nenhuma matriz no filtro atual.
      </div>
      <div v-else class="painel-corpo">
        <ul v-if="janela.naJanela.length" class="lista-acao">
          <li
            v-for="item in janela.naJanela"
            :key="item.matriz.id"
            class="lista-item"
            :class="`lista-item--${item.status}`"
          >
            <span class="lista-indicador" aria-hidden="true" />
            <div class="lista-conteudo">
              <div class="lista-topo">
                <strong>{{ item.matriz.nome }}</strong>
                <span class="tag" :class="tagJanela(item.status)">{{ labelStatusJanela(item.status) }}</span>
              </div>
              <p class="lista-meta">{{ item.especie }} · {{ item.local }}</p>
              <p class="lista-detalhe">
                {{ item.estagio }} · janela {{ item.janela }}
              </p>
            </div>
            <div class="lista-acoes">
              <button
                v-if="item.status === 'pronta'"
                type="button"
                class="btn-acao btn-acao--prim"
                @click="emit('coletar', item.matriz)"
              >
                Coletar
              </button>
              <button
                v-else
                type="button"
                class="btn-acao btn-acao--prim"
                @click="emit('editar', item.matriz)"
              >
                Atualizar
              </button>
              <button type="button" class="btn-link" @click="focarMatriz(item.matriz)">Mapa</button>
            </div>
          </li>
        </ul>

        <p v-else class="painel-sem-janela">
          Nenhuma matriz na janela de {{ mesAtualLabel }}.
          <template v-if="janela.foraJanela.length">
            Consulte as matrizes fora de época abaixo.
          </template>
        </p>

        <details v-if="janela.foraJanela.length" class="painel-detalhes">
          <summary>
            Fora da janela
            <span class="painel-detalhes-contagem">{{ janela.foraJanela.length }}</span>
          </summary>
          <ul class="lista-compacta">
            <li v-for="item in janela.foraJanela" :key="item.matriz.id">
              <button type="button" class="link-matriz" @click="focarMatriz(item.matriz)">
                <span>{{ item.matriz.nome }}</span>
                <span class="muted">{{ item.janela }}</span>
              </button>
            </li>
          </ul>
        </details>

        <details v-if="janela.semFenologia.length" class="painel-detalhes painel-detalhes--alerta">
          <summary>
            Sem fenologia cadastrada
            <span class="painel-detalhes-contagem">{{ janela.semFenologia.length }}</span>
          </summary>
          <ul class="lista-compacta">
            <li v-for="item in janela.semFenologia" :key="item.matriz.id">
              <button type="button" class="link-matriz" @click="emit('editar', item.matriz)">
                <span>{{ item.matriz.nome }}</span>
                <span class="muted">Cadastrar janela</span>
              </button>
            </li>
          </ul>
        </details>
      </div>
    </section>

    <!-- 2. Pendências -->
    <section class="coleta-panel painel" aria-labelledby="titulo-pendencias">
      <header class="painel-header">
        <div class="painel-header-texto">
          <h3 id="titulo-pendencias" class="painel-titulo">Pendências</h3>
          <p class="painel-lead">O que está bloqueando teste ou semeadura</p>
        </div>
        <span
          v-if="pendencias.itens.length"
          class="painel-badge painel-badge--alerta"
        >
          {{ pendencias.itens.length }}
        </span>
        <span v-else-if="!semMatrizes" class="painel-badge painel-badge--ok">Em dia</span>
      </header>

      <div v-if="semMatrizes" class="painel-vazio">
        Nenhuma matriz no filtro atual.
      </div>
      <div v-else-if="pendencias.itens.length === 0" class="painel-ok">
        <p class="painel-ok-titulo">Nenhuma pendência crítica</p>
        <p v-if="pendencias.liberados > 0" class="painel-ok-texto">
          {{ pendencias.liberados }} lote{{ pendencias.liberados === 1 ? '' : 's' }} com estoque
          liberado{{ pendencias.liberados === 1 ? '' : 's' }} para semeadura.
        </p>
        <button type="button" class="btn-link btn-link--block" @click="emit('ir-aba', 'lotes')">
          Ver testes de germinação
        </button>
      </div>
      <div v-else class="painel-corpo">
        <ul class="lista-acao">
          <li
            v-for="p in pendencias.itens"
            :key="p.id"
            class="lista-item"
            :class="`lista-item--${p.severidade}`"
          >
            <span class="lista-indicador" aria-hidden="true" />
            <div class="lista-conteudo">
              <div class="lista-topo">
                <strong>{{ p.titulo }}</strong>
              </div>
              <p class="lista-meta">{{ p.detalhe }}</p>
              <p class="lista-detalhe">{{ p.meta }}</p>
            </div>
            <div class="lista-acoes">
              <button
                type="button"
                class="btn-acao btn-acao--prim"
                @click="emit('registrar-teste', p.lote)"
              >
                {{ p.tipo === 'teste_pendente' ? 'Teste germ.' : 'Revisar' }}
              </button>
            </div>
          </li>
        </ul>
        <button type="button" class="btn-link btn-link--block" @click="emit('ir-aba', 'lotes')">
          Abrir aba Teste de germinação
        </button>
      </div>
    </section>

    <!-- 3. Ranking de qualidade -->
    <section class="coleta-panel painel" aria-labelledby="titulo-ranking">
      <header class="painel-header">
        <div class="painel-header-texto">
          <h3 id="titulo-ranking" class="painel-titulo">Qualidade por matriz</h3>
          <p class="painel-lead">Último teste de germinação — priorize matrizes com melhor desempenho</p>
        </div>
        <span v-if="ranking.length" class="painel-badge">{{ ranking.length }}</span>
      </header>

      <div v-if="semMatrizes" class="painel-vazio">
        Nenhuma matriz no filtro atual.
      </div>
      <div v-else-if="ranking.length === 0" class="painel-vazio">
        Registre testes na aba <button type="button" class="btn-inline" @click="emit('ir-aba', 'lotes')">Teste de germinação</button>
        para comparar matrizes.
      </div>
      <div v-else class="painel-corpo painel-corpo--ranking">
        <div
          v-for="item in ranking"
          :key="item.matriz.id"
          class="ranking-item"
        >
          <div class="ranking-cabecalho">
            <button type="button" class="ranking-nome" @click="focarMatriz(item.matriz)">
              {{ item.nome }}
            </button>
            <span class="ranking-valor" :class="`ranking-valor--${corGerminacao(item.taxa)}`">
              {{ item.taxa }}%
            </span>
          </div>
          <p class="ranking-especie">{{ item.especie }}</p>
          <div class="ranking-barra-track">
            <div
              class="ranking-barra"
              :class="`ranking-barra--${corGerminacao(item.taxa)}`"
              :style="{ width: `${Math.min(100, Math.max(0, item.taxa))}%` }"
            />
            <span
              v-if="item.mediaEspecie != null && ranking.length > 1"
              class="ranking-ref"
              :style="{ left: `${Math.min(100, item.mediaEspecie)}%` }"
              :title="`Média da espécie: ${item.mediaEspecie}%`"
            />
          </div>
          <p v-if="item.mediaEspecie != null" class="ranking-legenda">
            Média {{ item.especie }}: {{ item.mediaEspecie }}%
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useColetaStore } from '@/store/coleta'
import { MESES } from '@/constants/coletaDominio'
import {
  agruparMatrizesJanelaColeta,
  corGerminacao,
  listarPendenciasColeta,
  listarRankingGerminacao
} from '@/utils/coletaPainel'

const emit = defineEmits(['coletar', 'editar', 'registrar-teste', 'ir-aba', 'focar-matriz'])

const store = useColetaStore()

const mesAtual = computed(() => new Date().getMonth() + 1)
const mesAtualLabel = computed(() => MESES.find((m) => m.value === mesAtual.value)?.label || '')

const semMatrizes = computed(() => store.matrizesFiltradas.length === 0)

const janela = computed(() => agruparMatrizesJanelaColeta(store.matrizesFiltradas, mesAtual.value))

const pendencias = computed(() =>
  listarPendenciasColeta({
    lotes: store.lotesFiltrados,
    testes: store.testes
  })
)

const ranking = computed(() =>
  listarRankingGerminacao(store.matrizesFiltradas, store.lotesFiltrados, store.testes)
)

function labelStatusJanela(status) {
  const map = {
    pronta: 'Pronta p/ coleta',
    na_janela_aguardar: 'Aguardar maturação',
    na_janela_sem_estagio: 'Atualizar estágio'
  }
  return map[status] || status
}

function tagJanela(status) {
  if (status === 'pronta') return 'tag--ok'
  return 'tag--pendente'
}

function focarMatriz(matriz) {
  store.selecionar(matriz)
  emit('focar-matriz', matriz)
}
</script>

<style scoped>
.coleta-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.painels-coleta {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  align-items: stretch;
}

.painel {
  display: flex;
  flex-direction: column;
  min-height: 400px;
  max-height: 440px;
  padding: 1rem 1.125rem;
  overflow: hidden;
}

.painel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-shrink: 0;
}

.painel-header-texto {
  min-width: 0;
}

.painel-titulo {
  margin: 0 0 0.2rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.painel-lead {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.painel-lead strong {
  color: var(--color-text-primary);
  font-weight: 600;
}

.painel-badge {
  flex-shrink: 0;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: var(--color-surface-muted);
  color: var(--color-text-secondary);
}

.painel-badge--ok {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.painel-badge--alerta {
  background: var(--color-attention-bg);
  color: var(--color-analog-2);
}

.painel-corpo {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding-right: 0.15rem;
}

.painel-corpo--ranking {
  gap: 0.85rem;
}

.painel-vazio,
.painel-sem-janela {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
  padding: 1rem 0.5rem;
}

.painel-sem-janela {
  align-items: flex-start;
  justify-content: flex-start;
  padding-top: 0.25rem;
}

.painel-ok {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 1rem;
  gap: 0.35rem;
}

.painel-ok-titulo {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-success);
}

.painel-ok-texto {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  line-height: 1.45;
}

.lista-acao {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.lista-item {
  display: grid;
  grid-template-columns: 4px 1fr auto;
  gap: 0.65rem;
  align-items: start;
  padding: 0.65rem 0.7rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
}

.lista-indicador {
  width: 4px;
  align-self: stretch;
  border-radius: 4px;
  background: var(--color-primary);
}

.lista-item--pronta .lista-indicador {
  background: var(--color-success);
}

.lista-item--na_janela_aguardar .lista-indicador,
.lista-item--na_janela_sem_estagio .lista-indicador,
.lista-item--alerta .lista-indicador {
  background: var(--color-attention);
}

.lista-item--critico .lista-indicador {
  background: var(--color-error);
}

.lista-conteudo {
  min-width: 0;
}

.lista-topo {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.5rem;
  margin-bottom: 0.15rem;
}

.lista-topo strong {
  font-size: 0.8125rem;
  font-weight: 600;
}

.lista-meta {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  line-height: 1.35;
}

.lista-detalhe {
  margin: 0.15rem 0 0;
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  line-height: 1.35;
}

.lista-acoes {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  flex-shrink: 0;
}

.tag {
  display: inline-block;
  padding: 0.12rem 0.4rem;
  border-radius: var(--radius-sm);
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.tag--ok {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.tag--pendente {
  background: var(--color-attention-bg);
  color: var(--color-analog-2);
}

.btn-acao {
  border: none;
  padding: 0.35rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: 0.6875rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.btn-acao--prim {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-acao--prim:hover {
  background: var(--color-primary-dark);
}

.btn-link {
  border: none;
  background: none;
  padding: 0;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-primary);
  cursor: pointer;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-link--block {
  margin-top: auto;
  padding-top: 0.35rem;
  text-align: center;
  width: 100%;
}

.btn-inline {
  border: none;
  background: none;
  padding: 0;
  font: inherit;
  font-weight: 600;
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: underline;
}

.painel-detalhes {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  border-top: 1px solid var(--color-border);
  padding-top: 0.5rem;
}

.painel-detalhes summary {
  cursor: pointer;
  font-weight: 600;
  color: var(--color-text-secondary);
  list-style: none;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.painel-detalhes summary::-webkit-details-marker {
  display: none;
}

.painel-detalhes summary::before {
  content: '▸';
  font-size: 0.65rem;
  transition: transform 0.15s;
}

.painel-detalhes[open] summary::before {
  transform: rotate(90deg);
}

.painel-detalhes--alerta summary {
  color: var(--color-analog-2);
}

.painel-detalhes-contagem {
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0.05rem 0.35rem;
  border-radius: 999px;
  background: var(--color-surface-muted);
}

.lista-compacta {
  list-style: none;
  margin: 0.4rem 0 0;
  padding: 0;
}

.link-matriz {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  width: 100%;
  border: none;
  background: none;
  padding: 0.35rem 0;
  font-size: 0.75rem;
  text-align: left;
  cursor: pointer;
  color: var(--color-text-primary);
}

.link-matriz:hover span:first-child {
  color: var(--color-primary);
}

.muted {
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.ranking-item {
  padding-bottom: 0.15rem;
}

.ranking-cabecalho {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.1rem;
}

.ranking-nome {
  border: none;
  background: none;
  padding: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  cursor: pointer;
  text-align: left;
}

.ranking-nome:hover {
  color: var(--color-primary);
}

.ranking-especie {
  margin: 0 0 0.35rem;
  font-size: 0.6875rem;
  color: var(--color-text-muted);
}

.ranking-valor {
  font-size: 0.8125rem;
  font-weight: 700;
  flex-shrink: 0;
}

.ranking-valor--boa {
  color: var(--color-success);
}

.ranking-valor--media {
  color: var(--color-analog-2);
}

.ranking-valor--baixa {
  color: var(--color-error);
}

.ranking-barra-track {
  position: relative;
  height: 0.5rem;
  background: var(--color-surface-muted);
  border-radius: 999px;
  overflow: visible;
}

.ranking-barra {
  height: 100%;
  border-radius: 999px;
  min-width: 2px;
  transition: width 0.25s ease;
}

.ranking-barra--boa {
  background: var(--color-success);
}

.ranking-barra--media {
  background: var(--color-attention);
}

.ranking-barra--baixa {
  background: var(--color-error);
}

.ranking-ref {
  position: absolute;
  top: -2px;
  bottom: -2px;
  width: 2px;
  margin-left: -1px;
  background: var(--color-text-muted);
  opacity: 0.55;
  pointer-events: none;
}

.ranking-legenda {
  margin: 0.25rem 0 0;
  font-size: 0.625rem;
  color: var(--color-text-muted);
}

@media (max-width: 1200px) {
  .painels-coleta {
    grid-template-columns: repeat(2, 1fr);
  }

  .painels-coleta .painel:last-child {
    grid-column: 1 / -1;
    max-height: 360px;
  }
}

@media (max-width: 768px) {
  .painels-coleta {
    grid-template-columns: 1fr;
  }

  .painels-coleta .painel:last-child {
    grid-column: auto;
    max-height: 440px;
  }

  .lista-item {
    grid-template-columns: 4px 1fr;
  }

  .lista-acoes {
    grid-column: 2;
    flex-direction: row;
    align-items: center;
    margin-top: 0.35rem;
  }
}
</style>
