import { ref } from 'vue'

export interface RealtimeEvent {
  type: string
  event: string
  entity: string
  action: string
  id?: string | null
  data?: Record<string, any> | null
  actor?: string
  timestamp?: string
}

type EventHandler = (event: RealtimeEvent) => void

class RealtimeService {
  private ws: WebSocket | null = null
  private listeners: Map<string, Set<EventHandler>> = new Map()
  private globalListeners: Set<EventHandler> = new Set()
  private reconnectAttempts = 0
  private maxReconnectDelay = 10000
  private reconnectTimer: any = null
  private pingInterval: any = null
  private isExplicitClose = false

  public status = ref<'connected' | 'connecting' | 'disconnected'>('disconnected')

  constructor() {
    // Normalization aliases so listeners can subscribe to either singular or plural/domain
    // e.g. "product" matches "products", "cutting" matches "cutting_order", "cutting_task", etc.
  }

  private normalizeEntity(entity: string): string {
    if (!entity) return ''
    const lower = entity.toLowerCase().trim()
    if (lower.startsWith('product')) return 'product'
    if (lower.startsWith('sale') && !lower.includes('push')) return 'sale'
    if (lower.includes('push')) return 'sales_push'
    if (lower.startsWith('worker')) return 'worker'
    if (lower.startsWith('salary')) return 'salary'
    if (
      lower.startsWith('staff') ||
      lower.includes('timesheet') ||
      lower.includes('output') ||
      lower.includes('adjustment')
    )
      return 'staff_hr'
    if (lower.startsWith('device')) return 'device'
    if (lower.startsWith('debt')) return 'debt'
    return lower
  }

  public getWsUrl(): string {
    const isHttps = typeof window !== 'undefined' && window.location.protocol === 'https:'
    const protocol = isHttps ? 'wss:' : 'ws:'
    const host = typeof window !== 'undefined' ? window.location.host : '127.0.0.1:4000'
    return `${protocol}//${host}/api/ws/events`
  }

  public connect(): void {
    if (typeof window === 'undefined') return
    // Vercel serverless functions do not host persistent WebSockets
    if (window.location.hostname.includes('vercel.app')) {
      this.status.value = 'disconnected'
      return
    }
    if (this.reconnectAttempts >= 3) {
      this.status.value = 'disconnected'
      return
    }
    if (
      this.ws &&
      (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)
    ) {
      return
    }

    this.isExplicitClose = false
    this.status.value = 'connecting'
    const url = this.getWsUrl()

    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        const wasDisconnected = this.status.value === 'disconnected' || this.reconnectAttempts > 0
        this.status.value = 'connected'
        this.reconnectAttempts = 0
        this.startHeartbeat()
        console.log('[RealtimeSync] WebSocket connected successfully.')
        if (wasDisconnected) {
          // Trigger global catch-up event so all views silently refresh latest data
          this.handleIncomingEvent({
            type: 'connection_restored',
            event: 'connection_restored',
            entity: 'all',
            action: 'sync'
          })
        }
      }

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const payload = JSON.parse(event.data)
          if (payload.type === 'pong') return
          this.handleIncomingEvent(payload)
        } catch (e) {
          console.debug('[RealtimeSync] Non-JSON message:', event.data)
        }
      }

      this.ws.onclose = () => {
        this.status.value = 'disconnected'
        this.stopHeartbeat()
        if (!this.isExplicitClose && this.reconnectAttempts < 3) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = () => {
        // Silently handle error without uncaught exceptions
        this.status.value = 'disconnected'
      }
    } catch (err) {
      this.status.value = 'disconnected'
      if (this.reconnectAttempts < 3) {
        this.scheduleReconnect()
      }
    }
  }

  public disconnect(): void {
    this.isExplicitClose = true
    this.stopHeartbeat()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.status.value = 'disconnected'
  }

  private startHeartbeat(): void {
    this.stopHeartbeat()
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }))
      }
    }, 25000)
  }

  private stopHeartbeat(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer || this.isExplicitClose || this.reconnectAttempts >= 3) return
    this.reconnectAttempts++
    const delay = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts), this.maxReconnectDelay)
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      this.connect()
    }, delay)
  }

  private handleIncomingEvent(event: RealtimeEvent): void {
    if (!event || (!event.entity && !event.type)) return

    // Notify global listeners
    this.globalListeners.forEach((handler) => {
      try {
        handler(event)
      } catch (err) {
        console.error('[RealtimeSync] Handler error:', err)
      }
    })

    if (event.entity === 'all') {
      this.listeners.forEach((set) => {
        set.forEach((handler) => {
          try {
            handler(event)
          } catch (err) {
            console.error('[RealtimeSync] Entity broadcast error:', err)
          }
        })
      })
    } else if (event.entity) {
      const normalized = this.normalizeEntity(event.entity)
      const exactSet = this.listeners.get(event.entity.toLowerCase())
      const normSet = this.listeners.get(normalized)

      const targetHandlers = new Set<EventHandler>()
      if (exactSet) exactSet.forEach((h) => targetHandlers.add(h))
      if (normSet) normSet.forEach((h) => targetHandlers.add(h))

      targetHandlers.forEach((handler) => {
        try {
          handler(event)
        } catch (err) {
          console.error('[RealtimeSync] Entity handler error:', err)
        }
      })
    }
  }

  public on(entity: string, handler: EventHandler): () => void {
    const key = this.normalizeEntity(entity)
    if (!this.listeners.has(key)) {
      this.listeners.set(key, new Set())
    }
    this.listeners.get(key)!.add(handler)

    // Ensure connection is active
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.connect()
    }

    return () => this.off(entity, handler)
  }

  public off(entity: string, handler: EventHandler): void {
    const key = this.normalizeEntity(entity)
    const set = this.listeners.get(key)
    if (set) {
      set.delete(handler)
      if (set.size === 0) {
        this.listeners.delete(key)
      }
    }
  }

  public onAll(handler: EventHandler): () => void {
    this.globalListeners.add(handler)
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.connect()
    }
    return () => {
      this.globalListeners.delete(handler)
    }
  }
}

export const realtimeService = new RealtimeService()
