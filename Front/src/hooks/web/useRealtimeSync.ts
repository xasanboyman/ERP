import { onMounted, onUnmounted, computed } from 'vue'
import { realtimeService, type RealtimeEvent } from '@/utils/realtimeSync'

export interface UseRealtimeSyncOptions {
  debounceMs?: number
  immediate?: boolean
}

export function useRealtimeSync(
  entities: string | string[],
  callback: (event: RealtimeEvent) => void | Promise<void>,
  options: UseRealtimeSyncOptions = {}
) {
  const { debounceMs = 150 } = options
  const unsubs: Array<() => void> = []

  let timer: any = null
  let pendingEvents: RealtimeEvent[] = []

  const debouncedHandler = (event: RealtimeEvent) => {
    if (debounceMs <= 0) {
      callback(event)
      return
    }

    pendingEvents.push(event)
    if (timer) {
      clearTimeout(timer)
    }

    timer = setTimeout(() => {
      const lastEvent = pendingEvents[pendingEvents.length - 1]
      pendingEvents = []
      timer = null
      if (lastEvent) {
        callback(lastEvent)
      }
    }, debounceMs)
  }

  const register = () => {
    const list = Array.isArray(entities) ? entities : [entities]
    list.forEach((entity) => {
      if (entity === '*' || entity === 'all') {
        unsubs.push(realtimeService.onAll(debouncedHandler))
      } else {
        unsubs.push(realtimeService.on(entity, debouncedHandler))
      }
    })
  }

  const cleanup = () => {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
    unsubs.forEach((unsub) => unsub())
    unsubs.length = 0
  }

  onMounted(() => {
    register()
  })

  onUnmounted(() => {
    cleanup()
  })

  const isConnected = computed(() => realtimeService.status.value === 'connected')
  const connectionStatus = computed(() => realtimeService.status.value)

  return {
    isConnected,
    connectionStatus,
    realtimeService
  }
}
