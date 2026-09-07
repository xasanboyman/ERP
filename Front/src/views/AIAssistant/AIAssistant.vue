<template>
  <div class="ai-assistant-wrapper">
    <!-- Floating Orb Trigger Button -->
    <div class="orb-container">
      <button
        class="ai-trigger-orb"
        :class="{ 'is-active': isOpen, 'is-listening': clientStatus === 'connected' }"
        @click="togglePanel"
        :title="isOpen ? 'Yopish' : 'AI Yordamchi'"
      >
        <div class="orb-pulse-glow"></div>
        <div class="orb-pulse-glow-secondary"></div>
        <div class="orb-content">
          <!-- Animated AI Brain/Spark Icon -->
          <svg
            v-if="!isOpen"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            width="24"
            height="24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M12 2a8 8 0 0 0-8 8c0 3.32 2.02 6.17 4.9 7.37L9 22l3-1.5L15 22l.1-4.63A8.002 8.002 0 0 0 20 10a8 8 0 0 0-8-8z"
            />
            <circle cx="9" cy="10" r="1" fill="currentColor" />
            <circle cx="15" cy="10" r="1" fill="currentColor" />
            <path d="M9.5 14a3.5 3.5 0 0 0 5 0" />
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            width="22"
            height="22"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </div>
      </button>

      <!-- Mini Float Tag -->
      <div v-if="!isOpen" class="ai-badge-label" @click="togglePanel">
        <span class="ai-badge-dot"></span>
        <span>AI Yordamchi</span>
      </div>
    </div>

    <!-- Glassmorphic Dialog Panel -->
    <transition name="slide-up">
      <div v-if="isOpen" class="ai-glass-panel">
        <!-- Header -->
        <div class="panel-header">
          <div class="header-title-box">
            <span class="pulse-indicator" :class="clientStatus"></span>
            <div>
              <h2 class="header-title">Knit ERP AI</h2>
              <p class="header-status">
                {{
                  clientStatus === 'connected'
                    ? 'Ovozli rejimda (Tinglanmoqda...)'
                    : clientStatus === 'connecting'
                      ? "Bog'lanmoqda..."
                      : 'Onlayn va buyruqlarga tayyor'
                }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="messages.length > 0"
              class="clear-chat-btn"
              @click="clearMessages"
              title="Tozalash"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="3 6 5 6 21 6" />
                <path
                  d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                />
              </svg>
            </button>
            <button class="close-btn" @click="isOpen = false">&times;</button>
          </div>
        </div>

        <!-- Chat / Transcript Logs -->
        <div class="panel-body" ref="logsContainer">
          <div class="welcome-card" v-if="messages.length === 0">
            <div class="welcome-icon"><Icon icon="ep:magic-stick" style="font-size: 32px" /></div>
            <h3>Qanday yordam bera olaman?</h3>
            <p>
              ERP tizimi, mahsulotlar, qarzlar, kassa va xodimlarni boshqarish bo'yicha tezkor savol
              yoki buyruq bering.
            </p>

            <!-- Quick Suggestions -->
            <div class="quick-chips">
              <button
                v-for="chip in quickChips"
                :key="chip.label"
                class="chip-btn inline-flex items-center gap-4px"
                @click="sendQuickChip(chip.prompt)"
              >
                <Icon :icon="chip.icon" />
                <span>{{ chip.label }}</span>
              </button>
            </div>
          </div>

          <div v-else class="chat-flow">
            <div
              v-for="(msg, idx) in messages"
              :key="idx"
              class="chat-bubble-wrapper"
              :class="msg.role"
            >
              <!-- API Request Log Badge -->
              <div v-if="msg.role === 'api'" class="api-log-card">
                <div class="api-log-header">
                  <span class="api-pulse-dot"></span>
                  <span class="api-tag-title"
                    ><Icon icon="ep:lightning" class="mr-4px text-amber-400" />HTTP API
                    REQUEST</span
                  >
                </div>
                <div v-if="msg.requests && msg.requests.length" class="api-url-box">
                  <div v-for="(req, rIdx) in msg.requests" :key="rIdx" class="api-url-row">
                    <span class="url-code">{{ req }}</span>
                  </div>
                </div>
                <div class="api-log-summary">{{ msg.text }}</div>
              </div>

              <!-- User or Model Chat Bubble -->
              <div v-else class="chat-bubble">
                <span class="bubble-role-label">{{
                  msg.role === 'user' ? 'Siz' : 'AI Yordamchi'
                }}</span>
                <p class="bubble-text whitespace-pre-wrap">{{ msg.text }}</p>
              </div>
            </div>

            <!-- Loading indicator -->
            <div v-if="isThinking" class="chat-bubble-wrapper model">
              <div class="chat-bubble thinking-bubble">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Voice Level & Harmonic Frequency Wave Visualizer -->
        <div class="visualizer-container" v-show="clientStatus === 'connected'">
          <div class="visualizer-header">
            <div class="tone-indicator">
              <span
                class="live-pulse-dot"
                :class="{ 'is-active': currentFreqData.level > 6 }"
              ></span>
              <span class="tone-badge">{{ activeToneLabel }}</span>
            </div>
            <div class="pitch-indicator">
              <span
                class="pitch-tag inline-flex items-center gap-4px"
                :class="{ 'is-high': currentFreqData.high > 25 }"
              >
                <Icon v-if="currentFreqData.high > 25" icon="ep:lightning" />
                <Icon v-else-if="currentFreqData.bass > 30" icon="ep:bell" />
                <Icon v-else icon="ep:microphone" />
                <span>{{
                  currentFreqData.high > 25
                    ? 'Yuqori Pitch'
                    : currentFreqData.bass > 30
                      ? 'Bas'
                      : 'Normal'
                }}</span>
              </span>
              <span class="db-meter">{{ Math.round(currentFreqData.level) }} dB</span>
            </div>
          </div>
          <canvas ref="waveCanvas" class="wave-canvas"></canvas>
        </div>

        <!-- Control Bar -->
        <div class="panel-controls">
          <!-- Connect / Mic Toggle -->
          <button
            class="action-voice-btn"
            :class="{ 'is-active': clientStatus === 'connected' }"
            @click="toggleVoiceConnection"
          >
            <span class="btn-icon">
              <svg
                v-if="clientStatus !== 'connected'"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                width="20"
                height="20"
                fill="currentColor"
              >
                <path
                  d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"
                />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                width="20"
                height="20"
                fill="currentColor"
              >
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
              </svg>
            </span>
            <span class="btn-text">
              {{ clientStatus === 'connected' ? "Ovozni o'chirish" : 'Ovozli rejim' }}
            </span>
          </button>

          <!-- Text input option (hybrid mode) -->
          <div class="text-input-box">
            <el-input
              v-model="textCommand"
              placeholder="Savol yoki buyruq yozing..."
              clearable
              @keyup.enter="handleTextSubmit"
            >
              <template #append>
                <el-button @click="handleTextSubmit" :disabled="isThinking">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    width="16"
                    height="16"
                    fill="currentColor"
                  >
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                  </svg>
                </el-button>
              </template>
            </el-input>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onUnmounted } from 'vue'
