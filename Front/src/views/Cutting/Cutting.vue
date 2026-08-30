<template>
  <ContentWrap>
    <!-- Search Bar -->
    <div class="mb-20px flex justify-between items-center">
      <el-form :inline="true" :model="searchQuery" class="demo-form-inline">
        <el-form-item label="Order raqami">
          <el-input v-model="searchQuery.order_number" placeholder="Order raqami" clearable />
        </el-form-item>
        <el-form-item label="Loyiha">
          <el-input v-model="searchQuery.project" placeholder="Loyiha nomi" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">{{ t('common.search') }}</el-button>
          <el-button @click="resetSearch">{{ t('common.reset') }}</el-button>
        </el-form-item>
      </el-form>
      <div>
        <el-button type="primary" @click="openAddDialog">Yangi buyurtma</el-button>
      </div>
    </div>

    <!-- Table -->
    <el-table v-loading="loading" :data="tableData" style="width: 100%">
      <el-table-column type="expand">
        <template #default="props">
          <div class="p-4 bg-slate-50/50 rounded-lg border border-slate-100">
            <h3 class="font-bold mb-2">Buyurtma tarkibi:</h3>
            <el-table :data="props.row.items" size="small" border>
              <el-table-column prop="productName" :label="t('erp.productName')" min-width="180" />
              <el-table-column prop="category" :label="t('erp.category')" width="120" />
              <el-table-column prop="color" label="Rangi" width="100" />
              <el-table-column prop="code" label="Kodi/Artikul" width="120" />
              <el-table-column prop="cuttingProcessName" label="Jarayon (Tehprocess)" width="180" />
              <el-table-column prop="quantity" label="Miqdori (dona)" width="120" align="center" />
            </el-table>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="order_number" label="Buyurtma #" width="150" />
      <el-table-column
        prop="order_name"
        label="Buyurtma nomi"
        min-width="180"
        show-overflow-tooltip
      />
      <el-table-column prop="project" label="Loyiha" width="150" />
      <el-table-column prop="document_date" label="Hujjat sanasi" width="130" />
      <el-table-column prop="total_quantity" label="Jami miqdor" width="130" align="center" />
      <el-table-column label="Mas'ullar" width="160">
        <template #default="scope">
          <Avatars
            v-if="scope.row.responsible_user_ids && scope.row.responsible_user_ids.length"
            size="small"
            :max="4"
            :data="
              scope.row.responsible_user_ids.map((username: string) => {
                const u = userMap[username]
                return {
                  name: u?.full_name || username,
                  url: u?.avatar || '',
                  initials: u?.initials || username.slice(0, 2).toUpperCase()
                }
              })
            "
          />
        </template>
      </el-table-column>
      <el-table-column prop="status" :label="t('erp.holati')" width="150" align="center">
        <template #default="scope">
          <el-tag :type="getStatusTagType(scope.row.status)">
            {{ getStatusLabel(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('erp.amallar')" width="280" fixed="right">
        <template #default="scope">
          <el-button
            link
            type="success"
            :disabled="scope.row.status !== 'created'"
            @click="handleStartProduction(scope.row)"
          >
            Ishlab chiqarishni boshlash
          </el-button>
          <el-button link type="primary" @click="openEditDialog(scope.row)">{{
            t('common.edit')
          }}</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">{{
            t('common.delete')
          }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Add/Edit Order Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? 'Yangi buyurtma kiritish' : 'Buyurtmani tahrirlash'"
      width="850px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="Buyurtma #" prop="order_number">
            <el-input
              v-model="form.order_number"
              placeholder="Masalan: ORD-2026-001"
              :disabled="dialogType === 'edit'"
            />
          </el-form-item>
          <el-form-item label="Loyiha" prop="project">
            <el-input v-model="form.project" placeholder="Loyiha nomi" />
          </el-form-item>
          <el-form-item label="Buyurtma nomi" prop="order_name">
            <el-input v-model="form.order_name" placeholder="Masalan: T-shirt and Hoodie batch" />
          </el-form-item>
          <el-form-item label="Hujjat sanasi" prop="document_date">
            <el-date-picker
              v-model="form.document_date"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="Sana tanlang"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="Mas'ullar" prop="responsible_user_ids">
            <el-select
              v-model="form.responsible_user_ids"
              multiple
              placeholder="Mas'ullarni tanlang"
              style="width: 100%"
            >
              <el-option
                v-for="user in userList"
                :key="user.username"
                :label="user.username"
                :value="user.username"
              />
            </el-select>
          </el-form-item>
        </div>

        <el-divider>Buyurtma tarkibidagi mahsulotlar</el-divider>

        <div
          v-for="(item, idx) in form.items"
          :key="idx"
          class="border border-[var(--el-border-color-lighter)] p-3 rounded-lg mb-3 bg-[var(--el-fill-color-light)]"
        >
          <div class="flex justify-between items-center mb-2">
            <span class="font-bold text-[var(--el-text-color-primary)]"
              >Mahsulot #{{ idx + 1 }}</span
            >
            <el-button type="danger" link size="small" @click="removeItem(idx)">{{
              t('common.delete')
            }}</el-button>
          </div>
          <div class="grid grid-cols-3 gap-3">
            <el-form-item label="Mahsulot" label-width="80px">
              <el-select
                v-model="item.productId"
                placeholder="Tanlang"
                style="width: 100%"
                @change="onProductChange(item)"
              >
                <el-option v-for="p in products" :key="p.id" :label="p.productName" :value="p.id" />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('erp.category')" label-width="80px">
              <el-input v-model="item.category" placeholder="Masalan: Ustki kiyim" />
            </el-form-item>
            <el-form-item label="Rangi" label-width="80px">
              <el-input v-model="item.color" placeholder="Rangi" />
            </el-form-item>
            <el-form-item label="Artikul/Kodi" label-width="80px">
              <el-input v-model="item.code" placeholder="Kodi" />
            </el-form-item>
            <el-form-item label="Tehprocess" label-width="80px">
              <el-select
                v-model="item.cuttingProcessId"
                placeholder="Tanlang"
                style="width: 100%"
                @change="onProcessChange(item)"
              >
                <el-option v-for="pr in processes" :key="pr.id" :label="pr.name" :value="pr.id" />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('erp.miqdori')" label-width="80px">
              <el-input-number v-model="item.quantity" :min="1" :step="10" style="width: 100%" />
            </el-form-item>
          </div>
        </div>

        <div class="text-center mt-3">
          <el-button type="success" plain @click="addItem">Yangi mahsulot qo'shish</el-button>
        </div>
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
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
import { ref, reactive, onMounted } from 'vue'
import { ContentWrap } from '@/components/ContentWrap'
import {
  ElMessage,
  ElMessageBox,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElButton,
  ElTable,
  ElTableColumn,
  ElTag,
  ElDialog,
  ElDivider,
  ElSelect,
  ElOption,
  ElDatePicker
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getOrderListApi,
  saveOrderApi,
  deleteOrderApi,
  startProductionApi,
  getProcessListApi
} from '@/api/cutting'
import { getProductListApi } from '@/api/product'
import { getUserListApi } from '@/api/login'
import { Avatars } from '@/components/Avatars'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const searchQuery = reactive({
  order_number: '',
  project: ''
})

const loading = ref(false)
const tableData = ref<any[]>([])
const products = ref<any[]>([])
const processes = ref<any[]>([])

/** username → { full_name, initials, avatar } lookup map */
const userMap = ref<Record<string, any>>({})

const getList = async (silent = false) => {
  if (!silent) {
    loading.value = true
  }
  try {
    const res = await getOrderListApi()
    if (res && res.code === 0) {
      // Filter list locally based on search queries
      let list = res.data.list || []
      if (searchQuery.order_number) {
        list = list.filter((o: any) =>
          o.order_number.toLowerCase().includes(searchQuery.order_number.toLowerCase())
        )
      }
      if (searchQuery.project) {
        list = list.filter((o: any) =>
          o.project.toLowerCase().includes(searchQuery.project.toLowerCase())
        )
      }
      tableData.value = list
    }
  } catch (err) {
    console.error(err)
  } finally {
    if (!silent) {
      loading.value = false
    }
  }
}

// Silently refresh cutting orders when changes occur
useRealtimeSync('cutting', () => {
  getList(true)
})

const getProductsAndProcesses = async () => {
  try {
    const resProd = await getProductListApi({ pageIndex: 1, pageSize: 100 })
    if (resProd && resProd.code === 0) {
      products.value = resProd.data.list || []
    }
    const resProc = await getProcessListApi()
    if (resProc && resProc.code === 0) {
      processes.value = resProc.data.list || []
    }
  } catch (err) {
    console.error(err)
  }
}

const userList = ref<any[]>([])

const getUsers = async () => {
  try {
    const res = await getUserListApi({ params: { pageIndex: 1, pageSize: 100 } })
    if (res && res.code === 0) {
      const list = (res.data as any).list || []
      userList.value = list
      // Build lookup map: username → user object (contains avatar, initials, full_name)
      const map: Record<string, any> = {}
      list.forEach((u: any) => {
        map[u.username] = u
      })
      userMap.value = map
    }
  } catch (err) {
    console.error(err)
  }
}

const handleSearch = () => {
  getList()
}

const resetSearch = () => {
  searchQuery.order_number = ''
  searchQuery.project = ''
  getList()
}

// Dialog Logic
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  id: '',
  order_number: '',
  project: '',
  order_name: '',
  document_date: '',
  responsible_user_ids: [] as string[],
  status: 'created',
  items: [] as any[]
})

