<script setup lang="ts">
import PanelGroup from './components/PanelGroup.vue'
import {
  ElRow,
  ElCol,
  ElSkeleton,
  ElSkeletonItem,
  ElTable,
  ElTableColumn,
  ElTag,
  ElRadioGroup,
  ElRadioButton,
  ElButton,
  ElDatePicker,
  ElMessage,
  ElMessageBox,
  ElDialog,
  ElProgress,
  ElTooltip,
  ElInput,
  ElSelect,
  ElOption
} from 'element-plus'
import { Echart } from '@/components/Echart'
import { CountTo } from '@/components/CountTo'
import { Icon } from '@/components/Icon'
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'
import { useAppStore } from '@/store/modules/app'
import { getSalesListApi, SaleType } from '@/api/sales'
import {
  getFinancialOverviewApi,
  getMonthSummaryApi,
  comparePeriodsApi,
  getFinancialSnapshotsApi,
  closeMonthlyFinancialSnapshotApi,
  deleteFinancialSnapshotApi,
  getAnalysisBundleApi,
  type MonthlyFinancialSnapshotItem,
  type FinancialOverviewData,
  type MonthSummaryData,
  type PeriodComparisonData
} from '@/api/dashboard/analysis'
import { exportToExcel } from '@/utils/exportReport'
import { useI18n } from '@/hooks/web/useI18n'
import { useLocaleStore } from '@/store/modules/locale'
import type { EChartsOption } from 'echarts'

const { t } = useI18n()
const appStore = useAppStore()
const isDark = computed(() => appStore.getIsDark)
const localeStore = useLocaleStore()

const activeViewTab = ref<'standard' | 'closing' | 'compare'>('standard')
const loading = ref(true)
const closingLoading = ref(false)
const comparisonLoading = ref(false)
const timeRange = ref<'6m' | '1y'>('6m')

// Standard ECharts Options
const financialTrendOptions = ref<EChartsOption>({})
const expenseStructureOptions = ref<EChartsOption>({})
const categoryProfitOptions = ref<EChartsOption>({})
const monthlyFinancialTable = ref<any[]>([])
const overviewData = ref<FinancialOverviewData | null>(null)

// Closing & Archive Charts Options
const archiveHistoryTimelineOptions = ref<EChartsOption>({})
const monthDistributionDonutOptions = ref<EChartsOption>({})

// Comparison Mode States
const comparePreset = ref<'mom' | 'qoq' | 'last30' | 'yoy' | 'custom'>('mom')
const dNow = new Date()
const p1StartDef = `${dNow.getFullYear()}-${String(dNow.getMonth() + 1).padStart(2, '0')}-01`
const p1EndDef = `${dNow.getFullYear()}-${String(dNow.getMonth() + 1).padStart(2, '0')}-${String(dNow.getDate()).padStart(2, '0')}`
const prevMonthDate = new Date(dNow.getFullYear(), dNow.getMonth() - 1, 1)
const prevMonthLast = new Date(dNow.getFullYear(), dNow.getMonth(), 0)
const p2StartDef = `${prevMonthDate.getFullYear()}-${String(prevMonthDate.getMonth() + 1).padStart(2, '0')}-01`
const p2EndDef = `${prevMonthLast.getFullYear()}-${String(prevMonthLast.getMonth() + 1).padStart(2, '0')}-${String(prevMonthLast.getDate()).padStart(2, '0')}`

const period1Dates = ref<[string, string]>([p1StartDef, p1EndDef])
const period2Dates = ref<[string, string]>([p2StartDef, p2EndDef])
const period1Label = ref('Period 1')
const period2Label = ref('Period 2')

// Comparison ECharts Options
const comparisonBarOptions = ref<EChartsOption>({})
const comparisonCategoryOptions = ref<EChartsOption>({})

// Raw sales list for POS & Monthly Sales table
const allRawSales = ref<SaleType[]>([])
const salesLoading = ref(false)

// Comparison Calculated Data
const comparisonData = reactive({
  p1Revenue: 0,
  p2Revenue: 0,
  revDiff: 0,
  revGrowth: 0,

  p1COGS: 0,
  p2COGS: 0,
  cogsDiff: 0,
  cogsGrowth: 0,

  p1Payroll: 0,
  p2Payroll: 0,
  payrollDiff: 0,
  payrollGrowth: 0,

  p1Profit: 0,
  p2Profit: 0,
  profitDiff: 0,
  profitGrowth: 0,

  p1Margin: 0,
  p2Margin: 0,
  marginDiff: 0
})

const comparisonTable = ref<any[]>([])

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

const formatDateStr = (d: Date) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const getCurrentMonth = () => {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  return `${y}-${m}`
}

const getLastMonth = () => {
  const d = new Date()
  d.setMonth(d.getMonth() - 1)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  return `${y}-${m}`
}

// ══════════════════════════════════════════════════════════════
// MONTHLY FINANCIAL CLOSING & SALES TABLE STATE
// ══════════════════════════════════════════════════════════════
const closeMonthInput = ref(getCurrentMonth())
const closeMonthRemark = ref('')
const closingSubmitting = ref(false)
const savedSnapshots = ref<MonthlyFinancialSnapshotItem[]>([])
const snapshotsLoading = ref(false)
const selectedSnapshotDetail = ref<MonthlyFinancialSnapshotItem | null>(null)
const detailDialogVisible = ref(false)
const currentMonthSummary = ref<MonthSummaryData | null>(null)

// Bottom Table Mode: 'sales' (Monthly Sales List) or 'archive' (Historical Snapshots)
const bottomTableMode = ref<'sales' | 'archive'>('sales')
const monthlySalesFilterSearch = ref('')
const monthlySalesFilterPayment = ref('all')
const selectedSaleDetail = ref<SaleType | null>(null)
const saleDetailDialogVisible = ref(false)

// Quick jump months helper (Dynamically generated from current date)
const quickJumpMonths = computed(() => {
  const d = new Date()
  const res: Array<{ label: string; value: string; tip: string }> = []
  const monthNames = [
    t('analysis.january') || 'Yanvar',
    t('analysis.february') || 'Fevral',
    t('analysis.march') || 'Mart',
    t('analysis.april') || 'Aprel',
    t('analysis.may') || 'May',
    t('analysis.june') || 'Iyun',
    t('analysis.july') || 'Iyul',
    t('analysis.august') || 'Avgust',
    t('analysis.september') || 'Sentabr',
    t('analysis.october') || 'Oktabr',
    t('analysis.november') || 'Noyabr',
    t('analysis.december') || 'Dekabr'
  ]
  for (let i = 0; i < 4; i++) {
    const dt = new Date(d.getFullYear(), d.getMonth() - i, 1)
    const ym = `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}`
    const mName = monthNames[dt.getMonth()]
    const label =
      i === 0
        ? `${t('erp.currentMonthPill')} (${mName})`
        : i === 1
          ? `${t('erp.prevMonthPill')} (${mName})`
          : `${mName} ${dt.getFullYear()}`
    res.push({
      label,
      value: ym,
      tip: `${ym} ${t('analysis.tipSelectMonth')}`
    })
  }
  return res
})

// Filtered Monthly Sales Data
const filteredMonthlySales = computed(() => {
  const targetMonth = closeMonthInput.value
  let list = allRawSales.value

  // Month filter: if sale created_at matches targetMonth
  if (targetMonth) {
    list = list.filter((s) => (s.created_at || '').startsWith(targetMonth))
  }

  // Search query filter
  if (monthlySalesFilterSearch.value) {
    const q = monthlySalesFilterSearch.value.toLowerCase().trim()
    list = list.filter(
      (s) =>
        (s.receipt_number || '').toLowerCase().includes(q) ||
        (s.customer_name || '').toLowerCase().includes(q) ||
        (s.customer_phone || '').toLowerCase().includes(q) ||
        (s.cashier_name || '').toLowerCase().includes(q)
    )
  }

  // Payment method filter
  if (monthlySalesFilterPayment.value !== 'all') {
    list = list.filter((s) => s.payment_method === monthlySalesFilterPayment.value)
  }

  return list
})

const totalMonthlySalesRevenue = computed(() => {
  return filteredMonthlySales.value.reduce(
    (sum, s) => sum + (parseFloat(String(s.total_amount || (s as any).total || 0)) || 0),
    0
  )
})

const totalMonthlySalesPaid = computed(() => {
  return filteredMonthlySales.value.reduce(
    (sum, s) => sum + (parseFloat(String(s.paid_amount || 0)) || 0),
    0
  )
})

const totalMonthlySalesDebt = computed(() => {
  return filteredMonthlySales.value.reduce(
    (sum, s) => sum + (parseFloat(String(s.debt_amount || 0)) || 0),
    0
  )
})

const openSaleDetail = (sale: SaleType) => {
  selectedSaleDetail.value = sale
  saleDetailDialogVisible.value = true
}

// Fetch historical snapshots from DB
const fetchSavedSnapshots = async () => {
  snapshotsLoading.value = true
  try {
    const res = await getFinancialSnapshotsApi()
    if (res && res.data) {
      savedSnapshots.value = Array.isArray(res.data) ? res.data : (res.data as any).list || []
    } else {
      savedSnapshots.value = []
    }
    buildArchiveCharts()
  } catch (err) {
    console.error('Failed to load snapshots:', err)
    savedSnapshots.value = []
  } finally {
    snapshotsLoading.value = false
  }
}

// Check if currently selected month in closing view is already closed
const isSelectedMonthAlreadyClosed = computed(() => {
  if (!Array.isArray(savedSnapshots.value)) return false
  return savedSnapshots.value.some((s) => s.period_month === closeMonthInput.value)
})

const existingSnapshotForSelectedMonth = computed(() => {
  if (!Array.isArray(savedSnapshots.value)) return null
  return savedSnapshots.value.find((s) => s.period_month === closeMonthInput.value) || null
})

// Current month live preview calculation for closing
const closeMonthPreview = computed(() => {
  // If already closed in snapshot history, display frozen historical snapshot
  if (existingSnapshotForSelectedMonth.value) {
    const s = existingSnapshotForSelectedMonth.value
    return {
      revenue: s.revenue,
      totalPaid: (s as any).total_paid ?? s.revenue,
      totalDebt: (s as any).total_debt ?? 0,
      cogs: s.cogs,
      staffSalaries: s.staff_salaries,
      shortTerm: s.short_term_outputs,
      totalExpenses: s.total_expenses,
      netProfit: s.net_profit,
      margin: s.profit_margin,
      salesCount: s.sales_count,
      isFrozen: true
    }
  }

  // If backend month summary loaded, display live real summary
  if (currentMonthSummary.value) {
    const s = currentMonthSummary.value
    return {
      revenue: s.revenue,
      totalPaid: (s as any).totalPaid ?? totalMonthlySalesPaid.value,
      totalDebt: (s as any).totalDebt ?? totalMonthlySalesDebt.value,
      cogs: s.cogs,
      staffSalaries: s.staffSalaries,
      shortTerm: s.shortTermOutputs,
      totalExpenses: s.totalExpenses,
      netProfit: s.netProfit,
      margin: s.profitMargin,
      salesCount: s.salesCount,
      isFrozen: false
    }
  }

  return {
    revenue: totalMonthlySalesRevenue.value,
    totalPaid: totalMonthlySalesPaid.value,
    totalDebt: totalMonthlySalesDebt.value,
    cogs: 0,
    staffSalaries: 0,
    shortTerm: 0,
    totalExpenses: 0,
    netProfit: 0,
    margin: 0,
    salesCount: filteredMonthlySales.value.length,
    isFrozen: false
  }
})

// Fetch single month summary for Closing mode
const fetchMonthSummary = async () => {
  closingLoading.value = true
  try {
    const res = await getMonthSummaryApi({ month: closeMonthInput.value })
    if (res && res.data) {
      currentMonthSummary.value = res.data
    }
  } catch (err) {
    console.error('Failed to fetch month summary:', err)
  } finally {
    closingLoading.value = false
    buildArchiveCharts()
  }
}

// Action: Close and Archive Month
const handleCloseMonth = async () => {
  const month = closeMonthInput.value
  if (!month) {
    ElMessage.warning(t('analysis.selectMonthWarn'))
    return
  }

  ElMessageBox.confirm(
    `Ҳақиқатан ҳам <b>${month}</b> ойи молиявий ҳисоботини ёпиш ва тарихга муҳрлашни хоҳлайсизми?<br/><br/><small class="text-gray-500">* Ёпилгандан сўнг натижалар доимий архивга сақланади ва янги ой ҳисоблагичлари янгидан ишга тушади.</small>`,
    'Ойлик Ҳисоботни Муҳрлаш',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: t('analysis.confirmCloseBtn'),
      cancelButtonText: t('analysis.cancelBtn'),
      type: 'warning'
    }
  )
    .then(async () => {
      closingSubmitting.value = true
      try {
        const res = await closeMonthlyFinancialSnapshotApi({
          period_month: month,
          remark: closeMonthRemark.value || `${month} ойи якуний молиявий ҳисоботи (Ёпилди)`
        })
        if (res && res.code === 0) {
          ElMessage.success(
            (res as any).message || `${month} ойи молиявий ҳисоботи муваффақиятли ёпилди!`
          )
          closeMonthRemark.value = ''
          await fetchSavedSnapshots()
          await fetchMonthSummary()
          await loadStandardOverview()
        }
      } catch (err: any) {
        console.error(err)
        ElMessage.error(err?.response?.data?.message || 'Ҳисоботни ёпишда хатолик юз берди')
      } finally {
        closingSubmitting.value = false
      }
    })
    .catch(() => {})
}

// Action: Delete snapshot from history
const handleDeleteSnapshot = (row: MonthlyFinancialSnapshotItem) => {
  ElMessageBox.confirm(
    `<b>${row.period_month}</b> ойи архив ҳисоботини ўчиришни тасдиқлайсизми?`,
    'Тарихни ўчириш',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: t('analysis.deleteBtn'),
      cancelButtonText: t('analysis.cancelBtn'),
      type: 'warning'
    }
  )
    .then(async () => {
      const res = await deleteFinancialSnapshotApi({ id: row.id, period_month: row.period_month })
      if (res && res.code === 0) {
        ElMessage.success('Архивдан ўчирилди')
        await fetchSavedSnapshots()
        await fetchMonthSummary()
        await loadStandardOverview()
      }
    })
    .catch(() => {})
}

// Action: View snapshot details modal
const handleViewSnapshotDetail = (row: MonthlyFinancialSnapshotItem) => {
  selectedSnapshotDetail.value = row
  detailDialogVisible.value = true
}

