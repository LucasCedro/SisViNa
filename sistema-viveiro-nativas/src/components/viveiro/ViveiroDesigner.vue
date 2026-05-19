<template>
    <div class="viveiro-designer">
        <!-- Barra de ferramentas -->
        <div class="toolbar">
            <div class="toolbar-section">
                <h2 class="toolbar-title">Elementos</h2>
                <div class="tool-group">
                    <button @click="adicionarCampo" class="tool-btn" title="Adicionar Área de Produção">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="8" height="8" rx="1" />
                            <rect x="13" y="3" width="8" height="8" rx="1" />
                            <rect x="3" y="13" width="8" height="8" rx="1" />
                            <rect x="13" y="13" width="8" height="8" rx="1" />
                        </svg>
                        <span>Área de Produção</span>
                    </button>

                    <button @click="adicionarCanteiro" class="tool-btn" title="Adicionar Canteiro">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <rect x="3" y="5" width="18" height="14" rx="1" />
                            <line x1="3" y1="10" x2="21" y2="10" />
                            <line x1="3" y1="15" x2="21" y2="15" />
                        </svg>
                        <span>Canteiro</span>
                    </button>

                    <button @click="adicionarEspaco" class="tool-btn" title="Adicionar Espaço de Muda">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="5" />
                            <line x1="12" y1="6" x2="12" y2="8" />
                            <line x1="12" y1="16" x2="12" y2="18" />
                            <line x1="6" y1="12" x2="8" y2="12" />
                            <line x1="16" y1="12" x2="18" y2="12" />
                        </svg>
                        <span>Espaço de Muda</span>
                    </button>

                    <button @click="adicionarSementeira" class="tool-btn" title="Adicionar Sementeira">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <rect x="3" y="5" width="18" height="14" rx="1" />
                            <line x1="3" y1="9" x2="21" y2="9" />
                            <path d="M7 14h2m2 0h2m2 0h2" stroke-linecap="round" />
                        </svg>
                        <span>Sementeira</span>
                    </button>

                    <button @click="adicionarAreaTrabalho" class="tool-btn" title="Adicionar Área de Trabalho">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <rect x="3" y="5" width="18" height="14" rx="1" />
                            <path d="M12 5v14" stroke-dasharray="2,2" />
                            <path d="M3 12h18" stroke-dasharray="2,2" />
                        </svg>
                        <span>Área de Trabalho</span>
                    </button>

                    <button @click="adicionarEstoque" class="tool-btn" title="Adicionar Estoque de Substrato">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <path d="M4 10h16v8a1 1 0 01-1 1H5a1 1 0 01-1-1v-8z" />
                            <path d="M12 4v6" stroke-dasharray="2,2" />
                            <path d="M4 10l8-5 8 5" />
                        </svg>
                        <span>Estoque</span>
                    </button>
                </div>
            </div>

            <div class="toolbar-divider"></div>

            <div class="toolbar-section">
                <h2 class="toolbar-title">Projeto</h2>
                <div class="tool-group">
                    <button @click="exportarPlanta" class="tool-btn-export" title="Exportar Planta">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <path d="M12 3v12M5 15l7 7 7-7" />
                            <path d="M5 3h14" stroke-linecap="round" />
                        </svg>
                        <span>Exportar JSON</span>
                    </button>
                    <button @click="importarPlanta" class="tool-btn" title="Importar Planta">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <path d="M12 21V9M5 15l7-7 7 7" />
                            <path d="M5 3h14" stroke-linecap="round" />
                        </svg>
                        <span>Importar</span>
                    </button>
                    <button @click="exportarImagem" class="tool-btn-export" title="Exportar como Imagem">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                            <circle cx="8.5" cy="8.5" r="1.5" />
                            <polyline points="21 15 16 10 5 21" />
                        </svg>
                        <span>Exportar PNG</span>
                    </button>
                </div>
            </div>

            <div class="toolbar-divider"></div>

            <div class="toolbar-section">
                <h2 class="toolbar-title">Ações</h2>
                <div class="tool-group">
                    <button @click="salvarEVoltar" class="tool-btn-primary" title="Salvar e Voltar">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <path d="M5 12h14M12 5l7 7-7 7" />
                        </svg>
                        <span>Salvar e Voltar</span>
                    </button>
                </div>
            </div>

            <div class="zoom-info">Zoom: {{ Math.round(zoom * 100) }}%</div>
        </div>

        <!-- Área de desenho -->
        <div class="designer-area" ref="designerArea" @wheel.prevent="handleZoom" @mousedown="iniciarPanning"
            @touchstart="iniciarTouchPanning" @touchmove.prevent="moverTouchPanning" @touchend="finalizarTouchPanning">
            <div class="designer-container" :style="{
                transform: `scale(${zoom}) translate(${viewPosition.x}px, ${viewPosition.y}px)`,
                transformOrigin: '0 0'
            }">
                <svg class="designer-svg" :viewBox="`0 0 ${viewBox.width} ${viewBox.height}`"
                    preserveAspectRatio="xMinYMin meet">
                    <!-- Grade de fundo com evento de arraste -->
                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#eaeaea" stroke-width="0.5" />
                    </pattern>
                    <rect width="100%" height="100%" fill="url(#grid)" @mousedown="iniciarDragFundo"
                        class="fundo-mapa" />

                    <!-- Marcadores de tamanho -->
                    <g v-if="mostrarMarcadores">
                        <line x1="0" y1="20" x2="100" y2="20" stroke="#999" stroke-width="1" />
                        <text x="50" y="18" text-anchor="middle" class="marcador-texto">100 px</text>

                        <line x1="20" y1="0" x2="20" y2="100" stroke="#999" stroke-width="1" />
                        <text x="22" y="50" dominant-baseline="middle" class="marcador-texto">100 px</text>
                    </g>

                    <!-- Campos -->
                    <g v-for="campo in planta.campos" :key="campo.id">
                        <g class="elemento-grupo" :class="{ 'selecionado': elementoSelecionado?.id === campo.id }"
                            @mousedown="iniciarDragMapa($event, campo)" @click="selecionarElemento(campo)"
                            @dblclick="($event) => handleDblClick($event, campo)">
                            <rect :x="campo.x" :y="campo.y" :width="campo.largura" :height="campo.altura"
                                class="elemento" :style="{ fill: campo.cor, stroke: campo.cor }" :class="{
                                    'campo': campo.tipo === 'campo',
                                    'sementeira': campo.tipo === 'sementeira',
                                    'area-trabalho': campo.tipo === 'area-trabalho',
                                    'estoque': campo.tipo === 'estoque'
                                }" rx="4" />
                            <text :x="campo.x + 10" :y="campo.y + 24" class="elemento-texto"
                                :class="{ 'texto-escuro': ['area-trabalho', 'estoque'].includes(campo.tipo) }">
                                {{ campo.nome }}
                            </text>
                        </g>

                        <!-- Canteiros dentro do campo, apenas para campos de produção -->
                        <g v-if="campo.tipo === 'campo'" v-for="canteiro in campo.canteiros" :key="canteiro.id">
                            <g class="elemento-grupo"
                                :class="{ 'selecionado': elementoSelecionado?.id === canteiro.id }"
                                @mousedown="iniciarDragMapa($event, canteiro, campo)"
                                @click="selecionarElemento(canteiro)"
                                @dblclick="($event) => handleDblClick($event, canteiro)">
                                <rect :x="campo.x + canteiro.x" :y="campo.y + canteiro.y" :width="canteiro.largura"
                                    :height="canteiro.altura" class="elemento canteiro"
                                    :style="{ fill: canteiro.cor, stroke: canteiro.cor }" rx="4" />
                                <text :x="campo.x + canteiro.x + 10" :y="campo.y + canteiro.y + 20"
                                    class="elemento-texto">
                                    {{ canteiro.nome }}
                                </text>
                            </g>

                            <!-- Espaços dentro do canteiro -->
                            <g v-for="espaco in canteiro.espacos" :key="espaco.id">
                                <g class="elemento-grupo"
                                    :class="{ 'selecionado': elementoSelecionado?.id === espaco.id }"
                                    @mousedown="iniciarDragMapa($event, espaco, canteiro, campo)"
                                    @click="selecionarElemento(espaco)"
                                    @dblclick="($event) => handleDblClick($event, espaco)">
                                    <circle :cx="campo.x + canteiro.x + espaco.x" :cy="campo.y + canteiro.y + espaco.y"
                                        :r="espaco.raio" class="elemento espaco"
                                        :style="{ fill: espaco.cor, stroke: espaco.cor }" />
                                    <text :x="campo.x + canteiro.x + espaco.x"
                                        :y="campo.y + canteiro.y + espaco.y + espaco.raio + 12"
                                        class="elemento-texto texto-pequeno text-center" text-anchor="middle">
                                        {{ espaco.nome }}
                                    </text>
                                </g>
                            </g>
                        </g>
                    </g>
                </svg>
            </div>

            <!-- Minimap -->
            <div class="minimap" v-if="mostrarMinimap">
                <div class="minimap-content" @mousedown="iniciarNavegacaoMinimap">
                    <svg class="minimap-svg" :viewBox="`0 0 ${viewBox.width} ${viewBox.height}`">
                        <!-- Elementos simplificados -->
                        <rect v-for="campo in planta.campos" :key="`mini-${campo.id}`" :x="campo.x" :y="campo.y"
                            :width="campo.largura" :height="campo.altura" :style="{ fill: campo.cor }" opacity="0.7" />

                        <!-- Viewport atual -->
                        <rect :x="-viewPosition.x * zoom.value" :y="-viewPosition.y * zoom.value"
                            :width="viewportWidth / zoom.value" :height="viewportHeight / zoom.value" fill="none"
                            stroke="red" stroke-width="2" />
                    </svg>
                </div>
                <button @click="mostrarMinimap = false" class="minimap-toggle">-</button>
            </div>
            <button v-else @click="mostrarMinimap = true" class="minimap-toggle minimap-show">+</button>
        </div>

        <!-- Modal de edição -->
        <div v-if="elementoSelecionado && mostrarModal" class="modal-edicao" @mousedown.stop
            :style="{ left: `${modalPosition.x}px`, top: `${modalPosition.y}px` }">
            <div class="modal-conteudo">
                <div class="modal-header" @mousedown="iniciarDragModal($event)">
                    <h3>{{ obterTituloModal() }}</h3>
                    <button @click="fecharModal" class="btn-fechar">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div class="form-group">
                    <label>Nome:</label>
                    <input v-model="elementoSelecionado.nome" type="text" class="input">
                </div>

                <div v-if="elementoSelecionado.tipo !== 'espaco'" class="form-group">
                    <label>Largura:</label>
                    <div class="input-with-controls">
                        <button @click="ajustarTamanho('largura', -10)" class="input-control">-</button>
                        <input v-model.number="elementoSelecionado.largura" type="number" min="10"
                            class="input input-number">
                        <button @click="ajustarTamanho('largura', 10)" class="input-control">+</button>
                    </div>
                </div>

                <div v-if="elementoSelecionado.tipo !== 'espaco'" class="form-group">
                    <label>Altura:</label>
                    <div class="input-with-controls">
                        <button @click="ajustarTamanho('altura', -10)" class="input-control">-</button>
                        <input v-model.number="elementoSelecionado.altura" type="number" min="10"
                            class="input input-number">
                        <button @click="ajustarTamanho('altura', 10)" class="input-control">+</button>
                    </div>
                </div>

                <div v-if="elementoSelecionado.tipo === 'espaco'" class="form-group">
                    <label>Tamanho:</label>
                    <div class="input-with-controls">
                        <button @click="ajustarTamanho('raio', -1)" class="input-control">-</button>
                        <input v-model.number="elementoSelecionado.raio" type="number" min="3" max="20"
                            class="input input-number">
                        <button @click="ajustarTamanho('raio', 1)" class="input-control">+</button>
                    </div>
                </div>

                <div class="form-group">
                    <label>Cor:</label>
                    <div class="cores-grid">
                        <div v-for="(cor, index) in coresDisponiveis" :key="index" class="cor-opcao"
                            :style="{ backgroundColor: cor }"
                            :class="{ 'selecionada': elementoSelecionado.cor === cor }"
                            @click="elementoSelecionado.cor = cor"></div>
                    </div>
                </div>

                <div class="acoes">
                    <button @click="duplicarElemento" class="btn-duplicar">Duplicar</button>
                    <button @click="excluirElemento" class="btn-excluir">Excluir</button>
                    <button @click="salvarEdicao" class="btn-salvar">Salvar</button>
                </div>
            </div>
        </div>

        <!-- Alerta para confirmar exclusão -->
        <div v-if="alertaExclusao.mostrar" class="alerta-overlay">
            <div class="alerta-modal">
                <div class="alerta-conteudo">
                    <svg xmlns="http://www.w3.org/2000/svg" class="alerta-icone" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2">
                        <path
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <h3 class="alerta-titulo">Confirmar exclusão</h3>
                    <p class="alerta-mensagem">Tem certeza que deseja excluir {{ alertaExclusao.nome }}?</p>
                    <div class="alerta-acoes">
                        <button @click="alertaExclusao.mostrar = false" class="alerta-btn-cancelar">Cancelar</button>
                        <button @click="confirmarExclusao" class="alerta-btn-confirmar">Excluir</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Dicas de navegação -->
        <div v-if="mostrarDicas" class="dicas-navegacao" :class="{ 'fade-out': dicasFadeOut }">
            <div class="dicas-header">
                <h3>Dicas de Navegação</h3>
                <button @click="mostrarDicas = false" class="dicas-close">×</button>
            </div>
            <p><strong>Mover o mapa:</strong> Clique e arraste o fundo</p>
            <p><strong>Zoom:</strong> Use a roda do mouse</p>
            <p><strong>Mover elementos:</strong> Clique e arraste os elementos</p>
            <p><strong>Editar elementos:</strong> Duplo clique sobre o elemento</p>
            <p><strong>Atalhos:</strong></p>
            <p class="ml-2">• Setas para navegar</p>
            <p class="ml-2">• 'm' para mostrar/ocultar o minimap</p>
            <p class="ml-2">• 'r' para mostrar/ocultar réguas</p>
            <p class="ml-2">• 'c' para centralizar a visualização</p>
            <p class="ml-2">• 'h' para mostrar/ocultar estas dicas</p>
        </div>

        <!-- Botão de ajuda -->
        <button v-if="!mostrarDicas" @click="mostrarDicas = true" class="botao-ajuda"
            title="Mostrar dicas de navegação">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
        </button>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue';