import { AIVoiceClient } from './AIVoiceClient'
import { dispatchAIFunction } from './aiDispatcher'
import { getDebtorsApi, getSalesListApi } from '@/api/sales'
import { getProductListApi } from '@/api/product'
import { getWorkerListApi } from '@/api/worker'
import request from '@/axios'
import { ElButton, ElInput } from 'element-plus'
import { Icon } from '@/components/Icon'

const isOpen = ref(false)
const clientStatus = ref<'disconnected' | 'connecting' | 'connected'>('disconnected')
const textCommand = ref('')
const isThinking = ref(false)
const messages = ref<{ role: 'user' | 'model' | 'api'; text: string; requests?: string[] }[]>([])
const waveCanvas = ref<HTMLCanvasElement>()
const logsContainer = ref<HTMLElement>()

const currentFreqData = ref<{
  raw: Uint8Array
  bass: number
  mid: number
  high: number
  level: number
  source: 'playback' | 'mic' | 'idle'
}>({
  raw: new Uint8Array(64),
  bass: 0,
  mid: 0,
  high: 0,
  level: 0,
  source: 'idle'
})

const activeToneLabel = computed(() => {
  if (currentFreqData.value.source === 'playback') {
    if (currentFreqData.value.high > 28) return 'AI Javobi (Yuqori Pitch / Ton)'
    if (currentFreqData.value.bass > 35) return 'AI Javobi (Chuqur Tembr)'
    return 'AI So‘zlamoqda (Ovozli)'
  }
  if (currentFreqData.value.source === 'mic') {
    if (currentFreqData.value.high > 30) return 'Sizning ovozingiz (Yuqori Pitch)'
    if (currentFreqData.value.bass > 32) return 'Sizning ovozingiz (Bas Tembr)'
    return 'Sizning ovozingiz (Vokal)'
  }
  return 'Tinglanmoqda (Jonli rejim)'
})