const buildArchiveCharts = () => {
  const dark = isDark.value
  const textColor = dark ? '#f1f5f9' : '#1e293b'
  const subTextColor = dark ? '#94a3b8' : '#64748b'
  const gridLineColor = dark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(0, 0, 0, 0.06)'
  const axisLineColor = dark ? '#334155' : '#cbd5e1'
  const tooltipBg = dark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.96)'
  const tooltipBorder = dark ? '#334155' : '#e2e8f0'

  const cur = closeMonthPreview.value

  // 1. DUAL-RING ROTATING DONUT & PROFIT RADIUS CHART
  const donutData = [
    {
      value: cur.cogs,
      name: t('erp.costCogs'),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#f59e0b' },
            { offset: 1, color: '#d97706' }
          ]
        }
      }
    },
    {
      value: cur.staffSalaries,
      name: `${t('analysis.permanentSalaries')} & Avans`,
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#a855f7' },
            { offset: 1, color: '#7c3aed' }
          ]
        }
      }
    },
    {
      value: cur.shortTerm,
      name: t('analysis.shortTermWorkers'),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#ec4899' },
            { offset: 1, color: '#be185d' }
          ]
        }
      }
    },
    {
      value: Math.max(0, cur.netProfit),
      name: t('erp.realNetProfit'),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#10b981' },
            { offset: 1, color: '#059669' }
          ]
        },
        shadowBlur: 14,
        shadowColor: 'rgba(16, 185, 129, 0.45)'
      }
    }
  ]

  monthDistributionDonutOptions.value = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      borderWidth: 1,
      textStyle: { color: textColor },
      formatter: (params: any) => {
        return `<div style="font-weight: 700; color: ${textColor}">${params.name}</div>
        <div style="font-family: monospace; font-size: 15px; font-weight: 800; color: ${params.color}">
          $${formatMoney(params.value)} (${params.percent}%)
        </div>`
      }
    },
    series: [
      {
        name: t('erp.financialDistributionRing'),
        type: 'pie',
        radius: ['60%', '84%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: dark ? '#0f172a' : '#ffffff',
          borderWidth: 3
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          scale: true,
          scaleSize: 8,
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            formatter: '{b}\n${c}'
          }
        },
        data: donutData
      }
    ]
  } as any

  // 2. 6-MONTH ROLLING EVOLUTION TIMELINE FROM REAL HISTORICAL DATA
  const hist = overviewData.value?.monthlyFinancials || []
  const last6 = hist.slice(-6)
  const months = last6.map((m) => m.month)
  const timelineRevs = last6.map((m) => m.revenue)
  const timelineExps = last6.map((m) => m.totalExpenses)
  const timelineProfs = last6.map((m) => m.netProfit)

  archiveHistoryTimelineOptions.value = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      borderWidth: 1,
      textStyle: { color: textColor },
      axisPointer: {
        type: 'cross',
        crossStyle: { color: '#3b82f6', width: 1, type: 'dashed' }
      },
      formatter: (params: any) => {
        let title = `<div style="font-weight: 800; font-size: 13px; margin-bottom: 6px; color: ${textColor}">${params[0].name}</div>`
        params.forEach((item: any) => {
          title += `<div style="display: flex; justify-content: space-between; gap: 16px; margin: 4px 0;">
            <span style="display: flex; align-items: center; gap: 6px;">
              <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ${item.color};"></span>
              ${item.seriesName}
            </span>
            <span style="font-weight: 800; font-family: monospace; color: ${item.color}">$${formatMoney(item.value)}</span>
          </div>`
        })
        return title
      }
    },
    legend: {
      data: [t('erp.totalSalesSavdo'), t('erp.totalExpenses'), t('erp.realNetProfit')],
      top: 4,
      textStyle: { color: textColor, fontSize: 12, fontWeight: 600 },
      itemGap: 18
    },
    grid: { left: '3%', right: '3%', bottom: '5%', top: '16%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: months,
      axisLabel: { color: subTextColor, fontSize: 12, fontWeight: 600 },
      axisLine: { lineStyle: { color: axisLineColor } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: subTextColor,
        fontSize: 11,
        formatter: (v: number) => '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v)
      },
      splitLine: { lineStyle: { color: gridLineColor, type: 'dashed' } }
    },
    series: [
      {
        name: t('erp.totalSalesSavdo'),
        type: 'line',
        smooth: true,
        data: timelineRevs,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { color: '#3b82f6', borderWidth: 2, borderColor: '#ffffff' },
        lineStyle: { width: 3, shadowColor: 'rgba(59, 130, 246, 0.4)', shadowBlur: 10 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(59, 130, 246, 0.25)' },
              { offset: 1, color: 'rgba(59, 130, 246, 0.01)' }
            ]
          }
        }
      },
      {
        name: t('erp.totalExpenses'),
        type: 'line',
        smooth: true,
        data: timelineExps,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#f43f5e' },
        lineStyle: { width: 2, type: 'dashed' }
      },
      {
        name: t('erp.realNetProfit'),
        type: 'line',
        smooth: true,
        data: timelineProfs,
        symbol: 'diamond',
        symbolSize: 10,
        itemStyle: { color: '#10b981', borderWidth: 3, borderColor: '#ffffff' },
        lineStyle: { width: 4, shadowColor: 'rgba(16, 185, 129, 0.5)', shadowBlur: 12 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(16, 185, 129, 0.45)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.01)' }
            ]
          }
        }
      }
    ]
  }
}

watch(
  () => closeMonthInput.value,
  (newMonth) => {
    fetchMonthSummary()
    loadRawSales(newMonth)
  }
)

watch(
  () => isDark.value,
  () => {
    buildArchiveCharts()
  }
)

watch(
  () => activeViewTab.value,
  (newTab) => {
    if (newTab === 'closing') {
      if (!currentMonthSummary.value) fetchMonthSummary()
      if (savedSnapshots.value.length === 0) fetchSavedSnapshots()
      if (allRawSales.value.length === 0) loadRawSales(closeMonthInput.value)
    } else if (newTab === 'compare') {
      updateComparisonCalculations()
    } else if (newTab === 'standard') {
      if (!overviewData.value) loadStandardOverview()
    }
  }
)

// ══════════════════════════════════════════════════════════════
// COMPARISON MODE CALCULATIONS POWERED BY BACKEND API
// ══════════════════════════════════════════════════════════════
const updateComparisonCalculations = async () => {
  comparisonLoading.value = true
  const d = new Date()
  const todayStr = formatDateStr(d)

  let p1Start = ''
  let p1End = ''
  let p2Start = ''
  let p2End = ''

  if (comparePreset.value === 'mom') {
    // Current month vs Previous month
    const currFirst = new Date(d.getFullYear(), d.getMonth(), 1)
    const prevFirst = new Date(d.getFullYear(), d.getMonth() - 1, 1)
    const prevLast = new Date(d.getFullYear(), d.getMonth(), 0)

    p1Start = formatDateStr(currFirst)
    p1End = todayStr
    p2Start = formatDateStr(prevFirst)
    p2End = formatDateStr(prevLast)

    period1Label.value = `${t('erp.currentMonthPill')} (${p1Start.slice(0, 7)})`
    period2Label.value = `${t('erp.prevMonthPill')} (${p2Start.slice(0, 7)})`
  } else if (comparePreset.value === 'qoq') {
    // Current Quarter vs Previous Quarter
    const currQuarter = Math.floor(d.getMonth() / 3)
    const q1StartMonth = currQuarter * 3
    const q1Start = new Date(d.getFullYear(), q1StartMonth, 1)
    const q1End = new Date(d.getFullYear(), q1StartMonth + 3, 0)

    const q2StartMonth = (currQuarter - 1) * 3
    const q2Year = q2StartMonth < 0 ? d.getFullYear() - 1 : d.getFullYear()
    const normQ2Month = (q2StartMonth + 12) % 12
    const q2Start = new Date(q2Year, normQ2Month, 1)
    const q2End = new Date(q2Year, normQ2Month + 3, 0)

    p1Start = formatDateStr(q1Start)
    p1End = formatDateStr(q1End)
    p2Start = formatDateStr(q2Start)
    p2End = formatDateStr(q2End)

    period1Label.value = `Q${currQuarter + 1} ${d.getFullYear()}`
    period2Label.value = `Q${currQuarter === 0 ? 4 : currQuarter} ${q2Year}`
  } else if (comparePreset.value === 'last30') {
    // Last 30 Days vs Previous 30 Days
    const p1StartDate = new Date(d.getTime() - 29 * 86400000)
    const p2EndDate = new Date(d.getTime() - 30 * 86400000)
    const p2StartDate = new Date(d.getTime() - 59 * 86400000)

    p1Start = formatDateStr(p1StartDate)
    p1End = todayStr
    p2Start = formatDateStr(p2StartDate)
    p2End = formatDateStr(p2EndDate)

    period1Label.value = `${t('analysis.compareLast30')}`
    period2Label.value = `${t('erp.prevMonthPill')} (30d)`
  } else if (comparePreset.value === 'yoy') {
    // Current year vs Last year
    p1Start = `${d.getFullYear()}-01-01`
    p1End = `${d.getFullYear()}-12-31`
    p2Start = `${d.getFullYear() - 1}-01-01`
    p2End = `${d.getFullYear() - 1}-12-31`

    period1Label.value = `${d.getFullYear()} (${t('analysis.yearly')})`
    period2Label.value = `${d.getFullYear() - 1} (${t('analysis.yearly')})`
  } else if (comparePreset.value === 'custom') {
    if (
      Array.isArray(period1Dates.value) &&
      period1Dates.value.length === 2 &&
      period1Dates.value[0] &&
      period1Dates.value[1] &&
      Array.isArray(period2Dates.value) &&
      period2Dates.value.length === 2 &&
      period2Dates.value[0] &&
      period2Dates.value[1]
    ) {
      p1Start = String(period1Dates.value[0])
      p1End = String(period1Dates.value[1])
      p2Start = String(period2Dates.value[0])
      p2End = String(period2Dates.value[1])
    } else {
      // Fallback custom dates without mutating watched refs
      p1Start = `${d.getFullYear()}-08-01`
      p1End = `${d.getFullYear()}-08-31`
      p2Start = `${d.getFullYear()}-07-01`
      p2End = `${d.getFullYear()}-07-31`
    }
    period1Label.value = `${t('analysis.period1')} (${p1Start} ~ ${p1End})`
    period2Label.value = `${t('analysis.period2')} (${p2Start} ~ ${p2End})`
  }

  if (!p1Start || !p1End || !p2Start || !p2End) {
    comparisonLoading.value = false
    return
  }

  try {
    const res = await comparePeriodsApi({
      period1_start: p1Start,
      period1_end: p1End,
      period2_start: p2Start,
      period2_end: p2End
    })

    if (res && res.data) {
      applyComparisonData(res.data)
    }
  } catch (err) {
    console.error('Failed to update period comparison:', err)
  } finally {
    comparisonLoading.value = false
  }
}

const applyComparisonData = (compData: any) => {
  if (!compData) return
  const period1 = compData.period1 || {}
  const period2 = compData.period2 || {}

  const p1Rev = Number(period1.revenue) || 0
  const p2Rev = Number(period2.revenue) || 0
  const p1Cogs = Number(period1.cogs) || 0
  const p2Cogs = Number(period2.cogs) || 0
  const p1Staff = Number(period1.staff_salaries ?? period1.staffSalaries) || 0
  const p2Staff = Number(period2.staff_salaries ?? period2.staffSalaries) || 0
  const p1Short = Number(period1.short_term_outputs ?? period1.shortTermOutputs) || 0
  const p2Short = Number(period2.short_term_outputs ?? period2.shortTermOutputs) || 0
  const p1Payroll = Number(period1.total_payroll ?? period1.totalPayroll) || p1Staff + p1Short
  const p2Payroll = Number(period2.total_payroll ?? period2.totalPayroll) || p2Staff + p2Short
  const p1Profit = Number(period1.net_profit ?? period1.netProfit) || p1Rev - p1Cogs - p1Payroll
  const p2Profit = Number(period2.net_profit ?? period2.netProfit) || p2Rev - p2Cogs - p2Payroll
  const p1Margin =
    Number(period1.profit_margin ?? period1.margin) || (p1Rev > 0 ? (p1Profit / p1Rev) * 100 : 0)
  const p2Margin =
    Number(period2.profit_margin ?? period2.margin) || (p2Rev > 0 ? (p2Profit / p2Rev) * 100 : 0)

  const calcGrowth = (p1Val: number, p2Val: number) => {
    if (p2Val === 0) return p1Val === 0 ? 0 : 100
    return Math.round(((p1Val - p2Val) / Math.abs(p2Val)) * 1000) / 10
  }

  const rawDeltas = compData.deltas || {}
  const deltas = {
    revDiff: rawDeltas.revDiff ?? Math.round((p1Rev - p2Rev) * 100) / 100,
    revGrowth: rawDeltas.revGrowth ?? calcGrowth(p1Rev, p2Rev),
    cogsDiff: rawDeltas.cogsDiff ?? Math.round((p1Cogs - p2Cogs) * 100) / 100,
    cogsGrowth: rawDeltas.cogsGrowth ?? calcGrowth(p1Cogs, p2Cogs),
    staffDiff: rawDeltas.staffDiff ?? Math.round((p1Staff - p2Staff) * 100) / 100,
    staffGrowth: rawDeltas.staffGrowth ?? calcGrowth(p1Staff, p2Staff),
    shortDiff: rawDeltas.shortDiff ?? Math.round((p1Short - p2Short) * 100) / 100,
    shortGrowth: rawDeltas.shortGrowth ?? calcGrowth(p1Short, p2Short),
    payrollDiff: rawDeltas.payrollDiff ?? Math.round((p1Payroll - p2Payroll) * 100) / 100,
    payrollGrowth: rawDeltas.payrollGrowth ?? calcGrowth(p1Payroll, p2Payroll),
    profitDiff: rawDeltas.profitDiff ?? Math.round((p1Profit - p2Profit) * 100) / 100,
    profitGrowth: rawDeltas.profitGrowth ?? calcGrowth(p1Profit, p2Profit),
    marginDiff: rawDeltas.marginDiff ?? Math.round((p1Margin - p2Margin) * 10) / 10
  }

  comparisonData.p1Revenue = p1Rev
  comparisonData.p2Revenue = p2Rev
  comparisonData.revDiff = deltas.revDiff
  comparisonData.revGrowth = deltas.revGrowth

  comparisonData.p1COGS = p1Cogs
  comparisonData.p2COGS = p2Cogs
  comparisonData.cogsDiff = deltas.cogsDiff
  comparisonData.cogsGrowth = deltas.cogsGrowth

  comparisonData.p1Payroll = p1Payroll
  comparisonData.p2Payroll = p2Payroll
  comparisonData.payrollDiff = deltas.payrollDiff
  comparisonData.payrollGrowth = deltas.payrollGrowth

  comparisonData.p1Profit = p1Profit
  comparisonData.p2Profit = p2Profit
  comparisonData.profitDiff = deltas.profitDiff
  comparisonData.profitGrowth = deltas.profitGrowth

  comparisonData.p1Margin = p1Margin
  comparisonData.p2Margin = p2Margin
  comparisonData.marginDiff = deltas.marginDiff

  // Update comparison table with real data
  comparisonTable.value = [
    {
      metric: 'Жами Тушум (Gross Revenue)',
      p1: p1Rev,
      p2: p2Rev,
      diff: deltas.revDiff,
      growth: deltas.revGrowth,
      status: deltas.revGrowth >= 0 ? 'positive' : 'negative',
      desc: 'Барча сотилган товарлардан тушган ялпи даромад',
      tooltip:
        'Сотувлар орқали корхонага кирган умумий сумма. Қанча юқори бўлса, савдо ҳажми шунча яхши.'
    },
    {
      metric: 'Маҳсулот Таннархи (COGS)',
      p1: p1Cogs,
      p2: p2Cogs,
      diff: deltas.cogsDiff,
      growth: deltas.cogsGrowth,
      status: deltas.cogsGrowth <= 0 ? 'positive' : 'negative',
      desc: 'Сотилган товарларнинг асл харид ва тайёрлаш қиймати',
      tooltip:
        'Маҳсулотларни омборга олиб келиш ёки ишлаб чиқариш учун сарфланган тўғридан-тўғри харажат.'
    },
    {
      metric: 'Доимий Ишчиlar Маоши (Staff Salaries)',
      p1: p1Staff,
      p2: p2Staff,
      diff: deltas.staffDiff,
      growth: deltas.staffGrowth,
      status: 'neutral',
      desc: 'Доимий штатдаги ходимларнинг белгиланган тариф ойликлари',
      tooltip: 'Ҳар ой ходимларга тўланадиган қатъий белгиланган асосий ойлик маошлар йиғиндиси.'
    },
    {
      metric: 'Қисқа Муддатли Ишчилар (Piece-rate / Выработка)',
      p1: p1Short,
      p2: p2Short,
      diff: deltas.shortDiff,
      growth: deltas.shortGrowth,
      status: 'neutral',
      desc: 'Ҳосил ёки бажарилган иш ҳажми бўйича тўланган иш ҳақи',
      tooltip: 'Вақтинча ёки донабай (выработка) ишчилар бажарган ҳажмларига қараб олган тўловлар.'
    },
    {
      metric: 'Жами Иш Ҳақи Харажатлари (Total Payroll)',
      p1: p1Payroll,
      p2: p2Payroll,
      diff: deltas.payrollDiff,
      growth: deltas.payrollGrowth,
      status: deltas.payrollGrowth <= 0 ? 'positive' : 'negative',
      desc: 'Компаниянинг барча ойлик тўловлари йиғиндиси',
      tooltip: 'Доимий ойликлар ва қўшимча иш ҳажми учун тўланган барча меҳнат харажатлари суммаси.'
    },
    {
      metric: `${t('erp.realNetProfit')} (Real Net Profit)`,
      p1: p1Profit,
      p2: p2Profit,
      diff: deltas.profitDiff,
      growth: deltas.profitGrowth,
      status: deltas.profitGrowth >= 0 ? 'positive' : 'negative',
      desc: 'Таннарх ва барча ойликлар чегирилган тоза фойда',
      tooltip: 'Компаниянинг барча харажатларидан кейин тоза чўнтагига қолган ҳақиқий даромад.'
    },
    {
      metric: 'Рентабеллик Маржаси (Profit Margin %)',
      p1: p1Margin,
      p2: p2Margin,
      diff: deltas.marginDiff,
      growth: deltas.marginDiff,
      isPercentage: true,
      status: deltas.marginDiff >= 0 ? 'positive' : 'negative',
      desc: 'Соф фойданинг умумий тушумдаги фоиз улуши',
      tooltip:
        'Ҳар $100 долларлик савдодан компанияга неча доллар соф фойда қолаётганини кўрсатувчи самарадорлик индекси.'
    }
  ]

  buildComparisonChartOptions()
}

