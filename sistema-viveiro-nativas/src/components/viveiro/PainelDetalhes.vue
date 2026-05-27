<template>
    <div class="painel-detalhes" :class="{ 'aberto': temItemSelecionado }">
        <div v-if="temItemSelecionado" class="conteudo">
            <div class="header">
                <h3 class="titulo">{{ tituloDetalhes }}</h3>
                <button @click="fecharPainel" class="btn-fechar">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <!-- Detalhes do Elemento (Canteiro, Sementeira, etc) -->
            <div v-if="elementoSelecionado && !mudaSelecionada" class="secao">
                <div class="info-elemento">
                    <div class="campo">
                        <span class="campo-label">Tipo:</span>
                        <span class="campo-valor">{{ tipoElemento }}</span>
                    </div>

                    <div class="campo">
                        <span class="campo-label">Dimensões:</span>
                        <span class="campo-valor">{{ elementoSelecionado.dimensoes.largura }}cm x {{
                            elementoSelecionado.dimensoes.altura }}cm</span>
                    </div>

                    <div v-if="elementoSelecionado.mudas && elementoSelecionado.mudas.length > 0" class="campo">
                        <span class="campo-label">Quantidade de Mudas:</span>
                        <span class="campo-valor">{{ elementoSelecionado.mudas.length }}</span>
                    </div>
                </div>

                <!-- Lista de mudas do canteiro -->
                <div v-if="elementoSelecionado.mudas && elementoSelecionado.mudas.length > 0" class="secao-mudas">
                    <h4 class="subtitulo">Mudas neste {{ tipoElemento }}</h4>
                    <div class="lista-mudas">
                        <div v-for="muda in mudasDoElemento" :key="muda.id" @click="selecionarMuda(muda.id)"
                            class="item-muda"
                            :class="{ 'alerta': muda.status === 'alerta-umidade' || muda.status === 'alerta-temperatura' }">
                            <div class="muda-nome">{{ muda.especie }}</div>
                            <div class="muda-info">{{ muda.nomePopular }}</div>
                            <div class="muda-chip" :class="muda.status">{{ formatarStatus(muda.status) }}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Detalhes da Muda -->
            <div v-if="mudaSelecionada" class="secao">
                <div class="header-muda">
                    <button @click="voltarParaElemento" class="btn-voltar">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                        </svg>
                        Voltar
                    </button>
                </div>

                <div class="formulario">
                    <!-- Dados da muda em modo de visualização ou edição -->
                    <div class="modo-visualizacao" v-if="!modoEdicao">
                        <div class="campo">
                            <span class="campo-label">Espécie:</span>
                            <span class="campo-valor">{{ mudaSelecionada.especie }}</span>
                        </div>
                        <div class="campo">
                            <span class="campo-label">Nome Popular:</span>
                            <span class="campo-valor">{{ mudaSelecionada.nomePopular }}</span>
                        </div>
                        <div class="campo">
                            <span class="campo-label">Data da Semeadura:</span>
                            <span class="campo-valor">{{ formatarData(mudaSelecionada.dataSemeadura) }}</span>
                        </div>
                        <div class="campo">
                            <span class="campo-label">Teor de Umidade:</span>
                            <span class="campo-valor">{{ formatarMedicao(mudaSelecionada.teorUmidade, '%') }}</span>
                        </div>
                        <div class="campo">
                            <span class="campo-label">Tempo de Permanência:</span>
                            <span class="campo-valor">{{ formatarMedicao(mudaSelecionada.tempoPermanencia, ' dias') }}</span>
                        </div>
                        <div class="campo">
                            <span class="campo-label">Tipo de Substrato:</span>
                            <span class="campo-valor">{{ mudaSelecionada.tipoSubstrato }}</span>
                        </div>
                        <div class="campo">
                            <span class="campo-label">Temperatura do Ar:</span>
                            <span class="campo-valor">{{ formatarMedicao(mudaSelecionada.temperaturaAr, '°C') }}</span>
                        </div>
                        <div class="campo">
                            <span class="campo-label">Temperatura do Solo:</span>
                            <span class="campo-valor">{{ formatarMedicao(mudaSelecionada.temperaturaSolo, '°C') }}</span>
                        </div>
                        <div class="campo">
                            <span class="campo-label">Status:</span>
                            <span class="campo-valor chip" :class="mudaSelecionada.status">
                                {{ formatarStatus(mudaSelecionada.status) }}
                            </span>
                        </div>

                        <button @click="habilitarEdicao" class="btn-editar">
                            Editar Dados
                        </button>
                    </div>

                    <!-- Formulário de edição -->
                    <div class="modo-edicao" v-else>
                        <div class="campo-form">
                            <label for="teorUmidade">Teor de Umidade (%)</label>
                            <input type="number" id="teorUmidade" v-model.number="dadosEditados.teorUmidade"
                                class="input" min="0" max="100" />
                        </div>

                        <div class="campo-form">
                            <label for="tipoSubstrato">Tipo de Substrato</label>
                            <select id="tipoSubstrato" v-model="dadosEditados.tipoSubstrato" class="input">
                                <option value="Orgânico florestal">Orgânico florestal</option>
                                <option value="Fibra de coco">Fibra de coco</option>
                                <option value="Vermiculita">Vermiculita</option>
                                <option value="Terra vegetal">Terra vegetal</option>
                                <option value="Composto orgânico">Composto orgânico</option>
                            </select>
                        </div>

                        <div class="campo-form">
                            <label for="temperaturaAr">Temperatura do Ar (°C)</label>
                            <input type="number" id="temperaturaAr" v-model.number="dadosEditados.temperaturaAr"
                                class="input" step="0.1" />
                        </div>

                        <div class="campo-form">
                            <label for="temperaturaSolo">Temperatura do Solo (°C)</label>
                            <input type="number" id="temperaturaSolo" v-model.number="dadosEditados.temperaturaSolo"
                                class="input" step="0.1" />
                        </div>

                        <div class="campo-form">
                            <label for="status">Status</label>
                            <select id="status" v-model="dadosEditados.status" class="input">
                                <option value="saudável">Saudável</option>
                                <option value="alerta-umidade">Alerta de Umidade</option>
                                <option value="alerta-temperatura">Alerta de Temperatura</option>
                                <option value="em-tratamento">Em Tratamento</option>
                            </select>
                        </div>

                        <div class="acoes">
                            <button @click="cancelarEdicao" class="btn-cancelar">
                                Cancelar
                            </button>
                            <button @click="salvarEdicao" class="btn-salvar">
                                Salvar Alterações
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="sem-selecao">
            <p>Selecione um elemento na planta baixa para visualizar os detalhes</p>
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useViveiroStore } from '../../store/viveiro';

