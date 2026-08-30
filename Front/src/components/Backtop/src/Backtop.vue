<script setup lang="ts">
import { ElBacktop } from 'element-plus'
import { useDesign } from '@/hooks/web/useDesign'
import { ref, onMounted, nextTick } from 'vue'

const { getPrefixCls, variables } = useDesign()

const prefixCls = getPrefixCls('backtop')
const hasTarget = ref(false)
const targetSelector = `.${variables.namespace}-layout-content-scrollbar .${variables.elNamespace}-scrollbar__wrap`

onMounted(async () => {
  await nextTick()
  if (typeof document !== 'undefined' && document.querySelector(targetSelector)) {
    hasTarget.value = true
  } else {
    // Retry shortly in case layout is still transitioning
    setTimeout(() => {
      if (document.querySelector(targetSelector)) {
        hasTarget.value = true
      }
    }, 200)
  }
})
</script>

<template>
  <ElBacktop v-if="hasTarget" :class="prefixCls" :target="targetSelector" />
</template>
