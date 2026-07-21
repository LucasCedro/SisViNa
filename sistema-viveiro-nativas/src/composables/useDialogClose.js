/** `<dialog>` somente leitura — backdrop e Escape nativos. */
export function useDialogClose(dialogRef, { onAfterClose } = {}) {
  function fecharDialog() {
    dialogRef.value?.close()
    onAfterClose?.()
  }

  return { fecharDialog }
}
