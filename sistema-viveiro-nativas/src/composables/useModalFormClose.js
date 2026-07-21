import { unref } from 'vue'

import { useModalOverlayClose } from '@/composables/useModalOverlayClose'
import { useUnsavedFormGuard } from '@/composables/useUnsavedFormGuard'

/** Overlay + Escape + confirmação ao sair com formulário preenchido. */
export function useModalFormClose(onClose, isDirty, isOpen = null) {
  const resolver = () => (typeof isDirty === 'function' ? isDirty() : Boolean(unref(isDirty)))

  const guard = useUnsavedFormGuard({
    isDirty: resolver,
    onExit: onClose,
  })

  function requestCloseSafe() {
    if (guard.confirmAberto.value) return
    guard.requestClose()
  }

  function modalOverlayOpen() {
    if (guard.confirmAberto.value) return false
    if (isOpen == null) return false
    if (typeof isOpen === 'function') return Boolean(isOpen())
    return Boolean(unref(isOpen))
  }

  const overlay = useModalOverlayClose(requestCloseSafe, modalOverlayOpen)

  return {
    ...overlay,
    confirmAberto: guard.confirmAberto,
    confirmarSaida: guard.confirmarSaida,
    cancelarSaida: guard.cancelarSaida,
    requestClose: guard.requestClose,
    sairSemConfirmar: guard.executarSaida,
  }
}
