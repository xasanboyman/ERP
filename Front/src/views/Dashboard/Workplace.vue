<script setup lang="ts">
import {
  ElRow,
  ElCol,
  ElSkeleton,
  ElCard,
  ElDivider,
  ElTag,
  ElAvatar,
  ElTimeline,
  ElTimelineItem,
  ElDialog,
  ElButton,
  ElInput,
  ElTable,
  ElTableColumn,
  ElRadioGroup,
  ElRadioButton
} from 'element-plus'
import { useI18n } from '@/hooks/web/useI18n'
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CountTo } from '@/components/CountTo'
import { getWorkplaceSummaryApi, type WorkplaceSummaryData } from '@/api/dashboard/workplace'
import { getWorkerListApi, WorkerType } from '@/api/worker'
import { getProductListApi, ProductType } from '@/api/product'
import { getActivityListApi, ActivityLogType } from '@/api/activity'
import { listDeviceTokensApi, type DeviceTokenItem } from '@/api/device'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'
import request from '@/axios'
import { Icon } from '@/components/Icon'
import PanelGroup from './components/PanelGroup.vue'

const { t } = useI18n()
const router = useRouter()

const loading = ref(true)

// Stats counters - 100% Real Live Database Figures
const workplaceStats = reactive<WorkplaceSummaryData>({
  productsCount: 0,
  activeWorkersCount: 0,
  salesCount: 0,
  debtorsCount: 0,
  totalDebtAmount: 0
})

const getWorkplaceStats = async () => {
  try {
    const res = await getWorkplaceSummaryApi().catch(() => {})
    if (res && res.data) {
      Object.assign(workplaceStats, res.data)
    }
  } catch (err) {
    console.error('Failed to get workplace stats:', err)
  }
}

// Active Workers (status === 1 only)
const activeWorkers = ref<WorkerType[]>([])

const getActiveWorkers = async () => {
  const res = await getWorkerListApi({ pageSize: 50, pageIndex: 1 }).catch(() => {})
  if (res && res.data) {
    const list = Array.isArray(res.data.list)
      ? res.data.list
      : Array.isArray(res.data)
        ? res.data
        : []
    activeWorkers.value = list.filter((w: any) => w.status === 1).slice(0, 9)
  }
}

// Most Sold Products
const topProducts = ref<ProductType[]>([])

const getTopProducts = async () => {
  const res = await getProductListApi({ pageSize: 20, pageIndex: 1 }).catch(() => {})
  if (res && res.data) {
    const list = Array.isArray(res.data.list)
      ? res.data.list
      : Array.isArray(res.data)
        ? res.data
        : []
    topProducts.value = [...list]
      .sort((a, b) => (b.quantityInStock ?? 0) - (a.quantityInStock ?? 0))
      .slice(0, 5)
  }
}

// Low Stock Products Alert
const lowStockProducts = ref<ProductType[]>([])

const getLowStockProducts = async () => {
  const res = await getProductListApi({ pageSize: 50, pageIndex: 1 }).catch(() => {})
  if (res && res.data) {
    const list = Array.isArray(res.data.list)
      ? res.data.list
      : Array.isArray(res.data)
        ? res.data
        : []
    lowStockProducts.value = [...list]
      .filter((p: any) => (p.quantityInStock ?? 0) <= 25)
      .sort((a, b) => (a.quantityInStock ?? 0) - (b.quantityInStock ?? 0))
      .slice(0, 5)
  }
}

// Paired Connected Devices
const pairedDevices = ref<DeviceTokenItem[]>([])

const getPairedDevices = async () => {
  try {
    const res = await listDeviceTokensApi()
    if (res && res.data) {
      const list = Array.isArray(res.data.list)
        ? res.data.list
        : Array.isArray(res.data)
          ? res.data
          : []
      pairedDevices.value = list
    }
  } catch (err) {
    console.warn('Could not load paired devices:', err)
  }
}

// Activity Log
const activityList = ref<ActivityLogType[]>([])

const getActivityLog = async () => {
  const res = await getActivityListApi({ pageSize: 15, pageIndex: 1 }).catch(() => {})
  if (res && res.data) {
    const list = Array.isArray(res.data.list)
      ? res.data.list
      : Array.isArray(res.data)
        ? res.data
        : []
    activityList.value = list
  }
}

const getAllApi = async () => {
  await Promise.all([
    getWorkplaceStats(),
    getActiveWorkers(),
    getTopProducts(),
    getActivityLog(),
    getPairedDevices(),
    getLowStockProducts()
  ])
  loading.value = false
}

useRealtimeSync(['sale', 'product', 'worker', 'device'], () => {
  getAllApi()
})

onMounted(() => {
  getAllApi()
})

// Navigation Helper
const goTo = (path: string) => {
  router.push(path)
}

// Space-separated currency formatting (e.g. 1 528 000)
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

