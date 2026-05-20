import { defineStore } from 'pinia'
import {
  listArvoresMatriz,
  createArvoreMatriz,
  updateArvoreMatriz,
  deleteArvoreMatriz
} from '@/services/arvoresMatriz'
import {
  listColetasSementes,
  createColetaSementes,
  updateColetaSementes,
  deleteColetaSementes
} from '@/services/coletasSementes'
import { listLotesSementes, updateLoteSementes } from '@/services/lotesSementes'
import { listTestesSementes } from '@/services/testesSementes'
import { listSemeaduras } from '@/services/semeaduras'

export const useColetaStore = defineStore('coleta', {
  state: () => ({
    arvoresMatriz: [],
    coletas: [],
    lotes: [],
    testes: [],
    semeaduras: [],
    carregando: false,
    erro: null,
    matrizSelecionada: null,
    filtros: {
      busca: '',
      id_especie: '',
      estado: ''
    }
  }),

  getters: {
    matrizesFiltradas(state) {
      let lista = state.arvoresMatriz
      const { busca, id_especie, estado } = state.filtros

      if (busca?.trim()) {
        const q = busca.trim().toLowerCase()
        lista = lista.filter(
          (a) =>
            a.nome?.toLowerCase().includes(q) ||
            a.cidade?.toLowerCase().includes(q) ||
            a.municipio?.toLowerCase().includes(q) ||
            a.imovel_nome?.toLowerCase().includes(q) ||
            a.especie_nome?.toLowerCase().includes(q)
        )
      }
      if (id_especie) {
        lista = lista.filter((a) => a.id_especie === Number(id_especie))
      }
      if (estado) {
        lista = lista.filter((a) => a.estado === estado)
      }
      return lista
    },

    idsMatrizesFiltradas() {
      return new Set(this.matrizesFiltradas.map((m) => m.id))
    },

    coletasFiltradas() {
      return this.coletas.filter((c) => this.idsMatrizesFiltradas.has(c.id_arvore_matriz))
    },

    lotesFiltrados() {
      return this.lotes.filter((l) => this.idsMatrizesFiltradas.has(l.id_arvore_matriz))
    },

    coletasDaMatriz: (state) => (idMatriz) =>
      state.coletas
        .filter((c) => c.id_arvore_matriz === idMatriz)
        .sort((a, b) => new Date(b.data_coleta) - new Date(a.data_coleta)),

    lotesDaMatriz: (state) => (idMatriz) =>
      state.lotes.filter((l) => l.id_arvore_matriz === idMatriz),

    testesDaMatriz: (state) => (idMatriz) => {
      const idsLote = new Set(state.lotes.filter((l) => l.id_arvore_matriz === idMatriz).map((l) => l.id))
      return state.testes.filter((t) => idsLote.has(t.id_lote_sementes))
    },

    semeadurasDaMatriz: (state) => (idMatriz) => {
      const idsLote = new Set(state.lotes.filter((l) => l.id_arvore_matriz === idMatriz).map((l) => l.id))
      return state.semeaduras.filter((s) => idsLote.has(s.id_lote_sementes))
    },

    especiesParaFiltro(state) {
      const map = new Map()
      state.arvoresMatriz.forEach((a) => {
        if (a.id_especie) {
          map.set(a.id_especie, a.especie_nome || `Espécie #${a.id_especie}`)
        }
      })
      return [...map.entries()]
        .map(([id, nome]) => ({ id, nome }))
        .sort((a, b) => a.nome.localeCompare(b.nome))
    },

    matrizesParaGrafico() {
      return [...this.matrizesFiltradas].sort((a, b) => a.nome.localeCompare(b.nome))
    },

    estadosParaFiltro(state) {
      return [...new Set(state.arvoresMatriz.map((a) => a.estado).filter(Boolean))].sort()
    },

    temFiltroAtivo(state) {
      const { busca, id_especie, estado } = state.filtros
      return Boolean(busca?.trim() || id_especie || estado)
    }
  },

  actions: {
    async carregar() {
      this.carregando = true
      this.erro = null
      try {
        const [matrizes, coletas, lotes, testes, semeaduras] = await Promise.all([
          listArvoresMatriz(),
          listColetasSementes().catch(() => []),
          listLotesSementes().catch(() => []),
          listTestesSementes().catch(() => []),
          listSemeaduras().catch(() => [])
        ])
        this.arvoresMatriz = matrizes
        this.coletas = coletas
        this.lotes = lotes
        this.testes = testes
        this.semeaduras = semeaduras
      } catch (e) {
        this.erro = e.response?.data?.detail || e.message || 'Erro ao carregar dados de coleta'
        this.arvoresMatriz = []
        this.coletas = []
        this.lotes = []
        this.testes = []
        this.semeaduras = []
      } finally {
        this.carregando = false
      }
    },

    async recarregarMatriz(idMatriz) {
      const matrizes = await listArvoresMatriz()
      const atualizada = matrizes.find((m) => m.id === idMatriz)
      if (atualizada) {
        const idx = this.arvoresMatriz.findIndex((a) => a.id === idMatriz)
        if (idx !== -1) this.arvoresMatriz[idx] = atualizada
        if (this.matrizSelecionada?.id === idMatriz) {
          this.matrizSelecionada = atualizada
        }
      }
      const [coletas, lotes, testes, semeaduras] = await Promise.all([
        listColetasSementes({ id_arvore_matriz: idMatriz }),
        listLotesSementes({ id_arvore_matriz: idMatriz }),
        listTestesSementes({ id_arvore_matriz: idMatriz }),
        listSemeaduras({ id_arvore_matriz: idMatriz })
      ])
      this.coletas = [
        ...this.coletas.filter((c) => c.id_arvore_matriz !== idMatriz),
        ...coletas
      ]
      this.lotes = [...this.lotes.filter((l) => l.id_arvore_matriz !== idMatriz), ...lotes]
      this.testes = [
        ...this.testes.filter((t) => !lotes.some((l) => l.id === t.id_lote_sementes)),
        ...testes
      ]
      this.semeaduras = [
        ...this.semeaduras.filter((s) => !lotes.some((l) => l.id === s.id_lote_sementes)),
        ...semeaduras
      ]
    },

    async cadastrar(payload) {
      const criada = await createArvoreMatriz(payload)
      this.arvoresMatriz.unshift(criada)
      return criada
    },

    async atualizar(id, payload) {
      const atualizada = await updateArvoreMatriz(id, payload)
      const idx = this.arvoresMatriz.findIndex((a) => a.id === id)
      if (idx !== -1) this.arvoresMatriz[idx] = atualizada
      if (this.matrizSelecionada?.id === id) {
        this.matrizSelecionada = atualizada
      }
      return atualizada
    },

    async remover(id) {
      await deleteArvoreMatriz(id)
      this.arvoresMatriz = this.arvoresMatriz.filter((a) => a.id !== id)
      this.coletas = this.coletas.filter((c) => c.id_arvore_matriz !== id)
      this.lotes = this.lotes.filter((l) => l.id_arvore_matriz !== id)
      if (this.matrizSelecionada?.id === id) {
        this.matrizSelecionada = null
      }
    },

    async registrarColeta(payload) {
      const criada = await createColetaSementes(payload)
      this.coletas.unshift(criada)
      if (criada.lotes?.length) {
        this.lotes.unshift(...criada.lotes)
      }
      await this.recarregarMatriz(criada.id_arvore_matriz)
      return criada
    },

    async atualizarColeta(id, payload) {
      const atualizada = await updateColetaSementes(id, payload)
      const idx = this.coletas.findIndex((c) => c.id === id)
      if (idx !== -1) this.coletas[idx] = atualizada
      await this.recarregarMatriz(atualizada.id_arvore_matriz)
      return atualizada
    },

    async removerColeta(id) {
      const coleta = this.coletas.find((c) => c.id === id)
      await deleteColetaSementes(id)
      this.coletas = this.coletas.filter((c) => c.id !== id)
      if (coleta) {
        this.lotes = this.lotes.filter((l) => l.id_coleta_sementes !== id)
        await this.recarregarMatriz(coleta.id_arvore_matriz)
      }
    },

    async atualizarLote(id, payload) {
      const atualizado = await updateLoteSementes(id, payload)
      const idx = this.lotes.findIndex((l) => l.id === id)
      if (idx !== -1) this.lotes[idx] = atualizado
      await this.recarregarMatriz(atualizado.id_arvore_matriz)
      return atualizado
    },

    upsertTeste(teste) {
      const idx = this.testes.findIndex((t) => t.id === teste.id)
      if (idx === -1) this.testes.unshift(teste)
      else this.testes[idx] = teste
    },

    removeTeste(id) {
      this.testes = this.testes.filter((t) => t.id !== id)
    },

    upsertSemeadura(semeadura) {
      const idx = this.semeaduras.findIndex((s) => s.id === semeadura.id)
      if (idx === -1) this.semeaduras.unshift(semeadura)
      else this.semeaduras[idx] = semeadura
      const loteIdx = this.lotes.findIndex((l) => l.id === semeadura.id_lote_sementes)
      if (loteIdx !== -1) {
        listLotesSementes({ id_coleta_sementes: this.lotes[loteIdx].id_coleta_sementes }).then(
          (lotes) => {
            lotes.forEach((l) => {
              const i = this.lotes.findIndex((x) => x.id === l.id)
              if (i !== -1) this.lotes[i] = l
            })
          }
        )
      }
    },

    selecionar(matriz) {
      this.matrizSelecionada = matriz
    },

    limparSelecao() {
      this.matrizSelecionada = null
    },

    limparFiltros() {
      this.filtros.busca = ''
      this.filtros.id_especie = ''
      this.filtros.estado = ''
    }
  }
})