const quickChips = [
  {
    icon: 'ep:trophy',
    label: "Eng ko'p sotilganlar",
    prompt: "Qaysi mahsulotlar eng ko'p sotildi va eng ko'p tushum keltirdi?"
  },
  {
    icon: 'ep:data-analysis',
    label: 'Bugungi tushum',
    prompt: 'Bugungi tushum va savdolar qanday?'
  },
  {
    icon: 'ep:user',
    label: 'Nasiyalar (Qarzlar)',
    prompt: "Qarzdorlar ro'yxati va jami qarz qancha?"
  },
  { icon: 'ep:box', label: 'Ombor qoldiqlari', prompt: 'Ombordagi mahsulotlar qoldiqlari' },
  { icon: 'ep:avatar', label: "Xodimlar ro'yxati", prompt: "Xodimlar ro'yxatini ko'rsat" }
]

const client = new AIVoiceClient()

// Canvas Visualizer setup
let canvasCtx: CanvasRenderingContext2D | null = null
let audioLevel = 0

client.onStatusChange = (status) => {
  clientStatus.value = status
  if (status === 'connected') {
    initCanvas()
  }
}

client.onTranscription = (role, text, isFinal) => {
  if (isFinal) {
    messages.value.push({ role, text })
    scrollToBottom()
  }
}

client.onAudioLevel = (level) => {
  audioLevel = level
}

client.onFrequencyData = (data) => {
  currentFreqData.value = data
}

client.onToolExecution = (info) => {
  messages.value.push({
    role: 'api',
    text: info.message,
    requests: info.requests
  })
  scrollToBottom()
}

const togglePanel = async () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    await client.init()
    scrollToBottom()
  } else {
    client.disconnect()
  }
}

const toggleVoiceConnection = async () => {
  if (clientStatus.value === 'connected') {
    client.disconnect()
  } else {
    await client.connect()
  }
}

const clearMessages = () => {
  messages.value = []
}

const sendQuickChip = (promptText: string) => {
  textCommand.value = promptText
  handleTextSubmit()
}

