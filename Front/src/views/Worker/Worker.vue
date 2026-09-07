<template>
  <ContentWrap>
    <!-- Search and Actions Bar -->
    <div class="mb-20px flex justify-between items-center">
      <el-form :inline="true" :model="searchQuery" class="demo-form-inline">
        <el-form-item :label="t('erp.workerIdSearch')">
          <el-input
            v-model="searchQuery.name"
            :placeholder="t('erp.workerSearchPlaceholder')"
            clearable
          />
        </el-form-item>
        <el-form-item :label="t('erp.department')">
          <el-select
            v-model="searchQuery.departmentId"
            :placeholder="t('erp.selectDepartment')"
            clearable
            style="width: 180px"
          >
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.departmentName"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('userDemo.role')">
          <el-select
            v-model="searchQuery.role"
            placeholder="Rol bo'yicha"
            clearable
            style="width: 170px"
          >
            <el-option v-for="r in roleOptions" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">{{ t('common.search') }}</el-button>
          <el-button @click="resetSearch">{{ t('common.reset') }}</el-button>
        </el-form-item>
      </el-form>
      <div>
        <el-button type="primary" @click="openAddDialog">{{ t('erp.newWorker') }}</el-button>
        <el-button type="danger" :disabled="selectedIds.length === 0" @click="handleBatchDelete">{{
          t('erp.batchDismiss')
        }}</el-button>
      </div>
    </div>

    <!-- Table without Email column and with Roli -->
    <el-table
      v-loading="loading"
      :data="tableData"
      style="width: 100%"
      border
      stripe
      class="custom-workers-table"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" :label="t('erp.workerId')" width="130">
        <template #default="scope">
          <span class="font-mono font-bold text-blue-600 dark:text-blue-400">{{
            scope.row.id
          }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" :label="t('erp.workerFullName')" width="190">
        <template #default="scope">
          <span class="font-bold text-[var(--el-text-color-primary)] text-14px">{{
            scope.row.name
          }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="account" :label="t('erp.loginName')" width="140">
        <template #default="scope">
          <span class="font-semibold text-gray-700 dark:text-gray-300 font-mono">{{
            scope.row.account
          }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="role" :label="t('userDemo.role')" min-width="180">
        <template #default="scope">
          <el-tag
            :type="getRoleTagType(scope.row.role)"
            class="font-semibold rounded-lg"
            effect="light"
          >
            {{ scope.row.role || 'Oddiy xodim' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="departmentName" :label="t('erp.departmentNameCol')" min-width="160">
        <template #default="scope">
          <span class="font-semibold text-gray-800 dark:text-gray-200">{{
            scope.row.departmentName
          }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="phone" :label="t('erp.phoneNumber')" min-width="160">
        <template #default="scope">
          <span class="font-mono font-bold text-gray-700 dark:text-gray-300">{{
            scope.row.phone
          }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="baseSalary" :label="t('erp.baseSalaryDollar')" min-width="160">
        <template #default="scope">
          <span class="font-mono font-extrabold text-emerald-600 dark:text-emerald-400 text-14px"
            >${{ formatMoney(scope?.row?.baseSalary) }}</span
          >
        </template>
      </el-table-column>
      <el-table-column prop="hireDate" :label="t('erp.ishgaKirganSana')" min-width="150">
        <template #default="scope">
          <span class="font-mono font-semibold text-gray-600 dark:text-gray-400">{{
            scope.row.hireDate
          }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" :label="t('erp.holati')" min-width="120">
        <template #default="scope">
          <el-tag
            v-if="scope?.row"
            :type="scope.row.status === 1 ? 'success' : 'danger'"
            class="font-bold rounded-pill"
          >
            {{ scope.row.status === 1 ? t('erp.working') : t('erp.dismissed') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.action')" width="160" fixed="right" align="center">
        <template #default="scope">
          <div
            v-if="scope?.row"
            class="flex items-center justify-center gap-8px flex-nowrap whitespace-nowrap"
          >
            <el-button
              link
              type="primary"
              size="small"
              class="!font-bold !text-13px"
              @click="openEditDialog(scope.row)"
            >
              {{ t('common.edit') }}
            </el-button>
            <el-dropdown trigger="click">
              <el-button link type="info" size="small" class="!font-bold !text-13px">
                •••
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleDelete(scope.row)">
                    <span class="text-red-500 font-semibold">{{ t('erp.dismiss') }}</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div class="mt-20px flex justify-end">
      <el-pagination
        v-model:current-page="pagination.pageIndex"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[5, 10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- Add/Edit Employee Dialog -->
    <ResizeDialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? t('erp.hireNewWorker') : t('erp.editWorkerInfo')"
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="550"
      :min-resize-height="350"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="demo-ruleForm">
        <el-form-item :label="t('erp.workerFullName')" prop="name">
          <el-input v-model="form.name" :placeholder="t('erp.enterWorkerName')" />
        </el-form-item>
        <el-form-item :label="t('erp.loginName')" prop="account">
          <el-input
            v-model="form.account"
            :placeholder="t('erp.loginPlaceholder')"
            :disabled="dialogType === 'edit'"
          />
        </el-form-item>
        <el-form-item :label="t('userDemo.role')" prop="role">
          <el-select v-model="form.role" :placeholder="t('erp.selectRole')" style="width: 100%">
            <el-option v-for="r in roleOptions" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('erp.department')" prop="departmentId">
          <el-select
            v-model="form.departmentId"
            :placeholder="t('erp.selectDepartment')"
            style="width: 100%"
          >
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.departmentName"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('erp.phoneNumber')" prop="phone">
          <el-input v-model="form.phone" :placeholder="t('erp.phoneNumber')" />
        </el-form-item>
        <el-form-item :label="t('erp.baseSalaryLabel')" prop="baseSalary">
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
        <el-form-item :label="t('erp.ishgaKirganSana')" prop="hireDate">
          <el-date-picker
            v-model="form.hireDate"
            type="date"
            :placeholder="t('erp.selectDatePlaceholder')"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('erp.holati')" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">{{ t('erp.working') }}</el-radio>
            <el-radio :value="0">{{ t('erp.dismissed') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('erp.systemPassword')" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="
              dialogType === 'add' ? t('erp.passwordOptionalDefault') : t('erp.newPasswordOptional')
            "
          />
        </el-form-item>
        <el-form-item
          v-if="dialogType === 'edit'"
          :label="t('erp.adminPassword')"
          prop="adminPassword"
          class="admin-verify-item"
        >
          <el-input
            v-model="form.adminPassword"
            type="password"
            show-password
            :placeholder="t('erp.adminPasswordVerifyPlaceholder')"
          />
        </el-form-item>
        <el-form-item :label="t('erp.izoh')" prop="remark">
          <el-input v-model="form.remark" type="textarea" :placeholder="t('erp.workerExtraInfo')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="submitLoading" @click="submitForm">{{
            t('common.save')
          }}</el-button>
        </span>
      </template>
    </ResizeDialog>
  </ContentWrap>
</template>

<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
defineOptions({ name: 'Worker' })
import { ref, reactive, onMounted } from 'vue'

const dialogInitWidth = Math.min(window.innerWidth * 0.92, 1400)
const dialogInitHeight = Math.min(window.innerHeight * 0.88, 800)

import {
  ElMessage,
  ElMessageBox,
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption,
  ElButton,
  ElTable,
  ElTableColumn,
  ElTag,
  ElPagination,
  ElInputNumber,
  ElDatePicker,
  ElRadio,
  ElRadioGroup
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { ContentWrap } from '@/components/ContentWrap'
import { ResizeDialog } from '@/components/Dialog'
import { getWorkerListApi, saveWorkerApi, deleteWorkerApi } from '@/api/worker'
import type { WorkerType } from '@/api/worker'
import { getDepartmentApi } from '@/api/department'
import { getRoleListApi } from '@/api/role'
import { formatMoney, moneyFormatter, moneyParser } from '@/utils'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

interface DeptItem {
  id: string
  departmentName: string
}

const loading = ref(false)
const tableData = ref<WorkerType[]>([])
const total = ref(0)
const selectedIds = ref<string[]>([])
const departments = ref<DeptItem[]>([])
const roleOptions = ref<string[]>([
  'Super Administrator',
  'Administrator',
  'Cashier',
  'Oddiy xodim'
])

const searchQuery = reactive({
  name: '',
  departmentId: '',
  role: ''
})

const pagination = reactive({
  pageIndex: 1,
  pageSize: 10
})

const getRoleTagType = (roleName?: string) => {
  if (!roleName) return 'primary'
  if (roleName.includes('Super')) return 'danger'
  if (roleName.includes('Admin')) return 'warning'
  if (roleName.includes('Cashier') || roleName.includes('Kassir')) return 'success'
  if (roleName.includes('Oddiy') || roleName.includes('Staff')) return 'primary'
  return 'info'
}

const fetchRoles = async () => {
  try {
    const res: any = await getRoleListApi()
    if (res && res.data && res.data.list && res.data.list.length > 0) {
      const names = res.data.list.map((r: any) => r.roleName || r.name || r.role).filter(Boolean)
      roleOptions.value = Array.from(new Set(['Oddiy xodim', ...names]))
    }
  } catch (error) {
    console.error('Failed to load system roles', error)
  }
}

// Recursively extract all departments from tree
const extractDepts = (list: any[]): DeptItem[] => {
  let depts: DeptItem[] = []
  for (const item of list) {
    depts.push({
      id: item.id,
      departmentName: item.departmentName
    })
    if (item.children && item.children.length > 0) {
      depts = depts.concat(extractDepts(item.children))
    }
  }
  return depts
}

const fetchDepartments = async () => {
  try {
    const res = await getDepartmentApi()
    if (res && res.data && res.data.list) {
      departments.value = extractDepts(res.data.list)
    }
  } catch (error) {
    console.error('Failed to load departments', error)
  }
}

const getList = async (silent = false) => {
  if (!silent) {
    loading.value = true
  }
  try {
    const res = await getWorkerListApi({
      pageIndex: pagination.pageIndex,
      pageSize: pagination.pageSize,
      name: searchQuery.name,
      departmentId: searchQuery.departmentId,
      role: searchQuery.role
    })
    if (res && res.data) {
      tableData.value = res.data.list || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error(error)
  } finally {
    if (!silent) {
      loading.value = false
    }
  }
}

// Silently update worker list on changes
useRealtimeSync('worker', () => {
  getList(true)
})

import { useEventBus } from '@/hooks/event/useEventBus'

useEventBus({
  name: 'refresh-workers',
  callback: () => {
    getList()
  }
})

useEventBus({
  name: 'ai-data-updated',
  callback: () => {
    getList()
  }
})

onMounted(() => {
  fetchDepartments()
  fetchRoles()
  getList()
})

const handleSearch = () => {
  pagination.pageIndex = 1
  getList()
}

const resetSearch = () => {
  searchQuery.name = ''
  searchQuery.departmentId = ''
  searchQuery.role = ''
  pagination.pageIndex = 1
  getList()
}

const handleSelectionChange = (selection: WorkerType[]) => {
  selectedIds.value = selection.map((item) => item.id as string)
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  getList()
}

const handleCurrentChange = (val: number) => {
  pagination.pageIndex = val
  getList()
}

// Dialog Logic
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive<WorkerType>({
  id: '',
  name: '',
  account: '',
  email: '',
  phone: '',
  role: '',
  departmentId: '',
  hireDate: '',
  status: 1,
  baseSalary: 0,
  remark: '',
  password: '',
  adminPassword: ''
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: 'Iltimos, ismni kiriting', trigger: 'blur' }],
  account: [{ required: true, message: 'Iltimos, login nomini kiriting', trigger: 'blur' }],
  role: [{ required: true, message: 'Iltimos, rolni tanlang', trigger: 'change' }],
  departmentId: [{ required: true, message: "Iltimos, bo'limni tanlang", trigger: 'change' }],
  adminPassword: [
    {
      validator: (_rule: any, value: any, callback: any) => {
        if (dialogType.value === 'edit' && !value) {
          callback(new Error("O'zgartirishni tasdiqlash uchun admin parolingizni kiriting!"))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})

const openAddDialog = () => {
  dialogType.value = 'add'
  dialogVisible.value = true
  form.id = ''
  form.name = ''
  form.account = ''
  form.email = ''
  form.phone = ''
  form.role = roleOptions.value.includes('Oddiy xodim')
    ? 'Oddiy xodim'
    : roleOptions.value[0] || 'Oddiy xodim'
  form.departmentId = ''
  form.hireDate = new Date().toISOString().substring(0, 10)
  form.status = 1
  form.baseSalary = 3000
  form.remark = ''
  form.password = ''
  form.adminPassword = ''
}

const openEditDialog = (row: WorkerType) => {
  dialogType.value = 'edit'
  dialogVisible.value = true
  form.id = row.id
  form.name = row.name
  form.account = row.account
  form.email = row.email || ''
  form.phone = row.phone || ''
  form.role = row.role || 'Oddiy xodim'
  form.departmentId = row.departmentId || ''
  form.hireDate = row.hireDate || ''
  form.status = row.status ?? 1
  form.baseSalary = row.baseSalary || 0
  form.remark = row.remark || ''
  form.password = ''
  form.adminPassword = ''
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const res: any = await saveWorkerApi(form)
        if (res && res.code === 0) {
          ElMessage.success(
            dialogType.value === 'add'
              ? 'Xodim muvaffaqiyatli ishga olindi'
              : "Xodim ma'lumotlari muvaffaqiyatli tahrirlandi"
          )
          dialogVisible.value = false
          getList()
        } else if (res && res.message) {
          ElMessage.error(res.message)
        }
      } catch (error: any) {
        ElMessage.error(error.message || 'Saqlashda xatolik yuz berdi')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = (row: WorkerType) => {
  ElMessageBox.confirm(
    `Haqiqatan ham xodim [${row.name}] ni bo'shatishni xohlaysizmi?`,
    'Ogohlantirish',
    {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(async () => {
      const res = await deleteWorkerApi({ ids: [row.id as string] })
      if (res && res.code === 0) {
        ElMessage.success("Xodim muvaffaqiyatli bo'shatildi")
        getList()
      }
    })
    .catch(() => {})
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return
  ElMessageBox.confirm(
    `Tanlangan ${selectedIds.value.length} nafar xodimni bo'shatishni tasdiqlaysizmi?`,
    "Guruhli bo'shatish ogohlantirishi",
    {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(async () => {
      const res = await deleteWorkerApi({ ids: selectedIds.value })
      if (res && res.code === 0) {
        ElMessage.success("Guruhli bo'shatish muvaffaqiyatli yakunlandi")
        getList()
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.mb-20px {
  margin-bottom: 20px;
}
.mt-20px {
  margin-top: 20px;
}
</style>