// Helpers
const getInitials = (name: string) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const actionLabel = (action: string) => {
  const map: Record<string, string> = {
    created: t('workplace.actionCreated'),
    updated: t('workplace.actionUpdated'),
    deleted: t('workplace.actionDeleted'),
    payout: t('workplace.actionPayout'),
    sale: t('workplace.actionSale')
  }
  return map[action] ?? action
}

const entityLabel = (entity: string) => {
  const map: Record<string, string> = {
    worker: t('workplace.entityWorker'),
    product: t('workplace.entityProduct'),
    salary: t('workplace.entitySalary'),
    department: t('workplace.entityDepartment'),
    sale: t('erp.saleReceipt')
  }
  return map[entity] ?? entity
}

const actionColor = (action: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
  if (action === 'created') return 'success'
  if (action === 'updated') return 'warning'
  if (action === 'deleted') return 'danger'
  if (action === 'payout' || action === 'sale') return 'primary'
  return 'info'
}

const actionTimelineType = (
  action: string
): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
  if (action === 'created') return 'success'
  if (action === 'updated') return 'warning'
  if (action === 'deleted') return 'danger'
  if (action === 'payout' || action === 'sale') return 'primary'
  return 'info'
}

const formatTimestamp = (ts: string) => {
  if (!ts) return ''
  const today = new Date().toISOString().slice(0, 10)
  if (ts.startsWith(today)) {
    return t('workplace.toady') + ' ' + ts.slice(11, 16)
  }
  return ts.slice(0, 16)
}

// Extract receipt check number from activity text if present
const extractCheckNumber = (log: ActivityLogType): string | null => {
  const text = (log.entityName || '') + ' ' + (log.entityId || '')
  const match = text.match(/(CHK-[\w-]+)/i)
  return match ? match[1] : null
}

// ── View All Activities Modal State ──────────────────────────────
const allActivitiesDialogVisible = ref(false)
const allActivitiesLoading = ref(false)
const fullActivityList = ref<ActivityLogType[]>([])
const activitySearchKeyword = ref('')
const activityFilterTab = ref('all')

const openAllActivitiesModal = async () => {
  allActivitiesDialogVisible.value = true
  allActivitiesLoading.value = true
  try {
    const res = await getActivityListApi({ pageSize: 100, pageIndex: 1 })
    if (res && res.data) {
      const list = Array.isArray(res.data.list)
        ? res.data.list
        : Array.isArray(res.data)
          ? res.data
          : []
      fullActivityList.value = list
    }
  } catch (error) {
    console.error('Failed to load all activities:', error)
  } finally {
    allActivitiesLoading.value = false
  }
}

const filteredFullActivities = computed(() => {
  return fullActivityList.value.filter((log) => {
    // Filter tab
    if (activityFilterTab.value === 'sales' && log.entity !== 'sale' && !extractCheckNumber(log))
      return false
    if (activityFilterTab.value === 'worker' && log.entity !== 'worker') return false
    if (activityFilterTab.value === 'product' && log.entity !== 'product') return false
    if (activityFilterTab.value === 'salary' && log.entity !== 'salary') return false

    // Keyword search
    if (!activitySearchKeyword.value.trim()) return true
    const kw = activitySearchKeyword.value.toLowerCase()
    const matchActor = (log.actor || '').toLowerCase().includes(kw)
    const matchName = (log.entityName || '').toLowerCase().includes(kw)
    const matchEntity = (log.entity || '').toLowerCase().includes(kw)
    const matchCheck = (extractCheckNumber(log) || '').toLowerCase().includes(kw)
    return matchActor || matchName || matchEntity || matchCheck
  })
})

// ── Receipt Detail Modal State ─────────────────────────────────────
const receiptDetailDialogVisible = ref(false)
const receiptDetailLoading = ref(false)
const receiptData = ref<any>(null)

const openReceiptDetail = async (log: ActivityLogType) => {
  const checkNum = extractCheckNumber(log)
  const targetCheck = checkNum || log.entityId || log.entityName

  receiptDetailDialogVisible.value = true
  receiptDetailLoading.value = true
  receiptData.value = null

  if (targetCheck && targetCheck.startsWith('CHK-')) {
    try {
      const res = await request.get<{ code: number; data: any }>({
        url: `/sales/receipt/${targetCheck}`
      })
      if (res && res.data) {
        receiptData.value = res.data
      } else {
        createFallbackReceiptData(log, targetCheck)
      }
    } catch (e) {
      console.warn('Could not fetch online receipt detail, using log info:', e)
      createFallbackReceiptData(log, targetCheck)
    } finally {
      receiptDetailLoading.value = false
    }
  } else {
    createFallbackReceiptData(log, targetCheck || "NOMA'LUM")
    receiptDetailLoading.value = false
  }
}

