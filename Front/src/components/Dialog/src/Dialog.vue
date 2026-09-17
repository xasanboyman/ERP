<script setup lang="ts">
import { ElDialog, ElScrollbar } from 'element-plus'
import { propTypes } from '@/utils/propTypes'
import { computed, useAttrs, ref, unref, useSlots, watch, nextTick } from 'vue'
import { isNumber } from '@/utils/is'
import { useI18n } from '@/hooks/web/useI18n'

const { t } = useI18n()

const slots = useSlots()

const props = defineProps({
  modelValue: propTypes.bool.def(false),
  title: propTypes.string.def('Dialog'),
  fullscreen: propTypes.bool.def(true),
  maxHeight: propTypes.oneOfType([String, Number]).def('85vh'),
  resizable: propTypes.bool.def(true),
  autoHeight: propTypes.bool.def(true)
})

const getBindValue = computed(() => {
  const delArr: string[] = ['fullscreen', 'title', 'maxHeight', 'resizable', 'autoHeight']
  const attrs = useAttrs()
  const obj = { ...attrs, ...props }
  for (const key in obj) {
    if (delArr.indexOf(key) !== -1) {
      delete obj[key]
    }
  }
  return obj
})

const isFullscreen = ref(false)

const toggleFull = () => {
  isFullscreen.value = !unref(isFullscreen)
}

const computedMaxHeight = computed(() => {
  if (isNumber(props.maxHeight)) return `${props.maxHeight}px`
  return props.maxHeight || '85vh'
})

const dialogHeight = ref('auto')

watch(
  () => isFullscreen.value,
  async (val: boolean) => {
    await nextTick()
    if (val) {
      const windowHeight = document.documentElement.offsetHeight
      dialogHeight.value = `${windowHeight - 55 - 60 - (slots.footer ? 63 : 0)}px`
    } else {
      dialogHeight.value = 'auto'
    }
  },
  {
    immediate: true
  }
)

const dialogStyle = computed(() => {
  if (isFullscreen.value) {
    return {
      height: unref(dialogHeight),
      maxHeight: unref(dialogHeight),
      width: '100%'
    }
  }
  return {
    maxHeight: unref(computedMaxHeight),
    height: props.autoHeight ? 'auto' : '100%',
    width: '100%'
  }
})
</script>

<template>
  <ElDialog
    v-bind="getBindValue"
    :fullscreen="isFullscreen"
    destroy-on-close
    lock-scroll
    draggable
    top="0"
    :close-on-click-modal="false"
    :show-close="false"
    :class="{ 'is-resizable': resizable }"
  >
    <template #header="{ close }">
      <div
        class="dialog-header-bar flex justify-between items-center w-full h-52px px-18px select-none"
      >
        <div
          class="dialog-title-slot font-bold text-16px text-[var(--el-text-color-primary)] flex items-center gap-8px tracking-tight"
        >
          <slot name="title">
            {{ title ? t(title) : '' }}
          </slot>
        </div>
        <div class="dialog-header-actions flex items-center gap-8px">
          <div
            v-if="fullscreen"
            class="header-action-btn flex items-center justify-center w-30px h-30px rounded-lg cursor-pointer transition-all duration-200 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 active:scale-95"
            :title="isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'"
            @click="toggleFull"
          >
            <Icon
              class="text-17px"
              :icon="
                isFullscreen ? 'vi-radix-icons:exit-full-screen' : 'vi-radix-icons:enter-full-screen'
              "
            />
          </div>
          <div
            class="header-action-btn flex items-center justify-center w-30px h-30px rounded-lg cursor-pointer transition-all duration-200 text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 active:scale-95"
            title="Close"
            @click="close"
          >
            <Icon
              class="text-18px font-bold"
              icon="vi-ep:close"
            />
          </div>
        </div>
      </div>
    </template>

    <ElScrollbar :style="dialogStyle">
      <slot></slot>
    </ElScrollbar>

    <template v-if="slots.footer" #footer>
      <slot name="footer"></slot>
    </template>
  </ElDialog>
</template>