// Estado do designer
const planta = reactive({
    campos: [],
    nome: "Planta do Viveiro",
    data: new Date().toISOString().slice(0, 10)
});

// Estado de interação global
const estadoInteracao = reactive({
    arrastando: false,
    elementoArrastando: false,
    fundoArrastando: false,
    zoomAtivo: true,
    panningAtivo: true
});

// Sistema de diagnóstico
const diagnostico = reactive({
    ativo: false,
    ultimaOperacao: '',
    problemasEncontrados: 0,
    log: []
});

// Opções de visualização
const zoom = ref(1);
const mostrarMinimap = ref(false);
const mostrarMarcadores = ref(false);
const mostrarDicas = ref(true); // Mostrar dicas por padrão ao abrir
const viewportWidth = ref(window.innerWidth);
const viewportHeight = ref(window.innerHeight);

const elementoSelecionado = ref(null);
const elementoEmDrag = ref(null);
const elementoPai = ref(null);
const elementoAvo = ref(null); // Para espaços de muda
const offsetDrag = ref({ x: 0, y: 0 });
const designerArea = ref(null);
const mostrarModal = ref(false);

// Alerta de exclusão
const alertaExclusao = reactive({
    mostrar: false,
    elemento: null,
    nome: ''
});

// Cores disponíveis para personalização
const cores = reactive({
    campo: ['#8cc63f', '#6bc473', '#4aba9c', '#39b0c4', '#4793e0'],
    canteiro: ['#6ca234', '#5d9b4c', '#4e9364', '#3f8b7c', '#2f8294'],
    espaco: ['#ffe135', '#ffc42e', '#ffab28', '#ff9321', '#ff7c1c']
});

// Cores disponíveis para o elemento selecionado
const coresDisponiveis = computed(() => {
    if (!elementoSelecionado.value) return [];

    if (elementoSelecionado.value.tipo === 'campo' ||
        elementoSelecionado.value.tipo === 'canteiro' ||
        elementoSelecionado.value.tipo === 'espaco') {
        return cores[elementoSelecionado.value.tipo];
    }

    // Cores padrão para outros tipos
    const corPadrao = {
        'sementeira': ['#ff9600', '#ffb347', '#ffc168', '#ffd084', '#ffe0a8'],
        'area-trabalho': ['#ffe135', '#ffe94f', '#fff066', '#fff588', '#fff8aa'],
        'estoque': ['#b4b4b4', '#c8c8c8', '#d4d4d4', '#e0e0e0', '#ebebeb']
    };

    return corPadrao[elementoSelecionado.value.tipo] || [];
});

// ViewBox responsivo
const viewBox = reactive({
    width: 800,  // Reduzido de 1000 para 800
    height: 600  // Reduzido de 800 para 600
});

// Posição de visualização (panning)
const viewPosition = reactive({
    x: 0,
    y: 0
});

// Ajusta o viewBox quando elementos são adicionados
const ajustarViewBox = () => {
    // Valores iniciais para campos
    let maxX = 400;  // Valor base ainda mais reduzido
    let maxY = 300;  // Valor base ainda mais reduzido

    // Encontra os valores máximos para X e Y
    planta.campos.forEach(campo => {
        const campoMaxX = campo.x + campo.largura + 30; // Margem ainda mais reduzida
        const campoMaxY = campo.y + campo.altura + 30;  // Margem ainda mais reduzida

        maxX = Math.max(maxX, campoMaxX);
        maxY = Math.max(maxY, campoMaxY);
    });

    // Ajusta o viewBox para incluir todos os elementos com margem mínima
    viewBox.width = maxX;
    viewBox.height = maxY;
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Iniciar movimento de panning
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });

const iniciarPanning = (event) => {
    // Verificar se o panning está disponível
    if (!estadoInteracao.panningAtivo || estadoInteracao.arrastando) return;

    // Verificar se o clique foi em um elemento arrastável ou no fundo
    if (event.target.classList.contains('fundo-mapa')) {
        // Se for botão esquerdo no fundo, deixamos o iniciarDragFundo cuidar disso
        if (event.button === 0) {
            return;
        }
    }

    // Para elementos não-fundo, continuar permitindo o panning apenas com botão direito ou do meio
    if (event.button === 0) return;

    event.preventDefault();
    isPanning.value = true;
    estadoInteracao.arrastando = true;
    panStart.value = { x: event.clientX, y: event.clientY };

    document.addEventListener('mousemove', moverPanning);
    document.addEventListener('mouseup', finalizarPanning);
};

const moverPanning = (event) => {
    if (!isPanning.value) return;

    const dx = (event.clientX - panStart.value.x) / zoom.value;
    const dy = (event.clientY - panStart.value.y) / zoom.value;

    viewPosition.x += dx;
    viewPosition.y += dy;

    panStart.value = { x: event.clientX, y: event.clientY };
};

const finalizarPanning = () => {
    isPanning.value = false;
    document.removeEventListener('mousemove', moverPanning);
    document.removeEventListener('mouseup', finalizarPanning);

    // Resetar o estado de interação
    setTimeout(() => {
        estadoInteracao.arrastando = false;
    }, 50);
};

// Observa mudanças na planta para ajustar o viewBox
watch(() => planta.campos, () => {
    ajustarViewBox();
}, { deep: true });

// Variáveis para drag do modal
const modalDrag = ref(false);
const modalOffset = ref({ x: 0, y: 0 });
const modalPosition = ref({ x: 0, y: 0 });

// Funções auxiliares
const obterTituloModal = () => {
    if (!elementoSelecionado.value) return '';

    const tipos = {
        'campo': 'Área de Produção',
        'canteiro': 'Canteiro',
        'espaco': 'Espaço de Muda',
        'sementeira': 'Sementeira',
        'area-trabalho': 'Área de Trabalho',
        'estoque': 'Estoque de Substrato'
    };

    return `Editar ${tipos[elementoSelecionado.value.tipo] || elementoSelecionado.value.tipo}`;
};

const ajustarTamanho = (propriedade, valor) => {
    if (!elementoSelecionado.value) return;

    if (propriedade === 'raio') {
        elementoSelecionado.value.raio = Math.max(3, Math.min(20, elementoSelecionado.value[propriedade] + valor));
    } else {
        elementoSelecionado.value[propriedade] = Math.max(10, elementoSelecionado.value[propriedade] + valor);
    }
};

// Funções de manipulação de elementos
const adicionarCampo = () => {
    const novoCampo = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Nova Área de Produção',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };
    planta.campos.push(novoCampo);
    ajustarViewBox();
    selecionarElemento(novoCampo);

    // Centralize na nova área para melhor visualização
    setTimeout(() => {
        centralizarEmElemento(novoCampo);
    }, 100);
};

const adicionarCanteiro = () => {
    if (!elementoSelecionado.value || elementoSelecionado.value.tipo !== 'campo') {
        alert('Selecione uma área de produção para adicionar um canteiro');
        return;
    }

    const campo = elementoSelecionado.value;
    const novoCanteiro = {
        id: Date.now(),
        tipo: 'canteiro',
        nome: 'Novo Canteiro',
        x: 20,
        y: 20,
        largura: Math.min(80, campo.largura - 40),  // Reduzido para melhor visualização
        altura: Math.min(40, campo.altura - 40),    // Reduzido para melhor visualização
        cor: cores.canteiro[0],
        espacos: []
    };
    campo.canteiros.push(novoCanteiro);
    selecionarElemento(novoCanteiro);
};

const adicionarEspaco = () => {
    if (!elementoSelecionado.value || elementoSelecionado.value.tipo !== 'canteiro') {
        alert('Selecione um canteiro para adicionar um espaço de muda');
        return;
    }

    const canteiro = elementoSelecionado.value;
    const novoEspaco = {
        id: Date.now(),
        tipo: 'espaco',
        nome: 'Muda',
        x: canteiro.largura / 2,
        y: canteiro.altura / 2,
        raio: 5,
        cor: cores.espaco[0]
    };
    canteiro.espacos.push(novoEspaco);
    selecionarElemento(novoEspaco);
};

const adicionarSementeira = () => {
    const novaSementeira = {
        id: Date.now(),
        tipo: 'sementeira',
        nome: 'Nova Sementeira',
        x: 220,  // Posicionada mais próxima
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };
    planta.campos.push(novaSementeira);
    ajustarViewBox();
    selecionarElemento(novaSementeira);

    // Centralize na nova área
    setTimeout(() => {
        centralizarEmElemento(novaSementeira);
    }, 100);
};

const adicionarAreaTrabalho = () => {
    const novaAreaTrabalho = {
        id: Date.now(),
        tipo: 'area-trabalho',
        nome: 'Nova Área de Trabalho',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };
    planta.campos.push(novaAreaTrabalho);
    ajustarViewBox();
    selecionarElemento(novaAreaTrabalho);

    // Centralize na nova área
    setTimeout(() => {
        centralizarEmElemento(novaAreaTrabalho);
    }, 100);
};

const adicionarEstoque = () => {
    const novoEstoque = {
        id: Date.now(),
        tipo: 'estoque',
        nome: 'Novo Estoque de Substrato',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };
    planta.campos.push(novoEstoque);
    ajustarViewBox();
    selecionarElemento(novoEstoque);

    // Centralize no novo estoque
    setTimeout(() => {
        centralizarEmElemento(novoEstoque);
    }, 100);
};

// Nova função para centralizar visualização em um elemento específico
const centralizarEmElemento = (elemento) => {
    // Calcular o centro do elemento
    const centerX = elemento.x + elemento.largura / 2;
    const centerY = elemento.y + elemento.altura / 2;

    // Ajustar posição de visualização para centralizar o elemento
    viewPosition.x = -centerX + (viewportWidth.value / 2) / zoom.value;
    viewPosition.y = -centerY + (viewportHeight.value / 2) / zoom.value;
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para registrar eventos importantes no diagnóstico
const registrarEvento = (tipo, detalhes = null) => {
    if (!diagnostico.ativo) return;

    diagnostico.ultimaOperacao = tipo;
    diagnostico.log.push({
        timestamp: new Date().toISOString(),
        tipo,
        detalhes,
        estadoAtual: JSON.parse(JSON.stringify({
            arrastando: estadoInteracao.arrastando,
            elementoArrastando: estadoInteracao.elementoArrastando,
            fundoArrastando: estadoInteracao.fundoArrastando,
            elementoEmDrag: elementoEmDrag.value ? 'presente' : 'null',
            zoom: zoom.value
        }))
    });

    // Manter apenas os últimos 50 registros
    if (diagnostico.log.length > 50) {
        diagnostico.log.shift();
    }

    // Se detectar um estado inconsistente, incrementar contador
    if ((estadoInteracao.elementoArrastando && !elementoEmDrag.value) ||
        (estadoInteracao.fundoArrastando && !isDraggingFundo.value)) {
        diagnostico.problemasEncontrados++;

        // Se encontrar muitos problemas, tentar corrigir automaticamente
        if (diagnostico.problemasEncontrados > 5) {
            console.warn('Muitos problemas de estado encontrados, tentando corrigir');
            resetAllInteractions();
            diagnostico.problemasEncontrados = 0;
        }
    }
};

// Adicionar uma função especial para fixar problemas específicos com Áreas de Produção
const corrigirProblemasAreas = () => {
    // Verificar se há Áreas de Produção
    if (!planta.campos.length) return;

    // Recriar os elementos visuais (forçar repintura)
    const camposAtuais = [...planta.campos];
    planta.campos = [];
    setTimeout(() => {
        planta.campos = camposAtuais;
    }, 10);

    // Garantir que não há operações de arraste pendentes
    resetAllInteractions();
};
    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Iniciar movimento de panning
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });

const iniciarPanning = (event) => {
    // Verificar se o panning está disponível
    if (!estadoInteracao.panningAtivo || estadoInteracao.arrastando) return;

    // Verificar se o clique foi em um elemento arrastável ou no fundo
    if (event.target.classList.contains('fundo-mapa')) {
        // Se for botão esquerdo no fundo, deixamos o iniciarDragFundo cuidar disso
        if (event.button === 0) {
            return;
        }
    }

    // Para elementos não-fundo, continuar permitindo o panning apenas com botão direito ou do meio
    if (event.button === 0) return;

    event.preventDefault();
    isPanning.value = true;
    estadoInteracao.arrastando = true;
    panStart.value = { x: event.clientX, y: event.clientY };

    document.addEventListener('mousemove', moverPanning);
    document.addEventListener('mouseup', finalizarPanning);
};

const moverPanning = (event) => {
    if (!isPanning.value) return;

    const dx = (event.clientX - panStart.value.x) / zoom.value;
    const dy = (event.clientY - panStart.value.y) / zoom.value;

    viewPosition.x += dx;
    viewPosition.y += dy;

    panStart.value = { x: event.clientX, y: event.clientY };
};

const finalizarPanning = () => {
    isPanning.value = false;
    document.removeEventListener('mousemove', moverPanning);
    document.removeEventListener('mouseup', finalizarPanning);

    // Resetar o estado de interação
    setTimeout(() => {
        estadoInteracao.arrastando = false;
    }, 50);
};

// Observa mudanças na planta para ajustar o viewBox
watch(() => planta.campos, () => {
    ajustarViewBox();
}, { deep: true });

// Variáveis para drag do modal
const modalDrag = ref(false);
const modalOffset = ref({ x: 0, y: 0 });
const modalPosition = ref({ x: 0, y: 0 });

// Funções auxiliares
const obterTituloModal = () => {
    if (!elementoSelecionado.value) return '';

    const tipos = {
        'campo': 'Área de Produção',
        'canteiro': 'Canteiro',
        'espaco': 'Espaço de Muda',
        'sementeira': 'Sementeira',
        'area-trabalho': 'Área de Trabalho',
        'estoque': 'Estoque de Substrato'
    };

    return `Editar ${tipos[elementoSelecionado.value.tipo] || elementoSelecionado.value.tipo}`;
};

const ajustarTamanho = (propriedade, valor) => {
    if (!elementoSelecionado.value) return;

    if (propriedade === 'raio') {
        elementoSelecionado.value.raio = Math.max(3, Math.min(20, elementoSelecionado.value[propriedade] + valor));
    } else {
        elementoSelecionado.value[propriedade] = Math.max(10, elementoSelecionado.value[propriedade] + valor);
    }
};

