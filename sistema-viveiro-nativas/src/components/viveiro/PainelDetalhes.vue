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
                <p class="tipo-pill">{{ tipoElemento }}</p>

                <div
                    v-if="elementoSelecionado.badgeOcupacao != null && elementoSelecionado.apiId"
                    class="ocupacao-resumo"
                >
                    <span class="ocupacao-resumo-num">{{ elementoSelecionado.badgeOcupacao }}</span>
                    <span class="ocupacao-resumo-leg">ocupação</span>
                </div>

                <ul v-if="pendenciasLocal.length" class="pendencias-painel">
                    <li v-for="p in pendenciasLocal" :key="p.tipo">
                        <button type="button" class="pendencia-painel-btn" :class="`pendencia-painel-btn--${p.nivel}`" @click="irPendencia(p)">
                            <span class="pendencia-painel-ico" aria-hidden="true">{{ p.icone }}</span>
                            <span>
                                <strong>{{ p.rotulo }}</strong>
                                <small>{{ p.count }} pendência(s) — {{ p.titulo }}</small>
                            </span>
                        </button>
                    </li>
                </ul>

                <dl class="info-lista">
                    <div v-if="textoDimensoes" class="info-item">
                        <dt>Dimensões no chão</dt>
                        <dd>{{ textoDimensoes }}</dd>
                    </div>
                    <div v-if="elementoSelecionado.capacidade" class="info-item">
                        <dt>Capacidade</dt>
                        <dd>{{ elementoSelecionado.capacidade }} mudas</dd>
                    </div>
                    <div v-if="elementoSelecionado.mudas && elementoSelecionado.mudas.length > 0" class="info-item">
                        <dt>Plantas no local</dt>
                        <dd>{{ elementoSelecionado.mudas.length }}</dd>
                    </div>
                </dl>

                <!-- Lista de mudas do canteiro -->
                <div v-if="elementoSelecionado.mudas && elementoSelecionado.mudas.length > 0" class="secao-mudas">
                    <h4 class="subtitulo">Mudas neste {{ tipoElemento }}</h4>
                    <div class="lista-mudas">
                        <div
                            v-for="muda in mudasDoElemento"
                            :key="muda.id"
                            class="item-muda"
                            :class="{ alerta: muda.status === 'alerta-umidade' || muda.status === 'alerta-temperatura' }"
                            @click="selecionarMuda(muda.id)"
                        >
                            <div class="item-muda-corpo">
                                <div class="muda-nome">{{ muda.especie }}</div>
                                <div class="muda-info">{{ muda.nomePopular }}</div>
                            </div>
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
                    <dl v-if="!modoEdicao" class="info-lista">
                        <div class="info-item">
                            <dt>Espécie</dt>
                            <dd>{{ mudaSelecionada.especie }}</dd>
                        </div>
                        <div class="info-item">
                            <dt>Nome popular</dt>
                            <dd>{{ mudaSelecionada.nomePopular }}</dd>
                        </div>
                        <div class="info-item">
                            <dt>Semeadura</dt>
                            <dd>{{ formatarData(mudaSelecionada.dataSemeadura) }}</dd>
                        </div>
                        <div class="info-item">
                            <dt>Umidade</dt>
                            <dd>{{ formatarMedicao(mudaSelecionada.teorUmidade, '%') }}</dd>
                        </div>
                        <div class="info-item">
                            <dt>Permanência</dt>
                            <dd>{{ formatarMedicao(mudaSelecionada.tempoPermanencia, ' dias') }}</dd>
                        </div>
                        <div class="info-item">
                            <dt>Substrato</dt>
                            <dd>{{ mudaSelecionada.tipoSubstrato }}</dd>
                        </div>
                        <div class="info-item">
                            <dt>Temp. ar / solo</dt>
                            <dd>
                                {{ formatarMedicao(mudaSelecionada.temperaturaAr, '°C') }}
                                ·
                                {{ formatarMedicao(mudaSelecionada.temperaturaSolo, '°C') }}
                            </dd>
                        </div>
                        <div class="info-item">
                            <dt>Status</dt>
                            <dd><span class="chip" :class="mudaSelecionada.status">{{ formatarStatus(mudaSelecionada.status) }}</span></dd>
                        </div>
                    </dl>

                    <button v-if="podeEditarViveiro && !modoEdicao" type="button" class="btn-editar" @click="habilitarEdicao">
                        Editar dados
                    </button>

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
            <div class="sem-selecao-icon" aria-hidden="true">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="4" y="4" width="16" height="16" rx="2" />
                    <path d="M9 9h6M9 13h4" />
                </svg>
            </div>
            <p class="sem-selecao-titulo">Nenhuma área selecionada</p>
            <p class="sem-selecao-hint">Clique em uma área no mapa ou use os atalhos abaixo.</p>
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { usePermissions } from '@/composables/usePermissions';
import { textoMetros } from '@/constants/viveiroDimensoes';
import { pendenciasDoCanteiro } from '@/utils/viveiroPendenciasMapa';
import { useViveiroStore } from '../../store/viveiro';

