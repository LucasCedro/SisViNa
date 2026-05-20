<template>
  <div id="relatorio-coleta-pdf" class="pdf-root">
    <h1>Relatório de coleta de sementes — SisViNa</h1>
    <p class="meta">Gerado em {{ dataGeracao }}</p>
    <section>
      <h2>Resumo</h2>
      <p>{{ store.arvoresMatriz.length }} matrizes · {{ store.coletas.length }} coletas · {{ store.lotes.length }} lotes</p>
    </section>
    <section v-if="store.matrizSelecionada">
      <h2>Matriz selecionada: {{ store.matrizSelecionada.nome }}</h2>
      <p>Espécie: {{ store.matrizSelecionada.especie_nome }}</p>
      <p>Origem: {{ labelTipoOrigem(store.matrizSelecionada.tipo_origem) }}</p>
      <p>Autorização: {{ store.matrizSelecionada.numero_autorizacao || '—' }}</p>
      <p>Fenologia: {{ janelaFrutificacao(store.matrizSelecionada) }}</p>
    </section>
    <section>
      <h2>Matrizes (amostra)</h2>
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Espécie</th>
            <th>Origem</th>
            <th>Sementes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in store.matrizesFiltradas.slice(0, 40)" :key="m.id">
            <td>{{ m.nome }}</td>
            <td>{{ m.especie_nome }}</td>
            <td>{{ labelTipoOrigem(m.tipo_origem) }}</td>
            <td>{{ m.sementes_coletadas }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { useColetaStore } from '@/store/coleta'
import { labelTipoOrigem, janelaFrutificacao } from '@/constants/coletaDominio'

const store = useColetaStore()
const dataGeracao = new Date().toLocaleString('pt-BR')
</script>

<style scoped>
.pdf-root {
  position: fixed;
  left: -9999px;
  top: 0;
  width: 800px;
  padding: 24px;
  font-family: Arial, sans-serif;
  font-size: 12px;
  color: #111;
  background: #fff;
}
.pdf-root h1 {
  font-size: 18px;
  margin-bottom: 8px;
}
.pdf-root h2 {
  font-size: 14px;
  margin: 16px 0 8px;
}
.meta {
  color: #666;
  margin-bottom: 16px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  border: 1px solid #ccc;
  padding: 4px 6px;
  text-align: left;
}
</style>