// Funções de manipulação de elementos
const adicionarCampo = () => {
    const novoCampo = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Nova Área de Produção',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };
    planta.campos.push(novoCampo);
    ajustarViewBox();
    selecionarElemento(novoCampo);

    // Centralize na nova área para melhor visualização
    setTimeout(() => {
        centralizarEmElemento(novoCampo);
    }, 100);
};

const adicionarCanteiro = () => {
    if (!elementoSelecionado.value || elementoSelecionado.value.tipo !== 'campo') {
        alert('Selecione uma área de produção para adicionar um canteiro');
        return;
    }

    const campo = elementoSelecionado.value;
    const novoCanteiro = {
        id: Date.now(),
        tipo: 'canteiro',
        nome: 'Novo Canteiro',
        x: 20,
        y: 20,
        largura: Math.min(80, campo.largura - 40),  // Reduzido para melhor visualização
        altura: Math.min(40, campo.altura - 40),    // Reduzido para melhor visualização
        cor: cores.canteiro[0],
        espacos: []
    };
    campo.canteiros.push(novoCanteiro);
    selecionarElemento(novoCanteiro);
};

const adicionarEspaco = () => {
    if (!elementoSelecionado.value || elementoSelecionado.value.tipo !== 'canteiro') {
        alert('Selecione um canteiro para adicionar um espaço de muda');
        return;
    }

    const canteiro = elementoSelecionado.value;
    const novoEspaco = {
        id: Date.now(),
        tipo: 'espaco',
        nome: 'Muda',
        x: canteiro.largura / 2,
        y: canteiro.altura / 2,
        raio: 5,
        cor: cores.espaco[0]
    };
    canteiro.espacos.push(novoEspaco);
    selecionarElemento(novoEspaco);
};

const adicionarSementeira = () => {
    const novaSementeira = {
        id: Date.now(),
        tipo: 'sementeira',
        nome: 'Nova Sementeira',
        x: 220,  // Posicionada mais próxima
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };
    planta.campos.push(novaSementeira);
    ajustarViewBox();
    selecionarElemento(novaSementeira);

    // Centralize na nova área
    setTimeout(() => {
        centralizarEmElemento(novaSementeira);
    }, 100);
};

const adicionarAreaTrabalho = () => {
    const novaAreaTrabalho = {
        id: Date.now(),
        tipo: 'area-trabalho',
        nome: 'Nova Área de Trabalho',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };
    planta.campos.push(novaAreaTrabalho);
    ajustarViewBox();
    selecionarElemento(novaAreaTrabalho);

    // Centralize na nova área
    setTimeout(() => {
        centralizarEmElemento(novaAreaTrabalho);
    }, 100);
};

const adicionarEstoque = () => {
    const novoEstoque = {
        id: Date.now(),
        tipo: 'estoque',
        nome: 'Novo Estoque de Substrato',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };
    planta.campos.push(novoEstoque);
    ajustarViewBox();
    selecionarElemento(novoEstoque);

    // Centralize no novo estoque
    setTimeout(() => {
        centralizarEmElemento(novoEstoque);
    }, 100);
};

// Nova função para centralizar visualização em um elemento específico
const centralizarEmElemento = (elemento) => {
    // Calcular o centro do elemento
    const centerX = elemento.x + elemento.largura / 2;
    const centerY = elemento.y + elemento.altura / 2;

    // Ajustar posição de visualização para centralizar o elemento
    viewPosition.x = -centerX + (viewportWidth.value / 2) / zoom.value;
    viewPosition.y = -centerY + (viewportHeight.value / 2) / zoom.value;
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});


    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }

    // Adicionar verificação periódica para problemas com Áreas de Produção
    setInterval(() => {
        // Verificar estados inconsistentes específicos de Áreas de Produção
        const campoSemEventos = elementoEmDrag.value && 
                              elementoEmDrag.value.tipo === 'campo' && 
                              !estadoInteracao.elementoArrastando;
                              
        if (campoSemEventos || (estadoInteracao.elementoArrastando && !elementoEmDrag.value)) {
            console.warn('Estado inconsistente detectado, corrigindo...');
            resetAllInteractions();
        }
    }, 2000); // Verificar a cada 2 segundos
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
<template>
    <div class="viveiro-designer">
        <!-- Barra de ferramentas -->
        <div class="toolbar">
            <div class="toolbar-section">
                <h2 class="toolbar-title">Elementos</h2>
                <div class="tool-group">
                    <button @click="adicionarCampo" class="tool-btn" title="Adicionar Área de Produção">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="8" height="8" rx="1" />
                            <rect x="13" y="3" width="8" height="8" rx="1" />
                            <rect x="3" y="13" width="8" height="8" rx="1" />
                            <rect x="13" y="13" width="8" height="8" rx="1" />
                        </svg>
                        <span>Área de Produção</span>
                    </button>

                    <button @click="adicionarCanteiro" class="tool-btn" title="Adicionar Canteiro">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <rect x="3" y="5" width="18" height="14" rx="1" />
                            <line x1="3" y1="10" x2="21" y2="10" />
                            <line x1="3" y1="15" x2="21" y2="15" />
                        </svg>
                        <span>Canteiro</span>
                    </button>

                    <button @click="adicionarEspaco" class="tool-btn" title="Adicionar Espaço de Muda">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="5" />
                            <line x1="12" y1="6" x2="12" y2="8" />
                            <line x1="12" y1="16" x2="12" y2="18" />
                            <line x1="6" y1="12" x2="8" y2="12" />
                            <line x1="16" y1="12" x2="18" y2="12" />
                        </svg>
                        <span>Espaço de Muda</span>
                    </button>

                    <button @click="adicionarSementeira" class="tool-btn" title="Adicionar Sementeira">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <rect x="3" y="5" width="18" height="14" rx="1" />
                            <line x1="3" y1="9" x2="21" y2="9" />
                            <path d="M7 14h2m2 0h2m2 0h2" stroke-linecap="round" />
                        </svg>
                        <span>Sementeira</span>
                    </button>

                    <button @click="adicionarAreaTrabalho" class="tool-btn" title="Adicionar Área de Trabalho">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <rect x="3" y="5" width="18" height="14" rx="1" />
                            <path d="M12 5v14" stroke-dasharray="2,2" />
                            <path d="M3 12h18" stroke-dasharray="2,2" />
                        </svg>
                        <span>Área de Trabalho</span>
                    </button>

                    <button @click="adicionarEstoque" class="tool-btn" title="Adicionar Estoque de Substrato">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <path d="M4 10h16v8a1 1 0 01-1 1H5a1 1 0 01-1-1v-8z" />
                            <path d="M12 4v6" stroke-dasharray="2,2" />
                            <path d="M4 10l8-5 8 5" />
                        </svg>
                        <span>Estoque</span>
                    </button>
                </div>
            </div>

            <div class="toolbar-divider"></div>

            <div class="toolbar-section">
                <h2 class="toolbar-title">Projeto</h2>
                <div class="tool-group">
                    <button @click="exportarPlanta" class="tool-btn-export" title="Exportar Planta">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <path d="M12 3v12M5 15l7 7 7-7" />
                            <path d="M5 3h14" stroke-linecap="round" />
                        </svg>
                        <span>Exportar JSON</span>
                    </button>
                    <button @click="importarPlanta" class="tool-btn" title="Importar Planta">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <path d="M12 21V9M5 15l7-7 7 7" />
                            <path d="M5 3h14" stroke-linecap="round" />
                        </svg>
                        <span>Importar</span>
                    </button>
                    <button @click="exportarImagem" class="tool-btn-export" title="Exportar como Imagem">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                            <circle cx="8.5" cy="8.5" r="1.5" />
                            <polyline points="21 15 16 10 5 21" />
                        </svg>
                        <span>Exportar PNG</span>
                    </button>
                </div>
            </div>

            <div class="toolbar-divider"></div>

            <div class="toolbar-section">
                <h2 class="toolbar-title">Ações</h2>
                <div class="tool-group">
                    <button @click="salvarEVoltar" class="tool-btn-primary" title="Salvar e Voltar">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <path d="M5 12h14M12 5l7 7-7 7" />
                        </svg>
                        <span>Salvar e Voltar</span>
                    </button>
                </div>
            </div>

            <div class="zoom-info">Zoom: {{ Math.round(zoom * 100) }}%</div>
        </div>

        <!-- Área de desenho -->
        <div class="designer-area" ref="designerArea" @wheel.prevent="handleZoom" @mousedown="iniciarPanning"
            @touchstart="iniciarTouchPanning" @touchmove.prevent="moverTouchPanning" @touchend="finalizarTouchPanning">
            <div class="designer-container" :style="{
                transform: `scale(${zoom}) translate(${viewPosition.x}px, ${viewPosition.y}px)`,
                transformOrigin: '0 0'
            }">
                <svg class="designer-svg" :viewBox="`0 0 ${viewBox.width} ${viewBox.height}`"
                    preserveAspectRatio="xMinYMin meet">
                    <!-- Grade de fundo com evento de arraste -->
                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#eaeaea" stroke-width="0.5" />
                    </pattern>
                    <rect width="100%" height="100%" fill="url(#grid)" @mousedown="iniciarDragFundo"
                        class="fundo-mapa" />

                    <!-- Marcadores de tamanho -->
                    <g v-if="mostrarMarcadores">
                        <line x1="0" y1="20" x2="100" y2="20" stroke="#999" stroke-width="1" />
                        <text x="50" y="18" text-anchor="middle" class="marcador-texto">100 px</text>

                        <line x1="20" y1="0" x2="20" y2="100" stroke="#999" stroke-width="1" />
                        <text x="22" y="50" dominant-baseline="middle" class="marcador-texto">100 px</text>
                    </g>

                    <!-- Campos -->
                    <g v-for="campo in planta.campos" :key="campo.id">
                        <g class="elemento-grupo" :class="{ 'selecionado': elementoSelecionado?.id === campo.id }"
                            @mousedown="iniciarDragMapa($event, campo)" @click="selecionarElemento(campo)"
                            @dblclick="($event) => handleDblClick($event, campo)">
                            <rect :x="campo.x" :y="campo.y" :width="campo.largura" :height="campo.altura"
                                class="elemento" :style="{ fill: campo.cor, stroke: campo.cor }" :class="{
                                    'campo': campo.tipo === 'campo',
                                    'sementeira': campo.tipo === 'sementeira',
                                    'area-trabalho': campo.tipo === 'area-trabalho',
                                    'estoque': campo.tipo === 'estoque'
                                }" rx="4" />
                            <text :x="campo.x + 10" :y="campo.y + 24" class="elemento-texto"
                                :class="{ 'texto-escuro': ['area-trabalho', 'estoque'].includes(campo.tipo) }">
                                {{ campo.nome }}
                            </text>
                        </g>

                        <!-- Canteiros dentro do campo, apenas para campos de produção -->
                        <g v-if="campo.tipo === 'campo'" v-for="canteiro in campo.canteiros" :key="canteiro.id">
                            <g class="elemento-grupo"
                                :class="{ 'selecionado': elementoSelecionado?.id === canteiro.id }"
                                @mousedown="iniciarDragMapa($event, canteiro, campo)"
                                @click="selecionarElemento(canteiro)"
                                @dblclick="($event) => handleDblClick($event, canteiro)">
                                <rect :x="campo.x + canteiro.x" :y="campo.y + canteiro.y" :width="canteiro.largura"
                                    :height="canteiro.altura" class="elemento canteiro"
                                    :style="{ fill: canteiro.cor, stroke: canteiro.cor }" rx="4" />
                                <text :x="campo.x + canteiro.x + 10" :y="campo.y + canteiro.y + 20"
                                    class="elemento-texto">
                                    {{ canteiro.nome }}
                                </text>
                            </g>

                            <!-- Espaços dentro do canteiro -->
                            <g v-for="espaco in canteiro.espacos" :key="espaco.id">
                                <g class="elemento-grupo"
                                    :class="{ 'selecionado': elementoSelecionado?.id === espaco.id }"
                                    @mousedown="iniciarDragMapa($event, espaco, canteiro, campo)"
                                    @click="selecionarElemento(espaco)"
                                    @dblclick="($event) => handleDblClick($event, espaco)">
                                    <circle :cx="campo.x + canteiro.x + espaco.x" :cy="campo.y + canteiro.y + espaco.y"
                                        :r="espaco.raio" class="elemento espaco"
                                        :style="{ fill: espaco.cor, stroke: espaco.cor }" />
                                    <text :x="campo.x + canteiro.x + espaco.x"
                                        :y="campo.y + canteiro.y + espaco.y + espaco.raio + 12"
                                        class="elemento-texto texto-pequeno text-center" text-anchor="middle">
                                        {{ espaco.nome }}
                                    </text>
                                </g>
                            </g>
                        </g>
                    </g>
                </svg>
            </div>

            <!-- Minimap -->
            <div class="minimap" v-if="mostrarMinimap">
                <div class="minimap-content" @mousedown="iniciarNavegacaoMinimap">
                    <svg class="minimap-svg" :viewBox="`0 0 ${viewBox.width} ${viewBox.height}`">
                        <!-- Elementos simplificados -->
                        <rect v-for="campo in planta.campos" :key="`mini-${campo.id}`" :x="campo.x" :y="campo.y"
                            :width="campo.largura" :height="campo.altura" :style="{ fill: campo.cor }" opacity="0.7" />

                        <!-- Viewport atual -->
                        <rect :x="-viewPosition.x * zoom.value" :y="-viewPosition.y * zoom.value"
                            :width="viewportWidth / zoom.value" :height="viewportHeight / zoom.value" fill="none"
                            stroke="red" stroke-width="2" />
                    </svg>
                </div>
                <button @click="mostrarMinimap = false" class="minimap-toggle">-</button>
            </div>
            <button v-else @click="mostrarMinimap = true" class="minimap-toggle minimap-show">+</button>
        </div>

        <!-- Modal de edição -->
        <div v-if="elementoSelecionado && mostrarModal" class="modal-edicao" @mousedown.stop
            :style="{ left: `${modalPosition.x}px`, top: `${modalPosition.y}px` }">
            <div class="modal-conteudo">
                <div class="modal-header" @mousedown="iniciarDragModal($event)">
                    <h3>{{ obterTituloModal() }}</h3>
                    <button @click="fecharModal" class="btn-fechar">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div class="form-group">
                    <label>Nome:</label>
                    <input v-model="elementoSelecionado.nome" type="text" class="input">
                </div>

                <div v-if="elementoSelecionado.tipo !== 'espaco'" class="form-group">
                    <label>Largura:</label>
                    <div class="input-with-controls">
                        <button @click="ajustarTamanho('largura', -10)" class="input-control">-</button>
                        <input v-model.number="elementoSelecionado.largura" type="number" min="10"
                            class="input input-number">
                        <button @click="ajustarTamanho('largura', 10)" class="input-control">+</button>
                    </div>
                </div>

                <div v-if="elementoSelecionado.tipo !== 'espaco'" class="form-group">
                    <label>Altura:</label>
                    <div class="input-with-controls">
                        <button @click="ajustarTamanho('altura', -10)" class="input-control">-</button>
                        <input v-model.number="elementoSelecionado.altura" type="number" min="10"
                            class="input input-number">
                        <button @click="ajustarTamanho('altura', 10)" class="input-control">+</button>
                    </div>
                </div>

                <div v-if="elementoSelecionado.tipo === 'espaco'" class="form-group">
                    <label>Tamanho:</label>
                    <div class="input-with-controls">
                        <button @click="ajustarTamanho('raio', -1)" class="input-control">-</button>
                        <input v-model.number="elementoSelecionado.raio" type="number" min="3" max="20"
                            class="input input-number">
                        <button @click="ajustarTamanho('raio', 1)" class="input-control">+</button>
                    </div>
                </div>

                <div class="form-group">
                    <label>Cor:</label>
                    <div class="cores-grid">
                        <div v-for="(cor, index) in coresDisponiveis" :key="index" class="cor-opcao"
                            :style="{ backgroundColor: cor }"
                            :class="{ 'selecionada': elementoSelecionado.cor === cor }"
                            @click="elementoSelecionado.cor = cor"></div>
                    </div>
                </div>

                <div class="acoes">
                    <button @click="duplicarElemento" class="btn-duplicar">Duplicar</button>
                    <button @click="excluirElemento" class="btn-excluir">Excluir</button>
                    <button @click="salvarEdicao" class="btn-salvar">Salvar</button>
                </div>
            </div>
        </div>

        <!-- Alerta para confirmar exclusão -->
        <div v-if="alertaExclusao.mostrar" class="alerta-overlay">
            <div class="alerta-modal">
                <div class="alerta-conteudo">
                    <svg xmlns="http://www.w3.org/2000/svg" class="alerta-icone" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2">
                        <path
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <h3 class="alerta-titulo">Confirmar exclusão</h3>
                    <p class="alerta-mensagem">Tem certeza que deseja excluir {{ alertaExclusao.nome }}?</p>
                    <div class="alerta-acoes">
                        <button @click="alertaExclusao.mostrar = false" class="alerta-btn-cancelar">Cancelar</button>
                        <button @click="confirmarExclusao" class="alerta-btn-confirmar">Excluir</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Dicas de navegação -->
        <div v-if="mostrarDicas" class="dicas-navegacao" :class="{ 'fade-out': dicasFadeOut }">
            <div class="dicas-header">
                <h3>Dicas de Navegação</h3>
                <button @click="mostrarDicas = false" class="dicas-close">×</button>
            </div>
            <p><strong>Mover o mapa:</strong> Clique e arraste o fundo</p>
            <p><strong>Zoom:</strong> Use a roda do mouse</p>
            <p><strong>Mover elementos:</strong> Clique e arraste os elementos</p>
            <p><strong>Editar elementos:</strong> Duplo clique sobre o elemento</p>
            <p><strong>Atalhos:</strong></p>
            <p class="ml-2">• Setas para navegar</p>
            <p class="ml-2">• 'm' para mostrar/ocultar o minimap</p>
            <p class="ml-2">• 'r' para mostrar/ocultar réguas</p>
            <p class="ml-2">• 'c' para centralizar a visualização</p>
            <p class="ml-2">• 'h' para mostrar/ocultar estas dicas</p>
        </div>

        <!-- Botão de ajuda -->
        <button v-if="!mostrarDicas" @click="mostrarDicas = true" class="botao-ajuda"
            title="Mostrar dicas de navegação">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
        </button>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue';

