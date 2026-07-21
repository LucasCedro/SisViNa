/**
 * Fecha overlay só se pointerdown e pointerup ocorrerem no fundo escuro.
 * Evita fechar ao selecionar texto no formulário e soltar fora do modal.
 * Com `isOpen`, também fecha com Escape.
 */
import { useModalEscape } from '@/composables/useModalEscape'

export function useModalOverlayClose(onClose, isOpen = null) {
  let overlayPress = false

  if (isOpen != null) {
    useModalEscape(onClose, isOpen)
  }

  function onModalPointerDown() {
    overlayPress = false
  }

  function onOverlayPointerDown() {
    overlayPress = true
  }

  function onOverlayPointerUp() {
    if (overlayPress) onClose()
    overlayPress = false
  }

  function cancelarFechamentoOverlay() {
    overlayPress = false
  }

  function resetOverlayPress() {
    overlayPress = false
  }

  return {
    onModalPointerDown,
    onOverlayPointerDown,
    onOverlayPointerUp,
    cancelarFechamentoOverlay,
    resetOverlayPress,
  }
}
