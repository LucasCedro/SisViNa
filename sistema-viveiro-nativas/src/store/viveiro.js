import { defineStore } from 'pinia'
import { listCanteirosComOcupacao } from '@/services/canteiros'
import { mapOcupacaoPorApiId } from '@/utils/viveiroOcupacao'
import {
  listPlantasComRelacoes,
  listPendentesTransferencia,
  listAptasRustificacaoCanteiro,
} from '@/services/plantas'
import { agruparPendenciasPorCanteiro } from '@/utils/viveiroPendenciasMapa'
import { getDashboardResumo } from '@/services/dashboard'
import { listPragasPlantas } from '@/services/pragas'
import { buildLayoutFromCanteiros, buildLayoutFromPlantaSalva, mapPlantaApi } from '@/utils/viveiroApiMapper'
import { getViveiroLayout } from '@/services/viveiroLayout'

const emptyLayout = () => ({
  id: 1,
  nome: 'Viveiro',
  dimensoes: { largura: 1000, altura: 400 },
  elementos: [],
})

export const useViveiroStore = defineStore('viveiro', {
  state: () => ({
    layout: emptyLayout(),
    mudas: [],
    elementoSelecionado: null,
    mudaSelecionada: null,
    dadosAmbientais: { alertas: [] },
    pendenciasPorCanteiro: {},
    metricas: {
      totalMudas: 0,
      mudaEspecie: [],
      mediaPermanencia: 0,
    },
    carregando: false,
    erro: null,
    hidratado: false,
  }),

  getters: {
    mudasDoCanteiro: (state) => (elementoId) => {
      const elemento = state.layout.elementos.find((elem) => elem.id === elementoId)
      if (!elemento?.mudas?.length) return []
      return elemento.mudas
        .map((mudaId) => state.mudas.find((muda) => muda.id === mudaId))
        .filter(Boolean)
    },

    dadosMudasPorEspecie: (state) => state.metricas.mudaEspecie,

    alertasAtivos: (state) => state.dadosAmbientais.alertas,

    temperaturasMedias: (state) => {
      return state.layout.elementos
        .filter((elem) => elem.tipo === 'canteiro')
        .map((canteiro) => {
          let soma = 0
          let count = 0
          canteiro.mudas?.forEach((mudaId) => {
            const muda = state.mudas.find((m) => m.id === mudaId)
            if (muda?.tempoPermanencia != null) {
              soma += muda.tempoPermanencia
              count++
            }
          })
          return {
            nome: canteiro.nome,
            temperatura: count > 0 ? Math.round(soma / count) : '—',
          }
        })
    },
  },

  actions: {
    async carregar(force = false) {
      if (this.hidratado && !force) return
      this.carregando = true
      this.erro = null
      try {
        const [canteiros, plantas, resumo, pragas, plantaSalva, pendentesTransf, aptasRust] =
          await Promise.all([
            listCanteirosComOcupacao({ ativo: true }),
            listPlantasComRelacoes({ limit: 500 }),
            getDashboardResumo(),
            listPragasPlantas({ limit: 100 }).catch(() => []),
            getViveiroLayout().catch(() => ({})),
            listPendentesTransferencia({ limit: 500 }).catch(() => []),
            listAptasRustificacaoCanteiro({ limit: 500 }).catch(() => []),
          ])

        const ativas = plantas.filter((p) => !['VENDIDA', 'MORTA'].includes(p.status))
        this.mudas = ativas.map(mapPlantaApi)
        const ocupacaoPorId = mapOcupacaoPorApiId(canteiros)
        this.layout = buildLayoutFromPlantaSalva(plantaSalva, canteiros, ativas, ocupacaoPorId)

        this.metricas = {
          totalMudas: resumo.mudas_ativas ?? this.mudas.length,
          mudaEspecie: (resumo.plantas_por_especie || []).map((p) => ({
            especie: p.especie,
            quantidade: p.quantidade,
          })),
          mediaPermanencia: calcMediaPermanencia(this.mudas),
        }

        this.dadosAmbientais.alertas = buildAlertasFromPragas(pragas, canteiros, ativas)

        const plantasPorId = new Map(
          ativas.map((p) => [p.id, { idCanteiro: p.id_canteiro, id_canteiro: p.id_canteiro }])
        )
        this.pendenciasPorCanteiro = agruparPendenciasPorCanteiro({
          pendentesTransferencia: pendentesTransf,
          aptasRustificacao: aptasRust,
          pragas,
          plantasPorId,
        })

        this.hidratado = true
      } catch (e) {
        console.error('[viveiro] falha ao carregar', e)
        const detail = e.response?.data?.detail
        this.erro =
          (typeof detail === 'string' ? detail : null) ||
          e.message ||
          'Não foi possível carregar o viveiro.'
        this.layout = emptyLayout()
        this.mudas = []
        this.hidratado = false
      } finally {
        this.carregando = false
      }
    },

    selecionarElemento(elementoId) {
      this.elementoSelecionado =
        this.layout.elementos.find((elem) => elem.id === elementoId) || null
      this.mudaSelecionada = null
    },

    selecionarMuda(mudaId) {
      this.mudaSelecionada = this.mudas.find((muda) => muda.id === mudaId) || null
    },

    atualizarMuda(mudaId, novosDados) {
      const index = this.mudas.findIndex((muda) => muda.id === mudaId)
      if (index !== -1) {
        this.mudas[index] = { ...this.mudas[index], ...novosDados }
      }
    },

    adicionarAlerta(alerta) {
      this.dadosAmbientais.alertas.unshift({
        id: Date.now(),
        data: new Date().toISOString(),
        ...alerta,
      })
    },

    removerAlerta(alertaId) {
      const index = this.dadosAmbientais.alertas.findIndex((a) => a.id === alertaId)
      if (index !== -1) this.dadosAmbientais.alertas.splice(index, 1)
    },
  },
})

function calcMediaPermanencia(mudas) {
  const comDias = mudas.filter((m) => m.tempoPermanencia != null)
  if (!comDias.length) return 0
  return Math.round(
    comDias.reduce((s, m) => s + m.tempoPermanencia, 0) / comDias.length
  )
}

function buildAlertasFromPragas(pragas, canteiros, plantas) {
  const pl = new Map(plantas.map((p) => [p.id, p]))
  const cant = new Map(canteiros.map((c) => [c.id, c.nome]))
  return pragas.slice(0, 8).map((p) => {
    const planta = pl.get(p.id_planta)
    const idCant = planta?.id_canteiro
    return {
      id: p.id,
      tipo:
        p.nivel_infestacao === 'ALTO' || p.nivel_infestacao === 'CRITICO'
          ? 'temperatura-alta'
          : 'umidade-baixa',
      canteiro: (idCant && cant.get(idCant)) || planta?.nome_canteiro || '—',
      mensagem: `${p.tipo_praga?.nome || 'Praga'} — ${p.especie_nome || planta?.especie_nome || 'planta'}`,
      data: p.data_identificacao,
    }
  })
}
