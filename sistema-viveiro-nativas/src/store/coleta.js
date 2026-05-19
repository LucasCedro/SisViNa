import { defineStore } from 'pinia'

export const useColetaStore = defineStore('coleta', {
    state: () => ({
        arvoresMatriz: [
            {
                id: 1,
                especie: 'Araucaria angustifolia',
                nome: 'Pinheiro 1',
                lat: -25.4284,
                lng: -49.2733,
                sementesColetadas: 150,
                taxaGerminacao: 85,
                tempoArmazenamento: '6 meses',
                dataColeta: '2024-03-15',
                observacoes: 'Árvore saudável, boa produção'
            },
            {
                id: 2,
                especie: 'Handroanthus chrysotrichus',
                nome: 'Ipê Amarelo 1',
                lat: -25.4290,
                lng: -49.2740,
                sementesColetadas: 200,
                taxaGerminacao: 75,
                tempoArmazenamento: '3 meses',
                dataColeta: '2024-03-10',
                observacoes: 'Floração abundante'
            },
            {
                id: 3,
                especie: 'Tabebuia roseoalba',
                nome: 'Ipê Branco 1',
                lat: -25.4278,
                lng: -49.2725,
                sementesColetadas: 180,
                taxaGerminacao: 80,
                tempoArmazenamento: '4 meses',
                dataColeta: '2024-03-05',
                observacoes: 'Localização próxima ao rio'
            }
        ]
    }),

    getters: {
        totalSementesPorEspecie: (state) => {
            return state.arvoresMatriz.reduce((acc, arvore) => {
                acc[arvore.especie] = (acc[arvore.especie] || 0) + arvore.sementesColetadas
                return acc
            }, {})
        },

        germinacaoMediaPorMatriz: (state) => {
            return state.arvoresMatriz.map(arvore => ({
                nome: arvore.nome,
                taxa: arvore.taxaGerminacao
            }))
        },

        evolucaoTemporal: (state) => {
            return state.arvoresMatriz.map(arvore => ({
                data: arvore.dataColeta,
                quantidade: arvore.sementesColetadas
            }))
        }
    }
}) 