const buildComparisonChartOptions = () => {
  const dark = isDark.value
  const textColor = dark ? '#f1f5f9' : '#1e293b'
  const subTextColor = dark ? '#94a3b8' : '#64748b'
  const gridLineColor = dark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(0, 0, 0, 0.06)'
  const axisLineColor = dark ? '#334155' : '#cbd5e1'
  const tooltipBg = dark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.96)'
  const tooltipBorder = dark ? '#334155' : '#e2e8f0'

  const categories = [
    t('analysis.grossRevenue'),
    t('erp.costCogs'),
    t('analysis.totalPayroll'),
    t('erp.realNetProfit')
  ]

  const p1SeriesData = [
    comparisonData.p1Revenue,
    comparisonData.p1COGS,
    comparisonData.p1Payroll,
    comparisonData.p1Profit
  ]

  const p2SeriesData = [
    comparisonData.p2Revenue,
    comparisonData.p2COGS,
    comparisonData.p2Payroll,
    comparisonData.p2Profit
  ]

  // 1. Comparison Side-by-Side Bar Chart
  comparisonBarOptions.value = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      borderWidth: 1,
      textStyle: { color: textColor },
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        let title = `<div style="font-weight: 700; margin-bottom: 6px; color: ${textColor}">${params[0].name}</div>`
        params.forEach((item: any) => {
          const val = typeof item.value === 'number' ? '$' + formatMoney(item.value) : item.value
          title += `<div style="display: flex; justify-content: space-between; gap: 16px; margin: 3px 0;">
            <span style="display: flex; align-items: center; gap: 6px;">
              <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ${item.color};"></span>
              ${item.seriesName}
            </span>
            <span style="font-weight: 700; font-family: monospace;">${val}</span>
          </div>`
        })
        return title
      }
    },
    legend: {
      data: [period1Label.value, period2Label.value],
      top: 4,
      textStyle: { color: textColor, fontSize: 12, fontWeight: 600 },
      itemGap: 16
    },
    grid: { left: '3%', right: '3%', bottom: '5%', top: '16%', containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: textColor, fontSize: 12, fontWeight: 600 },
      axisLine: { lineStyle: { color: axisLineColor } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: subTextColor,
        fontSize: 11,
        formatter: (v: number) => '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v)
      },
      splitLine: { lineStyle: { color: gridLineColor, type: 'dashed' } }
    },
    series: [
      {
        name: period1Label.value,
        type: 'bar',
        barWidth: 24,
        data: p1SeriesData,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#3b82f6' },
              { offset: 1, color: '#1d4ed8' }
            ]
          },
          borderRadius: [6, 6, 0, 0]
        }
      },
      {
        name: period2Label.value,
        type: 'bar',
        barWidth: 24,
        data: p2SeriesData,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#f59e0b' },
              { offset: 1, color: '#d97706' }
            ]
          },
          borderRadius: [6, 6, 0, 0]
        }
      }
    ]
  }

  // 2. Comparison Donut/Category Options
  comparisonCategoryOptions.value = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      borderWidth: 1,
      textStyle: { color: textColor }
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      textStyle: { color: textColor, fontSize: 11 }
    },
    series: [
      {
        name: period1Label.value,
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: dark ? '#0f172a' : '#ffffff',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            fontSize: 13,
            fontWeight: 'bold',
            formatter: '{b}\n${c}'
          }
        },
        data: [
          {
            value: comparisonData.p1COGS,
            name: t('erp.costCogs'),
            itemStyle: { color: '#f59e0b' }
          },
          {
            value: comparisonData.p1Payroll,
            name: t('analysis.totalPayroll'),
            itemStyle: { color: '#a855f7' }
          },
          {
            value: Math.max(0, comparisonData.p1Profit),
            name: t('erp.realNetProfit'),
            itemStyle: { color: '#10b981' }
          }
        ]
      }
    ]
  }
}

const buildChartOptions = () => {
  if (!overviewData.value) return
  const data = overviewData.value
  const monthly = Array.isArray(data.monthlyFinancials) ? data.monthlyFinancials : []
  const months = monthly.map((m) => m.month || m.period_month || '')
  const revList = monthly.map((m) => m.revenue || 0)
  const cogsList = monthly.map((m) => m.cogs || 0)
  const staffList = monthly.map((m) => m.staffSalaries || m.staff_salaries || 0)
  const shortTermList = monthly.map((m) => m.shortTermOutputs || m.short_term_outputs || 0)
  const profitList = monthly.map((m) => m.netProfit || m.net_profit || 0)

  const dark = isDark.value
  const textColor = dark ? '#f1f5f9' : '#1e293b'
  const subTextColor = dark ? '#94a3b8' : '#64748b'
  const gridLineColor = dark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(0, 0, 0, 0.06)'
  const axisLineColor = dark ? '#334155' : '#cbd5e1'
  const tooltipBg = dark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.96)'
  const tooltipBorder = dark ? '#334155' : '#e2e8f0'

  // 1. Dynamic Financial Trend Line
  financialTrendOptions.value = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      borderWidth: 1,
      textStyle: { color: textColor },
      axisPointer: { type: 'cross', crossStyle: { color: '#999' } },
      formatter: (params: any) => {
        let title = `<div style="font-weight: 700; margin-bottom: 6px; color: ${textColor}">${params[0].name}</div>`
        params.forEach((item: any) => {
          title += `<div style="display: flex; justify-content: space-between; gap: 16px; margin: 3px 0;">
            <span style="display: flex; align-items: center; gap: 6px;">
              <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ${item.color};"></span>
              ${item.seriesName}
            </span>
            <span style="font-weight: 700; font-family: monospace;">$${formatMoney(item.value)}</span>
          </div>`
        })
        return title
      }
    },
    legend: {
      data: [
        t('analysis.grossRevenue'),
        t('analysis.cogs'),
        t('analysis.permanentSalaries'),
        t('analysis.shortTermWorkers'),
        t('analysis.realNetProfit')
      ],
      top: 4,
      textStyle: { color: textColor, fontSize: 12, fontWeight: 500 },
      itemGap: 16
    },
    grid: { left: '2%', right: '3%', bottom: '3%', top: '16%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: months,
      axisLabel: { color: subTextColor, fontSize: 12, fontWeight: 500 },
      axisLine: { lineStyle: { color: axisLineColor } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: subTextColor,
        fontSize: 11,
        formatter: (v: number) => '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v)
      },
      splitLine: { lineStyle: { color: gridLineColor, type: 'dashed' } }
    },
    series: [
      {
        name: t('analysis.grossRevenue'),
        type: 'line',
        smooth: true,
        data: revList,
        itemStyle: { color: '#3b82f6' },
        lineStyle: { width: 3 },
        showSymbol: false
      },
      {
        name: t('analysis.cogs'),
        type: 'line',
        smooth: true,
        data: cogsList,
        itemStyle: { color: '#f59e0b' },
        lineStyle: { width: 2, type: 'dashed' },
        showSymbol: false
      },
      {
        name: t('analysis.permanentSalaries'),
        type: 'line',
        smooth: true,
        data: staffList,
        itemStyle: { color: '#a855f7' },
        lineStyle: { width: 2 },
        showSymbol: false
      },
      {
        name: t('analysis.shortTermWorkers'),
        type: 'line',
        smooth: true,
        data: shortTermList,
        itemStyle: { color: '#ec4899' },
        lineStyle: { width: 2 },
        showSymbol: false
      },
      {
        name: t('analysis.realNetProfit'),
        type: 'line',
        smooth: true,
        data: profitList,
        itemStyle: { color: '#10b981' },
        lineStyle: { width: 4 },
        showSymbol: false,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(16, 185, 129, 0.45)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.01)' }
            ]
          }
        }
      }
    ]
  }

  // 2. Expense Structure Donut Chart
  expenseStructureOptions.value = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      borderWidth: 1,
      textStyle: { color: textColor },
      formatter: (p: any) => `${p.name}: <b>$${formatMoney(p.value)}</b> (${p.percent}%)`
    },
    legend: {
      orient: 'vertical',
      left: '4%',
      top: 'middle',
      itemGap: 14,
      textStyle: { color: textColor, fontSize: 12, fontWeight: 500 }
    },
    series: [
      {
        name: t('analysis.expenseStructure'),
        type: 'pie',
        radius: ['52%', '78%'],
        center: ['65%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: dark ? '#0f172a' : '#ffffff',
          borderWidth: 3
        },
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            formatter: '{b}\n${c}'
          }
        },
        data: [
          {
            value: data.cogs,
            name: t('analysis.cogs'),
            itemStyle: { color: '#f59e0b' }
          },
          {
            value: data.staffSalaries,
            name: t('analysis.permanentSalaries'),
            itemStyle: { color: '#a855f7' }
          },
          {
            value: data.shortTermOutputs,
            name: t('analysis.shortTermWorkers'),
            itemStyle: { color: '#ec4899' }
          }
        ]
      }
    ]
  }

  // 3. Category Profitability Breakdown
  const catNames = (data.categoryProfits || []).map((c) => c.name)
  const catRevenues = (data.categoryProfits || []).map((c) => c.revenue)
  const catProfits = (data.categoryProfits || []).map((c) => c.profit)

  categoryProfitOptions.value = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      borderWidth: 1,
      textStyle: { color: textColor },
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: [t('analysis.totalSalesValue'), t('analysis.netProfitShare')],
      top: 4,
      textStyle: { color: textColor, fontSize: 12, fontWeight: 500 }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '16%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: {
        color: subTextColor,
        fontSize: 11,
        formatter: (v: number) => '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v)
      },
      splitLine: { lineStyle: { color: gridLineColor, type: 'dashed' } }
    },
    yAxis: {
      type: 'category',
      data: catNames,
      axisLabel: {
        color: textColor,
        fontSize: 12,
        fontWeight: 600,
        width: 140,
        overflow: 'truncate'
      },
      axisLine: { lineStyle: { color: axisLineColor } }
    },
    series: [
      {
        name: t('analysis.totalSalesValue'),
        type: 'bar',
        barWidth: 10,
        barGap: '30%',
        barCategoryGap: '35%',
        data: catRevenues,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#2563eb' },
              { offset: 1, color: '#38bdf8' }
            ]
          },
          borderRadius: [0, 5, 5, 0]
        }
      },
      {
        name: t('analysis.netProfitShare'),
        type: 'bar',
        barWidth: 10,
        barGap: '30%',
        barCategoryGap: '35%',
        data: catProfits,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#059669' },
              { offset: 1, color: '#34d399' }
            ]
          },
          borderRadius: [0, 5, 5, 0]
        }
      }
    ]
  }

  buildArchiveCharts()
}

// Watchers for locale & dark theme
watch(
  () => [localeStore.getCurrentLocale, isDark.value],
  () => {
    buildChartOptions()
    buildComparisonChartOptions()
    buildArchiveCharts()
  }
)

// Watcher for Time Range button toggle (6m vs 1y)
watch(timeRange, () => {
  loadStandardOverview()
})

// Watcher for Comparison Preset or Custom Dates
watch(
  () => [comparePreset.value, period1Dates.value, period2Dates.value],
  () => {
    updateComparisonCalculations()
  },
  { deep: true }
)

// Load Standard Analysis Overview from Backend
const loadStandardOverview = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    const res = await getFinancialOverviewApi({
      time_range: timeRange.value
    })
    if (res && res.data) {
      overviewData.value = res.data
      monthlyFinancialTable.value = [...(res.data.monthlyFinancials || [])].reverse()
      buildChartOptions()
    }
  } catch (err) {
    console.error('Failed to load standard overview:', err)
  } finally {
    if (!silent) loading.value = false
  }
}

