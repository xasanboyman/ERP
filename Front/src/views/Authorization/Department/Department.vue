<script setup lang="tsx">
import { ContentWrap } from '@/components/ContentWrap'
import { Search } from '@/components/Search'
import { ResizeDialog } from '@/components/Dialog'
import { useI18n } from '@/hooks/web/useI18n'
import {
  ElTag,
  ElRadioGroup,
  ElRadioButton,
  ElDialog,
  ElTabs,
  ElTabPane,
  ElTable,
  ElTableColumn,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElMessageBox,
  ElTooltip
} from 'element-plus'
import { Icon } from '@/components/Icon'
import { Table } from '@/components/Table'
import {
  getDepartmentApi,
  getDepartmentTableApi,
  saveDepartmentApi,
  deleteDepartmentApi
} from '@/api/department'
import {
  getBranchStatisticsApi,
  saveBranchApi,
  deleteBranchApi,
  type BranchWithStats,
  type BranchType
} from '@/api/branch'
import type { DepartmentItem } from '@/api/department/types'
import { useTable } from '@/hooks/web/useTable'
import { ref, unref, reactive, computed, onMounted } from 'vue'
import Write from './components/Write.vue'
import Detail from './components/Detail.vue'
import { CrudSchema, useCrudSchemas } from '@/hooks/web/useCrudSchemas'
import { BaseButton } from '@/components/Button'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const dialogInitWidth = Math.min(window.innerWidth * 0.92, 1400)
const dialogInitHeight = Math.min(window.innerHeight * 0.88, 800)

const ids = ref<string[]>([])

const { tableRegister, tableState, tableMethods } = useTable({
  fetchDataApi: async () => {
    const { currentPage, pageSize } = tableState
    const res = await getDepartmentTableApi({
      pageIndex: unref(currentPage),
      pageSize: unref(pageSize),
      ...unref(searchParams)
    })
    return {
      list: res.data.list,
      total: res.data.total
    }
  },
  fetchDelApi: async () => {
    const res = await deleteDepartmentApi(unref(ids))
    return !!res
  }
})
const { loading, dataList, total, currentPage, pageSize } = tableState
const { getList, getElTableExpose, delList } = tableMethods

useRealtimeSync('department', () => {
  getList()
})

const searchParams = ref({})
const setSearchParams = (params: any) => {
  searchParams.value = params
  getList()
}

const { t } = useI18n()

