import { defineStore } from 'pinia'
import { ref } from 'vue'

/** Só exibe overlay após este tempo — evita piscar em operações rápidas. */
const SHOW_DELAY_MS = 400

export const useLoadingStore = defineStore('loading', () => {
  const depth = ref(0)
  const message = ref('Processando…')
  const visible = ref(false)

  let delayTimer = null

  function begin(msg) {
    if (msg) message.value = msg
    depth.value += 1
    if (depth.value === 1) {
      delayTimer = setTimeout(() => {
        if (depth.value > 0) visible.value = true
      }, SHOW_DELAY_MS)
    }
  }

  function end() {
    depth.value = Math.max(0, depth.value - 1)
    if (depth.value === 0) {
      if (delayTimer) {
        clearTimeout(delayTimer)
        delayTimer = null
      }
      visible.value = false
    }
  }

  /** Executa promise com overlay global (contador aninhado). */
  async function run(fn, msg = 'Processando…') {
    begin(msg)
    try {
      return await fn()
    } finally {
      end()
    }
  }

  return { visible, message, begin, end, run }
})