const handleTextSubmit = async () => {
  const query = textCommand.value.trim()
  if (!query) return

  messages.value.push({ role: 'user', text: query })
  textCommand.value = ''
  isThinking.value = true
  scrollToBottom()

  try {
    const lowerQuery = query.toLowerCase()

    // 0. Top Selling Products & What did we sell most
    if (
      lowerQuery.includes("ko'p sotil") ||
      lowerQuery.includes('kop sotil') ||
      lowerQuery.includes('nima sotdik') ||
      lowerQuery.includes("eng ko'p") ||
      lowerQuery.includes('eng kop') ||
      lowerQuery.includes('top tovar') ||
      lowerQuery.includes('top mahsulot') ||
      lowerQuery.includes('top sotuv') ||
      lowerQuery.includes('sell most') ||
      lowerQuery.includes('best seller') ||
      lowerQuery.includes('hafta')
    ) {
      try {
        const topRes: any = await request.get({ url: '/sales/top-selling' })
        const topList = topRes?.data || []
        if (topList.length > 0) {
          let text = `Eng Ko'p Sotilgan Mahsulotlar Reytingi (Top Tovarlar):\n\n`
          topList.forEach((item: any, idx: number) => {
            text += `#${idx + 1}. ${item.name}\n   Sotildi: ${item.quantity} dona | Jami tushum: $${Number(item.revenue || 0).toLocaleString()} (${item.orders_count} ta chekda)\n\n`
          })
          messages.value.push({ role: 'model', text: text.trim() })
        } else {
          messages.value.push({
            role: 'model',
            text: 'Hozircha sotilgan tovarlar statistikasi mavjud emas.'
          })
        }
      } catch {
        messages.value.push({
          role: 'model',
          text: "Eng ko'p sotilgan tovarlar ma'lumotlarini yuklashda xatolik yuz berdi."
        })
      }
      isThinking.value = false
      scrollToBottom()
      return
    }

    // 1. Debtors & Nasiya check
    if (
      lowerQuery.includes('qarz') ||
      lowerQuery.includes('nasiya') ||
      lowerQuery.includes('qarzdor')
    ) {
      try {
        const debtRes: any = await getDebtorsApi({})
        if (debtRes?.data) {
          const list = debtRes.data.list || []
          const totalDebt = debtRes.data.total_debt || 0
          const activeCount = debtRes.data.active_debtors_count || 0
          let text = `Nasiyalar Hisoboti:\n• Jami faol qarz: $${totalDebt.toLocaleString()}\n• Faol qarzdorlar soni: ${activeCount} ta\n`
          if (list.length > 0) {
            text += '\nAsosiy qarzdorlar:\n'
            list.slice(0, 5).forEach((d: any) => {
              text += `• ${d.name}: $${d.total_debt.toLocaleString()} (Oxirgi bitim: ${d.last_sale_date || '—'})\n`
            })
          }
          messages.value.push({ role: 'model', text })
        } else {
          messages.value.push({
            role: 'model',
            text: "Qarzdorlar bo'yicha ma'lumot topilmadi yoki qarzlar mavjud emas."
          })
        }
      } catch {
        messages.value.push({
          role: 'model',
          text: "Qarzdorlik ma'lumotlarini yuklashda xatolik yuz berdi."
        })
      }
      isThinking.value = false
      scrollToBottom()
      return
    }

    // 2. Today's sales & revenue check
    if (
      lowerQuery.includes('tushum') ||
      lowerQuery.includes('savdo') ||
      lowerQuery.includes('sotuv') ||
      lowerQuery.includes('kassa')
    ) {
      try {
        const salesRes: any = await getSalesListApi({ pageIndex: 1, pageSize: 100 })
        if (salesRes?.data) {
          const list = salesRes.data.list || []
          const totalRevenue = list.reduce(
            (sum: number, s: any) => sum + Number(s.total_amount || 0),
            0
          )
          const totalItems = list.reduce(
            (sum: number, s: any) => sum + Number(s.total_items || 1),
            0
          )
          const text = `Savdo va Kassa Ma'lumotlari:\n• Jami qayd etilgan sotuvlar: ${list.length} ta chek\n• Sotilgan tovarlar soni: ${totalItems} dona\n• Umumiy tushum aylanmasi: $${totalRevenue.toLocaleString()}`
          messages.value.push({ role: 'model', text })
        }
      } catch {
        messages.value.push({
          role: 'model',
          text: 'Sotuvlar hisobotini yuklashda xatolik yuz berdi.'
        })
      }
      isThinking.value = false
      scrollToBottom()
      return
    }

    // 3. Products / Stock queries
    if (
      lowerQuery.includes('mahsulot') ||
      lowerQuery.includes('ombor') ||
      lowerQuery.includes('qoldiq') ||
      lowerQuery.includes('tovar')
    ) {
      try {
        const prodRes: any = await getProductListApi({ pageIndex: 1, pageSize: 20 })
        if (prodRes?.data) {
          const list = (prodRes.data as any).list || prodRes.data || []
          let text = `Ombordagi Mahsulotlar (Jami: ${list.length} ta ko'rsatilmoqda):\n`
          list.slice(0, 8).forEach((p: any) => {
            text += `• ${p.productName || p.name}: ${p.quantityInStock || 0} ${p.unit || 'dona'} ($${p.price || 0})\n`
          })
          messages.value.push({ role: 'model', text })
        }
      } catch {
        messages.value.push({
          role: 'model',
          text: "Ombor ma'lumotlarini olishda xatolik yuz berdi."
        })
      }
      isThinking.value = false
      scrollToBottom()
      return
    }

    // 4. Workers queries
    if (lowerQuery.includes('xodim') || lowerQuery.includes('ishchi')) {
      try {
        const workerRes: any = await getWorkerListApi({ pageIndex: 1, pageSize: 50 })
        if (workerRes?.data) {
          const list = workerRes.data.list || workerRes.data || []
          let text = `Xodimlar Ro'yxati (Jami: ${list.length} nafar):\n`
          list.slice(0, 8).forEach((w: any) => {
            text += `• ${w.name || w.first_name + ' ' + w.last_name} — ${w.role || w.position || 'Xodim'}\n`
          })
          messages.value.push({ role: 'model', text })
        }
      } catch {
        messages.value.push({
          role: 'model',
          text: "Xodimlar ro'yxatini yuklashda xatolik yuz berdi."
        })
      }
      isThinking.value = false
      scrollToBottom()
      return
    }

    // 5. Stock addition pattern (e.g. 250 ta Pepsi 1.5l olib keldik)
    let action = ''
    let params: any = {}

    if (
      lowerQuery.includes('olib keldik') ||
      lowerQuery.includes('keltirildi') ||
      lowerQuery.includes('keldi') ||
      lowerQuery.includes('kirdik')
    ) {
      const numMatch = query.match(/\d+/)
      const qty = numMatch ? parseInt(numMatch[0]) : 0
      const productName = query
        .replace(/\d+/g, '')
        .replace(/ta|olib|keldik|keltirildi|keldi|kirdik|biz|omborga|dona/gi, '')
        .trim()

      if (qty > 0 && productName) {
        action = 'add_product_stock'
        params = { name: productName, added_quantity: qty }
      }
    }

    if (action) {
      const res = await dispatchAIFunction(action, params)
      if (res && res.requests && res.requests.length) {
        messages.value.push({
          role: 'api',
          text: res.message,
          requests: res.requests
        })
      }
      if (res && res.code === 0) {
        messages.value.push({ role: 'model', text: res.message || 'Bajarildi.' })
      } else {
        messages.value.push({
          role: 'model',
          text: res.message || 'Kechirasiz, ushbu amalni bajara olmadim.'
        })
      }
    } else {
      messages.value.push({
        role: 'model',
        text: `Savolingiz qabul qilindi. Siz quyidagi buyruqlarni berishingiz mumkin:\n• "Bugungi tushum qancha?"\n• "Qarzdorlar ro'yxati"\n• "Ombordagi mahsulot qoldiqlari"\n• "250 ta Pepsi 1.5l olib keldik"`
      })
    }
  } catch (err) {
    messages.value.push({ role: 'model', text: 'Xatolik yuz berdi.' })
  } finally {
    isThinking.value = false
  }
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
  })
}

