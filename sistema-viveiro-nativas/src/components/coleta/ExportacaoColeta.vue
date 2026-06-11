<template>
  <div class="export-bar">
    <span class="label" title="CSV usa os dados visíveis com os filtros atuais">Exportar</span>
    <button type="button" class="btn-exp" :disabled="carregando" @click="exp('matrizes')">
      Matrizes CSV
    </button>
    <button type="button" class="btn-exp" :disabled="carregando" @click="exp('coletas')">
      Coletas CSV
    </button>
    <button type="button" class="btn-exp" :disabled="carregando" @click="exp('lotes')">
      Lotes CSV
    </button>
    <button
      type="button"
      class="btn-exp"
      :disabled="carregando || !idMatriz"
      title="Selecione uma matriz no mapa"
      @click="exp('rastreio')"
    >
      Rastreio matriz CSV
    </button>
    <button type="button" class="btn-exp btn-pdf" :disabled="gerandoPdf" @click="gerarPdf">
      Relatório PDF
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useColetaStore } from '@/store/coleta'
import {
  exportMatrizesCsvFromStore,
  exportColetasCsvFromStore,
  exportLotesCsvFromStore,
  exportRastreabilidadeMatrizFromStore
} from '@/services/coletaRelatorios'

const store = useColetaStore()
const carregando = ref(false)
const gerandoPdf = ref(false)

const idMatriz = computed(() => store.matrizSelecionada?.id)

function exp(tipo) {
  carregando.value = true
  try {
    if (tipo === 'matrizes') exportMatrizesCsvFromStore(store)
    else if (tipo === 'coletas') exportColetasCsvFromStore(store)
    else if (tipo === 'lotes') exportLotesCsvFromStore(store)
    else if (tipo === 'rastreio') {
      if (!idMatriz.value) {
        alert('Selecione uma matriz no mapa para exportar o dossiê de rastreabilidade.')
        return
      }
      exportRastreabilidadeMatrizFromStore(store, idMatriz.value)
    }
  } catch (e) {
    alert(e.message || 'Erro na exportação')
  } finally {
    carregando.value = false
  }
}

async function gerarPdf() {
  const el = document.getElementById('relatorio-coleta-pdf')
  if (!el) return
  gerandoPdf.value = true
  try {
    const html2pdf = (await import('html2pdf.js')).default
    await html2pdf()
      .set({
        margin: 10,
        filename: `coleta-relatorio-${new Date().toISOString().slice(0, 10)}.pdf`,
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      })
      .from(el)
      .save()
  } catch (e) {
    alert('Erro ao gerar PDF: ' + (e.message || e))
  } finally {
    gerandoPdf.value = false
  }
}
</script>

<style scoped>
.export-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}
.label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-secondary);
}
.btn-exp {
  padding: 0.35rem 0.65rem;
  font-size: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  cursor: pointer;
}
.btn-exp:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary-dark);
}
.btn-exp:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-pdf {
  background: var(--color-success-bg);
  border-color: var(--color-primary);
}
</style>