const store = useViveiroStore();

// Dados do store
const elementoSelecionado = computed(() => store.elementoSelecionado);
const mudaSelecionada = computed(() => store.mudaSelecionada);

// Verifica se há algum item selecionado
const temItemSelecionado = computed(() => elementoSelecionado.value !== null || mudaSelecionada.value !== null);

// Título da seção de detalhes
const tituloDetalhes = computed(() => {
    if (mudaSelecionada.value) {
        return `Detalhes da Muda: ${mudaSelecionada.value.especie}`;
    } else if (elementoSelecionado.value) {
        return elementoSelecionado.value.nome;
    }
    return 'Detalhes';
});

// Tipo de elemento selecionado formatado
const tipoElemento = computed(() => {
    if (!elementoSelecionado.value) return '';

    const tipos = {
        'canteiro': 'Canteiro',
        'sementeira': 'Sementeira',
        'area-trabalho': 'Área de Trabalho',
        'armazenamento': 'Área de Armazenamento'
    };

    return tipos[elementoSelecionado.value.tipo] || elementoSelecionado.value.tipo;
});

// Mudas do elemento selecionado
const mudasDoElemento = computed(() => {
    if (!elementoSelecionado.value || !elementoSelecionado.value.mudas) return [];

    return elementoSelecionado.value.mudas.map(mudaId => {
        return store.mudas.find(muda => muda.id === mudaId);
    }).filter(Boolean);
});

// Estado de edição
const modoEdicao = ref(false);
const dadosEditados = ref({});

// Funções
const formatarMedicao = (valor, sufixo = '') => {
    if (valor === null || valor === undefined || valor === '') return '—'
    return `${valor}${sufixo}`
}

const formatarData = (dataString) => {
    const data = new Date(dataString);
    return data.toLocaleDateString('pt-BR');
};

const formatarStatus = (status) => {
    const statusMap = {
        'saudável': 'Saudável',
        'alerta-umidade': 'Alerta de Umidade',
        'alerta-temperatura': 'Alerta de Temperatura',
        'em-tratamento': 'Em Tratamento'
    };

    return statusMap[status] || status;
};

const selecionarMuda = (mudaId) => {
    store.selecionarMuda(mudaId);
};

