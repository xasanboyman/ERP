<template>
  <div class="ai-assistant-wrapper">
    <!-- Floating Orb Trigger Button -->
    <button
      class="ai-trigger-orb"
      :class="{ 'is-active': isOpen, 'is-listening': clientStatus === 'connected' }"
      @click="togglePanel"
    >
      <div class="orb-pulse-glow"></div>
      <div class="orb-content">
        <!-- SVG Robot/AI Head Icon -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          width="22"
          height="22"
          fill="currentColor"
        >
          <path
            d="M12 2a10 10 0 0 0-10 10c0 4.14 2.52 7.69 6.09 9.17A2 2 0 0 0 10 20v-2.09A7.98 7.98 0 0 1 4 12a8 8 0 0 1 14.62-4.38l1.41-1.41A9.95 9.95 0 0 0 12 2zm8 10c0 .92-.16 1.8-.44 2.62l1.52 1.52A9.97 9.97 0 0 0 22 12a10 10 0 0 0-2-6.09l-1.52 1.52c.28.82.44 1.7.44 2.62zm-6 2H10v-2h4v2zm-2 4h-2v-2h2v2zm6-4v2c0 2.21-1.79 4-4 4h-1v-2h1c1.1 0 2-.9 2-2v-2h2z"
          />
        </svg>
      </div>
    </button>

    <!-- Glassmorphic Dialog Panel -->
    <transition name="slide-up">
      <div v-if="isOpen" class="ai-glass-panel">
        <!-- Header -->
        <div class="panel-header">
          <div class="header-title-box">
            <span class="pulse-indicator" :class="clientStatus"></span>
            <div>
              <h2 class="header-title">Antigravity AI</h2>
              <p class="header-status">
                {{
                  clientStatus === 'connected'
                    ? 'Listening...'
                    : clientStatus === 'connecting'
                      ? 'Connecting...'
                      : 'Ready'
                }}
              </p>
            </div>
          </div>
          <button class="close-btn" @click="isOpen = false">&times;</button>
        </div>

        <!-- Chat / Transcript Logs -->
        <div class="panel-body" ref="logsContainer">
          <div class="welcome-card" v-if="messages.length === 0">
            <div class="welcome-icon">✨</div>
            <h3>Qanday yordam bera olaman?</h3>
            <p>
              Xodimlar, mahsulotlar hamda ombor inventarizatsiyasini ovozli yoki matnli buyruqlar
              bilan boshqaring.
            </p>
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
                  <span class="api-tag-title">⚡ HTTP API REQUEST</span>
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
                  msg.role === 'user' ? 'Siz' : 'AI Assistant'
                }}</span>
                <p class="bubble-text">{{ msg.text }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Voice Level Wave Visualizer -->
        <div class="visualizer-container" v-show="clientStatus === 'connected'">
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
                width="24"
                height="24"
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
                width="24"
                height="24"
                fill="currentColor"
              >
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
              </svg>
            </span>
            <span class="btn-text">
              {{ clientStatus === 'connected' ? "Ovozni o'chirish" : "Ovozli bog'lanish" }}
            </span>
          </button>

          <!-- Text input option (hybrid mode) -->
          <div class="text-input-box">
            <el-input
              v-model="textCommand"
              placeholder="Buyruq yozing (masalan: 250 ta Pepsi 1.5l olib keldik)..."
              clearable
              @keyup.enter="handleTextSubmit"
            >
              <template #append>
                <el-button @click="handleTextSubmit">
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
import { ref, nextTick, onUnmounted } from 'vue'
import { AIVoiceClient } from './AIVoiceClient'
import { dispatchAIFunction } from './aiDispatcher'
import { ElButton, ElInput } from 'element-plus'

const isOpen = ref(false)
const clientStatus = ref<'disconnected' | 'connecting' | 'connected'>('disconnected')
const textCommand = ref('')
const messages = ref<{ role: 'user' | 'model' | 'api'; text: string; requests?: string[] }[]>([])
const waveCanvas = ref<HTMLCanvasElement>()
const logsContainer = ref<HTMLElement>()

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

const handleTextSubmit = async () => {
  const query = textCommand.value.trim()
  if (!query) return

  messages.value.push({ role: 'user', text: query })
  textCommand.value = ''
  scrollToBottom()

  try {
    let action = ''
    let params: any = {}

    // Check for stock addition pattern (e.g. 250 ta Pepsi PET 1,5 l olib keldik)
    const lowerQuery = query.toLowerCase()
    if (
      lowerQuery.includes('xodim') &&
      (lowerQuery.includes("qo'sh") || lowerQuery.includes('qosh') || lowerQuery.includes('yarat'))
    ) {
      action = 'create_worker'
      const phoneMatch = query.match(/\+?\d[\d\s-]{8,12}\d/)
      params = {
        first_name: 'Anvar',
        last_name: 'Karimov',
        phone: phoneMatch ? phoneMatch[0] : '+998901234567',
        position: 'Tikuvchi',
        department: "Tikuv bo'limi"
      }
    } else if (
      lowerQuery.includes('olib keldik') ||
      lowerQuery.includes('keltirildi') ||
      lowerQuery.includes('keldi') ||
      lowerQuery.includes('kirdik') ||
      lowerQuery.includes("qo'sh") ||
      lowerQuery.includes('qosh')
    ) {
      const numMatch = query.match(/\d+/)
      const qty = numMatch ? parseInt(numMatch[0]) : 0
      const productName = query
        .replace(/\d+/g, '')
        .replace(/ta|olib|keldik|keltirildi|keldi|kirdik|biz|qo'sh|qosh|omborga|dona/gi, '')
        .trim()

      if (qty > 0 && productName) {
        action = 'add_product_stock'
        params = { name: productName, added_quantity: qty }
      }
    } else if (lowerQuery.includes('mahsulot') && lowerQuery.includes("ro'yxat")) {
      action = 'list_products'
    } else if (lowerQuery.includes('xodim') && lowerQuery.includes("ro'yxat")) {
      action = 'list_workers'
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
        let aiMsg = res.message || 'Bajarildi.'
        if (action === 'list_products' && Array.isArray(res.data)) {
          const listStr = res.data
            .map((p: any) => `- ${p.name} ($${p.price}) [Ombor: ${p.quantity}]`)
            .join('\n')
          aiMsg = `Mahsulotlar ro'yxati:\n${listStr}`
        } else if (action === 'list_workers' && Array.isArray(res.data)) {
          const listStr = res.data.map((w: any) => `- ${w.name} (${w.role})`).join('\n')
          aiMsg = `Xodimlar ro'yxati:\n${listStr}`
        }
        messages.value.push({ role: 'model', text: aiMsg })
      } else {
        messages.value.push({
          role: 'model',
          text: res.message || 'Kechirasiz, ushbu amalni bajara olmadim.'
        })
      }
    } else {
      messages.value.push({
        role: 'model',
        text: "Tushunmadim. Iltimos '250 ta Pepsi 1.5l olib keldik', xodim qo'shish yoki mahsulotlar ro'yxati kabi buyruq bering."
      })
    }
  } catch (err) {
    messages.value.push({ role: 'model', text: 'Xatolik yuz berdi.' })
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

// Visualizer Wave Drawing
let animFrameId: number
const initCanvas = () => {
  nextTick(() => {
    if (!waveCanvas.value) return
    canvasCtx = waveCanvas.value.getContext('2d')
    drawWave()
  })
}

const drawWave = () => {
  if (!waveCanvas.value || !canvasCtx) return

  const width = (waveCanvas.value.width = waveCanvas.value.offsetWidth)
  const height = (waveCanvas.value.height = waveCanvas.value.offsetHeight)

  canvasCtx.clearRect(0, 0, width, height)

  const bars = 20
  const barWidth = 6
  const gap = 4
  const startX = (width - bars * (barWidth + gap)) / 2

  canvasCtx.fillStyle = 'rgba(64, 158, 255, 0.8)'
  for (let i = 0; i < bars; i++) {
    const scale = Math.sin(Date.now() / 200 + i) * 0.4 + 0.6
    const level = (audioLevel / 255) * height * 1.5 * scale
    const barHeight = Math.max(4, level)
    const x = startX + i * (barWidth + gap)
    const y = (height - barHeight) / 2

    canvasCtx.beginPath()
    canvasCtx.roundRect(x, y, barWidth, barHeight, 3)
    canvasCtx.fill()
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
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  font-family: 'Outfit', 'Inter', sans-serif;
}

/* Orb Trigger Button */
.ai-trigger-orb {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border: none;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(168, 85, 247, 0.4);
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0.88;
  transition: all 0.25s ease;
}

.ai-trigger-orb:hover {
  opacity: 1;
  transform: scale(1.08);
  box-shadow: 0 10px 25px rgba(168, 85, 247, 0.6);
}

.orb-pulse-glow {
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  border-radius: 50%;
  border: 2px solid rgba(168, 85, 247, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.2);
    opacity: 0;
  }
}

.ai-trigger-orb.is-listening {
  background: linear-gradient(135deg, #10b981, #3b82f6);
  box-shadow: 0 10px 25px rgba(16, 185, 129, 0.5);
}

/* Glassmorphic Panel styling */
.ai-glass-panel {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 400px;
  height: 540px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.55);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: #f8fafc;
}

.panel-header {
  padding: 15px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pulse-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #64748b;
  display: inline-block;
}

.pulse-indicator.connected {
  background: #10b981;
  box-shadow: 0 0 10px #10b981;
  animation: indicator-pulse 1.5s infinite;
}

.pulse-indicator.connecting {
  background: #eab308;
  box-shadow: 0 0 10px #eab308;
}

@keyframes indicator-pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.3);
  }
  100% {
    transform: scale(1);
  }
}

