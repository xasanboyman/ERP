<template>
  <div class="output-container">
    <!-- Top Summary Stat Cards -->
    <ElRow :gutter="16" class="mb-20px">
      <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
        <div class="stat-card glass-card border-blue">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">{{ t('erp.totalCompletedTasks') }}</span>
              <div class="stat-number text-blue">
                {{ filteredData.length }} <span class="stat-unit">{{ t('erp.unitsCount') }}</span>
              </div>
            </div>
            <div class="stat-icon-wrapper bg-blue-gradient">
              <Icon icon="ep:document-checked" :size="22" class="text-white" />
            </div>
          </div>
        </div>
      </ElCol>

      <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
        <div class="stat-card glass-card border-emerald">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">{{ t('erp.totalCalculatedPayment') }}</span>
              <div class="stat-number text-emerald"> ${{ formatMoney(totalPayoutAmount) }} </div>
            </div>
            <div class="stat-icon-wrapper bg-emerald-gradient">
              <Icon icon="ep:money" :size="22" class="text-white" />
            </div>
          </div>
        </div>
      </ElCol>

      <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
        <div class="stat-card glass-card border-amber">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">{{ t('erp.shortTermWorkers') }}</span>
              <div class="stat-number text-amber">
                {{ uniqueWorkersCount }} <span class="stat-unit">{{ t('erp.peopleSuffix') }}</span>
              </div>
            </div>
            <div class="stat-icon-wrapper bg-amber-gradient">
              <Icon icon="ep:user" :size="22" class="text-white" />
            </div>
          </div>
        </div>
      </ElCol>

      <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
        <div class="stat-card glass-card border-purple">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">{{ t('erp.avgTaskPrice') }}</span>
              <div class="stat-number text-purple"> ${{ formatMoney(avgPayoutPerTask) }} </div>
            </div>
            <div class="stat-icon-wrapper bg-purple-gradient">
              <Icon icon="ep:pie-chart" :size="22" class="text-white" />
            </div>
          </div>
        </div>
      </ElCol>
    </ElRow>

    <ContentWrap>
      <!-- Filter and Action Bar -->
      <div class="filter-action-bar flex flex-wrap justify-between items-center gap-12px mb-16px">
        <ElForm :inline="true" class="flex flex-wrap items-center gap-12px !mb-0">
          <ElFormItem class="!mr-0">
            <ElDatePicker
              v-model="filterDateRange"
              type="daterange"
              range-separator="—"
              :start-placeholder="t('erp.startDate')"
              :end-placeholder="t('erp.endDate')"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              clearable
              class="date-picker-range"
            />
          </ElFormItem>

          <ElFormItem class="!mr-0">
            <ElSelect
              v-model="filterWorkerName"
              :placeholder="t('erp.allWorkersFilter')"
              clearable
              filterable
              style="width: 220px"
            >
              <ElOption
                v-for="name in allWorkerSuggestions"
                :key="name"
                :label="name"
                :value="name"
              />
            </ElSelect>
          </ElFormItem>

          <ElFormItem class="!mr-0">
            <ElInput
              v-model="searchKeyword"
              :placeholder="t('erp.searchTaskOrRemark')"
              clearable
              prefix-icon="vi-ep:search"
              style="width: 240px"
            />
          </ElFormItem>

          <ElFormItem class="!mr-0">
            <ElButton @click="resetFilters">{{ t('common.reset') }}</ElButton>
          </ElFormItem>
        </ElForm>

        <div class="action-buttons flex items-center gap-10px">
          <ElButton type="primary" size="large" class="add-btn shadow-btn" @click="openAddDialog">
            <Icon icon="vi-ep:plus" class="mr-6px" /> {{ t('erp.addNewWorkVolume') }}
          </ElButton>
          <ElButton
            type="danger"
            size="large"
            plain
            :disabled="selectedIds.length === 0"
            @click="handleBatchDelete"
          >
            <Icon icon="vi-ep:delete" class="mr-4px" /> {{ t('common.delete') }} ({{
              selectedIds.length
            }})
          </ElButton>
        </div>
      </div>

      <!-- Main Outputs Table -->
      <div class="table-wrapper">
        <ElTable
          v-loading="loading"
          :data="filteredData"
          style="width: 100%"
          border
          stripe
          class="custom-outputs-table"
          @selection-change="handleSelectionChange"
        >
          <ElTableColumn type="selection" width="50" align="center" />

          <ElTableColumn :label="t('erp.dateDayMonthYear')" width="150" align="center">
            <template #default="{ row }">
              <span
                class="font-mono text-13px font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/50 px-8px py-3px rounded-md border border-blue-200 dark:border-blue-800"
              >
                {{ formatWorkDate(row) }}
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="workerName" :label="t('erp.workerCraftsmanName')" min-width="190">
            <template #default="{ row }">
              <div class="flex items-center gap-8px">
                <div
                  class="w-30px h-30px rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 flex items-center justify-center font-bold text-12px flex-shrink-0"
                >
                  {{ (row.workerName || row.workerId || 'I')[0].toUpperCase() }}
                </div>
                <div class="flex flex-col">
                  <span class="font-bold text-[var(--el-text-color-primary)] text-13px">
                    {{ row.workerName || row.workerId || 'Vaqtinchalik Ishchi' }}
                  </span>
                  <span class="text-11px text-gray-400">{{ t('erp.temporaryWorkers') }}</span>
                </div>
              </div>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="name"
            :label="t('erp.completedTaskOp')"
            min-width="220"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span class="font-semibold text-13px">{{ row.name }}</span>
            </template>
          </ElTableColumn>

          <ElTableColumn :label="t('erp.tariffSalaryDollar')" width="160" align="right">
            <template #default="{ row }">
              <span class="font-mono text-14px font-bold text-emerald-600 dark:text-emerald-400">
                ${{ formatMoney(row.amount) }}
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="comment"
            :label="t('erp.izoh')"
            min-width="180"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span class="text-gray-500 dark:text-gray-400 text-13px">{{
                row.comment || '—'
              }}</span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="createTime" :label="t('erp.createdTime')" width="160" align="center">
            <template #default="{ row }">
              <span class="text-12px text-gray-400 font-mono">{{ row.createTime || '—' }}</span>
            </template>
          </ElTableColumn>

          <ElTableColumn :label="t('erp.amallar')" width="160" align="center" fixed="right">
            <template #default="{ row }">
              <div class="flex items-center justify-center gap-6px">
                <ElButton link type="primary" class="!font-bold" @click="openEditDialog(row)">{{
                  t('common.edit')
                }}</ElButton>
                <ElButton link type="danger" class="!font-bold" @click="handleDelete(row)">{{
                  t('common.delete')
                }}</ElButton>
              </div>
            </template>
          </ElTableColumn>
        </ElTable>
      </div>

      <!-- Add / Edit Dialog -->
      <ElDialog
        v-model="dialogVisible"
        :title="
          dialogType === 'add'
            ? `${t('erp.addNewWorkVolume')} (${t('erp.temporaryWorkers')})`
            : t('erp.editWorkVolume')
        "
        width="560px"
        class="custom-output-dialog"
      >
        <ElForm ref="formRef" :model="form" :rules="rules" label-position="top">
          <ElRow :gutter="16">
            <ElCol :span="12">
              <ElFormItem :label="t('erp.workDate')" prop="period_month">
                <ElDatePicker
                  v-model="form.period_month"
                  type="date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  :placeholder="t('erp.selectDate')"
                  style="width: 100%"
                />
              </ElFormItem>
            </ElCol>
            <ElCol :span="12">
              <ElFormItem :label="t('erp.workerCraftsmanName')" prop="workerName">
                <ElSelect
                  v-model="form.workerName"
                  filterable
                  allow-create
                  default-first-option
                  clearable
                  :placeholder="t('erp.workerNamePlaceholder')"
                  style="width: 100%"
                >
                  <ElOption
                    v-for="name in allWorkerSuggestions"
                    :key="name"
                    :label="name"
                    :value="name"
                  />
                </ElSelect>
              </ElFormItem>
            </ElCol>
          </ElRow>

          <ElFormItem :label="t('erp.operationNameLabel')" prop="name">
            <ElInput v-model="form.name" :placeholder="t('erp.operationNamePlaceholder')" />
          </ElFormItem>

          <ElRow :gutter="16">
            <ElCol :span="8">
              <ElFormItem :label="t('erp.completedQtyLabel')">
                <ElInputNumber
                  v-model="formQuantity"
                  :min="1"
                  :step="1"
                  style="width: 100%"
                  @change="calcAmount"
                />
              </ElFormItem>
            </ElCol>
            <ElCol :span="8">
              <ElFormItem :label="t('erp.unitRateLabel')">
                <ElInput
                  :model-value="formUnitRate ? moneyFormatter(formUnitRate) : ''"
                  placeholder="0"
                  @input="
                    (val: string) => {
                      formUnitRate = Number(moneyParser(val)) || 0
                      calcAmount()
                    }
                  "
                >
                  <template #prefix>$</template>
                </ElInput>
              </ElFormItem>
            </ElCol>
            <ElCol :span="8">
              <ElFormItem :label="t('erp.totalPaymentLabel')" prop="amount">
                <ElInput
                  :model-value="form.amount ? moneyFormatter(form.amount) : ''"
                  placeholder="0"
                  @input="
                    (val: string) => {
                      form.amount = Number(moneyParser(val)) || 0
                    }
                  "
                >
                  <template #prefix>$</template>
                </ElInput>
              </ElFormItem>
            </ElCol>
          </ElRow>

          <ElFormItem :label="t('erp.additionalRemarkLabel')" prop="comment">
            <ElInput
              v-model="form.comment"
              type="textarea"
              :rows="3"
              :placeholder="t('erp.additionalRemarkPlaceholder')"
            />
          </ElFormItem>
        </ElForm>

        <template #footer>
          <ElButton @click="dialogVisible = false">{{ t('common.cancel') }}</ElButton>
          <ElButton type="primary" :loading="submitLoading" @click="submitForm">{{
            t('common.save')
          }}</ElButton>
        </template>
      </ElDialog>
    </ContentWrap>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from '@/hooks/web/useI18n'
