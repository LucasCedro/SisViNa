<template>
  <div class="prescricao-container">
    <div class="instrucao-card">
      <div class="instrucao-header">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3>Como funciona</h3>
      </div>
      <p>
        Consulte os dados cadastrados de cada espécie (germinação, crescimento, descrição técnica).
        Selecione uma espécie e clique em "Ver ficha" para gerar o PDF com as informações do banco.
      </p>
      <p class="disclaimer">
        <strong>Nota:</strong> Campos de prescrição detalhada (adubação por fase, fitossanidade) devem ser
        cadastrados na espécie no banco. Enquanto não houver, a ficha exibe apenas os dados disponíveis.
      </p>
    </div>

    <!-- Filtro e seleção de espécies -->
    <div class="filtro-section">
      <div class="search-container">
        <input 
          type="text" 
          class="search-input" 
          v-model="filtro" 
          placeholder="Buscar espécie..."
        >
        <button class="search-button">
          <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
      </div>
    </div>

    <p v-if="carregando" class="status-msg">Carregando espécies...</p>

    <!-- Lista de espécies -->
    <div v-else class="especies-grid">
      <div v-for="especie in especiesFiltradas" :key="especie.id" class="especie-card">
        <div class="especie-header">
          <h3 class="especie-nome">{{ especie.nome }}</h3>
          <p class="especie-nome-cientifico">{{ especie.nomeCientifico }}</p>
        </div>
        <div class="especie-info">
          <div class="info-item">
            <span class="info-label">Família:</span>
            <span class="info-value">{{ especie.familia }}</span>
          </div>
          <div v-if="especie.tempoGerminacao" class="info-item">
            <span class="info-label">Germinação:</span>
            <span class="info-value">~{{ especie.tempoGerminacao }} dias</span>
          </div>
          <div v-if="especie.tempoCrescimento" class="info-item">
            <span class="info-label">Crescimento no viveiro:</span>
            <span class="info-value">~{{ especie.tempoCrescimento }} dias</span>
          </div>
        </div>
        <button class="gerar-prescricao-btn" @click="selecionarEspecie(especie)">
          Ver ficha
        </button>
      </div>
    </div>

    <!-- Modal de prescrição -->
    <div class="modal-overlay" v-if="modalAberto" @click.self="fecharModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">Prescrição Técnica: {{ especieSelecionada?.nome }}</h2>
          <button class="btn-fechar" @click="fecharModal">×</button>
        </div>
        
        <div class="modal-body" id="prescricao-para-pdf">
          <div class="prescricao-header">
            <h2>Prescrição Técnica - {{ especieSelecionada?.nome }}</h2>
            <p class="prescricao-subtitulo">{{ especieSelecionada?.nomeCientifico }}</p>
            <p class="prescricao-data">Data: {{ dataAtual }}</p>
          </div>

          <div class="prescricao-section">
            <h3 class="section-titulo">Dados cadastrados</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Família:</span>
                <span class="info-value">{{ especieSelecionada?.familia || '—' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Tempo de germinação:</span>
                <span class="info-value">
                  {{ especieSelecionada?.tempoGerminacao != null ? `${especieSelecionada.tempoGerminacao} dias` : '—' }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">Tempo de crescimento:</span>
                <span class="info-value">
                  {{ especieSelecionada?.tempoCrescimento != null ? `${especieSelecionada.tempoCrescimento} dias` : '—' }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">Altura máxima:</span>
                <span class="info-value">
                  {{ especieSelecionada?.alturaMaxima != null ? `${especieSelecionada.alturaMaxima} m` : '—' }}
                </span>
              </div>
              <div class="info-item full-width">
                <span class="info-label">Descrição / prescrição:</span>
                <span class="info-value">{{ especieSelecionada?.descricao || 'Nenhuma prescrição cadastrada para esta espécie.' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancelar" @click="fecharModal">Fechar</button>
          <button class="btn-exportar" @click="exportarPDF">
            <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Exportar PDF
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import html2pdf from 'html2pdf.js'
import { listEspecies } from '@/services/especies'

// Estado do componente
const filtro = ref('');
const modalAberto = ref(false);
const especieSelecionada = ref(null);

// Formatação da data atual
const dataAtual = new Date().toLocaleDateString('pt-BR');

const especies = ref([])
const carregando = ref(true)

onMounted(async () => {
  try {
    const data = await listEspecies()
    especies.value = data.map((e) => ({
      id: e.id,
      nome: e.nome_popular || e.nome_cientifico,
      nomeCientifico: e.nome_cientifico,
      familia: e.familia || '—',
      descricao: e.descricao,
      tempoGerminacao: e.tempo_germinacao,
      tempoCrescimento: e.tempo_crescimento,
      alturaMaxima: e.altura_maxima != null ? Number(e.altura_maxima) : null,
    }))
  } catch (e) {
    console.error(e)
  } finally {
    carregando.value = false
  }
})


// Filtragem de espécies
const especiesFiltradas = computed(() => {
  if (!filtro.value) return especies.value;
  
  const termoBusca = filtro.value.toLowerCase();
  return especies.value.filter(especie => {
    return especie.nome.toLowerCase().includes(termoBusca) || 
           especie.nomeCientifico.toLowerCase().includes(termoBusca);
  });
});

// Funções
const selecionarEspecie = (especie) => {
  especieSelecionada.value = especie;
  modalAberto.value = true;
};

const fecharModal = () => {
  modalAberto.value = false;
};

const exportarPDF = () => {
  const elemento = document.getElementById('prescricao-para-pdf');
  
  const opcoes = {
    margin: 10,
    filename: `Prescricao_${especieSelecionada.value.nome.replace(/\s+/g, '_')}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };
  
  html2pdf()
    .from(elemento)
    .set(opcoes)
    .save();
};
</script>

<style scoped>
.prescricao-container {
  width: 100%;
  padding: 1.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--color-text-primary);
}

/* Instrução card */
.instrucao-card {
  background-color: var(--color-info-bg);
  border-radius: 0.5rem;
  padding: 1.25rem;
  margin-bottom: 2rem;
  border-left: 4px solid var(--color-info);
}

.instrucao-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.instrucao-header .icon {
  width: 1.5rem;
  height: 1.5rem;
  margin-right: 0.5rem;
  color: var(--color-info);
}

.instrucao-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.disclaimer {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

/* Filtro seção */
.filtro-section {
  margin-bottom: 1.5rem;
}

.search-container {
  display: flex;
  max-width: 500px;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-right: none;
  border-radius: 0.25rem 0 0 0.25rem;
  font-size: 1rem;
}

.search-button {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: none;
  border-radius: 0 0.25rem 0.25rem 0;
  padding: 0 1rem;
  cursor: pointer;
}

.search-icon {
  width: 1.25rem;
  height: 1.25rem;
}

/* Lista de espécies */
.especies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.especie-card {
  background-color: var(--color-text-inverse);
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.25rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.especie-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.especie-header {
  margin-bottom: 1rem;
}

.especie-nome {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  color: var(--color-text-primary);
}

.especie-nome-cientifico {
  font-style: italic;
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin: 0;
}

.especie-info {
  margin-bottom: 1.25rem;
}

.info-item {
  margin-bottom: 0.5rem;
  display: flex;
  flex-wrap: wrap;
}

.info-label {
  font-weight: 600;
  margin-right: 0.5rem;
  min-width: 100px;
}

.info-value {
  color: var(--color-text-primary);
}

.full-width {
  flex-basis: 100%;
  margin-top: 0.5rem;
}

.gerar-prescricao-btn {
  width: 100%;
  background-color: var(--color-info);
  color: var(--color-text-inverse);
  border: none;
  border-radius: 0.25rem;
  padding: 0.75rem 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.gerar-prescricao-btn:hover {
  background-color: var(--color-info);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--color-text-inverse);
  border-radius: 0.5rem;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.btn-fechar {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: var(--color-text-muted);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid var(--color-border-subtle);
}

.btn-cancelar {
  background-color: var(--color-surface-muted);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-exportar {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: none;
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
}

/* Conteúdo específico da prescrição */
.prescricao-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

.prescricao-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: var(--color-text-primary);
}

.prescricao-subtitulo {
  font-style: italic;
  font-size: 1rem;
  color: var(--color-text-muted);
  margin: 0 0 0.5rem 0;
}

.prescricao-data {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin: 0;
}

.prescricao-section {
  margin-bottom: 2rem;
}

.section-titulo {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
  color: var(--color-text-primary);
}

.section-icon {
  width: 1.5rem;
  height: 1.5rem;
  margin-right: 0.5rem;
  color: var(--color-info);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.fase-card {
  background-color: var(--color-surface-muted);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.fase-titulo {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.75rem 0;
  color: var(--color-text-primary);
}

.fase-info {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.fitossanidade-card {
  background-color: var(--color-surface-muted);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.fitossanidade-card h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.75rem 0;
  color: var(--color-text-primary);
}

.medidas-lista {
  margin: 0.5rem 0 0 0;
  padding-left: 1.5rem;
}

.medidas-lista li {
  margin-bottom: 0.5rem;
}

.problema-item {
  border-left: 3px solid var(--color-info);
  padding-left: 1rem;
  margin-bottom: 1rem;
}

.problema-item h5 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: var(--color-text-primary);
}

.problema-item p {
  margin: 0 0 0.75rem 0;
  color: var(--color-text-muted);
}

/* Responsividade */
@media (max-width: 768px) {
  .especies-grid {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    max-width: 95%;
    margin: 0 10px;
  }
}
</style> 