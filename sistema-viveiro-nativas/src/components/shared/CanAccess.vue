<template>
  <slot v-if="allowed" />
</template>

<script setup>
import { computed } from 'vue'
import { usePermissions } from '@/composables/usePermissions'

const props = defineProps({
  /** Permissão única — ex.: `coleta.create` */
  permission: { type: String, default: '' },
  /** Qualquer uma das permissões (OR) */
  any: { type: Array, default: () => [] },
  /** Todas as permissões (AND) */
  all: { type: Array, default: () => [] },
})

const { can, canAny } = usePermissions()

const allowed = computed(() => {
  if (props.all.length) return props.all.every((p) => can(p))
  if (props.any.length) return canAny(...props.any)
  if (props.permission) return can(props.permission)
  return false
})
</script>