// Visualizer Wave & Realistic High-Pitch Harmonic Drawing
// Visualizer Wave & Realistic Dual-Mode Drawing (AI Radial Starburst vs User Symmetrical Wave)
let animFrameId: number
let phase = 0
let rotationAngle = 0
let modeMorph = 1.0 // 1.0 = AI Radial Starburst (Image 0), 0.0 = User Waveform (Image 1)
let smoothBass = 0
let smoothMid = 0
let smoothHigh = 0
let smoothLevel = 0

// Track smoothed array for waveform bars
const numWaveBars = 48
const smoothWaveBars = new Array(numWaveBars).fill(4)

const initCanvas = () => {
  nextTick(() => {
    if (!waveCanvas.value) return
    canvasCtx = waveCanvas.value.getContext('2d')
    drawWave()
  })
}

const drawWave = () => {
  if (!waveCanvas.value || !canvasCtx) return

  const dpr = window.devicePixelRatio || 1
  const rect = waveCanvas.value.getBoundingClientRect()
  const width = (waveCanvas.value.width = rect.width * dpr)
  const height = (waveCanvas.value.height = rect.height * dpr)
  canvasCtx.scale(dpr, dpr)

  const displayWidth = rect.width
  const displayHeight = rect.height
  const centerX = displayWidth / 2
  const centerY = displayHeight / 2

  canvasCtx.clearRect(0, 0, displayWidth, displayHeight)

  // 1. Smooth interpolation for energy & pitch
  const cur = currentFreqData.value
  smoothBass += (cur.bass - smoothBass) * 0.22
  smoothMid += (cur.mid - smoothMid) * 0.25
  smoothHigh += (cur.high - smoothHigh) * 0.28
  smoothLevel += (cur.level - smoothLevel) * 0.22

  const rawArray = cur.raw
  const isAISpeaking = cur.source === 'playback' || (cur.source !== 'mic' && smoothLevel > 14)
  const isUserSpeaking = cur.source === 'mic' && smoothLevel > 6

  // Mutually exclusive target morph: 1.0 when AI is speaking, 0.0 when User is speaking or Idle
  const targetMorph = isAISpeaking ? 1.0 : 0.0
  modeMorph += (targetMorph - modeMorph) * 0.25
  if (modeMorph < 0.005) modeMorph = 0.0
  if (modeMorph > 0.995) modeMorph = 1.0

  // Rotation & phase progression
  rotationAngle += 0.006 + (smoothHigh / 255) * 0.02 + (smoothMid / 255) * 0.01
  phase += 0.04 + (smoothLevel / 255) * 0.06

  // ══════════════════════════════════════════════════════════════════════════
  // MODE 1: AI SPEAKING → RADIAL DOTTED STARBURST / SUNBURST WAVE (IMAGE 0)
  // (Completely hidden when user speaks or idle)
  // ══════════════════════════════════════════════════════════════════════════
  if (modeMorph > 0.01) {
    canvasCtx.save()
    canvasCtx.globalAlpha = Math.min(1, Math.max(0, modeMorph))

    // Center Glowing Orb Aura
    const coreRadius = Math.max(12, 14 + (smoothBass / 255) * 16)
    const maxRadius = Math.min(centerX, centerY) * 0.95

    const centerGlow = canvasCtx.createRadialGradient(
      centerX,
      centerY,
      2,
      centerX,
      centerY,
      coreRadius * 2.2
    )
    if (smoothHigh > 25) {
      centerGlow.addColorStop(0, 'rgba(255, 255, 255, 0.95)')
      centerGlow.addColorStop(0.3, 'rgba(56, 189, 248, 0.6)')
      centerGlow.addColorStop(0.7, 'rgba(236, 72, 153, 0.25)')
      centerGlow.addColorStop(1, 'rgba(15, 23, 42, 0)')
    } else {
      centerGlow.addColorStop(0, 'rgba(255, 255, 255, 0.9)')
      centerGlow.addColorStop(0.35, 'rgba(99, 102, 241, 0.5)')
      centerGlow.addColorStop(0.7, 'rgba(139, 92, 246, 0.2)')
      centerGlow.addColorStop(1, 'rgba(15, 23, 42, 0)')
    }
    canvasCtx.fillStyle = centerGlow
    canvasCtx.beginPath()
    canvasCtx.arc(centerX, centerY, coreRadius * 2.2, 0, Math.PI * 2)
    canvasCtx.fill()

    // 72 Radial Dotted Rays around 360 degrees
    const totalRays = 72
    const dotSpacing = 3.6

    for (let r = 0; r < totalRays; r++) {
      const angle = (r * (Math.PI * 2)) / totalRays + rotationAngle
      const cosA = Math.cos(angle)
      const sinA = Math.sin(angle)

      // Frequency mapping from FFT bins
      const binIdx = Math.floor((r / totalRays) * rawArray.length)
      const rawVal = rawArray[binIdx % rawArray.length] || 0

      // Compute dynamic length of ray based on audio pitch & volume
      const harmonicPulse = Math.sin(phase * 2 + r * 0.3) * 0.15 + 0.85
      const rayExtent =
        coreRadius +
        ((rawVal / 255) * (maxRadius - coreRadius) * 0.95 + 6) * harmonicPulse +
        (smoothHigh > 20 ? (Math.sin(r * 4 + phase) > 0.4 ? 8 : 0) : 0)

      const numDots = Math.max(3, Math.floor((rayExtent - coreRadius) / dotSpacing))

      for (let d = 0; d < numDots; d++) {
        const dist = coreRadius + d * dotSpacing
        if (dist > maxRadius) break

        const dotX = centerX + cosA * dist
        const dotY = centerY + sinA * dist

        const distRatio = (dist - coreRadius) / (maxRadius - coreRadius)
        const dotSize = Math.max(0.7, 1.8 * (1 - distRatio * 0.5) + (smoothLevel / 255) * 0.4)

        // Color gradient from inner white -> cyan/indigo -> magenta tips
        let dotColor: string
        if (distRatio < 0.25) {
          dotColor = '#ffffff'
        } else if (distRatio < 0.6) {
          dotColor = smoothHigh > 20 ? '#38bdf8' : '#818cf8'
        } else if (distRatio < 0.85) {
          dotColor = smoothHigh > 20 ? '#c084fc' : '#6366f1'
        } else {
          dotColor = '#ec4899'
        }

        canvasCtx.fillStyle = dotColor
        canvasCtx.beginPath()
        canvasCtx.arc(dotX, dotY, dotSize, 0, Math.PI * 2)
        canvasCtx.fill()
      }
    }
    canvasCtx.restore()
  }

  // ══════════════════════════════════════════════════════════════════════════
  // MODE 2: USER SPEAKING OR IDLE → SYMMETRIC VOICE WAVEFORM STRIP (IMAGE 1)
  // (Completely hidden when AI is speaking)
  // ══════════════════════════════════════════════════════════════════════════
  if (modeMorph < 0.99) {
    canvasCtx.save()
    canvasCtx.globalAlpha = Math.min(1, Math.max(0, 1 - modeMorph))

    const barWidth = 3.8
    const barGap = 3.2
    const totalWaveWidth = numWaveBars * (barWidth + barGap) - barGap
    const waveStartX = (displayWidth - totalWaveWidth) / 2

    // Background horizontal baseline accent
    canvasCtx.strokeStyle = 'rgba(99, 102, 241, 0.15)'
    canvasCtx.lineWidth = 1
    canvasCtx.beginPath()
    canvasCtx.moveTo(waveStartX - 10, centerY)
    canvasCtx.lineTo(waveStartX + totalWaveWidth + 10, centerY)
    canvasCtx.stroke()

    for (let i = 0; i < numWaveBars; i++) {
      // Gaussian window envelope (bars are shortest at ends, peak in center harmonics like Image 1)
      const normPos = i / (numWaveBars - 1)
      const envelope = Math.sin(normPos * Math.PI)

      // Map frequency bin to bar
      const freqIdx = Math.floor(
        Math.abs(i - numWaveBars / 2) * (rawArray.length / (numWaveBars / 2))
      )
      const rawVal = rawArray[Math.min(freqIdx, rawArray.length - 1)] || 0

      // Add harmonic ripple variation across bars
      const ripple = Math.sin(i * 0.45 + phase * 2.5) * 0.2 + 0.9
      const targetHeight = Math.max(
        3.5,
        ((rawVal / 255) * (displayHeight * 0.8) + (smoothLevel / 255) * 15) * envelope * ripple + 4
      )

      smoothWaveBars[i] += (targetHeight - smoothWaveBars[i]) * 0.32
      const barH = smoothWaveBars[i]

      const barX = waveStartX + i * (barWidth + barGap)
      const topY = centerY - barH / 2

      // Periwinkle / indigo gradient matching Image 1
      const barGrad = canvasCtx.createLinearGradient(barX, topY, barX, topY + barH)
      if (smoothHigh > 25) {
        barGrad.addColorStop(0, '#38bdf8')
        barGrad.addColorStop(0.5, '#818cf8')
        barGrad.addColorStop(1, '#6366f1')
      } else {
        barGrad.addColorStop(0, '#93c5fd')
        barGrad.addColorStop(0.5, '#818cf8')
        barGrad.addColorStop(1, '#6366f1')
      }

      canvasCtx.fillStyle = barGrad
      canvasCtx.beginPath()
      canvasCtx.roundRect(barX, topY, barWidth, barH, barWidth / 2)
      canvasCtx.fill()
    }
    canvasCtx.restore()
  }

  animFrameId = requestAnimationFrame(drawWave)
}

