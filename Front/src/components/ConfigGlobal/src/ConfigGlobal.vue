<script setup lang="ts">
import { provide, computed, watch, onMounted } from 'vue'
import { propTypes } from '@/utils/propTypes'
import { ComponentSize, ElConfigProvider } from 'element-plus'
import { useLocaleStore } from '@/store/modules/locale'
import { useWindowSize } from '@vueuse/core'
import { useAppStore } from '@/store/modules/app'
import { setCssVar } from '@/utils'
import { useDesign } from '@/hooks/web/useDesign'

const { variables } = useDesign()

const appStore = useAppStore()

const props = defineProps({
  size: propTypes.oneOf<ComponentSize>(['default', 'small', 'large']).def('default')
})

provide('configGlobal', props)

// 初始化所有主题色
onMounted(() => {
  appStore.setCssVarTheme()
})

const { width } = useWindowSize()

// 监听窗口变化
watch(
  () => width.value,
  (width: number) => {
    if (width < 768) {
      !appStore.getMobile ? appStore.setMobile(true) : undefined
      setCssVar('--left-menu-min-width', '0')
      appStore.setCollapse(true)
      appStore.getLayout !== 'classic' ? appStore.setLayout('classic') : undefined
    } else {
      appStore.getMobile ? appStore.setMobile(false) : undefined
      setCssVar('--left-menu-min-width', '64px')
    }
  },
  {
    immediate: true
  }
)

const updateSizeVars = (size: ComponentSize) => {
  document.documentElement.setAttribute('data-size', size || 'default')
  if (size === 'large') {
    setCssVar('--app-font-size', '16px')
    setCssVar('--app-title-size', '19px')
    setCssVar('--app-item-padding', '14px 18px')
    setCssVar('--app-icon-size', '22px')
    setCssVar('--app-tree-node-height', '44px')
    setCssVar('--app-button-px', '28px')
    setCssVar('--app-button-py', '12px')
    setCssVar('--el-font-size-base', '16px')
    setCssVar('--el-component-size', '44px')
  } else if (size === 'small') {
    setCssVar('--app-font-size', '12px')
    setCssVar('--app-title-size', '13px')
    setCssVar('--app-item-padding', '6px 10px')
    setCssVar('--app-icon-size', '14px')
    setCssVar('--app-tree-node-height', '28px')
    setCssVar('--app-button-px', '16px')
    setCssVar('--app-button-py', '6px')
    setCssVar('--el-font-size-base', '12px')
    setCssVar('--el-component-size', '28px')
  } else {
    setCssVar('--app-font-size', '14px')
    setCssVar('--app-title-size', '16px')
    setCssVar('--app-item-padding', '10px 14px')
    setCssVar('--app-icon-size', '18px')
    setCssVar('--app-tree-node-height', '36px')
    setCssVar('--app-button-px', '22px')
    setCssVar('--app-button-py', '9px')
    setCssVar('--el-font-size-base', '14px')
    setCssVar('--el-component-size', '36px')
  }
}

watch(
  () => props.size,
  (s) => updateSizeVars(s),
  { immediate: true }
)

// 多语言相关
const localeStore = useLocaleStore()

const currentLocale = computed(() => localeStore.currentLocale)
</script>

<template>
  <ElConfigProvider
    :namespace="variables.elNamespace"
    :locale="currentLocale.elLocale"
    :message="{ max: 1 }"
    :size="size"
  >
    <slot></slot>
  </ElConfigProvider>
</template>
