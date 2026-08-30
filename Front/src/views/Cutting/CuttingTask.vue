<template>
  <ContentWrap>
    <el-tabs v-model="activeTab">
      <!-- Tasks Tab -->
      <el-tab-pane label="Ishlab chiqarish vazifalari" name="tasks">
        <div class="mb-20px flex justify-between items-center">
          <div class="text-slate-500 text-sm"
            >QR-kodli yorliqlar orqali yoki qo'lda bajarilgan ishlarni ro'yxatdan o'tkazing</div
          >
        </div>

        <el-table
          v-loading="loadingTasks"
          :data="tasksData"
          style="width: 100%"
          table-layout="auto"
        >
          <el-table-column prop="id" label="Vazifa ID" min-width="200" show-overflow-tooltip />
          <el-table-column prop="order_number_snapshot" label="Buyurtma #" min-width="120" />
          <el-table-column
            prop="product_name_snapshot"
            label="Mahsulot"
            min-width="180"
            show-overflow-tooltip
          />
          <el-table-column prop="stage_name_snapshot" label="Etap (Operatsiya)" min-width="150" />
          <el-table-column
            prop="quantity"
            label="Kutilayotgan miqdor"
            min-width="140"
            align="center"
          />
          <el-table-column prop="status" :label="t('erp.holati')" min-width="130" align="center">
            <template #default="scope">
              <el-tag
                :type="
                  scope.row.status === 'completed'
                    ? 'success'
                    : scope.row.status === 'in_progress'
                      ? 'warning'
                      : 'info'
                "
              >
                {{
                  scope.row.status === 'completed'
                    ? 'Bajarildi'
                    : scope.row.status === 'in_progress'
                      ? 'Bajarilmoqda'
                      : 'Yaratilgan'
                }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('erp.amallar')" min-width="280" fixed="right">
            <template #default="scope">
              <div class="flex gap-2 flex-nowrap">
                <el-button
                  link
                  type="primary"
                  :disabled="scope.row.status === 'completed'"
                  @click="openLogDialog(scope.row)"
                >
                  Bajarishni kiritish
                </el-button>
                <el-button
                  link
                  type="success"
                  :disabled="scope.row.status === 'completed'"
                  @click="handleCompleteTask(scope.row)"
                >
                  Bajarildi deb belgilash
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Executions Tab -->
      <el-tab-pane label="Bajarilgan ishlar jurnali" name="executions">
        <el-table
          v-loading="loadingExecutions"
          :data="executionsData"
          style="width: 100%"
          table-layout="auto"
        >
          <el-table-column prop="id" label="Log ID" min-width="120" show-overflow-tooltip />
          <el-table-column prop="task_details.order_number" label="Buyurtma #" min-width="120" />
          <el-table-column
            prop="task_details.product_name"
            label="Mahsulot"
            min-width="180"
            show-overflow-tooltip
          />
          <el-table-column prop="task_details.stage_name" label="Etap" min-width="130" />
          <el-table-column prop="workerName" label="Xodim (Usta)" min-width="140" />
          <el-table-column
            prop="quantity"
            label="Bajarilgan miqdor"
            min-width="140"
            align="center"
          />
          <el-table-column prop="period_month" label="Hisobot oyi" min-width="120" align="center" />
          <el-table-column
            prop="comment"
            :label="t('erp.izoh')"
            show-overflow-tooltip
            min-width="150"
          />
          <el-table-column prop="createTime" label="Kiritilgan vaqt" min-width="160" />
          <el-table-column :label="t('erp.amallar')" min-width="110" fixed="right">
            <template #default="scope">
              <el-button link type="danger" @click="handleDeleteExecution(scope.row)">{{
                t('common.delete')
              }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Log Execution Dialog -->
    <el-dialog v-model="logDialogVisible" title="Bajarilgan ish hajmini kiritish" width="500px">
      <el-form ref="logFormRef" :model="logForm" :rules="logRules" label-width="120px">
        <el-form-item label="Vazifa">
          <el-input :value="selectedTaskInfo" disabled />
        </el-form-item>
        <el-form-item label="Xodim (Usta)" prop="workerId">
          <el-select v-model="logForm.workerId" placeholder="Xodimni tanlang" style="width: 100%">
            <el-option v-for="w in workers" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Soni (dona)" prop="quantity">
          <el-input-number v-model="logForm.quantity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Hisobot oyi" prop="period_month">
          <el-date-picker
            v-model="logForm.period_month"
            type="month"
            value-format="YYYY-MM"
            placeholder="Oy tanlang"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('erp.izoh')" prop="comment">
          <el-input
            v-model="logForm.comment"
            type="textarea"
            placeholder="Izoh yozishingiz mumkin"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="logDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitLogLoading" @click="submitLogForm">{{
          t('common.confirm')
        }}</el-button>
      </template>
    </el-dialog>
  </ContentWrap>
</template>

<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
import { ref, reactive, onMounted, computed } from 'vue'
import { ContentWrap } from '@/components/ContentWrap'
import {
  ElMessage,
  ElMessageBox,
  ElTabs,
  ElTabPane,
  ElTable,
  ElTableColumn,
  ElTag,
  ElButton,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElDatePicker
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getTaskListApi,
  updateTaskStatusApi,
  getExecutionListApi,
  saveExecutionApi,
  deleteExecutionApi
} from '@/api/cutting'
import { getWorkerListApi } from '@/api/worker'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const activeTab = ref('tasks')

const loadingTasks = ref(false)
const tasksData = ref<any[]>([])
const loadingExecutions = ref(false)
const executionsData = ref<any[]>([])
const workers = ref<any[]>([])

useRealtimeSync(['cutting', 'cutting_order', 'cutting_task', 'worker'], () => {
  getTasks()
  getExecutions()
  getWorkers()
})

const logDialogVisible = ref(false)
const submitLogLoading = ref(false)
const logFormRef = ref<FormInstance>()
const selectedTask = ref<any>(null)

const logForm = reactive({
  taskId: '',
  workerId: '',
  quantity: 1,
  period_month: '',
  comment: ''
})

const logRules = reactive<FormRules>({
  workerId: [{ required: true, message: 'Iltimos, xodimni tanlang', trigger: 'change' }],
  quantity: [{ required: true, message: 'Iltimos, miqdorni kiriting', trigger: 'blur' }]
})

const selectedTaskInfo = computed(() => {
  if (!selectedTask.value) return ''
  return `${selectedTask.value.order_number_snapshot} — ${selectedTask.value.stage_name_snapshot}`
})

const getTasks = async () => {
  loadingTasks.value = true
  try {
    const res = await getTaskListApi()
    if (res && res.code === 0) {
      tasksData.value = res.data.list || []
    }
  } catch (err) {
    console.error(err)
  } finally {
    loadingTasks.value = false
  }
}

const getExecutions = async () => {
  loadingExecutions.value = true
  try {
    const res = await getExecutionListApi()
    if (res && res.code === 0) {
      executionsData.value = res.data.list || []
    }
  } catch (err) {
    console.error(err)
  } finally {
    loadingExecutions.value = false
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

const handleCompleteTask = (row: any) => {
  ElMessageBox.confirm("Ushbu vazifani to'liq yakunlangan deb belgilaysizmi?", 'Tasdiqlash', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'success'
  })
    .then(async () => {
      const res = await updateTaskStatusApi({ taskId: row.id, status: 'completed' })
      if (res && res.code === 0) {
        ElMessage.success('Vazifa yakunlandi')
        getTasks()
      }
    })
    .catch(() => {})
}

const openLogDialog = (row: any) => {
  selectedTask.value = row
  logForm.taskId = row.id
  logForm.workerId = ''
  logForm.quantity = row.quantity
  logForm.period_month = new Date().toISOString().split('T')[0].substring(0, 7)
  logForm.comment = ''
  logDialogVisible.value = true
}

const submitLogForm = async () => {
  if (!logFormRef.value) return
  await logFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLogLoading.value = true
      try {
        const res = await saveExecutionApi(logForm)
        if (res && res.code === 0) {
          ElMessage.success('Bajarilgan ish muvaffaqiyatli saqlandi')
          logDialogVisible.value = false
          getTasks()
          getExecutions()
        }
      } catch (err) {
        console.error(err)
      } finally {
        submitLogLoading.value = false
      }
    }
  })
}

const handleDeleteExecution = (row: any) => {
  ElMessageBox.confirm("Ushbu yozuvni o'chirishni tasdiqlaysizmi?", 'Eslatma', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'warning'
  })
    .then(async () => {
      const res = await deleteExecutionApi({ ids: [row.id] })
      if (res && res.code === 0) {
        ElMessage.success("Yozuv o'chirildi")
        getExecutions()
        getTasks()
      }
    })
    .catch(() => {})
}

onMounted(() => {
  getTasks()
  getExecutions()
  getWorkers()
})
</script>

<style scoped>
.mb-20px {
  margin-bottom: 20px;
}
</style>