// Estado do designer
const planta = reactive({
    campos: [],
    nome: "Planta do Viveiro",
    data: new Date().toISOString().slice(0, 10)
});

// Estado de interação global
const estadoInteracao = reactive({
    arrastando: false,
    elementoArrastando: false,
    fundoArrastando: false,
    zoomAtivo: true,
    panningAtivo: true
});

// Sistema de diagnóstico
const diagnostico = reactive({
    ativo: false,
    ultimaOperacao: '',
    problemasEncontrados: 0,
    log: []
});

// Opções de visualização
const zoom = ref(1);
const mostrarMinimap = ref(false);
const mostrarMarcadores = ref(false);
const mostrarDicas = ref(true); // Mostrar dicas por padrão ao abrir
const viewportWidth = ref(window.innerWidth);
const viewportHeight = ref(window.innerHeight);

const elementoSelecionado = ref(null);
const elementoEmDrag = ref(null);
const elementoPai = ref(null);
const elementoAvo = ref(null); // Para espaços de muda
const offsetDrag = ref({ x: 0, y: 0 });
const designerArea = ref(null);
const mostrarModal = ref(false);

// Alerta de exclusão
const alertaExclusao = reactive({
    mostrar: false,
    elemento: null,
    nome: ''
});

// Cores disponíveis para personalização
const cores = reactive({
    campo: ['#8cc63f', '#6bc473', '#4aba9c', '#39b0c4', '#4793e0'],
    canteiro: ['#6ca234', '#5d9b4c', '#4e9364', '#3f8b7c', '#2f8294'],
    espaco: ['#ffe135', '#ffc42e', '#ffab28', '#ff9321', '#ff7c1c']
});

// Cores disponíveis para o elemento selecionado
const coresDisponiveis = computed(() => {
    if (!elementoSelecionado.value) return [];

    if (elementoSelecionado.value.tipo === 'campo' ||
        elementoSelecionado.value.tipo === 'canteiro' ||
        elementoSelecionado.value.tipo === 'espaco') {
        return cores[elementoSelecionado.value.tipo];
    }

    // Cores padrão para outros tipos
    const corPadrao = {
        'sementeira': ['#ff9600', '#ffb347', '#ffc168', '#ffd084', '#ffe0a8'],
        'area-trabalho': ['#ffe135', '#ffe94f', '#fff066', '#fff588', '#fff8aa'],
        'estoque': ['#b4b4b4', '#c8c8c8', '#d4d4d4', '#e0e0e0', '#ebebeb']
    };

    return corPadrao[elementoSelecionado.value.tipo] || [];
});

// ViewBox responsivo
const viewBox = reactive({
    width: 800,  // Reduzido de 1000 para 800
    height: 600  // Reduzido de 800 para 600
});

// Posição de visualização (panning)
const viewPosition = reactive({
    x: 0,
    y: 0
});

// Ajusta o viewBox quando elementos são adicionados
const ajustarViewBox = () => {
    // Valores iniciais para campos
    let maxX = 400;  // Valor base ainda mais reduzido
    let maxY = 300;  // Valor base ainda mais reduzido

    // Encontra os valores máximos para X e Y
    planta.campos.forEach(campo => {
        const campoMaxX = campo.x + campo.largura + 30; // Margem ainda mais reduzida
        const campoMaxY = campo.y + campo.altura + 30;  // Margem ainda mais reduzida

        maxX = Math.max(maxX, campoMaxX);
        maxY = Math.max(maxY, campoMaxY);
    });

    // Ajusta o viewBox para incluir todos os elementos com margem mínima
    viewBox.width = maxX;
    viewBox.height = maxY;
};

// Função para centralizar a visualização
const centralizarVisualizacao = () => {
    // Calcular o centro dos elementos
    if (planta.campos.length === 0) {
        // Se não houver elementos, iniciar na origem
        viewPosition.x = 0;
        viewPosition.y = 0;
        return;
    }

    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;

    planta.campos.forEach(campo => {
        minX = Math.min(minX, campo.x);
        minY = Math.min(minY, campo.y);
        maxX = Math.max(maxX, campo.x + campo.largura);
        maxY = Math.max(maxY, campo.y + campo.altura);
    });

    // Garantir que minX e minY sejam pelo menos 0
    minX = Math.max(0, minX);
    minY = Math.max(0, minY);

    // Centralizar no container de visualização
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    // Ajustar posição de visualização (com pequeno ajuste para esquerda)
    viewPosition.x = -minX + 10; // Pequena margem à esquerda
    viewPosition.y = -minY + (viewportHeight.value / 4) / zoom.value; // Centralizar verticalmente com mais espaço acima
};

// Iniciar movimento de panning
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });

const iniciarPanning = (event) => {
    // Verificar se o panning está disponível
    if (!estadoInteracao.panningAtivo || estadoInteracao.arrastando) return;

    // Verificar se o clique foi em um elemento arrastável ou no fundo
    if (event.target.classList.contains('fundo-mapa')) {
        // Se for botão esquerdo no fundo, deixamos o iniciarDragFundo cuidar disso
        if (event.button === 0) {
            return;
        }
    }

    // Para elementos não-fundo, continuar permitindo o panning apenas com botão direito ou do meio
    if (event.button === 0) return;

    event.preventDefault();
    isPanning.value = true;
    estadoInteracao.arrastando = true;
    panStart.value = { x: event.clientX, y: event.clientY };

    document.addEventListener('mousemove', moverPanning);
    document.addEventListener('mouseup', finalizarPanning);
};

const moverPanning = (event) => {
    if (!isPanning.value) return;

    const dx = (event.clientX - panStart.value.x) / zoom.value;
    const dy = (event.clientY - panStart.value.y) / zoom.value;

    viewPosition.x += dx;
    viewPosition.y += dy;

    panStart.value = { x: event.clientX, y: event.clientY };
};

const finalizarPanning = () => {
    isPanning.value = false;
    document.removeEventListener('mousemove', moverPanning);
    document.removeEventListener('mouseup', finalizarPanning);

    // Resetar o estado de interação
    setTimeout(() => {
        estadoInteracao.arrastando = false;
    }, 50);
};

// Observa mudanças na planta para ajustar o viewBox
watch(() => planta.campos, () => {
    ajustarViewBox();
}, { deep: true });

// Variáveis para drag do modal
const modalDrag = ref(false);
const modalOffset = ref({ x: 0, y: 0 });
const modalPosition = ref({ x: 0, y: 0 });

// Funções auxiliares
const obterTituloModal = () => {
    if (!elementoSelecionado.value) return '';

    const tipos = {
        'campo': 'Área de Produção',
        'canteiro': 'Canteiro',
        'espaco': 'Espaço de Muda',
        'sementeira': 'Sementeira',
        'area-trabalho': 'Área de Trabalho',
        'estoque': 'Estoque de Substrato'
    };

    return `Editar ${tipos[elementoSelecionado.value.tipo] || elementoSelecionado.value.tipo}`;
};

const ajustarTamanho = (propriedade, valor) => {
    if (!elementoSelecionado.value) return;

    if (propriedade === 'raio') {
        elementoSelecionado.value.raio = Math.max(3, Math.min(20, elementoSelecionado.value[propriedade] + valor));
    } else {
        elementoSelecionado.value[propriedade] = Math.max(10, elementoSelecionado.value[propriedade] + valor);
    }
};

// Funções de manipulação de elementos
const adicionarCampo = () => {
    const novoCampo = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Nova Área de Produção',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };
    planta.campos.push(novoCampo);
    ajustarViewBox();
    selecionarElemento(novoCampo);

    // Centralize na nova área para melhor visualização
    setTimeout(() => {
        centralizarEmElemento(novoCampo);
    }, 100);
};

const adicionarCanteiro = () => {
    if (!elementoSelecionado.value || elementoSelecionado.value.tipo !== 'campo') {
        alert('Selecione uma área de produção para adicionar um canteiro');
        return;
    }

    const campo = elementoSelecionado.value;
    const novoCanteiro = {
        id: Date.now(),
        tipo: 'canteiro',
        nome: 'Novo Canteiro',
        x: 20,
        y: 20,
        largura: Math.min(80, campo.largura - 40),  // Reduzido para melhor visualização
        altura: Math.min(40, campo.altura - 40),    // Reduzido para melhor visualização
        cor: cores.canteiro[0],
        espacos: []
    };
    campo.canteiros.push(novoCanteiro);
    selecionarElemento(novoCanteiro);
};

const adicionarEspaco = () => {
    if (!elementoSelecionado.value || elementoSelecionado.value.tipo !== 'canteiro') {
        alert('Selecione um canteiro para adicionar um espaço de muda');
        return;
    }

    const canteiro = elementoSelecionado.value;
    const novoEspaco = {
        id: Date.now(),
        tipo: 'espaco',
        nome: 'Muda',
        x: canteiro.largura / 2,
        y: canteiro.altura / 2,
        raio: 5,
        cor: cores.espaco[0]
    };
    canteiro.espacos.push(novoEspaco);
    selecionarElemento(novoEspaco);
};

const adicionarSementeira = () => {
    const novaSementeira = {
        id: Date.now(),
        tipo: 'sementeira',
        nome: 'Nova Sementeira',
        x: 220,  // Posicionada mais próxima
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };
    planta.campos.push(novaSementeira);
    ajustarViewBox();
    selecionarElemento(novaSementeira);

    // Centralize na nova área
    setTimeout(() => {
        centralizarEmElemento(novaSementeira);
    }, 100);
};

const adicionarAreaTrabalho = () => {
    const novaAreaTrabalho = {
        id: Date.now(),
        tipo: 'area-trabalho',
        nome: 'Nova Área de Trabalho',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };
    planta.campos.push(novaAreaTrabalho);
    ajustarViewBox();
    selecionarElemento(novaAreaTrabalho);

    // Centralize na nova área
    setTimeout(() => {
        centralizarEmElemento(novaAreaTrabalho);
    }, 100);
};

const adicionarEstoque = () => {
    const novoEstoque = {
        id: Date.now(),
        tipo: 'estoque',
        nome: 'Novo Estoque de Substrato',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };
    planta.campos.push(novoEstoque);
    ajustarViewBox();
    selecionarElemento(novoEstoque);

    // Centralize no novo estoque
    setTimeout(() => {
        centralizarEmElemento(novoEstoque);
    }, 100);
};