onUnmounted(() => {
  client.disconnect()
  cancelAnimationFrame(animFrameId)
})
</script>

<style scoped>
.ai-assistant-wrapper {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family:
    'Outfit',
    'Inter',
    -apple-system,
    BlinkMacSystemFont,
    sans-serif;
  user-select: none;
}

.orb-container {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}

/* Float Label Tag */
.ai-badge-label {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 20px;
  color: #e2e8f0;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: floatBadge 3s ease-in-out infinite;
}

.ai-badge-label:hover {
  transform: translateY(-2px);
  border-color: rgba(139, 92, 246, 0.6);
  background: rgba(30, 41, 59, 0.95);
  color: #fff;
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);
}

.ai-badge-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

@keyframes floatBadge {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

/* Orb Trigger Button */
.ai-trigger-orb {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
  border: none;
  color: #fff;
  cursor: pointer;
  box-shadow:
    0 8px 24px rgba(99, 102, 241, 0.45),
    inset 0 1px 2px rgba(255, 255, 255, 0.35);
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.ai-trigger-orb:hover {
  transform: scale(1.1) rotate(5deg);
  box-shadow:
    0 12px 30px rgba(99, 102, 241, 0.6),
    0 0 20px rgba(236, 72, 153, 0.4);
}

.ai-trigger-orb:active {
  transform: scale(0.95);
}

.ai-trigger-orb.is-active {
  background: linear-gradient(135deg, #475569, #334155);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
}

.orb-pulse-glow {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border-radius: 50%;
  border: 2px solid rgba(99, 102, 241, 0.5);
  animation: pulse 2.2s cubic-bezier(0.24, 0, 0.38, 1) infinite;
  pointer-events: none;
}

.orb-pulse-glow-secondary {
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  border-radius: 50%;
  border: 1.5px solid rgba(236, 72, 153, 0.3);
  animation: pulse 2.2s cubic-bezier(0.24, 0, 0.38, 1) infinite 0.7s;
  pointer-events: none;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.35);
    opacity: 0;
  }
}

.ai-trigger-orb.is-listening {
  background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
  box-shadow: 0 10px 30px rgba(16, 185, 129, 0.6);
}

/* Glassmorphic Panel styling */
.ai-glass-panel {
  position: absolute;
  bottom: 70px;
  right: 0;
  width: 420px;
  max-width: calc(100vw - 32px);
  height: 580px;
  max-height: calc(100vh - 100px);
  background: rgba(15, 23, 42, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  box-shadow:
    0 24px 60px rgba(0, 0, 0, 0.65),
    0 0 1px 1px rgba(255, 255, 255, 0.1) inset;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: #f8fafc;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(30, 41, 59, 0.4);
}

.header-title-box {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pulse-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #64748b;
  display: inline-block;
  flex-shrink: 0;
}

.pulse-indicator.connected {
  background: #10b981;
  box-shadow: 0 0 12px #10b981;
  animation: indicator-pulse 1.5s infinite;
}

.pulse-indicator.connecting {
  background: #eab308;
  box-shadow: 0 0 12px #eab308;
}

@keyframes indicator-pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.35);
  }
  100% {
    transform: scale(1);
  }
}

