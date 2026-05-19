<template>
    <div class="planta-baixa-container">
        <div class="planta-baixa"
            :style="{ width: `${layout.dimensoes.largura}px`, height: `${layout.dimensoes.altura}px` }">
            <!-- Renderiza cada elemento do layout -->
            <div v-for="elemento in layout.elementos" :key="elemento.id"
                :class="['elemento', elemento.tipo, { 'selecionado': elementoSelecionado?.id === elemento.id }]"
                :style="estiloElemento(elemento)" @click="selecionarElemento(elemento.id)">
                <div class="elemento-titulo">{{ elemento.nome }}</div>
                <!-- Renderiza um indicador de alerta se necessário -->
                <div v-if="temAlerta(elemento)" class="alerta-indicador">!</div>
            </div>
        </div>

        <!-- Legenda -->
        <div class="legenda">
            <div class="legenda-item">
                <div class="cor-amostra" style="background-color: #8BC34A;"></div>
                <span>Canteiro</span>
            </div>
            <div class="legenda-item">
                <div class="cor-amostra" style="background-color: #FF9800;"></div>
                <span>Sementeira</span>
            </div>
            <div class="legenda-item">
                <div class="cor-amostra" style="background-color: #FFEB3B;"></div>
                <span>Área de Trabalho</span>
            </div>
            <div class="legenda-item">
                <div class="cor-amostra" style="background-color: #9E9E9E;"></div>
                <span>Armazenamento</span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useViveiroStore } from '../../store/viveiro';

const store = useViveiroStore();

// Dados do layout
const layout = computed(() => store.layout);
const elementoSelecionado = computed(() => store.elementoSelecionado);
const alertas = computed(() => store.alertasAtivos);

// Calcula o estilo CSS para posicionamento e dimensões do elemento
const estiloElemento = (elemento) => {
    return {
        left: `${elemento.posicao.x}px`,
        top: `${elemento.posicao.y}px`,
        width: `${elemento.dimensoes.largura}px`,
        height: `${elemento.dimensoes.altura}px`,
        backgroundColor: elemento.cor
    };
};

// Verifica se um elemento tem alertas associados
const temAlerta = (elemento) => {
    if (elemento.tipo !== 'canteiro') return false;

    return alertas.value.some(alerta =>
        alerta.canteiro === elemento.nome
    );
};

// Seleciona um elemento para exibição de detalhes
const selecionarElemento = (elementoId) => {
    store.selecionarElemento(elementoId);
};
</script>

<style scoped>
.planta-baixa-container {
    width: 100%;
    overflow: auto;
    background-color: #f8f8f8;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 16px;
}

.planta-baixa {
    position: relative;
    margin: 0 auto;
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
}

.elemento {
    position: absolute;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease-in-out;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(0, 0, 0, 0.7);
    font-weight: 500;
    overflow: hidden;
}

.elemento:hover {
    opacity: 0.9;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.elemento.selecionado {
    box-shadow: 0 0 0 3px #1976D2, 0 4px 8px rgba(0, 0, 0, 0.2);
    z-index: 10;
}

.elemento-titulo {
    background-color: rgba(255, 255, 255, 0.8);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9rem;
}

.alerta-indicador {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 20px;
    height: 20px;
    background-color: #f44336;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 14px;
    animation: pulsate 1.5s infinite;
}

@keyframes pulsate {
    0% {
        transform: scale(0.9);
        opacity: 0.7;
    }

    50% {
        transform: scale(1.1);
        opacity: 1;
    }

    100% {
        transform: scale(0.9);
        opacity: 0.7;
    }
}

.legenda {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-top: 16px;
    padding: 8px;
    background-color: white;
    border-radius: 4px;
}

.legenda-item {
    display: flex;
    align-items: center;
    gap: 8px;
}

.cor-amostra {
    width: 16px;
    height: 16px;
    border-radius: 3px;
}
</style>