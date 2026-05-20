<template>
  <div class="prescricao-container">
    <h1 class="page-title">Prescrição Técnica</h1>
    
    <div class="instrucao-card">
      <div class="instrucao-header">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3>Como funciona</h3>
      </div>
      <p>
        Este módulo fornece recomendações técnicas para fertilização e controle fitossanitário 
        das principais espécies nativas. Selecione uma espécie da lista e clique em "Gerar prescrição" 
        para visualizar as recomendações específicas para cada fase do desenvolvimento.
      </p>
      <p class="disclaimer">
        <strong>Nota:</strong> Estas prescrições são baseadas em dados gerais e literatura técnica. 
        Para casos específicos ou problemas graves, consulte um engenheiro florestal ou agrônomo.
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

    <!-- Lista de espécies -->
    <div class="especies-grid">
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
          <div class="info-item">
            <span class="info-label">Bioma:</span>
            <span class="info-value">{{ especie.bioma }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Ciclo de vida:</span>
            <span class="info-value">{{ especie.cicloViveiro }} dias no viveiro</span>
          </div>
        </div>
        <button class="gerar-prescricao-btn" @click="selecionarEspecie(especie)">
          Gerar prescrição
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

          <!-- Informações da espécie -->
          <div class="prescricao-section">
            <h3 class="section-titulo">
              <svg xmlns="http://www.w3.org/2000/svg" class="section-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Informações da Espécie
            </h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Família:</span>
                <span class="info-value">{{ especieSelecionada?.familia }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Bioma:</span>
                <span class="info-value">{{ especieSelecionada?.bioma }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Ciclo no viveiro:</span>
                <span class="info-value">{{ especieSelecionada?.cicloViveiro }} dias</span>
              </div>
              <div class="info-item">
                <span class="info-label">Exigência nutricional:</span>
                <span class="info-value">{{ especieSelecionada?.exigenciaNutricional }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Sensibilidade a pragas:</span>
                <span class="info-value">{{ especieSelecionada?.sensibilidadePragas }}</span>
              </div>
            </div>
          </div>

          <!-- Recomendações de fertilização -->
          <div class="prescricao-section">
            <h3 class="section-titulo">
              <svg xmlns="http://www.w3.org/2000/svg" class="section-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
              Recomendações de Fertilização
            </h3>
            
            <div v-if="especieSelecionada?.fertilizacao">
              <div v-for="(fase, index) in especieSelecionada.fertilizacao" :key="index" class="fase-card">
                <h4 class="fase-titulo">{{ fase.estagio }}</h4>
                <div class="fase-info">
                  <div class="info-item full-width">
                    <span class="info-label">Fertilizante recomendado:</span>
                    <span class="info-value">{{ fase.fertilizante }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Dose:</span>
                    <span class="info-value">{{ fase.dose }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Frequência:</span>
                    <span class="info-value">{{ fase.frequencia }}</span>
                  </div>
                  <div class="info-item full-width">
                    <span class="info-label">Observações:</span>
                    <span class="info-value">{{ fase.observacoes }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recomendações fitossanitárias -->
          <div class="prescricao-section">
            <h3 class="section-titulo">
              <svg xmlns="http://www.w3.org/2000/svg" class="section-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Recomendações Fitossanitárias
            </h3>
            
            <div v-if="especieSelecionada?.fitossanidade">
              <div class="fitossanidade-card">
                <h4>Condições ideais de cultivo</h4>
                <div class="info-item">
                  <span class="info-label">Temperatura:</span>
                  <span class="info-value">{{ especieSelecionada.fitossanidade.temperatura }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Umidade:</span>
                  <span class="info-value">{{ especieSelecionada.fitossanidade.umidade }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Sombreamento:</span>
                  <span class="info-value">{{ especieSelecionada.fitossanidade.sombreamento }}</span>
                </div>
              </div>

              <div class="fitossanidade-card">
                <h4>Monitoramento e Prevenção</h4>
                <div class="info-item full-width">
                  <span class="info-label">Periodicidade:</span>
                  <span class="info-value">{{ especieSelecionada.fitossanidade.periodicidadeMonitoramento }}</span>
                </div>
                <div class="info-item full-width">
                  <span class="info-label">Medidas preventivas:</span>
                  <ul class="medidas-lista">
                    <li v-for="(medida, i) in especieSelecionada.fitossanidade.medidasPreventivas" :key="i">
                      {{ medida }}
                    </li>
                  </ul>
                </div>
              </div>

              <div class="fitossanidade-card">
                <h4>Problemas mais comuns</h4>
                <div v-for="(problema, i) in especieSelecionada.fitossanidade.problemasComuns" :key="i" class="problema-item">
                  <h5>{{ problema.nome }}</h5>
                  <p>{{ problema.descricao }}</p>
                  <div class="info-item full-width">
                    <span class="info-label">Tratamento recomendado:</span>
                    <span class="info-value">{{ problema.tratamento }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Notas e observações gerais -->
          <div class="prescricao-section">
            <h3 class="section-titulo">Notas Adicionais</h3>
            <p>As recomendações acima são baseadas em informações técnicas gerais para a espécie. Ajustes podem ser necessários conforme as condições específicas do seu viveiro, incluindo tipo de solo, clima local e estágio de desenvolvimento das mudas.</p>
            <p>Para aplicação de defensivos, sempre utilize EPI adequado e siga as instruções do fabricante.</p>
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

// Dados mockados de espécies
const especies = ref([])

onMounted(async () => {
  try {
    const data = await listEspecies()
    especies.value = data.map(e => ({
      id: e.id,
      nome: e.nome_popular || e.nome_cientifico,
      nomeCientifico: e.nome_cientifico,
      familia: e.familia,
      descricao: e.descricao
    }))
  } catch (e) { console.error(e) }
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
  color: #333;
}

/* Instrução card */
.instrucao-card {
  background-color: #e8f4f8;
  border-radius: 0.5rem;
  padding: 1.25rem;
  margin-bottom: 2rem;
  border-left: 4px solid #2196F3;
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
  color: #2196F3;
}

.instrucao-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.disclaimer {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #666;
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
  border: 1px solid #ddd;
  border-right: none;
  border-radius: 0.25rem 0 0 0.25rem;
  font-size: 1rem;
}

.search-button {
  background-color: #4CAF50;
  color: white;
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
  background-color: white;
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
  color: #333;
}

.especie-nome-cientifico {
  font-style: italic;
  font-size: 0.9rem;
  color: #666;
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
  color: #444;
}

.full-width {
  flex-basis: 100%;
  margin-top: 0.5rem;
}

.gerar-prescricao-btn {
  width: 100%;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 0.25rem;
  padding: 0.75rem 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.gerar-prescricao-btn:hover {
  background-color: #1976D2;
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
  background-color: white;
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
  border-bottom: 1px solid #eee;
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
  color: #777;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #eee;
}

.btn-cancelar {
  background-color: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-exportar {
  background-color: #4CAF50;
  color: white;
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
  border-bottom: 1px solid #eee;
}

.prescricao-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: #333;
}

.prescricao-subtitulo {
  font-style: italic;
  font-size: 1rem;
  color: #666;
  margin: 0 0 0.5rem 0;
}

.prescricao-data {
  font-size: 0.9rem;
  color: #666;
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
  border-bottom: 1px solid #eee;
  color: #333;
}

.section-icon {
  width: 1.5rem;
  height: 1.5rem;
  margin-right: 0.5rem;
  color: #2196F3;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.fase-card {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.fase-titulo {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.75rem 0;
  color: #444;
}

.fase-info {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.fitossanidade-card {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.fitossanidade-card h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.75rem 0;
  color: #444;
}

.medidas-lista {
  margin: 0.5rem 0 0 0;
  padding-left: 1.5rem;
}

.medidas-lista li {
  margin-bottom: 0.5rem;
}

.problema-item {
  border-left: 3px solid #2196F3;
  padding-left: 1rem;
  margin-bottom: 1rem;
}

.problema-item h5 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: #333;
}

.problema-item p {
  margin: 0 0 0.75rem 0;
  color: #666;
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