const rules = reactive<FormRules>({
  order_number: [
    { required: true, message: 'Iltimos, buyurtma raqamini kiriting', trigger: 'blur' }
  ]
})

const openAddDialog = () => {
  dialogType.value = 'add'
  dialogVisible.value = true
  form.id = ''
  form.order_number = ''
  form.project = ''
  form.order_name = ''
  form.document_date = new Date().toISOString().split('T')[0]
  form.responsible_user_ids = []
  form.items = []
  addItem()
}

const openEditDialog = (row: any) => {
  dialogType.value = 'edit'
  dialogVisible.value = true
  form.id = row.id
  form.order_number = row.order_number
  form.project = row.project
  form.order_name = row.order_name
  form.document_date = row.document_date
  form.status = row.status
  form.responsible_user_ids = row.responsible_user_ids ? [...row.responsible_user_ids] : []
  form.items = row.items ? JSON.parse(JSON.stringify(row.items)) : []
}

const addItem = () => {
  form.items.push({
    productId: '',
    category: '',
    color: '',
    code: '',
    cuttingProcessId: '',
    quantity: 100,
    size_breakdown: {},
    material_consumptions: [],
    process_snapshot: []
  })
}

const removeItem = (idx: number) => {
  form.items.splice(idx, 1)
}

const onProductChange = (item: any) => {
  const p = products.value.find((prod) => prod.id === item.productId)
  if (p) {
    item.category = p.category
    item.code = p.SKU
  }
}

