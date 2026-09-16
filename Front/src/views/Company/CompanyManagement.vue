<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  ElCard,
  ElRow,
  ElCol,
  ElButton,
  ElInput,
  ElSelect,
  ElOption,
  ElTable,
  ElTableColumn,
  ElTag,
  ElDialog,
  ElDrawer,
  ElTabs,
  ElTabPane,
  ElForm,
  ElFormItem,
  ElInputNumber,
  ElDatePicker,
  ElSwitch,
  ElMessage,
  ElMessageBox,
  ElTooltip,
  ElBadge,
  ElProgress,
  ElRadioGroup,
  ElRadioButton,
  ElDivider,
  ElEmpty
} from 'element-plus'
import { Icon } from '@/components/Icon'
import {
  getCompanyListApi,
  getCompanyDetailApi,
  saveCompanyApi,
  updateCompanyTierApi,
  toggleCompanyStatusApi,
  deleteCompanyApi,
  saveCompanyEmployeeApi,
  deleteCompanyEmployeeApi,
  getMainAccountApi,
  updateMainAccountApi,
  resetCompanyPasswordApi,
  type CompanyType,
  type CompanyDetailType,
  type CompanyWorkerType
} from '@/api/company'

// State
const loading = ref(false)
const tableData = ref<CompanyType[]>([])
const searchQuery = ref('')
const selectedPlanFilter = ref('')
const selectedBillingFilter = ref('')
const selectedStatusFilter = ref('')
const viewMode = ref<'table' | 'card'>('table')

// Dialogs
const saveDialogVisible = ref(false)
const saveDialogType = ref<'add' | 'edit'>('add')
const saveLoading = ref(false)
const saveFormRef = ref()

const tierDialogVisible = ref(false)
const tierLoading = ref(false)
const selectedCompanyForTier = ref<CompanyType | null>(null)

// Password Reset Dialog State
const passwordResetDialogVisible = ref(false)
const passwordResetLoading = ref(false)
const passwordResetForm = reactive({
  company_id: '',
  company_name: '',
  username: '',
  new_password: '',
  full_name: ''
})

// Main Account Dialog State
const mainAccountDialogVisible = ref(false)
const mainAccountLoading = ref(false)
const mainAccountForm = reactive({
  admin_username: 'admin',
  admin_password: '',
  admin_full_name: 'Administrator',
  admin_email: '',
  admin_phone: '',
  company_name: 'Bosh Korxona',
  company_code: 'default',
  company_phone: '',
  company_email: '',
  company_address: ''
})

// Drilldown Drawer State
const drawerVisible = ref(false)
const drawerLoading = ref(false)
const drawerActiveTab = ref('overview')
const currentCompanyDetail = ref<CompanyDetailType | null>(null)
const workerSearchQuery = ref('')

const drawerSize = computed(() => {
  if (typeof window !== 'undefined' && window.innerWidth < 860) {
    return '100%'
  }
  return '840px'
})

// Employee Dialog State
const employeeDialogVisible = ref(false)
const employeeDialogType = ref<'add' | 'edit'>('add')
const employeeFormRef = ref()
const employeeLoading = ref(false)
const employeeForm = reactive<Partial<CompanyWorkerType>>({
  id: '',
  name: '',
  role: 'Mutaxassis',
  phone: '',
  account: '',
  employee_code: '',
  department: '',
  hireDate: '',
  status: 1,
  baseSalary: 0,
  company_id: ''
})

// Company Form State
const companyForm = reactive<Partial<CompanyType>>({
  id: '',
  name: '',
  code: '',
  plan: 'basic',
  billing_cycle: 'monthly',
  subscription_expires_at: '',
  status: 1,
  max_users: 10,
  phone: '',
  email: '',
  address: '',
  admin_username: '',
  admin_password: '',
  admin_full_name: ''
})

const tierForm = reactive({
  company_id: '',
  plan: 'pro' as 'basic' | 'pro',
  billing_cycle: 'monthly' as 'monthly' | 'yearly',
  duration_months: 1,
  subscription_expires_at: '',
  max_users: 10,
  feature_ai: true,
  feature_upcoming: true,
  feature_analytics: true
})

const rules = {
  name: [{ required: true, message: 'Iltimos, kompaniya nomini kiriting', trigger: 'blur' }],
  code: [{ required: true, message: 'Iltimos, kompaniya unikal kodini kiriting', trigger: 'blur' }],
  plan: [{ required: true, message: 'Iltimos, tarifni tanlang', trigger: 'change' }]
}

const employeeRules = {
  name: [{ required: true, message: 'Xodim ismini kiriting', trigger: 'blur' }],
  role: [{ required: true, message: 'Lavozimni tanlang yoki kiriting', trigger: 'blur' }]
}

// KPI Statistics
const stats = computed(() => {
  const total = tableData.value.length
  const proCount = tableData.value.filter((c) => c.plan === 'pro').length
  const basicCount = tableData.value.filter((c) => c.plan === 'basic').length
  const activeCount = tableData.value.filter((c) => !c.is_expired && c.status === 1).length
  const totalRev = tableData.value.reduce((acc, c) => acc + (c.total_revenue || 0), 0)
  const totalEmployees = tableData.value.reduce((acc, c) => acc + (c.employees_count || 0), 0)
  const totalProducts = tableData.value.reduce((acc, c) => acc + (c.products_count || 0), 0)
  return { total, proCount, basicCount, activeCount, totalRev, totalEmployees, totalProducts }
})

// Filtered Companies
const filteredCompanies = computed(() => {
  return tableData.value.filter((comp) => {
    const q = searchQuery.value.toLowerCase().trim()
    const matchSearch =
      !q ||
      comp.name.toLowerCase().includes(q) ||
      comp.code.toLowerCase().includes(q) ||
      (comp.phone && comp.phone.toLowerCase().includes(q)) ||
      (comp.email && comp.email.toLowerCase().includes(q))

    const matchPlan = !selectedPlanFilter.value || comp.plan === selectedPlanFilter.value
    const matchBilling = !selectedBillingFilter.value || comp.billing_cycle === selectedBillingFilter.value
    
    let matchStatus = true
    if (selectedStatusFilter.value === 'active') {
      matchStatus = comp.status === 1 && !comp.is_expired
    } else if (selectedStatusFilter.value === 'suspended') {
      matchStatus = comp.status === 0
    } else if (selectedStatusFilter.value === 'expired') {
      matchStatus = !!comp.is_expired
    }

    return matchSearch && matchPlan && matchBilling && matchStatus
  })
})

// Filtered workers in drawer
const filteredWorkers = computed(() => {
  if (!currentCompanyDetail.value || !currentCompanyDetail.value.workers) return []
  const q = workerSearchQuery.value.toLowerCase().trim()
  if (!q) return currentCompanyDetail.value.workers
  return currentCompanyDetail.value.workers.filter(
    (w) =>
      w.name.toLowerCase().includes(q) ||
      (w.role && w.role.toLowerCase().includes(q)) ||
      (w.phone && w.phone.includes(q)) ||
      (w.account && w.account.toLowerCase().includes(q)) ||
      (w.employee_code && w.employee_code.toLowerCase().includes(q))
  )
})

const formatMoney = (amount?: number) => {
  if (amount === undefined || amount === null) return '0'
  return amount.toLocaleString('uz-UZ')
}

// Fetch list of companies
const fetchCompanies = async () => {
  loading.value = true
  try {
    const res = await getCompanyListApi()
    if (res && res.data) {
      tableData.value = res.data.list || []
    }
  } catch (err: any) {
    ElMessage.error(err?.message || "Kompaniyalar ro'yxatini yuklashda xatolik")
  } finally {
    loading.value = false
  }
}

// Open Drilldown Drawer
const openDrilldownDrawer = async (comp: CompanyType) => {
  drawerVisible.value = true
  drawerLoading.value = true
  drawerActiveTab.value = 'overview'
  workerSearchQuery.value = ''
  try {
    const res = await getCompanyDetailApi(comp.id!)
    if (res && res.data) {
      currentCompanyDetail.value = res.data
    }
  } catch (err: any) {
    ElMessage.error(err?.message || "Kompaniya tafsilotlarini yuklashda xatolik")
  } finally {
    drawerLoading.value = false
  }
}

// Refresh drawer detail
const refreshCurrentCompanyDetail = async () => {
  if (!currentCompanyDetail.value?.id) return
  drawerLoading.value = true
  try {
    const res = await getCompanyDetailApi(currentCompanyDetail.value.id)
    if (res && res.data) {
      currentCompanyDetail.value = res.data
    }
    fetchCompanies()
  } catch (err: any) {
    ElMessage.error(err?.message || "Yangilashda xatolik")
  } finally {
    drawerLoading.value = false
  }
}

// Toggle Company Status
const handleToggleStatus = async (comp: CompanyType, newStatus: number) => {
  try {
    await toggleCompanyStatusApi({ company_id: comp.id!, status: newStatus })
    comp.status = newStatus
    ElMessage.success(`"${comp.name}" holati ${newStatus === 1 ? 'faollashtirildi' : 'to\'xtatildi'}`)
    if (currentCompanyDetail.value && currentCompanyDetail.value.id === comp.id) {
      currentCompanyDetail.value.status = newStatus
    }
  } catch (err: any) {
    ElMessage.error(err?.message || "Holatni o'zgartirishda xatolik")
  }
}

// Open create dialog
const openCreateDialog = () => {
  saveDialogType.value = 'add'
  Object.assign(companyForm, {
    id: '',
    name: '',
    code: `comp_${Date.now().toString().slice(-4)}`,
    plan: 'basic',
    billing_cycle: 'monthly',
    subscription_expires_at: '',
    status: 1,
    max_users: 10,
    phone: '',
    email: '',
    address: '',
    admin_username: '',
    admin_password: '',
    admin_full_name: ''
  })
  saveDialogVisible.value = true
}

// Open edit dialog
const openEditDialog = (row: CompanyType) => {
  saveDialogType.value = 'edit'
  Object.assign(companyForm, {
    id: row.id,
    name: row.name,
    code: row.code,
    plan: row.plan,
    billing_cycle: row.billing_cycle,
    subscription_expires_at: row.subscription_expires_at,
    status: row.status,
    max_users: row.max_users || 10,
    phone: row.phone || '',
    email: row.email || '',
    address: row.address || '',
    admin_username: '',
    admin_password: '',
    admin_full_name: ''
  })
  saveDialogVisible.value = true
}

// Save company
const handleSaveSubmit = async () => {
  if (!saveFormRef.value) return
  await saveFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      saveLoading.value = true
      try {
        await saveCompanyApi(companyForm)
        ElMessage.success(
          saveDialogType.value === 'add'
            ? 'Yangi kompaniya muvaffaqiyatli yaratildi'
            : 'Kompaniya ma\'lumotlari yangilandi'
        )
        saveDialogVisible.value = false
        fetchCompanies()
        if (currentCompanyDetail.value && currentCompanyDetail.value.id === companyForm.id) {
          refreshCurrentCompanyDetail()
        }
      } catch (err: any) {
        ElMessage.error(err?.message || "Saqlashda xatolik yuz berdi")
      } finally {
        saveLoading.value = false
      }
    }
  })
}