<style lang="less">
.@{elNamespace}-overlay-dialog {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  overflow: hidden !important;
  padding: 16px !important;
  box-sizing: border-box !important;
  background-color: rgba(15, 23, 42, 0.45) !important;
  backdrop-filter: blur(12px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(12px) saturate(180%) !important;
  transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;

  &:has(.is-fullscreen) {
    padding: 0 !important;
  }
}

.@{elNamespace}-dialog {
  margin: 0 !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
  max-width: 95vw !important;
  max-height: 92vh !important;
  height: auto;
  box-sizing: border-box !important;
  background-color: var(--el-bg-color-overlay, #ffffff) !important;
  border: 1px solid rgba(226, 232, 240, 0.85) !important;
  border-radius: 20px !important;
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.22), 0 0 0 1px rgba(15, 23, 42, 0.05) !important;
  color: var(--el-text-color-primary, #0f172a) !important;
  transform: translateZ(0);
  will-change: transform, opacity;

  &.is-fullscreen {
    width: 100vw !important;
    height: 100vh !important;
    max-width: 100vw !important;
    max-height: 100vh !important;
    border-radius: 0 !important;
    border: none !important;

    .dialog-header-bar {
      border-radius: 0 !important;
    }
  }

  &.is-resizable:not(.is-fullscreen) {
    position: relative !important;
    min-width: 320px !important;
    min-height: 180px !important;
    max-width: 95vw !important;
    max-height: 92vh !important;

    /* Corner resize grip handle */
    &::after {
      content: '';
      position: absolute;
      bottom: 4px;
      right: 4px;
      width: 10px;
      height: 10px;
      border-right: 2px solid var(--el-text-color-placeholder, #9ca3af);
      border-bottom: 2px solid var(--el-text-color-placeholder, #9ca3af);
      cursor: nwse-resize;
      pointer-events: none;
      z-index: 99;
      opacity: 0.7;
    }
  }

  &__header {
    height: 52px;
    padding: 0 !important;
    margin-right: 0 !important;
    border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
    color: var(--el-text-color-primary, #0f172a) !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    flex-shrink: 0 !important;

    .dialog-header-bar {
      width: 100% !important;
      padding: 0 18px !important;
    }
  }

  &__body {
    flex: 1 1 0% !important;
    min-height: 0 !important;
    padding: 18px 22px !important;
    background-color: var(--el-bg-color-overlay, #ffffff) !important;
    color: var(--el-text-color-primary, #0f172a) !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    box-sizing: border-box !important;

    > .el-scrollbar {
      flex: 1 1 0% !important;
      display: flex !important;
      flex-direction: column !important;
      width: 100% !important;
      height: 100% !important;
      min-height: 0 !important;

      > .el-scrollbar__wrap {
        flex: 1 1 0% !important;
        width: 100% !important;
        height: 100% !important;
        max-height: 100% !important;
        min-height: 0 !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;

        > .el-scrollbar__view {
          min-height: 100% !important;
          height: auto !important;
          display: flex !important;
          flex-direction: column !important;
        }
      }
    }
  }

  &__footer {
    flex-shrink: 0 !important;
    border-top: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
    background-color: var(--el-fill-color-light, #f8fafc) !important;
    padding: 12px 20px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 10px !important;
  }

  &__headerbtn {
    top: 0;
  }
}

html.dark {
  .@{elNamespace}-overlay-dialog {
    background-color: rgba(0, 0, 0, 0.65) !important;
  }

  .@{elNamespace}-dialog {
    background-color: #0f172a !important;
    border-color: #334155 !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85), 0 0 0 1px rgba(255, 255, 255, 0.08) !important;
    color: var(--el-text-color-primary, #f8fafc) !important;

    &__header {
      border-bottom-color: #334155 !important;
      background: linear-gradient(180deg, #1e293b 0%, #172033 100%) !important;
      color: #f8fafc !important;
    }

    &__body {
      background-color: #0f172a !important;
      color: #f8fafc !important;
    }

    &__footer {
      border-top-color: #334155 !important;
      background-color: #172033 !important;
    }
  }
}

/* Stylish, visible scrollbar for all dialogs */
.el-scrollbar__bar {
  opacity: 0.5 !important;
  transition: opacity 0.2s ease !important;
  z-index: 20 !important;
}

.el-scrollbar:hover .el-scrollbar__bar {
  opacity: 0.9 !important;
}

.el-scrollbar__thumb {
  background-color: rgba(148, 163, 184, 0.5) !important;
  border-radius: 6px !important;
  &:hover {
    background-color: rgba(100, 116, 139, 0.8) !important;
  }
}

@media (max-width: 768px) {
  .@{elNamespace}-overlay-dialog {
    padding: 8px !important;
    align-items: flex-end !important;
  }

  .@{elNamespace}-dialog {
    width: 100% !important;
    max-width: 100% !important;
    max-height: 92vh !important;
    border-radius: 18px 18px 0 0 !important;
    margin: 0 !important;
  }
}
</style>