// Nova função para centralizar visualização em um elemento específico
const centralizarEmElemento = (elemento) => {
    // Calcular o centro do elemento
    const centerX = elemento.x + elemento.largura / 2;
    const centerY = elemento.y + elemento.altura / 2;

    // Ajustar posição de visualização para centralizar o elemento
    viewPosition.x = -centerX + (viewportWidth.value / 2) / zoom.value;
    viewPosition.y = -centerY + (viewportHeight.value / 2) / zoom.value;
};

// Inicialização
onMounted(() => {
    // Atualizar dimensões da viewport ao iniciar
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    // Detectar dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        (window.innerWidth <= 768);

    // Definir posição inicial explicitamente para garantir que não haja espaço em branco
    viewPosition.x = 0;
    viewPosition.y = 0;

    if (planta.campos.length === 0) {
        // Em vez de adicionar um campo inicial, vamos criar um layout inicial completo
        criarLayoutInicial();

        // Aplicar zoom inicial adequado
        if (isMobile) {
            zoom.value = 0.6;
        } else {
            zoom.value = 1.0;
        }
    } else {
        // Para mapas existentes, apenas ajustar o viewBox
        ajustarViewBox();
    }

    // Adicionar eventos de teclado para controle de panning
    window.addEventListener('keydown', (event) => {
        // Se estiver com algum input focado, não processar atalhos
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        if (event.key === 'Escape') {
            // Se estiver arrastando algo, cancelar a operação
            if (estadoInteracao.arrastando) {
                resetAllInteractions();
            } else {
                // Se não estiver arrastando, comportamento normal (fechar modal, etc)
                fecharModal();
                elementoSelecionado.value = null;
                // Fechar também as dicas
                mostrarDicas.value = false;
            }
        } else if (event.key === 'c') {
            // Centralizar visualização apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                centralizarVisualizacao();
            }
        } else if (event.key === 'h') {
            // Mostrar/ocultar dicas de navegação
            if (!estadoInteracao.arrastando) {
                mostrarDicas.value = !mostrarDicas.value;
            }
        } else if (event.key === 'r') {
            // Mostrar/ocultar marcadores apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMarcadores.value = !mostrarMarcadores.value;
            }
        } else if (event.key === 'm') {
            // Mostrar/ocultar minimap apenas se não estiver em operação de arraste
            if (!estadoInteracao.arrastando) {
                mostrarMinimap.value = !mostrarMinimap.value;
            }
        }

        // Adiciona navegação com setas apenas se não estiver arrastando
        if (!estadoInteracao.arrastando) {
            handleKeyNavigation(event);
        }
    });

    // Adicionar evento de contexto para permitir panning com botão direito
    designerArea.value.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });

    // Ajustes adicionais para dispositivos móveis
    if (isMobile) {
        // Ajustar tamanho inicial de zoom
        zoom.value = 0.6;

        // Diminuir os tamanhos dos elementos do layout inicial para melhor visualização
        const scaleElements = () => {
            planta.campos.forEach(elemento => {
                if (elemento.tipo === 'campo') {
                    // Não diminuir muito os campos de produção
                } else {
                    // Diminuir outros elementos para melhor visualização em telas pequenas
                    elemento.largura = Math.max(100, elemento.largura * 0.8);
                    elemento.altura = Math.max(60, elemento.altura * 0.8);
                }
            });
        };

        // Aplicar após um pequeno atraso para garantir que o layout inicial esteja pronto
        setTimeout(scaleElements, 100);
    }

    // Atualizar dimensões da viewport quando a janela for redimensionada
    window.addEventListener('resize', () => {
        viewportWidth.value = window.innerWidth;
        viewportHeight.value = window.innerHeight;
    });

    // Esconder as dicas após 15 segundos com uma transição suave
    setTimeout(() => {
        dicasFadeOut.value = true;

        // Após a animação terminar, realmente escondemos o elemento
        setTimeout(() => {
            mostrarDicas.value = false;
            dicasFadeOut.value = false; // Resetar para próxima vez
        }, 1000); // 1 segundo para a animação de fade out
    }, 15000); // 15 segundos para exibição das dicas

    // Adicionar evento para detectar cliques fora de elementos e reiniciar estados se necessário
    document.addEventListener('mousedown', (event) => {
        // Se clicar fora dos elementos principais, verificar se deve resetar estados
        const clickInsideDesigner = designerArea.value && designerArea.value.contains(event.target);
        const clickInsideModal = document.querySelector('.modal-edicao') &&
            document.querySelector('.modal-edicao').contains(event.target);
        const clickInsideDicas = document.querySelector('.dicas-navegacao') &&
            document.querySelector('.dicas-navegacao').contains(event.target);

        // Se clicar fora de tudo e estiver arrastando, cancelar a operação
        if (!clickInsideDesigner && !clickInsideModal && !clickInsideDicas && estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para perda de foco da janela
    window.addEventListener('blur', () => {
        // Se o usuário mudar de janela enquanto estiver arrastando, cancelar a operação
        if (estadoInteracao.arrastando) {
            resetAllInteractions();
        }
    });

    // Adicionar manipulador para quando o usuário sair da página
    window.addEventListener('beforeunload', () => {
        // Limpar todos os listeners antes de sair
        resetAllInteractions();
    });

    // Iniciar diagnóstico em modo de desenvolvimento
    if (process.env.NODE_ENV === 'development') {
        diagnostico.ativo = true;
        console.log('Modo de diagnóstico ativado no ViveiroDesigner');

        // Verificação periódica de estados inconsistentes
        const intervaloDiagnostico = setInterval(() => {
            if (estadoInteracao.arrastando) {
                // Verificar se o estado de arraste está ativo há muito tempo (mais de 30 segundos)
                const ultimoEvento = diagnostico.log[diagnostico.log.length - 1];
                if (ultimoEvento && Date.now() - new Date(ultimoEvento.timestamp).getTime() > 30000) {
                    console.warn('Estado de arraste ativo por mais de 30 segundos, resetando');
                    resetAllInteractions();
                }
            }
        }, 10000);

        // Limpar intervalo ao desmontar
        return () => {
            clearInterval(intervaloDiagnostico);
        };
    }
});

// Função para criar um layout inicial mais estruturado
const criarLayoutInicial = () => {
    // Área de produção principal (ainda mais próxima da origem)
    const areaProducao = {
        id: Date.now(),
        tipo: 'campo',
        nome: 'Área de Produção Principal',
        x: 10,  // Ainda mais próximo da origem
        y: 10,  // Ainda mais próximo da origem
        largura: 180,
        altura: 130,
        cor: cores.campo[0],
        canteiros: []
    };

    // Adicionar alguns canteiros na área de produção
    const canteiro1 = {
        id: Date.now() + 1,
        tipo: 'canteiro',
        nome: 'Canteiro 1',
        x: 15,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[0],
        espacos: []
    };

    const canteiro2 = {
        id: Date.now() + 2,
        tipo: 'canteiro',
        nome: 'Canteiro 2',
        x: 105,
        y: 15,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[1],
        espacos: []
    };

    const canteiro3 = {
        id: Date.now() + 3,
        tipo: 'canteiro',
        nome: 'Canteiro 3',
        x: 15,
        y: 70,
        largura: 60,  // Reduzido de 70 para 60
        altura: 35,   // Reduzido de 40 para 35
        cor: cores.canteiro[2],
        espacos: []
    };

    // Adicionar alguns espaços no canteiro 1
    const espaco1 = {
        id: Date.now() + 4,
        tipo: 'espaco',
        nome: 'Muda 1',
        x: 15,
        y: 17,
        raio: 5,
        cor: cores.espaco[0]
    };

    const espaco2 = {
        id: Date.now() + 5,
        tipo: 'espaco',
        nome: 'Muda 2',
        x: 30,
        y: 17,
        raio: 5,
        cor: cores.espaco[1]
    };

    const espaco3 = {
        id: Date.now() + 6,
        tipo: 'espaco',
        nome: 'Muda 3',
        x: 45,
        y: 17,
        raio: 5,
        cor: cores.espaco[2]
    };

    canteiro1.espacos.push(espaco1, espaco2, espaco3);
    areaProducao.canteiros.push(canteiro1, canteiro2, canteiro3);

    // Adicionar uma sementeira
    const sementeira = {
        id: Date.now() + 7,
        tipo: 'sementeira',
        nome: 'Sementeira 1',
        x: 220,  // Posicionada mais próximo
        y: 10,   // Ainda mais próximo da origem
        largura: 130,
        altura: 70,
        cor: '#ff9600'
    };

    // Adicionar uma área de trabalho
    const areaTrabalho = {
        id: Date.now() + 8,
        tipo: 'area-trabalho',
        nome: 'Área de Trabalho 1',
        x: 10,   // Ainda mais próximo da origem
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#ffe135'
    };

    // Adicionar um estoque
    const estoque = {
        id: Date.now() + 9,
        tipo: 'estoque',
        nome: 'Estoque de Substrato 1',
        x: 220,  // Posicionado mais próximo
        y: 160,  // Mais próximo para evitar espaço em branco
        largura: 130,
        altura: 70,
        cor: '#b4b4b4'
    };

    // Adicionar todos os elementos à planta
    planta.campos.push(areaProducao, sementeira, areaTrabalho, estoque);

    // Ajustar o viewBox para mostrar todos os elementos
    ajustarViewBox();

    // Definir um zoom inicial adequado (reduzido para mostrar melhor)
    zoom.value = 1.0;

    // Centralizar a visualização
    centralizarVisualizacao();
};

// Funções de interação
const handleZoom = (event) => {
    // Verificar se o zoom está ativo
    if (!estadoInteracao.zoomAtivo || estadoInteracao.arrastando) return;

    event.preventDefault();
    const delta = event.deltaY;

    // Obter a posição do mouse em relação ao SVG antes do zoom
    const rect = designerArea.value.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    // Converter para coordenadas do mundo
    const worldX = (mouseX / zoom.value) - viewPosition.x;
    const worldY = (mouseY / zoom.value) - viewPosition.y;

    // Aplicar zoom
    const oldZoom = zoom.value;
    if (delta > 0) {
        zoom.value = Math.max(0.2, zoom.value - 0.1);
    } else {
        zoom.value = Math.min(3, zoom.value + 0.1);
    }

    // Ajustar a posição para manter o ponto sob o mouse
    viewPosition.x = -(worldX - (mouseX / zoom.value));
    viewPosition.y = -(worldY - (mouseY / zoom.value));
};

// Função auxiliar para obter coordenadas SVG a partir de um evento de mouse
const getSVGCoordinates = (event) => {
    if (!designerArea.value) return { x: 0, y: 0 };

    const svg = designerArea.value.querySelector('svg');
    if (!svg) return { x: 0, y: 0 };

    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;

    // Aplicar a transformação inversa considerando o zoom e pan atuais
    const matrix = svg.getScreenCTM().inverse();
    return point.matrixTransform(matrix);
};

// Recuperar eventos ao clicar fora ou cancelar uma operação
const resetAllInteractions = () => {
    // Registrar diagnóstico
    registrarEvento('resetAllInteractions');

    // Função para resetar todos os estados de interação e event listeners
    estadoInteracao.arrastando = false;
    estadoInteracao.elementoArrastando = false;
    estadoInteracao.fundoArrastando = false;
    estadoInteracao.zoomAtivo = true;
    estadoInteracao.panningAtivo = true;

    elementoEmDrag.value = null;
    elementoPai.value = null;
    elementoAvo.value = null;
    isPanning.value = false;
    isDraggingFundo.value = false;

    // Remover todos os event listeners possíveis
    document.removeEventListener('mousemove', moverElementoMapa);
    document.removeEventListener('mousemove', moverFundo);
    document.removeEventListener('mousemove', moverPanning);
    document.removeEventListener('mouseup', finalizarDragMapa);
    document.removeEventListener('mouseup', finalizarDragFundo);
    document.removeEventListener('mouseup', finalizarPanning);

    // Remover qualquer event listeners adicional que possa existir no document
    const oldListeners = window.getEventListeners ? window.getEventListeners(document) : null;
    if (oldListeners && oldListeners.mousemove) {
        oldListeners.mousemove.forEach(listener => {
            document.removeEventListener('mousemove', listener.listener);
        });
    }
    if (oldListeners && oldListeners.mouseup) {
        oldListeners.mouseup.forEach(listener => {
            document.removeEventListener('mouseup', listener.listener);
        });
    }

    // Restaurar o cursor
    document.body.style.cursor = 'default';
};

// Funções de drag dos elementos do mapa
const iniciarDragMapa = (event, elemento, pai = null, avo = null) => {
    // Registrar diagnóstico
    registrarEvento('iniciarDragMapa', { elementoTipo: elemento.tipo, elementoId: elemento.id });

    // Se já estiver em alguma operação de arraste, não iniciar outra
    if (estadoInteracao.arrastando) return;

    event.preventDefault();
    event.stopPropagation();

    estadoInteracao.arrastando = true;
    estadoInteracao.elementoArrastando = true;
    estadoInteracao.zoomAtivo = false;

    elementoEmDrag.value = elemento;
    elementoPai.value = pai;
    elementoAvo.value = avo;

    // Usar a função centralizada para obter coordenadas
    const svgPoint = getSVGCoordinates(event);

    // Ajustar o offset baseado na posição atual de visualização
    if (elemento.tipo === 'espaco') {
        offsetDrag.value = {
            x: svgPoint.x - (pai ? pai.x + elemento.x : elemento.x),
            y: svgPoint.y - (pai ? pai.y + elemento.y : elemento.y)
        };
    } else {
        offsetDrag.value = {
            x: svgPoint.x - elemento.x,
            y: svgPoint.y - elemento.y
        };
    }

    // Alterar o cursor para indicar que está arrastando
    document.body.style.cursor = 'grabbing';

    document.addEventListener('mousemove', moverElementoMapa);
    document.addEventListener('mouseup', finalizarDragMapa);

    // Adicionar um evento de escape para cancelar o drag
    const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
            document.removeEventListener('keydown', handleKeyDown);
            resetAllInteractions();
        }
    };
    document.addEventListener('keydown', handleKeyDown);
};

