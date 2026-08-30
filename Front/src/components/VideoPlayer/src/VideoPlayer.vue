<script setup lang="ts">
import { ref, unref, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  url: {
    type: String,
    default: '',
    required: true
  },
  poster: {
    type: String,
    default: ''
  }
})

const playerRef = ref<any>()

const videoEl = ref<HTMLDivElement>()

const intiPlayer = async () => {
  if (!unref(videoEl)) return
  try {
    const PlayerModule = await import('xgplayer')
    const PlayerClass = PlayerModule.default || PlayerModule
    playerRef.value = new PlayerClass({
      autoplay: false,
      ...props,
      el: unref(videoEl)
    })
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  intiPlayer()
})

watch(
  () => props,
  async (newProps) => {
    await nextTick()
    if (newProps) {
      unref(playerRef)?.setConfig(newProps)
    }
  },
  {
    deep: true
  }
)

onBeforeUnmount(() => {
  unref(playerRef)?.destroy()
})

defineExpose({
  playerExpose: () => unref(playerRef)
})
</script>

<template>
  <div ref="videoEl"></div>
</template>
