<template>
  <div class="biblioteca-container">
    <!-- Cabeçalho e Busca -->
    <div class="cabecalho">
      <h1 class="titulo">Biblioteca de Espécies Nativas</h1>
      <div class="campo-busca">
        <input 
          type="text" 
          v-model="termoBusca" 
          placeholder="Buscar por nome científico ou popular..." 
          @input="filtrarEspecies"
          class="input-busca"
        />
        <button class="btn-busca">
          <svg xmlns="http://www.w3.org/2000/svg" class="icon-busca" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Grid de Espécies -->
    <div class="grid-especies" v-if="especiesFiltradas.length > 0">
      <div 
        v-for="especie in especiesFiltradas" 
        :key="especie.nomeCientifico" 
        class="card-especie"
        @click="selecionarEspecie(especie)"
      >
        <div class="card-imagem">
          <img :src="especie.imagens.plantaAdulta" :alt="especie.nomePopular" class="imagem-capa" />
        </div>
        <div class="card-conteudo">
          <h3 class="nome-cientifico">{{ especie.nomeCientifico }}</h3>
          <p class="nome-popular">{{ especie.nomePopular }}</p>
          <p class="familia">Família: {{ especie.familia }}</p>
          <p class="fitofisionomia">{{ especie.fitofisionomia }}</p>
        </div>
      </div>
    </div>
    
    <div v-else class="mensagem-vazia">
      <p>Nenhuma espécie encontrada com o termo "{{ termoBusca }}"</p>
    </div>

    <!-- Modal de Detalhes -->
    <div v-if="especieSelecionada" class="modal-overlay" @click="fecharModal">
      <div class="modal-conteudo" @click.stop>
        <div class="modal-cabecalho">
          <h2 class="titulo-modal">{{ especieSelecionada.nomeCientifico }}</h2>
          <button class="btn-fechar" @click="fecharModal">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon-fechar" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="modal-corpo">
          <!-- Galeria de Imagens -->
          <div class="galeria-imagens">
            <h3 class="titulo-secao">Galeria</h3>
            <div class="grid-imagens">
              <div v-for="(url, tipo) in especieSelecionada.imagens" :key="tipo" class="item-galeria">
                <img :src="url" :alt="tipo" class="imagem-galeria" />
                <p class="legenda-imagem">{{ tipoParaLegenda(tipo) }}</p>
              </div>
            </div>
          </div>

          <!-- Informações Básicas -->
          <div class="info-basica">
            <h3 class="titulo-secao">Informações Básicas</h3>
            <div class="campo-info">
              <span class="label-info">Nome Popular:</span>
              <span class="valor-info">{{ especieSelecionada.nomePopular }}</span>
            </div>
            <div class="campo-info">
              <span class="label-info">Família:</span>
              <span class="valor-info">{{ especieSelecionada.familia }}</span>
            </div>
            <div class="campo-info">
              <span class="label-info">Fitofisionomia:</span>
              <span class="valor-info">{{ especieSelecionada.fitofisionomia }}</span>
            </div>
          </div>

          <!-- Cultivo e Manejo -->
          <div class="info-cultivo">
            <h3 class="titulo-secao">Cultivo e Manejo</h3>
            
            <div class="campo-info">
              <span class="label-info">Processamento do Fruto e Limpeza:</span>
              <p class="valor-info texto-completo">{{ especieSelecionada.processamento }}</p>
            </div>
            
            <div class="campo-info">
              <span class="label-info">Armazenamento:</span>
              <p class="valor-info texto-completo">{{ especieSelecionada.armazenamento }}</p>
            </div>
            
            <div class="campo-info">
              <span class="label-info">Semeadura e Germinação:</span>
              <p class="valor-info texto-completo">{{ especieSelecionada.semeadura }}</p>
            </div>
            
            <div class="campo-info">
              <span class="label-info">Condução da Muda:</span>
              <p class="valor-info texto-completo">{{ especieSelecionada.conducao }}</p>
            </div>
            
            <div class="campo-info">
              <span class="label-info">Substrato:</span>
              <p class="valor-info texto-completo">{{ especieSelecionada.substrato }}</p>
            </div>
            
            <div class="campo-info">
              <span class="label-info">Tempo no Viveiro:</span>
              <p class="valor-info">{{ especieSelecionada.tempoViveiro }}</p>
            </div>
            
            <div class="campo-info">
              <span class="label-info">Adubação:</span>
              <p class="valor-info texto-completo">{{ especieSelecionada.adubacao }}</p>
            </div>
          </div>

          <!-- Observações -->
          <div class="info-observacoes">
            <h3 class="titulo-secao">Observações Gerais</h3>
            <p class="texto-observacoes">{{ especieSelecionada.observacoes }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

// Mock de dados para as espécies
const especies = ref([
  {
    nomeCientifico: "Schinus terebinthifolius",
    nomePopular: "Aroeira",
    familia: "Anacardiaceae",
    fitofisionomia: "Mata Atlântica, Cerrado",
    processamento: "Coletar os frutos diretamente da árvore quando estiverem avermelhados. Para extração das sementes, macerar os frutos em água corrente e separar as sementes usando peneiras. Lavar bem para remover a polpa.",
    armazenamento: "As sementes podem ser armazenadas em local seco e ventilado por até 6 meses. Recomenda-se usar recipientes herméticos em temperatura ambiente ou refrigerada para prolongar a viabilidade.",
    semeadura: "Semear diretamente em canteiros com substrato arenoso. Cobrir levemente com uma fina camada de substrato. A germinação ocorre entre 10 e 30 dias após a semeadura, com taxa de germinação de aproximadamente 60%.",
    conducao: "Evitar excesso de água nos primeiros 20 dias. Plantas jovens toleram luz solar direta, mas devem ser aclimatadas gradualmente. Realizar regas regulares, mas evitando encharcamento.",
    substrato: "Substrato misto com areia, terra vegetal e composto orgânico na proporção 2:1:1. Preferência por solos bem drenados e levemente ácidos.",
    tempoViveiro: "3 a 5 meses",
    adubacao: "Adubação orgânica mensal com composto ou húmus de minhoca. Após 45 dias da germinação, pode-se aplicar fertilizante NPK 10-10-10 em baixa concentração a cada 60 dias.",
    observacoes: "Espécie pioneira com ótimo desenvolvimento em áreas degradadas. Apresenta rápido crescimento e boa capacidade de adaptação a diferentes condições de solo. Importante para a recuperação da fauna local por produzir frutos atrativos para aves.",
    imagens: {
      fruto: "https://source.unsplash.com/random/300x300/?berry",
      semente: "https://source.unsplash.com/random/300x300/?seed",
      muda: "https://source.unsplash.com/random/300x300/?seedling",
      folha: "https://source.unsplash.com/random/300x300/?leaf",
      raiz: "https://source.unsplash.com/random/300x300/?root",
      plantaAdulta: "https://source.unsplash.com/random/300x300/?tree"
    }
  },
  {
    nomeCientifico: "Cecropia pachystachya",
    nomePopular: "Embaúba",
    familia: "Urticaceae",
    fitofisionomia: "Mata Atlântica, Cerrado, Amazônia",
    processamento: "Coletar os frutos maduros e extrair as sementes manualmente ou por maceração em água. As sementes são muito pequenas e precisam ser separadas com cuidado.",
    armazenamento: "Sementes com baixa longevidade. Recomenda-se o uso imediato ou armazenamento por no máximo 3 meses em condições refrigeradas (4-8°C) em recipientes herméticos.",
    semeadura: "Semear superficialmente em substrato fino e peneirado, sem cobrir as sementes. Manter umidade constante através de nebulização. Germinação ocorre entre 15-45 dias, com taxa variável de 30-70%.",
    conducao: "Requer alta luminosidade desde o início. Manter substrato sempre úmido, mas não encharcado. Transplante deve ser realizado quando a muda atingir 5-10 cm de altura.",
    substrato: "Mistura de terra vegetal, areia e composto orgânico na proporção 1:1:1. Substrato deve ser leve e com boa drenagem.",
    tempoViveiro: "4 a 6 meses",
    adubacao: "Adubação orgânica a cada 30 dias. Pode-se utilizar biofertilizantes diluídos a cada 15 dias após o primeiro mês.",
    observacoes: "Espécie pioneira de rápido crescimento, excelente para recuperação de áreas degradadas. Frutos são muito apreciados pela avifauna, tornando-a importante para a restauração ecológica. Preferência por solos úmidos e bem drenados.",
    imagens: {
      fruto: "https://source.unsplash.com/random/300x300/?wild+fruit",
      semente: "https://source.unsplash.com/random/300x300/?tiny+seed",
      muda: "https://source.unsplash.com/random/300x300/?young+plant",
      folha: "https://source.unsplash.com/random/300x300/?tropical+leaf",
      raiz: "https://source.unsplash.com/random/300x300/?plant+root",
      plantaAdulta: "https://source.unsplash.com/random/300x300/?tropical+tree"
    }
  },
  {
    nomeCientifico: "Handroanthus impetiginosus",
    nomePopular: "Ipê-roxo",
    familia: "Bignoniaceae",
    fitofisionomia: "Mata Atlântica, Cerrado, Caatinga",
    processamento: "Coletar os frutos (cápsulas) quando começarem a rachar naturalmente. Secar ao sol para completar a abertura e liberar as sementes aladas. Separar manualmente as sementes do material inerte.",
    armazenamento: "As sementes podem ser armazenadas em câmara fria (5-10°C) por até 8 meses, mantidas em embalagens herméticas com baixa umidade (5-7%).",
    semeadura: "Semear em canteiros ou recipientes individuais com substrato leve. Cobrir levemente com fina camada de substrato peneirado. Manter umidade constante. Germinação ocorre entre 7-20 dias, com taxa aproximada de 70-85%.",
    conducao: "Requer sombreamento parcial (50%) nos primeiros meses, com aclimatação gradual para pleno sol. Regas regulares, reduzindo frequência com o desenvolvimento da muda.",
    substrato: "Mistura de terra de subsolo, areia e composto orgânico na proporção 2:1:1. Preferência por substrato com boa drenagem e pH entre 6.0-7.0.",
    tempoViveiro: "8 a 12 meses",
    adubacao: "Adubação de base com fertilizante de liberação lenta. Complementar com adubações foliares mensais a partir do terceiro mês com macro e micronutrientes.",
    observacoes: "Espécie secundária tardia de grande valor ecológico e paisagístico. Sua madeira é de alta qualidade e durabilidade. Floração exuberante ocorre normalmente durante o período de seca, quando a árvore perde todas as folhas. Desenvolvimento inicial é moderado, acelerando após estabelecimento.",
    imagens: {
      fruto: "https://source.unsplash.com/random/300x300/?seed+pod",
      semente: "https://source.unsplash.com/random/300x300/?winged+seed",
      muda: "https://source.unsplash.com/random/300x300/?tree+sapling",
      folha: "https://source.unsplash.com/random/300x300/?compound+leaf",
      raiz: "https://source.unsplash.com/random/300x300/?tree+root",
      plantaAdulta: "https://source.unsplash.com/random/300x300/?flowering+tree"
    }
  }
]);

// Estado para busca e seleção
const termoBusca = ref('');
const especieSelecionada = ref(null);

// Filtrar espécies com base no termo de busca
const especiesFiltradas = computed(() => {
  if (!termoBusca.value) return especies.value;
  
  const termo = termoBusca.value.toLowerCase();
  return especies.value.filter(especie => 
    especie.nomeCientifico.toLowerCase().includes(termo) || 
    especie.nomePopular.toLowerCase().includes(termo)
  );
});

// Resetar o termo de busca quando o componente for montado
const filtrarEspecies = () => {
  // Esta função existe apenas para capturar o evento @input,
  // o trabalho real é feito pelo computed especiesFiltradas
};

// Selecionar uma espécie para exibir detalhes
const selecionarEspecie = (especie) => {
  especieSelecionada.value = especie;
};

// Fechar o modal de detalhes
const fecharModal = () => {
  especieSelecionada.value = null;
};

// Converter o tipo de imagem em uma legenda mais amigável
const tipoParaLegenda = (tipo) => {
  const mapa = {
    fruto: 'Fruto',
    semente: 'Semente',
    muda: 'Muda',
    folha: 'Folha',
    raiz: 'Sistema Radicular',
    plantaAdulta: 'Planta Adulta'
  };
  return mapa[tipo] || tipo;
};

// Simula a função que buscaria as espécies do backend
const fetchEspecies = async () => {
  try {
    // Aqui seria uma chamada para API
    console.log('Buscando espécies do backend...');
    // No futuro, esta função seria substituída por uma chamada real à API
    // const response = await fetch('/api/especies');
    // especies.value = await response.json();
  } catch (erro) {
    console.error('Erro ao buscar espécies:', erro);
  }
};
</script>

<style scoped>
.biblioteca-container {
  @apply w-full max-w-7xl mx-auto p-6 bg-white min-h-[calc(100vh-64px)];
}

.cabecalho {
  @apply mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4;
}

.titulo {
  @apply text-2xl font-bold text-gray-800;
}

.campo-busca {
  @apply relative flex w-full md:w-96;
}

.input-busca {
  @apply w-full px-4 py-2 border border-gray-300 rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.btn-busca {
  @apply absolute right-2 top-1/2 transform -translate-y-1/2 p-1 text-gray-500;
}

.icon-busca {
  @apply w-5 h-5;
}

.grid-especies {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6;
}

.card-especie {
  @apply bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow cursor-pointer;
}

.card-imagem {
  @apply w-full h-48 overflow-hidden;
}

.imagem-capa {
  @apply w-full h-full object-cover transition-transform hover:scale-105;
}

.card-conteudo {
  @apply p-4;
}

.nome-cientifico {
  @apply text-lg font-semibold text-gray-800 italic;
}

.nome-popular {
  @apply text-base font-medium text-gray-700 mb-2;
}

.familia {
  @apply text-sm text-gray-600;
}

.fitofisionomia {
  @apply text-sm text-gray-600 mt-1;
}

.mensagem-vazia {
  @apply text-center py-12 text-gray-500;
}

/* Estilos do Modal */
.modal-overlay {
  @apply fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4;
}

.modal-conteudo {
  @apply bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto;
}

.modal-cabecalho {
  @apply sticky top-0 bg-white p-6 border-b border-gray-200 flex justify-between items-center z-10;
}

.titulo-modal {
  @apply text-xl font-bold text-gray-800 italic;
}

.btn-fechar {
  @apply p-2 rounded-full hover:bg-gray-100 transition-colors;
}

.icon-fechar {
  @apply w-5 h-5 text-gray-500;
}

.modal-corpo {
  @apply p-6 flex flex-col gap-8;
}

.titulo-secao {
  @apply text-lg font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200;
}

/* Galeria de imagens */
.galeria-imagens {
  @apply mb-6;
}

.grid-imagens {
  @apply grid grid-cols-2 sm:grid-cols-3 gap-4;
}

.item-galeria {
  @apply flex flex-col;
}

.imagem-galeria {
  @apply w-full h-48 object-cover rounded-lg;
}

.legenda-imagem {
  @apply text-sm text-center mt-2 text-gray-700;
}

/* Campos de informação */
.campo-info {
  @apply mb-4;
}

.label-info {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.valor-info {
  @apply text-gray-800;
}

.texto-completo {
  @apply block text-sm text-gray-800 leading-relaxed;
}

.info-observacoes {
  @apply bg-gray-50 p-4 rounded-lg;
}

.texto-observacoes {
  @apply text-sm text-gray-800 leading-relaxed;
}
</style> 