// Load POS / Sales for Monthly Sales Table (fast month-filtered query)
const loadRawSales = async (month?: string) => {
  salesLoading.value = true
  try {
    const targetMonth = month || closeMonthInput.value
    const res = await getSalesListApi({
      pageIndex: 1,
      pageSize: 200,
      month: targetMonth
    })
    if (res && res.data) {
      allRawSales.value = Array.isArray(res.data.list) ? res.data.list : []
    }
  } catch (err) {
    console.error('Failed to load sales list:', err)
  } finally {
    salesLoading.value = false
  }
}

// Master reload function - fetches ALL sections at once in a SINGLE network request
const loadAnalyticsData = async () => {
  loading.value = true
  closingLoading.value = true
  comparisonLoading.value = true
  try {
    loadRawSales(closeMonthInput.value)
    const res = await getAnalysisBundleApi({
      time_range: timeRange.value,
      month: closeMonthInput.value
    })
    if (res && res.data) {
      const { overview, snapshots, monthSummary, comparison } = res.data
      if (overview) {
        overviewData.value = overview
        monthlyFinancialTable.value = [...(overview.monthlyFinancials || [])].reverse()
        buildChartOptions()
      }
      if (snapshots) {
        savedSnapshots.value = snapshots
      }
      if (monthSummary) {
        currentMonthSummary.value = monthSummary
        buildArchiveCharts()
      }
      if (comparison) {
        applyComparisonData(comparison)
      }
    }
  } catch (err) {
    console.error('Failed to load analytics bundle:', err)
  } finally {
    loading.value = false
    closingLoading.value = false
    comparisonLoading.value = false
  }
}

// Silently update live analytics when sales, payouts, or product stock updates occur
useRealtimeSync(
  ['sale', 'salary', 'product'],
  () => {
    loadStandardOverview(true)
  }
)

// Excel Financial Export
const handleExportFinancialExcel = () => {
  if (!overviewData.value) {
    ElMessage.warning('Eksport qilish uchun moliyaviy maʼlumotlar topilmadi')
    return
  }

  const reportData = (overviewData.value.monthlyFinancials || []).map((item: any) => ({
    month: item.month,
    revenue: item.revenue || 0,
    cogs: item.cogs || 0,
    gross_profit: item.grossProfit || 0,
    salary_expense: item.salaryExpense || 0,
    other_expense: item.otherExpense || 0,
    profit: item.netProfit || 0,
    margin: `${(item.profitMargin || 0).toFixed(1)}%`
  }))

  exportToExcel(
    `Moliyaviy_Tahlil_Hisoboti_${dayjs().format('YYYY-MM-DD')}`,
    [
      { key: 'month', title: 'Oy' },
      { key: 'revenue', title: 'Tushum ($)', formatter: (v) => formatMoney(v || 0) },
      { key: 'cogs', title: 'Tannarx ($)', formatter: (v) => formatMoney(v || 0) },
      { key: 'gross_profit', title: 'Yalpi Foyda ($)', formatter: (v) => formatMoney(v || 0) },
      { key: 'salary_expense', title: 'Oylik Fondi ($)', formatter: (v) => formatMoney(v || 0) },
      { key: 'other_expense', title: 'Boshqa Xarajatlar ($)', formatter: (v) => formatMoney(v || 0) },
      { key: 'profit', title: 'Haqiqiy Sof Foyda ($)', formatter: (v) => formatMoney(v || 0) },
      { key: 'margin', title: 'Rentabellik (Marja)' }
    ],
    reportData
  )
  ElMessage.success('Moliyaviy hisobot Excel fayliga yuklab olindi!')
}

onMounted(() => {
  loadAnalyticsData()
})
</script>

