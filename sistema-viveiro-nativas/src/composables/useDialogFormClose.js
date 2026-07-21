import { unref } from 'vue'

import { useUnsavedFormGuard } from '@/composables/useUnsavedFormGuard'

/** `<dialog>` nativo + confirmação ao sair com formulário preenchido. */
export function useDialogFormClose(dialogRef, { isDirty, onAfterClose } = {}) {
  const resolver = () => (typeof isDirty === 'function' ? isDirty() : Boolean(unref(isDirty)))

  const guard = useUnsavedFormGuard({
    isDirty: resolver,
    onExit: () => {
      dialogRef.value?.close()
      onAfterClose?.()
    },
  })

  function onDialogCancel(event) {
    if (resolver()) {
      event.preventDefault()
      guard.confirmAberto.value = true
    }
  }

  return {
    ...guard,
    onDialogCancel,
    fecharDialog: guard.requestClose,
    sairSemConfirmar: guard.executarSaida,
  }
}
