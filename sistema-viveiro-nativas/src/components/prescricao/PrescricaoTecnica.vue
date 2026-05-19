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
import { ref, computed } from 'vue';
import html2pdf from 'html2pdf.js';

// Estado do componente
const filtro = ref('');
const modalAberto = ref(false);
const especieSelecionada = ref(null);

// Formatação da data atual
const dataAtual = new Date().toLocaleDateString('pt-BR');

// Dados mockados de espécies
const especies = ref([
  {
    id: 1,
    nome: 'Ipê Amarelo',
    nomeCientifico: 'Handroanthus albus',
    familia: 'Bignoniaceae',
    bioma: 'Cerrado, Mata Atlântica',
    cicloViveiro: 150,
    exigenciaNutricional: 'Média',
    sensibilidadePragas: 'Baixa',
    fertilizacao: [
      {
        estagio: 'Germinação (1-30 dias)',
        fertilizante: 'Sem adubação',
        dose: 'N/A',
        frequencia: 'N/A',
        observacoes: 'Manter substrato úmido. Não é necessário fertilizar nesta fase.'
      },
      {
        estagio: 'Crescimento inicial (30-90 dias)',
        fertilizante: 'NPK 10-10-10 (solução diluída)',
        dose: '2g/L de água',
        frequencia: 'A cada 15 dias',
        observacoes: 'Iniciar fertilização leve quando surgirem as primeiras folhas verdadeiras.'
      },
      {
        estagio: 'Desenvolvimento (90-120 dias)',
        fertilizante: 'NPK 20-05-20 ou composto orgânico',
        dose: '3g/L de água ou 20g/planta de composto',
        frequencia: 'A cada 15 dias',
        observacoes: 'Aumentar dose de nitrogênio para favorecer o crescimento vegetativo.'
      },
      {
        estagio: 'Rustificação (120-150 dias)',
        fertilizante: 'NPK 04-14-08',
        dose: '3g/L de água',
        frequencia: 'A cada 20 dias',
        observacoes: 'Reduzir nitrogênio e aumentar fósforo para fortalecer sistema radicular e resistência.'
      }
    ],
    fitossanidade: {
      temperatura: '20-30°C (ideal: 25°C)',
      umidade: '60-80%',
      sombreamento: '50% inicialmente, reduzir gradualmente',
      periodicidadeMonitoramento: 'Verificação semanal de folhas e caules, especialmente na face inferior das folhas',
      medidasPreventivas: [
        'Manter bom espaçamento entre mudas para ventilação adequada',
        'Evitar excesso de irrigação, especialmente no final do dia',
        'Remover folhas caídas e material vegetal em decomposição',
        'Desinfetar ferramentas e recipientes antes do uso'
      ],
      problemasComuns: [
        {
          nome: 'Ferrugem (Puccinia spp.)',
          descricao: 'Fungos que causam manchas alaranjadas ou amarronzadas nas folhas.',
          tratamento: 'Aplicação de calda bordalesa (1%) a cada 15 dias como preventivo. Para tratamento curativo, usar fungicida à base de cobre.'
        },
        {
          nome: 'Oidio (Fungo pulverulento)',
          descricao: 'Manchas brancas pulverulentas na superfície das folhas.',
          tratamento: 'Aplicação de solução de bicarbonato de sódio (20g/L + 5ml detergente neutro) ou fungicida à base de enxofre.'
        },
        {
          nome: 'Cochonilhas',
          descricao: 'Pequenos insetos que formam colônias e sugam a seiva das plantas.',
          tratamento: 'Aplicação de óleo de neem (10ml/L) ou óleo mineral (10ml/L). Em infestações severas, inseticida natural à base de rotenona.'
        }
      ]
    }
  },
  {
    id: 2,
    nome: 'Jatobá',
    nomeCientifico: 'Hymenaea courbaril',
    familia: 'Fabaceae',
    bioma: 'Amazônia, Cerrado, Caatinga',
    cicloViveiro: 180,
    exigenciaNutricional: 'Média-Alta',
    sensibilidadePragas: 'Média',
    fertilizacao: [
      {
        estagio: 'Germinação (1-40 dias)',
        fertilizante: 'Sem adubação',
        dose: 'N/A',
        frequencia: 'N/A',
        observacoes: 'Escarificar sementes antes do plantio para melhorar germinação. Manter substrato úmido.'
      },
      {
        estagio: 'Crescimento inicial (40-100 dias)',
        fertilizante: 'NPK 04-14-08 (solução diluída)',
        dose: '2g/L de água',
        frequencia: 'A cada 20 dias',
        observacoes: 'Iniciar com dose baixa de fertilizante rico em fósforo para estimular o desenvolvimento radicular.'
      },
      {
        estagio: 'Desenvolvimento (100-150 dias)',
        fertilizante: 'NPK 10-10-10 ou bokashi',
        dose: '3g/L de água ou 30g/planta de bokashi',
        frequencia: 'A cada 15 dias',
        observacoes: 'Aumentar nitrogênio para estimular crescimento vegetativo.'
      },
      {
        estagio: 'Rustificação (150-180 dias)',
        fertilizante: 'NPK 04-14-08 ou fertilizante natural à base de ossos e cinzas',
        dose: '3g/L de água',
        frequencia: 'A cada 30 dias',
        observacoes: 'Reduzir irrigação e aumentar exposição solar para adaptação ao campo.'
      }
    ],
    fitossanidade: {
      temperatura: '22-32°C (ideal: 28°C)',
      umidade: '60-70%',
      sombreamento: '50% inicialmente, reduzir para 30% após 100 dias',
      periodicidadeMonitoramento: 'Verificação semanal, com especial atenção a mudanças na coloração foliar',
      medidasPreventivas: [
        'Evitar excesso de água no substrato',
        'Garantir boa drenagem para prevenir podridão radicular',
        'Manter espaçamento adequado entre mudas',
        'Realizar podas sanitárias quando necessário'
      ],
      problemasComuns: [
        {
          nome: 'Antracnose (Colletotrichum spp.)',
          descricao: 'Manchas escuras e necróticas nas folhas, frequentemente com lesões arredondadas.',
          tratamento: 'Aplicação de calda bordalesa (1%) preventivamente. Para controle, fungicida à base de cobre orgânico.'
        },
        {
          nome: 'Lagartas desfolhadoras',
          descricao: 'Diversos tipos de lagartas que se alimentam das folhas, causando desfolha parcial ou total.',
          tratamento: 'Aplicação de Bacillus thuringiensis (Bt) em pulverização foliar (1-2g/L).'
        },
        {
          nome: 'Podridão radicular (Fusarium spp.)',
          descricao: 'Fungos que atacam as raízes, causando amarelecimento, murcha e morte.',
          tratamento: 'Preventivo: Trichoderma spp. (10g/L) aplicado no substrato. Para tratamento, reduzir irrigação e aplicar fungicida adequado.'
        }
      ]
    }
  },
  {
    id: 3,
    nome: 'Pau-Brasil',
    nomeCientifico: 'Paubrasilia echinata',
    familia: 'Fabaceae',
    bioma: 'Mata Atlântica',
    cicloViveiro: 200,
    exigenciaNutricional: 'Média',
    sensibilidadePragas: 'Média-Alta',
    fertilizacao: [
      {
        estagio: 'Germinação (1-45 dias)',
        fertilizante: 'Sem adubação',
        dose: 'N/A',
        frequencia: 'N/A',
        observacoes: 'Escarificar sementes. Manter substrato úmido mas não encharcado.'
      },
      {
        estagio: 'Crescimento inicial (45-120 dias)',
        fertilizante: 'Composto orgânico ou húmus de minhoca',
        dose: '20g/planta ou 10% do volume do substrato',
        frequencia: 'Aplicação única no transplante',
        observacoes: 'Prefere adubação orgânica nesta fase inicial. Evitar adubos químicos concentrados.'
      },
      {
        estagio: 'Desenvolvimento (120-180 dias)',
        fertilizante: 'NPK 10-10-10 ou biofertilizante',
        dose: '2g/L de água ou 10ml/L de biofertilizante',
        frequencia: 'A cada 20 dias',
        observacoes: 'Iniciar fertilização química leve ou continuar com biofertilizantes.'
      },
      {
        estagio: 'Rustificação (180-200 dias)',
        fertilizante: 'NPK 04-14-08',
        dose: '2g/L de água',
        frequencia: 'A cada 30 dias',
        observacoes: 'Reduzir adubação e irrigação gradualmente para preparo ao campo.'
      }
    ],
    fitossanidade: {
      temperatura: '20-28°C (ideal: 24°C)',
      umidade: '70-80%',
      sombreamento: '70% inicialmente, reduzir para 40% gradualmente',
      periodicidadeMonitoramento: 'Verificação a cada 5 dias na fase inicial, semanal na fase de desenvolvimento',
      medidasPreventivas: [
        'Manter boa circulação de ar entre as mudas',
        'Evitar mudanças bruscas de temperatura',
        'Remover folhas atacadas ou com sinais de doenças imediatamente',
        'Utilizar substrato esterilizado'
      ],
      problemasComuns: [
        {
          nome: 'Míldio (Peronospora spp.)',
          descricao: 'Manchas amareladas na parte superior das folhas e esporulação acinzentada na parte inferior.',
          tratamento: 'Aplicação de calda bordalesa preventivamente. Para controle, fungicida à base de cobre ou fosfito de potássio.'
        },
        {
          nome: 'Pulgões',
          descricao: 'Pequenos insetos que se agrupam geralmente em brotos novos e sugam a seiva.',
          tratamento: 'Pulverização com solução de sabão de coco (5%) ou óleo de neem (10ml/L).'
        },
        {
          nome: 'Cochonilhas',
          descricao: 'Insetos que formam colônias nos ramos e folhas, sugando a seiva.',
          tratamento: 'Aplicação de óleo mineral (10ml/L) ou inseticida natural à base de alho e pimenta.'
        }
      ]
    }
  },
  {
    id: 4,
    nome: 'Peroba Rosa',
    nomeCientifico: 'Aspidosperma polyneuron',
    familia: 'Apocynaceae',
    bioma: 'Mata Atlântica',
    cicloViveiro: 220,
    exigenciaNutricional: 'Baixa-Média',
    sensibilidadePragas: 'Baixa',
    fertilizacao: [
      {
        estagio: 'Germinação (1-60 dias)',
        fertilizante: 'Sem adubação',
        dose: 'N/A',
        frequencia: 'N/A',
        observacoes: 'Germinação lenta. Manter substrato úmido e sombreado.'
      },
      {
        estagio: 'Crescimento inicial (60-140 dias)',
        fertilizante: 'NPK 04-14-08 (baixa concentração)',
        dose: '1g/L de água',
        frequencia: 'A cada 30 dias',
        observacoes: 'Iniciar com fertilização muito leve, espécie sensível a excesso de adubos.'
      },
      {
        estagio: 'Desenvolvimento (140-190 dias)',
        fertilizante: 'NPK 10-10-10 ou composto orgânico bem curtido',
        dose: '2g/L de água ou 15g/planta de composto',
        frequencia: 'A cada 25 dias',
        observacoes: 'Crescimento lento, não exige muita adubação.'
      },
      {
        estagio: 'Rustificação (190-220 dias)',
        fertilizante: 'NPK 04-14-08',
        dose: '2g/L de água',
        frequencia: 'Aplicação única no início da fase',
        observacoes: 'Reduzir irrigação e sombreamento gradualmente.'
      }
    ],
    fitossanidade: {
      temperatura: '18-28°C (ideal: 22°C)',
      umidade: '60-70%',
      sombreamento: '70% inicialmente, reduzir para 30% na fase final',
      periodicidadeMonitoramento: 'Verificação quinzenal, espécie bastante resistente',
      medidasPreventivas: [
        'Evitar excesso de água',
        'Garantir boa drenagem do substrato',
        'Evitar danos mecânicos nas mudas',
        'Manter bom espaçamento entre mudas'
      ],
      problemasComuns: [
        {
          nome: 'Fungos de solo (Pythium spp., Rhizoctonia spp.)',
          descricao: 'Causam apodrecimento de raízes e tombamento de mudas.',
          tratamento: 'Preventivo: aplicação de Trichoderma spp. no substrato (10g/L). Reduzir a irrigação e aplicar fungicida adequado se necessário.'
        },
        {
          nome: 'Manchas foliares',
          descricao: 'Diversos fungos que causam manchas de diferentes cores nas folhas.',
          tratamento: 'Calda bordalesa (1%) preventivamente ou fungicida à base de cobre para tratamento.'
        }
      ]
    }
  },
  {
    id: 5,
    nome: 'Aroeira',
    nomeCientifico: 'Schinus terebinthifolia',
    familia: 'Anacardiaceae',
    bioma: 'Mata Atlântica, Cerrado',
    cicloViveiro: 120,
    exigenciaNutricional: 'Baixa',
    sensibilidadePragas: 'Muito Baixa',
    fertilizacao: [
      {
        estagio: 'Germinação (1-25 dias)',
        fertilizante: 'Sem adubação',
        dose: 'N/A',
        frequencia: 'N/A',
        observacoes: 'Germinação rápida. Manter substrato úmido.'
      },
      {
        estagio: 'Crescimento inicial (25-60 dias)',
        fertilizante: 'Composto orgânico ou húmus',
        dose: '10% do volume do substrato',
        frequencia: 'Aplicação única no transplante',
        observacoes: 'Espécie pioneira de rápido crescimento, responde bem à matéria orgânica.'
      },
      {
        estagio: 'Desenvolvimento (60-100 dias)',
        fertilizante: 'NPK 10-10-10',
        dose: '2g/L de água',
        frequencia: 'A cada 20 dias',
        observacoes: 'Adubação leve é suficiente, espécie rústica.'
      },
      {
        estagio: 'Rustificação (100-120 dias)',
        fertilizante: 'NPK 04-14-08',
        dose: '2g/L de água',
        frequencia: 'Aplicação única',
        observacoes: 'Reduzir irrigação. Espécie já é naturalmente resistente.'
      }
    ],
    fitossanidade: {
      temperatura: '18-32°C (ideal: 25°C)',
      umidade: '50-70%',
      sombreamento: '30% inicialmente, pleno sol após 60 dias',
      periodicidadeMonitoramento: 'Verificação mensal, espécie muito resistente',
      medidasPreventivas: [
        'Evitar excesso de irrigação',
        'Garantir boa ventilação',
        'Manter espaçamento adequado entre mudas'
      ],
      problemasComuns: [
        {
          nome: 'Formigas cortadeiras',
          descricao: 'Formigas que cortam as folhas para cultivar fungos.',
          tratamento: 'Uso de iscas à base de sulfluramida no entorno do viveiro, barreira física com graxa, pó de rocha ou iscas atrativas alternativas.'
        }
      ]
    }
  }
]);

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