<template>
  <aside v-if="matriz" class="painel-detalhe">
    <button type="button" class="painel-fechar" @click="store.limparSelecao()">×</button>

    <h4>{{ matriz.nome }}</h4>
    <p class="sub">{{ matriz.especie_nome }}</p>

    <nav class="tabs">
      <button
        v-for="t in tabs"
        :key="t.id"
        type="button"
        :class="{ ativo: aba === t.id }"
        @click="aba = t.id"
      >
        {{ t.label }}
      </button>
    </nav>

    <div class="tab-body">
      <div v-show="aba === 'resumo'" class="tab-pane">
        <dl class="dl">
          <dt>Local</dt>
          <dd>{{ local }}</dd>
          <dt>Imóvel</dt>
          <dd>{{ matriz.imovel_nome || '—' }}</dd>
          <dt>Origem</dt>
          <dd>{{ labelTipoOrigem(matriz.tipo_origem) }}</dd>
          <dt>Autorização</dt>
          <dd>{{ matriz.numero_autorizacao || '—' }}</dd>
          <dt>Fenologia</dt>
          <dd>{{ janelaFrutificacao(matriz) }} · {{ labelEstagio(matriz.estagio_frutificacao) }}</dd>
          <dt>Sementes (total)</dt>
          <dd>{{ matriz.sementes_coletadas ?? 0 }}</dd>
          <dt>Germinação (resumo)</dt>
          <dd>{{ matriz.taxa_germinacao != null ? `${matriz.taxa_germinacao}%` : '—' }}</dd>
          <dt>Última coleta</dt>
          <dd>{{ formatarData(matriz.data_ultima_coleta) }}</dd>
        </dl>
        <p v-if="matriz.observacoes_legais" class="legal">
          <strong>Legal:</strong> {{ matriz.observacoes_legais }}
        </p>
        <div class="painel-acoes">
          <button type="button" class="btn-coletar" @click="emit('coletar', matriz)">Registrar coleta</button>
          <button type="button" class="btn-editar" @click="emit('editar', matriz)">Editar matriz</button>
        </div>
      </div>

      <div v-show="aba === 'coletas'" class="tab-pane">
        <div class="tab-head">
          <span>{{ coletas.length }} coleta(s)</span>
          <button type="button" class="link" @click="emit('coletar', matriz)">+ Nova</button>
        </div>
        <ul v-if="coletas.length" class="lista">
          <li v-for="c in coletas" :key="c.id">
            <div>
              <strong>{{ formatarData(c.data_coleta) }}</strong>
              <span>{{ c.quantidade_sementes }} sementes</span>
              <span class="muted">{{ c.funcionario_nome }}</span>
            </div>
            <div class="li-acoes">
              <button type="button" class="link" @click="editarColeta(c)">Editar</button>
              <button type="button" class="link danger" @click="excluirColeta(c)">Excluir</button>
            </div>
          </li>
        </ul>
        <p v-else class="vazio-tab">Nenhuma coleta registrada.</p>
      </div>

      <div v-show="aba === 'lotes'" class="tab-pane">
        <div class="tab-head"><span>{{ lotes.length }} lote(s)</span></div>
        <ul v-if="lotes.length" class="lista">
          <li v-for="l in lotes" :key="l.id">
            <div>
              <strong>{{ l.codigo_lote }}</strong>
              <span>{{ l.quantidade_disponivel }}/{{ l.quantidade_inicial }} disp.</span>
              <span v-if="l.ultimo_teste_germinacao != null" class="tag">
                Germ. {{ l.ultimo_teste_germinacao }}%
              </span>
            </div>
            <button type="button" class="link" @click="emit('teste', l)">Teste</button>
            <button type="button" class="link" @click="emit('semeadura', l)">Semear</button>
          </li>
        </ul>
        <p v-else class="vazio-tab">Coletas geram lotes automaticamente.</p>
      </div>

      <div v-show="aba === 'testes'" class="tab-pane">
        <ul v-if="testes.length" class="lista">
          <li v-for="t in testes" :key="t.id">
            <strong>{{ formatarData(t.data_teste) }}</strong>
            <span>{{ t.codigo_lote }} — {{ t.tipo_teste }}: {{ t.percentual_resultado }}%</span>
          </li>
        </ul>
        <p v-else class="vazio-tab">Registre testes a partir de um lote.</p>
      </div>

      <div v-show="aba === 'producao'" class="tab-pane">
        <ul v-if="semeaduras.length" class="lista">
          <li v-for="s in semeaduras" :key="s.id">
            <strong>{{ formatarData(s.data_semeadura) }}</strong>
            <span>{{ s.codigo_lote }} — {{ s.quantidade_sementes_usadas }} sementes</span>
            <span v-if="s.quantidade_mudas_obtidas">→ {{ s.quantidade_mudas_obtidas }} mudas</span>
            <span v-if="s.plantas_vinculadas">({{ s.plantas_vinculadas }} plantas)</span>
          </li>
        </ul>
        <p v-else class="vazio-tab">Nenhuma semeadura vinculada a lotes desta matriz.</p>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useColetaStore } from '@/store/coleta'