import { ContentWrap } from '@/components/ContentWrap'
import { Icon } from '@/components/Icon'
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
  ElInputNumber,
  ElDatePicker,
  ElInput,
  ElRow,
  ElCol
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getOutputListApi, saveOutputApi, deleteOutputApi } from '@/api/staff_hr'
import { getWorkerListApi } from '@/api/worker'
import { moneyFormatter, moneyParser } from '@/utils'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const { t } = useI18n()

const loading = ref(false)
const tableData = ref<any[]>([])
const workers = ref<any[]>([])
const selectedIds = ref<string[]>([])

useRealtimeSync(['staff_hr', 'staff_output', 'output', 'worker'], () => {
  getList()
  getWorkers()
})

// Filter States
const filterDateRange = ref<any>(null)
const filterWorkerName = ref('')
const searchKeyword = ref('')

const formatMoney = (val: number | string | null | undefined, decimals = 0) => {
  if (val === undefined || val === null || val === '') return '0'
  const num = typeof val === 'string' ? parseFloat(val) : val
  if (isNaN(num)) return '0'
  const hasDecimals = Math.abs(num % 1) > 0.001
  const decCount = decimals > 0 ? decimals : hasDecimals ? 2 : 0
  const parts = num.toFixed(decCount).split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  return parts.join('.')
}

