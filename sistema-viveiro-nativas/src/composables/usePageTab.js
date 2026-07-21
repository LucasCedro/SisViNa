import { ref, watch, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'

const PREFIX = 'sisvina:tab:'

function fullKey(routeKey, subKey) {
  const base = `${PREFIX}${routeKey}`
  return subKey ? `${base}:${subKey}` : base
}

function isValidTab(tab, valid) {
  if (tab == null || tab === '') return false
  if (Array.isArray(valid)) return valid.includes(tab)
  if (typeof valid === 'function') return valid(tab)
  return true
}

/**
 * Persiste guia/aba no refresh (sessionStorage), mas reseta ao navegar para outra página.
 *
 * @param {string} routeKey — nome da rota (router name), ex.: 'estoques'
 * @param {string} defaultTab — guia inicial ao entrar na página
 * @param {{ valid?: string[]|function, subKey?: string, queryResolver?: (route) => string|null }} [options]
 */
export function usePageTab(routeKey, defaultTab, options = {}) {
  const { valid = null, subKey = null, queryResolver = null } = options
  const route = useRoute()
  const key = fullKey(routeKey, subKey)
  const tab = ref(defaultTab)

  function read() {
    try {
      const v = sessionStorage.getItem(key)
      return isValidTab(v, valid) ? v : null
    } catch {
      return null
    }
  }

  function write(value) {
    try {
      if (isValidTab(value, valid)) sessionStorage.setItem(key, value)
    } catch {
      /* quota / privado */
    }
  }

  function applyFromQuery() {
    if (!queryResolver) return false
    const fromQuery = queryResolver(route)
    if (fromQuery && isValidTab(fromQuery, valid)) {
      tab.value = fromQuery
      write(fromQuery)
      return true
    }
    return false
  }

  function restore() {
    if (applyFromQuery()) return
    const stored = read()
    tab.value = stored ?? defaultTab
  }

  onMounted(restore)

  if (queryResolver) {
    watch(
      () => route.query,
      () => {
        applyFromQuery()
      }
    )
  }

  watch(tab, (v) => {
    if (isValidTab(v, valid)) write(v)
  })

  return tab
}

/**
 * Estado composto (ex.: grupo + aba na Contabilidade).
 */
export function usePageTabBundle(routeKey, defaults, options = {}) {
  const { validate = null } = options
  const key = fullKey(routeKey)
  const state = reactive({ ...defaults })

  function read() {
    try {
      const raw = sessionStorage.getItem(key)
      if (!raw) return null
      const parsed = JSON.parse(raw)
      if (validate && !validate(parsed)) return null
      return parsed
    } catch {
      return null
    }
  }

  function write() {
    try {
      sessionStorage.setItem(key, JSON.stringify({ ...state }))
    } catch {
      /* ignore */
    }
  }

  onMounted(() => {
    const stored = read()
    if (stored) Object.assign(state, { ...defaults, ...stored })
  })

  watch(state, write, { deep: true })

  return state
}

/** Limpa guias salvas ao sair da página (chamado no router afterEach). */
export function clearPageTabStorage(routeKey) {
  if (!routeKey) return
  const prefix = fullKey(routeKey)
  try {
    for (let i = sessionStorage.length - 1; i >= 0; i--) {
      const k = sessionStorage.key(i)
      if (k && (k === prefix || k.startsWith(`${prefix}:`))) {
        sessionStorage.removeItem(k)
      }
    }
  } catch {
    /* ignore */
  }
}