// Adicionar um timeout de segurança para moverElementoMapa
let ultimoMovimento = 0;
const moverElementoMapa = (event) => {
    if (!elementoEmDrag.value || !estadoInteracao.elementoArrastando) return;

    // Otimização: limitar a taxa de atualização para melhor desempenho
    const agora = Date.now();
    if (agora - ultimoMovimento < 16) return; // ~60fps
    ultimoMovimento = agora;

    // Usar a função centralizada para obter coordenadas
    const svgPoint = getSVGCoordinates(event);

    // Detectar se é um campo (Área de Produção)
    const ehCampo = elementoEmDrag.value.tipo === 'campo';

    // Tratamento comum para todos os elementos
    if (elementoEmDrag.value.tipo === 'espaco') {
        // Código para espaços
        const x = svgPoint.x - offsetDrag.value.x;
        const y = svgPoint.y - offsetDrag.value.y;

        if (elementoPai.value) {
            const raio = elementoEmDrag.value.raio || 5;
            const maxX = elementoPai.value.largura - raio;
            const maxY = elementoPai.value.altura - raio;

            elementoEmDrag.value.x = Math.max(raio, Math.min(x, maxX));
            elementoEmDrag.value.y = Math.max(raio, Math.min(y, maxY));
        } else {
            elementoEmDrag.value.x = Math.max(0, x);
            elementoEmDrag.value.y = Math.max(0, y);
        }
    } else {
        // Código para retângulos (campos e canteiros)
        const x = svgPoint.x - offsetDrag.value.x;
        const y = svgPoint.y - offsetDrag.value.y;

        if (elementoPai.value) {
            const maxX = elementoPai.value.largura - elementoEmDrag.value.largura;
            const maxY = elementoPai.value.altura - elementoEmDrag.value.altura;

            elementoEmDrag.value.x = Math.max(0, Math.min(x, maxX));
            elementoEmDrag.value.y = Math.max(0, Math.min(y, maxY));
        } else {
            // Limitação adicional de movimento para campos para evitar problemas
            if (ehCampo) {
                // Permitir movimento limitado para áreas de produção para evitar bugs
                elementoEmDrag.value.x = Math.max(0, Math.min(x, viewBox.width - elementoEmDrag.value.largura));
                elementoEmDrag.value.y = Math.max(0, Math.min(y, viewBox.height - elementoEmDrag.value.altura));
            } else {
                elementoEmDrag.value.x = Math.max(0, x);
                elementoEmDrag.value.y = Math.max(0, y);
            }
        }
    }
};

const finalizarDragMapa = () => {
    // Registrar diagnóstico
    registrarEvento('finalizarDragMapa');

    // Verificar se estávamos arrastando um elemento pai (campo)
    const eraCampo = elementoEmDrag.value && elementoEmDrag.value.tipo === 'campo';

    elementoEmDrag.value = null;
    elementoPai.value = null;
    elementoAvo.value = null;
    document.removeEventListener('mousemove', moverElementoMapa);
    document.removeEventListener('mouseup', finalizarDragMapa);

    // Restaurar o cursor para o padrão
    document.body.style.cursor = 'default';

    // Resetar estados de interação com pequeno atraso para evitar conflitos
    // Atrasar mais se era um campo para garantir que a UI e os eventos estejam estáveis
    const atraso = eraCampo ? 100 : 50;

    setTimeout(() => {
        estadoInteracao.arrastando = false;
        estadoInteracao.elementoArrastando = false;
        estadoInteracao.zoomAtivo = true;

        // Para campos, garantir que todos os listeners estejam limpos
        if (eraCampo) {
            // Verificação adicional para garantir que não há listeners residuais
            document.removeEventListener('mousemove', moverElementoMapa);
            document.removeEventListener('mouseup', finalizarDragMapa);
            document.body.style.cursor = 'default';
        }
    }, atraso);
};

// Funções de drag do modal
const iniciarDragModal = (event) => {
    modalDrag.value = true;
    const modal = event.target.closest('.modal-edicao');
    const rect = modal.getBoundingClientRect();

    modalOffset.value = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    };

    document.addEventListener('mousemove', moverModal);
    document.addEventListener('mouseup', finalizarDragModal);
};

const moverModal = (event) => {
    if (!modalDrag.value) return;

    const modal = document.querySelector('.modal-edicao');
    if (!modal) return;

    const x = event.clientX - modalOffset.value.x;
    const y = event.clientY - modalOffset.value.y;

    // Limites para manter o modal visível na tela
    const maxX = window.innerWidth - 100;
    const maxY = window.innerHeight - 100;

    modalPosition.value = {
        x: Math.max(0, Math.min(x, maxX)),
        y: Math.max(0, Math.min(y, maxY))
    };
};

const finalizarDragModal = () => {
    modalDrag.value = false;
    document.removeEventListener('mousemove', moverModal);
    document.removeEventListener('mouseup', finalizarDragModal);
};

const selecionarElemento = (elemento) => {
    elementoSelecionado.value = elemento;
    mostrarModal.value = false;

    // Animar suavemente para centralizar no elemento selecionado
    animarCentralizacao(elemento);
};

// Nova função para animar a centralização de um elemento
const animarCentralizacao = (elemento) => {
    if (!elemento) return;

    // Obter posição atual
    const posAtual = { ...viewPosition.value };

    // Calcular posição alvo (centro do elemento)
    let centerX, centerY;

    if (elemento.tipo === 'espaco') {
        // Para espaços, encontrar o canteiro e campo pai
        const canteiro = encontrarCanteiroDeEspaco(elemento);
        const campo = encontrarCampoDeElemento(canteiro || elemento);

        if (canteiro && campo) {
            centerX = campo.x + canteiro.x + elemento.x;
            centerY = campo.y + canteiro.y + elemento.y;
        } else if (campo) {
            centerX = campo.x + elemento.x;
            centerY = campo.y + elemento.y;
        } else {
            centerX = elemento.x;
            centerY = elemento.y;
        }
    } else if (elemento.tipo === 'canteiro') {
        // Para canteiros, encontrar o campo pai
        const campo = encontrarCampoDeElemento(elemento);

        if (campo) {
            centerX = campo.x + elemento.x + elemento.largura / 2;
            centerY = campo.y + elemento.y + elemento.altura / 2;
        } else {
            centerX = elemento.x + elemento.largura / 2;
            centerY = elemento.y + elemento.altura / 2;
        }
    } else {
        // Para campos e outros elementos principais
        centerX = elemento.x + elemento.largura / 2;
        centerY = elemento.y + elemento.altura / 2;
    }

    // Calcular posição final para centralizar o elemento
    const posAlvo = {
        x: -centerX + (viewportWidth.value / 2) / zoom.value,
        y: -centerY + (viewportHeight.value / 2) / zoom.value
    };

    // Definir a duração da animação
    const duracao = 300; // milissegundos
    const inicio = Date.now();

    // Função para animar o movimento
    const animar = () => {
        const tempoDecorrido = Date.now() - inicio;
        const progresso = Math.min(tempoDecorrido / duracao, 1);

        // Função de easing para movimento suave
        const easeOutCubic = (x) => 1 - Math.pow(1 - x, 3);
        const fatorEasing = easeOutCubic(progresso);

        // Interpolar entre posição atual e alvo
        viewPosition.x = posAtual.x + (posAlvo.x - posAtual.x) * fatorEasing;
        viewPosition.y = posAtual.y + (posAlvo.y - posAtual.y) * fatorEasing;

        if (progresso < 1) {
            requestAnimationFrame(animar);
        }
    };

    // Iniciar animação
    animar();
};

// Funções auxiliares para encontrar relacionamentos entre elementos
const encontrarCampoDeElemento = (elemento) => {
    if (!elemento) return null;

    // Se o elemento já for um campo ou outro elemento principal, retornar null
    if (elemento.tipo === 'campo' || elemento.tipo === 'sementeira' ||
        elemento.tipo === 'area-trabalho' || elemento.tipo === 'estoque') {
        return null;
    }

    // Procurar o campo pai
    return planta.campos.find(campo =>
        campo.canteiros && campo.canteiros.some(c => c.id === elemento.id));
};

const encontrarCanteiroDeEspaco = (espaco) => {
    if (!espaco || espaco.tipo !== 'espaco') return null;

    // Procurar em todos os campos
    for (const campo of planta.campos) {
        if (!campo.canteiros) continue;

        // Procurar em todos os canteiros deste campo
        for (const canteiro of campo.canteiros) {
            if (canteiro.espacos && canteiro.espacos.some(e => e.id === espaco.id)) {
                return canteiro;
            }
        }
    }

    return null;
};

const handleDblClick = (evento, elemento) => {
    elementoSelecionado.value = { ...elemento };
    mostrarModal.value = true;

    // Posiciona o modal próximo à posição do mouse
    const modalWidth = 320;
    const modalHeight = 450;

    // Usa a posição do evento (mouse) como referência
    const x = evento.clientX;
    const y = evento.clientY;

    // Ajusta a posição para garantir que o modal fique dentro da tela
    modalPosition.value = {
        x: Math.min(Math.max(10, x), window.innerWidth - modalWidth - 10),
        y: Math.min(Math.max(10, y), window.innerHeight - modalHeight - 10)
    };

    // Destaca visualmente o elemento selecionado com uma animação suave
    setTimeout(() => {
        const elementoNode = evento.currentTarget;
        if (elementoNode) {
            // Aplicar e remover classe para criar efeito de pulso
            elementoNode.classList.add('pulse-animation');
            setTimeout(() => {
                elementoNode.classList.remove('pulse-animation');
            }, 300);
        }
    }, 0);
};

const fecharModal = () => {
    mostrarModal.value = false;
    elementoSelecionado.value = null;
};

const excluirElemento = () => {
    if (!elementoSelecionado.value) return;

    const elemento = elementoSelecionado.value;
    alertaExclusao.elemento = elemento;
    alertaExclusao.nome = `${elemento.nome} (${obterTituloModal().replace('Editar ', '')})`;
    alertaExclusao.mostrar = true;
};

const confirmarExclusao = () => {
    const elemento = alertaExclusao.elemento;

    if (elemento.tipo === 'campo' || elemento.tipo === 'sementeira' ||
        elemento.tipo === 'area-trabalho' || elemento.tipo === 'estoque') {
        const index = planta.campos.findIndex(c => c.id === elemento.id);
        if (index !== -1) planta.campos.splice(index, 1);
    } else if (elemento.tipo === 'canteiro') {
        const campo = planta.campos.find(c => c.canteiros && c.canteiros.some(ct => ct.id === elemento.id));
        if (campo) {
            const index = campo.canteiros.findIndex(ct => ct.id === elemento.id);
            if (index !== -1) campo.canteiros.splice(index, 1);
        }
    } else if (elemento.tipo === 'espaco') {
        const campo = planta.campos.find(c =>
            c.canteiros && c.canteiros.some(ct =>
                ct.espacos && ct.espacos.some(e => e.id === elemento.id)
            )
        );

        if (campo) {
            const canteiro = campo.canteiros.find(ct =>
                ct.espacos && ct.espacos.some(e => e.id === elemento.id)
            );

            if (canteiro) {
                const index = canteiro.espacos.findIndex(e => e.id === elemento.id);
                if (index !== -1) canteiro.espacos.splice(index, 1);
            }
        }
    }

    alertaExclusao.mostrar = false;
    elementoSelecionado.value = null;
};

const duplicarElemento = () => {
    if (!elementoSelecionado.value) return;

    const elemento = elementoSelecionado.value;
    const copia = JSON.parse(JSON.stringify(elemento));
    copia.id = Date.now();
    copia.nome = `${elemento.nome} (Cópia)`;

    // Ajusta a posição da cópia
    copia.x += 20;
    copia.y += 20;

    if (elemento.tipo === 'campo' || elemento.tipo === 'sementeira' ||
        elemento.tipo === 'area-trabalho' || elemento.tipo === 'estoque') {
        planta.campos.push(copia);
    } else if (elemento.tipo === 'canteiro') {
        const campo = planta.campos.find(c => c.canteiros && c.canteiros.some(ct => ct.id === elemento.id));
        if (campo) {
            // Verificar limites do campo
            copia.x = Math.min(copia.x, campo.largura - copia.largura);
            copia.y = Math.min(copia.y, campo.altura - copia.altura);
            campo.canteiros.push(copia);
        }
    } else if (elemento.tipo === 'espaco') {
        const campo = planta.campos.find(c =>
            c.canteiros && c.canteiros.some(ct =>
                ct.espacos && ct.espacos.some(e => e.id === elemento.id)
            )
        );

        if (campo) {
            const canteiro = campo.canteiros.find(ct =>
                ct.espacos && ct.espacos.some(e => e.id === elemento.id)
            );

            if (canteiro) {
                // Verificar limites do canteiro
                copia.x = Math.min(copia.x, canteiro.largura - copia.raio);
                copia.y = Math.min(copia.y, canteiro.altura - copia.raio);
                canteiro.espacos.push(copia);
            }
        }
    }

    elementoSelecionado.value = copia;
};

const salvarEdicao = () => {
    // Encontra o elemento original e atualiza suas propriedades
    if (!elementoSelecionado.value) return;

    const elemento = elementoSelecionado.value;

    if (elemento.tipo === 'campo' || elemento.tipo === 'sementeira' ||
        elemento.tipo === 'area-trabalho' || elemento.tipo === 'estoque') {
        const index = planta.campos.findIndex(c => c.id === elemento.id);
        if (index !== -1) {
            // Atualizando cor e outras propriedades
            planta.campos[index].nome = elemento.nome;
            planta.campos[index].largura = elemento.largura;
            planta.campos[index].altura = elemento.altura;
            planta.campos[index].cor = elemento.cor;
        }
    } else if (elemento.tipo === 'canteiro') {
        const campo = planta.campos.find(c => c.canteiros && c.canteiros.some(ct => ct.id === elemento.id));
        if (campo) {
            const index = campo.canteiros.findIndex(ct => ct.id === elemento.id);
            if (index !== -1) {
                campo.canteiros[index].nome = elemento.nome;
                campo.canteiros[index].largura = elemento.largura;
                campo.canteiros[index].altura = elemento.altura;
                campo.canteiros[index].cor = elemento.cor;
            }
        }
    } else if (elemento.tipo === 'espaco') {
        const campo = planta.campos.find(c =>
            c.canteiros && c.canteiros.some(ct =>
                ct.espacos && ct.espacos.some(e => e.id === elemento.id)
            )
        );

        if (campo) {
            const canteiro = campo.canteiros.find(ct =>
                ct.espacos && ct.espacos.some(e => e.id === elemento.id)
            );

            if (canteiro) {
                const index = canteiro.espacos.findIndex(e => e.id === elemento.id);
                if (index !== -1) {
                    canteiro.espacos[index].nome = elemento.nome;
                    canteiro.espacos[index].raio = elemento.raio;
                    canteiro.espacos[index].cor = elemento.cor;
                }
            }
        }
    }

    mostrarModal.value = false;
};