// Open Tier Dialog
const openTierDialog = (row: CompanyType) => {
  selectedCompanyForTier.value = row
  tierForm.company_id = row.id || ''
  tierForm.plan = row.plan || 'pro'
  tierForm.billing_cycle = row.billing_cycle || 'monthly'
  tierForm.duration_months = 1
  tierForm.subscription_expires_at = row.subscription_expires_at || ''
  tierForm.max_users = row.max_users || 10
  tierForm.feature_ai = row.plan === 'pro' ? true : !!row.features?.ai
  tierForm.feature_upcoming = row.plan === 'pro' ? true : !!row.features?.upcoming
  tierForm.feature_analytics = row.plan === 'pro' ? true : !!row.features?.advanced_analytics
  tierDialogVisible.value = true
}

// Save Tier & Subscription
const handleTierSubmit = async () => {
  tierLoading.value = true
  try {
    await updateCompanyTierApi({
      company_id: tierForm.company_id,
      plan: tierForm.plan,
      billing_cycle: tierForm.billing_cycle,
      duration_months: Number(tierForm.duration_months) || 1,
      subscription_expires_at: tierForm.subscription_expires_at || undefined,
      max_users: Number(tierForm.max_users) || 10,
      features: {
        ai: tierForm.feature_ai,
        upcoming: tierForm.feature_upcoming,
        advanced_analytics: tierForm.feature_analytics
      }
    })
    ElMessage.success(`"${selectedCompanyForTier.value?.name}" tarifi muvaffaqiyatli yangilandi!`)
    tierDialogVisible.value = false
    fetchCompanies()
    if (currentCompanyDetail.value && currentCompanyDetail.value.id === tierForm.company_id) {
      refreshCurrentCompanyDetail()
    }
  } catch (err: any) {
    ElMessage.error(err?.message || "Tarifni o'zgartirishda xatolik")
  } finally {
    tierLoading.value = false
  }
}

// Delete company
const handleDeleteCompany = (row: CompanyType) => {
  if (row.id === 'comp-default') {
    ElMessage.warning("Asosiy bosh korxonani o'chirib bo'lmaydi")
    return
  }
  ElMessageBox.confirm(
    `Haqiqatan ham "${row.name}" kompaniyasini va unga tegishli barcha ma'lumotlarni (mahsulotlar, savdolar, xodimlar) o'chirmoqchimisiz?`,
    'Xavfli Amal: Kompaniyani o\'chirish',
    {
      confirmButtonText: 'Ha, butunlay o\'chirish',
      cancelButtonText: 'Bekor qilish',
      type: 'error'
    }
  ).then(async () => {
    try {
      await deleteCompanyApi({ id: row.id! })
      ElMessage.success("Kompaniya muvaffaqiyatli o'chirildi")
      if (drawerVisible.value && currentCompanyDetail.value?.id === row.id) {
        drawerVisible.value = false
      }
      fetchCompanies()
    } catch (err: any) {
      ElMessage.error(err?.message || "O'chirishda xatolik")
    }
  })
}

// Open Password Reset Dialog
const openPasswordResetDialog = (row: any) => {
  passwordResetForm.company_id = row.id || ''
  passwordResetForm.company_name = row.name || ''
  passwordResetForm.username = row.admin_username || row.admin_user?.username || ''
  passwordResetForm.new_password = ''
  passwordResetForm.full_name = row.admin_full_name || row.admin_user?.full_name || ''
  passwordResetDialogVisible.value = true
}

const handlePasswordResetSubmit = async () => {
  if (!passwordResetForm.new_password || !passwordResetForm.new_password.trim()) {
    ElMessage.warning('Iltimos, yangi parolni kiriting')
    return
  }
  passwordResetLoading.value = true
  try {
    await resetCompanyPasswordApi({
      company_id: passwordResetForm.company_id,
      new_password: passwordResetForm.new_password.trim(),
      username: passwordResetForm.username ? passwordResetForm.username.trim() : undefined,
      full_name: passwordResetForm.full_name ? passwordResetForm.full_name.trim() : undefined
    })
    ElMessage.success(`"${passwordResetForm.company_name}" admin paroli muvaffaqiyatli yangilandi!`)
    passwordResetDialogVisible.value = false
    fetchCompanies()
    if (currentCompanyDetail.value && currentCompanyDetail.value.id === passwordResetForm.company_id) {
      if (passwordResetForm.username) {
        currentCompanyDetail.value.admin_username = passwordResetForm.username
        if (currentCompanyDetail.value.admin_user) {
          currentCompanyDetail.value.admin_user.username = passwordResetForm.username
        }
      }
      if (passwordResetForm.full_name && currentCompanyDetail.value.admin_user) {
        currentCompanyDetail.value.admin_user.full_name = passwordResetForm.full_name
      }
    }
  } catch (err: any) {
    ElMessage.error(err?.message || "Parolni yangilashda xatolik yuz berdi")
  } finally {
    passwordResetLoading.value = false
  }
}

// Open Employee Add/Edit Dialog
const openAddEmployeeDialog = () => {
  if (!currentCompanyDetail.value?.id) return
  employeeDialogType.value = 'add'
  Object.assign(employeeForm, {
    id: '',
    name: '',
    role: 'Mutaxassis',
    phone: '',
    account: `usr_${Date.now().toString().slice(-4)}`,
    employee_code: `EMP-${Date.now().toString().slice(-5)}`,
    department: 'Asosiy bo\'lim',
    hireDate: new Date().toISOString().slice(0, 10),
    status: 1,
    baseSalary: 0,
    company_id: currentCompanyDetail.value.id
  })
  employeeDialogVisible.value = true
}

const openEditEmployeeDialog = (emp: CompanyWorkerType) => {
  employeeDialogType.value = 'edit'
  Object.assign(employeeForm, {
    id: emp.id,
    name: emp.name,
    role: emp.role || 'Mutaxassis',
    phone: emp.phone || '',
    account: emp.account || '',
    employee_code: emp.employee_code || '',
    department: emp.department || '',
    hireDate: emp.hireDate || '',
    status: emp.status !== undefined ? emp.status : 1,
    baseSalary: emp.baseSalary || 0,
    company_id: currentCompanyDetail.value?.id
  })
  employeeDialogVisible.value = true
}

// Submit Employee
const handleEmployeeSubmit = async () => {
  if (!employeeFormRef.value) return
  await employeeFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      employeeLoading.value = true
      try {
        await saveCompanyEmployeeApi(employeeForm)
        ElMessage.success(
          employeeDialogType.value === 'add'
            ? 'Xodim kompaniyaga muvaffaqiyatli biriktirildi'
            : 'Xodim ma\'lumotlari yangilandi'
        )
        employeeDialogVisible.value = false
        refreshCurrentCompanyDetail()
      } catch (err: any) {
        ElMessage.error(err?.message || "Xodimni saqlashda xatolik")
      } finally {
        employeeLoading.value = false
      }
    }
  })
}

// Delete Employee
const handleDeleteEmployee = (emp: CompanyWorkerType) => {
  ElMessageBox.confirm(
    `"${emp.name}" nomli xodimni ushbu kompaniyadan o'chirmoqchimisiz?`,
    'Xodimni o\'chirish',
    {
      confirmButtonText: 'Ha, o\'chirish',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteCompanyEmployeeApi({ id: emp.id, company_id: currentCompanyDetail.value!.id! })
      ElMessage.success("Xodim muvaffaqiyatli o'chirildi")
      refreshCurrentCompanyDetail()
    } catch (err: any) {
      ElMessage.error(err?.message || "O'chirishda xatolik")
    }
  })
}

const openMainAccountDialog = async () => {
  mainAccountDialogVisible.value = true
  mainAccountLoading.value = true
  try {
    const res = await getMainAccountApi()
    if (res && res.data) {
      const sa = res.data.super_admin || {}
      const mc = res.data.main_company || {}
      mainAccountForm.admin_username = sa.username || 'admin'
      mainAccountForm.admin_password = ''
      mainAccountForm.admin_full_name = sa.full_name || 'Administrator'
      mainAccountForm.admin_email = sa.email || ''
      mainAccountForm.admin_phone = sa.phone || ''
      mainAccountForm.company_name = mc.name || 'Bosh Korxona'
      mainAccountForm.company_code = mc.code || 'default'
      mainAccountForm.company_phone = mc.phone || ''
      mainAccountForm.company_email = mc.email || ''
      mainAccountForm.company_address = mc.address || ''
    }
  } catch (err: any) {
    ElMessage.error(err?.message || "Bosh korxona ma'lumotlarini yuklashda xatolik")
  } finally {
    mainAccountLoading.value = false
  }
}

const handleSaveMainAccount = async () => {
  mainAccountLoading.value = true
  try {
    const res = await updateMainAccountApi(mainAccountForm)
    ElMessage.success(res?.message || "Bosh admin va korxona ma'lumotlari muvaffaqiyatli saqlandi")
    mainAccountDialogVisible.value = false
    fetchCompanies()
  } catch (err: any) {
    ElMessage.error(err?.message || "Saqlashda xatolik yuz berdi")
  } finally {
    mainAccountLoading.value = false
  }
}

onMounted(() => {
  fetchCompanies()
})
</script>