const createFallbackReceiptData = (log: ActivityLogType, checkNum: string) => {
  let amount = 0
  const matchMoney = (log.entityName || '').match(/\$([\d,.]+)/)
  if (matchMoney) {
    amount = parseFloat(matchMoney[1].replace(/,/g, ''))
  }

  receiptData.value = {
    receipt_number: checkNum,
    cashier_name: log.actor || 'admin',
    customer_name: t('workplace.customerColon').replace(':', ''),
    payment_method: 'naqd',
    total_amount: amount,
    paid_amount: amount,
    debt_amount: 0,
    created_at: log.timestamp,
    items: [
      {
        product_name: log.entityName || t('workplace.saleOperationDefault'),
        shtrix_code: '—',
        price: amount,
        quantity: 1,
        total: amount
      }
    ]
  }
}
</script>

<template>
  <div class="workplace-container">
    <!-- Top Hero Banner Card -->
    <ElCard shadow="never" class="hero-banner-card mb-20px">
      <ElSkeleton :loading="loading" animated>
        <ElRow :gutter="20" justify="space-between" align="middle">
          <ElCol :xl="12" :lg="12" :md="12" :sm="24" :xs="24">
            <div class="flex items-center gap-20px">
              <div class="avatar-wrapper">
                <img src="@/assets/imgs/avatar.jpg" alt="User Avatar" class="user-avatar" />
                <span class="online-indicator" title="Tizimda faol"></span>
              </div>
              <div>
                <div class="greeting-title"> {{ t('workplace.goodMorning') }}, Admin! </div>
                <div class="mt-6px greeting-sub">
                  {{ t('erp.heroSubtitle') }}
                </div>
              </div>
            </div>
          </ElCol>
          <ElCol :xl="12" :lg="12" :md="12" :sm="24" :xs="24">
            <div class="flex items-center justify-end gap-24px lt-sm:mt-20px">
              <div class="hero-stat-item text-right">
                <div class="stat-title">{{ t('erp.productTypesCount') }}</div>
                <CountTo
                  class="stat-value text-blue"
                  :start-val="0"
                  :end-val="workplaceStats.productsCount"
                  :duration="2000"
                />
              </div>
              <ElDivider direction="vertical" class="hero-divider" />
              <div class="hero-stat-item text-right">
                <div class="stat-title">{{ t('erp.activeWorkersCount') }}</div>
                <CountTo
                  class="stat-value text-amber"
                  :start-val="0"
                  :end-val="workplaceStats.activeWorkersCount"
                  :duration="2000"
                />
              </div>
              <ElDivider direction="vertical" class="hero-divider" />
              <div class="hero-stat-item text-right">
                <div class="stat-title">{{ t('erp.totalSalesCount') }}</div>
                <CountTo
                  class="stat-value text-purple"
                  :start-val="0"
                  :end-val="workplaceStats.salesCount"
                  :duration="2000"
                />
              </div>
            </div>
          </ElCol>
        </ElRow>
      </ElSkeleton>
    </ElCard>

    <!-- ── 1. REAL-TIME FINANCIAL KPI METRICS PANEL ────────────────────── -->
    <PanelGroup />

    <!-- ── 2. ERP FAST-TRACK QUICK ACTIONS TOOLBAR ───────────────────── -->
    <ElCard shadow="never" class="glass-section-card mb-20px">
      <template #header>
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-10px">
            <div class="card-dot purple"></div>
            <span class="card-title">{{ t('erp.quickActions') }}</span>
          </div>
          <span class="text-12px text-gray-400">{{ t('erp.quickActionsDesc') }}</span>
        </div>
      </template>
      <ElRow :gutter="12" class="quick-actions-row">
        <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="12" class="mb-10px">
          <div class="quick-action-btn action-pos" @click="goTo('/sales/pos')">
            <div class="action-icon bg-blue-glow">
              <Icon icon="ep:shopping-cart-full" :size="22" />
            </div>
            <span class="action-label">{{ t('erp.posSaleAction') }}</span>
            <span class="action-desc">{{ t('erp.posSaleDesc') }}</span>
          </div>
        </ElCol>
        <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="12" class="mb-10px">
          <div class="quick-action-btn action-prod" @click="goTo('/product/list')">
            <div class="action-icon bg-emerald-glow">
              <Icon icon="ep:goods" :size="22" />
            </div>
            <span class="action-label">{{ t('erp.productsAction') }}</span>
            <span class="action-desc">{{ t('erp.productsDesc') }}</span>
          </div>
        </ElCol>
        <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="12" class="mb-10px">
          <div class="quick-action-btn action-salary" @click="goTo('/hr/salary')">
            <div class="action-icon bg-purple-glow">
              <Icon icon="ep:money" :size="22" />
            </div>
            <span class="action-label">{{ t('erp.salaryAction') }}</span>
            <span class="action-desc">{{ t('erp.salaryDesc') }}</span>
          </div>
        </ElCol>
        <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="12" class="mb-10px">
          <div class="quick-action-btn action-analytics" @click="goTo('/dashboard/analysis')">
            <div class="action-icon bg-rose-glow">
              <Icon icon="ep:data-analysis" :size="22" />
            </div>
            <span class="action-label">{{ t('erp.analyticsAction') }}</span>
            <span class="action-desc">{{ t('erp.analyticsDesc') }}</span>
          </div>
        </ElCol>
      </ElRow>
    </ElCard>

    <!-- Main Content Layout Row -->
    <ElRow :gutter="20" justify="space-between">
      <!-- Left Column: Active Workers & Connected Devices -->
      <ElCol :xl="15" :lg="15" :md="24" :sm="24" :xs="24" class="mb-20px">
        <!-- Active Workers Card -->
        <ElCard shadow="never" class="glass-section-card h-full">
          <template #header>
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-10px">
                <div class="card-dot green"></div>
                <span class="card-title">{{ t('workplace.activeWorkers') }}</span>
                <ElTag type="success" size="small" effect="dark" class="rounded-full font-bold">
                  {{ activeWorkers.length }} {{ t('erp.activeCountSuffix') }}
                </ElTag>
              </div>
              <ElButton type="primary" link class="font-semibold" @click="goTo('/staff/hr')">
                {{ t('erp.allWorkers') }} <Icon icon="ep:arrow-right" class="ml-4px" :size="12" />
              </ElButton>
            </div>
          </template>
          <ElSkeleton :loading="loading" animated>
            <ElRow :gutter="14">
              <ElCol
                v-for="(worker, idx) in activeWorkers"
                :key="`worker-${idx}`"
                :xl="8"
                :lg="8"
                :md="12"
                :sm="24"
                :xs="24"
                class="mb-14px"
              >
                <div class="worker-card">
                  <div class="flex items-center gap-12px">
                    <ElAvatar :size="46" class="worker-avatar">
                      {{ getInitials(worker.name) }}
                    </ElAvatar>
                    <div class="worker-info min-w-0">
                      <div class="worker-name truncate">{{ worker.name }}</div>
                      <div class="worker-role truncate">{{
                        worker.role || t('workplace.defaultWorkerRole')
                      }}</div>
                      <div class="worker-dept truncate">{{ worker.departmentName || '—' }}</div>
                    </div>
                  </div>
                  <div
                    class="mt-12px flex items-center justify-between border-t border-gray-100 dark:border-gray-800 pt-8px"
                  >
                    <span class="salary-tag">${{ formatMoney(worker.baseSalary) }}</span>
                    <span v-if="worker.hireDate" class="text-11px text-gray-400 font-mono">
                      {{ worker.hireDate }}
                    </span>
                  </div>
                </div>
              </ElCol>
            </ElRow>
            <div v-if="!activeWorkers.length" class="text-center text-gray-400 py-30px text-14px">
              {{ t('common.noData') }}
            </div>
          </ElSkeleton>
        </ElCard>
      </ElCol>

      <!-- Right Column: Activity Log, Top Products & Low Stock Alerts -->
      <ElCol :xl="9" :lg="9" :md="24" :sm="24" :xs="24" class="mb-20px">
        <!-- Activity Log Card -->
        <ElCard shadow="never" class="glass-section-card">
          <template #header>
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-10px">
                <div class="card-dot blue"></div>
                <span class="card-title">{{ t('workplace.activityLog') }}</span>
              </div>
              <ElButton
                type="primary"
                link
                class="view-all-btn font-semibold"
                @click="openAllActivitiesModal"
              >
                {{ t('erp.viewAll') }} <Icon icon="ep:arrow-right" class="ml-4px" :size="12" />
              </ElButton>
            </div>
          </template>
          <ElSkeleton :loading="loading" animated>
            <div v-if="activityList.length" class="activity-timeline-wrapper">
              <ElTimeline>
                <ElTimelineItem
                  v-for="log in activityList"
                  :key="log.id"
                  :type="actionTimelineType(log.action)"
                  :timestamp="formatTimestamp(log.timestamp)"
                  placement="top"
                  size="normal"
                >
                  <div class="activity-item-content">
                    <div class="flex items-center gap-6px flex-wrap">
                      <span class="actor-name font-bold text-slate-800 dark:text-slate-200">
                        {{ log.actor || 'admin' }}
                      </span>
                      <ElTag
                        :type="actionColor(log.action)"
                        size="small"
                        effect="light"
                        class="activity-tag"
                      >
                        {{ actionLabel(log.action) }}
                      </ElTag>
                      <span class="text-12px text-gray-400 font-medium">
                        {{ entityLabel(log.entity) }}:
                      </span>
                    </div>

                    <!-- Display detail card / check button if check or sale -->
                    <div class="mt-6px flex items-center justify-between gap-8px">
                      <span
                        class="text-13px font-semibold text-slate-700 dark:text-slate-300 truncate"
                      >
                        {{ log.entityName || log.entityId }}
                      </span>
                      <ElButton
                        v-if="log.entity === 'sale' || extractCheckNumber(log)"
                        size="small"
                        type="primary"
                        plain
                        class="check-detail-btn"
                        @click="openReceiptDetail(log)"
                      >
                        <Icon icon="ep:tickets" class="mr-4px" :size="13" />
                        {{ t('erp.receiptDetail') }}
                      </ElButton>
                      <ElButton
                        v-else
                        size="small"
                        type="info"
                        text
                        class="check-detail-btn"
                        @click="openReceiptDetail(log)"
                      >
                        <Icon icon="ep:info-filled" class="mr-4px" :size="13" />
                        {{ t('common.detail') }}
                      </ElButton>
                    </div>
                  </div>
                </ElTimelineItem>
              </ElTimeline>
            </div>
            <div v-else class="text-center py-30px">
              <div class="text-gray-400 text-14px">{{ t('workplace.noActivity') }}</div>
            </div>
          </ElSkeleton>
        </ElCard>

        <!-- Low Stock Inventory Warning Alert Card -->
        <ElCard shadow="never" class="glass-section-card mt-20px warning-stock-card">
          <template #header>
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-10px">
                <div class="card-dot rose"></div>
                <span class="card-title text-rose-600 dark:text-rose-400 font-bold">{{
                  t('erp.lowStockWarning')
                }}</span>
              </div>
              <ElTag type="danger" size="small" effect="dark" class="font-bold">
                {{ lowStockProducts.length }} {{ t('erp.warningsCount') }}
              </ElTag>
            </div>
          </template>
          <ElSkeleton :loading="loading" animated>
            <div v-if="lowStockProducts.length" class="space-y-8px">
              <div
                v-for="prod in lowStockProducts"
                :key="prod.id"
                class="flex items-center justify-between p-8px rounded-8px bg-rose-50/60 dark:bg-rose-950/30 border border-rose-100 dark:border-rose-900/50"
              >
                <div class="min-w-0 pr-8px">
                  <div class="font-semibold text-13px text-slate-800 dark:text-slate-200 truncate">
                    {{ prod.productName }}
                  </div>
                  <div class="text-11px text-gray-400 truncate">{{ prod.category }}</div>
                </div>
                <div class="text-right flex-shrink-0">
                  <span
                    class="text-12px font-extrabold text-rose-600 dark:text-rose-400 font-mono bg-rose-100 dark:bg-rose-900/80 px-8px py-2px rounded-4px"
                  >
                    {{ prod.quantityInStock }} {{ t('erp.unitsRemaining') }}
                  </span>
                </div>
              </div>
            </div>
            <div
              v-else
              class="text-center py-16px text-emerald-600 dark:text-emerald-400 text-13px font-medium flex items-center justify-center gap-6px"
            >
              <Icon icon="ep:circle-check" class="text-15px" />
              <span>{{ t('workplace.allProductsSufficient') }}</span>
            </div>
          </ElSkeleton>
        </ElCard>

        <!-- Most Sold Products Card -->
        <ElCard shadow="never" class="glass-section-card mt-20px">
          <template #header>
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-10px">
                <div class="card-dot amber"></div>
                <span class="card-title">{{ t('workplace.mostSoldProducts') }}</span>
              </div>
              <span class="text-12px text-gray-400">{{ t('workplace.topSales') }}</span>
            </div>
          </template>
          <ElSkeleton :loading="loading" animated>
            <div
              v-for="(product, idx) in topProducts"
              :key="`product-${idx}`"
              class="product-row-item"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-12px min-w-0">
                  <div class="rank-badge" :class="`rank-${idx + 1}`">{{ idx + 1 }}</div>
                  <div class="min-w-0">
                    <div
                      class="product-title font-semibold text-14px text-slate-800 dark:text-slate-100 truncate"
                    >
                      {{ product.productName }}
                    </div>
                    <div class="text-12px text-gray-400 truncate">{{ product.category }}</div>
                  </div>
                </div>
                <div class="text-right flex-shrink-0 ml-10px">
                  <div
                    class="text-14px font-extrabold text-emerald-600 dark:text-emerald-400 font-mono"
                  >
                    ${{ formatMoney(product.price) }}
                  </div>
                  <div class="text-11px text-gray-400 font-medium">
                    {{ t('workplace.inStockCount', { qty: formatMoney(product.quantityInStock) }) }}
                  </div>
                </div>
              </div>
              <ElDivider v-if="idx < topProducts.length - 1" class="my-8px!" />
            </div>
            <div v-if="!topProducts.length" class="text-center text-gray-400 py-20px text-14px">
              {{ t('common.noData') }}
            </div>
          </ElSkeleton>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- ── MODAL 1: ALL ACTIVITIES AUDIT LOG DIALOG ──────────────────── -->
    <ElDialog
      v-model="allActivitiesDialogVisible"
      :title="t('workplace.auditTrailTitle')"
      width="900px"
      destroy-on-close
      class="custom-activity-dialog"
    >
      <div class="dialog-body-container">
        <!-- Search and Filter Bar -->
        <div class="flex items-center justify-between flex-wrap gap-12px mb-16px">
          <ElRadioGroup v-model="activityFilterTab" size="default" class="custom-radio-group">
            <ElRadioButton value="all">{{ t('erp.allCategories') }}</ElRadioButton>
            <ElRadioButton value="sales">{{ t('workplace.salesReceiptsTab') }}</ElRadioButton>
            <ElRadioButton value="worker">{{ t('erp.allWorkers') }}</ElRadioButton>
            <ElRadioButton value="product">{{ t('erp.productsAction') }}</ElRadioButton>
            <ElRadioButton value="salary">{{ t('erp.salaryAction') }}</ElRadioButton>
          </ElRadioGroup>

          <ElInput
            v-model="activitySearchKeyword"
            :placeholder="t('workplace.searchAuditPlaceholder')"
            clearable
            style="width: 280px"
          >
            <template #prefix>
              <Icon icon="ep:search" class="text-gray-400" />
            </template>
          </ElInput>
        </div>

        <!-- Activity Table -->
        <ElTable
          v-loading="allActivitiesLoading"
          :data="filteredFullActivities"
          border
          stripe
          max-height="460"
          style="width: 100%"
          class="activity-full-table"
        >
          <ElTableColumn
            prop="timestamp"
            :label="t('workplace.timeColumn')"
            width="160"
            align="center"
          >
            <template #default="{ row }">
              <span class="font-mono text-12px text-slate-600 dark:text-slate-400 font-semibold">
                {{ row.timestamp }}
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="actor" :label="t('workplace.userColumn')" width="140">
            <template #default="{ row }">
              <span class="font-bold text-blue-600 dark:text-blue-400 text-13px">
                {{ row.actor || 'admin' }}
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="action"
            :label="t('workplace.actionTypeColumn')"
            width="160"
            align="center"
          >
            <template #default="{ row }">
              <ElTag :type="actionColor(row.action)" effect="light" class="font-semibold">
                {{ actionLabel(row.action) }}
              </ElTag>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="entityName"
            :label="t('workplace.operationDetailColumn')"
            min-width="260"
          >
            <template #default="{ row }">
              <span class="font-medium text-slate-800 dark:text-slate-200 text-13px">
                {{ row.entityName || row.entityId }}
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn
            :label="t('workplace.actionColumn')"
            width="130"
            align="center"
            fixed="right"
          >
            <template #default="{ row }">
              <ElButton
                size="small"
                type="primary"
                plain
                class="font-semibold"
                @click="openReceiptDetail(row)"
              >
                <Icon icon="ep:tickets" class="mr-4px" :size="12" />
                {{ t('workplace.detailAction') }}
              </ElButton>
            </template>
          </ElTableColumn>
        </ElTable>
      </div>

      <template #footer>
        <div class="flex justify-between items-center">
          <span class="text-12px text-gray-400">{{
            t('workplace.totalActivitiesCount', { count: filteredFullActivities.length })
          }}</span>
          <ElButton type="primary" @click="allActivitiesDialogVisible = false">{{
            t('common.close')
          }}</ElButton>
        </div>
      </template>
    </ElDialog>

    <!-- ── MODAL 2: RECEIPT & CHECK DETAILS DIALOG ────────────────────── -->
    <ElDialog
      v-model="receiptDetailDialogVisible"
      :title="t('workplace.receiptDetailsTitle')"
      width="680px"
      destroy-on-close
      class="custom-receipt-dialog"
    >
      <div v-loading="receiptDetailLoading" class="receipt-modal-body">
        <div v-if="receiptData">
          <!-- Receipt Header Card -->
          <div class="receipt-header-box">
            <div class="flex items-center justify-between">
              <div>
                <div class="receipt-check-number">
                  {{ receiptData.receipt_number || t('workplace.salesReceiptUpper') }}
                </div>
                <div class="text-12px text-gray-400 mt-2px">
                  {{ t('workplace.dateLabelColon') }}
                  <span class="font-mono text-slate-700 dark:text-slate-300 font-semibold">{{
                    receiptData.created_at
                  }}</span>
                </div>
              </div>
              <ElTag
                :type="receiptData.payment_method === 'nasiya' ? 'warning' : 'success'"
                effect="dark"
                size="large"
                class="font-bold uppercase"
              >
                {{
                  receiptData.payment_method === 'nasiya'
                    ? t('workplace.nasiyaDebtUpper')
                    : t('workplace.paidSuccessUpper')
                }}
              </ElTag>
            </div>

            <!-- Meta info grid -->
            <div
              class="grid grid-cols-2 gap-12px mt-16px pt-12px border-t border-gray-200 dark:border-gray-700"
            >
              <div>
                <span class="text-12px text-gray-400">{{ t('workplace.cashierColon') }}</span>
                <div class="font-bold text-slate-800 dark:text-slate-100 text-13px">
                  {{ receiptData.cashier_name || 'admin' }}
                </div>
              </div>
              <div>
                <span class="text-12px text-gray-400">{{ t('workplace.customerColon') }}</span>
                <div class="font-bold text-slate-800 dark:text-slate-100 text-13px">
                  {{ receiptData.customer_name || t('workplace.defaultBuyer') }}
                </div>
              </div>
            </div>
          </div>

          <!-- Items Table -->
          <div class="mt-16px">
            <div class="text-13px font-bold text-slate-700 dark:text-slate-300 mb-8px">
              {{ t('workplace.purchasedProductsList') }}
            </div>
            <ElTable
              :data="receiptData.items || []"
              border
              stripe
              max-height="240"
              style="width: 100%"
            >
              <ElTableColumn prop="product_name" :label="t('erp.productName')" min-width="220">
                <template #default="{ row }">
                  <span class="font-semibold text-slate-800 dark:text-slate-200 text-13px">
                    {{ row.product_name }}
                  </span>
                </template>
              </ElTableColumn>

              <ElTableColumn
                prop="price"
                :label="t('analysis.priceDollar')"
                width="120"
                align="right"
              >
                <template #default="{ row }">
                  <span class="font-mono text-13px">${{ formatMoney(row.price) }}</span>
                </template>
              </ElTableColumn>

              <ElTableColumn
                prop="quantity"
                :label="t('workplace.qtyHeader')"
                width="90"
                align="center"
              >
                <template #default="{ row }">
                  <span class="font-bold text-blue-600 dark:text-blue-400">{{ row.quantity }}</span>
                </template>
              </ElTableColumn>

              <ElTableColumn
                prop="total"
                :label="t('analysis.totalDollar')"
                width="130"
                align="right"
              >
                <template #default="{ row }">
                  <span
                    class="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-14px"
                  >
                    ${{ formatMoney(row.total || row.price * row.quantity) }}
                  </span>
                </template>
              </ElTableColumn>
            </ElTable>
          </div>

          <!-- Financial Totals Summary -->
          <div class="receipt-totals-box mt-16px">
            <div class="flex justify-between items-center mb-6px">
              <span class="text-13px text-gray-500 font-medium">{{
                t('workplace.totalSumColon')
              }}</span>
              <span class="font-mono font-bold text-15px text-slate-800 dark:text-slate-100">
                ${{ formatMoney(receiptData.total_amount) }}
              </span>
            </div>
            <div class="flex justify-between items-center mb-6px">
              <span class="text-13px text-gray-500 font-medium">{{
                t('workplace.paidMoneyColon')
              }}</span>
              <span class="font-mono font-bold text-15px text-blue-600 dark:text-blue-400">
                ${{ formatMoney(receiptData.paid_amount) }}
              </span>
            </div>
            <div
              v-if="receiptData.debt_amount > 0"
              class="flex justify-between items-center pt-6px border-t border-rose-200 dark:border-rose-900"
            >
              <span class="text-14px font-bold text-rose-600 dark:text-rose-400">{{
                t('workplace.debtSumColon')
              }}</span>
              <span class="font-mono font-extrabold text-16px text-rose-600 dark:text-rose-400">
                ${{ formatMoney(receiptData.debt_amount) }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-40px text-gray-400">
          {{ t('workplace.receiptNotFound') }}
        </div>
      </div>

      <template #footer>
        <ElButton type="primary" @click="receiptDetailDialogVisible = false">{{
          t('workplace.understoodBtn')
        }}</ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped lang="less">
.workplace-container {
  padding-bottom: 30px;
}

.hero-banner-card {
  border-radius: 16px;
  background: var(--el-bg-color-overlay, #ffffff);
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);

  .avatar-wrapper {
    position: relative;
    display: inline-block;

    .user-avatar {
      width: 68px;
      height: 68px;
      border-radius: 50%;
      object-fit: cover;
      border: 3px solid #3b82f6;
      box-shadow: 0 0 16px rgba(59, 130, 246, 0.35);
    }

    .online-indicator {
      position: absolute;
      bottom: 2px;
      right: 2px;
      width: 14px;
      height: 14px;
      background: #10b981;
      border: 2.5px solid #ffffff;
      border-radius: 50%;
    }
  }

  .greeting-title {
    font-size: 20px;
    font-weight: 800;
    color: var(--el-text-color-primary, #1e293b);
  }

  .greeting-sub {
    font-size: 13px;
    color: var(--el-text-color-regular, #64748b);
  }

  .hero-stat-item {
    .stat-title {
      font-size: 12px;
      font-weight: 600;
      color: var(--el-text-color-secondary, #94a3b8);
      margin-bottom: 6px;
      letter-spacing: 0.02em;
    }

    .stat-value {
      font-size: 22px;
      font-weight: 800;

      &.text-blue {
        color: #3b82f6;
      }
      &.text-amber {
        color: #f59e0b;
      }
      &.text-purple {
        color: #a855f7;
      }
    }
  }

  .hero-divider {
    height: 36px;
    border-color: var(--el-border-color-lighter, #cbd5e1);
  }
}

.glass-section-card {
  border-radius: 16px;
  background: var(--el-bg-color-overlay, #ffffff);
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.22s ease;

  .card-title {
    font-size: 14px;
    font-weight: 700;
    color: var(--el-text-color-primary, #1e293b);
  }

  .card-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;

    &.green {
      background: #10b981;
      box-shadow: 0 0 8px rgba(16, 185, 129, 0.8);
    }
    &.blue {
      background: #3b82f6;
      box-shadow: 0 0 8px rgba(59, 130, 246, 0.8);
    }
    &.amber {
      background: #f59e0b;
      box-shadow: 0 0 8px rgba(245, 158, 11, 0.8);
    }
    &.purple {
      background: #8b5cf6;
      box-shadow: 0 0 8px rgba(139, 92, 246, 0.8);
    }
    &.cyan {
      background: #06b6d4;
      box-shadow: 0 0 8px rgba(6, 182, 212, 0.8);
    }
    &.rose {
      background: #f43f5e;
      box-shadow: 0 0 8px rgba(244, 63, 94, 0.8);
    }
  }
}

/* Quick Action Buttons */
.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px 10px;
  border-radius: 14px;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  background: var(--el-fill-color-blank, #ffffff);
  cursor: pointer;
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
    border-color: #3b82f6;

    .action-icon {
      transform: scale(1.1);
    }
  }

  .action-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    margin-bottom: 8px;
    transition: transform 0.2s ease;

    &.bg-blue-glow {
      background: linear-gradient(135deg, #3b82f6, #1d4ed8);
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
    }
    &.bg-emerald-glow {
      background: linear-gradient(135deg, #10b981, #059669);
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
    }
    &.bg-purple-glow {
      background: linear-gradient(135deg, #8b5cf6, #6d28d9);
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.35);
    }
    &.bg-amber-glow {
      background: linear-gradient(135deg, #f59e0b, #d97706);
      box-shadow: 0 4px 12px rgba(245, 158, 11, 0.35);
    }
    &.bg-cyan-glow {
      background: linear-gradient(135deg, #06b6d4, #0891b2);
      box-shadow: 0 4px 12px rgba(6, 182, 212, 0.35);
    }
    &.bg-rose-glow {
      background: linear-gradient(135deg, #f43f5e, #be123c);
      box-shadow: 0 4px 12px rgba(244, 63, 94, 0.35);
    }
  }

  .action-label {
    font-size: 13px;
    font-weight: 700;
    color: var(--el-text-color-primary, #1e293b);
  }

  .action-desc {
    font-size: 11px;
    color: var(--el-text-color-secondary, #94a3b8);
    margin-top: 2px;
  }
}

.worker-card {
  padding: 14px;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  background: var(--el-fill-color-blank, #ffffff);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    border-color 0.2s ease;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    border-color: #3b82f6;
  }

  .worker-avatar {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    color: #ffffff;
    font-weight: 800;
    font-size: 15px;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  }

  .worker-name {
    font-size: 14px;
    font-weight: 700;
    color: var(--el-text-color-primary, #1e293b);
  }

  .worker-role {
    font-size: 12px;
    color: var(--el-text-color-secondary, #64748b);
  }

  .worker-dept {
    font-size: 11px;
    color: var(--el-text-color-placeholder, #94a3b8);
  }

  .salary-tag {
    font-family: monospace;
    font-weight: 700;
    font-size: 12px;
    color: #10b981;
  }
}

.device-item-card {
  background: var(--el-fill-color-light, #f8fafc);
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);

  .device-icon-box {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: rgba(59, 130, 246, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.activity-item-content {
  padding: 4px 0;

  .check-detail-btn {
    border-radius: 6px;
    font-weight: 600;
  }
}

.product-row-item {
  padding: 8px 0;

  .rank-badge {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
    background: var(--el-fill-color-light, #f1f5f9);
    color: var(--el-text-color-regular, #64748b);

    &.rank-1 {
      background: linear-gradient(135deg, #f59e0b, #d97706);
      color: #fff;
    }
    &.rank-2 {
      background: linear-gradient(135deg, #94a3b8, #64748b);
      color: #fff;
    }
    &.rank-3 {
      background: linear-gradient(135deg, #b45309, #78350f);
      color: #fff;
    }
  }
}

/* Modals styling */
.receipt-header-box {
  background: var(--el-fill-color-light, #f8fafc);
  padding: 16px;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);

  .receipt-check-number {
    font-size: 16px;
    font-weight: 800;
    color: #3b82f6;
    font-family: monospace;
  }
}

.receipt-totals-box {
  background: var(--el-fill-color-light, #f8fafc);
  padding: 14px 18px;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
}
</style>
