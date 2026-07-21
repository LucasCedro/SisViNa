import { onBeforeUnmount, unref, watch } from 'vue'

function resolveIsOpen(isOpen) {
  if (isOpen == null) return false
  if (typeof isOpen === 'function') return Boolean(isOpen())
  return Boolean(unref(isOpen))
}

/** Fecha modal com Escape enquanto `isOpen` estiver true. */
export function useModalEscape(onClose, isOpen) {
  let removeListener = null

  function detach() {
    if (removeListener) {
      removeListener()
      removeListener = null
    }
  }

  watch(
    () => resolveIsOpen(isOpen),
    (open) => {
      detach()
      if (!open) return
      const onKey = (e) => {
        if (e.key !== 'Escape') return
        e.preventDefault()
        onClose()
      }
      document.addEventListener('keydown', onKey)
      removeListener = () => document.removeEventListener('keydown', onKey)
    },
    { immediate: true },
  )

  onBeforeUnmount(detach)
}