const voltarParaElemento = () => {
    store.mudaSelecionada = null;
    modoEdicao.value = false;
};

const fecharPainel = () => {
    store.elementoSelecionado = null;
    store.mudaSelecionada = null;
    modoEdicao.value = false;
};

const habilitarEdicao = () => {
    // Copia os dados atuais para o formulário
    dadosEditados.value = { ...mudaSelecionada.value };
    modoEdicao.value = true;
};

const cancelarEdicao = () => {
    modoEdicao.value = false;
};

const salvarEdicao = () => {
    store.atualizarMuda(mudaSelecionada.value.id, dadosEditados.value);
    modoEdicao.value = false;
};
</script>

<style scoped>
.painel-detalhes {
    position: relative;
    background-color: var(--color-surface);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: all 0.3s ease;
    height: 100%;
    width: 100%;
}

.aberto {
    transform: translateX(0);
}

.conteudo {
    padding: 1rem;
    height: 100%;
    overflow-y: auto;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--color-border);
}

.titulo {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
}

.btn-fechar {
    background: transparent;
    border: none;
    color: var(--color-text-muted);
    cursor: pointer;
    width: 30px;
    height: 30px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
}

.btn-fechar:hover {
    background-color: var(--color-surface-muted);
    color: var(--color-text-primary);
}

.btn-fechar svg {
    width: 20px;
    height: 20px;
}

.secao {
    margin-bottom: 1.5rem;
}

.subtitulo {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-secondary);
    margin-bottom: 0.75rem;
}

.campo {
    display: flex;
    margin-bottom: 0.5rem;
}

.campo-label {
    font-weight: 500;
    color: var(--color-text-muted);
    width: 40%;
}

.campo-valor {
    color: var(--color-text-primary);
    flex: 1;
}

.secao-mudas {
    margin-top: 1.5rem;
}

.lista-mudas {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: 300px;
    overflow-y: auto;
}

.item-muda {
    padding: 0.75rem;
    background-color: var(--color-surface-muted);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    border-left: 4px solid var(--color-primary);
}

.item-muda:hover {
    background-color: var(--color-surface-muted);
    transform: translateY(-2px);
}

.item-muda.alerta {
    border-left-color: var(--color-attention);
}

.muda-nome {
    font-weight: 500;
    font-size: 0.9rem;
}

.muda-info {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    margin-top: 0.25rem;
}

.muda-chip {
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 10px;
    background-color: var(--color-success-bg);
    color: var(--color-success);
}

.muda-chip.alerta-umidade,
.muda-chip.alerta-temperatura {
    background-color: var(--color-attention-bg);
    color: var(--color-complement-dark);
}

.chip {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
}

.chip.saudável {
    background-color: var(--color-success-bg);
    color: var(--color-success);
}

.chip.alerta-umidade,
.chip.alerta-temperatura {
    background-color: var(--color-attention-bg);
    color: var(--color-complement-dark);
}

.chip.em-tratamento {
    background-color: var(--color-info-bg);
    color: var(--color-info-dark);
}

.header-muda {
    margin-bottom: 1rem;
}

.btn-voltar {
    background: transparent;
    border: none;
    color: var(--color-info);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 8px;
    border-radius: 4px;
    font-size: 0.9rem;
}

.btn-voltar:hover {
    background-color: var(--color-surface-muted);
}

.btn-voltar svg {
    width: 16px;
    height: 16px;
}

.modo-visualizacao {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.btn-editar {
    margin-top: 1rem;
    background-color: var(--color-info);
    color: var(--color-text-inverse);
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s;
}

.btn-editar:hover {
    background-color: var(--color-info-dark);
}

.modo-edicao {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.campo-form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.campo-form label {
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--color-text-secondary);
}

.input {
    padding: 8px 12px;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    font-size: 0.9rem;
}

.input:focus {
    outline: none;
    border-color: var(--color-info);
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

.acoes {
    display: flex;
    gap: 10px;
    margin-top: 1rem;
}

.btn-cancelar {
    flex: 1;
    padding: 8px 16px;
    background-color: var(--color-surface-muted);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
}

.btn-salvar {
    flex: 1;
    padding: 8px 16px;
    background-color: var(--color-info);
    color: var(--color-text-inverse);
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
}

.btn-cancelar:hover {
    background-color: var(--color-border);
}

.btn-salvar:hover {
    background-color: var(--color-info-dark);
}

.sem-selecao {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    color: var(--color-text-muted);
    text-align: center;
}
</style>