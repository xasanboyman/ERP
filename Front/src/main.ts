import 'vue/jsx'

if (typeof window !== 'undefined') {
  ;(window as any).global = window
  ;(window as any).module = (window as any).module || { exports: {} }
}

if (typeof window !== 'undefined' && window.localStorage) {
  const currentLangRaw = window.localStorage.getItem('lang')
  let currentLang = ''
  try {
    if (currentLangRaw) {
      currentLang = JSON.parse(currentLangRaw).value
    }
  } catch (e) {
    console.error(e)
  }
  // Force a clean cache refresh on version change or reset flag missing
  const resetFlag = window.localStorage.getItem('reset_v3')
  if (!['uz', 'cr', 'en'].includes(currentLang) || !resetFlag) {
    window.localStorage.setItem('lang', JSON.stringify({ type: 'String', value: 'uz' }))
    window.localStorage.removeItem('user')
    window.localStorage.removeItem('permission')
    window.localStorage.setItem('reset_v3', 'true')
  }
}

// 引入windi css
import '@/plugins/unocss'

// 导入全局的svg图标
import '@/plugins/svgIcon'

// 初始化多语言
import { setupI18n } from '@/plugins/vueI18n'

// 引入状态管理
import { setupStore } from '@/store'

// 全局组件
import { setupGlobCom } from '@/components'

import { setupIconify } from '@/plugins/iconify'

// 引入element-plus
import { setupElementPlus } from '@/plugins/elementPlus'

// 引入全局样式
import '@/styles/index.less'

// 引入动画
import '@/plugins/animate.css'

// 路由
import { setupRouter } from './router'

// 权限
import { setupPermission } from './directives'

import { createApp } from 'vue'

import App from './App.vue'

import './permission'

// 创建实例
const setupAll = () => {
  const app = createApp(App)

  // 1. Setup Pinia Store First
  setupStore(app)

  // 2. Setup i18n (Now instant & synchronous)
  setupI18n(app)

  // 3. Setup Global UI Components
  setupGlobCom(app)

  // 4. Setup Icon Collections (Non-blocking background)
  setupIconify()

  // 5. Setup Element Plus
  setupElementPlus(app)

  // 6. Setup Router & Permissions
  setupRouter(app)
  setupPermission(app)

  // 7. Mount App Instantly (Zero delay)
  app.mount('#app')

  // 8. Initialize Real-Time WebSocket Reactive Synchronization & Offline Queue in background
  setTimeout(async () => {
    try {
      const { realtimeService } = await import('@/utils/realtimeSync')
      const { offlineQueue } = await import('@/utils/offlineQueue')
      realtimeService.connect()
      offlineQueue.flushQueue()
    } catch (wsErr) {
      console.debug('RealtimeSync / OfflineQueue init note:', wsErr)
    }
  }, 100)
}

setupAll()