const crudSchemas = reactive<CrudSchema[]>([
  {
    field: 'selection',
    search: {
      hidden: true
    },
    form: {
      hidden: true
    },
    detail: {
      hidden: true
    },
    table: {
      type: 'selection'
    }
  },
  {
    field: 'index',
    label: t('tableDemo.index'),
    type: 'index',
    search: {
      hidden: true
    },
    form: {
      hidden: true
    },
    detail: {
      hidden: true
    }
  },
  {
    field: 'departmentName',
    label: "Bo'lim / Filial Nomi",
    table: {
      slots: {
        default: (data: any) => {
          return (
            <span class="font-bold text-[var(--el-text-color-primary)]">
              {data.row.departmentName}
            </span>
          )
        }
      }
    },
    form: {
      component: 'Input',
      componentProps: {
        placeholder: "Bo'lim yoki filial nomini kiriting (masalan: Bosh Bo'lim, Chorsu Filiali...)"
      },
      colProps: {
        span: 24
      }
    },
    detail: {
      slots: {
        default: (data: any) => {
          return <>{data.departmentName}</>
        }
      }
    }
  },
  {
    field: 'parentId',
    label: "Yuqori Bo'lim (Ota bo'lim)",
    search: {
      hidden: true
    },
    form: {
      component: 'TreeSelect',
      componentProps: {
        nodeKey: 'id',
        checkStrictly: true,
        props: {
          label: 'departmentName',
          children: 'children'
        },
        placeholder: 'Tanlang (ixtiyoriy)'
      },
      optionApi: async () => {
        const res = await getDepartmentApi()
        return res.data.list
      },
      colProps: {
        span: 24
      }
    },
    detail: {
      hidden: true
    }
  },
  {
    field: 'status',
    label: t('userDemo.status'),
    search: {
      hidden: true
    },
    table: {
      slots: {
        default: (data: any) => {
          const status = data.row.status
          return (
            <>
              <ElTag type={status === 0 ? 'danger' : 'success'}>
                {status === 1 ? t('userDemo.enable') : t('userDemo.disable')}
              </ElTag>
            </>
          )
        }
      }
    },
    form: {
      component: 'Select',
      componentProps: {
        options: [
          {
            value: 1,
            label: t('userDemo.enable')
          },
          {
            value: 0,
            label: t('userDemo.disable')
          }
        ]
      },
      colProps: {
        span: 24
      }
    },
    detail: {
      slots: {
        default: (data: any) => {
          return (
            <>
              <ElTag type={data.status === 0 ? 'danger' : 'success'}>
                {data.status === 1 ? t('userDemo.enable') : t('userDemo.disable')}
              </ElTag>
            </>
          )
        }
      }
    }
  },
  {
    field: 'createTime',
    label: t('tableDemo.displayTime'),
    search: {
      hidden: true
    },
    form: {
      hidden: true
    }
  },
  {
    field: 'remark',
    label: t('userDemo.remark'),
    search: {
      hidden: true
    },
    form: {
      component: 'Input',
      componentProps: {
        type: 'textarea',
        rows: 3,
        placeholder: 'Izoh yozing...'
      },
      colProps: {
        span: 24
      }
    },
    detail: {
      slots: {
        default: (data: any) => {
          return <>{data.remark}</>
        }
      }
    }
  },
  {
    field: 'action',
    minWidth: '200px',
    width: '200px',
    label: t('tableDemo.action'),
    search: {
      hidden: true
    },
    form: {
      hidden: true
    },
    detail: {
      hidden: true
    },
    table: {
      slots: {
        default: (data: any) => {
          return (
            <div class="flex items-center gap-6px flex-nowrap whitespace-nowrap">
              <BaseButton type="primary" size="small" onClick={() => action(data.row, 'edit')}>
                {t('exampleDemo.edit')}
              </BaseButton>
              <BaseButton type="success" size="small" onClick={() => action(data.row, 'detail')}>
                {t('exampleDemo.detail')}
              </BaseButton>
              <BaseButton type="danger" size="small" onClick={() => delData(data.row)}>
                {t('exampleDemo.del')}
              </BaseButton>
            </div>
          )
        }
      }
    }
  }
])

// @ts-ignore
const { allSchemas } = useCrudSchemas(crudSchemas)

const dialogVisible = ref(false)
const dialogTitle = ref('')

const currentRow = ref<DepartmentItem | null>(null)
const actionType = ref('')

const AddAction = () => {
  dialogTitle.value = t('exampleDemo.add')
  currentRow.value = {
    status: 1
  } as any
  dialogVisible.value = true
  actionType.value = ''
}

const delLoading = ref(false)

const delData = async (row: DepartmentItem | null) => {
  const elTableExpose = await getElTableExpose()
  ids.value = row
    ? [row.id]
    : elTableExpose?.getSelectionRows().map((v: DepartmentItem) => v.id) || []
  delLoading.value = true
  await delList(unref(ids).length).finally(() => {
    delLoading.value = false
  })
}

const action = (row: DepartmentItem, type: string) => {
  dialogTitle.value = t(type === 'edit' ? 'exampleDemo.edit' : 'exampleDemo.detail')
  actionType.value = type
  currentRow.value = row
  dialogVisible.value = true
}

const writeRef = ref<ComponentRef<typeof Write>>()

const saveLoading = ref(false)

const save = async () => {
  const write = unref(writeRef)
  const formData = await write?.submit()
  if (formData) {
    saveLoading.value = true
    const res = await saveDepartmentApi(formData)
      .catch(() => {})
      .finally(() => {
        saveLoading.value = false
      })
    if (res) {
      dialogVisible.value = false
      currentPage.value = 1
      getList()
    }
  }
}

// ==================== BRANCH MANAGEMENT & STATISTICS ====================
const currentMainTab = ref<'branches' | 'departments'>('branches')
const branchStatsList = ref<BranchWithStats[]>([])
const branchLoading = ref(false)
const branchSearchQuery = ref('')

const loadBranchStatistics = async () => {
  branchLoading.value = true
  try {
    const res = await getBranchStatisticsApi()
    if (res && res.data) {
      branchStatsList.value = res.data
    }
  } catch (err) {
    console.error('Failed to load branch statistics:', err)
  } finally {
    branchLoading.value = false
  }
}

