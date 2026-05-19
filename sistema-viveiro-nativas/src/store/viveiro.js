import { defineStore } from 'pinia'

export const useViveiroStore = defineStore('viveiro', {
    state: () => ({
        // Estrutura da planta baixa do viveiro
        layout: {
            id: 1,
            nome: 'Viveiro Principal',
            dimensoes: { largura: 1000, altura: 600 },
            // Elementos da planta baixa (canteiros, espaço de mudas, etc)
            elementos: [
                {
                    id: 'canteiro-1',
                    tipo: 'canteiro',
                    nome: 'Canteiro A',
                    posicao: { x: 50, y: 50 },
                    dimensoes: { largura: 200, altura: 120 },
                    cor: '#8BC34A',
                    mudas: [1, 2, 3, 4, 5]
                },
                {
                    id: 'canteiro-2',
                    tipo: 'canteiro',
                    nome: 'Canteiro B',
                    posicao: { x: 300, y: 50 },
                    dimensoes: { largura: 200, altura: 120 },
                    cor: '#8BC34A',
                    mudas: [6, 7, 8, 9]
                },
                {
                    id: 'canteiro-3',
                    tipo: 'canteiro',
                    nome: 'Canteiro C',
                    posicao: { x: 550, y: 50 },
                    dimensoes: { largura: 400, altura: 120 },
                    cor: '#8BC34A',
                    mudas: [10, 11, 12, 13, 14, 15]
                },
                {
                    id: 'canteiro-4',
                    tipo: 'canteiro',
                    nome: 'Canteiro D',
                    posicao: { x: 50, y: 220 },
                    dimensoes: { largura: 300, altura: 150 },
                    cor: '#8BC34A',
                    mudas: [16, 17, 18, 19, 20]
                },
                {
                    id: 'canteiro-5',
                    tipo: 'canteiro',
                    nome: 'Canteiro E',
                    posicao: { x: 400, y: 220 },
                    dimensoes: { largura: 300, altura: 150 },
                    cor: '#8BC34A',
                    mudas: [21, 22, 23, 24, 25]
                },
                {
                    id: 'area-trabalho-1',
                    tipo: 'area-trabalho',
                    nome: 'Área de Trabalho',
                    posicao: { x: 750, y: 220 },
                    dimensoes: { largura: 200, altura: 150 },
                    cor: '#FFEB3B'
                },
                {
                    id: 'sementeira-1',
                    tipo: 'sementeira',
                    nome: 'Sementeira 1',
                    posicao: { x: 50, y: 420 },
                    dimensoes: { largura: 200, altura: 100 },
                    cor: '#FF9800',
                    mudas: [26, 27, 28, 29, 30]
                },
                {
                    id: 'sementeira-2',
                    tipo: 'sementeira',
                    nome: 'Sementeira 2',
                    posicao: { x: 300, y: 420 },
                    dimensoes: { largura: 200, altura: 100 },
                    cor: '#FF9800',
                    mudas: [31, 32, 33, 34, 35]
                },
                {
                    id: 'armazenamento-1',
                    tipo: 'armazenamento',
                    nome: 'Estoque de Substrato',
                    posicao: { x: 750, y: 420 },
                    dimensoes: { largura: 200, altura: 100 },
                    cor: '#9E9E9E'
                }
            ]
        },

        // Dados das mudas
        mudas: [
            {
                id: 1,
                especie: 'Araucaria angustifolia',
                nomePopular: 'Pinheiro-do-paraná',
                dataSemeadura: '2024-01-15',
                teorUmidade: 75,
                tempoPermanencia: 90, // dias
                tipoSubstrato: 'Orgânico florestal',
                temperaturaAr: 23.5,
                temperaturaSolo: 22.1,
                status: 'saudável'
            },
            {
                id: 2,
                especie: 'Cedrela fissilis',
                nomePopular: 'Cedro',
                dataSemeadura: '2024-01-20',
                teorUmidade: 68,
                tempoPermanencia: 85, // dias
                tipoSubstrato: 'Orgânico florestal',
                temperaturaAr: 23.8,
                temperaturaSolo: 22.3,
                status: 'saudável'
            },
            {
                id: 3,
                especie: 'Euterpe edulis',
                nomePopular: 'Palmito-juçara',
                dataSemeadura: '2024-02-05',
                teorUmidade: 72,
                tempoPermanencia: 70, // dias
                tipoSubstrato: 'Fibra de coco',
                temperaturaAr: 24.2,
                temperaturaSolo: 23.0,
                status: 'alerta-umidade'
            },
            {
                id: 4,
                especie: 'Handroanthus chrysotrichus',
                nomePopular: 'Ipê-amarelo',
                dataSemeadura: '2024-02-10',
                teorUmidade: 65,
                tempoPermanencia: 65, // dias
                tipoSubstrato: 'Orgânico florestal',
                temperaturaAr: 23.9,
                temperaturaSolo: 22.6,
                status: 'saudável'
            },
            {
                id: 5,
                especie: 'Tabebuia roseoalba',
                nomePopular: 'Ipê-branco',
                dataSemeadura: '2024-02-15',
                teorUmidade: 62,
                tempoPermanencia: 60, // dias
                tipoSubstrato: 'Orgânico florestal',
                temperaturaAr: 24.5,
                temperaturaSolo: 23.2,
                status: 'saudável'
            }
        ],

        // Elemento selecionado na planta baixa
        elementoSelecionado: null,

        // Muda selecionada
        mudaSelecionada: null,

        // Dados de temperatura e umidade do viveiro
        dadosAmbientais: {
            temperaturaMediaAr: 23.8,
            temperaturaMediaSolo: 22.5,
            umidadeMediaAr: 70,
            alertas: [
                {
                    id: 1,
                    tipo: 'umidade-baixa',
                    canteiro: 'Canteiro D',
                    mensagem: 'Umidade abaixo do ideal no Canteiro D',
                    data: '2024-04-10T14:30:00'
                },
                {
                    id: 2,
                    tipo: 'temperatura-alta',
                    canteiro: 'Canteiro A',
                    mensagem: 'Temperatura elevada no Canteiro A',
                    data: '2024-04-10T12:15:00'
                }
            ]
        },

        // Métricas e estatísticas
        metricas: {
            totalMudas: 35,
            mudaEspecie: [
                { especie: 'Araucaria angustifolia', quantidade: 8 },
                { especie: 'Cedrela fissilis', quantidade: 5 },
                { especie: 'Euterpe edulis', quantidade: 7 },
                { especie: 'Handroanthus chrysotrichus', quantidade: 6 },
                { especie: 'Tabebuia roseoalba', quantidade: 9 }
            ],
            mediaPermanencia: 75 // dias
        }
    }),

    getters: {
        // Retorna todas as mudas de um canteiro específico
        mudasDoCanteiro: (state) => (canteiroId) => {
            const canteiro = state.layout.elementos.find(elem => elem.id === canteiroId);
            if (!canteiro || !canteiro.mudas) return [];

            return canteiro.mudas.map(mudaId => {
                return state.mudas.find(muda => muda.id === mudaId);
            }).filter(Boolean);
        },

        // Retorna dados para o dashboard de mudas por espécie
        dadosMudasPorEspecie: (state) => {
            return state.metricas.mudaEspecie;
        },

        // Retorna todos os alertas ativos
        alertasAtivos: (state) => {
            return state.dadosAmbientais.alertas;
        },

        // Retorna a temperatura média dos canteiros
        temperaturasMedias: (state) => {
            const canteiros = state.layout.elementos.filter(elem => elem.tipo === 'canteiro');
            const mudas = state.mudas;

            return canteiros.map(canteiro => {
                let somaTemp = 0;
                let count = 0;

                if (canteiro.mudas) {
                    canteiro.mudas.forEach(mudaId => {
                        const muda = mudas.find(m => m.id === mudaId);
                        if (muda) {
                            somaTemp += muda.temperaturaSolo;
                            count++;
                        }
                    });
                }

                return {
                    nome: canteiro.nome,
                    temperatura: count > 0 ? (somaTemp / count).toFixed(1) : 'N/A'
                };
            });
        }
    },

    actions: {
        // Seleciona um elemento da planta baixa
        selecionarElemento(elementoId) {
            this.elementoSelecionado = this.layout.elementos.find(elem => elem.id === elementoId) || null;
            this.mudaSelecionada = null;
        },

        // Seleciona uma muda específica
        selecionarMuda(mudaId) {
            this.mudaSelecionada = this.mudas.find(muda => muda.id === mudaId) || null;
        },

        // Atualiza os dados de uma muda
        atualizarMuda(mudaId, novosDados) {
            const index = this.mudas.findIndex(muda => muda.id === mudaId);
            if (index !== -1) {
                this.mudas[index] = { ...this.mudas[index], ...novosDados };
            }
        },

        // Adiciona um novo alerta
        adicionarAlerta(alerta) {
            this.dadosAmbientais.alertas.unshift({
                id: Date.now(),
                data: new Date().toISOString(),
                ...alerta
            });
        },

        // Remove um alerta
        removerAlerta(alertaId) {
            const index = this.dadosAmbientais.alertas.findIndex(alerta => alerta.id === alertaId);
            if (index !== -1) {
                this.dadosAmbientais.alertas.splice(index, 1);
            }
        }
    }
}); 