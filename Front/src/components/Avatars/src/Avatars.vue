<script setup lang="ts">
import { ComponentSize, ElTooltip } from 'element-plus'
import { PropType, computed } from 'vue'
import { AvatarItem } from './types'
import { useDesign } from '@/hooks/web/useDesign'

const { getPrefixCls } = useDesign()
const prefixCls = getPrefixCls('avatars')

const props = defineProps({
  size: {
    type: [String, Number] as PropType<ComponentSize | number>,
    default: 'small'
  },
  max: {
    type: Number,
    default: 5
  },
  data: {
    type: Array as PropType<AvatarItem[]>,
    default: () => []
  },
  showTooltip: {
    type: Boolean,
    default: true
  }
})

const filterData = computed(() => props.data.slice(0, props.max))

/** px size of the circle */
const pxSize = computed(() => {
  if (typeof props.size === 'number') return props.size
  const map: Record<string, number> = { large: 40, default: 32, small: 24, '': 32 }
  return map[props.size as string] ?? 32
})

/** negative left margin so each avatar overlaps by ~55% */
const overlapPx = computed(() => Math.ceil(pxSize.value * 0.55))

/** font-size for initials text */
const fontSize = computed(() => Math.max(8, Math.floor(pxSize.value * 0.38)) + 'px')

/** deterministic hue from a string – gives each person a unique colour */
function hue(str: string): number {
  let h = 0
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) & 0xffff
  return h % 360
}

function gradientFor(item: AvatarItem): string {
  const key = item.initials || item.name || '?'
  const h = hue(key)
  return `linear-gradient(135deg, hsl(${h},72%,54%), hsl(${(h + 42) % 360},72%,38%))`
}

function bubbleStyle(item: AvatarItem, index: number): Record<string, string | number> {
  const base: Record<string, string | number> = {
    width: pxSize.value + 'px',
    height: pxSize.value + 'px',
    minWidth: pxSize.value + 'px',
    borderRadius: '50%',
    zIndex: index + 1,
    marginLeft: index === 0 ? '0' : `-${overlapPx.value}px`,
    fontSize: fontSize.value
  }
  if (!item.url) base['background'] = gradientFor(item)
  return base
}

function overflowStyle(): Record<string, string | number> {
  const h = 210
  return {
    width: pxSize.value + 'px',
    height: pxSize.value + 'px',
    minWidth: pxSize.value + 'px',
    borderRadius: '50%',
    zIndex: props.data.length + 1,
    marginLeft: `-${overlapPx.value}px`,
    fontSize: fontSize.value,
    background: `linear-gradient(135deg, hsl(${h},50%,45%), hsl(${h + 30},55%,32%))`
  }
}
</script>

<template>
  <div :class="prefixCls" class="flex items-center">
    <template
      v-for="(item, index) in filterData"
      :key="(item.url || item.initials || '') + '_' + index"
    >
      <!-- With tooltip -->
      <ElTooltip v-if="showTooltip && item.name" :content="item.name" placement="top">
        <div v-if="item.url" class="avatar-bubble" :style="bubbleStyle(item, index)">
          <img :src="item.url" class="avatar-img" :alt="item.name || ''" />
        </div>
        <div v-else class="avatar-bubble initials-bubble" :style="bubbleStyle(item, index)">
          {{ item.initials || (item.name || '?').slice(0, 2).toUpperCase() }}
        </div>
      </ElTooltip>

      <!-- Without tooltip -->
      <template v-else>
        <div v-if="item.url" class="avatar-bubble" :style="bubbleStyle(item, index)">
          <img :src="item.url" class="avatar-img" :alt="item.name || ''" />
        </div>
        <div v-else class="avatar-bubble initials-bubble" :style="bubbleStyle(item, index)">
          {{ item.initials || (item.name || '?').slice(0, 2).toUpperCase() }}
        </div>
      </template>
    </template>

    <!-- +N overflow bubble -->
    <div v-if="data.length > max" class="avatar-bubble initials-bubble" :style="overflowStyle()">
      +{{ data.length - max }}
    </div>
  </div>
</template>

<style scoped lang="less">
@prefix-cls: ~'@{adminNamespace}-avatars';

.@{prefix-cls} {
  display: inline-flex;
  align-items: center;
}

.avatar-bubble {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 2.5px solid var(--el-bg-color, #fff);
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.18);
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
  position: relative;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease;

  &:hover {
    transform: scale(1.18) translateY(-3px);
    box-shadow: 0 5px 16px rgba(0, 0, 0, 0.24);
    z-index: 999 !important;
  }
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.initials-bubble {
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.4px;
  user-select: none;
}
</style>
