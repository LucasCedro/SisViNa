<template>
  <div v-if="aberto" class="wizard-overlay" @click.self="fechar">
    <div class="wizard-card" role="dialog" aria-labelledby="wizard-titulo">
      <header class="wizard-header">
        <h2 id="wizard-titulo">{{ tituloEtapa }}</h2>
        <button type="button" class="btn-fechar" @click="fechar" aria-label="Fechar">×</button>
      </header>

      <div v-if="etapa === 'tipo'" class="wizard-body">
        <p class="wizard-hint">Escolha o tipo de peça para montar o mapa do seu viveiro (estilo LEGO).</p>
        <div class="tipo-grid">
          <button
            v-for="item in COMPONENTE_CATALOGO"
            :key="item.tipo"
            type="button"
            class="tipo-card"
            @click="escolherTipo(item.tipo)"
          >
            <span class="tipo-cor" :style="{ backgroundColor: item.corPadrao }" />
            <strong>{{ item.titulo }}</strong>
            <span class="tipo-desc">{{ item.descricao }}</span>
          </button>
        </div>
        <footer class="wizard-footer">
          <button type="button" class="btn-sec" @click="fechar">Cancelar</button>
        </footer>
      </div>

      <div v-else-if="etapa === 'canteiro'" class="wizard-body">
        <label class="field">
          Nome do canteiro
          <input v-model="form.nome" type="text" placeholder="Ex.: Canteiro A" />
        </label>
        <div class="field-row">
          <label class="field">
            Linhas
            <input v-model.number="form.linhas" type="number" min="1" max="20" />
          </label>
          <label class="field">
            Colunas
            <input v-model.number="form.colunas" type="number" min="1" max="20" />
          </label>
        </div>
        <p class="wizard-hint">Capacidade: <strong>{{ form.linhas * form.colunas }}</strong> mudas</p>
        <label class="field">
          Espécie (opcional)
          <select v-model="form.especieId" :disabled="carregandoEspecies">
            <option :value="null">— Sem espécie definida —</option>
            <option v-for="e in especies" :key="e.id" :value="e.id">
              {{ e.nome_popular || e.nome_cientifico }}
            </option>
          </select>
        </label>
        <div class="field-row">
          <label class="field">
            Largura no mapa (px)
            <input v-model.number="form.largura" type="number" min="80" max="800" />
          </label>
          <label class="field">
            Altura no mapa (px)
            <input v-model.number="form.altura" type="number" min="60" max="600" />
          </label>
        </div>
        <footer class="wizard-footer">
          <button type="button" class="btn-sec" @click="voltarTipo">Voltar</button>
          <button type="button" class="btn-prim" @click="confirmar">Adicionar ao mapa</button>
        </footer>
      </div>

      <div v-else-if="etapa === 'sementeira'" class="wizard-body">
        <label class="field">
          Nome da sementeira
          <input v-model="form.nome" type="text" placeholder="Ex.: Sementeira 1" />
        </label>
        <label class="field">
          Capacidade aproximada (mudas)
          <input v-model.number="form.capacidade" type="number" min="1" max="9999" />
        </label>
        <div class="field-row">
          <label class="field">
            Largura (px)
            <input v-model.number="form.largura" type="number" min="60" max="800" />
          </label>
          <label class="field">
            Altura (px)
            <input v-model.number="form.altura" type="number" min="40" max="600" />
          </label>
        </div>
        <footer class="wizard-footer">
          <button type="button" class="btn-sec" @click="voltarTipo">Voltar</button>
          <button type="button" class="btn-prim" @click="confirmar">Adicionar ao mapa</button>
        </footer>
      </div>

      <div v-else-if="etapa === 'rustificacao'" class="wizard-body">
        <label class="field">
          Nome da área
          <input v-model="form.nome" type="text" placeholder="Ex.: Rustificação norte" />
        </label>
        <label class="field">
          Capacidade aproximada (mudas)
          <input v-model.number="form.capacidade" type="number" min="1" max="9999" />
        </label>
        <div class="field-row">
          <label class="field">
            Largura (px)
            <input v-model.number="form.largura" type="number" min="60" max="800" />
          </label>
          <label class="field">
            Altura (px)
            <input v-model.number="form.altura" type="number" min="40" max="600" />
          </label>
        </div>
        <footer class="wizard-footer">
          <button type="button" class="btn-sec" @click="voltarTipo">Voltar</button>
          <button type="button" class="btn-prim" @click="confirmar">Adicionar ao mapa</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { COMPONENTE_CATALOGO, TIPOS_COMPONENTE } from '@/constants/viveiroComponentes'