.header-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
}

.header-status {
  font-size: 11px;
  color: #94a3b8;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 24px;
  cursor: pointer;
}

/* Chat logs panel */
.panel-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.welcome-card {
  text-align: center;
  margin: auto;
  color: #94a3b8;
}

.welcome-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.chat-bubble-wrapper {
  display: flex;
  margin-bottom: 6px;
}

.chat-bubble-wrapper.user {
  justify-content: flex-end;
}

.chat-bubble-wrapper.api {
  justify-content: center;
}

.chat-bubble {
  max-width: 82%;
  padding: 10px 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.05);
}

.chat-bubble-wrapper.user .chat-bubble {
  background: #6366f1;
  border-bottom-right-radius: 2px;
}

.chat-bubble-wrapper.model .chat-bubble {
  background: rgba(168, 85, 247, 0.15);
  border-bottom-left-radius: 2px;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.bubble-role-label {
  font-size: 9px;
  color: #cbd5e1;
  display: block;
  margin-bottom: 4px;
}

.bubble-text {
  font-size: 13px;
  margin: 0;
  line-height: 1.4;
  white-space: pre-line;
}

/* API Request Log Badge */
.api-log-card {
  width: 95%;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 10px;
  padding: 10px 12px;
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
  box-shadow: 0 0 6px #34d399;
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
  background: rgba(0, 0, 0, 0.35);
  padding: 4px 8px;
  border-radius: 5px;
  word-break: break-all;
  border: 1px solid rgba(52, 211, 153, 0.2);
}

.api-log-summary {
  font-size: 11px;
  color: #d1fae5;
  margin-top: 2px;
}

/* Visualizer Wave */
.visualizer-container {
  height: 45px;
  padding: 0 20px;
  display: flex;
  align-items: center;
}

.wave-canvas {
  width: 100%;
  height: 100%;
}

/* Controls */
.panel-controls {
  padding: 15px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-voice-btn {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border: none;
  color: white;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
  transition: all 0.3s;
}

.action-voice-btn.is-active {
  background: linear-gradient(135deg, #ef4444, #f43f5e);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.text-input-box :deep(.el-input-group__append) {
  background-color: #6366f1;
  color: white;
  border: none;
}

.text-input-box :deep(.el-input__inner) {
  background-color: rgba(255, 255, 255, 0.04);
  color: white;
  border-color: rgba(255, 255, 255, 0.1);
}

/* Transition Animations */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(30px) scale(0.95);
  opacity: 0;
}
</style>
