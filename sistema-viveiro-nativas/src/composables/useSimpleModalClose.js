import { useModalOverlayClose } from '@/composables/useModalOverlayClose'

/** Modal somente leitura — overlay, Escape, sem confirmação de saída. */
export function useSimpleModalClose(onClose, isOpen) {
  return useModalOverlayClose(onClose, isOpen)
}