onMounted(() => {
  loadBranchStatistics()
})

useRealtimeSync(['branch', 'worker', 'product', 'sale'], () => {
  loadBranchStatistics()
})

const filteredBranches = computed(() => {
  if (!branchSearchQuery.value.trim()) return branchStatsList.value
  const q = branchSearchQuery.value.toLowerCase()
  return branchStatsList.value.filter(
    (b) =>
      (b.name && b.name.toLowerCase().includes(q)) ||
      (b.code && b.code.toLowerCase().includes(q)) ||
      (b.address && b.address.toLowerCase().includes(q))
  )
})

// Branch Drilldown Detail Dialog
const detailDialogVisible = ref(false)
const selectedBranch = ref<BranchWithStats | null>(null)
const detailActiveTab = ref<'workers' | 'products' | 'income'>('workers')

const openBranchDetail = (branch: BranchWithStats) => {
  selectedBranch.value = branch
  detailActiveTab.value = 'workers'
  detailDialogVisible.value = true
}

// Branch Form Add/Edit Dialog
const branchFormVisible = ref(false)
const branchFormLoading = ref(false)
const branchFormTitle = ref('')
const branchFormData = reactive<BranchType>({
  id: undefined,
  name: '',
  code: '',
  address: '',
  phone: '',
  is_active: 1
})

const openAddBranch = () => {
  branchFormTitle.value = "Yangi filial qo'shish"
  branchFormData.id = undefined
  branchFormData.name = ''
  branchFormData.code = ''
  branchFormData.address = ''
  branchFormData.phone = ''
  branchFormData.is_active = 1
  branchFormVisible.value = true
}

const openEditBranch = (b: BranchWithStats) => {
  branchFormTitle.value = 'Filialni tahrirlash'
  branchFormData.id = b.id
  branchFormData.name = b.name
  branchFormData.code = b.code || ''
  branchFormData.address = b.address || ''
  branchFormData.phone = b.phone || ''
  branchFormData.is_active = b.is_active ?? 1
  branchFormVisible.value = true
}

const submitBranchForm = async () => {
  if (!branchFormData.name.trim()) {
    ElMessage.warning('Filial nomini kiriting')
    return
  }
  branchFormLoading.value = true
  try {
    const res = await saveBranchApi(branchFormData)
    if (res && res.code === 0) {
      ElMessage.success(res.message || 'Filial saqlandi')
      branchFormVisible.value = false
      loadBranchStatistics()
    }
  } catch (e: any) {
    ElMessage.error(e?.message || 'Xatolik yuz berdi')
  } finally {
    branchFormLoading.value = false
  }
}

