<script setup lang="ts">
import { computed, unref } from 'vue'
import { ElIcon } from 'element-plus'
import { propTypes } from '@/utils/propTypes'
import { useDesign } from '@/hooks/web/useDesign'
import { Icon as IconifyIcon } from '@iconify/vue'
import { ICON_PREFIX } from '@/constants'

const { getPrefixCls } = useDesign()
const prefixCls = getPrefixCls('icon')

const props = defineProps({
  icon: propTypes.string,
  color: propTypes.string,
  size: propTypes.number.def(16),
  hoverColor: propTypes.string
})

const isLocal = computed(() => (props.icon ? props.icon.startsWith('svg-icon:') : false))

const symbolId = computed(() => {
  return unref(isLocal) && props.icon
    ? `#icon-${props.icon.split('svg-icon:')[1]}`
    : props.icon || ''
})

const getIconName = computed(() => {
  if (!props.icon) return ''
  let name = props.icon.startsWith(ICON_PREFIX) ? props.icon.replace(ICON_PREFIX, '') : props.icon
  if (name.startsWith('vi-')) {
    name = name.replace('vi-', '')
  }
  return name
})

const getIconifyStyle = computed(() => {
  const { color, size } = props
  return {
    fontSize: `${size}px`,
    color
  }
})
</script>

<template>
  <ElIcon :class="prefixCls" :size="size" :color="color">
    <svg v-if="isLocal" aria-hidden="true">
      <use :xlink:href="symbolId" />
    </svg>

    <IconifyIcon v-else-if="icon" :icon="getIconName" :style="getIconifyStyle" />
  </ElIcon>
</template>

<style lang="less" scoped>
@prefix-cls: ~'@{adminNamespace}-icon';

.@{prefix-cls},
.iconify {
  :deep(svg) {
    &:hover {
      // stylelint-disable-next-line
      color: v-bind(hoverColor) !important;
    }
  }
}

.iconify {
  &:hover {
    // stylelint-disable-next-line
    color: v-bind(hoverColor) !important;
  }
}
</style>
