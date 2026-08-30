<template>
  <ContentWrap>
    <div class="mb-20px flex justify-between items-center">
      <el-button type="primary" @click="openAddDialog">Yangi lavozim</el-button>
      <el-button type="danger" :disabled="selectedIds.length === 0" @click="handleBatchDelete"
        >Guruhli o'chirish</el-button
      >
    </div>

    <!-- Table -->
    <el-table
      v-loading="loading"
      :data="tableData"
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="120" />
      <el-table-column prop="positionName" label="Lavozim nomi" min-width="180" />
      <el-table-column prop="departmentName" :label="t('erp.department')" width="180" />
      <el-table-column prop="baseSalary" label="Tarif stavkasi (Asosiy oylik) ($)" width="220">
        <template #default="scope">
          <span class="font-mono">{{ formatMoney(scope.row.baseSalary) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" :label="t('erp.holati')" width="120" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
            {{ scope.row.status === 1 ? 'Faol' : 'Nofaol' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" :label="t('erp.izoh')" show-overflow-tooltip min-width="180" />
      <el-table-column :label="t('erp.amallar')" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openEditDialog(scope.row)">{{
            t('common.edit')
          }}</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">{{
            t('common.delete')
          }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? 'Yangi lavozim kiritish' : 'Lavozimni tahrirlash'"
      width="500px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="Lavozim nomi" prop="positionName">
          <el-input v-model="form.positionName" placeholder="Masalan: Tikuvchi, Dizayner" />
        </el-form-item>
        <el-form-item :label="t('erp.department')" prop="departmentId">
          <el-select v-model="form.departmentId" placeholder="Bo'limni tanlang" style="width: 100%">
            <el-option
              v-for="d in departments"
              :key="d.id"
              :label="d.departmentName"
              :value="d.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Tarif ($)" prop="baseSalary">
          <el-input
            :model-value="form.baseSalary ? moneyFormatter(form.baseSalary) : ''"
            placeholder="0"
            @input="
              (val: string) => {
                form.baseSalary = Number(moneyParser(val)) || 0
              }
            "
          >
            <template #prefix>$</template>
          </el-input>
        </el-form-item>
        <el-form-item :label="t('erp.holati')" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">{{ t('erp.faol') }}</el-radio>
            <el-radio :value="0">{{ t('erp.nofaol') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('erp.izoh')" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="Lavozim haqida qo'shimcha ma'lumotlar"
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
  ElTag,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElRadioGroup,
  ElRadio
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getPositionListApi, savePositionApi, deletePositionApi } from '@/api/staff_hr'
import { getDepartmentApi } from '@/api/department'
import { formatMoney, moneyFormatter, moneyParser } from '@/utils'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

interface DeptItem {
  id: string
  departmentName: string
}

const loading = ref(false)
const tableData = ref<any[]>([])
const departments = ref<DeptItem[]>([])
const selectedIds = ref<string[]>([])

useRealtimeSync(['staff_hr', 'position', 'department'], () => {
  getList()
  getDepartments()
})

const getList = async () => {
  loading.value = true
  try {
    const res = await getPositionListApi()
    if (res && res.code === 0) {
      tableData.value = res.data.list || []
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const extractDepts = (list: any[]): DeptItem[] => {
  const result: DeptItem[] = []
  const traverse = (items: any[]) => {
    for (const item of items) {
      result.push({
        id: item.id,
        departmentName: item.departmentName
      })
      if (item.children && item.children.length > 0) {
        traverse(item.children)
      }
    }
  }
  traverse(list)
  return result
}

const getDepartments = async () => {
  try {
    const res = await getDepartmentApi()
    if (res && res.code === 0) {
      departments.value = extractDepts(res.data.list)
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
  positionName: '',
  departmentId: '',
  baseSalary: 0,
  status: 1,
  remark: ''
})

const rules = reactive<FormRules>({
  positionName: [{ required: true, message: 'Iltimos, lavozim nomini kiriting', trigger: 'blur' }]
})

const openAddDialog = () => {
  dialogType.value = 'add'
  form.id = ''
  form.positionName = ''
  form.departmentId = ''
  form.baseSalary = 0
  form.status = 1
  form.remark = ''
  dialogVisible.value = true
}

const openEditDialog = (row: any) => {
  dialogType.value = 'edit'
  form.id = row.id
  form.positionName = row.positionName
  form.departmentId = row.departmentId
  form.baseSalary = row.baseSalary
  form.status = row.status
  form.remark = row.remark || ''
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const res = await savePositionApi(form)
        if (res && res.code === 0) {
          ElMessage.success('Lavozim muvaffaqiyatli saqlandi')
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
  ElMessageBox.confirm("Ushbu lavozimni o'chirishni tasdiqlaysizmi?", 'Eslatma', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'warning'
  })
    .then(async () => {
      const res = await deletePositionApi({ ids: [row.id] })
      if (res && res.code === 0) {
        ElMessage.success("Lavozim o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return
  ElMessageBox.confirm(
    `Tanlangan ${selectedIds.value.length} ta lavozimni o'chirishni tasdiqlaysizmi?`,
    'Eslatma',
    {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(async () => {
      const res = await deletePositionApi({ ids: selectedIds.value })
      if (res && res.code === 0) {
        ElMessage.success("Tanlangan lavozimlar o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

onMounted(() => {
  getList()
  getDepartments()
})
</script>

<style scoped>
.mb-20px {
  margin-bottom: 20px;
}
</style>