const store = useViveiroStore();
const router = useRouter();
const { can } = usePermissions();
const podeEditarViveiro = computed(() => can('viveiro.edit'));

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
const textoDimensoes = computed(() => textoMetros(elementoSelecionado.value))

const pendenciasLocal = computed(() =>
    pendenciasDoCanteiro(store.pendenciasPorCanteiro, elementoSelecionado.value?.apiId)
)

function irPendencia(p) {
    if (p?.rota) router.push(p.rota)
}

const tipoElemento = computed(() => {
    if (!elementoSelecionado.value) return '';

    const tipos = {
        canteiro: 'Canteiro',
        sementeira: 'Sementeira',
        rustificacao: 'Rustificação',
        'area-trabalho': 'Área de trabalho',
        armazenamento: 'Armazém',
        sede: 'Sede',
        lago: 'Lago / água',
        garagem: 'Garagem',
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
    if (!podeEditarViveiro.value) return;
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
    width: 100%;
    min-width: 0;
    min-height: 80px;
}

.conteudo {
    padding: 0;
    min-width: 0;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: var(--v-s2);
    margin-bottom: var(--v-s3);
    padding-bottom: var(--v-s2);
    border-bottom: 1px solid var(--color-border-subtle);
}

.titulo {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
    line-height: 1.3;
    word-break: break-word;
    overflow-wrap: anywhere;
    flex: 1;
    min-width: 0;
}

.tipo-pill {
    display: inline-block;
    margin: 0 0 var(--v-s2);
    padding: var(--v-s1) var(--v-s2);
    font-size: 0.8125rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-primary);
    background: rgba(74, 124, 42, 0.1);
    border-radius: var(--radius-md);
}

.ocupacao-resumo {
    text-align: center;
    padding: var(--v-s3);
    margin-bottom: var(--v-s3);
    background: linear-gradient(180deg, #f4f7f0 0%, #eef4e8 100%);
    border: 1px solid #d4e4c8;
    border-radius: var(--radius-xl);
}

.ocupacao-resumo-num {
    display: block;
    font-size: 1.375rem;
    font-weight: 700;
    color: #2d5016;
    line-height: 1.15;
}

.ocupacao-resumo-leg {
    display: block;
    margin-top: var(--v-s2);
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    line-height: var(--v-line);
}

.pendencias-painel {
    list-style: none;
    margin: 0 0 var(--v-s3);
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--v-s2);
}

.pendencia-painel-btn {
    display: flex;
    align-items: flex-start;
    gap: var(--v-s2);
    width: 100%;
    padding: var(--v-s2) var(--v-s3);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-lg);
    background: #fff;
    text-align: left;
    cursor: pointer;
    font-family: inherit;
}

.pendencia-painel-btn strong {
    display: block;
    font-size: 0.9375rem;
    line-height: var(--v-line);
}

.pendencia-painel-btn small {
    display: block;
    margin-top: var(--v-s1);
    font-size: 0.8125rem;
    color: var(--color-text-secondary);
    line-height: var(--v-line);
}

