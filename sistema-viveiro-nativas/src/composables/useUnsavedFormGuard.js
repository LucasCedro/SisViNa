import { ref, unref } from 'vue'

/**
 * Intercepta fechamento quando o formulário tem alterações não salvas.
 */
export function useUnsavedFormGuard({ isDirty, onExit }) {
  const confirmAberto = ref(false)

  function resolveDirty() {
    if (typeof isDirty === 'function') return Boolean(isDirty())
    return Boolean(unref(isDirty))
  }

  function executarSaida() {
    confirmAberto.value = false
    onExit()
  }

  function requestClose() {
    if (resolveDirty()) confirmAberto.value = true
    else executarSaida()
  }

  function confirmarSaida() {
    executarSaida()
  }

  function cancelarSaida() {
    confirmAberto.value = false
  }

  return {
    confirmAberto,
    requestClose,
    confirmarSaida,
    cancelarSaida,
    executarSaida,
    sairSemConfirmar: executarSaida,
  }
}
