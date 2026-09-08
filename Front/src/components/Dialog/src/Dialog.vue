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
    maxHeight: '100%',
    height: '100%',
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
        class="dialog-header-bar flex justify-between items-center w-full h-50px px-16px select-none"
      >
        <div
          class="dialog-title-slot font-bold text-16px text-[var(--el-text-color-primary)] flex items-center gap-8px"
        >
          <slot name="title">
            {{ title ? t(title) : '' }}
          </slot>
        </div>
        <div class="dialog-header-actions flex items-center gap-12px">
          <Icon
            v-if="fullscreen"
            class="cursor-pointer is-hover text-gray-400 hover:text-[var(--el-text-color-primary)] text-18px"
            :icon="
              isFullscreen ? 'vi-radix-icons:exit-full-screen' : 'vi-radix-icons:enter-full-screen'
            "
            @click="toggleFull"
          />
          <Icon
            class="cursor-pointer is-hover text-gray-400 hover:text-red-400 text-20px font-bold"
            icon="vi-ep:close"
            @click="close"
          />
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
  border: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
  border-radius: 14px !important;
  box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.15) !important;
  color: var(--el-text-color-primary, #0f172a) !important;

  &.is-resizable {
    position: relative !important;
    min-width: 320px !important;
    min-height: 180px !important;
    max-width: 95vw !important;
    max-height: 92vh !important;

    /* Corner resize grip handle */
    &::after {
      content: '';
      position: absolute;
      bottom: 3px;
      right: 3px;
      width: 12px;
      height: 12px;
      border-right: 2px solid var(--el-text-color-placeholder, #9ca3af);
      border-bottom: 2px solid var(--el-text-color-placeholder, #9ca3af);
      cursor: nwse-resize;
      pointer-events: none;
      z-index: 99;
    }
  }

  &__header {
    height: 50px;
    padding: 0 !important;
    margin-right: 0 !important;
    border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
    background-color: var(--el-fill-color-light, #f8fafc) !important;
    color: var(--el-text-color-primary, #0f172a) !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    flex-shrink: 0 !important;

    .dialog-header-bar {
      width: 100% !important;
      padding: 0 16px !important;
    }
  }

  &__body {
    flex: 1 1 0% !important;
    min-height: 0 !important;
    padding: 16px 20px !important;
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
  }

  &__headerbtn {
    top: 0;
  }
}

:global(.dark) {
  .@{elNamespace}-dialog {
    background-color: var(--el-bg-color-overlay, #111827) !important;
    border-color: var(--el-border-color, #374151) !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8) !important;
    color: var(--el-text-color-primary, #f8fafc) !important;

    &__header {
      border-bottom-color: var(--el-border-color, #374151) !important;
      background-color: #1f2937 !important;
      color: #f8fafc !important;
    }

    &__body {
      background-color: #111827 !important;
      color: #f8fafc !important;
    }

    &__footer {
      border-top-color: var(--el-border-color, #374151) !important;
      background-color: #1f2937 !important;
    }
  }
}

/* Stylish, visible scrollbar for all dialogs */
.el-scrollbar__bar {
  opacity: 0.6 !important;
  transition: opacity 0.3s !important;
  z-index: 20 !important;
}

.el-scrollbar:hover .el-scrollbar__bar {
  opacity: 1 !important;
}

.el-scrollbar__thumb {
  background-color: rgba(148, 163, 184, 0.6) !important;
  border-radius: 4px !important;
}
</style>