const importarPlanta = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';

    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const importado = JSON.parse(event.target.result);

                // Verifica se o formato é válido
                if (importado && importado.campos) {
                    Object.assign(planta, importado);
                    ajustarViewBox();
                } else {
                    alert('Formato de arquivo inválido');
                }
            } catch (error) {
                alert(`Erro ao importar: ${error.message}`);
            }
        };
        reader.readAsText(file);
    };

    input.click();
};

const exportarPlanta = () => {
    const json = JSON.stringify(planta, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `planta-viveiro-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
};

const exportarImagem = () => {
    // Criar um SVG temporário que contém apenas os elementos do mapa, sem interfaces
    const svgTemp = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svgTemp.setAttribute('xmlns', 'http://www.w3.org/2000/svg');

    // Definir o tamanho baseado no viewBox
    svgTemp.setAttribute('width', viewBox.width);
    svgTemp.setAttribute('height', viewBox.height);
    svgTemp.setAttribute('viewBox', `0 0 ${viewBox.width} ${viewBox.height}`);

    // Adicionar estilo de fundo
    const style = document.createElementNS('http://www.w3.org/2000/svg', 'style');
    style.textContent = `
        .elemento { stroke-width: 2; }
        .campo { fill-opacity: 0.7; }
        .canteiro { fill-opacity: 0.7; }
        .espaco { fill-opacity: 0.85; }
        .sementeira { fill-opacity: 0.7; }
        .area-trabalho { fill-opacity: 0.7; }
        .estoque { fill-opacity: 0.7; }
        .elemento-texto { 
            font-family: sans-serif; 
            font-size: 12px; 
            font-weight: 500;
            fill: white;
            text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.5);
        }
        .texto-escuro {
            fill: #333;
            text-shadow: 0px 1px 2px rgba(255, 255, 255, 0.5);
        }
        .texto-pequeno {
            font-size: 10px;
        }
    `;
    svgTemp.appendChild(style);

    // Adicionar o fundo branco
    const background = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    background.setAttribute('width', viewBox.width);
    background.setAttribute('height', viewBox.height);
    background.setAttribute('fill', 'white');
    svgTemp.appendChild(background);

    // Adicionar grade de fundo
    const defsElement = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const patternElement = document.createElementNS('http://www.w3.org/2000/svg', 'pattern');
    patternElement.setAttribute('id', 'grid');
    patternElement.setAttribute('width', '20');
    patternElement.setAttribute('height', '20');
    patternElement.setAttribute('patternUnits', 'userSpaceOnUse');

    const gridPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    gridPath.setAttribute('d', 'M 20 0 L 0 0 0 20');
    gridPath.setAttribute('fill', 'none');
    gridPath.setAttribute('stroke', '#eaeaea');
    gridPath.setAttribute('stroke-width', '0.5');

    patternElement.appendChild(gridPath);
    defsElement.appendChild(patternElement);
    svgTemp.appendChild(defsElement);

    const gridRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    gridRect.setAttribute('width', viewBox.width);
    gridRect.setAttribute('height', viewBox.height);
    gridRect.setAttribute('fill', 'url(#grid)');
    svgTemp.appendChild(gridRect);

    // Clonar todos os elementos do mapa
    const desenhoOriginal = designerArea.value.querySelector('.designer-svg');
    const grupos = desenhoOriginal.querySelectorAll('g > g');

    grupos.forEach(grupo => {
        const clone = grupo.cloneNode(true);
        svgTemp.appendChild(clone);
    });

    // Adicionar título
    const titulo = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    titulo.setAttribute('x', '20');
    titulo.setAttribute('y', '30');
    titulo.setAttribute('font-family', 'sans-serif');
    titulo.setAttribute('font-size', '20');
    titulo.setAttribute('font-weight', 'bold');
    titulo.setAttribute('fill', '#333');
    titulo.textContent = planta.nome;
    svgTemp.appendChild(titulo);

    // Converter SVG para string
    const svgData = new XMLSerializer().serializeToString(svgTemp);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);

    // Criar imagem a partir do SVG
    const img = new Image();
    img.onload = () => {
        // Criar canvas para converter em PNG
        const canvas = document.createElement('canvas');
        canvas.width = viewBox.width;
        canvas.height = viewBox.height;

        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);

        // Converter canvas para PNG e fazer download
        const pngUrl = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = pngUrl;
        a.download = `mapa-viveiro-${new Date().toISOString().slice(0, 10)}.png`;
        a.click();

        // Limpar recursos
        URL.revokeObjectURL(url);
    };

    img.src = url;
};

// Adicione a nova função de salvar e voltar
const salvarEVoltar = () => {
    // Em um cenário real, você salvaria os dados no back-end aqui
    console.log('Salvando planta do viveiro:', planta);

    // Aqui você pode adicionar a navegação para voltar para a página anterior
    // Se estiver usando Vue Router:
    // router.push('/viveiros');

    // Emite um evento para o componente pai saber que deve voltar
    emit('voltar');
};

// Adicione emit para os eventos
const emit = defineEmits(['voltar']);

// Adicionando navegação com teclado para panning
const handleKeyNavigation = (event) => {
    const step = 20 / zoom.value; // Ajustar o passo baseado no zoom

    switch (event.key) {
        case 'ArrowLeft':
            viewPosition.x += step;
            event.preventDefault();
            break;
        case 'ArrowRight':
            viewPosition.x -= step;
            event.preventDefault();
            break;
        case 'ArrowUp':
            viewPosition.y += step;
            event.preventDefault();
            break;
        case 'ArrowDown':
            viewPosition.y -= step;
            event.preventDefault();
            break;
        case 'm':
            mostrarMinimap.value = !mostrarMinimap.value;
            event.preventDefault();
            break;
        case 'r':
            mostrarMarcadores.value = !mostrarMarcadores.value;
            event.preventDefault();
            break;
        case 'h':
            // Alternar visibilidade das dicas
            if (mostrarDicas.value) {
                // Se as dicas estão visíveis, começar a animação de fade out
                dicasFadeOut.value = true;
                setTimeout(() => {
                    mostrarDicas.value = false;
                    dicasFadeOut.value = false; // Resetar para próxima vez
                }, 1000);
            } else {
                // Se as dicas estão invisíveis, mostrar imediatamente
                mostrarDicas.value = true;
                dicasFadeOut.value = false;
            }
            event.preventDefault();
            break;
    }
};

// Navegação via minimap
const iniciarNavegacaoMinimap = (event) => {
    const minimap = event.currentTarget;
    const rect = minimap.getBoundingClientRect();

    // Calcular a posição relativa ao minimap
    const relX = event.clientX - rect.left;
    const relY = event.clientY - rect.top;

    // Converter para coordenadas do mundo
    const worldX = (relX / rect.width) * viewBox.width;
    const worldY = (relY / rect.height) * viewBox.height;

    // Centralizar a visualização neste ponto
    viewPosition.x = -worldX + (viewportWidth.value / 2) / zoom.value;
    viewPosition.y = -worldY + (viewportHeight.value / 2) / zoom.value;

    // Manter o evento ativo para arrastar
    document.addEventListener('mousemove', moverNavegacaoMinimap);
    document.addEventListener('mouseup', finalizarNavegacaoMinimap);
};

const moverNavegacaoMinimap = (event) => {
    const minimap = document.querySelector('.minimap-content');
    if (!minimap) return;

    const rect = minimap.getBoundingClientRect();

    // Calcular a posição relativa ao minimap
    const relX = Math.max(0, Math.min(event.clientX - rect.left, rect.width));
    const relY = Math.max(0, Math.min(event.clientY - rect.top, rect.height));

    // Converter para coordenadas do mundo
    const worldX = (relX / rect.width) * viewBox.width;
    const worldY = (relY / rect.height) * viewBox.height;

    // Centralizar a visualização neste ponto
    viewPosition.x = -worldX + (viewportWidth.value / 2) / zoom.value;
    viewPosition.y = -worldY + (viewportHeight.value / 2) / zoom.value;
};

const finalizarNavegacaoMinimap = () => {
    document.removeEventListener('mousemove', moverNavegacaoMinimap);
    document.removeEventListener('mouseup', finalizarNavegacaoMinimap);
};

// Variáveis para suporte a touch
const touchStartDistance = ref(0);
const touchStartZoom = ref(1);
const touchStartPosition = ref({ x: 0, y: 0 });
const touchLastPosition = ref({ x: 0, y: 0 });
const isTouchPanning = ref(false);
const isTouchZooming = ref(false);

// Funções de suporte a touch
const iniciarTouchPanning = (event) => {
    if (event.target.closest('.modal-edicao') || event.target.closest('.dicas-navegacao') ||
        event.target.closest('.botao-ajuda') || event.target.closest('.minimap')) {
        // Não iniciar panning se estiver tocando em elementos de interface
        return;
    }

    if (event.touches.length === 1) {
        // Single touch para panning
        isTouchPanning.value = true;
        isTouchZooming.value = false;

        const touch = event.touches[0];
        touchStartPosition.value = { x: touch.clientX, y: touch.clientY };
        touchLastPosition.value = { x: touch.clientX, y: touch.clientY };
    } else if (event.touches.length === 2) {
        // Multi-touch para zoom
        isTouchPanning.value = false;
        isTouchZooming.value = true;

        // Calcular a distância inicial entre dois toques
        const touch1 = event.touches[0];
        const touch2 = event.touches[1];
        touchStartDistance.value = Math.hypot(
            touch2.clientX - touch1.clientX,
            touch2.clientY - touch1.clientY
        );
        touchStartZoom.value = zoom.value;

        // Salvar o ponto médio como referência
        touchStartPosition.value = {
            x: (touch1.clientX + touch2.clientX) / 2,
            y: (touch1.clientY + touch2.clientY) / 2
        };
        touchLastPosition.value = { ...touchStartPosition.value };
    }
};

const moverTouchPanning = (event) => {
    if (isTouchPanning.value && event.touches.length === 1) {
        // Single touch panning
        const touch = event.touches[0];
        const dx = (touch.clientX - touchLastPosition.value.x) / zoom.value;
        const dy = (touch.clientY - touchLastPosition.value.y) / zoom.value;

        viewPosition.x += dx;
        viewPosition.y += dy;

        touchLastPosition.value = { x: touch.clientX, y: touch.clientY };
    } else if (isTouchZooming.value && event.touches.length === 2) {
        // Multi-touch zooming
        const touch1 = event.touches[0];
        const touch2 = event.touches[1];

        // Calcular a nova distância e ajustar o zoom
        const currentDistance = Math.hypot(
            touch2.clientX - touch1.clientX,
            touch2.clientY - touch1.clientY
        );

        // Calcular o novo zoom com base na proporção das distâncias
        const newZoom = Math.min(3, Math.max(0.2, touchStartZoom.value * (currentDistance / touchStartDistance.value)));

        // Calcular o ponto médio atual
        const currentMidpoint = {
            x: (touch1.clientX + touch2.clientX) / 2,
            y: (touch1.clientY + touch2.clientY) / 2
        };

        // Aplicar o zoom e ajustar a posição para manter o ponto médio
        const oldZoom = zoom.value;
        zoom.value = newZoom;

        // Ajustar a posição baseado no novo zoom
        const rect = designerArea.value.getBoundingClientRect();
        const mouseX = currentMidpoint.x - rect.left;
        const mouseY = currentMidpoint.y - rect.top;

        // Converter para coordenadas do mundo
        const worldX = (mouseX / oldZoom) - viewPosition.x;
        const worldY = (mouseY / oldZoom) - viewPosition.y;

        // Ajustar a posição para manter o ponto sob os dedos
        viewPosition.x = -(worldX - (mouseX / zoom.value));
        viewPosition.y = -(worldY - (mouseY / zoom.value));

        // Atualizar a última posição
        touchLastPosition.value = currentMidpoint;
    }
};

const finalizarTouchPanning = () => {
    isTouchPanning.value = false;
    isTouchZooming.value = false;
};

// Variáveis para controlar o drag do fundo do mapa
const isDraggingFundo = ref(false);
const dragFundoStart = ref({ x: 0, y: 0 });

// Iniciar o drag do fundo do mapa
const iniciarDragFundo = (event) => {
    // Registrar diagnóstico
    registrarEvento('iniciarDragFundo');

    // Verificar se o clique foi realmente no fundo e não em um elemento
    if (event.target.classList.contains('fundo-mapa') && event.button === 0) {
        // Se já estiver em alguma operação de arraste, não iniciar outra
        if (estadoInteracao.arrastando) return;

        event.preventDefault();
        event.stopPropagation();

        estadoInteracao.arrastando = true;
        estadoInteracao.fundoArrastando = true;
        isDraggingFundo.value = true;
        dragFundoStart.value = { x: event.clientX, y: event.clientY };

        document.addEventListener('mousemove', moverFundo);
        document.addEventListener('mouseup', finalizarDragFundo);

        // Alterar o cursor para indicar que está arrastando
        document.body.style.cursor = 'grabbing';

        // Adicionar um evento de escape para cancelar o drag
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') {
                document.removeEventListener('keydown', handleKeyDown);
                resetAllInteractions();
            }
        };
        document.addEventListener('keydown', handleKeyDown);
    }
};

// Mover o fundo do mapa durante o drag
let ultimoMovimentoFundo = 0;
const moverFundo = (event) => {
    if (!isDraggingFundo.value || !estadoInteracao.fundoArrastando) return;

    // Otimização: limitar a taxa de atualização para melhor desempenho
    const agora = Date.now();
    if (agora - ultimoMovimentoFundo < 16) return; // ~60fps
    ultimoMovimentoFundo = agora;

    const dx = (event.clientX - dragFundoStart.value.x) / zoom.value;
    const dy = (event.clientY - dragFundoStart.value.y) / zoom.value;

    viewPosition.x += dx;
    viewPosition.y += dy;

    dragFundoStart.value = { x: event.clientX, y: event.clientY };
};

// Finalizar o drag do fundo do mapa
const finalizarDragFundo = () => {
    // Registrar diagnóstico
    registrarEvento('finalizarDragFundo');

    isDraggingFundo.value = false;
    document.removeEventListener('mousemove', moverFundo);
    document.removeEventListener('mouseup', finalizarDragFundo);

    // Restaurar o cursor
    document.body.style.cursor = 'default';

    // Resetar estados de interação com pequeno atraso para evitar conflitos
    setTimeout(() => {
        estadoInteracao.arrastando = false;
        estadoInteracao.fundoArrastando = false;
    }, 50);
};

// Variável para controlar o fade out das dicas
const dicasFadeOut = ref(false);

// Função para registrar eventos importantes no diagnóstico
const registrarEvento = (tipo, detalhes = null) => {
    if (!diagnostico.ativo) return;

    diagnostico.ultimaOperacao = tipo;
    diagnostico.log.push({
        timestamp: new Date().toISOString(),
        tipo,
        detalhes,
        estadoAtual: JSON.parse(JSON.stringify({
            arrastando: estadoInteracao.arrastando,
            elementoArrastando: estadoInteracao.elementoArrastando,
            fundoArrastando: estadoInteracao.fundoArrastando,
            elementoEmDrag: elementoEmDrag.value ? 'presente' : 'null',
            zoom: zoom.value
        }))
    });

    // Manter apenas os últimos 50 registros
    if (diagnostico.log.length > 50) {
        diagnostico.log.shift();
    }

    // Se detectar um estado inconsistente, incrementar contador
    if ((estadoInteracao.elementoArrastando && !elementoEmDrag.value) ||
        (estadoInteracao.fundoArrastando && !isDraggingFundo.value)) {
        diagnostico.problemasEncontrados++;

        // Se encontrar muitos problemas, tentar corrigir automaticamente
        if (diagnostico.problemasEncontrados > 5) {
            console.warn('Muitos problemas de estado encontrados, tentando corrigir');
            resetAllInteractions();
            diagnostico.problemasEncontrados = 0;
        }
    }
};

// Adicionar uma função especial para fixar problemas específicos com Áreas de Produção
const corrigirProblemasAreas = () => {
    // Verificar se há Áreas de Produção
    if (!planta.campos.length) return;

    // Recriar os elementos visuais (forçar repintura)
    const camposAtuais = [...planta.campos];
    planta.campos = [];
    setTimeout(() => {
        planta.campos = camposAtuais;
    }, 10);

    // Garantir que não há operações de arraste pendentes
    resetAllInteractions();
};
</script>

<style scoped>
.viveiro-designer {
    @apply w-full h-full flex flex-col bg-gray-50 min-h-[calc(100vh-64px)] overflow-hidden;
}

.toolbar {
    @apply p-2 md:p-4 bg-white border-b border-gray-200 flex flex-wrap gap-4 items-center shadow-sm sticky top-0 z-10;
}

.toolbar-section {
    @apply flex flex-col gap-1;
}

.toolbar-title {
    @apply text-xs text-gray-500 font-medium px-2;
}

.toolbar-divider {
    @apply h-10 w-px bg-gray-200 mx-2;
}

.tool-group {
    @apply flex gap-2 flex-wrap;
}

.tool-btn {
    @apply h-10 px-3 bg-white border border-gray-200 rounded-lg flex items-center gap-2 font-medium text-gray-700 text-sm transition-all hover:bg-gray-50 hover:border-gray-300 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20;
}

.tool-btn-primary {
    @apply h-10 px-3 bg-green-600 border border-green-700 rounded-lg flex items-center gap-2 font-medium text-white text-sm transition-all hover:bg-green-700 hover:border-green-800 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500/40;
}

.tool-btn-export {
    @apply h-10 px-3 bg-blue-600 border border-blue-700 rounded-lg flex items-center gap-2 font-medium text-white text-sm transition-all hover:bg-blue-700 hover:border-blue-800 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500/40;
}

.tool-btn .icon,
.tool-btn-primary .icon,
.tool-btn-export .icon {
    @apply w-5 h-5;
}

.tool-btn-primary .icon,
.tool-btn-export .icon {
    @apply text-white;
}

.zoom-info {
    @apply text-xs text-gray-500 font-mono px-3 py-1 bg-gray-100 rounded-md ml-auto;
}

.designer-area {
    @apply flex-1 overflow-hidden relative bg-white shadow-inner p-0 m-2 border border-gray-200;
    height: calc(100vh - 120px);
    width: calc(100vw - 20px);
    max-width: 100%;
}

.toolbar-bottom {
    @apply fixed bottom-6 right-6 bg-white border border-gray-200 rounded-lg shadow-lg py-1 px-2 z-10;
}

.canvas-controls {
    @apply hidden;
}

.designer-container {
    width: 100%;
    height: 100%;
    position: relative;
}

.designer-svg {
    @apply w-full h-full bg-white;
    /* Sem tamanho mínimo - isso permite que o SVG redimensione corretamente */
}

.fundo-mapa {
    cursor: grab;
}

.fundo-mapa:active {
    cursor: grabbing !important;
}

.elemento-grupo {
    @apply cursor-move;
    transition: transform 0.2s ease-out;
}

/* Adicionar uma pequena dica visual quando passar sobre o fundo */
.designer-area::after {
    content: "";
    position: absolute;
    bottom: 4px;
    right: 4px;
    width: 24px;
    height: 24px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='rgba(0,0,0,0.4)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M15 3h6v6'/%3E%3Cpath d='M9 21H3v-6'/%3E%3Cpath d='M21 3l-7 7'/%3E%3Cpath d='M3 21l7-7'/%3E%3C/svg%3E");
    opacity: 0.5;
    pointer-events: none;
    z-index: 10;
}

.elemento-grupo:hover .elemento {
    @apply filter brightness-95;
}

.elemento-grupo:active .elemento {
    @apply scale-[1.01];
}

.elemento-grupo.selecionado .elemento {
    @apply stroke-blue-600 stroke-[3px];
    filter: drop-shadow(0px 0px 4px rgba(37, 99, 235, 0.5));
}

.elemento-grupo.selecionado text {
    @apply font-bold;
    text-shadow: 0px 1px 4px rgba(0, 0, 0, 0.8);
}

/* Animação de pulso ao selecionar um elemento */
@keyframes pulse {
    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.05);
    }

    100% {
        transform: scale(1);
    }
}

.pulse-animation {
    animation: pulse 0.3s ease-in-out;
}

.elemento {
    @apply stroke-2 transition-all duration-200 rounded-md;
    filter: drop-shadow(0px 2px 3px rgba(0, 0, 0, 0.1));
}

.campo {
    @apply stroke-[#8cc63f] fill-[#8cc63f];
    fill-opacity: 0.8;
}

.canteiro {
    @apply stroke-[#6ca234] fill-[#6ca234];
    fill-opacity: 0.8;
}

.espaco {
    @apply stroke-[#ffe135] fill-[#ffe135];
    fill-opacity: 0.9;
    filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.2));
}

.sementeira {
    @apply stroke-[#ff9600] fill-[#ff9600];
    fill-opacity: 0.8;
}

.area-trabalho {
    @apply stroke-[#ffe135] fill-[#ffe135];
    fill-opacity: 0.8;
}

.estoque {
    @apply stroke-[#b4b4b4] fill-[#b4b4b4];
    fill-opacity: 0.8;
}

.selecionado .elemento {
    @apply stroke-blue-600 stroke-[3px] filter drop-shadow;
}

.elemento-texto {
    @apply text-xs font-semibold fill-white pointer-events-none select-none;
    text-shadow: 0px 1px 3px rgba(0, 0, 0, 0.7);
}

.texto-escuro {
    @apply fill-gray-800;
    text-shadow: 0px 1px 2px rgba(255, 255, 255, 0.5);
}

.texto-pequeno {
    @apply text-[10px];
}

.modal-edicao {
    @apply fixed bg-white p-6 rounded-xl shadow-2xl z-50 w-[320px] cursor-default border border-gray-200;
}

.modal-header {
    @apply flex justify-between items-center mb-6 cursor-move select-none pb-4 border-b border-gray-200;
}

.modal-header h3 {
    @apply m-0 text-xl font-semibold text-gray-900;
}

.btn-fechar {
    @apply bg-transparent border-none p-2 cursor-pointer rounded-full flex items-center justify-center transition-all text-gray-500 hover:bg-gray-100 hover:text-gray-700;
}

.modal-conteudo {
    @apply flex flex-col gap-5;
}

.form-group {
    @apply flex flex-col gap-2;
}

.form-group label {
    @apply font-medium text-gray-700 text-sm;
}

.input {
    @apply px-3 py-2 border border-gray-300 rounded-lg text-sm transition-all text-gray-800 bg-gray-50 hover:border-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:bg-white;
}

.input-with-controls {
    @apply flex items-center;
}

.input-number {
    @apply flex-1 text-center;
}

.input-control {
    @apply px-3 py-2 bg-gray-100 border border-gray-300 text-gray-700 hover:bg-gray-200 transition-all;
}

.input-control:first-child {
    @apply rounded-l-lg border-r-0;
}

.input-control:last-child {
    @apply rounded-r-lg border-l-0;
}

.cores-grid {
    @apply grid grid-cols-5 gap-2;
}

.cor-opcao {
    @apply w-8 h-8 rounded-full cursor-pointer border-2 border-transparent transition-all hover:scale-110;
}

.cor-opcao.selecionada {
    @apply border-blue-500 ring-2 ring-blue-500/30;
}

.acoes {
    @apply flex gap-3 justify-end mt-6 pt-6 border-t border-gray-200;
}

.btn-duplicar {
    @apply px-4 py-2 bg-gray-100 text-gray-700 border border-gray-200 rounded-lg cursor-pointer font-medium transition-all hover:bg-gray-200 hover:border-gray-300;
}

.btn-excluir {
    @apply px-4 py-2 bg-red-50 text-red-600 border border-red-200 rounded-lg cursor-pointer font-medium transition-all hover:bg-red-100 hover:border-red-300;
}

.btn-salvar {
    @apply px-4 py-2 bg-blue-600 text-white border-none rounded-lg cursor-pointer font-medium transition-all hover:bg-blue-700;
}

/* Alerta de confirmação */
.alerta-overlay {
    @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.alerta-modal {
    @apply bg-white rounded-xl shadow-2xl p-6 max-w-md w-full mx-4;
}

.alerta-icone {
    @apply w-12 h-12 text-red-500 mx-auto mb-4;
}

.alerta-titulo {
    @apply text-xl font-bold text-center text-gray-900 mb-2;
}

.alerta-mensagem {
    @apply text-gray-600 text-center mb-6;
}

.alerta-acoes {
    @apply flex gap-4 justify-center;
}

.alerta-btn-cancelar {
    @apply px-5 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium border border-gray-200 transition-all hover:bg-gray-200;
}

.alerta-btn-confirmar {
    @apply px-5 py-2 bg-red-600 text-white rounded-lg font-medium transition-all hover:bg-red-700;
}

/* Responsividade */
@media (max-width: 768px) {
    .toolbar {
        @apply overflow-x-auto whitespace-nowrap py-2 px-2;
    }

    .toolbar-divider {
        @apply hidden;
    }

    .toolbar-section {
        @apply min-w-max;
    }

    .zoom-info {
        @apply hidden;
    }

    .designer-area {
        height: calc(100vh - 100px);
        margin: 0;
        border: none;
    }

    .dicas-navegacao {
        @apply text-[10px] p-1 bottom-2 left-2;
        max-width: 180px;
    }

    .minimap {
        width: 120px;
        height: 100px;
        @apply bottom-2 right-2;
    }

    .tool-btn,
    .tool-btn-export,
    .tool-btn-primary {
        @apply h-9 px-2 text-xs;
    }

    .tool-btn .icon,
    .tool-btn-export .icon,
    .tool-btn-primary .icon {
        @apply w-4 h-4;
    }

    .tool-btn span,
    .tool-btn-export span,
    .tool-btn-primary span {
        @apply text-[10px];
    }

    .modal-edicao {
        @apply w-[90%] max-w-[300px];
    }

    /* Esconder dicas após um tempo */
    .dicas-navegacao.auto-hide {
        opacity: 0;
        transition: opacity 0.5s ease;
    }
}

/* Adicionar dicas de navegação */
.dicas-navegacao {
    @apply fixed bottom-20 left-4 bg-white p-4 rounded-lg shadow-lg text-xs text-gray-600;
    z-index: 40;
    max-width: 250px;
    border: 1px solid #ddd;
    line-height: 1.5;
    transition: opacity 1s ease-out;
}

.dicas-navegacao.fade-out {
    opacity: 0;
}

.dicas-navegacao p {
    @apply mb-1;
}

.dicas-navegacao p strong {
    @apply text-gray-700;
}

.ml-2 {
    margin-left: 0.5rem;
}

.dicas-header {
    @apply flex justify-between items-center mb-2 pb-2 border-b border-gray-200;
}

.dicas-header h3 {
    @apply text-sm font-bold text-gray-700;
    margin: 0;
}

.dicas-close {
    @apply text-xl font-bold text-gray-500 hover:text-gray-800;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0 4px;
    line-height: 1;
}

.botao-ajuda {
    @apply fixed bottom-4 left-4 bg-white rounded-full w-10 h-10 shadow-lg flex items-center justify-center;
    z-index: 40;
    border: 1px solid #ddd;
}

.botao-ajuda:hover {
    @apply bg-gray-50;
}

.botao-ajuda .icon {
    @apply w-6 h-6 text-gray-600;
}

/* Minimap */
.minimap {
    @apply fixed bottom-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden;
    width: 200px;
    height: 150px;
    z-index: 40;
}

.minimap-content {
    width: 100%;
    height: 100%;
    cursor: crosshair;
}

.minimap-svg {
    width: 100%;
    height: 100%;
}

.minimap-toggle {
    @apply absolute top-1 right-1 w-6 h-6 bg-white rounded-full flex items-center justify-center border border-gray-300 text-gray-600 hover:bg-gray-100;
    z-index: 41;
}

.minimap-show {
    @apply fixed bottom-4 right-4;
    z-index: 40;
}

.marcador-texto {
    @apply fill-gray-500 text-[8px];
}
</style>