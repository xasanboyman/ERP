<template>
  <ContentWrap>
    <el-tabs v-model="activeTab">
      <!-- Technical Stages Tab -->
      <el-tab-pane label="Texnologik etaplar" name="stages">
        <div class="mb-20px flex justify-between items-center">
          <el-button type="primary" @click="openStageDialog('add')">Yangi etap</el-button>
          <el-button
            type="danger"
            :disabled="selectedStageIds.length === 0"
            @click="handleBatchDeleteStages"
            >Guruhli o'chirish</el-button
          >
        </div>

        <el-table
          v-loading="loadingStages"
          :data="stagesData"
          style="width: 100%"
          @selection-change="handleStageSelection"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="ID" width="120" />
          <el-table-column prop="name" :label="t('erp.stageName')" min-width="200" />
          <el-table-column prop="price" label="Etap narxi ($)" width="150">
            <template #default="scope">
              <span class="font-mono">{{ formatMoney(scope.row.price) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="Davomiyligi (sekund)" width="180" />
          <el-table-column prop="is_system" label="Tizimniki" width="120">
            <template #default="scope">
              <el-tag :type="scope.row.is_system === 1 ? 'info' : 'success'">
                {{ scope.row.is_system === 1 ? 'Tizim' : 'Maxsus' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('erp.amallar')" width="180" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="openStageDialog('edit', scope.row)">{{
                t('common.edit')
              }}</el-button>
              <el-button link type="danger" @click="handleDeleteStage(scope.row)">{{
                t('common.delete')
              }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Technical Processes Tab -->
      <el-tab-pane label="Texnologik jarayonlar (Tehprocesslar)" name="processes">
        <div class="mb-20px flex justify-between items-center">
          <el-button type="primary" @click="openProcessDialog('add')">Yangi jarayon</el-button>
          <el-button
            type="danger"
            :disabled="selectedProcessIds.length === 0"
            @click="handleBatchDeleteProcesses"
            >Guruhli o'chirish</el-button
          >
        </div>

        <el-table
          v-loading="loadingProcesses"
          :data="processesData"
          style="width: 100%"
          @selection-change="handleProcessSelection"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="ID" width="120" />
          <el-table-column prop="name" :label="t('erp.processName')" min-width="200" />
          <el-table-column prop="stages" label="Etaplar soni" width="150">
            <template #default="scope">
              {{ scope.row.stages ? scope.row.stages.length : 0 }} ta etap
            </template>
          </el-table-column>
          <el-table-column
            prop="remark"
            :label="t('erp.izoh')"
            show-overflow-tooltip
            min-width="200"
          />
          <el-table-column :label="t('erp.amallar')" width="180" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="openProcessDialog('edit', scope.row)">{{
                t('common.edit')
              }}</el-button>
              <el-button link type="danger" @click="handleDeleteProcess(scope.row)">{{
                t('common.delete')
              }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Stage Form Dialog -->
    <el-dialog
      v-model="stageDialogVisible"
      :title="stageDialogType === 'add' ? t('erp.addNewStage') : t('erp.editStage')"
      width="500px"
    >
      <el-form ref="stageFormRef" :model="stageForm" :rules="stageRules" label-width="120px">
        <el-form-item :label="t('erp.stageName')" prop="name">
          <el-input v-model="stageForm.name" placeholder="Masalan: Laying, Pattern cutting" />
        </el-form-item>
        <el-form-item label="Narxi ($)" prop="price">
          <el-input
            :model-value="stageForm.price ? moneyFormatter(stageForm.price) : ''"
            placeholder="0"
            @input="
              (val: string) => {
                stageForm.price = Number(moneyParser(val)) || 0
              }
            "
          >
            <template #prefix>$</template>
          </el-input>
        </el-form-item>
        <el-form-item label="Davomiyligi (s)" prop="duration">
          <el-input-number v-model="stageForm.duration" :min="0" :step="10" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Tizimniki" prop="is_system">
          <el-radio-group v-model="stageForm.is_system">
            <el-radio :value="1">Ha</el-radio>
            <el-radio :value="0">Yo'q (Maxsus)</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stageDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitStageLoading" @click="submitStageForm">{{
          t('common.confirm')
        }}</el-button>
      </template>
    </el-dialog>

    <!-- Process Form Dialog -->
    <el-dialog
      v-model="processDialogVisible"
      :title="processDialogType === 'add' ? t('erp.addNewProcess') : t('erp.editProcess')"
      width="650px"
    >
      <el-form ref="processFormRef" :model="processForm" :rules="processRules" label-width="120px">
        <el-form-item :label="t('erp.processName')" prop="name">
          <el-input
            v-model="processForm.name"
            placeholder="Masalan: Premium T-shirt cutting workflow"
          />
        </el-form-item>
        <el-form-item :label="t('erp.izoh')" prop="remark">
          <el-input
            v-model="processForm.remark"
            type="textarea"
            placeholder="Jarayon haqida qo'shimcha ma'lumot"
          />
        </el-form-item>
        <el-form-item label="Etaplar tartibi">
          <div class="w-full">
            <el-checkbox-group v-model="selectedStageIdsInProcess" class="flex flex-col gap-2">
              <el-checkbox v-for="s in stagesData" :key="s.id" :value="s.id">
                {{ s.name }} ({{ formatMoney(s.price) }} $)
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="processDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitProcessLoading" @click="submitProcessForm">{{
          t('common.confirm')
        }}</el-button>
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
  ElTabs,
  ElTabPane,
  ElButton,
  ElTable,
  ElTableColumn,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElDialog,
  ElCheckbox,
  ElCheckboxGroup,
  ElRadio,
  ElRadioGroup,
  ElTag
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getStageListApi,
  saveStageApi,
  deleteStageApi,
  getProcessListApi,
  saveProcessApi,
  deleteProcessApi
} from '@/api/cutting'
import { formatMoney, moneyFormatter, moneyParser } from '@/utils'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const activeTab = ref('stages')

// ---------------- Stages Logic ----------------
const loadingStages = ref(false)
const stagesData = ref<any[]>([])
const selectedStageIds = ref<string[]>([])
const stageDialogVisible = ref(false)

useRealtimeSync(['cutting', 'cutting_order', 'cutting_task', 'product'], () => {
  getStages()
  getProcesses()
})
const stageDialogType = ref<'add' | 'edit'>('add')
const submitStageLoading = ref(false)
const stageFormRef = ref<FormInstance>()

const stageForm = reactive({
  id: '',
  name: '',
  price: 0,
  duration: 0,
  is_system: 0
})

const stageRules = reactive<FormRules>({
  name: [{ required: true, message: 'Iltimos, etap nomini kiriting', trigger: 'blur' }]
})

const getStages = async () => {
  loadingStages.value = true
  try {
    const res = await getStageListApi()
    if (res && res.code === 0) {
      stagesData.value = res.data.list || []
    }
  } catch (err) {
    console.error(err)
  } finally {
    loadingStages.value = false
  }
}

const handleStageSelection = (selection: any[]) => {
  selectedStageIds.value = selection.map((item) => item.id)
}

const openStageDialog = (type: 'add' | 'edit', row?: any) => {
  stageDialogType.value = type
  stageDialogVisible.value = true
  if (type === 'edit' && row) {
    stageForm.id = row.id
    stageForm.name = row.name
    stageForm.price = row.price
    stageForm.duration = row.duration
    stageForm.is_system = row.is_system
  } else {
    stageForm.id = ''
    stageForm.name = ''
    stageForm.price = 0
    stageForm.duration = 0
    stageForm.is_system = 0
  }
}

const submitStageForm = async () => {
  if (!stageFormRef.value) return
  await stageFormRef.value.validate(async (valid) => {
    if (valid) {
      submitStageLoading.value = true
      try {
        const res = await saveStageApi(stageForm)
        if (res && res.code === 0) {
          ElMessage.success('Etap muvaffaqiyatli saqlandi')
          stageDialogVisible.value = false
          getStages()
        }
      } catch (err) {
        console.error(err)
      } finally {
        submitStageLoading.value = false
      }
    }
  })
}

const handleDeleteStage = (row: any) => {
  ElMessageBox.confirm("Ushbu etapni o'chirishni tasdiqlaysizmi?", 'Eslatma', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'warning'
  })
    .then(async () => {
      const res = await deleteStageApi({ ids: [row.id] })
      if (res && res.code === 0) {
        ElMessage.success("Etap o'chirildi")
        getStages()
      }
    })
    .catch(() => {})
}