<template>
  <div class="analysis-container">
    <!-- Top Mode Switch & Header Toolbar -->
    <div
      class="analytics-header-toolbar flex items-center justify-between flex-wrap gap-14px mb-20px"
    >
      <div class="flex items-center gap-12px">
        <div
          class="mode-pills flex items-center p-4px rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
        >
          <ElTooltip
            :content="t('analysis.tipStandardAnalysis') || t('analysis.standardAnalysis')"
            placement="top"
          >
            <button
              class="mode-btn"
              :class="{ active: activeViewTab === 'standard' }"
              @click="activeViewTab = 'standard'"
            >
              <Icon icon="vi-ep:data-line" class="mr-6px" /> {{ t('analysis.standardAnalysis') }}
            </button>
          </ElTooltip>

          <ElTooltip
            :content="t('analysis.tipMonthlyClosing') || t('analysis.monthlyClosing')"
            placement="top"
          >
            <button
              class="mode-btn mode-btn--archive"
              :class="{ active: activeViewTab === 'closing' }"
              @click="activeViewTab = 'closing'"
            >
              <Icon icon="ep:folder-checked" class="mr-6px" /> {{ t('analysis.monthlyClosing') }}
              <span v-if="savedSnapshots.length > 0" class="badge-count">{{
                savedSnapshots.length
              }}</span>
            </button>
          </ElTooltip>

          <ElTooltip
            :content="t('analysis.tipComparePeriods') || t('analysis.comparePeriods')"
            placement="top"
          >
            <button
              class="mode-btn"
              :class="{ active: activeViewTab === 'compare' }"
              @click="activeViewTab = 'compare'"
            >
              <Icon icon="vi-ep:switch" class="mr-6px" /> {{ t('analysis.comparePeriods') }}
            </button>
          </ElTooltip>
        </div>
      </div>

      <div class="flex items-center gap-10px flex-wrap">
        <ElButton
          type="success"
          plain
          class="!font-bold shadow-sm"
          @click="handleExportFinancialExcel"
        >
          <Icon icon="vi-ep:download" class="mr-6px" /> Excelga Hisobot
        </ElButton>
        <ElTooltip :content="t('analysis.tipRefresh') || t('common.refresh')" placement="top">
          <ElButton type="primary" plain class="!font-bold shadow-sm" @click="loadAnalyticsData">
            <Icon icon="vi-ep:refresh" class="mr-6px" /> {{ t('common.refresh') }}
          </ElButton>
        </ElTooltip>
      </div>
    </div>

    <!-- ==================== VIEW 1: STANDART TAHLIL ==================== -->
    <div v-if="activeViewTab === 'standard'" class="fade-in-content">
      <!-- Executive KPI Summary Cards -->
      <PanelGroup :data="overviewData" :loading="loading" />

      <!-- Main Chart: Financial Dynamics & Net Profit Trend -->
      <ElRow :gutter="20" class="mb-20px">
        <ElCol :span="24">
          <div class="chart-card glass-panel">
            <div class="chart-card-header justify-between">
              <div class="flex items-center gap-10px">
                <div class="chart-card-dot green pulse"></div>
                <ElTooltip
                  :content="t('analysis.tipFinancialDynamics') || t('analysis.financialDynamics')"
                  placement="top"
                >
                  <span class="header-title cursor-help">
                    {{ t('analysis.financialDynamics') }}
                  </span>
                </ElTooltip>
              </div>
              <div class="flex items-center gap-10px">
                <ElRadioGroup v-model="timeRange" size="small" class="custom-radio-group">
                  <ElRadioButton value="6m">{{ t('analysis.last6Months') }}</ElRadioButton>
                  <ElRadioButton value="1y">{{ t('analysis.yearly') }}</ElRadioButton>
                </ElRadioGroup>
              </div>
            </div>
            <div class="chart-body">
              <ElSkeleton :loading="loading" animated :rows="6">
                <Echart :options="financialTrendOptions as any" :height="360" />
              </ElSkeleton>
            </div>
          </div>
        </ElCol>
      </ElRow>

      <!-- Secondary Charts: Expense Structure & Category Profitability -->
      <ElRow :gutter="20" class="mb-20px">
        <!-- Left: Expense Structure Donut Chart -->
        <ElCol :xl="10" :lg="10" :md="24" :sm="24" :xs="24" class="mb-16px">
          <div class="chart-card glass-panel h-full">
            <div class="chart-card-header">
              <div class="chart-card-dot amber"></div>
              <ElTooltip
                :content="t('analysis.tipExpenseStructure') || t('analysis.expenseStructure')"
                placement="top"
              >
                <span class="header-title cursor-help">{{ t('analysis.expenseStructure') }}</span>
              </ElTooltip>
            </div>
            <div class="chart-body">
              <ElSkeleton :loading="loading" animated :rows="5">
                <Echart :options="expenseStructureOptions as any" :height="300" />
              </ElSkeleton>
            </div>
          </div>
        </ElCol>

        <!-- Right: Category Profitability Breakdown -->
        <ElCol :xl="14" :lg="14" :md="24" :sm="24" :xs="24" class="mb-16px">
          <div class="chart-card glass-panel h-full">
            <div class="chart-card-header">
              <div class="chart-card-dot blue"></div>
              <ElTooltip
                :content="
                  t('analysis.tipCategoryProfitability') || t('analysis.categoryProfitability')
                "
                placement="top"
              >
                <span class="header-title cursor-help">
                  {{ t('analysis.categoryProfitability') }}
                </span>
              </ElTooltip>
            </div>
            <div class="chart-body">
              <ElSkeleton :loading="loading" animated :rows="5">
                <Echart :options="categoryProfitOptions as any" :height="300" />
              </ElSkeleton>
            </div>
          </div>
        </ElCol>
      </ElRow>

      <!-- Monthly Financial Overview Data Table -->
      <div class="chart-card glass-panel mb-20px">
        <div class="chart-card-header justify-between">
          <div class="flex items-center gap-10px">
            <div class="chart-card-dot green"></div>
            <ElTooltip
              :content="t('analysis.tipMonthlyFinancialTable') || t('erp.monthlyFinancialTable')"
              placement="top"
            >
              <span class="header-title cursor-help">{{ t('erp.monthlyFinancialTable') }}</span>
            </ElTooltip>
          </div>
        </div>
        <div class="p-16px">
          <ElTable
            v-loading="loading"
            :data="monthlyFinancialTable"
            border
            size="small"
            class="financial-summary-table"
          >
            <ElTableColumn prop="month" :label="t('erp.reportMonth')" width="140" />
            <ElTableColumn prop="revenue" :label="t('erp.grossRevenueDollar')" align="right">
              <template #default="{ row }">
                <span class="font-mono font-bold text-blue-600 dark:text-blue-400">
                  ${{ formatMoney(row.revenue) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="cogs" :label="t('erp.cogsDollar')" align="right">
              <template #default="{ row }">
                <span class="font-mono text-amber-600 dark:text-amber-400">
                  ${{ formatMoney(row.cogs) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn
              prop="staffSalaries"
              :label="t('erp.permanentSalariesDollar')"
              align="right"
            >
              <template #default="{ row }">
                <span class="font-mono text-purple-600 dark:text-purple-400">
                  ${{ formatMoney(row.staffSalaries) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="shortTermOutputs" :label="t('erp.shortTermDollar')" align="right">
              <template #default="{ row }">
                <span class="font-mono text-pink-600 dark:text-pink-400">
                  ${{ formatMoney(row.shortTermOutputs) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="totalExpenses" :label="t('erp.totalExpensesDollar')" align="right">
              <template #default="{ row }">
                <span class="font-mono font-bold text-rose-600 dark:text-rose-400">
                  ${{ formatMoney(row.totalExpenses) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="netProfit" :label="t('erp.netProfitDollar')" align="right">
              <template #default="{ row }">
                <span
                  class="font-mono font-extrabold text-14px text-emerald-600 dark:text-emerald-400"
                >
                  ${{ formatMoney(row.netProfit) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="margin" :label="t('erp.marginPercent')" width="130" align="center">
              <template #default="{ row }">
                <ElTag
                  :type="row.margin >= 20 ? 'success' : row.margin >= 10 ? 'warning' : 'danger'"
                  effect="plain"
                  round
                >
                  {{ row.margin }}%
                </ElTag>
              </template>
            </ElTableColumn>
          </ElTable>
        </div>
      </div>
    </div>

    <!-- ==================== VIEW 2: OYLIK YOPILISH & OYLIK SAVDOLAR RO'YXATI ==================== -->
    <div v-else-if="activeViewTab === 'closing'" class="fade-in-content">
      <!-- Top Station Control Banner -->
      <div
        class="station-hero-card glass-panel mb-24px p-22px rounded-20px relative overflow-hidden"
      >
        <div class="hero-glow-blob"></div>

        <div class="relative z-1 flex flex-wrap items-center justify-between gap-18px">
          <div>
            <div class="flex items-center gap-10px">
              <span class="station-icon-badge">
                <Icon icon="ep:folder-opened" class="text-22px text-blue-600 dark:text-blue-400" />
              </span>
              <div>
                <h2 class="text-20px font-black text-[var(--el-text-color-primary)] tracking-tight">
                  {{ t('erp.monthlyCloseReportTitle') }}
                </h2>
                <p class="text-13px text-gray-500 dark:text-gray-400 mt-2px">
                  {{ t('erp.monthlyCloseReportSubtitle') }}
                </p>
              </div>
            </div>

            <!-- Quick Month Jump Tabs -->
            <div class="quick-month-pills flex items-center gap-8px mt-16px flex-wrap">
              <span class="text-11px font-bold text-gray-400 uppercase mr-4px">{{
                t('erp.quickSelect')
              }}</span>
              <ElTooltip
                v-for="q in quickJumpMonths"
                :key="q.value"
                :content="q.tip"
                placement="top"
              >
                <button
                  class="quick-pill-btn"
                  :class="{ active: closeMonthInput === q.value }"
                  @click="closeMonthInput = q.value"
                >
                  {{ q.label }}
                </button>
              </ElTooltip>
            </div>
          </div>

          <!-- Controls and Action Button -->
          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-12px">
            <ElTooltip :content="t('analysis.tipSelectMonth')" placement="top">
              <div
                class="flex items-center gap-8px bg-slate-100 dark:bg-slate-800/80 p-6px rounded-12px border border-slate-200 dark:border-slate-700"
              >
                <span class="text-12px font-bold px-6px text-gray-500">{{
                  t('erp.periodLabel')
                }}</span>
                <ElDatePicker
                  v-model="closeMonthInput"
                  type="month"
                  value-format="YYYY-MM"
                  format="YYYY-MM (MMMM)"
                  :clearable="false"
                  style="width: 170px"
                />
              </div>
            </ElTooltip>

            <ElTooltip
              :content="
                isSelectedMonthAlreadyClosed
                  ? t('erp.monthAlreadyClosedHint')
                  : t('erp.sealMonthRecordHint')
              "
              placement="top"
            >
              <button
                class="grand-archive-btn"
                :class="{ 'grand-archive-btn--update': isSelectedMonthAlreadyClosed }"
                :disabled="closingSubmitting"
                @click="handleCloseMonth"
              >
                <Icon
                  :icon="isSelectedMonthAlreadyClosed ? 'ep:refresh' : 'ep:folder-checked'"
                  class="text-18px"
                />
                <span>{{
                  isSelectedMonthAlreadyClosed ? t('erp.recalcAndUpdate') : t('erp.sealAndArchive')
                }}</span>
              </button>
            </ElTooltip>
          </div>
        </div>

        <!-- Month Status Alert Chip -->
        <div
          class="mt-18px pt-14px border-t border-slate-200/60 dark:border-slate-800 flex items-center justify-between flex-wrap gap-10px"
        >
          <div class="flex items-center gap-10px">
            <span
              class="status-indicator-dot"
              :class="isSelectedMonthAlreadyClosed ? 'is-closed' : 'is-open'"
            ></span>
            <span
              class="text-13px font-bold flex items-center gap-4px"
              :class="
                isSelectedMonthAlreadyClosed
                  ? 'text-emerald-600 dark:text-emerald-400'
                  : 'text-amber-600 dark:text-amber-400'
              "
            >
              <Icon
                :icon="isSelectedMonthAlreadyClosed ? 'ep:check' : 'ep:timer'"
                class="text-14px"
              />
              {{
                isSelectedMonthAlreadyClosed
                  ? `${closeMonthInput} ${t('erp.monthSealedNotice')}`
                  : `${closeMonthInput} ${t('erp.monthOpenNotice')}`
              }}
            </span>
          </div>

          <div v-if="existingSnapshotForSelectedMonth" class="text-12px text-gray-500">
            {{ t('analysis.sealedDateLabel') }}
            <b>{{ existingSnapshotForSelectedMonth.created_at }}</b> ({{
              t('analysis.responsibleLabel')
            }}
            {{ existingSnapshotForSelectedMonth.closed_by || 'admin' }})
          </div>
        </div>
      </div>

      <!-- 4 Grand Animated Interactive KPI Cards -->
      <ElSkeleton :loading="closingLoading" animated>
        <template #template>
          <ElRow :gutter="16" class="mb-24px">
            <ElCol
              v-for="i in 4"
              :key="i"
              :xl="6"
              :lg="6"
              :md="12"
              :sm="12"
              :xs="24"
              class="mb-14px"
            >
              <div
                class="grand-stat-card glass-panel p-20px h-[134px] flex flex-col justify-between"
              >
                <ElSkeletonItem variant="text" style="width: 45%; height: 16px" />
                <ElSkeletonItem variant="h1" style="width: 65%; height: 32px" />
                <div class="flex justify-between items-center">
                  <ElSkeletonItem variant="text" style="width: 35%; height: 14px" />
                  <ElSkeletonItem variant="text" style="width: 40%; height: 14px" />
                </div>
              </div>
            </ElCol>
          </ElRow>
        </template>
        <template #default>
          <ElRow :gutter="16" class="mb-24px">
            <!-- 1. Gross Revenue KPI Card -->
            <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
              <ElTooltip :content="t('analysis.tipGrossRevenueCard')" placement="top">
                <div class="grand-stat-card glass-panel stat-card--blue cursor-help">
                  <div class="flex justify-between items-start">
                    <div>
                      <span class="stat-subtitle">{{ t('analysis.grossRevenueSavdoUpper') }}</span>
                      <div class="stat-value text-blue-600 dark:text-blue-400">
                        $<CountTo
                          :start-val="0"
                          :end-val="closeMonthPreview.revenue"
                          :duration="1200"
                        />
                      </div>
                    </div>
                    <div class="stat-icon-wrap bg-blue-500/10 text-blue-600 dark:text-blue-400">
                      <Icon icon="ep:money" class="text-22px" />
                    </div>
                  </div>
                  <div class="stat-footer-strip">
                    <span
                      class="stat-subtag bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300"
                    >
                      {{ closeMonthPreview.salesCount }} {{ t('erp.dealsCountSuffix') }}
                    </span>
                    <span v-if="closeMonthPreview.totalDebt > 0" class="text-11px font-bold text-amber-700 dark:text-amber-300">
                      Naqd: ${{ Math.round(closeMonthPreview.totalPaid).toLocaleString() }} | Nasiya: ${{ Math.round(closeMonthPreview.totalDebt).toLocaleString() }}
                    </span>
                    <span v-else class="text-11px text-muted">{{ t('erp.collectedDuringMonth') }}</span>
                  </div>
                </div>
              </ElTooltip>
            </ElCol>

            <!-- 2. COGS Product Cost KPI Card -->
            <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
              <ElTooltip :content="t('analysis.tipCogsCard')" placement="top">
                <div class="grand-stat-card glass-panel stat-card--amber cursor-help">
                  <div class="flex justify-between items-start">
                    <div>
                      <span class="stat-subtitle">{{ t('analysis.cogsUpper') }}</span>
                      <div class="stat-value text-amber-600 dark:text-amber-400">
                        $<CountTo
                          :start-val="0"
                          :end-val="closeMonthPreview.cogs"
                          :duration="1200"
                        />
                      </div>
                    </div>
                    <div class="stat-icon-wrap bg-amber-500/10 text-amber-600 dark:text-amber-400">
                      <Icon icon="ep:box" class="text-22px" />
                    </div>
                  </div>
                  <div class="stat-footer-strip">
                    <span
                      class="stat-subtag bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300"
                    >
                      {{
                        t('analysis.revenueShare', {
                          percent:
                            closeMonthPreview.revenue > 0
                              ? Math.round(
                                  (closeMonthPreview.cogs / closeMonthPreview.revenue) * 100
                                )
                              : 62
                        })
                      }}
                    </span>
                    <span class="text-11px text-muted">{{ t('erp.materialAndGoodsValue') }}</span>
                  </div>
                </div>
              </ElTooltip>
            </ElCol>

            <!-- 3. Staff Salaries & Advances KPI Card -->
            <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
              <ElTooltip :content="t('analysis.tipPayrollCard')" placement="top">
                <div class="grand-stat-card glass-panel stat-card--purple cursor-help">
                  <div class="flex justify-between items-start">
                    <div>
                      <span class="stat-subtitle">{{ t('analysis.payrollAdvancesUpper') }}</span>
                      <div class="stat-value text-purple-600 dark:text-purple-400">
                        $<CountTo
                          :start-val="0"
                          :end-val="closeMonthPreview.staffSalaries + closeMonthPreview.shortTerm"
                          :duration="1200"
                        />
                      </div>
                    </div>
                    <div
                      class="stat-icon-wrap bg-purple-500/10 text-purple-600 dark:text-purple-400"
                    >
                      <Icon icon="ep:user-filled" class="text-22px" />
                    </div>
                  </div>
                  <div class="stat-footer-strip">
                    <span
                      class="stat-subtag bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300"
                    >
                      {{ t('analysis.permanentSalariesLabel') }} ${{
                        formatMoney(closeMonthPreview.staffSalaries)
                      }}
                    </span>
                    <span class="text-11px text-muted"
                      >{{ t('analysis.pieceworkLabel') }} ${{
                        formatMoney(closeMonthPreview.shortTerm)
                      }}</span
                    >
                  </div>
                </div>
              </ElTooltip>
            </ElCol>

            <!-- 4. Grand Net Profit KPI Card -->
            <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
              <ElTooltip :content="t('analysis.tipNetProfitCard')" placement="top">
                <div class="grand-stat-card glass-panel stat-card--emerald cursor-help">
                  <div class="flex justify-between items-start">
                    <div>
                      <span
                        class="stat-subtitle text-emerald-800 dark:text-emerald-300 font-extrabold"
                        >{{ t('analysis.realNetProfitUpper') }}</span
                      >
                      <div class="stat-value text-emerald-600 dark:text-emerald-400">
                        $<CountTo
                          :start-val="0"
                          :end-val="closeMonthPreview.netProfit"
                          :duration="1200"
                        />
                      </div>
                    </div>
                    <div
                      class="stat-icon-wrap bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 pulse-glow"
                    >
                      <Icon icon="ep:trophy" class="text-22px" />
                    </div>
                  </div>
                  <div class="stat-footer-strip">
                    <span class="stat-subtag bg-emerald-600 text-white font-bold">
                      {{ t('erp.profitability') }}: {{ closeMonthPreview.margin }}%
                    </span>
                    <span v-if="closeMonthPreview.totalDebt > 0" class="text-11px text-amber-700 dark:text-amber-300 font-bold">
                      Kassada: ${{ Math.max(0, Math.round(closeMonthPreview.totalPaid - closeMonthPreview.totalExpenses)).toLocaleString() }}
                    </span>
                    <span v-else class="text-11px text-emerald-700 dark:text-emerald-300 font-bold">{{
                      t('erp.allExpensesDeducted')
                    }}</span>
                  </div>
                </div>
              </ElTooltip>
            </ElCol>
          </ElRow>
        </template>
      </ElSkeleton>

      <!-- Interactive Luxury Charts: Dual-Ring Profit Donut & 6-Month Rolling Evolution Timeline -->
      <ElRow :gutter="20" class="mb-24px">
        <!-- Left: Interactive Donut & Financial Breakdown Matrix -->
        <ElCol :xl="10" :lg="10" :md="24" :sm="24" :xs="24" class="mb-16px">
          <div class="chart-card glass-panel h-full flex flex-col justify-between">
            <div class="chart-card-header justify-between">
              <div class="flex items-center gap-10px">
                <div class="chart-card-dot amber"></div>
                <ElTooltip :content="t('analysis.tipDistributionRing')" placement="top">
                  <span class="header-title cursor-help"
                    >{{ closeMonthInput }} {{ t('erp.financialDistributionRing') }}</span
                  >
                </ElTooltip>
              </div>
            </div>
            <div class="chart-body relative p-10px flex-1 flex flex-col justify-center">
              <ElSkeleton :loading="closingLoading" animated :rows="6">
                <template #default>
                  <div class="relative">
                    <Echart :options="monthDistributionDonutOptions as any" :height="260" />
                    <!-- Hollow Center Hero Stat -->
                    <div class="donut-center-hero pointer-events-none">
                      <div class="center-title">{{ t('analysis.netProfitUpper') }}</div>
                      <div
                        class="center-amount font-mono text-emerald-600 dark:text-emerald-400 font-black text-18px"
                      >
                        ${{ formatMoney(closeMonthPreview.netProfit) }}
                      </div>
                      <div class="center-badge text-10px font-bold text-gray-500">
                        {{ closeMonthPreview.margin }}% {{ t('analysis.marginText') }}
                      </div>
                    </div>
                  </div>

                  <!-- Interactive Donut Micro-Legend Matrix -->
                  <div
                    class="donut-legend-matrix grid grid-cols-2 gap-8px mt-10px pt-10px border-t border-slate-200/70 dark:border-slate-800"
                  >
                    <div class="legend-pill-item">
                      <span class="dot bg-amber-500"></span>
                      <span class="text-11px text-gray-600 dark:text-gray-400 truncate"
                        >{{ t('erp.costCogs') }}:</span
                      >
                      <span class="font-mono text-12px font-bold ml-auto"
                        >${{ formatMoney(closeMonthPreview.cogs) }}</span
                      >
                    </div>
                    <div class="legend-pill-item">
                      <span class="dot bg-purple-500"></span>
                      <span class="text-11px text-gray-600 dark:text-gray-400 truncate"
                        >{{ t('erp.salaries') }}:</span
                      >
                      <span class="font-mono text-12px font-bold ml-auto"
                        >${{ formatMoney(closeMonthPreview.staffSalaries) }}</span
                      >
                    </div>
                    <div class="legend-pill-item">
                      <span class="dot bg-pink-500"></span>
                      <span class="text-11px text-gray-600 dark:text-gray-400 truncate"
                        >{{ t('erp.pieceworkSalary') }}:</span
                      >
                      <span class="font-mono text-12px font-bold ml-auto"
                        >${{ formatMoney(closeMonthPreview.shortTerm) }}</span
                      >
                    </div>
                    <div class="legend-pill-item bg-emerald-500/10 rounded-6px px-4px">
                      <span class="dot bg-emerald-500"></span>
                      <span
                        class="text-11px text-emerald-700 dark:text-emerald-300 font-bold truncate"
                        >{{ t('erp.realNetProfit') }}:</span
                      >
                      <span class="font-mono text-12px font-extrabold text-emerald-600 ml-auto"
                        >+${{ formatMoney(closeMonthPreview.netProfit) }}</span
                      >
                    </div>
                  </div>
                </template>
              </ElSkeleton>
            </div>
          </div>
        </ElCol>

        <!-- Right: 6-Month Rolling Financial Evolution Timeline -->
        <ElCol :xl="14" :lg="14" :md="24" :sm="24" :xs="24" class="mb-16px">
          <div class="chart-card glass-panel h-full">
            <div class="chart-card-header justify-between">
              <div class="flex items-center gap-10px">
                <div class="chart-card-dot green pulse"></div>
                <ElTooltip :content="t('analysis.tipEvolutionTimeline')" placement="top">
                  <span class="header-title cursor-help"
                    >6 {{ t('erp.monthlyEvolutionSpline') }} (Evolution Spline)</span
                  >
                </ElTooltip>
              </div>
              <span class="text-11px text-gray-400 font-bold">{{
                t('analysis.splineSubtitle')
              }}</span>
            </div>
            <div class="chart-body">
              <ElSkeleton :loading="closingLoading" animated :rows="6">
                <template #default>
                  <Echart :options="archiveHistoryTimelineOptions as any" :height="340" />
                </template>
              </ElSkeleton>
            </div>
          </div>
        </ElCol>
      </ElRow>

      <!-- ═══════════════════════════════════════════════════════════════════ -->
      <!-- BOTTOM SECTION: MONTHLY SALES LIST & TRANSACTIONS (USER REQUESTED) -->
      <!-- ═══════════════════════════════════════════════════════════════════ -->
      <div class="chart-card glass-panel mb-24px">
        <!-- Section Header with Mode Switch Tabs -->
        <div class="chart-card-header justify-between flex-wrap gap-12px">
          <div class="flex items-center gap-12px">
            <div
              class="mode-pills flex items-center p-3px rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
            >
              <ElTooltip :content="t('analysis.tipSalesList')" placement="top">
                <button
                  class="mode-btn text-12px px-12px py-6px"
                  :class="{ active: bottomTableMode === 'sales' }"
                  @click="bottomTableMode = 'sales'"
                >
                  <Icon icon="ep:shopping-cart" class="mr-4px" />
                  {{
                    t('analysis.monthlySalesTab', {
                      month: closeMonthInput,
                      count: filteredMonthlySales.length
                    })
                  }}
                </button>
              </ElTooltip>

              <ElTooltip :content="t('analysis.tipArchiveList')" placement="top">
                <button
                  class="mode-btn text-12px px-12px py-6px"
                  :class="{ active: bottomTableMode === 'archive' }"
                  @click="bottomTableMode = 'archive'"
                >
                  <Icon icon="ep:folder-checked" class="mr-4px" />
                  {{ t('analysis.archivedMonthsTab', { count: savedSnapshots.length }) }}
                </button>
              </ElTooltip>
            </div>
          </div>

          <!-- Total Metrics Ribbon (When in Sales mode) -->
          <div
            v-if="bottomTableMode === 'sales'"
            class="flex items-center gap-12px flex-wrap text-12px"
          >
            <ElTooltip :content="t('analysis.tipTotalSalesSummary')" placement="top">
              <div class="flex items-center gap-4px font-bold cursor-help">
                <span class="text-gray-500">{{ t('analysis.totalSalesLabel') }}</span>
                <span class="font-mono text-blue-600 font-extrabold text-13px"
                  >${{ formatMoney(totalMonthlySalesRevenue) }}</span
                >
              </div>
            </ElTooltip>

            <ElTooltip :content="t('analysis.tipPaidSummary')" placement="top">
              <div class="flex items-center gap-4px font-bold cursor-help">
                <span class="text-gray-500">{{ t('analysis.paidLabel') }}</span>
                <span class="font-mono text-emerald-600 font-extrabold"
                  >${{ formatMoney(totalMonthlySalesPaid) }}</span
                >
              </div>
            </ElTooltip>

            <ElTooltip
              v-if="totalMonthlySalesDebt > 0"
              :content="t('analysis.tipDebtSummary')"
              placement="top"
            >
              <div class="flex items-center gap-4px font-bold cursor-help">
                <span class="text-gray-500">{{ t('analysis.debtLabel') }}</span>
                <span class="font-mono text-rose-600 font-extrabold"
                  >${{ formatMoney(totalMonthlySalesDebt) }}</span
                >
              </div>
            </ElTooltip>

            <ElTooltip :content="t('analysis.tipRefresh')" placement="top">
              <ElButton size="small" @click="loadAnalyticsData">
                <Icon icon="vi-ep:refresh" class="mr-4px" /> {{ t('common.refresh') }}
              </ElButton>
            </ElTooltip>
          </div>

          <div v-else class="flex items-center gap-10px">
            <ElTooltip :content="t('analysis.tipRefresh')" placement="top">
              <ElButton size="small" @click="fetchSavedSnapshots">
                <Icon icon="vi-ep:refresh" class="mr-4px" /> {{ t('common.refresh') }}
              </ElButton>
            </ElTooltip>
          </div>
        </div>

        <!-- 1. MONTHLY SALES & RECEIPTS TABLE (ACTIVE BY DEFAULT) -->
        <div v-if="bottomTableMode === 'sales'" class="p-16px">
          <!-- Search & Filter Controls -->
          <div class="flex items-center justify-between gap-12px mb-14px flex-wrap">
            <div class="flex items-center gap-10px flex-wrap flex-1">
              <ElTooltip :content="t('analysis.tipSearchSales')" placement="top">
                <ElInput
                  v-model="monthlySalesFilterSearch"
                  :placeholder="t('analysis.searchPlaceholder')"
                  clearable
                  size="small"
                  style="max-width: 320px"
                >
                  <template #prefix>
                    <Icon icon="ep:search" class="text-gray-400" />
                  </template>
                </ElInput>
              </ElTooltip>

              <ElTooltip :content="t('analysis.tipFilterPayment')" placement="top">
                <ElSelect
                  v-model="monthlySalesFilterPayment"
                  size="small"
                  style="width: 170px"
                  :placeholder="t('analysis.paymentMethodPlaceholder')"
                >
                  <ElOption :label="t('analysis.allPaymentMethods')" value="all" />
                  <ElOption :label="t('analysis.cashPayment')" value="naqd" />
                  <ElOption :label="t('analysis.cardPayment')" value="karta" />
                  <ElOption :label="t('erp.bankTransfer')" value="otkazma" />
                  <ElOption :label="t('erp.debt')" value="nasiya" />
                </ElSelect>
              </ElTooltip>
            </div>
          </div>

          <!-- Empty State -->
          <div
            v-if="!salesLoading && filteredMonthlySales.length === 0"
            class="py-40px text-center text-gray-400"
          >
            <Icon
              icon="ep:shopping-bag"
              class="text-44px text-gray-300 dark:text-gray-600 mb-10px inline-block"
            />
            <div class="text-15px font-bold text-gray-600 dark:text-gray-300">{{
              t('analysis.noSalesFound')
            }}</div>
            <div class="text-12px mt-4px text-gray-400">{{ t('analysis.noSalesFoundSub') }}</div>
          </div>

          <!-- Sales Table -->
          <ElTable
            v-else
            v-loading="salesLoading"
            :data="filteredMonthlySales"
            border
            size="small"
            class="financial-summary-table luxury-archive-table"
          >
            <ElTableColumn prop="receipt_number" :label="t('erp.receiptNumber')" min-width="190">
              <template #default="{ row }">
                <ElTooltip :content="t('analysis.tipReceiptCode')" placement="top">
                  <div class="flex items-center gap-6px cursor-help">
                    <Icon icon="ep:document" class="text-blue-500 flex-shrink-0" />
                    <span class="font-mono font-bold text-12px text-blue-600 dark:text-blue-400">
                      {{ row.receipt_number || row.id }}
                    </span>
                  </div>
                </ElTooltip>
              </template>
            </ElTableColumn>

            <ElTableColumn
              prop="customer_name"
              :label="t('analysis.customerLabel')"
              min-width="160"
            >
              <template #default="{ row }">
                <div class="flex flex-col">
                  <span class="font-semibold text-13px text-[var(--el-text-color-primary)]">
                    {{ row.customer_name || t('analysis.walkInCustomer') }}
                  </span>
                  <span v-if="row.customer_phone" class="text-11px text-gray-400 font-mono">{{
                    row.customer_phone
                  }}</span>
                </div>
              </template>
            </ElTableColumn>

            <ElTableColumn
              prop="payment_method"
              :label="t('analysis.paymentMethodLabel')"
              width="130"
              align="center"
            >
              <template #default="{ row }">
                <ElTag
                  v-if="row.payment_method === 'naqd'"
                  type="success"
                  effect="light"
                  round
                  size="small"
                >
                  {{ t('analysis.cashPayment') }}
                </ElTag>
                <ElTag
                  v-else-if="row.payment_method === 'karta'"
                  type="primary"
                  effect="light"
                  round
                  size="small"
                >
                  {{ t('analysis.cardPayment') }}
                </ElTag>
                <ElTag
                  v-else-if="row.payment_method === 'nasiya'"
                  type="danger"
                  effect="dark"
                  round
                  size="small"
                >
                  {{ t('erp.debt') }}
                </ElTag>
                <ElTag
                  v-else-if="row.payment_method === 'otkazma'"
                  type="warning"
                  effect="light"
                  round
                  size="small"
                >
                  {{ t('erp.bankTransfer') }}
                </ElTag>
                <ElTag v-else size="small" round>
                  {{ row.payment_method || t('analysis.cashPayment') }}
                </ElTag>
              </template>
            </ElTableColumn>

            <ElTableColumn
              prop="total_items"
              :label="t('analysis.productsCountLabel')"
              width="110"
              align="center"
            >
              <template #default="{ row }">
                <span class="text-12px font-bold text-gray-600 dark:text-gray-300">
                  {{ (row.items && row.items.length) || row.total_items || 1 }}
                  {{ t('erp.typesCount') }}
                </span>
              </template>
            </ElTableColumn>

            <ElTableColumn
              prop="total_amount"
              :label="t('erp.totalAmountDollar')"
              min-width="140"
              align="right"
            >
              <template #default="{ row }">
                <span class="font-mono font-bold text-13px text-blue-600 dark:text-blue-400">
                  ${{ formatMoney(row.total_amount || row.total) }}
                </span>
              </template>
            </ElTableColumn>

            <ElTableColumn
              prop="paid_amount"
              :label="t('analysis.paidAmountDollarLabel')"
              min-width="130"
              align="right"
            >
              <template #default="{ row }">
                <span class="font-mono font-semibold text-emerald-600 dark:text-emerald-400">
                  ${{
                    formatMoney(
                      row.paid_amount !== undefined && row.paid_amount !== null
                        ? row.paid_amount
                        : row.payment_method === 'nasiya'
                          ? 0
                          : row.total_amount || row.total
                    )
                  }}
                </span>
              </template>
            </ElTableColumn>

            <ElTableColumn
              prop="debt_amount"
              :label="t('analysis.debtAmountDollarLabel')"
              min-width="110"
              align="right"
            >
              <template #default="{ row }">
                <span
                  class="font-mono font-bold"
                  :class="Number(row.debt_amount || 0) > 0 ? 'text-rose-600' : 'text-gray-400'"
                >
                  ${{ formatMoney(row.debt_amount || 0) }}
                </span>
              </template>
            </ElTableColumn>

            <ElTableColumn prop="cashier_name" :label="t('erp.cashier')" width="110" align="center">
              <template #default="{ row }">
                <ElTag size="small" type="info" effect="plain" round>
                  {{ row.cashier_name || 'admin' }}
                </ElTag>
              </template>
            </ElTableColumn>

            <ElTableColumn prop="created_at" :label="t('analysis.timeLabel')" width="160">
              <template #default="{ row }">
                <span class="text-11px text-gray-500 font-mono">{{ row.created_at || '—' }}</span>
              </template>
            </ElTableColumn>

            <ElTableColumn :label="t('erp.amallar')" width="130" align="center" fixed="right">
              <template #default="{ row }">
                <ElTooltip :content="t('analysis.tipViewReceiptDetail')" placement="top">
                  <ElButton link type="primary" size="small" @click="openSaleDetail(row)">
                    <Icon icon="ep:view" class="mr-2px" /> {{ t('analysis.viewReceipt') }}
                  </ElButton>
                </ElTooltip>
              </template>
            </ElTableColumn>
          </ElTable>
        </div>

        <!-- 2. ARCHIVED MONTHLY SNAPSHOTS TABLE (SUB-VIEW) -->
        <div v-else class="p-16px">
          <div v-if="savedSnapshots.length === 0" class="py-40px text-center text-gray-400">
            <Icon
              icon="ep:folder-delete"
              class="text-44px text-gray-300 dark:text-gray-600 mb-10px inline-block"
            />
            <div class="text-15px font-bold text-gray-600 dark:text-gray-300">{{
              t('analysis.noArchivedMonths')
            }}</div>
            <div class="text-12px mt-4px text-gray-400">{{
              t('analysis.noArchivedMonthsSub')
            }}</div>
          </div>

          <ElTable
            v-else
            v-loading="snapshotsLoading"
            :data="savedSnapshots"
            border
            class="financial-summary-table luxury-archive-table"
          >
            <ElTableColumn
              prop="period_month"
              :label="t('erp.reportMonth')"
              width="160"
              align="center"
            >
              <template #default="{ row }">
                <div class="flex items-center justify-center gap-6px">
                  <Icon icon="ep:calendar" class="text-14px text-blue-500" />
                  <span class="font-bold text-14px text-blue-600 dark:text-blue-400 font-mono">
                    {{ row.period_month }}
                  </span>
                </div>
              </template>
            </ElTableColumn>
            <ElTableColumn
              prop="sales_count"
              :label="t('analysis.dealsLabel')"
              width="110"
              align="center"
            >
              <template #default="{ row }">
                <ElTag size="small" type="info" effect="plain" round>
                  {{ row.sales_count }} {{ t('erp.dealsCountSuffix') }}
                </ElTag>
              </template>
            </ElTableColumn>
            <ElTableColumn
              prop="revenue"
              :label="t('erp.grossRevenueDollar')"
              min-width="150"
              align="right"
            >
              <template #default="{ row }">
                <span class="font-mono font-bold text-blue-600 dark:text-blue-400 text-14px">
                  ${{ formatMoney(row.revenue) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="cogs" :label="t('erp.cogsDollar')" min-width="140" align="right">
              <template #default="{ row }">
                <span class="font-mono text-amber-600 dark:text-amber-400">
                  ${{ formatMoney(row.cogs) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn
              prop="staff_salaries"
              :label="`${t('erp.salaries')} + Аванслар ($)`"
              min-width="170"
              align="right"
            >
              <template #default="{ row }">
                <span class="font-mono text-purple-600 dark:text-purple-400">
                  ${{ formatMoney(row.staff_salaries) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn
              prop="short_term_outputs"
              :label="t('erp.shortTermDollar')"
              min-width="140"
              align="right"
            >
              <template #default="{ row }">
                <span class="font-mono text-pink-600 dark:text-pink-400">
                  ${{ formatMoney(row.short_term_outputs) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn
              prop="total_expenses"
              :label="t('erp.totalExpensesDollar')"
              min-width="150"
              align="right"
            >
              <template #default="{ row }">
                <span class="font-mono font-bold text-rose-600 dark:text-rose-400">
                  ${{ formatMoney(row.total_expenses) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn
              prop="netProfit"
              :label="t('erp.netProfitDollar')"
              min-width="170"
              align="right"
            >
              <template #default="{ row }">
                <span class="font-mono font-black text-15px text-emerald-600 dark:text-emerald-400">
                  +${{ formatMoney(row.net_profit) }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn
              prop="profit_margin"
              :label="t('analysis.profitabilityLabel')"
              width="140"
              align="center"
            >
              <template #default="{ row }">
                <div class="flex items-center gap-6px justify-center">
                  <ElProgress
                    :percentage="Math.min(100, Math.max(0, row.profit_margin))"
                    :stroke-width="6"
                    :show-text="false"
                    class="w-60px"
                    color="#10b981"
                  />
                  <span class="text-11px font-bold text-emerald-600">{{ row.profit_margin }}%</span>
                </div>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="status" :label="t('erp.holati')" width="120" align="center">
              <template #default>
                <ElTag type="success" effect="dark" round size="small">
                  <Icon icon="ep:check" class="mr-2px" /> {{ t('analysis.sealedStatus') }}
                </ElTag>
              </template>
            </ElTableColumn>
            <ElTableColumn :label="t('analysis.sealedDateCol')" width="160">
              <template #default="{ row }">
                <span class="text-11px text-gray-500 font-mono">{{ row.created_at || '—' }}</span>
              </template>
            </ElTableColumn>
            <ElTableColumn :label="t('erp.amallar')" width="140" align="center" fixed="right">
              <template #default="{ row }">
                <ElTooltip :content="t('analysis.tipViewArchiveCert')" placement="top">
                  <ElButton link type="primary" size="small" @click="handleViewSnapshotDetail(row)">
                    <Icon icon="ep:view" class="mr-2px" /> {{ t('analysis.viewText') }}
                  </ElButton>
                </ElTooltip>
                <ElTooltip :content="t('analysis.tipDeleteArchiveReport')" placement="top">
                  <ElButton link type="danger" size="small" @click="handleDeleteSnapshot(row)">
                    <Icon icon="ep:delete" class="mr-2px" />{{ t('common.delete') }}</ElButton
                  >
                </ElTooltip>
              </template>
            </ElTableColumn>
          </ElTable>
        </div>
      </div>

      <!-- Receipt Items Details Modal -->
      <ElDialog
        v-model="saleDetailDialogVisible"
        :title="
          t('analysis.receiptTitle', {
            number: selectedSaleDetail?.receipt_number || selectedSaleDetail?.id || ''
          })
        "
        width="640px"
      >
        <div v-if="selectedSaleDetail" class="flex flex-col gap-14px">
          <div
            class="flex justify-between items-center p-12px bg-slate-50 dark:bg-slate-800 rounded-10px"
          >
            <div>
              <span class="text-11px text-gray-400 font-bold uppercase">{{
                t('analysis.buyerLabel')
              }}</span>
              <div class="font-bold text-14px">{{
                selectedSaleDetail.customer_name || 'Умумий харидор (Walk-in)'
              }}</div>
            </div>
            <div class="text-right">
              <span class="text-11px text-gray-400 font-bold uppercase">{{
                t('analysis.dateAndCashier')
              }}</span>
              <div class="text-12px font-mono text-gray-500"
                >{{ selectedSaleDetail.created_at }} ({{
                  selectedSaleDetail.cashier_name || 'admin'
                }})</div
              >
            </div>
          </div>

          <ElTable :data="selectedSaleDetail.items || []" border size="small">
            <ElTableColumn prop="product_name" :label="t('erp.productName')" min-width="180" />
            <ElTableColumn prop="quantity" :label="t('erp.miqdori')" width="90" align="center" />
            <ElTableColumn
              prop="price"
              :label="t('analysis.priceDollar')"
              width="110"
              align="right"
            >
              <template #default="{ row }">
                <span class="font-mono">${{ formatMoney(row.price) }}</span>
              </template>
            </ElTableColumn>
            <ElTableColumn
              prop="total"
              :label="t('analysis.totalDollar')"
              width="120"
              align="right"
            >
              <template #default="{ row }">
                <span class="font-mono font-bold text-blue-600"
                  >${{ formatMoney(row.total || row.price * row.quantity) }}</span
                >
              </template>
            </ElTableColumn>
          </ElTable>

          <div
            class="flex justify-between items-center p-12px bg-blue-50/50 dark:bg-blue-950/20 rounded-10px border border-blue-200/50"
          >
            <span class="font-bold text-14px text-blue-800 dark:text-blue-300">{{
              t('analysis.totalReceiptSum')
            }}</span>
            <span class="font-mono font-black text-18px text-blue-600 dark:text-blue-400">
              ${{
                formatMoney(selectedSaleDetail.total_amount || (selectedSaleDetail as any).total)
              }}
            </span>
          </div>
        </div>
      </ElDialog>

      <!-- Snapshot Details Modal (Executive Financial Certificate Sheet) -->
      <ElDialog
        v-model="detailDialogVisible"
        :title="
          t('analysis.officialArchiveReportTitle', { month: selectedSnapshotDetail?.period_month })
        "
        width="680px"
        custom-class="executive-report-dialog"
      >
        <div v-if="selectedSnapshotDetail" class="snapshot-detail-content flex flex-col gap-16px">
          <!-- Top Certificate Header -->
          <div
            class="flex items-center justify-between p-16px rounded-14px bg-gradient-to-r from-blue-600/10 via-emerald-600/10 to-transparent border border-blue-500/20"
          >
            <div>
              <span class="text-11px uppercase tracking-wider text-gray-500 font-bold">{{
                t('analysis.reportPeriod')
              }}</span>
              <div class="text-22px font-black font-mono text-blue-600"
                >{{ selectedSnapshotDetail.period_month }} {{ t('analysis.monthlyClosing') }}</div
              >
              <div class="text-12px text-gray-400 mt-2px"
                >{{ t('analysis.dealsCountLabel') }} {{ selectedSnapshotDetail.sales_count }}
                {{ t('erp.dealsCountSuffix') }}</div
              >
            </div>
            <div class="text-right">
              <ElTag type="success" effect="dark" round size="large" class="!font-bold">
                <Icon icon="ep:document-checked" class="mr-4px" />
                {{ t('analysis.officiallySealedBadge') }}
              </ElTag>
              <div class="text-11px text-gray-400 mt-4px"
                >{{ t('analysis.sealedTimeLabel') }} {{ selectedSnapshotDetail.created_at }}</div
              >
            </div>
          </div>

          <!-- Structured P&L Financial Sheet -->
          <div
            class="divide-y border rounded-12px overflow-hidden bg-white dark:bg-slate-900 shadow-sm"
          >
            <div
              class="p-12px flex justify-between items-center hover:bg-slate-50 dark:hover:bg-slate-800/50"
            >
              <span class="font-semibold text-gray-700 dark:text-gray-200">{{
                t('analysis.line1Revenue')
              }}</span>
              <span class="font-mono font-bold text-16px text-blue-600 dark:text-blue-400"
                >${{ formatMoney(selectedSnapshotDetail.revenue) }}</span
              >
            </div>
            <div
              class="p-12px flex justify-between items-center hover:bg-slate-50 dark:hover:bg-slate-800/50"
            >
              <span class="font-medium text-gray-600 dark:text-gray-300">{{
                t('analysis.line2Cogs')
              }}</span>
              <span class="font-mono text-amber-600 font-semibold"
                >-${{ formatMoney(selectedSnapshotDetail.cogs) }}</span
              >
            </div>
            <div
              class="p-12px flex justify-between items-center hover:bg-slate-50 dark:hover:bg-slate-800/50"
            >
              <span class="font-medium text-gray-600 dark:text-gray-300">{{
                t('analysis.line3Staff')
              }}</span>
              <span class="font-mono text-purple-600 font-semibold"
                >-${{ formatMoney(selectedSnapshotDetail.staff_salaries) }}</span
              >
            </div>
            <div
              class="p-12px flex justify-between items-center hover:bg-slate-50 dark:hover:bg-slate-800/50"
            >
              <span class="font-medium text-gray-600 dark:text-gray-300">{{
                t('analysis.line4ShortTerm')
              }}</span>
              <span class="font-mono text-pink-600 font-semibold"
                >-${{ formatMoney(selectedSnapshotDetail.short_term_outputs) }}</span
              >
            </div>
            <div
              class="p-12px flex justify-between items-center bg-rose-50/50 dark:bg-rose-950/20 font-bold"
            >
              <span class="text-rose-600">{{ t('analysis.totalExpensesUpper') }}</span>
              <span class="font-mono text-rose-600 text-15px"
                >-${{ formatMoney(selectedSnapshotDetail.total_expenses) }}</span
              >
            </div>
            <div
              class="p-14px flex justify-between items-center bg-emerald-50 dark:bg-emerald-950/40 font-black text-18px text-emerald-600"
            >
              <span>{{ t('analysis.realNetProfitUpper') }}:</span>
              <span class="font-mono"
                >+${{ formatMoney(selectedSnapshotDetail.net_profit) }} ({{
                  selectedSnapshotDetail.profit_margin
                }}%)</span
              >
            </div>
          </div>

          <div class="text-12px text-gray-400 text-center">
            {{ t('analysis.archiveNotice', { user: selectedSnapshotDetail.closed_by || 'admin' }) }}
          </div>
        </div>
      </ElDialog>
    </div>

    <!-- ==================== VIEW 3: DAVRLARNI TAQQOSLASH (COMPARE) ==================== -->
    <div v-else-if="activeViewTab === 'compare'" class="fade-in-content">
      <!-- Comparison Toolbar & Preset Switcher -->
      <div
        class="compare-toolbar glass-panel mb-20px flex items-center justify-between flex-wrap gap-12px"
      >
        <div class="flex items-center gap-10px flex-wrap">
          <span class="text-13px font-bold text-[var(--el-text-color-regular)]">{{
            t('analysis.compareType')
          }}</span>
          <ElRadioGroup v-model="comparePreset" size="small" class="custom-radio-group">
            <ElTooltip :content="t('analysis.tipMoM')" placement="top">
              <ElRadioButton value="mom">{{ t('analysis.compareMoM') }}</ElRadioButton>
            </ElTooltip>
            <ElTooltip :content="t('analysis.tipQoQ')" placement="top">
              <ElRadioButton value="qoq">{{ t('analysis.compareQoQ') }}</ElRadioButton>
            </ElTooltip>
            <ElTooltip :content="t('analysis.tipLast30')" placement="top">
              <ElRadioButton value="last30">{{ t('analysis.compareLast30') }}</ElRadioButton>
            </ElTooltip>
            <ElTooltip :content="t('analysis.tipYoY')" placement="top">
              <ElRadioButton value="yoy">{{ t('analysis.compareYoY') }}</ElRadioButton>
            </ElTooltip>
            <ElTooltip :content="t('analysis.tipCustom')" placement="top">
              <ElRadioButton value="custom">{{ t('analysis.compareCustom') }}</ElRadioButton>
            </ElTooltip>
          </ElRadioGroup>
        </div>

        <!-- Custom Date Range Pickers (if custom selected) -->
        <div v-if="comparePreset === 'custom'" class="flex items-center gap-10px flex-wrap">
          <div class="flex items-center gap-6px">
            <span class="text-12px font-semibold text-blue-600">{{ t('analysis.period1') }}:</span>
            <ElDatePicker
              v-model="period1Dates"
              type="daterange"
              size="small"
              range-separator="~"
              :start-placeholder="t('analysis.startPlaceholder')"
              :end-placeholder="t('analysis.endPlaceholder')"
              value-format="YYYY-MM-DD"
              style="width: 220px"
            />
          </div>
          <div class="flex items-center gap-6px">
            <span class="text-12px font-semibold text-amber-600">{{ t('analysis.period2') }}:</span>
            <ElDatePicker
              v-model="period2Dates"
              type="daterange"
              size="small"
              range-separator="~"
              :start-placeholder="t('analysis.startPlaceholder')"
              :end-placeholder="t('analysis.endPlaceholder')"
              value-format="YYYY-MM-DD"
              style="width: 220px"
            />
          </div>
        </div>
      </div>

      <!-- Comparison KPI Executive Cards with Helpful Hover Tooltips -->
      <ElSkeleton :loading="comparisonLoading" animated>
        <template #template>
          <ElRow :gutter="16" class="mb-20px">
            <ElCol
              v-for="i in 4"
              :key="i"
              :xl="6"
              :lg="6"
              :md="12"
              :sm="12"
              :xs="24"
              class="mb-14px"
            >
              <div
                class="compare-kpi-card glass-panel p-20px h-[120px] flex flex-col justify-between"
              >
                <ElSkeletonItem variant="text" style="width: 50%; height: 16px" />
                <ElSkeletonItem variant="h1" style="width: 65%; height: 28px" />
                <div class="flex justify-between items-center">
                  <ElSkeletonItem variant="text" style="width: 35%; height: 14px" />
                  <ElSkeletonItem variant="text" style="width: 45%; height: 14px" />
                </div>
              </div>
            </ElCol>
          </ElRow>
        </template>
        <template #default>
          <ElRow :gutter="16" class="mb-20px">
            <!-- 1. Revenue Comparison KPI Card -->
            <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
              <ElTooltip :content="t('analysis.tipRevDiff')" placement="top">
                <div class="compare-kpi-card glass-panel card-blue cursor-help">
                  <div class="kpi-title">{{ t('analysis.revenueGrowth') }}</div>
                  <div class="kpi-main-val text-blue">
                    {{ comparisonData.revDiff >= 0 ? '+$' : '-$'
                    }}{{ formatMoney(Math.abs(comparisonData.revDiff)) }}
                  </div>
                  <div class="flex items-center justify-between">
                    <span
                      class="growth-tag"
                      :class="comparisonData.revGrowth >= 0 ? 'tag-green' : 'tag-red'"
                    >
                      <Icon
                        :icon="comparisonData.revGrowth >= 0 ? 'ep:caret-top' : 'ep:caret-bottom'"
                        class="mr-2px"
                      />
                      {{ comparisonData.revGrowth >= 0 ? '+' : '' }}{{ comparisonData.revGrowth }}%
                    </span>
                    <span class="text-11px text-muted"
                      >{{ t('analysis.period1') }}:
                      <b>${{ formatMoney(comparisonData.p1Revenue) }}</b></span
                    >
                  </div>
                </div>
              </ElTooltip>
            </ElCol>

            <!-- 2. COGS Comparison KPI Card -->
            <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
              <ElTooltip :content="t('analysis.tipCogsDiff')" placement="top">
                <div class="compare-kpi-card glass-panel card-amber cursor-help">
                  <div class="kpi-title">{{ t('analysis.cogsDiff') }}</div>
                  <div class="kpi-main-val text-amber">
                    {{ comparisonData.cogsDiff >= 0 ? '+$' : '-$'
                    }}{{ formatMoney(Math.abs(comparisonData.cogsDiff)) }}
                  </div>
                  <div class="flex items-center justify-between">
                    <span
                      class="growth-tag"
                      :class="comparisonData.cogsGrowth <= 0 ? 'tag-green' : 'tag-red'"
                    >
                      <Icon
                        :icon="comparisonData.cogsGrowth >= 0 ? 'ep:caret-top' : 'ep:caret-bottom'"
                        class="mr-2px"
                      />
                      {{ comparisonData.cogsGrowth >= 0 ? '+' : ''
                      }}{{ comparisonData.cogsGrowth }}%
                    </span>
                    <span class="text-11px text-muted"
                      >{{ t('analysis.period1') }}:
                      <b>${{ formatMoney(comparisonData.p1COGS) }}</b></span
                    >
                  </div>
                </div>
              </ElTooltip>
            </ElCol>

            <!-- 3. Payroll Comparison KPI Card -->
            <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
              <ElTooltip :content="t('analysis.tipPayrollDiff')" placement="top">
                <div class="compare-kpi-card glass-panel card-purple cursor-help">
                  <div class="kpi-title">{{ t('analysis.payrollDiff') }}</div>
                  <div class="kpi-main-val text-purple">
                    {{ comparisonData.payrollDiff >= 0 ? '+$' : '-$'
                    }}{{ formatMoney(Math.abs(comparisonData.payrollDiff)) }}
                  </div>
                  <div class="flex items-center justify-between">
                    <span
                      class="growth-tag"
                      :class="comparisonData.payrollGrowth <= 0 ? 'tag-green' : 'tag-red'"
                    >
                      <Icon
                        :icon="
                          comparisonData.payrollGrowth >= 0 ? 'ep:caret-top' : 'ep:caret-bottom'
                        "
                        class="mr-2px"
                      />
                      {{ comparisonData.payrollGrowth >= 0 ? '+' : ''
                      }}{{ comparisonData.payrollGrowth }}%
                    </span>
                    <span class="text-11px text-muted"
                      >{{ t('analysis.period1') }}:
                      <b>${{ formatMoney(comparisonData.p1Payroll) }}</b></span
                    >
                  </div>
                </div>
              </ElTooltip>
            </ElCol>

            <!-- 4. Real Net Profit Comparison KPI Card -->
            <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
              <ElTooltip :content="t('analysis.tipProfitDiff')" placement="top">
                <div class="compare-kpi-card glass-panel glow-emerald cursor-help">
                  <div class="kpi-title text-emerald-700 dark:text-emerald-300 font-extrabold">{{
                    t('analysis.netProfitChange')
                  }}</div>
                  <div class="kpi-main-val text-emerald">
                    {{ comparisonData.profitDiff >= 0 ? '+$' : '-$'
                    }}{{ formatMoney(Math.abs(comparisonData.profitDiff)) }}
                  </div>
                  <div class="flex items-center justify-between">
                    <span
                      class="growth-tag"
                      :class="comparisonData.profitGrowth >= 0 ? 'tag-green' : 'tag-red'"
                    >
                      <Icon
                        :icon="
                          comparisonData.profitGrowth >= 0 ? 'ep:caret-top' : 'ep:caret-bottom'
                        "
                        class="mr-2px"
                      />
                      {{ comparisonData.profitGrowth >= 0 ? '+' : ''
                      }}{{ comparisonData.profitGrowth }}%
                    </span>
                    <span class="text-11px text-emerald-700 dark:text-emerald-300"
                      >{{ t('analysis.period1') }}:
                      <b>${{ formatMoney(comparisonData.p1Profit) }}</b> ({{
                        comparisonData.p1Margin
                      }}%)</span
                    >
                  </div>
                </div>
              </ElTooltip>
            </ElCol>
          </ElRow>
        </template>
      </ElSkeleton>

      <!-- Side-by-Side Comparison Charts -->
      <ElRow :gutter="20" class="mb-20px">
        <ElCol :xl="15" :lg="15" :md="24" :sm="24" :xs="24" class="mb-16px">
          <div class="chart-card glass-panel h-full">
            <div class="chart-card-header">
              <div class="chart-card-dot green"></div>
              <ElTooltip :content="t('analysis.tipComparisonBar')" placement="top">
                <span class="header-title cursor-help"
                  >{{ period1Label }} vs {{ period2Label }}
                  {{ t('analysis.comparisonChart') }}</span
                >
              </ElTooltip>
            </div>
            <div class="chart-body">
              <ElSkeleton :loading="comparisonLoading" animated :rows="6">
                <template #default>
                  <Echart :options="comparisonBarOptions as any" :height="320" />
                </template>
              </ElSkeleton>
            </div>
          </div>
        </ElCol>

        <ElCol :xl="9" :lg="9" :md="24" :sm="24" :xs="24" class="mb-16px">
          <div class="chart-card glass-panel h-full">
            <div class="chart-card-header">
              <div class="chart-card-dot blue"></div>
              <ElTooltip :content="t('analysis.tipRevenueStructure')" placement="top">
                <span class="header-title cursor-help">{{ t('analysis.revenueStructure') }}</span>
              </ElTooltip>
            </div>
            <div class="chart-body">
              <ElSkeleton :loading="comparisonLoading" animated :rows="6">
                <template #default>
                  <Echart :options="comparisonCategoryOptions as any" :height="320" />
                </template>
              </ElSkeleton>
            </div>
          </div>
        </ElCol>
      </ElRow>

      <!-- Complete Metric Delta Comparison Table -->
      <div class="chart-card glass-panel mb-20px">
        <div class="chart-card-header justify-between">
          <div class="flex items-center gap-10px">
            <div class="chart-card-dot green"></div>
            <ElTooltip :content="t('analysis.tipDeltaTable')" placement="top">
              <span class="header-title cursor-help">{{ t('analysis.deltaTableTitle') }}</span>
            </ElTooltip>
          </div>
        </div>
        <div class="p-16px">
          <ElTable
            v-loading="comparisonLoading"
            :data="comparisonTable"
            border
            size="small"
            class="financial-summary-table"
          >
            <ElTableColumn prop="metric" :label="t('analysis.financialMetric')" min-width="220">
              <template #default="{ row }">
                <ElTooltip :content="row.tooltip" placement="top">
                  <div class="flex flex-col cursor-help">
                    <span class="font-bold text-[var(--el-text-color-primary)]">{{
                      row.metric
                    }}</span>
                    <span class="text-11px text-gray-500">{{ row.desc }}</span>
                  </div>
                </ElTooltip>
              </template>
            </ElTableColumn>

            <ElTableColumn prop="p1" :label="period1Label" width="160" align="right">
              <template #default="{ row }">
                <ElTooltip :content="t('analysis.tipP1Value')" placement="top">
                  <span class="font-mono font-bold text-blue-600 dark:text-blue-400 cursor-help">
                    {{ row.isPercentage ? `${row.p1}%` : `$${formatMoney(row.p1)}` }}
                  </span>
                </ElTooltip>
              </template>
            </ElTableColumn>

            <ElTableColumn prop="p2" :label="period2Label" width="160" align="right">
              <template #default="{ row }">
                <ElTooltip :content="t('analysis.tipP2Value')" placement="top">
                  <span class="font-mono text-gray-600 dark:text-gray-300 cursor-help">
                    {{ row.isPercentage ? `${row.p2}%` : `$${formatMoney(row.p2)}` }}
                  </span>
                </ElTooltip>
              </template>
            </ElTableColumn>

            <ElTableColumn
              prop="diff"
              :label="t('analysis.absoluteDiff')"
              width="150"
              align="right"
            >
              <template #default="{ row }">
                <ElTooltip :content="t('analysis.tipDiffValue')" placement="top">
                  <span
                    class="font-mono font-bold cursor-help"
                    :class="
                      row.status === 'positive'
                        ? 'text-emerald-600'
                        : row.status === 'negative'
                          ? 'text-rose-600'
                          : 'text-gray-500'
                    "
                  >
                    {{ row.diff >= 0 ? '+' : ''
                    }}{{ row.isPercentage ? `${row.diff}%` : `$${formatMoney(row.diff)}` }}
                  </span>
                </ElTooltip>
              </template>
            </ElTableColumn>

            <ElTableColumn
              prop="growth"
              :label="t('analysis.growthRate')"
              width="140"
              align="center"
            >
              <template #default="{ row }">
                <ElTooltip :content="t('analysis.tipGrowthValue')" placement="top">
                  <ElTag
                    :type="
                      row.status === 'positive'
                        ? 'success'
                        : row.status === 'negative'
                          ? 'danger'
                          : 'info'
                    "
                    effect="dark"
                    round
                    class="cursor-help"
                  >
                    <Icon
                      :icon="row.growth >= 0 ? 'ep:caret-top' : 'ep:caret-bottom'"
                      class="mr-2px"
                    />
                    {{ row.growth >= 0 ? '+' : '' }}{{ row.growth }}%
                  </ElTag>
                </ElTooltip>
              </template>
            </ElTableColumn>
          </ElTable>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.analysis-container {
  padding: 4px;
}

.fade-in-content {
  animation: fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.cursor-help {
  cursor: help;
}

.analytics-header-toolbar {
  .mode-pills {
    .mode-btn {
      position: relative;
      display: flex;
      align-items: center;
      padding: 8px 16px;
      font-size: 13px;
      font-weight: 700;
      border: none;
      background: transparent;
      color: var(--el-text-color-regular, #64748b);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        color: var(--el-color-primary, #3b82f6);
      }

      &.active {
        background: var(--el-bg-color-overlay, #ffffff);
        color: var(--el-color-primary, #3b82f6);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      }

      .badge-count {
        margin-left: 6px;
        background: #3b82f6;
        color: #ffffff;
        font-size: 10px;
        font-weight: 800;
        padding: 1px 6px;
        border-radius: 10px;
      }
    }
  }
}

// Grand Hero Closing Station
.station-hero-card {
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  background: var(--el-bg-color-overlay, #ffffff);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);

  .hero-glow-blob {
    position: absolute;
    top: -40px;
    right: -40px;
    width: 200px;
    height: 200px;
    background: radial-gradient(
      circle,
      rgba(59, 130, 246, 0.15) 0%,
      rgba(16, 185, 129, 0.05) 50%,
      transparent 70%
    );
    border-radius: 50%;
    pointer-events: none;
  }

  .station-icon-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(16, 185, 129, 0.12));
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 12px;
    font-size: 22px;
  }

  .quick-month-pills {
    .quick-pill-btn {
      padding: 4px 10px;
      font-size: 11px;
      font-weight: 700;
      border: 1px solid var(--el-border-color-lighter, #e2e8f0);
      background: var(--el-fill-color-light, #f8fafc);
      color: var(--el-text-color-regular, #64748b);
      border-radius: 20px;
      cursor: pointer;
      transition: all 0.18s ease;

      &:hover {
        border-color: #3b82f6;
        color: #3b82f6;
      }

      &.active {
        background: #3b82f6;
        color: #ffffff;
        border-color: #3b82f6;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
      }
    }
  }

  .grand-archive-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 800;
    color: #ffffff;
    background: linear-gradient(135deg, #059669, #10b981);
    border: none;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
    cursor: pointer;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);

    &:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 22px rgba(16, 185, 129, 0.55);
    }

    &:active {
      transform: translateY(0);
    }

    &--update {
      background: linear-gradient(135deg, #2563eb, #3b82f6);
      box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
      &:hover:not(:disabled) {
        box-shadow: 0 6px 22px rgba(59, 130, 246, 0.55);
      }
    }
  }

  .status-indicator-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;

    &.is-closed {
      background: #10b981;
      box-shadow: 0 0 10px rgba(16, 185, 129, 0.8);
    }

    &.is-open {
      background: #f59e0b;
      box-shadow: 0 0 10px rgba(245, 158, 11, 0.8);
      animation: pulseDot 1.8s infinite ease-in-out;
    }
  }
}

// 4 Grand Stat Cards
.grand-stat-card {
  padding: 18px 20px;
  border-radius: 16px;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  background: var(--el-bg-color-overlay, #ffffff);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
  transition: all 0.24s ease;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.07);
  }

  .stat-subtitle {
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--el-text-color-secondary, #64748b);
  }

  .stat-value {
    font-size: 26px;
    font-weight: 900;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    letter-spacing: -0.02em;
    margin: 4px 0 12px 0;
  }

  .stat-icon-wrap {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
  }

  .stat-footer-strip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 8px;
    border-top: 1px dashed var(--el-border-color-lighter, #e2e8f0);

    .stat-subtag {
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 10px;
    }
  }

  &.stat-card--blue {
    border-color: rgba(59, 130, 246, 0.25);
  }
  &.stat-card--amber {
    border-color: rgba(245, 158, 11, 0.25);
  }
  &.stat-card--purple {
    border-color: rgba(168, 85, 247, 0.25);
  }
  &.stat-card--emerald {
    border-color: rgba(16, 185, 129, 0.4);
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(5, 150, 105, 0.12) 100%);
  }
}

// Center Hero in Donut Chart
.donut-center-hero {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  .center-title {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.05em;
    color: var(--el-text-color-secondary, #64748b);
  }

  .center-amount {
    line-height: 1.1;
    margin: 2px 0;
  }
}

.donut-legend-matrix {
  .legend-pill-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 3px 0;

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      flex-shrink: 0;
    }
  }
}

.chart-card {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  background: var(--el-bg-color-overlay, #ffffff);

  .chart-card-header {
    display: flex;
    align-items: center;
    padding: 14px 20px;
    border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0);

    .header-title {
      font-size: 14px;
      font-weight: 700;
      color: var(--el-text-color-primary, #1e293b);
    }

    .chart-card-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;

      &.green {
        background: #10b981;
      }
      &.blue {
        background: #3b82f6;
      }
      &.amber {
        background: #f59e0b;
      }

      &.pulse {
        animation: pulseDot 2s infinite ease-in-out;
      }
    }
  }

  .chart-body {
    padding: 14px 16px;
  }
}

.compare-toolbar {
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  background: var(--el-bg-color-overlay, #ffffff);
}

.compare-kpi-card {
  border-radius: 14px;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  background: var(--el-bg-color-overlay, #ffffff);
  padding: 18px 20px;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
  transition: all 0.28s ease;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08);
  }

  &.card-blue {
    border-color: rgba(59, 130, 246, 0.25);
  }
  &.card-amber {
    border-color: rgba(245, 158, 11, 0.25);
  }
  &.card-purple {
    border-color: rgba(168, 85, 247, 0.25);
  }
  &.glow-emerald {
    border-color: rgba(16, 185, 129, 0.45);
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.06) 0%, rgba(5, 150, 105, 0.12) 100%);
  }

  .kpi-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--el-text-color-secondary, #64748b);
  }

  .kpi-main-val {
    font-size: 24px;
    font-weight: 800;
    margin: 6px 0 10px 0;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    letter-spacing: -0.02em;

    &.text-blue {
      color: #2563eb;
    }
    &.text-amber {
      color: #d97706;
    }
    &.text-purple {
      color: #7c3aed;
    }
    &.text-emerald {
      color: #059669;
    }
  }

  .growth-tag {
    font-size: 11px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 10px;

    &.tag-green {
      background: #10b981;
      color: #ffffff;
    }
    &.tag-red {
      background: #ef4444;
      color: #ffffff;
    }
    &.tag-neutral {
      background: #64748b;
      color: #ffffff;
    }
  }
}

:global(.dark) {
  .station-hero-card,
  .grand-stat-card,
  .chart-card,
  .compare-toolbar {
    background: #0f172a;
    border-color: #1e293b;
  }

  .station-hero-card {
    .quick-month-pills .quick-pill-btn {
      background: #1e293b;
      border-color: #334155;
      color: #94a3b8;
      &.active {
        background: #3b82f6;
        color: #ffffff;
      }
    }
  }

  .grand-stat-card {
    &.stat-card--emerald {
      background: linear-gradient(
        135deg,
        rgba(16, 185, 129, 0.12) 0%,
        rgba(5, 150, 105, 0.22) 100%
      );
    }
  }

  .compare-kpi-card {
    background: #0f172a;
    border-color: #1e293b;

    .kpi-main-val {
      &.text-blue {
        color: #60a5fa;
      }
      &.text-amber {
        color: #fbbf24;
      }
      &.text-purple {
        color: #c084fc;
      }
      &.text-emerald {
        color: #34d399;
      }
    }

    &.glow-emerald {
      background: linear-gradient(
        135deg,
        rgba(16, 185, 129, 0.12) 0%,
        rgba(5, 150, 105, 0.22) 100%
      );
      border-color: rgba(16, 185, 129, 0.5);
    }
  }
}

.financial-summary-table {
  :deep(.el-table__header th) {
    background-color: var(--el-fill-color-light, #f8fafc) !important;
    font-weight: 700;
    color: var(--el-text-color-primary, #1e293b);
  }
}

.luxury-archive-table {
  border-radius: 12px;
  overflow: hidden;
  :deep(.el-table__row) {
    transition: background 0.15s ease;
    &:hover > td {
      background: rgba(59, 130, 246, 0.05) !important;
    }
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulseDot {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.6;
  }
}

.pulse-glow {
  animation: pulseGlow 2.5s infinite ease-in-out;
}

@keyframes pulseGlow {
  0%,
  100% {
    transform: scale(1);
    filter: drop-shadow(0 0 4px rgba(16, 185, 129, 0.4));
  }
  50% {
    transform: scale(1.08);
    filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.8));
  }
}
</style>
