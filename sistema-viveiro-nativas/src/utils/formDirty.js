import { computed, ref, toRaw, unref, watch } from 'vue'

export function snapshotForm(value) {
  try {
    return JSON.parse(JSON.stringify(toRaw(unref(value))))
  } catch {
    return null
  }
}

/** Compara formulário com snapshot tirado ao abrir o modal. */
export function useFormDirty(form, isOpen) {
  const baseline = ref(null)

  watch(
    () => unref(isOpen),
    (open) => {
      if (open) baseline.value = snapshotForm(form)
      else baseline.value = null
    },
    { immediate: true },
  )

  const isDirty = computed(() => {
    if (baseline.value == null) return false
    const atual = snapshotForm(form)
    if (atual == null) return false
    return JSON.stringify(atual) !== JSON.stringify(baseline.value)
  })

  function rebase() {
    baseline.value = snapshotForm(form)
  }

  return { isDirty, rebase }
}
