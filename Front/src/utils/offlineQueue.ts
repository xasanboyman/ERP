/**
 * Offline Sync Queue & Auto-Purge Manager
 *
 * Features:
 * 1. Safely queues pending actions/edits if network drops.
 * 2. As soon as connection is restored, immediately flushes all pending items to the server.
 * 3. INSTANTLY PURGES successfully synced items from storage so they NEVER cause duplicates or memory bloat in the future.
 * 4. Triggers full background table refresh so local views catch up with the latest server state.
 */

import axios from 'axios'
import { ElNotification } from 'element-plus'
import { realtimeService } from './realtimeSync'

export interface PendingAction {
  id: string
  title: string
  url: string
  method: 'POST' | 'PUT' | 'DELETE'
  payload: any
  timestamp: number
  retryCount: number
}

const STORAGE_KEY = 'erp_pending_offline_actions'

class OfflineQueueManager {
  private queue: PendingAction[] = []
  private isProcessing = false

  constructor() {
    this.loadFromStorage()
    this.setupListeners()
  }

  private loadFromStorage(): void {
    if (typeof window === 'undefined') return
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) {
        this.queue = JSON.parse(raw)
      }
    } catch {
      this.queue = []
      this.clearStorage()
    }
  }

  private saveToStorage(): void {
    if (typeof window === 'undefined') return
    try {
      if (this.queue.length === 0) {
        this.clearStorage()
      } else {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.queue))
      }
    } catch (err) {
      console.warn('[OfflineQueue] Storage quota or write error:', err)
    }
  }

  private clearStorage(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem(STORAGE_KEY)
  }

  private setupListeners(): void {
    if (typeof window === 'undefined') return

    // Reconnect on browser online event
    window.addEventListener('online', () => {
      console.log('[OfflineQueue] Network is online. Flushing queue...')
      this.flushQueue()
    })

    // Reconnect when WebSocket connects
    realtimeService.onAll((event) => {
      if (event.type === 'connection_ack') {
        this.flushQueue()
      }
    })
  }

  /**
   * Enqueue a pending mutation that failed due to network loss
   */
  public enqueue(action: Omit<PendingAction, 'id' | 'timestamp' | 'retryCount'>): void {
    const item: PendingAction = {
      ...action,
      id: `queue_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
      timestamp: Date.now(),
      retryCount: 0
    }

    this.queue.push(item)
    this.saveToStorage()

    ElNotification({
      title: 'Oflayn rejim',
      message: `Tarmoq uzildi. "${item.title}" saqlandi va internet ulanganda avtomatik yuboriladi.`,
      type: 'warning',
      duration: 4000
    })
  }

  /**
   * Process and flush all pending actions to server sequentially
   */
  public async flushQueue(): Promise<void> {
    if (this.isProcessing || this.queue.length === 0) return
    this.isProcessing = true

    console.log(`[OfflineQueue] Processing ${this.queue.length} pending actions...`)
    const remaining: PendingAction[] = []

    for (const item of this.queue) {
      try {
        const response = await axios({
          url: item.url,
          method: item.method,
          data: item.payload,
          timeout: 10000
        })

        if (response.status >= 200 && response.status < 300) {
          console.log(
            `[OfflineQueue] Successfully synced and PURGED action: ${item.id} (${item.title})`
          )
          // Item is intentionally NOT added to 'remaining', thus 100% purged!
          ElNotification({
            title: 'Sinxronizatsiya muvaffaqiyatli',
            message: `"${item.title}" serverga muvaffaqiyatli yetkazildi va xotiradan tozalindi.`,
            type: 'success',
            duration: 3500
          })
        } else {
          // Server returned error (e.g. 400 validation error) - discard to prevent toxic queue block
          console.warn(`[OfflineQueue] Discarding invalid action ${item.id}:`, response.data)
        }
      } catch (err: any) {
        if (!navigator.onLine || err.code === 'ERR_NETWORK' || !err.response) {
          // Truly still offline, keep in queue
          item.retryCount++
          remaining.push(item)
          break // Stop processing until connection improves
        } else {
          // Server error or 4xx, discard so queue is not permanently clogged
          console.warn(`[OfflineQueue] Purging failing item ${item.id}:`, err.message)
        }
      }
    }

    this.queue = remaining
    this.saveToStorage()
    this.isProcessing = false

    // Notify all active Vue views to silently refresh their data to match the new server state
    realtimeService.connect()
  }

  public getPendingCount(): number {
    return this.queue.length
  }

  public clearAll(): void {
    this.queue = []
    this.clearStorage()
  }
}

export const offlineQueue = new OfflineQueueManager()