const handleBatchDeleteStages = () => {
  if (selectedStageIds.value.length === 0) return
  ElMessageBox.confirm(
    `Tanlangan ${selectedStageIds.value.length} ta etapni o'chirishni tasdiqlaysizmi?`,
    'Eslatma',
    {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(async () => {
      const res = await deleteStageApi({ ids: selectedStageIds.value })
      if (res && res.code === 0) {
        ElMessage.success("Tanlangan etaplar o'chirildi")
        getStages()
      }
    })
    .catch(() => {})
}

// ---------------- Processes Logic ----------------
const loadingProcesses = ref(false)
const processesData = ref<any[]>([])
const selectedProcessIds = ref<string[]>([])
const processDialogVisible = ref(false)
const processDialogType = ref<'add' | 'edit'>('add')
const submitProcessLoading = ref(false)
const processFormRef = ref<FormInstance>()
const selectedStageIdsInProcess = ref<string[]>([])

const processForm = reactive({
  id: '',
  name: '',
  remark: ''
})

const processRules = reactive<FormRules>({
  name: [{ required: true, message: 'Iltimos, jarayon nomini kiriting', trigger: 'blur' }]
})

const getProcesses = async () => {
  loadingProcesses.value = true
  try {
    const res = await getProcessListApi()
    if (res && res.code === 0) {
      processesData.value = res.data.list || []
    }
  } catch (err) {
    console.error(err)
  } finally {
    loadingProcesses.value = false
  }
}

const handleProcessSelection = (selection: any[]) => {
  selectedProcessIds.value = selection.map((item) => item.id)
}

const openProcessDialog = (type: 'add' | 'edit', row?: any) => {
  processDialogType.value = type
  processDialogVisible.value = true
  selectedStageIdsInProcess.value = []
  if (type === 'edit' && row) {
    processForm.id = row.id
    processForm.name = row.name
    processForm.remark = row.remark || ''
    if (row.stages) {
      selectedStageIdsInProcess.value = row.stages.map((st: any) => st.id || st)
    }
  } else {
    processForm.id = ''
    processForm.name = ''
    processForm.remark = ''
  }
}

const submitProcessForm = async () => {
  if (!processFormRef.value) return
  await processFormRef.value.validate(async (valid) => {
    if (valid) {
      submitProcessLoading.value = true
      // Map stage IDs to complete objects
      const stagesList = selectedStageIdsInProcess.value.map((id) => {
        const found = stagesData.value.find((s) => s.id === id)
        return found
          ? { id: found.id, name: found.name, price: found.price, duration: found.duration }
          : { id }
      })
      try {
        const res = await saveProcessApi({
          ...processForm,
          stages: stagesList
        })
        if (res && res.code === 0) {
          ElMessage.success('Jarayon muvaffaqiyatli saqlandi')
          processDialogVisible.value = false
          getProcesses()
        }
      } catch (err) {
        console.error(err)
      } finally {
        submitProcessLoading.value = false
      }
    }
  })
}

const handleDeleteProcess = (row: any) => {
  ElMessageBox.confirm("Ushbu jarayonni o'chirishni tasdiqlaysizmi?", 'Eslatma', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'warning'
  })
    .then(async () => {
      const res = await deleteProcessApi({ ids: [row.id] })
      if (res && res.code === 0) {
        ElMessage.success("Jarayon o'chirildi")
        getProcesses()
      }
    })
    .catch(() => {})
}

const handleBatchDeleteProcesses = () => {
  if (selectedProcessIds.value.length === 0) return
  ElMessageBox.confirm(
    `Tanlangan ${selectedProcessIds.value.length} ta jarayonni o'chirishni tasdiqlaysizmi?`,
    'Eslatma',
    {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(async () => {
      const res = await deleteProcessApi({ ids: selectedProcessIds.value })
      if (res && res.code === 0) {
        ElMessage.success("Tanlangan jarayonlar o'chirildi")
        getProcesses()
      }
    })
    .catch(() => {})
}

onMounted(() => {
  getStages()
  getProcesses()
})
</script>

<style scoped>
.mb-20px {
  margin-bottom: 20px;
}
.flex {
  display: flex;
}
.flex-col {
  flex-direction: column;
}
.gap-2 {
  gap: 8px;
}
</style>