import { listEspecies } from '@/services/especies'

const props = defineProps({
  aberto: { type: Boolean, default: false }
})

const emit = defineEmits(['fechar', 'confirmar'])

const etapa = ref('tipo')
const especies = ref([])
const carregandoEspecies = ref(false)

const form = ref(criarFormPadrao())

const tituloEtapa = computed(() => {
  const map = {
    tipo: 'Cadastrar componente',
    canteiro: 'Novo canteiro',
    sementeira: 'Nova sementeira',
    rustificacao: 'Nova área de rustificação'
  }
  return map[etapa.value] || 'Cadastrar componente'
})

function criarFormPadrao() {
  return {
    tipo: null,
    nome: '',
    linhas: 4,
    colunas: 4,
    largura: 180,
    altura: 130,
    capacidade: 20,
    especieId: null
  }
}

watch(
  () => props.aberto,
  async (aberto) => {
    if (!aberto) return
    etapa.value = 'tipo'
    form.value = criarFormPadrao()
    if (especies.value.length) return
    carregandoEspecies.value = true
    try {
      especies.value = await listEspecies()
    } catch {
      especies.value = []
    } finally {
      carregandoEspecies.value = false
    }
  }
)

function escolherTipo(tipo) {
  form.value = { ...criarFormPadrao(), tipo }
  if (tipo === TIPOS_COMPONENTE.CANTEIRO) {
    form.value.nome = 'Canteiro'
    form.value.largura = 180
    form.value.altura = 130
    etapa.value = 'canteiro'
  } else if (tipo === TIPOS_COMPONENTE.SEMENTEIRA) {
    form.value.nome = 'Sementeira'
    form.value.largura = 130
    form.value.altura = 70
    etapa.value = 'sementeira'
  } else if (tipo === TIPOS_COMPONENTE.RUSTIFICACAO) {
    form.value.nome = 'Área de rustificação'
    form.value.largura = 130
    form.value.altura = 70
    etapa.value = 'rustificacao'
  }
}

function voltarTipo() {
  etapa.value = 'tipo'
  form.value = criarFormPadrao()
}

function fechar() {
  emit('fechar')
}

function confirmar() {
  const f = form.value
  const nome = (f.nome || '').trim()
  if (!nome) {
    alert('Informe um nome para o componente.')
    return
  }

  let especieNome = null
  if (f.especieId) {
    const esp = especies.value.find((e) => e.id === f.especieId)
    especieNome = esp?.nome_popular || esp?.nome_cientifico || null
  }

  emit('confirmar', {
    tipo: f.tipo,
    nome,
    linhas: f.linhas,
    colunas: f.colunas,
    largura: f.largura,
    altura: f.altura,
    capacidade: f.capacidade,
    especieId: f.especieId,
    especieNome
  })
}
</script>

<style scoped>
.wizard-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.wizard-card {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 440px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.wizard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.wizard-header h2 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.btn-fechar {
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem 0.5rem;
}

.wizard-body {
  padding: 1.25rem;
}

.wizard-hint {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.tipo-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tipo-card {
  display: grid;
  grid-template-columns: 12px 1fr;
  grid-template-rows: auto auto;
  gap: 0.25rem 0.75rem;
  text-align: left;
  padding: 0.875rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  background: #fafafa;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.tipo-card:hover {
  border-color: #6ca234;
  background: #f0fdf4;
}

.tipo-cor {
  grid-row: 1 / span 2;
  width: 12px;
  border-radius: 4px;
  align-self: stretch;
}

.tipo-desc {
  grid-column: 2;
  font-size: 0.8125rem;
  color: #6b7280;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.field input,
.field select {
  font-weight: 400;
  padding: 0.5rem 0.65rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.wizard-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #f3f4f6;
  margin-top: 0.5rem;
}

.btn-sec,
.btn-prim {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
}

.btn-sec {
  background: #f3f4f6;
  color: #374151;
}

.btn-prim {
  background: #6ca234;
  color: #fff;
  font-weight: 600;
}

.btn-prim:hover {
  background: #5d9130;
}
</style>
