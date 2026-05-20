<template>
  <div v-if="aberto" class="modal-overlay" @click.self="fechar">
    <div class="modal-card" role="dialog">
      <header class="modal-header">
        <h2>{{ modoEdicao ? 'Editar árvore matriz' : 'Cadastrar árvore matriz' }}</h2>
        <button type="button" class="btn-fechar" @click="fechar">×</button>
      </header>

      <form class="modal-body" @submit.prevent="salvar">
        <label class="field">
          Nome / código da matriz
          <input v-model="form.nome" type="text" required placeholder="Ex.: Matriz IPÊ-01" />
        </label>

        <label class="field">
          Espécie
          <select v-model="form.id_especie" required :disabled="carregandoEspecies">
            <option value="">Selecione...</option>
            <option v-for="e in especies" :key="e.id" :value="e.id">
              {{ e.nome_popular || e.nome_cientifico }}
            </option>
          </select>
        </label>

        <div class="field-row">
          <label class="field">
            Cidade
            <input v-model="form.cidade" type="text" placeholder="Ex.: Curitiba" />
          </label>
          <label class="field">
            Município
            <input v-model="form.municipio" type="text" placeholder="Município do imóvel" />
          </label>
        </div>

        <div class="field-row">
          <label class="field">
            UF
            <input v-model="form.estado" type="text" maxlength="2" placeholder="PR" />
          </label>
          <label class="field">
            Nome do imóvel
            <input v-model="form.imovel_nome" type="text" placeholder="Fazenda, fragmento, APP..." />
          </label>
        </div>

        <fieldset class="secao-fieldset">
          <legend>Procedência / compliance</legend>
          <label class="field">
            Tipo de origem
            <select v-model="form.tipo_origem">
              <option value="">Selecione...</option>
              <option v-for="t in TIPOS_ORIGEM" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </label>
          <label class="field">
            Nº autorização / documento
            <input v-model="form.numero_autorizacao" type="text" placeholder="Licença, AUTEF, termo..." />
          </label>
          <label class="field">
            Observações legais
            <textarea v-model="form.observacoes_legais" rows="2" />
          </label>
        </fieldset>

        <fieldset class="secao-fieldset">
          <legend>Fenologia / janela de coleta</legend>
          <div class="field-row">
            <label class="field">
              Início frutificação
              <select v-model="form.mes_inicio_frutificacao">
                <option value="">—</option>
                <option v-for="m in MESES" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
            </label>
            <label class="field">
              Fim frutificação
              <select v-model="form.mes_fim_frutificacao">
                <option value="">—</option>
                <option v-for="m in MESES" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
            </label>
          </div>
          <label class="field">
            Estágio atual
            <select v-model="form.estagio_frutificacao">
              <option value="">—</option>
              <option v-for="e in ESTAGIOS_FRUTIFICACAO" :key="e.value" :value="e.value">{{ e.label }}</option>
            </select>
          </label>
          <label class="field">
            Observações fenológicas
            <textarea v-model="form.fenologia_observacoes" rows="2" />
          </label>
        </fieldset>

        <fieldset class="coord-fieldset">
          <legend>Tipo de coordenada</legend>
          <label class="radio">
            <input v-model="form.tipo_coordenada" type="radio" value="geografica" />
            Geográficas (latitude / longitude)
          </label>
          <label class="radio">
            <input v-model="form.tipo_coordenada" type="radio" value="utm" />
            Cartesianas UTM (metros)
          </label>
        </fieldset>

        <div v-if="form.tipo_coordenada === 'geografica'" class="field-row">
          <label class="field">
            Latitude
            <input v-model.number="form.latitude" type="number" step="any" required placeholder="-25.4284" />
          </label>
          <label class="field">
            Longitude
            <input v-model.number="form.longitude" type="number" step="any" required placeholder="-49.2733" />
          </label>
        </div>

        <div v-else class="utm-grid">
          <label class="field">
            Zona UTM
            <input v-model.number="form.utm_zona" type="number" min="1" max="60" required placeholder="22" />
          </label>
          <label class="field">
            Easting (X)
            <input v-model.number="form.utm_easting" type="number" step="any" required />
          </label>
          <label class="field">
            Northing (Y)
            <input v-model.number="form.utm_northing" type="number" step="any" required />
          </label>
          <p v-if="previewLatLng" class="preview-coord">
            ≈ Lat {{ previewLatLng.latitude }}, Lng {{ previewLatLng.longitude }}
          </p>
        </div>

        <p class="dica-coleta">
          Coletas geram lotes rastreáveis. A taxa de germinação na matriz é atualizada pelos testes nos lotes.
        </p>

        <label class="field">
          Observações
          <textarea v-model="form.observacoes" rows="3" placeholder="Acesso, porte, produção..." />
        </label>

        <p v-if="erro" class="erro">{{ erro }}</p>

        <footer class="modal-footer">
          <button type="button" class="btn-sec" @click="fechar">Cancelar</button>
          <button type="submit" class="btn-prim" :disabled="salvando">
            {{ salvando ? 'Salvando...' : modoEdicao ? 'Salvar alterações' : 'Cadastrar' }}
          </button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { listEspecies } from '@/services/especies'
import { useColetaStore } from '@/store/coleta'
import { utmParaLatLng } from '@/utils/coordenadas'
import { TIPOS_ORIGEM, ESTAGIOS_FRUTIFICACAO, MESES } from '@/constants/coletaDominio'

const props = defineProps({
  aberto: { type: Boolean, default: false },
  /** Se informado, abre em modo edição */
  matriz: { type: Object, default: null }
})

const emit = defineEmits(['fechar', 'salvo'])