<template>
  <div class="company-management-container p-20px">
    <!-- TOP EXECUTIVE HEADER -->
    <div class="header-section mb-20px flex flex-wrap items-center justify-between gap-12px">
      <div>
        <div class="flex items-center gap-10px">
          <div class="w-40px h-40px rounded-12px bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md">
            <Icon icon="vi-ep:office-building" class="text-24px" />
          </div>
          <div>
            <h1 class="text-22px font-extrabold text-gray-900 dark:text-white tracking-tight">
              SaaS Kompaniyalar Boshqaruv Markazi
            </h1>
            <p class="text-13px text-gray-500 dark:text-gray-400 mt-2px">
              Klaster korxonalari, ularning xodimlari, savdo aylanmasi va tarif rejalarini boshqarish
            </p>
          </div>
        </div>
      </div>
      <div class="flex items-center gap-10px">
        <ElButton type="default" plain @click="fetchCompanies" :loading="loading">
          <Icon icon="ep:refresh" class="mr-4px" /> Yangilash
        </ElButton>
        <ElButton type="warning" plain class="font-semibold" @click="openMainAccountDialog">
          <Icon icon="ep:user" class="mr-4px" /> Bosh Korxona & Super Admin
        </ElButton>
        <ElButton type="primary" class="gradient-btn font-semibold shadow-md" @click="openCreateDialog">
          <Icon icon="ep:plus" class="mr-6px text-16px" /> Yangi Kompaniya Qo'shish
        </ElButton>
      </div>
    </div>

    <!-- METRICS OVERVIEW BAR -->
    <ElRow :gutter="14" class="mb-20px">
      <!-- Total Companies -->
      <ElCol :xs="24" :sm="12" :md="6" class="mb-10px">
        <ElCard shadow="hover" class="stat-card border-l-4 border-blue-500">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-12px text-gray-500 font-medium">Jami Kompaniyalar</div>
              <div class="text-26px font-bold text-gray-900 dark:text-white mt-4px font-mono">
                {{ stats.total }}
              </div>
              <div class="text-11px text-emerald-600 mt-4px flex items-center gap-4px font-medium">
                <Icon icon="ep:circle-check" /> {{ stats.activeCount }} ta faol obuna
              </div>
            </div>
            <div class="icon-circle bg-blue-50 dark:bg-blue-900/30 text-blue-600">
              <Icon icon="ep:office-building" class="text-26px" />
            </div>
          </div>
        </ElCard>
      </ElCol>

      <!-- Pro vs Basic Tier Distribution -->
      <ElCol :xs="24" :sm="12" :md="6" class="mb-10px">
        <ElCard shadow="hover" class="stat-card border-l-4 border-purple-500">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-12px text-purple-600 dark:text-purple-400 font-medium flex items-center gap-4px">
                <Icon icon="ep:medal" /> PRO vs BASIC Tarif
              </div>
              <div class="text-26px font-bold text-purple-600 dark:text-purple-400 mt-4px font-mono">
                {{ stats.proCount }} <span class="text-14px font-normal text-gray-400">/ {{ stats.basicCount }}</span>
              </div>
              <div class="text-11px text-purple-500 mt-4px font-medium flex items-center gap-4px">
                <Icon icon="ep:medal" class="text-12px" /> {{ stats.proCount }} ta PRO (To'liq AI & Yangi imkoniyatlar)
              </div>
            </div>
            <div class="icon-circle bg-purple-50 dark:bg-purple-900/30 text-purple-600">
              <Icon icon="ep:star" class="text-26px" />
            </div>
          </div>
        </ElCard>
      </ElCol>

      <!-- Total Employees across platform -->
      <ElCol :xs="24" :sm="12" :md="6" class="mb-10px">
        <ElCard shadow="hover" class="stat-card border-l-4 border-indigo-500">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-12px text-indigo-600 dark:text-indigo-400 font-medium flex items-center gap-4px">
                <Icon icon="ep:user" /> Jami Platforma Xodimlari
              </div>
              <div class="text-26px font-bold text-indigo-600 dark:text-indigo-400 mt-4px font-mono">
                {{ stats.totalEmployees }}
              </div>
              <div class="text-11px text-gray-500 mt-4px">
                Ishchilar va kassa administratorlari
              </div>
            </div>
            <div class="icon-circle bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600">
              <Icon icon="ep:avatar" class="text-26px" />
            </div>
          </div>
        </ElCard>
      </ElCol>

      <!-- Total Platform GMV Sales Revenue -->
      <ElCol :xs="24" :sm="12" :md="6" class="mb-10px">
        <ElCard shadow="hover" class="stat-card border-l-4 border-emerald-500">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-12px text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-4px">
                <Icon icon="ep:coin" /> Umumiy Savdo Aylanmasi
              </div>
              <div class="text-22px font-bold text-emerald-600 dark:text-emerald-400 mt-4px font-mono">
                {{ formatMoney(stats.totalRev) }} <span class="text-12px font-normal">so'm</span>
              </div>
              <div class="text-11px text-gray-500 mt-4px">
                Klaster bo'yicha jami tushum
              </div>
            </div>
            <div class="icon-circle bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600">
              <Icon icon="ep:money" class="text-26px" />
            </div>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- FILTER & TOOLBAR CARD -->
    <ElCard shadow="never" class="mb-16px filter-card">
      <div class="flex flex-wrap items-center gap-12px justify-between">
        <div class="flex flex-wrap items-center gap-10px flex-1 min-w-280px">
          <ElInput
            v-model="searchQuery"
            placeholder="Kompaniya nomi, kodi yoki telefon..."
            clearable
            class="w-280px"
          >
            <template #prefix>
              <Icon icon="ep:search" class="text-gray-400" />
            </template>
          </ElInput>

          <ElSelect v-model="selectedPlanFilter" placeholder="Barcha tariflar" clearable class="w-160px">
            <ElOption label="Barcha tariflar" value="" />
            <ElOption label="PRO Plan" value="pro" />
            <ElOption label="BASIC Plan" value="basic" />
          </ElSelect>

          <ElSelect v-model="selectedBillingFilter" placeholder="To'lov davri" clearable class="w-150px">
            <ElOption label="Barcha davrlar" value="" />
            <ElOption label="Yillik to'lov" value="yearly" />
            <ElOption label="Oylik to'lov" value="monthly" />
          </ElSelect>

          <ElSelect v-model="selectedStatusFilter" placeholder="Holati" clearable class="w-160px">
            <ElOption label="Barcha holatlar" value="" />
            <ElOption label="Faol obuna" value="active" />
            <ElOption label="To'xtatilgan" value="suspended" />
            <ElOption label="Muddati tugagan" value="expired" />
          </ElSelect>
        </div>

        <!-- View Switcher & Result Count -->
        <div class="flex items-center gap-14px">
          <ElRadioGroup v-model="viewMode" size="small">
            <ElRadioButton label="table">
              <Icon icon="ep:menu" class="mr-2px" /> Jadval
            </ElRadioButton>
            <ElRadioButton label="card">
              <Icon icon="ep:grid" class="mr-2px" /> Kartalar
            </ElRadioButton>
          </ElRadioGroup>

          <div class="text-12px text-gray-500 font-medium">
            Jami: <span class="font-bold text-gray-900 dark:text-white">{{ filteredCompanies.length }}</span> ta korxona
          </div>
        </div>
      </div>
    </ElCard>

    <!-- 1. TABLE VIEW -->
    <ElCard v-if="viewMode === 'table'" shadow="never" class="main-table-card">
      <ElTable
        :data="filteredCompanies"
        v-loading="loading"
        style="width: 100%"
        stripe
        class="custom-company-table"
      >
        <!-- Company Info -->
        <ElTableColumn label="Kompaniya Nomi" min-width="240">
          <template #default="{ row }">
            <div class="flex items-center gap-12px py-4px cursor-pointer" @click="openDrilldownDrawer(row)">
              <div
                class="w-42px h-42px rounded-12px flex items-center justify-center font-bold text-white font-mono shadow-sm transition-transform hover:scale-105"
                :class="row.plan === 'pro' ? 'bg-gradient-to-br from-purple-500 via-indigo-600 to-blue-600' : 'bg-gradient-to-br from-blue-500 to-cyan-600'"
              >
                {{ (row.name || 'K').slice(0, 2).toUpperCase() }}
              </div>
              <div>
                <div class="font-bold text-14px text-gray-900 dark:text-white hover:text-blue-600 flex items-center gap-6px">
                  <span>{{ row.name }}</span>
                  <ElTag v-if="row.id === 'comp-default'" size="small" type="info" effect="plain" class="text-[10px]">
                    Asosiy Bosh Korxona
                  </ElTag>
                </div>
                <div class="text-11px text-gray-400 font-mono mt-2px">
                  Kodi: <span class="text-gray-700 dark:text-gray-300 font-semibold">{{ row.code }}</span> | ID: {{ row.id }}
                </div>
              </div>
            </div>
          </template>
        </ElTableColumn>

        <!-- Admin Account -->
        <ElTableColumn label="Admin Hisobi" min-width="160">
          <template #default="{ row }">
            <div class="flex items-center gap-6px">
              <ElTag size="small" type="primary" effect="light" class="font-mono font-semibold">
                @{{ row.admin_username || (row.id === 'comp-default' ? 'admin' : 'admin') }}
              </ElTag>
              <ElTooltip content="Admin login va parolini o'zgartirish" placement="top">
                <ElButton
                  size="small"
                  type="warning"
                  link
                  @click="openPasswordResetDialog(row)"
                >
                  <Icon icon="ep:key" class="text-14px" />
                </ElButton>
              </ElTooltip>
            </div>
            <div class="text-11px text-gray-400 mt-2px truncate">
              {{ row.admin_full_name || 'Kompaniya Administratori' }}
            </div>
          </template>
        </ElTableColumn>

        <!-- Tier / Plan -->
        <ElTableColumn label="Tarif (Tier)" width="150" align="center">
          <template #default="{ row }">
            <div v-if="row.plan === 'pro'" class="inline-flex items-center gap-4px px-10px py-4px rounded-full bg-purple-50 dark:bg-purple-950/60 border border-purple-300 dark:border-purple-800 text-purple-700 dark:text-purple-300 font-bold text-12px shadow-sm">
              <Icon icon="ep:medal" class="text-12px text-purple-600" />
              <span>PRO PLAN</span>
            </div>
            <div v-else class="inline-flex items-center gap-4px px-10px py-4px rounded-full bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300 font-semibold text-12px">
              <Icon icon="ep:shield" class="text-11px" />
              <span>BASIC</span>
            </div>
          </template>
        </ElTableColumn>

        <!-- Billing Cycle -->
        <ElTableColumn label="To'lov Davri" width="130" align="center">
          <template #default="{ row }">
            <ElTag :type="row.billing_cycle === 'yearly' ? 'success' : 'warning'" effect="light" class="font-semibold">
              <span class="inline-flex items-center gap-4px">
                <Icon :icon="row.billing_cycle === 'yearly' ? 'ep:calendar' : 'ep:timer'" class="text-11px" />
                <span>{{ row.billing_cycle === 'yearly' ? 'Yillik' : 'Oylik' }}</span>
              </span>
            </ElTag>
          </template>
        </ElTableColumn>

        <!-- Employee Quota & Count -->
        <ElTableColumn label="Xodimlar & Limit" min-width="190">
          <template #default="{ row }">
            <div>
              <div class="flex items-center justify-between text-12px font-medium mb-3px">
                <span class="inline-flex items-center gap-4px text-gray-700 dark:text-gray-300 font-mono">
                  <Icon icon="ep:user" class="text-12px text-gray-500" />
                  {{ row.employees_count || 0 }} / {{ row.max_users || 10 }} xodim
                </span>
                <span class="text-11px font-bold" :class="(row.employees_count || 0) >= (row.max_users || 10) ? 'text-red-500' : 'text-gray-500'">
                  {{ Math.min(100, Math.round(((row.employees_count || 0) / (row.max_users || 10)) * 100)) }}%
                </span>
              </div>
              <ElProgress
                :percentage="Math.min(100, Math.round(((row.employees_count || 0) / (row.max_users || 10)) * 100))"
                :status="(row.employees_count || 0) >= (row.max_users || 10) ? 'exception' : (row.employees_count || 0) > (row.max_users || 10) * 0.8 ? 'warning' : 'success'"
                :stroke-width="6"
                :show-text="false"
              />
              <div class="text-10px text-gray-400 mt-3px flex items-center gap-6px">
                <span>{{ row.workers_count || 0 }} ishchi</span>
                <span>•</span>
                <span>{{ row.users_count || 0 }} login tizimda</span>
              </div>
            </div>
          </template>
        </ElTableColumn>

        <!-- Inventory & Sales Metrics -->
        <ElTableColumn label="Ombor & Savdo" min-width="180">
          <template #default="{ row }">
            <div class="text-12px space-y-2px">
              <div class="text-gray-700 dark:text-gray-300 flex items-center gap-4px">
                <Icon icon="ep:goods" class="text-12px text-gray-500" /> Mahsulotlar: <span class="font-bold font-mono">{{ row.products_count || 0 }}</span> ta
              </div>
              <div class="text-gray-700 dark:text-gray-300 flex items-center gap-4px">
                <Icon icon="ep:money" class="text-12px text-emerald-600" /> Tushum: <span class="font-bold font-mono text-emerald-600">{{ formatMoney(row.total_revenue) }}</span> so'm
              </div>
            </div>
          </template>
        </ElTableColumn>

        <!-- Subscription Expiry -->
        <ElTableColumn label="Obuna Holati" min-width="160">
          <template #default="{ row }">
            <div>
              <div class="flex items-center gap-6px">
                <span
                  class="w-8px h-8px rounded-full"
                  :class="row.is_expired ? 'bg-red-500 animate-pulse' : row.status === 1 ? 'bg-emerald-500' : 'bg-gray-400'"
                ></span>
                <span :class="row.is_expired ? 'text-red-600 font-bold' : row.status === 1 ? 'text-emerald-600 font-semibold' : 'text-gray-500'" class="text-12px">
                  {{ row.is_expired ? 'Muddati tugagan' : row.status === 1 ? 'Faol obuna' : 'To\'xtatilgan' }}
                </span>
              </div>
              <div class="text-11px text-gray-400 font-mono mt-2px">
                {{ row.subscription_expires_at || 'Cheklovlarsiz' }}
              </div>
            </div>
          </template>
        </ElTableColumn>

        <!-- Status Switch -->
        <ElTableColumn label="Holati" width="95" align="center">
          <template #default="{ row }">
            <ElSwitch
              :model-value="row.status === 1"
              active-color="#10b981"
              inactive-color="#9ca3af"
              @change="(val: any) => handleToggleStatus(row, val ? 1 : 0)"
            />
          </template>
        </ElTableColumn>

        <!-- Actions -->
        <ElTableColumn label="Amallar" width="260" fixed="right">
          <template #default="{ row }">
            <div class="flex items-center gap-6px">
              <!-- Drilldown Button -->
              <ElTooltip content="Kompaniya ko'rsatkichlari va tahlili" placement="top">
                <ElButton
                  size="small"
                  type="primary"
                  class="font-semibold"
                  @click="openDrilldownDrawer(row)"
                >
                  <Icon icon="ep:data-analysis" class="mr-2px" /> Tahlil
                </ElButton>
              </ElTooltip>

              <!-- Password Reset Button -->
              <ElTooltip content="Admin parolini o'zgartirish" placement="top">
                <ElButton
                  size="small"
                  type="warning"
                  plain
                  @click="openPasswordResetDialog(row)"
                >
                  <Icon icon="ep:key" />
                </ElButton>
              </ElTooltip>

              <!-- Tier Button -->
              <ElTooltip content="Tarifni oshirish yoki muddatni uzaytirish" placement="top">
                <ElButton
                  size="small"
                  type="warning"
                  plain
                  @click="openTierDialog(row)"
                >
                  <Icon icon="ep:top" />
                </ElButton>
              </ElTooltip>

              <!-- Edit Button -->
              <ElButton
                size="small"
                type="info"
                plain
                @click="openEditDialog(row)"
              >
                <Icon icon="ep:edit" />
              </ElButton>

              <!-- Delete Button -->
              <ElButton
                size="small"
                type="danger"
                plain
                :disabled="row.id === 'comp-default'"
                @click="handleDeleteCompany(row)"
              >
                <Icon icon="ep:delete" />
              </ElButton>
            </div>
          </template>
        </ElTableColumn>
      </ElTable>
    </ElCard>

    <!-- 2. CARD / GRID VIEW -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-16px">
      <div
        v-for="comp in filteredCompanies"
        :key="comp.id"
        class="company-card bg-white dark:bg-gray-800 rounded-16px p-18px border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-lg transition-all relative overflow-hidden"
      >
        <!-- Top Pro Stripe -->
        <div
          v-if="comp.plan === 'pro'"
          class="absolute top-0 left-0 right-0 h-4px bg-gradient-to-r from-purple-500 via-indigo-500 to-pink-500"
        ></div>

        <!-- Header -->
        <div class="flex items-start justify-between mb-14px">
          <div class="flex items-center gap-10px">
            <div
              class="w-44px h-44px rounded-12px flex items-center justify-center font-bold text-white font-mono shadow-sm"
              :class="comp.plan === 'pro' ? 'bg-gradient-to-br from-purple-600 to-indigo-600' : 'bg-gradient-to-br from-blue-600 to-cyan-600'"
            >
              {{ (comp.name || 'K').slice(0, 2).toUpperCase() }}
            </div>
            <div>
              <div class="font-bold text-15px text-gray-900 dark:text-white leading-tight">
                {{ comp.name }}
              </div>
              <div class="text-11px text-gray-400 font-mono mt-2px">
                Kod: <span class="text-gray-600 dark:text-gray-300 font-semibold">{{ comp.code }}</span>
              </div>
            </div>
          </div>

          <div class="flex flex-col items-end gap-4px">
            <ElTag v-if="comp.plan === 'pro'" type="warning" effect="dark" class="font-bold text-11px rounded-full inline-flex items-center gap-3px">
              <Icon icon="ep:medal" class="text-10px" /> PRO PLAN
            </ElTag>
            <ElTag v-else type="info" effect="plain" class="font-semibold text-11px rounded-full inline-flex items-center gap-3px">
              <Icon icon="ep:shield" class="text-10px" /> BASIC
            </ElTag>
          </div>
        </div>

        <!-- Metrics Grid -->
        <div class="grid grid-cols-2 gap-10px p-12px rounded-12px bg-gray-50 dark:bg-gray-900/50 mb-14px">
          <div>
            <div class="text-11px text-gray-500">Xodimlar / Limit</div>
            <div class="text-16px font-bold text-gray-900 dark:text-white font-mono mt-2px">
              {{ comp.employees_count || 0 }} / {{ comp.max_users || 10 }}
            </div>
            <div class="text-10px text-gray-400 mt-2px">
              {{ comp.workers_count || 0 }} ishchi, {{ comp.users_count || 0 }} login
            </div>
          </div>
          <div>
            <div class="text-11px text-gray-500">Klaster Savdosi</div>
            <div class="text-15px font-bold text-emerald-600 font-mono mt-2px truncate">
              {{ formatMoney(comp.total_revenue) }} so'm
            </div>
            <div class="text-10px text-gray-400 mt-2px">
              {{ comp.products_count || 0 }} ta mahsulot omborda
            </div>
          </div>
        </div>

        <!-- Quota progress bar -->
        <div class="mb-14px">
          <div class="flex justify-between text-11px text-gray-500 mb-4px font-medium">
            <span>Xodimlar kvotasi bandligi</span>
            <span :class="(comp.employees_count || 0) >= (comp.max_users || 10) ? 'text-red-500 font-bold' : ''">
              {{ Math.min(100, Math.round(((comp.employees_count || 0) / (comp.max_users || 10)) * 100)) }}%
            </span>
          </div>
          <ElProgress
            :percentage="Math.min(100, Math.round(((comp.employees_count || 0) / (comp.max_users || 10)) * 100))"
            :status="(comp.employees_count || 0) >= (comp.max_users || 10) ? 'exception' : 'success'"
            :stroke-width="5"
            :show-text="false"
          />
        </div>

        <!-- Expiry & Status Footer -->
        <div class="flex items-center justify-between text-11px text-gray-500 pt-8px border-t border-gray-100 dark:border-gray-700/60 mb-14px">
          <div class="flex items-center gap-6px">
            <span
              class="w-7px h-7px rounded-full"
              :class="comp.is_expired ? 'bg-red-500 animate-pulse' : comp.status === 1 ? 'bg-emerald-500' : 'bg-gray-400'"
            ></span>
            <span>{{ comp.is_expired ? 'Obuna tugagan' : comp.subscription_expires_at ? `Muddat: ${comp.subscription_expires_at.slice(0, 10)}` : 'Cheklovlarsiz' }}</span>
          </div>
          <ElSwitch
            :model-value="comp.status === 1"
            size="small"
            active-color="#10b981"
            inactive-color="#9ca3af"
            @change="(val: any) => handleToggleStatus(comp, val ? 1 : 0)"
          />
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-8px">
          <ElButton
            type="primary"
            class="flex-1 font-semibold"
            @click="openDrilldownDrawer(comp)"
          >
            <Icon icon="ep:data-analysis" class="mr-4px" /> Boshqaruv Markazi
          </ElButton>
          <ElButton
            type="warning"
            plain
            @click="openTierDialog(comp)"
          >
            <Icon icon="ep:top" />
          </ElButton>
          <ElButton
            type="info"
            plain
            @click="openEditDialog(comp)"
          >
            <Icon icon="ep:edit" />
          </ElButton>
          <ElButton
            type="danger"
            plain
            :disabled="comp.id === 'comp-default'"
            @click="handleDeleteCompany(comp)"
          >
            <Icon icon="ep:delete" />
          </ElButton>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- 3. COMPREHENSIVE COMPANY DRILLDOWN & CONTROL DRAWER -->
    <!-- ============================================================== -->
    <ElDrawer
      v-model="drawerVisible"
      :size="drawerSize"
      destroy-on-close
      class="company-drilldown-drawer"
    >
      <template #header>
        <div v-if="currentCompanyDetail" class="flex items-center justify-between flex-wrap gap-12px w-full pr-12px">
          <div class="flex items-center gap-12px">
            <div
              class="w-48px h-48px rounded-14px flex items-center justify-center font-bold text-18px text-white font-mono shadow-md"
              :class="currentCompanyDetail.plan === 'pro' ? 'bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-600' : 'bg-gradient-to-br from-blue-600 to-cyan-600'"
            >
              {{ (currentCompanyDetail.name || 'K').slice(0, 2).toUpperCase() }}
            </div>
            <div>
              <div class="flex items-center gap-8px">
                <h2 class="text-18px font-extrabold text-gray-900 dark:text-white">
                  {{ currentCompanyDetail.name }}
                </h2>
                <ElTag v-if="currentCompanyDetail.plan === 'pro'" type="warning" effect="dark" class="font-bold">
                  <span class="inline-flex items-center gap-3px"><Icon icon="ep:medal" class="text-11px" /> PRO</span>
                </ElTag>
                <ElTag v-else type="info" effect="plain" class="font-semibold">
                  <span class="inline-flex items-center gap-3px"><Icon icon="ep:shield" class="text-11px" /> BASIC</span>
                </ElTag>
              </div>
              <div class="text-12px text-gray-400 font-mono mt-2px">
                ID: <span class="text-gray-700 dark:text-gray-300 font-semibold">{{ currentCompanyDetail.id }}</span> | 
                Kod: <span class="text-blue-600 dark:text-blue-400 font-bold">{{ currentCompanyDetail.code }}</span> | 
                To'lov: {{ currentCompanyDetail.billing_cycle === 'yearly' ? 'Yillik' : 'Oylik' }}
              </div>
            </div>
          </div>

          <div class="flex items-center gap-10px">
            <ElButton
              size="small"
              type="warning"
              plain
              @click="openTierDialog(currentCompanyDetail)"
            >
              <Icon icon="ep:top" class="mr-2px" /> Tarifni Oshirish
            </ElButton>
            <ElButton
              size="small"
              type="default"
              plain
              @click="refreshCurrentCompanyDetail"
              :loading="drawerLoading"
            >
              <Icon icon="ep:refresh" />
            </ElButton>
          </div>
        </div>
      </template>

      <!-- DRAWER BODY TABS -->
      <div v-if="currentCompanyDetail" v-loading="drawerLoading" class="p-4px">
        <ElTabs v-model="drawerActiveTab" class="drilldown-tabs">
          <!-- TAB 1: COMPANY OVERVIEW & ADMIN ACCOUNT -->
          <ElTabPane name="overview">
            <template #label>
              <span class="flex items-center gap-6px font-semibold">
                <Icon icon="ep:office-building" />
                <span>Kompaniya & Hisob</span>
              </span>
            </template>

            <!-- Admin Account Management Card -->
            <div class="mb-16px p-16px rounded-14px bg-gradient-to-r from-purple-50/70 via-indigo-50/50 to-blue-50/70 dark:from-purple-950/40 dark:via-indigo-950/30 dark:to-blue-950/40 border border-purple-200 dark:border-purple-800 shadow-sm">
              <div class="flex items-center justify-between flex-wrap gap-12px mb-12px">
                <div class="flex items-center gap-12px">
                  <div class="w-44px h-44px rounded-12px bg-gradient-to-br from-purple-600 to-indigo-600 text-white flex items-center justify-center shadow-md">
                    <Icon icon="ep:key" class="text-22px" />
                  </div>
                  <div>
                    <div class="flex items-center gap-8px">
                      <span class="text-15px font-extrabold text-gray-900 dark:text-white">Kompaniya Administrator Hisobi</span>
                      <ElTag size="small" type="success" effect="dark" class="font-bold">
                        <Icon icon="ep:circle-check" class="mr-2px" /> Faol
                      </ElTag>
                    </div>
                    <div class="text-12px text-gray-500 dark:text-gray-400 mt-2px font-mono">
                      Login: <span class="font-bold text-purple-700 dark:text-purple-300">@{{ currentCompanyDetail.admin_username || currentCompanyDetail.admin_user?.username || currentCompanyDetail.code }}</span>
                      <span v-if="currentCompanyDetail.admin_full_name || currentCompanyDetail.admin_user?.full_name" class="ml-8px text-gray-400 font-sans">
                        ({{ currentCompanyDetail.admin_full_name || currentCompanyDetail.admin_user?.full_name }})
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Action buttons for the admin account -->
                <div class="flex items-center gap-8px">
                  <ElButton
                    type="primary"
                    size="small"
                    class="font-semibold shadow-sm"
                    @click="openPasswordResetDialog(currentCompanyDetail)"
                  >
                    <Icon icon="ep:key" class="mr-4px" /> Parolni O'zgartirish
                  </ElButton>
                  <ElButton
                    type="warning"
                    size="small"
                    plain
                    class="font-semibold"
                    @click="openTierDialog(currentCompanyDetail)"
                  >
                    <Icon icon="ep:top" class="mr-4px" /> Tarifni Yangilash
                  </ElButton>
                </div>
              </div>

              <!-- Quick account details row -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-10px pt-10px border-t border-purple-100 dark:border-purple-900/60 text-12px">
                <div>
                  <span class="text-gray-400 block text-10px uppercase font-semibold">Tizimdagi Roli</span>
                  <span class="font-bold text-gray-800 dark:text-gray-200">Kompaniya Administratori</span>
                </div>
                <div>
                  <span class="text-gray-400 block text-10px uppercase font-semibold">Bog'langan Kod</span>
                  <span class="font-mono font-bold text-blue-600 dark:text-blue-400">{{ currentCompanyDetail.code }}</span>
                </div>
                <div>
                  <span class="text-gray-400 block text-10px uppercase font-semibold">Tarif Rejasi</span>
                  <span class="font-bold uppercase" :class="currentCompanyDetail.plan === 'pro' ? 'text-purple-600' : 'text-gray-700 dark:text-gray-300'">
                    {{ currentCompanyDetail.plan }} ({{ currentCompanyDetail.billing_cycle === 'yearly' ? 'Yillik' : 'Oylik' }})
                  </span>
                </div>
                <div>
                  <span class="text-gray-400 block text-10px uppercase font-semibold">Amal Qilish</span>
                  <span class="font-mono text-gray-700 dark:text-gray-300">
                    {{ currentCompanyDetail.subscription_expires_at ? currentCompanyDetail.subscription_expires_at.slice(0, 10) : 'Muddatsiz' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Aggregate Business Metrics Grid -->
            <h3 class="text-13px font-bold text-gray-800 dark:text-gray-200 mb-10px flex items-center gap-6px">
              <Icon icon="ep:pie-chart" class="text-blue-600" />
              <span>Kompaniya Asosiy Ko'rsatkichlari (Yig'ma Ma'lumotlar)</span>
            </h3>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-12px mb-18px">
              <div class="p-14px rounded-12px bg-blue-50/60 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800">
                <div class="flex items-center justify-between text-blue-600 mb-6px">
                  <span class="text-11px font-bold uppercase tracking-wider">Jamoa / Xodimlar</span>
                  <Icon icon="ep:user" class="text-16px" />
                </div>
                <div class="text-22px font-extrabold text-blue-800 dark:text-blue-300 font-mono">
                  {{ currentCompanyDetail.stats.employees_count }}
                  <span class="text-12px text-blue-500 font-normal">/ {{ currentCompanyDetail.stats.max_users }} ta</span>
                </div>
                <div class="text-10px text-blue-600/80 dark:text-blue-400 mt-4px">
                  Kompaniya ishchi xodimlari
                </div>
              </div>

              <div class="p-14px rounded-12px bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800">
                <div class="flex items-center justify-between text-emerald-600 mb-6px">
                  <span class="text-11px font-bold uppercase tracking-wider">Jami Tushum</span>
                  <Icon icon="ep:money" class="text-16px" />
                </div>
                <div class="text-20px font-extrabold text-emerald-800 dark:text-emerald-300 font-mono">
                  {{ formatMoney(currentCompanyDetail.stats.total_revenue) }}
                </div>
                <div class="text-10px text-emerald-600/80 dark:text-emerald-400 mt-4px">
                  {{ currentCompanyDetail.stats.total_sales_count }} ta savdo orqali
                </div>
              </div>

              <div class="p-14px rounded-12px bg-amber-50/60 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800">
                <div class="flex items-center justify-between text-amber-600 mb-6px">
                  <span class="text-11px font-bold uppercase tracking-wider">Qarzdorlik (Nasiya)</span>
                  <Icon icon="ep:wallet" class="text-16px" />
                </div>
                <div class="text-20px font-extrabold text-amber-800 dark:text-amber-300 font-mono">
                  {{ formatMoney(currentCompanyDetail.stats.total_debt) }}
                </div>
                <div class="text-10px text-amber-600/80 dark:text-amber-400 mt-4px">
                  {{ currentCompanyDetail.stats.debtors_count }} ta qarzdor mijoz
                </div>
              </div>

              <div class="p-14px rounded-12px bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800">
                <div class="flex items-center justify-between text-indigo-600 mb-6px">
                  <span class="text-11px font-bold uppercase tracking-wider">Ombor / Mahsulotlar</span>
                  <Icon icon="ep:goods" class="text-16px" />
                </div>
                <div class="text-22px font-extrabold text-indigo-800 dark:text-indigo-300 font-mono">
                  {{ currentCompanyDetail.stats.products_count }} <span class="text-12px font-normal text-indigo-500">xil</span>
                </div>
                <div class="text-10px text-indigo-600/80 dark:text-indigo-400 mt-4px font-mono">
                  Qiymati: {{ formatMoney(currentCompanyDetail.stats.inventory_value) }} so'm
                </div>
              </div>
            </div>

            <!-- Company Profile & Contact Info -->
            <div class="p-14px rounded-12px bg-gray-50 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700">
              <h4 class="text-12px font-bold text-gray-800 dark:text-gray-200 mb-8px flex items-center gap-6px">
                <Icon icon="ep:document" class="text-gray-500" />
                <span>Kompaniya Rekvizitlari</span>
              </h4>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-10px text-12px">
                <div>
                  <span class="text-gray-400 block text-11px">Telefon</span>
                  <span class="font-semibold text-gray-800 dark:text-gray-200">{{ currentCompanyDetail.phone || 'Kiritilmagan' }}</span>
                </div>
                <div>
                  <span class="text-gray-400 block text-11px">Email</span>
                  <span class="font-semibold text-gray-800 dark:text-gray-200">{{ currentCompanyDetail.email || 'Kiritilmagan' }}</span>
                </div>
                <div>
                  <span class="text-gray-400 block text-11px">Manzil</span>
                  <span class="font-semibold text-gray-800 dark:text-gray-200">{{ currentCompanyDetail.address || 'Kiritilmagan' }}</span>
                </div>
              </div>
            </div>
          </ElTabPane>

          <!-- TAB 4: EMPLOYEES (READ-ONLY MONITORING) -->
          <ElTabPane name="employees">
            <template #label>
              <span class="flex items-center gap-6px font-semibold">
                <Icon icon="ep:user" />
                <span>Xodimlar Monitoringi ({{ currentCompanyDetail.stats.employees_count }})</span>
              </span>
            </template>

            <!-- Read-only Alert explaining Super Admin's boundary -->
            <div class="mb-14px p-12px rounded-10px bg-blue-50/70 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 text-12px text-blue-800 dark:text-blue-300 flex items-center gap-8px">
              <Icon icon="ep:info-filled" class="text-16px shrink-0 text-blue-600" />
              <span>Super Administrator kompaniya xodimlarini bevosita boshqarmaydi. Bu yerda kompaniya tomonidan kiritilgan xodimlar va tizim foydalanuvchilari statistik maqsadlarda monitoring qilinadi.</span>
            </div>

            <!-- Filter workers bar -->
            <div class="flex items-center justify-between gap-10px mb-12px">
              <ElInput
                v-model="workerSearchQuery"
                placeholder="Xodim ismi, lavozimi yoki telefon..."
                clearable
                class="w-300px"
                size="small"
              >
                <template #prefix>
                  <Icon icon="ep:search" class="text-gray-400" />
                </template>
              </ElInput>
              <div class="text-12px text-gray-400">
                Topildi: <span class="font-bold text-gray-700 dark:text-gray-300">{{ filteredWorkers.length }}</span> ta
              </div>
            </div>

            <!-- Workers Table (NO CRUD buttons) -->
            <ElTable :data="filteredWorkers" stripe style="width: 100%" size="small" class="rounded-8px border border-gray-200 dark:border-gray-700">
              <ElTableColumn label="Ism & Kod" min-width="160">
                <template #default="{ row }">
                  <div class="font-bold text-gray-900 dark:text-white">{{ row.name }}</div>
                  <div class="text-10px text-gray-400 font-mono">Kod: {{ row.employee_code || row.id }}</div>
                </template>
              </ElTableColumn>

              <ElTableColumn label="Lavozim & Bo'lim" min-width="150">
                <template #default="{ row }">
                  <ElTag size="small" type="primary" effect="light" class="font-semibold">
                    {{ row.role || 'Mutaxassis' }}
                  </ElTag>
                  <div class="text-10px text-gray-500 mt-2px">{{ row.department || 'Bosh bo\'lim' }}</div>
                </template>
              </ElTableColumn>

              <ElTableColumn label="Telefon & Hisob" min-width="150">
                <template #default="{ row }">
                  <div class="text-11px text-gray-700 dark:text-gray-300">{{ row.phone || '-' }}</div>
                  <div class="text-10px text-gray-400 font-mono">Login: {{ row.account || '-' }}</div>
                </template>
              </ElTableColumn>

              <ElTableColumn label="Maosh (so'm)" width="130" align="right">
                <template #default="{ row }">
                  <span class="font-mono font-bold text-emerald-600">
                    {{ formatMoney(row.baseSalary) }}
                  </span>
                </template>
              </ElTableColumn>

              <ElTableColumn label="Ishga kirgan sana" width="130" align="center">
                <template #default="{ row }">
                  <span class="text-11px text-gray-500 font-mono">{{ row.hireDate || '-' }}</span>
                </template>
              </ElTableColumn>
            </ElTable>

            <!-- Login Users Table Section -->
            <div class="mt-20px">
              <h3 class="text-13px font-bold text-gray-800 dark:text-gray-200 mb-8px flex items-center gap-6px">
                <Icon icon="ep:key" class="text-indigo-500" />
                <span>Tizimga Kirish Hisoblari (Login Users: {{ currentCompanyDetail.users?.length || 0 }})</span>
              </h3>
              <ElTable :data="currentCompanyDetail.users || []" stripe style="width: 100%" size="small" class="rounded-8px border border-gray-200 dark:border-gray-700">
                <ElTableColumn label="Foydalanuvchi nomi" prop="username" min-width="140">
                  <template #default="{ row }">
                    <span class="font-bold text-gray-900 dark:text-white font-mono">{{ row.username }}</span>
                  </template>
                </ElTableColumn>
                <ElTableColumn label="To'liq ismi" prop="full_name" min-width="160" />
                <ElTableColumn label="Roli" prop="role" width="140">
                  <template #default="{ row }">
                    <ElTag size="small" type="success">{{ row.role }}</ElTag>
                  </template>
                </ElTableColumn>
                <ElTableColumn label="Email / Telefon" min-width="160">
                  <template #default="{ row }">
                    <span class="text-11px text-gray-500">{{ row.email || row.phone || '-' }}</span>
                  </template>
                </ElTableColumn>
              </ElTable>
            </div>
          </ElTabPane>

          <!-- TAB 2: FINANCIAL ANALYTICS & SALES -->
          <ElTabPane name="analytics">
            <template #label>
              <span class="flex items-center gap-6px font-semibold">
                <Icon icon="ep:data-line" />
                <span>Moliyaviy Tahlil & Savdo</span>
              </span>
            </template>

            <!-- 4 Financial Stat Cards -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-10px mb-16px">
              <div class="p-12px rounded-12px bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800">
                <div class="text-11px text-emerald-700 dark:text-emerald-400 font-medium">Jami Tushum</div>
                <div class="text-18px font-bold text-emerald-700 dark:text-emerald-300 font-mono mt-2px">
                  {{ formatMoney(currentCompanyDetail.stats.total_revenue) }} <span class="text-10px">so'm</span>
                </div>
              </div>

              <div class="p-12px rounded-12px bg-blue-50/60 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800">
                <div class="text-11px text-blue-700 dark:text-blue-400 font-medium">Jami Savdolar</div>
                <div class="text-18px font-bold text-blue-700 dark:text-blue-300 font-mono mt-2px">
                  {{ currentCompanyDetail.stats.total_sales_count }} ta
                </div>
              </div>

              <div class="p-12px rounded-12px bg-amber-50/60 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800">
                <div class="text-11px text-amber-700 dark:text-amber-400 font-medium">Qarzdorlik (Nasiya)</div>
                <div class="text-18px font-bold text-amber-700 dark:text-amber-300 font-mono mt-2px">
                  {{ formatMoney(currentCompanyDetail.stats.total_debt) }} <span class="text-10px">so'm</span>
                </div>
              </div>

              <div class="p-12px rounded-12px bg-purple-50/60 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800">
                <div class="text-11px text-purple-700 dark:text-purple-400 font-medium">Qarzdor Mijozlar</div>
                <div class="text-18px font-bold text-purple-700 dark:text-purple-300 font-mono mt-2px">
                  {{ currentCompanyDetail.stats.debtors_count }} ta
                </div>
              </div>
            </div>

            <!-- Recent Sales Table -->
            <div>
              <h3 class="text-13px font-bold text-gray-800 dark:text-gray-200 mb-8px flex items-center gap-6px">
                <Icon icon="ep:shopping-bag" class="text-emerald-500" />
                <span>Oxirgi Savdolar Tarixi</span>
              </h3>
              <ElTable :data="currentCompanyDetail.recent_sales || []" stripe style="width: 100%" size="small" class="rounded-8px border border-gray-200 dark:border-gray-700">
                <ElTableColumn label="Mijoz" prop="customer_name" min-width="140" />
                <ElTableColumn label="Telefon" prop="customer_phone" min-width="120" />
                <ElTableColumn label="Jami Summa" min-width="130" align="right">
                  <template #default="{ row }">
                    <span class="font-mono font-semibold">{{ formatMoney(row.total_amount) }} so'm</span>
                  </template>
                </ElTableColumn>
                <ElTableColumn label="To'langan" min-width="130" align="right">
                  <template #default="{ row }">
                    <span class="font-mono font-bold text-emerald-600">{{ formatMoney(row.paid_amount) }} so'm</span>
                  </template>
                </ElTableColumn>
                <ElTableColumn label="Nasiya" min-width="120" align="right">
                  <template #default="{ row }">
                    <span :class="row.debt_amount > 0 ? 'text-amber-600 font-bold' : 'text-gray-400'" class="font-mono">
                      {{ formatMoney(row.debt_amount) }}
                    </span>
                  </template>
                </ElTableColumn>
                <ElTableColumn label="Sana" prop="createTime" min-width="130" />
              </ElTable>
            </div>
          </ElTabPane>

          <!-- TAB 3: INVENTORY & PRODUCTS -->
          <ElTabPane name="inventory">
            <template #label>
              <span class="flex items-center gap-6px font-semibold">
                <Icon icon="ep:goods" />
                <span>Ombor & Mahsulotlar</span>
              </span>
            </template>

            <!-- Inventory Stats -->
            <div class="grid grid-cols-3 gap-10px mb-16px">
              <div class="p-12px rounded-12px bg-blue-50/60 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800">
                <div class="text-11px text-blue-700 dark:text-blue-400 font-medium">Mahsulot Turlari</div>
                <div class="text-20px font-bold text-blue-700 dark:text-blue-300 font-mono mt-2px">
                  {{ currentCompanyDetail.stats.products_count }} ta
                </div>
              </div>

              <div class="p-12px rounded-12px bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800">
                <div class="text-11px text-indigo-700 dark:text-indigo-400 font-medium">Jami Qoldiq Miqdori</div>
                <div class="text-20px font-bold text-indigo-700 dark:text-indigo-300 font-mono mt-2px">
                  {{ formatMoney(currentCompanyDetail.stats.total_stock) }}
                </div>
              </div>

              <div class="p-12px rounded-12px bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800">
                <div class="text-11px text-emerald-700 dark:text-emerald-400 font-medium">Omborning Umumiy Qiymati</div>
                <div class="text-20px font-bold text-emerald-700 dark:text-emerald-300 font-mono mt-2px">
                  {{ formatMoney(currentCompanyDetail.stats.inventory_value) }} <span class="text-11px">so'm</span>
                </div>
              </div>
            </div>

            <!-- Top Products Table -->
            <ElTable :data="currentCompanyDetail.top_products || []" stripe style="width: 100%" size="small" class="rounded-8px border border-gray-200 dark:border-gray-700">
              <ElTableColumn label="Mahsulot Nomi" prop="productName" min-width="160">
                <template #default="{ row }">
                  <span class="font-bold text-gray-900 dark:text-white">{{ row.productName }}</span>
                </template>
              </ElTableColumn>
              <ElTableColumn label="Kategoriya" prop="category" min-width="120" />
              <ElTableColumn label="Sotuv Narxi" min-width="120" align="right">
                <template #default="{ row }">
                  <span class="font-mono font-semibold">{{ formatMoney(row.price) }} so'm</span>
                </template>
              </ElTableColumn>
              <ElTableColumn label="Qoldiq" min-width="100" align="right">
                <template #default="{ row }">
                  <span class="font-mono font-bold text-blue-600">{{ row.stock }} {{ row.unit || 'dona' }}</span>
                </template>
              </ElTableColumn>
            </ElTable>
          </ElTabPane>

          <!-- TAB 4: PLAN, SUBSCRIPTION & CONFIGURATION -->
          <ElTabPane name="config">
            <template #label>
              <span class="flex items-center gap-6px font-semibold">
                <Icon icon="ep:setting" />
                <span>Tarif & Konfiguratsiya</span>
              </span>
            </template>

            <div class="p-10px space-y-16px">
              <!-- Tier Overview -->
              <div class="p-14px rounded-12px bg-gray-50 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700">
                <div class="flex items-center justify-between mb-10px">
                  <div>
                    <div class="text-14px font-bold text-gray-900 dark:text-white">
                      Hozirgi Tarif: <span class="uppercase text-purple-600 font-extrabold">{{ currentCompanyDetail.plan }}</span>
                    </div>
                    <div class="text-12px text-gray-500 font-mono mt-2px">
                      Amal qilish: {{ currentCompanyDetail.subscription_expires_at || 'Muddatsiz / Cheklovlarsiz' }}
                    </div>
                  </div>
                  <ElButton type="primary" size="small" class="gradient-btn font-semibold" @click="openTierDialog(currentCompanyDetail)">
                    Tarifni O'zgartirish
                  </ElButton>
                </div>
              </div>

              <!-- Feature Flags Status -->
              <div class="p-14px rounded-12px bg-gray-50 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700 space-y-10px">
                <h4 class="text-13px font-bold text-gray-800 dark:text-gray-200">
                  Faollashtirilgan Funksiyalar (Feature Flags)
                </h4>

                <div class="flex items-center justify-between py-6px border-b border-gray-200 dark:border-gray-700/60">
                  <div class="flex items-center gap-8px">
                    <Icon icon="ep:cpu" class="text-20px text-purple-600" />
                    <div>
                      <div class="text-12px font-bold text-gray-900 dark:text-white">AI Yordamchi & Aqlli Tahlil</div>
                      <div class="text-11px text-gray-500">Kassa va ombor bo'yicha aqlli yordamchi</div>
                    </div>
                  </div>
                  <ElTag :type="currentCompanyDetail.plan === 'pro' || currentCompanyDetail.features?.ai ? 'success' : 'info'">
                    {{ currentCompanyDetail.plan === 'pro' || currentCompanyDetail.features?.ai ? 'Yoqilgan' : 'O\'chirilgan' }}
                  </ElTag>
                </div>

                <div class="flex items-center justify-between py-6px border-b border-gray-200 dark:border-gray-700/60">
                  <div class="flex items-center gap-8px">
                    <Icon icon="ep:promotion" class="text-20px text-indigo-600" />
                    <div>
                      <div class="text-12px font-bold text-gray-900 dark:text-white">Yangi & Kelgusi Funksiyalar (Early Access)</div>
                      <div class="text-11px text-gray-500">Platformaga qo'shiladigan eng so'nggi imkoniyatlar</div>
                    </div>
                  </div>
                  <ElTag :type="currentCompanyDetail.plan === 'pro' || currentCompanyDetail.features?.upcoming ? 'warning' : 'info'">
                    {{ currentCompanyDetail.plan === 'pro' || currentCompanyDetail.features?.upcoming ? 'Ruxsat bor' : 'Bloklangan' }}
                  </ElTag>
                </div>

                <div class="flex items-center justify-between py-6px">
                  <div class="flex items-center gap-8px">
                    <Icon icon="ep:trend-charts" class="text-20px text-emerald-600" />
                    <div>
                      <div class="text-12px font-bold text-gray-900 dark:text-white">Kengaytirilgan Moliyaviy Prognoz</div>
                      <div class="text-11px text-gray-500">Chuqur tahliliy grafiklar va diagrammalar</div>
                    </div>
                  </div>
                  <ElTag :type="currentCompanyDetail.plan === 'pro' || currentCompanyDetail.features?.advanced_analytics ? 'success' : 'info'">
                    {{ currentCompanyDetail.plan === 'pro' || currentCompanyDetail.features?.advanced_analytics ? 'Mavjud' : 'Cheklangan' }}
                  </ElTag>
                </div>
              </div>
            </div>
          </ElTabPane>
        </ElTabs>
      </div>
    </ElDrawer>

    <!-- ============================================================== -->
    <!-- 4. CREATE / EDIT COMPANY DIALOG -->
    <!-- ============================================================== -->
    <ElDialog
      v-model="saveDialogVisible"
      :title="saveDialogType === 'add' ? 'Yangi Kompaniya Yaratish' : 'Kompaniya Ma\'lumotlarini Tahrirlash'"
      width="580px"
      destroy-on-close
    >
      <ElForm ref="saveFormRef" :model="companyForm" :rules="rules" label-position="top">
        <ElRow :gutter="14">
          <ElCol :span="14">
            <ElFormItem label="Kompaniya Nomi" prop="name">
              <ElInput v-model="companyForm.name" placeholder="Masalan: Alpha Textile MCHJ" />
            </ElFormItem>
          </ElCol>
          <ElCol :span="10">
            <ElFormItem label="Unikal Kodi (Slug)" prop="code">
              <ElInput v-model="companyForm.code" placeholder="masalan: alpha_textile" />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElRow :gutter="14">
          <ElCol :span="12">
            <ElFormItem label="Tanlangan Tarif (Tier)" prop="plan">
              <ElSelect v-model="companyForm.plan" class="w-full">
                <ElOption label="PRO (Barcha imkoniyatlar + AI)" value="pro" />
                <ElOption label="BASIC (Standart ERP, AI yo'q)" value="basic" />
              </ElSelect>
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="To'lov Davri" prop="billing_cycle">
              <ElSelect v-model="companyForm.billing_cycle" class="w-full">
                <ElOption label="Oylik to'lov" value="monthly" />
                <ElOption label="Yillik to'lov" value="yearly" />
              </ElSelect>
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElRow :gutter="14">
          <ElCol :span="12">
            <ElFormItem label="Xodimlar Limiti (Max Users)">
              <ElInputNumber v-model="companyForm.max_users" :min="1" :max="1000" class="w-full" />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="Telefon Raqami">
              <ElInput v-model="companyForm.phone" placeholder="+998 90 123 45 67" />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElRow :gutter="14">
          <ElCol :span="12">
            <ElFormItem label="Email">
              <ElInput v-model="companyForm.email" placeholder="info@company.uz" />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="Yuridik Manzil">
              <ElInput v-model="companyForm.address" placeholder="Toshkent sh., Chilonzor tumani..." />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <!-- Initial Admin Account for new company -->
        <div v-if="saveDialogType === 'add'" class="p-12px rounded-8px bg-blue-50/50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900/50 mt-10px">
          <div class="text-12px font-bold text-blue-800 dark:text-blue-300 mb-8px flex items-center gap-6px">
            <Icon icon="ep:user" /> Kompaniya Birinchi Administratori (Login)
          </div>
          <ElRow :gutter="10">
            <ElCol :span="12">
              <ElFormItem label="Admin Username" class="!mb-6px">
                <ElInput v-model="companyForm.admin_username" placeholder="masalan: alpha_admin" />
              </ElFormItem>
            </ElCol>
            <ElCol :span="12">
              <ElFormItem label="Admin Paroli" class="!mb-6px">
                <ElInput v-model="companyForm.admin_password" type="password" show-password placeholder="••••••••" />
              </ElFormItem>
            </ElCol>
          </ElRow>
        </div>
      </ElForm>

      <template #footer>
        <div class="flex justify-end gap-10px">
          <ElButton @click="saveDialogVisible = false">Bekor qilish</ElButton>
          <ElButton type="primary" :loading="saveLoading" @click="handleSaveSubmit">
            Saqlash
          </ElButton>
        </div>
      </template>
    </ElDialog>

    <!-- ============================================================== -->
    <!-- 4.1. COMPANY ADMIN PASSWORD RESET DIALOG -->
    <!-- ============================================================== -->
    <ElDialog
      v-model="passwordResetDialogVisible"
      title="Kompaniya Admin Hisobini Boshqarish va Parol Yangilash"
      width="500px"
      destroy-on-close
    >
      <div class="mb-16px p-14px rounded-12px bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-950/40 dark:to-indigo-950/40 border border-purple-200 dark:border-purple-800">
        <div class="flex items-center gap-10px">
          <div class="w-38px h-38px rounded-10px bg-purple-600 text-white flex items-center justify-center font-bold text-16px shadow-sm">
            <Icon icon="ep:key" class="text-20px" />
          </div>
          <div>
            <div class="text-15px font-bold text-gray-900 dark:text-white">
              {{ passwordResetForm.company_name }}
            </div>
            <div class="text-12px text-gray-500 font-mono mt-2px">
              Admin hisobi: <span class="font-bold text-purple-600">@{{ passwordResetForm.username || 'admin' }}</span>
            </div>
          </div>
        </div>
      </div>

      <ElForm :model="passwordResetForm" label-position="top">
        <ElFormItem label="Foydalanuvchi Nomi (Login)">
          <ElInput
            v-model="passwordResetForm.username"
            placeholder="Kompaniya admini logini"
          >
            <template #prefix>
              <Icon icon="ep:user" class="text-gray-400" />
            </template>
          </ElInput>
        </ElFormItem>

        <ElFormItem label="Admin To'liq Ismi">
          <ElInput
            v-model="passwordResetForm.full_name"
            placeholder="Masalan: Sardor Rahimov"
          >
            <template #prefix>
              <Icon icon="ep:avatar" class="text-gray-400" />
            </template>
          </ElInput>
        </ElFormItem>

        <ElFormItem label="Yangi Maxfiy Parol" required>
          <ElInput
            v-model="passwordResetForm.new_password"
            type="password"
            show-password
            placeholder="Yangi parolni kiriting (masalan: pass123)"
          >
            <template #prefix>
              <Icon icon="ep:lock" class="text-gray-400" />
            </template>
          </ElInput>
        </ElFormItem>
      </ElForm>

      <template #footer>
        <div class="flex justify-end gap-10px">
          <ElButton @click="passwordResetDialogVisible = false">Bekor qilish</ElButton>
          <ElButton
            type="primary"
            :loading="passwordResetLoading"
            @click="handlePasswordResetSubmit"
            class="gradient-btn font-semibold"
          >
            <Icon icon="ep:check" class="mr-4px" /> Parolni Yangilash
          </ElButton>
        </div>
      </template>
    </ElDialog>

    <!-- ============================================================== -->
    <!-- 5. RAISE TIER / SUBSCRIPTION MANAGEMENT DIALOG -->
    <!-- ============================================================== -->
    <ElDialog
      v-model="tierDialogVisible"
      title="Tarifni Oshirish va Obunani Boshqarish"
      width="600px"
      destroy-on-close
    >
      <div v-if="selectedCompanyForTier" class="company-tier-box">
        <div class="p-14px rounded-10px bg-gradient-to-r from-gray-50 to-blue-50/40 dark:from-gray-800 dark:to-blue-950/40 border border-gray-200 dark:border-gray-700 mb-16px flex items-center justify-between">
          <div>
            <div class="text-16px font-bold text-gray-900 dark:text-white">
              {{ selectedCompanyForTier.name }}
            </div>
            <div class="text-12px text-gray-500 font-mono mt-2px">
              Hozirgi tarif: <span class="font-bold uppercase text-purple-600">{{ selectedCompanyForTier.plan }}</span> | 
              Amal qilish muddati: {{ selectedCompanyForTier.subscription_expires_at || "Cheksiz" }}
            </div>
          </div>
          <ElTag :type="selectedCompanyForTier.plan === 'pro' ? 'warning' : 'info'" size="large" effect="dark" class="font-bold">
            {{ selectedCompanyForTier.plan.toUpperCase() }}
          </ElTag>
        </div>

        <!-- Tier Selection Cards -->
        <div class="grid grid-cols-2 gap-12px mb-16px">
          <!-- Basic Option -->
          <div
            class="tier-plan-card p-14px rounded-12px border-2 cursor-pointer transition-all"
            :class="tierForm.plan === 'basic' ? 'border-blue-500 bg-blue-50/20 dark:bg-blue-950/30' : 'border-gray-200 dark:border-gray-700 hover:border-gray-400'"
            @click="tierForm.plan = 'basic'; tierForm.feature_ai = false; tierForm.feature_upcoming = false; tierForm.feature_analytics = false"
          >
            <div class="flex items-center justify-between mb-8px">
              <span class="font-bold text-14px text-gray-900 dark:text-white">BASIC TARIF</span>
              <Icon v-if="tierForm.plan === 'basic'" icon="ep:circle-check-filled" class="text-blue-500 text-18px" />
            </div>
            <ul class="text-11px text-gray-500 dark:text-gray-400 space-y-4px">
              <li class="flex items-center gap-6px"><Icon icon="ep:check" class="text-emerald-500 text-12px" /> Mahsulotlar & Ombor boshqaruvi</li>
              <li class="flex items-center gap-6px"><Icon icon="ep:check" class="text-emerald-500 text-12px" /> Savdo & POS Kassa tizimi</li>
              <li class="flex items-center gap-6px"><Icon icon="ep:check" class="text-emerald-500 text-12px" /> Xodimlar & Ish haqi vedomosti</li>
              <li class="text-red-500 font-semibold flex items-center gap-6px"><Icon icon="ep:close" class="text-red-500 text-12px" /> AI Yordamchi cheklangan</li>
              <li class="text-red-500 font-semibold flex items-center gap-6px"><Icon icon="ep:close" class="text-red-500 text-12px" /> Yangi funksiyalarga kirish yo'q</li>
            </ul>
          </div>

          <!-- Pro Option -->
          <div
            class="tier-plan-card p-14px rounded-12px border-2 cursor-pointer transition-all relative overflow-hidden"
            :class="tierForm.plan === 'pro' ? 'border-purple-500 bg-purple-50/25 dark:bg-purple-950/30 shadow-md' : 'border-gray-200 dark:border-gray-700 hover:border-purple-300'"
            @click="tierForm.plan = 'pro'; tierForm.feature_ai = true; tierForm.feature_upcoming = true; tierForm.feature_analytics = true"
          >
            <div class="absolute top-0 right-0 bg-gradient-to-l from-purple-600 to-indigo-600 text-white text-[9px] font-bold px-8px py-2px rounded-bl-8px">
              TAVSIYA ETILADI
            </div>
            <div class="flex items-center justify-between mb-8px">
              <span class="font-bold text-14px text-purple-700 dark:text-purple-300 flex items-center gap-4px">
                <Icon icon="ep:medal" class="text-14px" /> PRO TARIF
              </span>
              <Icon v-if="tierForm.plan === 'pro'" icon="ep:circle-check-filled" class="text-purple-600 text-18px" />
            </div>
            <ul class="text-11px text-gray-600 dark:text-gray-300 space-y-4px">
              <li class="flex items-center gap-6px"><Icon icon="ep:check" class="text-emerald-500 text-12px" /> Barcha asosiy ERP imkoniyatlari</li>
              <li class="font-bold text-purple-600 dark:text-purple-400 flex items-center gap-6px"><Icon icon="ep:cpu" class="text-12px" /> To'liq AI Yordamchi</li>
              <li class="font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-6px"><Icon icon="ep:promotion" class="text-12px" /> Barcha yangi funksiyalar birinchi bo'lib</li>
              <li class="flex items-center gap-6px"><Icon icon="ep:check" class="text-emerald-500 text-12px" /> Kengaytirilgan chuqur tahlillar</li>
            </ul>
          </div>
        </div>

        <!-- Period, Duration & Max Users -->
        <div class="grid grid-cols-3 gap-12px mb-14px">
          <div>
            <label class="block text-12px font-bold text-gray-700 dark:text-gray-300 mb-6px">To'lov Tsikli</label>
            <ElSelect v-model="tierForm.billing_cycle" class="w-full">
              <ElOption label="Oylik to'lov" value="monthly" />
              <ElOption label="Yillik to'lov" value="yearly" />
            </ElSelect>
          </div>

          <div>
            <label class="block text-12px font-bold text-gray-700 dark:text-gray-300 mb-6px">Muddatni Uzaytirish</label>
            <ElSelect v-model="tierForm.duration_months" class="w-full">
              <ElOption label="+1 Oy" :value="1" />
              <ElOption label="+3 Oy" :value="3" />
              <ElOption label="+6 Oy" :value="6" />
              <ElOption label="+1 Yil" :value="12" />
            </ElSelect>
          </div>

          <div>
            <label class="block text-12px font-bold text-gray-700 dark:text-gray-300 mb-6px">Xodimlar Limiti</label>
            <ElInputNumber v-model="tierForm.max_users" :min="1" :max="1000" class="w-full" />
          </div>
        </div>

        <!-- Custom Feature Toggles -->
        <div class="p-12px rounded-10px bg-gray-50 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700">
          <div class="text-12px font-bold text-gray-800 dark:text-gray-200 mb-8px">
            Alohida Imkoniyatlar (Feature Flags)
          </div>
          <div class="flex items-center justify-between py-4px">
            <span class="text-12px text-gray-600 dark:text-gray-400 flex items-center gap-6px"><Icon icon="ep:cpu" class="text-purple-600 text-14px" /> AI Yordamchisi va Maslahatchi</span>
            <ElSwitch v-model="tierForm.feature_ai" />
          </div>
          <div class="flex items-center justify-between py-4px">
            <span class="text-12px text-gray-600 dark:text-gray-400 flex items-center gap-6px"><Icon icon="ep:promotion" class="text-indigo-600 text-14px" /> Yangi va Kelgusi Funksiyalar (Early Access)</span>
            <ElSwitch v-model="tierForm.feature_upcoming" />
          </div>
          <div class="flex items-center justify-between py-4px">
            <span class="text-12px text-gray-600 dark:text-gray-400 flex items-center gap-6px"><Icon icon="ep:trend-charts" class="text-emerald-600 text-14px" /> Kengaytirilgan Tahlil Grafikalari</span>
            <ElSwitch v-model="tierForm.feature_analytics" />
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-10px">
          <ElButton @click="tierDialogVisible = false">Bekor qilish</ElButton>
          <ElButton type="primary" :loading="tierLoading" @click="handleTierSubmit" class="gradient-btn font-semibold">
            Tarifni Saqlash
          </ElButton>
        </div>
      </template>
    </ElDialog>

    <!-- ============================================================== -->
    <!-- 6. ADD / EDIT EMPLOYEE IN COMPANY DIALOG -->
    <!-- ============================================================== -->
    <ElDialog
      v-model="employeeDialogVisible"
      :title="employeeDialogType === 'add' ? 'Kompaniyaga Yangi Xodim Qo\'shish' : 'Xodim Ma\'lumotlarini Tahrirlash'"
      width="520px"
      destroy-on-close
    >
      <ElForm ref="employeeFormRef" :model="employeeForm" :rules="employeeRules" label-position="top">
        <ElFormItem label="Xodim F.I.SH." prop="name">
          <ElInput v-model="employeeForm.name" placeholder="Masalan: Sardor Rustamov" />
        </ElFormItem>

        <ElRow :gutter="12">
          <ElCol :span="12">
            <ElFormItem label="Lavozimi" prop="role">
              <ElInput v-model="employeeForm.role" placeholder="masalan: Usta / Bichuvchi" />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="Bo'limi">
              <ElInput v-model="employeeForm.department" placeholder="masalan: Ishlab chiqarish" />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElRow :gutter="12">
          <ElCol :span="12">
            <ElFormItem label="Telefon Raqami">
              <ElInput v-model="employeeForm.phone" placeholder="+998 90 123 45 67" />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="Tizim Hisobi (Account)">
              <ElInput v-model="employeeForm.account" placeholder="masalan: sardor_r" />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElRow :gutter="12">
          <ElCol :span="12">
            <ElFormItem label="Oylik Maosh (so'm)">
              <ElInputNumber v-model="employeeForm.baseSalary" :min="0" :step="100000" class="w-full" />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="Ishga Kirgan Sana">
              <ElDatePicker
                v-model="employeeForm.hireDate"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="Tanlang"
                class="w-full"
              />
            </ElFormItem>
          </ElCol>
        </ElRow>
      </ElForm>

      <template #footer>
        <div class="flex justify-end gap-10px">
          <ElButton @click="employeeDialogVisible = false">Bekor qilish</ElButton>
          <ElButton type="primary" :loading="employeeLoading" @click="handleEmployeeSubmit">
            Saqlash
          </ElButton>
        </div>
      </template>
    </ElDialog>

    <!-- ============================================================== -->
    <!-- 7. MAIN COMPANY & SUPER ADMIN ACCOUNT MANAGEMENT DIALOG -->
    <!-- ============================================================== -->
    <ElDialog
      v-model="mainAccountDialogVisible"
      title="Bosh Korxona va Super Administrator Sozlamalari"
      width="640px"
      destroy-on-close
    >
      <ElForm :model="mainAccountForm" label-position="top" v-loading="mainAccountLoading">
        <div class="mb-14px p-12px rounded-10px bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-12px text-amber-800 dark:text-amber-200 flex items-center gap-8px">
          <Icon icon="ep:warning" class="text-18px shrink-0 text-amber-600" />
          <span>Bu yerda asosiy Super Administrator tizimga kirish akkaunti va Bosh korxona rekvizitlarini o'zgartirishingiz mumkin.</span>
        </div>

        <h4 class="text-13px font-bold text-gray-800 dark:text-gray-200 mb-10px flex items-center gap-6px">
          <Icon icon="ep:user" class="text-purple-600" /> Super Administrator Akkaunti
        </h4>

        <ElRow :gutter="14">
          <ElCol :span="12">
            <ElFormItem label="Foydalanuvchi Nomi (Login)">
              <ElInput v-model="mainAccountForm.admin_username" placeholder="admin" />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="Yangi Parol (Bo'sh qolsa o'zgarmaydi)">
              <ElInput v-model="mainAccountForm.admin_password" type="password" show-password placeholder="Yangi parol..." />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElRow :gutter="14">
          <ElCol :span="12">
            <ElFormItem label="Super Admin Ismi">
              <ElInput v-model="mainAccountForm.admin_full_name" placeholder="Administrator" />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="Telefon">
              <ElInput v-model="mainAccountForm.admin_phone" placeholder="+998..." />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElDivider class="my-16px" />

        <h4 class="text-13px font-bold text-gray-800 dark:text-gray-200 mb-10px flex items-center gap-6px">
          <Icon icon="ep:office-building" class="text-blue-600" /> Asosiy Bosh Korxona Ma'lumotlari
        </h4>

        <ElRow :gutter="14">
          <ElCol :span="14">
            <ElFormItem label="Bosh Korxona Nomi">
              <ElInput v-model="mainAccountForm.company_name" placeholder="Bosh Korxona" />
            </ElFormItem>
          </ElCol>
          <ElCol :span="10">
            <ElFormItem label="Korxona Kodi">
              <ElInput v-model="mainAccountForm.company_code" placeholder="default" />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElRow :gutter="14">
          <ElCol :span="12">
            <ElFormItem label="Korxona Telefoni">
              <ElInput v-model="mainAccountForm.company_phone" placeholder="+998..." />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="Korxona Emaili">
              <ElInput v-model="mainAccountForm.company_email" placeholder="info@korxona.uz" />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElFormItem label="Korxona Manzili">
          <ElInput v-model="mainAccountForm.company_address" placeholder="Toshkent sh..." />
        </ElFormItem>
      </ElForm>

      <template #footer>
        <div class="flex justify-end gap-10px">
          <ElButton @click="mainAccountDialogVisible = false">Bekor qilish</ElButton>
          <ElButton type="primary" :loading="mainAccountLoading" @click="handleSaveMainAccount" class="gradient-btn font-semibold">
            Saqlash
          </ElButton>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.gradient-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border: none;
}
.gradient-btn:hover {
  opacity: 0.92;
}
.stat-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover {
  transform: translateY(-2px);
}
.icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.tier-plan-card {
  user-select: none;
}
.company-card {
  transition: all 0.25s ease;
}
.company-card:hover {
  transform: translateY(-3px);
}
</style>
