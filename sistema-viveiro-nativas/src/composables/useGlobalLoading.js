import { storeToRefs } from 'pinia'
import { useLoadingStore } from '@/store/loading'

export function useGlobalLoading() {
  const store = useLoadingStore()
  const { visible, message } = storeToRefs(store)

  return {
    visible,
    message,
    runWithLoading: store.run,
    beginLoading: store.begin,
    endLoading: store.end,
  }
}