const onProcessChange = (item: any) => {
  const pr = processes.value.find((proc) => proc.id === item.cuttingProcessId)
  if (pr) {
    item.process_snapshot = pr.stages || []
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (form.items.length === 0) {
        ElMessage.warning("Iltimos, kamida bitta mahsulot qo'shing")
        return
      }
      submitLoading.value = true
      try {
        const res = await saveOrderApi(form)
        if (res && res.code === 0) {
          ElMessage.success('Buyurtma muvaffaqiyatli saqlandi')
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
  ElMessageBox.confirm("Ushbu buyurtmani o'chirishni tasdiqlaysizmi?", 'Eslatma', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'warning'
  })
    .then(async () => {
      const res = await deleteOrderApi({ ids: [row.id] })
      if (res && res.code === 0) {
        ElMessage.success("Buyurtma o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

const handleStartProduction = (row: any) => {
  ElMessageBox.confirm(
    "Buyurtma bo'yicha ishlab chiqarishni (raskroy) boshlashni tasdiqlaysizmi? Bu barcha etaplar uchun vazifalar (cutting tasks) yaratadi.",
    'Tasdiqlash',
    {
      confirmButtonText: 'Boshlash',
      cancelButtonText: 'Bekor qilish',
      type: 'success'
    }
  )
    .then(async () => {
      const res = await startProductionApi({ orderId: row.id })
      if (res && res.code === 0) {
        ElMessage.success('Ishlab chiqarish boshlandi va vazifalar yaratildi!')
        getList()
      }
    })
    .catch(() => {})
}

// Helpers
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    created: 'Yaratilgan',
    in_production: 'Ishlab chiqarishda',
    in_progress: 'Jarayonda',
    completed: 'Yakunlangan',
    cancelled: 'Bekor qilingan',
    shipped: "Jo'natilgan"
  }
  return map[status] || status
}

const getStatusTagType = (
  status: string
): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
  const map: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
    created: 'info',
    in_production: 'primary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger',
    shipped: 'success'
  }
  return map[status] || 'info'
}

onMounted(() => {
  getList()
  getProductsAndProcesses()
  getUsers()
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
.grid-cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.gap-4 {
  gap: 16px;
}
.gap-3 {
  gap: 12px;
}
.p-4 {
  padding: 16px;
}
.p-3 {
  padding: 12px;
}
.rounded-lg {
  border-radius: 8px;
}
.font-bold {
  font-weight: 700;
}
:deep(.el-avatar + .el-avatar) {
  margin-left: -16px !important;
}
</style>
