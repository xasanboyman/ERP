<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
import { ref, onMounted } from 'vue'
import {
  ElButton,
  ElTable,
  ElTableColumn,
  ElTag,
  ElMessage,
  ElMessageBox,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput
} from 'element-plus'
import {
  listDeviceTokensApi,
  pairDeviceTokenApi,
  revokeDeviceTokenApi,
  DeviceTokenItem
} from '@/api/device'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const loading = ref(false)
const deviceList = ref<DeviceTokenItem[]>([])

const fetchDevices = async (silent = false) => {
  try {
    if (!silent) {
      loading.value = true
    }
    const res = await listDeviceTokensApi()
    if (res && res.data) {
      deviceList.value = res.data.list || res.data || []
    }
  } catch (err: any) {
    if (!silent) {
      ElMessage.error(err.message || 'Qurilmalar ro‘yxatini yuklashda xatolik')
    }
  } finally {
    if (!silent) {
      loading.value = false
    }
  }
}

// Silently refresh devices list when pairing/revocation happens
useRealtimeSync('device', () => {
  fetchDevices(true)
})

// Pair Device Dialog
const pairDialogVisible = ref(false)
const deviceName = ref('')
const pairingResult = ref<{ pair_code: string; token: string; qr_payload: string } | null>(null)
const pairLoading = ref(false)

const openPairDialog = () => {
  deviceName.value = 'Telefon Skaner'
  pairingResult.value = null
  pairDialogVisible.value = true
}

const handleCreatePair = async () => {
  if (!deviceName.value.trim()) {
    ElMessage.warning('Qurilma nomini kiriting!')
    return
  }
  try {
    pairLoading.value = true
    const res = await pairDeviceTokenApi({ device_name: deviceName.value.trim() })
    if (res && res.data) {
      const pairCode = res.data?.pair_code || (res as any)?.pair_code
      const host = window.location.host || 'localhost:4000'
      const directUrl = `http://${host}/#/mobile/scanner?pair_code=${encodeURIComponent(pairCode)}`
      pairingResult.value = {
        pair_code: pairCode,
        token: res.data?.token || (res as any)?.token,
        qr_payload: directUrl
      }
      ElMessage.success('Ulash kodi va auto-pairing QR generator muvaffaqiyatli yaratildi!')
      fetchDevices()
    }
  } catch (err: any) {
    ElMessage.error(err.message || 'Qurilma kodini yaratishda xatolik')
  } finally {
    pairLoading.value = false
  }
}

const handleRevoke = (device: DeviceTokenItem) => {
  ElMessageBox.confirm(
    `'${device.device_name}' qurilmasini o'chirishga (uzishga) ishonchingiz komilmi? Token darhol bekor qilinadi.`,
    "Qurilmani o'chirish",
    {
      confirmButtonText: 'Uzish',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await revokeDeviceTokenApi(device.id)
      ElMessage.success("Qurilma muvaffaqiyatli o'chirildi!")
      fetchDevices()
    } catch (err: any) {
      ElMessage.error(err.message || "Qurilmani o'chirishda xatolik")
    }
  })
}

onMounted(() => {
  fetchDevices()
})
</script>

<template>
  <div class="connected-devices">
    <div class="flex justify-between items-center mb-15px">
      <div class="text-16px font-bold">Ulangan Mobil Skaner Qurilmalari</div>
      <ElButton type="primary" @click="openPairDialog"> + Yangi Qurilma Ulash (QR Kod) </ElButton>
    </div>

    <ElTable :data="deviceList" v-loading="loading" border style="width: 100%">
      <ElTableColumn prop="id" label="ID" width="70" align="center" />
      <ElTableColumn prop="device_name" label="Qurilma Nomi" min-width="150" />
      <ElTableColumn prop="pair_code" label="Ulash Kodi" width="120" align="center">
        <template #default="{ row }">
          <ElTag type="info" effect="dark">{{ row.pair_code }}</ElTag>
        </template>
      </ElTableColumn>
      <ElTableColumn prop="status" :label="t('erp.holati')" width="110" align="center">
        <template #default="{ row }">
          <ElTag :type="row.status === 'active' ? 'success' : 'danger'">
            {{ row.status === 'active' ? 'Faol' : "O'chirilgan" }}
          </ElTag>
        </template>
      </ElTableColumn>
      <ElTableColumn prop="created_at" label="Yaratilgan Vaqti" min-width="160" />
      <ElTableColumn :label="t('erp.amallar')" width="130" align="center">
        <template #default="{ row }">
          <ElButton
            v-if="row.status === 'active'"
            type="danger"
            size="small"
            @click="handleRevoke(row)"
            >{{ t('common.delete') }}</ElButton
          >
          <span v-else class="text-gray-400">O'chirilgan</span>
        </template>
      </ElTableColumn>
    </ElTable>

    <!-- Pair Dialog -->
    <ElDialog
      v-model="pairDialogVisible"
      title="Mobil Skaner Qurilmasini Ulash"
      width="500px"
      append-to-body
    >
      <div v-if="!pairingResult">
        <ElForm label-position="top">
          <ElFormItem label="Qurilma Nomi (masalan: Samsung S23, iPhone 14)">
            <ElInput v-model="deviceName" placeholder="Qurilma nomini kiriting" />
          </ElFormItem>
        </ElForm>
        <div class="text-13px text-gray-500 mt-10px">
          * Ushbu qurilma uchun doimiy skanerlash va sotuv huquqi beriladi. Profil markazidan uni
          istalgan vaqtda o'chirib bekor qilishingiz mumkin.
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-10px">
        <div class="text-16px font-bold text-green-600 mb-10px">
          QR Kod tayyor! Telefon kamerangiz bilan skanerlang:
        </div>
        <div class="p-15px bg-white border rounded-lg shadow-sm mb-15px flex justify-center">
          <img
            :src="`https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(pairingResult.qr_payload)}`"
            alt="Pairing QR Code"
            class="w-220px h-220px border rounded"
          />
        </div>
        <div class="text-14px font-medium mb-5px">
          Ulash Kodi:
          <span class="text-18px font-bold text-blue-600">{{ pairingResult.pair_code }}</span>
        </div>
        <div class="text-12px text-gray-400 text-center px-20px">
          Ushbu QR kodni telefonda skanerlash orqali kompyuter va telefon o'rtasida xavfsiz ulanish
          o'rnatiladi.
        </div>
      </div>

      <template #footer>
        <template v-if="!pairingResult">
          <ElButton @click="pairDialogVisible = false">{{ t('common.cancel') }}</ElButton>
          <ElButton type="primary" :loading="pairLoading" @click="handleCreatePair">
            QR Kod Yaratish
          </ElButton>
        </template>
        <template v-else>
          <ElButton type="primary" @click="pairDialogVisible = false">{{
            t('common.close')
          }}</ElButton>
        </template>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.connected-devices {
  padding: 10px 0;
}
</style>