const formatWorkDate = (row: any) => {
  if (!row) return '—'
  if (row.period_month) {
    return row.period_month
  }
  if (row.createTime) {
    return row.createTime.split(' ')[0]
  }
  return '—'
}

const getList = async () => {
  loading.value = true
  try {
    const res = await getOutputListApi()
    if (res && (res.code === 0 || res.data)) {
      const rawList = res.data?.list || res.data || []
      tableData.value = rawList.map((item: any) => {
        const name =
          item.workerName && item.workerName !== 'Unknown Worker'
            ? item.workerName
            : item.workerId || 'Vaqtinchalik Ishchi'
        return {
          ...item,
          workerName: name
        }
      })
    }
  } catch (err: any) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const getWorkers = async () => {
  try {
    const res = await getWorkerListApi({ pageIndex: 1, pageSize: 100 })
    if (res && (res.code === 0 || res.data)) {
      workers.value = res.data?.list || res.data || []
    }
  } catch (err) {
    console.error(err)
  }
}

// All suggestion names combining registered employees and previous temporary workers
const allWorkerSuggestions = computed(() => {
  const names = new Set<string>()
  workers.value.forEach((w) => {
    if (w.name) names.add(w.name)
  })
  tableData.value.forEach((t) => {
    const name = t.workerName || t.workerId
    if (name && name !== 'Unknown Worker') names.add(name)
  })
  return Array.from(names)
})

const filteredData = computed(() => {
  return tableData.value.filter((item) => {
    // 1. Date Range
    if (filterDateRange.value && filterDateRange.value[0] && filterDateRange.value[1]) {
      const itemDate = formatWorkDate(item)
      if (itemDate < filterDateRange.value[0] || itemDate > filterDateRange.value[1]) {
        return false
      }
    }
    // 2. Worker Name
    if (filterWorkerName.value) {
      const currentName = item.workerName || item.workerId || ''
      if (currentName !== filterWorkerName.value) {
        return false
      }
    }
    // 3. Search Keyword
    if (searchKeyword.value.trim()) {
      const kw = searchKeyword.value.toLowerCase().trim()
      const inName = (item.name || '').toLowerCase().includes(kw)
      const inWorker = (item.workerName || item.workerId || '').toLowerCase().includes(kw)
      const inComment = (item.comment || '').toLowerCase().includes(kw)
      if (!inName && !inWorker && !inComment) return false
    }
    return true
  })
})

const totalPayoutAmount = computed(() => {
  return filteredData.value.reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0)
})