.header-title {
  font-size: 15px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #fff 0%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-status {
  font-size: 11px;
  color: #94a3b8;
  margin: 0;
}

.clear-chat-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #94a3b8;
  padding: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.clear-chat-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #f87171;
}

.close-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #94a3b8;
  width: 28px;
  height: 28px;
  font-size: 18px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

/* Chat logs panel */
.panel-body {
  flex: 1;
  padding: 16px 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.welcome-card {
  text-align: center;
  margin: auto;
  color: #94a3b8;
  padding: 10px;
}

.welcome-icon {
  font-size: 36px;
  margin-bottom: 8px;
}

.welcome-card h3 {
  font-size: 16px;
  color: #f1f5f9;
  font-weight: 700;
  margin-bottom: 6px;
}

.welcome-card p {
  font-size: 12px;
  line-height: 1.5;
  color: #94a3b8;
  margin-bottom: 16px;
}

.quick-chips {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 10px;
}

.chip-btn {
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 12px;
  color: #c7d2fe;
  font-size: 11px;
  font-weight: 600;
  padding: 8px 10px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
}

.chip-btn:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.5);
  color: #fff;
  transform: translateY(-1px);
}

.chat-bubble-wrapper {
  display: flex;
  margin-bottom: 4px;
}

.chat-bubble-wrapper.user {
  justify-content: flex-end;
}