const store = useColetaStore()
const especies = ref([])
const carregandoEspecies = ref(false)
const salvando = ref(false)
const erro = ref('')

const modoEdicao = computed(() => Boolean(props.matriz?.id))

const formPadrao = () => ({
  nome: '',
  id_especie: '',
  cidade: '',
  estado: '',
  tipo_coordenada: 'geografica',
  latitude: null,
  longitude: null,
  utm_zona: 22,
  utm_easting: null,
  utm_northing: null,
  municipio: '',
  imovel_nome: '',
  tipo_origem: '',
  numero_autorizacao: '',
  observacoes_legais: '',
  mes_inicio_frutificacao: '',
  mes_fim_frutificacao: '',
  estagio_frutificacao: '',
  fenologia_observacoes: '',
  observacoes: ''
})

const form = ref(formPadrao())

function preencherForm(matriz) {
  if (!matriz) {
    form.value = formPadrao()
    return
  }
  form.value = {
    nome: matriz.nome || '',
    id_especie: matriz.id_especie || '',
    cidade: matriz.cidade || '',
    estado: matriz.estado || '',
    tipo_coordenada: matriz.tipo_coordenada || 'geografica',
    latitude: matriz.latitude != null ? Number(matriz.latitude) : null,
    longitude: matriz.longitude != null ? Number(matriz.longitude) : null,
    utm_zona: matriz.utm_zona ?? 22,
    utm_easting: matriz.utm_easting != null ? Number(matriz.utm_easting) : null,
    utm_northing: matriz.utm_northing != null ? Number(matriz.utm_northing) : null,
    municipio: matriz.municipio || '',
    imovel_nome: matriz.imovel_nome || '',
    tipo_origem: matriz.tipo_origem || '',
    numero_autorizacao: matriz.numero_autorizacao || '',
    observacoes_legais: matriz.observacoes_legais || '',
    mes_inicio_frutificacao: matriz.mes_inicio_frutificacao ?? '',
    mes_fim_frutificacao: matriz.mes_fim_frutificacao ?? '',
    estagio_frutificacao: matriz.estagio_frutificacao || '',
    fenologia_observacoes: matriz.fenologia_observacoes || '',
    observacoes: matriz.observacoes || ''
  }
}

const previewLatLng = computed(() => {
  if (form.value.tipo_coordenada !== 'utm') return null
  const { utm_easting, utm_northing, utm_zona } = form.value
  if (!utm_easting || !utm_northing || !utm_zona) return null
  try {
    return utmParaLatLng(utm_easting, utm_northing, utm_zona)
  } catch {
    return null
  }
})

async function carregarEspecies() {
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

watch(
  () => [props.aberto, props.matriz],
  async ([aberto]) => {
    if (!aberto) return
    erro.value = ''
    await carregarEspecies()
    preencherForm(props.matriz)
  }
)

function fechar() {
  emit('fechar')
}

function montarPayload() {
  const payload = {
    nome: form.value.nome.trim(),
    id_especie: Number(form.value.id_especie),
    cidade: form.value.cidade || null,
    estado: form.value.estado?.toUpperCase() || null,
    tipo_coordenada: form.value.tipo_coordenada,
    municipio: form.value.municipio || null,
    imovel_nome: form.value.imovel_nome || null,
    tipo_origem: form.value.tipo_origem || null,
    numero_autorizacao: form.value.numero_autorizacao || null,
    observacoes_legais: form.value.observacoes_legais || null,
    mes_inicio_frutificacao: form.value.mes_inicio_frutificacao || null,
    mes_fim_frutificacao: form.value.mes_fim_frutificacao || null,
    estagio_frutificacao: form.value.estagio_frutificacao || null,
    fenologia_observacoes: form.value.fenologia_observacoes || null,
    observacoes: form.value.observacoes || null
  }

  if (form.value.tipo_coordenada === 'geografica') {
    payload.latitude = form.value.latitude
    payload.longitude = form.value.longitude
  } else {
    payload.utm_zona = form.value.utm_zona
    payload.utm_easting = form.value.utm_easting
    payload.utm_northing = form.value.utm_northing
  }

  return payload
}

async function salvar() {
  erro.value = ''
  if (!form.value.id_especie) {
    erro.value = 'Selecione uma espécie.'
    return
  }
  salvando.value = true
  try {
    const payload = montarPayload()
    const resultado = modoEdicao.value
      ? await store.atualizar(props.matriz.id, payload)
      : await store.cadastrar(payload)
    emit('salvo', resultado)
    fechar()
  } catch (e) {
    const detail = e.response?.data?.detail
    erro.value = Array.isArray(detail)
      ? detail.map((d) => d.msg || d).join(', ')
      : detail || e.message || 'Erro ao salvar'
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1500;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-card {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 560px;
  max-height: 92vh;
  overflow: auto;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.125rem;
}

.btn-fechar {
  border: none;
  background: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.field input,
.field select,
.field textarea {
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

.secao-fieldset,
.coord-fieldset {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.coord-fieldset legend {
  font-size: 0.8125rem;
  font-weight: 600;
  padding: 0 0.25rem;
}

.radio {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 400;
  margin-bottom: 0.35rem;
  font-size: 0.875rem;
}

.utm-grid {
  margin-bottom: 1rem;
}

.preview-coord {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-sec,
.btn-prim {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-sec {
  background: #f3f4f6;
}

.btn-prim {
  background: #6ca234;
  color: #fff;
  font-weight: 600;
}

.btn-prim:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.dica-coleta {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0 0 1rem;
  line-height: 1.4;
}

.erro {
  color: #b91c1c;
  font-size: 0.875rem;
}
</style>
