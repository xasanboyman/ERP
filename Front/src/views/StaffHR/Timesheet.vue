<template>
  <ContentWrap>
    <div class="mb-20px flex justify-between items-center">
      <el-button type="primary" @click="openAddDialog">{{ t('erp.newTimesheetBtn') }}</el-button>
    </div>

    <!-- Table -->
    <el-table v-loading="loading" :data="tableData" style="width: 100%">
      <el-table-column type="expand">
        <template #default="props">
          <div class="p-4 bg-slate-50/50 rounded-lg border border-slate-100">
            <h3 class="font-bold mb-2">Xodimlar davomati:</h3>
            <el-table :data="props.row.records" size="small" border>
              <el-table-column prop="workerName" label="Ismi" min-width="150" />
              <el-table-column prop="status" label="Ishtiroki" width="150">
                <template #default="scope">
                  <el-tag :type="getAttendanceTagType(scope.row.status)">
                    {{ getAttendanceLabel(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="hours" label="Ish soati" width="120" align="center" />
            </el-table>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="date" :label="t('erp.timesheetDate')" width="150" />
      <el-table-column
        prop="records.length"
        :label="t('erp.workerCount')"
        width="150"
        align="center"
      >
        <template #default="scope">
          {{ scope.row.records ? scope.row.records.length : 0 }} nafar
        </template>
      </el-table-column>
      <el-table-column prop="status" :label="t('erp.timesheetStatus')" width="150" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'archived' ? 'info' : 'success'">
            {{ scope.row.status === 'archived' ? 'Arxivlangan' : 'Faol' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" :label="t('erp.createdTime')" min-width="180" />
      <el-table-column :label="t('erp.amallar')" width="180" fixed="right">
        <template #default="scope">
          <el-button
            link
            type="primary"
            :disabled="scope.row.status === 'archived'"
            @click="openEditDialog(scope.row)"
            >{{ t('common.edit') }}</el-button
          >
          <el-button link type="danger" @click="handleDelete(scope.row)">{{
            t('common.delete')
          }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? 'Yangi tabel kiritish' : 'Tabelni tahrirlash'"
      width="750px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <div class="grid grid-cols-2 gap-4">
          <el-form-item :label="t('erp.timesheetDate')" prop="date">
            <el-date-picker
              v-model="form.date"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="Sana tanlang"
              style="width: 100%"
              :disabled="dialogType === 'edit'"
            />
          </el-form-item>
          <el-form-item :label="t('erp.holati')" prop="status">
            <el-radio-group v-model="form.status">
              <el-radio value="active">{{ t('erp.faol') }}</el-radio>
              <el-radio value="archived">Arxivlash</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>

        <el-divider>Xodimlar ro'yxati va davomati</el-divider>

        <el-table :data="form.records" size="small" style="width: 100%" max-height="300">
          <el-table-column prop="workerName" label="Ismi" />
          <el-table-column label="Davomati" width="200">
            <template #default="scope">
              <el-select v-model="scope.row.status" placeholder="Tanlang" size="small">
                <el-option label="Keldi (Present)" value="present" />
                <el-option label="Kelmagan (Absent)" value="absent" />
                <el-option label="Kasal (Sick)" value="sick" />
                <el-option label="Ta'til (Leave)" value="leave" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="Ish soati" width="180">
            <template #default="scope">
              <el-input-number
                v-model="scope.row.hours"
                :min="0"
                :max="24"
                :step="1"
                size="small"
                style="width: 100%"
              />
            </template>
          </el-table-column>
        </el-table>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">{{
          t('common.save')
        }}</el-button>
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
  ElDatePicker,
  ElRadioGroup,
  ElRadio,
  ElDivider,
  ElSelect,
  ElOption,
  ElInputNumber
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getTimesheetListApi, saveTimesheetApi, deleteTimesheetApi } from '@/api/staff_hr'
import { getWorkerListApi } from '@/api/worker'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const { t } = useI18n()

const loading = ref(false)
const tableData = ref<any[]>([])
const workers = ref<any[]>([])

useRealtimeSync(['staff_hr', 'staff_timesheet', 'timesheet', 'worker'], () => {
  getList()
  getWorkers()
})

const getList = async () => {
  loading.value = true
  try {
    const res = await getTimesheetListApi()
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

// Dialog Logic
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  id: '',
  date: '',
  status: 'active',
  records: [] as any[]
})

const rules = reactive<FormRules>({
  date: [{ required: true, message: 'Iltimos, tabel sanasini tanlang', trigger: 'blur' }]
})

const openAddDialog = () => {
  dialogType.value = 'add'
  form.id = ''
  form.date = new Date().toISOString().split('T')[0]
  form.status = 'active'
  form.records = workers.value.map((w) => ({
    workerId: w.id,
    workerName: w.name,
    status: 'present',
    hours: 8
  }))
  dialogVisible.value = true
}

const openEditDialog = (row: any) => {
  dialogType.value = 'edit'
  form.id = row.id
  form.date = row.date
  form.status = row.status
  form.records = JSON.parse(JSON.stringify(row.records))
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const res = await saveTimesheetApi(form)
        if (res && res.code === 0) {
          ElMessage.success('Tabel muvaffaqiyatli saqlandi')
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
  ElMessageBox.confirm("Ushbu tabelni o'chirishni tasdiqlaysizmi?", 'Eslatma', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'warning'
  })
    .then(async () => {
      const res = await deleteTimesheetApi({ ids: [row.id] })
      if (res && res.code === 0) {
        ElMessage.success("Tabel o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

// Helpers
const getAttendanceLabel = (status: string) => {
  const map: Record<string, string> = {
    present: 'Keldi',
    absent: 'Kelmagan',
    sick: 'Kasal',
    leave: "Ta'tilda"
  }
  return map[status] || status
}

const getAttendanceTagType = (
  status: string
): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
  const map: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
    present: 'success',
    absent: 'danger',
    sick: 'warning',
    leave: 'info'
  }
  return map[status] || 'info'
}

onMounted(() => {
  getList()
  getWorkers()
})
</script>

<style scoped>
.mb-20px {
  margin-bottom: 20px;
}
.grid {
  display: grid;
}
.grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.gap-4 {
  gap: 16px;
}
.p-4 {
  padding: 16px;
}
</style>
