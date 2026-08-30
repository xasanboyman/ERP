<template>
  <ContentWrap>
    <div class="adj-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" class="btn-add" @click="openAddDialog">
          <span class="btn-icon">＋</span> {{ t('erp.newAdjustmentBtn') }}
        </el-button>
        <el-button
          type="danger"
          class="btn-batch-del"
          :disabled="selectedIds.length === 0"
          @click="handleBatchDelete"
        >
          {{ t('erp.batchDelete') }}
        </el-button>
      </div>
    </div>

    <!-- Table -->
    <div class="table-wrap">
      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        class="adj-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="120">
          <template #default="scope">
            <span class="id-mono">{{ scope.row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="workerName" label="Xodim (Usta)" width="180">
          <template #default="scope">
            <span class="worker-name">{{ scope.row.workerName }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="document_type" label="Turi" width="160" align="center">
          <template #default="scope">
            <span :class="['type-badge', `type-badge--${scope.row.document_type}`]">
              {{ getTypeLabel(scope.row.document_type) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="amount" :label="t('erp.miqdoriDollar')" min-width="160">
          <template #default="scope">
            <span class="amount-value font-mono whitespace-nowrap">{{
              formatMoney(scope.row.amount)
            }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="period_month"
          :label="t('erp.reportMonth')"
          width="130"
          align="center"
        >
          <template #default="scope">
            <span class="period-mono">{{ scope.row.period_month }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="description"
          label="Tavsif (Sababi)"
          min-width="200"
          show-overflow-tooltip
        />
        <el-table-column prop="createTime" label="Kiritilgan vaqt" width="180">
          <template #default="scope">
            <span class="date-mono">{{ scope.row.createTime }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('erp.amallar')" width="180" fixed="right">
          <template #default="scope">
            <el-button
              link
              type="primary"
              class="action-btn action-btn--edit"
              @click="openEditDialog(scope.row)"
              >{{ t('common.edit') }}</el-button
            >
            <el-button
              link
              type="danger"
              class="action-btn action-btn--del"
              @click="handleDelete(scope.row)"
              >{{ t('common.delete') }}</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? t('erp.addAdjustment') : t('erp.editAdjustment')"
      width="500px"
      class="adj-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item :label="t('erp.worker')" prop="workerId">
          <el-select
            v-model="form.workerId"
            :placeholder="t('erp.selectWorker')"
            style="width: 100%"
          >
            <el-option v-for="w in workers" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('erp.docTypeLabel')" prop="document_type">
          <el-select v-model="form.document_type" placeholder="Turi" style="width: 100%">
            <el-option :label="t('erp.bonusRewardOption')" value="bonus" />
            <el-option label="Jarima (Fine)" value="fine" />
            <el-option label="Avans (Advance)" value="advance" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('erp.miqdoriDollar')" prop="amount">
          <el-input
            :model-value="form.amount ? moneyFormatter(form.amount) : ''"
            placeholder="0"
            @input="
              (val: string) => {
                form.amount = Number(moneyParser(val)) || 0
              }
            "
          >
            <template #prefix>$</template>
          </el-input>
        </el-form-item>
        <el-form-item :label="t('erp.reportMonth')" prop="period_month">
          <el-date-picker
            v-model="form.period_month"
            type="month"
            value-format="YYYY-MM"
            placeholder="Oy tanlang"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('erp.tavsif')" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            :placeholder="t('erp.adjustmentReasonPlaceholder')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="submitLoading" @click="submitForm">{{
            t('common.save')
          }}</el-button>
        </div>
      </template>
    </el-dialog>
  </ContentWrap>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from '@/hooks/web/useI18n'
import { ContentWrap } from '@/components/ContentWrap'
import {
  ElMessage,
  ElMessageBox,
  ElButton,
  ElTable,
  ElTableColumn,
  ElTag,
  ElDialog,
  ElForm,
  ElFormItem,
  ElSelect,
  ElOption,
  ElInputNumber,
  ElDatePicker,
  ElInput
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getAdjustmentListApi, saveAdjustmentApi, deleteAdjustmentApi } from '@/api/staff_hr'
import { getWorkerListApi } from '@/api/worker'
import { formatMoney, moneyFormatter, moneyParser } from '@/utils'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const { t } = useI18n()

const loading = ref(false)
const tableData = ref<any[]>([])
const workers = ref<any[]>([])
const selectedIds = ref<string[]>([])

useRealtimeSync(['staff_hr', 'staff_adjustment', 'adjustment', 'worker'], () => {
  getList()
  getWorkers()
})

const getList = async () => {
  loading.value = true
  try {
    const res = await getAdjustmentListApi()
    if (res && res.code === 0) {
      tableData.value = res.data.list || []
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const getWorkers = async () => {
  try {
    const res = await getWorkerListApi({ pageIndex: 1, pageSize: 100 })
    if (res && res.code === 0) {
      workers.value = res.data.list || []
    }
  } catch (err) {
    console.error(err)
  }
}

const handleSelectionChange = (selection: any[]) => {
  selectedIds.value = selection.map((item) => item.id)
}

// Dialog Logic
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  id: '',
  workerId: '',
  document_type: 'bonus',
  amount: 0,
  period_month: '',
  description: ''
})

const rules = reactive<FormRules>({
  workerId: [{ required: true, message: 'Iltimos, xodimni tanlang', trigger: 'change' }],
  document_type: [{ required: true, message: 'Iltimos, hujjat turini tanlang', trigger: 'change' }],
  amount: [{ required: true, message: 'Iltimos, miqdorni kiriting', trigger: 'blur' }]
})

const openAddDialog = () => {
  dialogType.value = 'add'
  form.id = ''
  form.workerId = ''
  form.document_type = 'bonus'
  form.amount = 0
  form.period_month = new Date().toISOString().split('T')[0].substring(0, 7)
  form.description = ''
  dialogVisible.value = true
}

const openEditDialog = (row: any) => {
  dialogType.value = 'edit'
  form.id = row.id
  form.workerId = row.workerId
  form.document_type = row.document_type
  form.amount = row.amount
  form.period_month = row.period_month
  form.description = row.description || ''
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const res = await saveAdjustmentApi(form)
        if (res && res.code === 0) {
          ElMessage.success('Korrektirovka muvaffaqiyatli saqlandi')
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

const handleSubmit = submitForm

const handleDelete = (row: any) => {
  ElMessageBox.confirm("Ushbu korrektirovkani o'chirishni tasdiqlaysizmi?", 'Eslatma', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'warning'
  })
    .then(async () => {
      const res = await deleteAdjustmentApi({ ids: [row.id] })
      if (res && res.code === 0) {
        ElMessage.success("Korrektirovka o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return
  ElMessageBox.confirm(
    `Tanlangan ${selectedIds.value.length} ta korrektirovkani o'chirishni tasdiqlaysizmi?`,
    'Eslatma',
    {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(async () => {
      const res = await deleteAdjustmentApi({ ids: selectedIds.value })
      if (res && res.code === 0) {
        ElMessage.success("Tanlangan korrektirovka yozuvlari o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

// Helpers
const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    bonus: 'Bonus (Mukofot)',
    fine: 'Jarima (Shtraf)',
    advance: 'Avans'
  }
  return map[type] || type
}

const getTypeTag = (type: string): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
  const map: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
    bonus: 'success',
    fine: 'danger',
    advance: 'warning'
  }
  return map[type] || 'info'
}

onMounted(() => {
  getList()
  getWorkers()
})
</script>

<style scoped lang="less">
// ─── Variables ────────────────────────────────────────────────
@green: #10b981;
@green-glow: #10b981;
@amber: #f59e0b;
@amber-glow: #f59e0b;
@red: #ef4444;
@red-glow: #ef4444;
@blue: #3b82f6;
@blue-glow: #3b82f6;
@purple: #8b5cf6;
@purple-glow: #8b5cf6;
@mono: 'SF Mono', 'Fira Code', 'Fira Mono', monospace;

// ─── Toolbar ──────────────────────────────────────────────────
.adj-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--el-bg-color-overlay, #ffffff);
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);

  .toolbar-left {
    display: flex;
    gap: 10px;
    align-items: center;
  }
}

:global(.dark) {
  .adj-toolbar {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-color: #1e293b;
    box-shadow: none;
  }
}

// ─── Buttons ──────────────────────────────────────────────────
.btn-add {
  background: linear-gradient(135deg, @blue, darken(@blue, 8%)) !important;
  border: none !important;
  box-shadow: 0 2px 10px rgba(59, 130, 246, 0.35);
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  font-weight: 600;

  .btn-icon {
    margin-right: 6px;
    font-weight: 300;
    font-size: 16px;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 18px rgba(59, 130, 246, 0.55);
  }
}

.btn-batch-del {
  background: linear-gradient(135deg, @red, darken(@red, 8%)) !important;
  border: none !important;
  box-shadow: 0 2px 10px rgba(239, 68, 68, 0.25);
  transition:
    transform 0.2s,
    box-shadow 0.2s;

  &:not(:disabled):hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 18px rgba(239, 68, 68, 0.45);
  }
}

.btn-cancel {
  background: var(--el-fill-color, #f1f5f9) !important;
  border: 1px solid var(--el-border-color, #e2e8f0) !important;
  color: var(--el-text-color-regular, #475569) !important;
  transition:
    transform 0.2s,
    border-color 0.2s;

  &:hover {
    transform: translateY(-1px);
    border-color: @blue !important;
    color: @blue !important;
  }
}

.btn-save {
  background: linear-gradient(135deg, @green, darken(@green, 8%)) !important;
  border: none !important;
  box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
  transition:
    transform 0.2s,
    box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.5);
  }
}

// ─── Table Wrapper ────────────────────────────────────────────
.table-wrap {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);

  :deep(.el-table) {
    background: var(--el-bg-color-overlay, #ffffff);
    color: var(--el-text-color-primary, #0f172a);
    border: none;

    .el-table__header-wrapper th {
      background: var(--el-fill-color-light, #f8fafc) !important;
      color: var(--el-text-color-regular, #64748b) !important;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0);
      border-right: 1px solid var(--el-border-color-lighter, #e2e8f0);
      padding: 12px 0;
    }

    .el-table__body tr td {
      background: transparent;
      border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0);
      border-right: 1px solid var(--el-border-color-lighter, #e2e8f0);
      transition: background 0.18s;
    }

    .el-table__body tr:hover td {
      background: rgba(139, 92, 246, 0.05) !important;
    }

    .el-table__fixed-right,
    .el-table__fixed {
      background: var(--el-bg-color-overlay, #ffffff);
    }

    .el-table__fixed-right .el-table__body tr td,
    .el-table__fixed .el-table__body tr td {
      background: var(--el-bg-color-overlay, #ffffff);
    }
  }
}

:global(.dark) {
  .table-wrap {
    border-color: #1e293b;

    :deep(.el-table) {
      background: #0d1424;
      color: #e2e8f0;

      .el-table__header-wrapper th {
        background: #0d1424 !important;
        color: #94a3b8 !important;
        border-bottom-color: #1e293b;
        border-right-color: #1e293b;
      }

      .el-table__body tr td {
        border-bottom: 1px solid rgba(30, 41, 59, 0.7);
        border-right: 1px solid rgba(30, 41, 59, 0.5);
      }

      .el-table__body tr:hover td {
        background: rgba(139, 92, 246, 0.07) !important;
      }

      .el-table__fixed-right,
      .el-table__fixed {
        background: #0d1424;
      }

      .el-table__fixed-right .el-table__body tr td,
      .el-table__fixed .el-table__body tr td {
        background: #0d1424;
      }
    }
  }
}

// ─── Cell Atoms ───────────────────────────────────────────────
.id-mono {
  font-family: @mono;
  font-size: 12px;
  color: var(--el-text-color-secondary, #94a3b8);
}

.worker-name {
  font-weight: 600;
  color: var(--el-text-color-primary, #0f172a);
}

:global(.dark) .worker-name {
  color: #e2e8f0;
}

.amount-value {
  font-family: @mono;
  font-size: 13.5px;
  font-weight: 700;
  color: @green;
}

.period-mono {
  font-family: @mono;
  font-size: 12.5px;
  color: var(--el-text-color-regular, #475569);
}

:global(.dark) .period-mono {
  color: #cbd5e1;
}

.date-mono {
  font-family: @mono;
  font-size: 12px;
  color: var(--el-text-color-secondary, #94a3b8);
}

// ─── Type Badges ──────────────────────────────────────────────
.type-badge {
  display: inline-block;
  font-size: 11.5px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid transparent;
  letter-spacing: 0.03em;
  transition: box-shadow 0.2s;

  &--bonus {
    color: @green;
    background: rgba(16, 185, 129, 0.13);
    border-color: rgba(16, 185, 129, 0.4);
  }

  &--fine {
    color: @red;
    background: rgba(239, 68, 68, 0.13);
    border-color: rgba(239, 68, 68, 0.4);
  }

  &--advance {
    color: @amber;
    background: rgba(245, 158, 11, 0.13);
    border-color: rgba(245, 158, 11, 0.4);
  }
}

// ─── Action Buttons ───────────────────────────────────────────
.action-btn {
  font-size: 12.5px !important;
  font-weight: 600 !important;
  transition:
    transform 0.18s,
    text-shadow 0.18s !important;
  padding: 0 4px !important;

  &--edit {
    color: @blue !important;
    &:hover {
      transform: translateY(-1px);
    }
  }

  &--del {
    color: @red !important;
    &:hover {
      transform: translateY(-1px);
    }
  }
}
</style>
