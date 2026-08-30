<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElDialog, ElButton, ElTag, ElMessage, ElTable, ElTableColumn } from 'element-plus'
import { respondSalesPushApi, getPushPayloadApi } from '@/api/device'
import { formatMoney } from '@/utils'

const router = useRouter()

const dialogVisible = ref(false)
const activePush = ref<any>(null)
const pushItems = ref<any[]>([])
const loading = ref(false)

const pollTimer: any = null

const handledPushIds = ref<Set<string>>(new Set())

const handleAccept = async () => {
  if (!activePush.value) return
  const pushId = activePush.value.push_id
  handledPushIds.value.add(pushId)

  try {
    loading.value = true
    await respondSalesPushApi(pushId, 'accept')
    ElMessage.success("🚀 Telefon skaneri qabul qilindi! POS Kassaga o'tilmoqda...")
    dialogVisible.value = false

    // Fetch full payload and navigate to /sales/pos (Yangi Sotuv)
    const payloadRes = await getPushPayloadApi(pushId)
    const itemsToPreFill = payloadRes?.data?.items || (payloadRes as any)?.items || pushItems.value

    // Save payload to session storage for Pos.vue to read
    sessionStorage.setItem('PENDING_POS_CART', JSON.stringify(itemsToPreFill))

    // Dispatch custom event for Pos.vue if already mounted
    window.dispatchEvent(new CustomEvent('LOAD_PENDING_POS_CART', { detail: itemsToPreFill }))

    // Navigate to POS terminal
    router.push('/sales/pos')
  } catch (err: any) {
    ElMessage.error(err.message || 'Push alertni qabul qilishda xatolik')
  } finally {
    loading.value = false
    activePush.value = null
  }
}

const handleDecline = async () => {
  if (!activePush.value) return
  const pushId = activePush.value.push_id
  handledPushIds.value.add(pushId)

  try {
    loading.value = true
    await respondSalesPushApi(pushId, 'decline')
    ElMessage.info("Telefon skaner ma'lumoti rad etildi.")
    dialogVisible.value = false
  } catch (err: any) {
    ElMessage.error(err.message || 'Push alertni rad etishda xatolik')
  } finally {
    loading.value = false
    activePush.value = null
  }
}

const handleCloseDialog = () => {
  if (activePush.value) {
    handledPushIds.value.add(activePush.value.push_id)
    respondSalesPushApi(activePush.value.push_id, 'decline').catch(() => {})
  }
  dialogVisible.value = false
  activePush.value = null
}

import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

useRealtimeSync('sales_push', (event) => {
  if (event.action === 'created' && event.data) {
    const pushData = event.data
    activePush.value = pushData
    pushItems.value = pushData.items || []
    dialogVisible.value = true
  }
})

onMounted(() => {
  // Real-time synchronization active via useRealtimeSync
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
})
</script>

<template>
  <ElDialog
    v-model="dialogVisible"
    title="📲 Telefonda Skanerlangan Mahsulotlar Qabul Qilindi!"
    width="600px"
    :close-on-click-modal="false"
    :before-close="handleCloseDialog"
    append-to-body
  >
    <div v-if="activePush" class="push-alert-content">
      <div class="flex justify-between items-center mb-15px bg-blue-50 p-10px rounded border">
        <div>
          <span class="text-gray-500">Qurilma: </span>
          <span class="font-bold text-blue-600">{{ activePush.device_name }}</span>
        </div>
        <ElTag type="warning" effect="dark">Jami: {{ activePush.item_count }} ta mahsulot</ElTag>
      </div>

      <ElTable :data="pushItems" border style="width: 100%" max-height="250">
        <ElTableColumn prop="product_name" label="Mahsulot Nomi" min-width="160" />
        <ElTableColumn prop="quantity" label="Soni" width="80" align="center" />
        <ElTableColumn prop="price" label="Narxi" width="100" align="center">
          <template #default="{ row }"> ${{ formatMoney(row.price) }} </template>
        </ElTableColumn>
        <ElTableColumn label="Jami" width="100" align="center">
          <template #default="{ row }">
            ${{ formatMoney(Number(row.price) * Number(row.quantity)) }}
          </template>
        </ElTableColumn>
      </ElTable>
    </div>

    <template #footer>
      <div class="flex justify-end gap-10px">
        <ElButton type="danger" size="large" :loading="loading" @click="handleDecline">
          ✕ Rad etish (Decline)
        </ElButton>
        <ElButton
          type="success"
          size="large"
          class="font-bold"
          :loading="loading"
          @click="handleAccept"
        >
          ✓ Qabul qilish & POS (Accept)
        </ElButton>
      </div>
    </template>
  </ElDialog>
</template>

<style scoped>
.push-alert-content {
  font-family: inherit;
}
</style>
