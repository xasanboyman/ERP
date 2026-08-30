<script lang="tsx" setup>
import { propTypes } from '@/utils/propTypes'
import { computed, getCurrentInstance, onMounted, unref, useAttrs, useSlots } from 'vue'
import Dialog from './Dialog.vue'
import { useResize } from '../hooks/useResize'

const props = defineProps({
  modelValue: propTypes.bool.def(false),
  title: propTypes.string.def('Dialog'),
  fullscreen: propTypes.bool.def(true),
  initWidth: propTypes.oneOfType([Number, String]).def(''),
  initHeight: propTypes.oneOfType([Number, String]).def(''),
  minResizeWidth: propTypes.number.def(360),
  minResizeHeight: propTypes.number.def(220),
  autoHeight: propTypes.bool.def(true),
  resizable: propTypes.bool.def(true)
})

const { dialogHeight, maxHeight, minWidth, setupDrag } = useResize({
  minHeightPx: props.minResizeHeight,
  minWidthPx: props.minResizeWidth,
  initHeight: props.initHeight || undefined,
  initWidth: props.initWidth || undefined,
  storageKey: props.title,
  autoHeight: props.autoHeight
})

const vResize = {
  mounted(el: any) {
    const observer = new MutationObserver(() => {
      const elDialog = el.querySelector('.el-dialog')
      if (elDialog) {
        setupDrag(elDialog, el)
      }
    })
    observer.observe(el, { childList: true, subtree: true })
  }
}

const attrs = useAttrs()
const slots = useSlots()
const getBindValue = computed(() => {
  const delArr: string[] = [
    'maxHeight',
    'width',
    'style',
    'initWidth',
    'initHeight',
    'minResizeWidth',
    'minResizeHeight',
    'autoHeight'
  ]
  const obj = Object.assign({}, { ...unref(attrs), ...props })
  for (const key in obj) {
    if (delArr.indexOf(key) !== -1) {
      delete obj[key]
    }
  }
  return obj
})
const instance = getCurrentInstance()
const initDirective = () => {
  const directives = instance?.appContext?.app._context?.directives

  if (!directives || !directives['resize']) {
    instance?.appContext?.app.directive('resize', vResize)
  }
}
onMounted(() => {
  initDirective()
})
</script>

<template>
  <div v-resize>
    <Dialog
      v-bind="getBindValue"
      :maxHeight="maxHeight"
      :width="minWidth === 'auto' ? undefined : minWidth"
      :style="{ height: dialogHeight === 'auto' ? undefined : dialogHeight }"
      :resizable="resizable"
      :autoHeight="autoHeight"
    >
      <slot></slot>
      <template v-if="slots.title" #title>
        <slot name="title"></slot>
      </template>
      <template v-if="slots.footer" #footer>
        <slot name="footer"></slot>
      </template>
    </Dialog>
  </div>
</template>