const confirmDeleteBranch = (b: BranchWithStats) => {
  ElMessageBox.confirm(
    `"${b.name}" filialini o'chirishni tasdiqlaysizmi?`,
    "Filialni o'chirish",
    {
      confirmButtonText: "O'chirish",
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(async () => {
      try {
        const res = await deleteBranchApi(b.id!)
        if (res && res.code === 0) {
          ElMessage.success("Filial o'chirildi")
          loadBranchStatistics()
        }
      } catch (e: any) {
        ElMessage.error(e?.message || "O'chirishda xatolik yuz berdi")
      }
    })
    .catch(() => {})
}
</script>

<template>
  <div class="mb-16px flex items-center justify-between flex-wrap gap-12px">
    <ElRadioGroup v-model="currentMainTab" size="large">
      <ElRadioButton label="branches">
        <Icon icon="ep:office-building" class="mr-6px" /> Filiallar & Statistika
      </ElRadioButton>
      <ElRadioButton label="departments">
        <Icon icon="ep:folder" class="mr-6px" /> Bo'limlar tuzilmasi
      </ElRadioButton>
    </ElRadioGroup>

    <div v-if="currentMainTab === 'branches'" class="flex items-center gap-10px flex-wrap">
      <ElInput
        v-model="branchSearchQuery"
        placeholder="Filial qidirish..."
        clearable
        class="!w-240px"
        prefix-icon="ep:search"
      />
      <BaseButton type="primary" @click="openAddBranch">
        <Icon icon="ep:plus" class="mr-4px" /> Filial qo'shish
      </BaseButton>
      <BaseButton :loading="branchLoading" @click="loadBranchStatistics">
        <Icon icon="ep:refresh" class="mr-4px" /> Yangilash
      </BaseButton>
    </div>
  </div>

  <!-- ==================== TAB 1: FILIALLAR & STATISTIKA ==================== -->
  <div v-if="currentMainTab === 'branches'" class="space-y-16px">
    <!-- Empty State -->
    <div
      v-if="!branchLoading && filteredBranches.length === 0"
      class="p-40px text-center rounded-16px border border-dashed border-slate-300 dark:border-slate-700 bg-white dark:bg-[#1e293b]"
    >
      <div class="text-48px text-slate-300 mb-12px">
        <Icon icon="ep:office-building" />
      </div>
      <p class="text-16px font-semibold text-slate-600 dark:text-slate-300 mb-6px">
        Filiallar topilmadi
      </p>
      <p class="text-13px text-slate-400 mb-16px">
        Kompaniyangiz uchun yangi filial qo'shing va uning individual statistikasini kuzatib boring.
      </p>
      <BaseButton type="primary" @click="openAddBranch">
        <Icon icon="ep:plus" class="mr-4px" /> Filial qo'shish
      </BaseButton>
    </div>

    <!-- Branch Cards Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-16px">
      <div
        v-for="b in filteredBranches"
        :key="b.id"
        class="p-16px rounded-16px border border-slate-200 dark:border-slate-700/70 bg-white dark:bg-[#1e293b] shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
      >
        <!-- Card Header -->
        <div>
          <div class="flex items-start justify-between gap-10px mb-12px">
            <div class="flex items-center gap-10px">
              <div
                class="w-40px h-40px rounded-12px bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-18px"
              >
                <Icon icon="ep:office-building" />
              </div>
              <div>
                <h3 class="text-16px font-bold text-slate-800 dark:text-slate-100 flex items-center gap-6px">
                  {{ b.name }}
                  <ElTag v-if="b.code" size="small" type="info" class="font-mono">{{ b.code }}</ElTag>
                </h3>
                <p class="text-12px text-slate-400 flex items-center gap-4px mt-2px">
                  <Icon icon="ep:location" /> {{ b.address || "Manzil ko'rsatilmagan" }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-6px">
              <ElTag :type="b.is_active ? 'success' : 'danger'" size="small">
                {{ b.is_active ? 'Faol' : 'Nofaol' }}
              </ElTag>
              <BaseButton size="small" type="default" circle @click="openEditBranch(b)">
                <Icon icon="ep:edit" />
              </BaseButton>
              <BaseButton size="small" type="danger" circle @click="confirmDeleteBranch(b)">
                <Icon icon="ep:delete" />
              </BaseButton>
            </div>
          </div>

          <div class="h-1px bg-slate-100 dark:bg-slate-700/50 mb-14px" />

          <!-- Branch Statistics Blocks -->
          <div class="space-y-10px mb-14px">
            <!-- 1. Employees Info -->
            <div
              class="p-10px rounded-10px bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50"
            >
              <div class="flex items-center justify-between text-13px mb-4px">
                <span class="text-slate-500 dark:text-slate-400 flex items-center gap-6px font-medium">
                  <Icon icon="ep:user" class="text-blue-500" /> Xodimlar
                </span>
                <span class="font-bold text-slate-700 dark:text-slate-200">
                  {{ b.statistics?.employees?.count || 0 }} nafar
                  <span class="text-xs text-green-500 font-normal">
                    ({{ b.statistics?.employees?.active_count || 0 }} faol)
                  </span>
                </span>
              </div>
              <div class="flex items-center justify-between text-12px text-slate-400">
                <span>Oylik maosh fondi:</span>
                <span class="font-semibold text-slate-600 dark:text-slate-300">
                  {{ (b.statistics?.employees?.total_salary || 0).toLocaleString() }} so'm
                </span>
              </div>
            </div>

            <!-- 2. Products / Inventory Info -->
            <div
              class="p-10px rounded-10px bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50"
            >
              <div class="flex items-center justify-between text-13px mb-4px">
                <span class="text-slate-500 dark:text-slate-400 flex items-center gap-6px font-medium">
                  <Icon icon="ep:goods" class="text-amber-500" /> Mahsulotlar & Ombor
                </span>
                <span class="font-bold text-slate-700 dark:text-slate-200">
                  {{ b.statistics?.products?.count || 0 }} turdagi
                </span>
              </div>
              <div class="flex items-center justify-between text-12px text-slate-400 mb-2px">
                <span>Ombordagi qoldiq:</span>
                <span class="font-semibold text-slate-600 dark:text-slate-300">
                  {{ (b.statistics?.products?.total_quantity || 0).toLocaleString() }} dona
                </span>
              </div>
              <div class="flex items-center justify-between text-12px text-slate-400">
                <span>Umumiy qiymati:</span>
                <span class="font-semibold text-emerald-600 dark:text-emerald-400">
                  {{ (b.statistics?.products?.total_inventory_value || 0).toLocaleString() }} so'm
                </span>
              </div>
            </div>

            <!-- 3. Income / Sales Info -->
            <div
              class="p-10px rounded-10px bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50"
            >
              <div class="flex items-center justify-between text-13px mb-4px">
                <span class="text-slate-500 dark:text-slate-400 flex items-center gap-6px font-medium">
                  <Icon icon="ep:coin" class="text-emerald-500" /> Savdo Tushumi
                </span>
                <span class="font-bold text-emerald-600 dark:text-emerald-400">
                  {{ (b.statistics?.income?.total_revenue || 0).toLocaleString() }} so'm
                </span>
              </div>
              <div class="flex items-center justify-between text-12px text-slate-400 mb-2px">
                <span>Savdolar soni:</span>
                <span class="font-semibold text-slate-600 dark:text-slate-300">
                  {{ b.statistics?.income?.total_sales_count || 0 }} ta chek
                </span>
              </div>
              <div class="flex items-center justify-between text-12px text-slate-400">
                <span>O'rtacha chek:</span>
                <span class="font-semibold text-slate-600 dark:text-slate-300">
                  {{ (b.statistics?.income?.average_check || 0).toLocaleString() }} so'm
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Action -->
        <div class="pt-10px border-t border-slate-100 dark:border-slate-700/50">
          <BaseButton type="primary" class="w-full !rounded-8px" @click="openBranchDetail(b)">
            <Icon icon="ep:data-analysis" class="mr-6px" /> Batafsil Statistika & Ro'yxat
          </BaseButton>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== TAB 2: BO'LIMLAR TUZILMASI ==================== -->
  <ContentWrap v-else>
    <Search :schema="allSchemas.searchSchema" @search="setSearchParams" @reset="setSearchParams" />

    <div class="mb-10px flex gap-8px">
      <BaseButton type="primary" @click="AddAction">{{ t('exampleDemo.add') }}</BaseButton>
      <BaseButton :loading="delLoading" type="danger" @click="delData(null)">
        {{ t('exampleDemo.del') }}
      </BaseButton>
    </div>

    <Table
      v-model:pageSize="pageSize"
      v-model:currentPage="currentPage"
      :columns="allSchemas.tableColumns"
      :data="dataList"
      :loading="loading"
      :pagination="{
        total: total
      }"
      @register="tableRegister"
    />
  </ContentWrap>

  <!-- ==================== DRILLDOWN DETAIL DIALOG ==================== -->
  <ElDialog
    v-model="detailDialogVisible"
    :title="`Filial Statistikasi: ${selectedBranch?.name || ''}`"
    width="85%"
    top="5vh"
    destroy-on-close
  >
    <div v-if="selectedBranch" class="space-y-16px">
      <!-- Quick Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-12px">
        <div
          class="p-12px rounded-10px bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800"
        >
          <div class="text-12px text-blue-500 font-medium">Xodimlar Soni</div>
          <div class="text-20px font-bold text-blue-700 dark:text-blue-300 mt-4px">
            {{ selectedBranch.statistics?.employees?.count || 0 }} nafar
          </div>
          <div class="text-11px text-blue-400 mt-2px">
            Oylik fond: {{ (selectedBranch.statistics?.employees?.total_salary || 0).toLocaleString() }} so'm
          </div>
        </div>
        <div
          class="p-12px rounded-10px bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800"
        >
          <div class="text-12px text-amber-500 font-medium">Mahsulot Turlari</div>
          <div class="text-20px font-bold text-amber-700 dark:text-amber-300 mt-4px">
            {{ selectedBranch.statistics?.products?.count || 0 }} tur
          </div>
          <div class="text-11px text-amber-400 mt-2px">
            Qoldiq: {{ (selectedBranch.statistics?.products?.total_quantity || 0).toLocaleString() }} dona
          </div>
        </div>
        <div
          class="p-12px rounded-10px bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800"
        >
          <div class="text-12px text-emerald-500 font-medium">Ombor Qiymati</div>
          <div class="text-20px font-bold text-emerald-700 dark:text-emerald-300 mt-4px">
            {{ (selectedBranch.statistics?.products?.total_inventory_value || 0).toLocaleString() }} so'm
          </div>
          <div class="text-11px text-emerald-400 mt-2px">
            Kam qolganlar: {{ selectedBranch.statistics?.products?.low_stock_count || 0 }} ta
          </div>
        </div>
        <div
          class="p-12px rounded-10px bg-purple-50 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-800"
        >
          <div class="text-12px text-purple-500 font-medium">Jami Tushum</div>
          <div class="text-20px font-bold text-purple-700 dark:text-purple-300 mt-4px">
            {{ (selectedBranch.statistics?.income?.total_revenue || 0).toLocaleString() }} so'm
          </div>
          <div class="text-11px text-purple-400 mt-2px">
            {{ selectedBranch.statistics?.income?.total_sales_count || 0 }} ta savdo cheki
          </div>
        </div>
      </div>

      <!-- Detail Tabs -->
      <ElTabs v-model="detailActiveTab">
        <ElTabPane label="Xodimlar Ro'yxati" name="workers">
          <ElTable :data="selectedBranch.statistics?.employees?.list || []" stripe border style="width: 100%">
            <ElTableColumn prop="name" label="Xodim Ismi" min-width="140" />
            <ElTableColumn prop="role" label="Lavozimi" min-width="120" />
            <ElTableColumn prop="phone" label="Telefon" min-width="120" />
            <ElTableColumn prop="baseSalary" label="Oylik Maoshi" min-width="120">
              <template #default="{ row }">
                <span class="font-semibold">{{ (row.baseSalary || 0).toLocaleString() }} so'm</span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="status" label="Holati" width="100">
              <template #default="{ row }">
                <ElTag :type="row.status === 1 ? 'success' : 'info'" size="small">
                  {{ row.status === 1 ? 'Faol' : 'Nofaol' }}
                </ElTag>
              </template>
            </ElTableColumn>
          </ElTable>
        </ElTabPane>

        <ElTabPane label="Mahsulotlar & Ombor" name="products">
          <ElTable :data="selectedBranch.statistics?.products?.list || []" stripe border style="width: 100%">
            <ElTableColumn prop="productName" label="Mahsulot Nomi" min-width="160" />
            <ElTableColumn prop="category" label="Kategoriya" min-width="120" />
            <ElTableColumn prop="price" label="Sotuv Narxi" min-width="120">
              <template #default="{ row }">
                <span class="font-semibold">{{ (row.price || 0).toLocaleString() }} so'm</span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="quantityInStock" label="Ombordagi Qoldiq" min-width="120">
              <template #default="{ row }">
                <ElTag :type="(row.quantityInStock || 0) <= 5 ? 'danger' : 'success'" size="small">
                  {{ (row.quantityInStock || 0).toLocaleString() }} {{ row.unit || 'dona' }}
                </ElTag>
              </template>
            </ElTableColumn>
          </ElTable>
        </ElTabPane>

        <ElTabPane label="Savdolar va Tushumlar" name="income">
          <div
            class="mb-10px flex items-center justify-between flex-wrap gap-8px text-13px p-10px rounded-8px bg-slate-50 dark:bg-slate-800"
          >
            <div>
              <span class="text-slate-400">Naqd / Karta to'langan: </span>
              <span class="font-bold text-emerald-600">
                {{ (selectedBranch.statistics?.income?.total_paid || 0).toLocaleString() }} so'm
              </span>
            </div>
            <div>
              <span class="text-slate-400">Nasiya (Qarz): </span>
              <span class="font-bold text-amber-600">
                {{ (selectedBranch.statistics?.income?.total_debt || 0).toLocaleString() }} so'm
              </span>
            </div>
            <div>
              <span class="text-slate-400">O'rtacha chek: </span>
              <span class="font-bold text-blue-600">
                {{ (selectedBranch.statistics?.income?.average_check || 0).toLocaleString() }} so'm
              </span>
            </div>
          </div>
          <ElTable :data="selectedBranch.statistics?.income?.recent_sales || []" stripe border style="width: 100%">
            <ElTableColumn prop="receipt_number" label="Chek raqami" min-width="140" />
            <ElTableColumn prop="total_amount" label="Summa" min-width="120">
              <template #default="{ row }">
                <span class="font-bold text-emerald-600">{{ (row.total_amount || 0).toLocaleString() }} so'm</span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="payment_method" label="To'lov turi" min-width="110">
              <template #default="{ row }">
                <ElTag size="small" type="primary">{{ row.payment_method || 'naqd' }}</ElTag>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="created_at" label="Sana va Vaqt" min-width="160" />
          </ElTable>
        </ElTabPane>
      </ElTabs>
    </div>
    <template #footer>
      <BaseButton @click="detailDialogVisible = false">Yopish</BaseButton>
    </template>
  </ElDialog>

  <!-- ==================== BRANCH FORM ADD/EDIT DIALOG ==================== -->
  <ElDialog
    v-model="branchFormVisible"
    :title="branchFormTitle"
    width="500px"
    destroy-on-close
  >
    <ElForm label-position="top">
      <ElFormItem label="Filial Nomi" required>
        <ElInput v-model="branchFormData.name" placeholder="Masalan: Chorsu Filiali" />
      </ElFormItem>
      <ElFormItem label="Filial Kodi">
        <ElInput v-model="branchFormData.code" placeholder="Masalan: FIL-CH01" />
      </ElFormItem>
      <ElFormItem label="Manzili">
        <ElInput v-model="branchFormData.address" placeholder="Toshkent sh., Navoiy ko'chasi, 15-uy" />
      </ElFormItem>
      <ElFormItem label="Telefon Raqami">
        <ElInput v-model="branchFormData.phone" placeholder="+998 90 123 45 67" />
      </ElFormItem>
    </ElForm>
    <template #footer>
      <div class="flex justify-end gap-10px">
        <BaseButton @click="branchFormVisible = false">Bekor qilish</BaseButton>
        <BaseButton type="primary" :loading="branchFormLoading" @click="submitBranchForm">
          Saqlash
        </BaseButton>
      </div>
    </template>
  </ElDialog>

  <ResizeDialog
    v-model="dialogVisible"
    :title="dialogTitle"
    :init-width="dialogInitWidth"
    :init-height="dialogInitHeight"
    :min-resize-width="500"
    :min-resize-height="380"
    class="dept-custom-dialog"
  >
    <div class="p-12px flex-1 h-full min-h-0">
      <Write
        v-if="actionType !== 'detail'"
        ref="writeRef"
        :form-schema="allSchemas.formSchema"
        :current-row="currentRow"
      />

      <Detail
        v-if="actionType === 'detail'"
        :detail-schema="allSchemas.detailSchema"
        :current-row="currentRow"
      />
    </div>

    <template #footer>
      <div class="flex justify-end gap-10px pt-8px border-t border-gray-700">
        <BaseButton
          v-if="actionType !== 'detail'"
          type="primary"
          :loading="saveLoading"
          @click="save"
        >
          {{ t('exampleDemo.save') }}
        </BaseButton>
        <BaseButton @click="dialogVisible = false">{{ t('dialogDemo.close') }}</BaseButton>
      </div>
    </template>
  </ResizeDialog>
</template>

<style lang="less">
.dept-custom-dialog {
  &.el-dialog {
    background: var(--el-bg-color-overlay, #ffffff) !important;
    border: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
    border-radius: 12px !important;

    .el-dialog__header {
      padding: 14px 20px !important;
      background: var(--el-fill-color-light, #f8fafc) !important;
      border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
    }

    .el-dialog__body {
      padding: 16px !important;
      background: var(--el-bg-color-overlay, #ffffff) !important;
    }

    .el-dialog__footer {
      padding: 12px 20px !important;
      border-top: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
      background: var(--el-fill-color-light, #f8fafc) !important;
    }
  }
}

:global(.dark) {
  .dept-custom-dialog {
    &.el-dialog {
      background: #1f2937 !important;
      border-color: #374151 !important;

      .el-dialog__header {
        background: #1f2937 !important;
        border-bottom-color: #374151 !important;
      }

      .el-dialog__body {
        background: #1f2937 !important;
      }

      .el-dialog__footer {
        background: #111827 !important;
        border-top-color: #374151 !important;
      }
    }
  }
}
</style>