.pendencia-painel-btn--alto {
    border-color: #fecaca;
    background: #fef2f2;
}

.pendencia-painel-btn--medio {
    border-color: #fde68a;
    background: #fffbeb;
}

.pendencia-painel-ico {
    font-size: 1rem;
    font-weight: 800;
    line-height: 1;
    margin-top: 0.1rem;
}

.info-lista {
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: var(--v-s2);
}

.info-item {
    display: grid;
    grid-template-columns: minmax(0, 38%) minmax(0, 1fr);
    gap: var(--v-s2) var(--v-s3);
    align-items: baseline;
    padding: var(--v-s2) 0;
    border-bottom: 1px solid var(--color-border-subtle);
}

.info-item:last-child {
    border-bottom: none;
}

.info-item dt {
    margin: 0;
    font-size: 0.8125rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: var(--color-text-muted);
    line-height: var(--v-line);
}

.info-item dd {
    margin: 0;
    font-size: 0.9375rem;
    color: var(--color-text-primary);
    word-break: break-word;
    overflow-wrap: anywhere;
    text-align: right;
    line-height: var(--v-line);
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
    margin-bottom: var(--v-s4);
}

.subtitulo {
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--color-text-secondary);
    margin: 0 0 var(--v-s2);
    line-height: var(--v-line);
}

.secao-mudas {
    margin-top: var(--v-s3);
    padding-top: var(--v-s3);
    border-top: 1px solid var(--color-border-subtle);
}

.lista-mudas {
    display: flex;
    flex-direction: column;
    gap: var(--v-s2);
    max-height: 260px;
    overflow-x: hidden;
    overflow-y: auto;
}

.item-muda {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--v-s2);
    padding: var(--v-s2) var(--v-s3);
    background-color: var(--color-surface-muted);
    border-radius: var(--radius-lg);
    cursor: pointer;
    border-left: 3px solid var(--color-primary);
    min-width: 0;
}

.item-muda:hover {
    background-color: #ecece8;
}

.item-muda.alerta {
    border-left-color: var(--color-attention);
}

.item-muda-corpo {
    min-width: 0;
    flex: 1;
}

.muda-nome {
    font-weight: 600;
    font-size: 0.9375rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: var(--v-line);
}

.muda-info {
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    margin-top: var(--v-s1);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: var(--v-line);
}

.muda-chip {
    flex-shrink: 0;
    max-width: 45%;
    font-size: 0.6875rem;
    line-height: var(--v-line);
    padding: var(--v-s1) var(--v-s2);
    border-radius: 999px;
    background-color: var(--color-success-bg);
    color: var(--color-success);
    text-align: center;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
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

.btn-editar {
    margin-top: 1rem;
    width: 100%;
    box-sizing: border-box;
    background-color: var(--color-primary, #4a7c2a);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1rem;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.875rem;
    font-family: inherit;
    transition: background-color 0.15s ease;
}

.btn-editar:hover {
    background-color: #3d6623;
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
    width: 100%;
    box-sizing: border-box;
    min-width: 0;
    padding: 8px 12px;
    border: 1px solid var(--color-border);
    border-radius: 8px;
    font-size: 0.875rem;
    font-family: inherit;
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
    padding: var(--v-s4) var(--v-s3);
    text-align: center;
    background: var(--color-surface-muted);
    border: 1px dashed var(--color-border);
    border-radius: var(--radius-xl);
}

.sem-selecao-icon {
    color: var(--color-text-muted);
    opacity: 0.45;
    margin-bottom: var(--v-s3);
}

.sem-selecao-titulo {
    margin: 0 0 var(--v-s2);
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--color-text-primary);
    line-height: var(--v-line);
}

.sem-selecao-hint {
    margin: 0;
    font-size: 0.875rem;
    color: var(--color-text-muted);
    line-height: var(--v-line);
}

@media (max-width: 400px) {
    .info-item {
        grid-template-columns: 1fr;
    }

    .info-item dd {
        text-align: left;
    }
}
</style>