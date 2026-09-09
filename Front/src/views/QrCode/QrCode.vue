<template>
  <ContentWrap>
    <div class="mb-20px flex justify-between items-center">
      <div>
        <el-button type="primary" @click="openGenerateDialog">QR Kod Generatsiya qilish</el-button>
        <el-button type="success" :disabled="selectedQrs.length === 0" @click="handlePrintSelected">
          Tanlanganlarni chop etish (PDF/Yorliq)
        </el-button>
      </div>
      <el-button type="danger" :disabled="selectedQrIds.length === 0" @click="handleBatchDelete">
        Guruhli o'chirish
      </el-button>
    </div>

    <!-- Table -->
    <el-table
      v-loading="loading"
      :data="tableData"
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="code" label="QR Kod" width="180">
        <template #default="scope">
          <span class="font-mono bg-slate-100 px-2 py-1 rounded text-xs">{{ scope.row.code }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="task_details.order_number" label="Buyurtma #" width="130" />
      <el-table-column
        prop="task_details.product_name"
        label="Mahsulot"
        min-width="150"
        show-overflow-tooltip
      />
      <el-table-column prop="task_details.stage_name" label="Etap (Operatsiya)" width="150" />
      <el-table-column prop="quantity" label="Ish miqdori (dona)" width="150" align="center" />
      <el-table-column prop="createTime" label="Yaratilgan vaqt" width="180" />
      <el-table-column :label="t('erp.amallar')" width="120" fixed="right">
        <template #default="scope">
          <el-button link type="danger" @click="handleDelete(scope.row)">{{
            t('common.delete')
          }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- QR Generate Dialog -->
    <el-dialog v-model="dialogVisible" title="Vazifa uchun QR kod generatsiya qilish" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="Vazifa" prop="taskId">
          <el-select v-model="form.taskId" placeholder="Vazifani tanlang" style="width: 100%">
            <el-option v-for="t in tasks" :key="t.id" :label="getTaskLabel(t)" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Ish miqdori" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm"
          >Generatsiya</el-button
        >
      </template>
    </el-dialog>

    <!-- Print Preview Overlay -->
    <el-dialog v-model="printVisible" title="QR yorliqlarni chop etish" width="700px">
      <div id="print-area" class="print-container">
        <div v-for="qr in selectedQrs" :key="qr.id" class="qr-card">
          <div class="qr-header">APEX ERP - TRACKING LABEL</div>
          <div class="qr-content">
            <div class="qr-info">
              <div><strong>Buyurtma:</strong> {{ qr.task_details?.order_number }}</div>
              <div><strong>Mahsulot:</strong> {{ qr.task_details?.product_name }}</div>
              <div><strong>Etap:</strong> {{ qr.task_details?.stage_name }}</div>
              <div><strong>Miqdor:</strong> {{ qr.quantity }} ta</div>
            </div>
            <!-- Mock barcode/QR container for high-tech print preview -->
            <div class="qr-barcode-box">
              <div class="qr-mock-code"></div>
              <span class="qr-code-text">{{ qr.code }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="printVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="triggerPrint">Chop etish</el-button>
      </template>
    </el-dialog>
  </ContentWrap>
</template>

<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
import { ref, reactive, onMounted } from 'vue'
import { ContentWrap } from '@/components/ContentWrap'
import {
  ElMessage,
  ElMessageBox,
  ElButton,
  ElTable,
  ElTableColumn,
  ElDialog,
  ElForm,
  ElFormItem,
  ElSelect,
  ElOption,
  ElInputNumber
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getQrListApi, saveQrApi, deleteQrApi } from '@/api/qr'
import { getTaskListApi } from '@/api/cutting'

const loading = ref(false)
const tableData = ref<any[]>([])
const tasks = ref<any[]>([])
const selectedQrs = ref<any[]>([])
const selectedQrIds = ref<string[]>([])

const getList = async () => {
  loading.value = true
  try {
    const res = await getQrListApi()
    if (res && res.code === 0) {
      tableData.value = res.data.list || []
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const getTasks = async () => {
  try {
    const res = await getTaskListApi()
    if (res && res.code === 0) {
      tasks.value = res.data.list || []
    }
  } catch (err) {
    console.error(err)
  }
}

const handleSelectionChange = (selection: any[]) => {
  selectedQrs.value = selection
  selectedQrIds.value = selection.map((item) => item.id)
}

const getTaskLabel = (t: any) => {
  return `${t.order_number_snapshot} — ${t.stage_name_snapshot} (${t.product_name_snapshot})`
}

// Generate Dialog Logic
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  taskId: '',
  quantity: 100
})

const rules = reactive<FormRules>({
  taskId: [{ required: true, message: 'Iltimos, vazifani tanlang', trigger: 'change' }],
  quantity: [{ required: true, message: 'Iltimos, miqdorni kiriting', trigger: 'blur' }]
})

const openGenerateDialog = () => {
  form.taskId = ''
  form.quantity = 100
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const res = await saveQrApi(form)
        if (res) {
          ElMessage.success('QR Kod muvaffaqiyatli yaratildi!')
          dialogVisible.value = false
          getList()
        }
      } catch (err) {
        console.error(err)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm("Ushbu QR kodni o'chirishni tasdiqlaysizmi?", 'Eslatma', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'warning'
  })
    .then(async () => {
      const res = await deleteQrApi({ ids: [row.id] })
      if (res && res.code === 0) {
        ElMessage.success("QR kod o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

const handleBatchDelete = () => {
  if (selectedQrIds.value.length === 0) return
  ElMessageBox.confirm(
    `Tanlangan ${selectedQrIds.value.length} ta QR kodni o'chirishni tasdiqlaysizmi?`,
    'Eslatma',
    {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(async () => {
      const res = await deleteQrApi({ ids: selectedQrIds.value })
      if (res && res.code === 0) {
        ElMessage.success("Tanlangan QR kodlar o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

// Print logic
const printVisible = ref(false)
const handlePrintSelected = () => {
  printVisible.value = true
}

const triggerPrint = () => {
  const printContents = document.getElementById('print-area')?.innerHTML
  if (!printContents) return

  const popupWin = window.open('', '_blank', 'width=800,height=600')
  if (popupWin) {
    popupWin.document.open()
    popupWin.document.write(`
      <html>
        <head>
          <title>QR Labels Print</title>
          <style>
            body { font-family: sans-serif; margin: 20px; }
            .print-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
            .qr-card { border: 2px dashed #000; padding: 15px; border-radius: 8px; box-sizing: border-box; }
            .qr-header { font-size: 10px; font-weight: bold; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-bottom: 10px; text-align: center; }
            .qr-content { display: flex; justify-content: space-between; align-items: center; }
            .qr-info { font-size: 12px; line-height: 1.5; }
            .qr-barcode-box { text-align: center; }
            .qr-mock-code { width: 80px; height: 80px; background: repeating-linear-gradient(45deg, #000, #000 4px, #fff 4px, #fff 8px); border: 1px solid #000; margin-bottom: 5px; }
            .qr-code-text { font-family: monospace; font-size: 10px; }
            @media print {
              .qr-card { page-break-inside: avoid; }
            }
          </style>
        </head>
        <body onload="window.print();window.close()">
          <div class="print-container">${printContents}</div>
        </body>
      </html>
    `)
    popupWin.document.close()
  }
}

onMounted(() => {
  getList()
  getTasks()
})
</script>

<style scoped>
.mb-20px {
  margin-bottom: 20px;
}
.font-mono {
  font-family: monospace;
}
.print-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
}
.qr-card {
  border: 1px dashed var(--el-color-primary, #409eff);
  padding: 15px;
  border-radius: 8px;
  background-color: var(--el-fill-color-light, #f8fafc);
  color: var(--el-text-color-primary, #0f172a);
}
.qr-header {
  font-size: 10px;
  font-weight: bold;
  border-bottom: 1px solid var(--el-border-color-lighter, #e6ebf5);
  padding-bottom: 5px;
  margin-bottom: 10px;
  text-align: center;
  color: var(--el-color-primary, #409eff);
}
.qr-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.qr-info {
  font-size: 12px;
  line-height: 1.6;
  color: var(--el-text-color-primary, #0f172a);
}
.qr-barcode-box {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.qr-mock-code {
  width: 70px;
  height: 70px;
  background: repeating-linear-gradient(45deg, #333, #333 4px, #eee 4px, #eee 8px);
  border: 1px solid var(--el-border-color, #ccc);
  margin-bottom: 5px;
}
.qr-code-text {
  font-family: monospace;
  font-size: 9px;
  color: var(--el-text-color-secondary, #606266);
}
</style>