const uniqueWorkersCount = computed(() => {
  const set = new Set(filteredData.value.map((i) => i.workerName || i.workerId))
  return set.size
})

const avgPayoutPerTask = computed(() => {
  if (filteredData.value.length === 0) return 0
  return totalPayoutAmount.value / filteredData.value.length
})

const resetFilters = () => {
  filterDateRange.value = null
  filterWorkerName.value = ''
  searchKeyword.value = ''
}

const handleSelectionChange = (selection: any[]) => {
  selectedIds.value = selection.map((item) => item.id)
}

// Dialog Logic
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const formQuantity = ref(1)
const formUnitRate = ref(0)

const form = reactive({
  id: '',
  workerId: '',
  workerName: '',
  name: '',
  amount: 0,
  period_month: '',
  comment: ''
})

const calcAmount = () => {
  if (formQuantity.value && formUnitRate.value) {
    form.amount = parseFloat((formQuantity.value * formUnitRate.value).toFixed(2))
  }
}

const rules = reactive<FormRules>({
  workerName: [
    { required: true, message: 'Iltimos, ishchi ismini kiriting yoki tanlang', trigger: 'blur' }
  ],
  name: [{ required: true, message: 'Iltimos, ish nomini kiriting', trigger: 'blur' }],
  amount: [{ required: true, message: 'Iltimos, to‘lov summasini kiriting', trigger: 'blur' }]
})