import {
  labelTipoOrigem,
  labelEstagio,
  janelaFrutificacao
} from '@/constants/coletaDominio'

const emit = defineEmits(['editar', 'coletar', 'editar-coleta', 'teste', 'semeadura'])

const store = useColetaStore()
const aba = ref('resumo')

const tabs = [
  { id: 'resumo', label: 'Resumo' },
  { id: 'coletas', label: 'Coletas' },
  { id: 'lotes', label: 'Lotes' },
  { id: 'testes', label: 'Testes' },
  { id: 'producao', label: 'Mudas no viveiro' }
]

const matriz = computed(() => store.matrizSelecionada)
const coletas = computed(() => (matriz.value ? store.coletasDaMatriz(matriz.value.id) : []))
const lotes = computed(() => (matriz.value ? store.lotesDaMatriz(matriz.value.id) : []))
const testes = computed(() => (matriz.value ? store.testesDaMatriz(matriz.value.id) : []))
const semeaduras = computed(() => (matriz.value ? store.semeadurasDaMatriz(matriz.value.id) : []))

function formatarData(data) {
  if (!data) return '—'
  return new Date(data + (String(data).includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR')
}

function local() {
  const p = [matriz.value?.cidade, matriz.value?.municipio, matriz.value?.estado].filter(Boolean)
  return p.length ? p.join(' / ') : '—'
}

function editarColeta(c) {
  emit('editar-coleta', c)
}

async function excluirColeta(c) {
  if (!confirm(`Excluir coleta de ${formatarData(c.data_coleta)}? Lotes vinculados serão removidos.`)) return
  try {
    await store.removerColeta(c.id)
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir')
  }
}
</script>

<style scoped>
.painel-detalhe {
  width: 320px;
  flex-shrink: 0;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  position: relative;
  overflow-y: auto;
  max-height: 560px;
}

.painel-fechar {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  border: none;
  background: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: #6b7280;
}

.painel-detalhe h4 {
  margin: 0 0 0.15rem;
  font-size: 1rem;
  padding-right: 1.5rem;
}

.sub {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}

.tabs button {
  border: none;
  background: #fff;
  padding: 0.25rem 0.45rem;
  font-size: 0.68rem;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.tabs button.ativo {
  background: #6ca234;
  color: #fff;
  font-weight: 600;
}

.tab-body {
  font-size: 0.8125rem;
}

.dl {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.25rem 0.5rem;
  margin: 0 0 0.75rem;
}

.dl dt {
  font-weight: 600;
  color: var(--color-text-secondary);
}

.dl dd {
  margin: 0;
}

.legal {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
}

.tab-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.lista {
  list-style: none;
  margin: 0;
  padding: 0;
}

.lista li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.35rem;
  align-items: flex-start;
}

.lista li div {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.muted {
  color: #9ca3af;
  font-size: 0.75rem;
}

.tag {
  color: #2e7d32;
  font-size: 0.75rem;
}

.link {
  border: none;
  background: none;
  color: #6ca234;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.link.danger {
  color: #b91c1c;
}

.li-acoes {
  display: flex;
  gap: 0.5rem;
}

.vazio-tab {
  color: var(--color-text-secondary);
  text-align: center;
  padding: 1rem 0;
}

.painel-acoes {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.painel-acoes button {
  width: 100%;
  padding: 0.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.8125rem;
  cursor: pointer;
}

.btn-coletar {
  background: #fff3e0;
  color: #e65100;
}

.btn-editar {
  background: #6ca234;
  color: #fff;
}

@media (max-width: 900px) {
  .painel-detalhe {
    width: 100%;
    max-height: none;
  }
}
</style>