.chat-bubble-wrapper.model {
  justify-content: flex-start;
}

.chat-bubble-wrapper.api {
  justify-content: center;
}

.chat-bubble {
  max-width: 86%;
  padding: 10px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
}

.chat-bubble-wrapper.user .chat-bubble {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border-bottom-right-radius: 4px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.chat-bubble-wrapper.model .chat-bubble {
  background: rgba(30, 41, 59, 0.8);
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

.bubble-role-label {
  font-size: 10px;
  color: #94a3b8;
  display: block;
  margin-bottom: 4px;
  font-weight: 600;
}

.bubble-text {
  font-size: 13px;
  margin: 0;
  line-height: 1.5;
}

/* Thinking Indicator */
.thinking-bubble {
  display: flex;
  gap: 5px;
  align-items: center;
  padding: 12px 18px !important;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #818cf8;
  animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingBounce {
  0%,
  80%,
  100% {
    transform: scale(0.6);
    opacity: 0.4;
  }
  40% {
    transform: scale(1.1);
    opacity: 1;
  }
}

/* API Request Log Badge */
.api-log-card {
  width: 95%;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 12px;
  padding: 10px 14px;
  color: #a7f3d0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.api-log-header {
  display: flex;
  align-items: center;
  gap: 6px;
}

.api-pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 8px #34d399;
}

.api-tag-title {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: #34d399;
}

.api-url-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.api-url-row {
  display: flex;
}

.url-code {
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 11px;
  color: #6ee7b7;
  background: rgba(0, 0, 0, 0.4);
  padding: 4px 8px;
  border-radius: 6px;
  word-break: break-all;
  border: 1px solid rgba(52, 211, 153, 0.2);
}

.api-log-summary {
  font-size: 11px;
  color: #d1fae5;
  margin-top: 2px;
}

/* Visualizer Wave & Tone Header */
.visualizer-container {
  padding: 6px 18px 4px 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: rgba(15, 23, 42, 0.4);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.visualizer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
}

.tone-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.live-pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #64748b;
  transition: all 0.2s;
}

.live-pulse-dot.is-active {
  background: #38bdf8;
  box-shadow: 0 0 8px #38bdf8;
  animation: pulseDot 1s infinite alternate;
}

@keyframes pulseDot {
  0% {
    transform: scale(0.9);
    opacity: 0.7;
  }
  100% {
    transform: scale(1.3);
    opacity: 1;
  }
}

.tone-badge {
  color: #cbd5e1;
  font-weight: 500;
  letter-spacing: 0.2px;
}

.pitch-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pitch-tag {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.3);
  transition: all 0.2s;
}

.pitch-tag.is-high {
  background: rgba(236, 72, 153, 0.2);
  color: #f472b6;
  border-color: rgba(236, 72, 153, 0.45);
  box-shadow: 0 0 6px rgba(236, 72, 153, 0.3);
}

.db-meter {
  font-size: 10px;
  color: #64748b;
  font-variant-numeric: tabular-nums;
}

.wave-canvas {
  width: 100%;
  height: 100px;
  display: block;
}

/* Controls */
.panel-controls {
  padding: 14px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: rgba(30, 41, 59, 0.35);
}

.action-voice-btn {
  width: 100%;
  padding: 10px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
  color: white;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transition: all 0.25s;
}

.action-voice-btn:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.action-voice-btn.is-active {
  background: linear-gradient(135deg, #ef4444, #f43f5e);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
}

.text-input-box :deep(.el-input-group__append) {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  padding: 0 14px;
}

.text-input-box :deep(.el-input__wrapper) {
  background-color: rgba(15, 23, 42, 0.6) !important;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.12) inset !important;
  border-radius: 10px 0 0 10px;
}

.text-input-box :deep(.el-input__inner) {
  color: #fff !important;
  font-size: 13px;
}

.text-input-box :deep(.el-input__inner::placeholder) {
  color: #64748b !important;
}

/* Transition Animations */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.35s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(20px) scale(0.96);
  opacity: 0;
}
</style>