const openAddDialog = () => {
  dialogType.value = 'add'
  form.id = ''
  form.workerId = ''
  form.workerName = ''
  form.name = ''
  form.amount = 0
  form.period_month = new Date().toISOString().split('T')[0]
  form.comment = ''
  formQuantity.value = 1
  formUnitRate.value = 0
  dialogVisible.value = true
}

const openEditDialog = (row: any) => {
  dialogType.value = 'edit'
  form.id = row.id
  form.workerName = row.workerName || row.workerId || ''
  form.workerId = row.workerId || row.workerName || ''
  form.name = row.name
  form.amount = row.amount
  form.period_month =
    row.period_month ||
    (row.createTime ? row.createTime.split(' ')[0] : new Date().toISOString().split('T')[0])
  form.comment = row.comment || ''
  formQuantity.value = 1
  formUnitRate.value = row.amount || 0
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const payload = {
          ...form,
          workerId: form.workerName,
          workerName: form.workerName
        }
        const res = await saveOutputApi(payload)
        if (res && (res.code === 0 || res.data)) {
          ElMessage.success('Ish hajmi muvaffaqiyatli saqlandi')
          dialogVisible.value = false
          getList()
        }
      } catch (err: any) {
        ElMessage.error(err.message || 'Saqlashda xatolik yuz berdi')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm("Ushbu yozuvni o'chirishni tasdiqlaysizmi?", 'Eslatma', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'warning'
  })
    .then(async () => {
      const res = await deleteOutputApi({ ids: [row.id] })
      if (res && (res.code === 0 || res.data)) {
        ElMessage.success("Yozuv o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return
  ElMessageBox.confirm(
    `Tanlangan ${selectedIds.value.length} ta yozuvni o'chirishni tasdiqlaysizmi?`,
    'Eslatma',
    {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(async () => {
      const res = await deleteOutputApi({ ids: selectedIds.value })
      if (res && (res.code === 0 || res.data)) {
        ElMessage.success("Tanlangan yozuvlar o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

onMounted(() => {
  getList()
  getWorkers()
})
</script>

<style scoped lang="less">
.output-container {
  padding-bottom: 20px;
}

.stat-card {
  background: var(--el-bg-color-overlay, #ffffff);
  border-radius: 14px;
  padding: 16px 20px;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  }

  &.border-blue {
    border-left: 4px solid #3b82f6;
  }
  &.border-emerald {
    border-left: 4px solid #10b981;
  }
  &.border-amber {
    border-left: 4px solid #f59e0b;
  }
  &.border-purple {
    border-left: 4px solid #8b5cf6;
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--el-text-color-secondary, #94a3b8);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .stat-number {
    font-size: 22px;
    font-weight: 800;
    margin-top: 4px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;

    &.text-blue {
      color: #2563eb;
    }
    &.text-emerald {
      color: #059669;
    }
    &.text-amber {
      color: #d97706;
    }
    &.text-purple {
      color: #7c3aed;
    }
  }

  .stat-unit {
    font-size: 13px;
    font-weight: 500;
    color: #64748b;
  }

  .stat-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

    &.bg-blue-gradient {
      background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    }
    &.bg-emerald-gradient {
      background: linear-gradient(135deg, #10b981, #047857);
    }
    &.bg-amber-gradient {
      background: linear-gradient(135deg, #f59e0b, #b45309);
    }
    &.bg-purple-gradient {
      background: linear-gradient(135deg, #8b5cf6, #6d28d9);
    }
  }
}

:global(.dark) .stat-card {
  background: #0f172a;
  border-color: #1e293b;

  .stat-number {
    &.text-blue {
      color: #60a5fa;
    }
    &.text-emerald {
      color: #34d399;
    }
    &.text-amber {
      color: #fbbf24;
    }
    &.text-purple {
      color: #a78bfa;
    }
  }
}
</style>
