<template>
  <div class="sales-history-container">
    <ContentWrap>
      <!-- Filter and Stats Bar -->
      <div class="filter-bar">
        <ElForm :inline="true" :model="searchQuery" class="filter-form">
          <ElFormItem class="!mr-0">
            <ElInput
              v-model="searchQuery.search"
              placeholder="Chek #, Kassir yoki Mijoz..."
              clearable
              style="width: 260px"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <Icon icon="ep:search" class="text-gray-400" />
              </template>
            </ElInput>
          </ElFormItem>

          <ElFormItem class="!mr-0">
            <ElSelect
              v-model="searchQuery.payment_method"
              placeholder="To'lov usuli"
              clearable
              style="width: 160px"
            >
              <ElOption :label="t('erp.cash')" value="naqd" />
              <ElOption :label="t('erp.card')" value="karta" />
              <ElOption label="O'tkazma" value="otkazma" />
              <ElOption :label="t('erp.debt')" value="nasiya" />
            </ElSelect>
          </ElFormItem>

          <ElFormItem class="!mr-0">
            <ElButton type="primary" class="btn-search" @click="handleSearch">
              <Icon icon="ep:search" class="mr-4px" />{{ t('common.search') }}</ElButton
            >
            <ElButton class="btn-reset" @click="resetSearch">{{ t('common.reset') }}</ElButton>
          </ElFormItem>
        </ElForm>

        <div class="total-sales-stat">
          <div class="stat-icon">
            <Icon icon="ep:money" />
          </div>
          <div>
            <div class="stat-label">Jami Sotuv Haridi</div>
            <div class="stat-value">${{ formatMoney(totalSalesAmount) }}</div>
          </div>
        </div>
      </div>

      <!-- Sales History Table -->
      <div class="table-wrap">
        <ElTable
          v-loading="loading"
          :data="salesList"
          style="width: 100%"
          border
          class="custom-sales-table"
        >
          <ElTableColumn prop="receipt_number" :label="t('erp.receiptNumber')" width="220">
            <template #default="scope">
              <span class="receipt-badge">
                <Icon icon="ep:tickets" class="mr-4px" />{{ scope.row.receipt_number }}
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="created_at" :label="t('erp.dateTime')" width="180">
            <template #default="scope">
              <span class="mono-date">{{ scope.row.created_at }}</span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="cashier_name" label="Kassir (Kim tomonidan)" width="160">
            <template #default="scope">
              <span class="cashier-badge">
                <Icon icon="ep:user" class="mr-4px" />{{ scope.row.cashier_name || 'admin' }}
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="customer_name" label="Mijoz" width="160">
            <template #default="scope">
              <span v-if="scope.row.customer_name" class="customer-name">{{
                scope.row.customer_name
              }}</span>
              <span v-else class="empty-dash">—</span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="payment_method" label="To'lov Usuli" width="140" align="center">
            <template #default="scope">
              <span :class="['payment-pill', `payment-pill--${scope.row.payment_method}`]">
                {{ scope.row.payment_method }}
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="total_items"
            :label="t('erp.productQuantity')"
            width="140"
            align="center"
          >
            <template #default="scope">
              <span class="items-count">{{ scope.row.total_items }} dona</span>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="total_amount"
            :label="t('erp.totalAmountDollar')"
            width="160"
            align="right"
          >
            <template #default="scope">
              <span class="total-amount">${{ formatMoney(scope.row.total_amount) }}</span>
            </template>
          </ElTableColumn>

          <ElTableColumn label="Batafsil" width="110" align="center" fixed="right">
            <template #default="scope">
              <ElButton size="small" class="btn-detail" @click="openReceiptDetail(scope.row)">
                <Icon icon="ep:document" class="mr-2px" /> Chek
              </ElButton>
            </template>
          </ElTableColumn>
        </ElTable>
      </div>

      <!-- Pagination -->
      <div class="pagination-wrap">
        <ElPagination
          v-model:current-page="pagination.pageIndex"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </ContentWrap>

    <!-- Receipt Detail Modal -->
    <Dialog v-model="detailModalVisible" title="Chek Ma'lumotlari va Mahsulotlar" width="600px">
      <div v-if="selectedSale" class="receipt-detail-card" v-loading="receiptLoading">
        <div class="receipt-header">
          <span class="receipt-title">CHEK #{{ selectedSale.receipt_number }}</span>
          <span :class="['payment-pill', `payment-pill--${selectedSale.payment_method}`]">
            {{ selectedSale.payment_method?.toUpperCase() }}
          </span>
        </div>

        <div class="receipt-meta">
          <div><b>Sana:</b> {{ selectedSale.created_at }}</div>
          <div><b>Kassir:</b> {{ selectedSale.cashier_name || 'admin' }}</div>
          <div v-if="selectedSale.customer_name"
            ><b>Mijoz:</b> {{ selectedSale.customer_name }}</div
          >
        </div>

        <div class="receipt-items-wrap">
          <div
            class="flex items-center font-bold text-11px text-gray-400 pb-6px border-b border-gray-700 uppercase tracking-wider mb-8px"
          >
            <span class="w-24px text-center">#</span>
            <span class="flex-1 px-6px">MAHSULOT NOMI</span>
            <span class="w-100px text-center">SONI</span>
            <span class="w-90px text-right">NARXI</span>
            <span class="w-100px text-right">JAMI</span>
          </div>

          <div
            v-if="selectedSale.items && selectedSale.items.length > 0"
            class="divide-y divide-gray-800"
          >
            <div
              v-for="(item, idx) in selectedSale.items"
              :key="item.id || idx"
              class="flex items-center py-6px text-13px"
            >
              <span class="w-24px text-center text-11px text-gray-400 font-mono">{{
                idx + 1
              }}</span>
              <div class="flex-1 px-6px min-w-0">
                <span
                  class="font-bold text-[var(--el-text-color-primary)] block leading-snug break-words"
                >
                  {{ item.product_name }}
                </span>
                <span v-if="item.shtrix_code" class="text-10px text-gray-400 font-mono">
                  {{ item.shtrix_code }}
                </span>
              </div>
              <span
                class="w-100px text-center font-mono font-bold text-[var(--el-text-color-primary)]"
              >
                {{ formatMoney(item.quantity) }} {{ item.unit_name || 'dona' }}
              </span>
              <span class="w-90px text-right font-mono text-gray-400">
                ${{ formatMoney(item.price) }}
              </span>
              <span class="w-100px text-right font-mono font-bold text-emerald-500">
                ${{ formatMoney(item.total || item.quantity * item.price) }}
              </span>
            </div>
          </div>
          <div v-else-if="!receiptLoading" class="text-center py-16px text-gray-400 text-12px">
            Mahsulotlar mavjud emas
          </div>
        </div>

        <div class="receipt-footer mt-16px pt-12px border-t border-gray-700 space-y-6px">
          <div class="flex justify-between text-13px text-gray-400">
            <span>Mahsulotlar soni:</span>
            <span class="font-bold text-[var(--el-text-color-primary)]">
              {{
                (selectedSale.items || []).reduce(
                  (acc: number, it: any) => acc + (Number(it.quantity) || 1),
                  0
                )
              }}
              dona
            </span>
          </div>
          <div
            v-if="(selectedSale.discount || 0) > 0"
            class="flex justify-between text-amber-500 text-13px"
          >
            <span>Chegirma:</span>
            <span>-${{ formatMoney(selectedSale.discount) }}</span>
          </div>
          <div
            class="flex justify-between items-center text-18px font-bold text-emerald-500 pt-6px border-t border-dashed border-gray-700"
          >
            <span>JAMI SUMMA:</span>
            <span class="text-22px font-mono">${{ formatMoney(selectedSale.total_amount) }}</span>
          </div>
          <div class="flex justify-between text-13px text-gray-400">
            <span>To'langan:</span>
            <span class="font-mono font-bold"
              >${{
                formatMoney(
                  selectedSale.paid_amount !== undefined
                    ? selectedSale.paid_amount
                    : selectedSale.total_amount
                )
              }}</span
            >
          </div>
          <div
            v-if="(selectedSale.debt_amount || 0) > 0"
            class="flex justify-between text-13px text-red-400 font-bold"
          >
            <span>Qarz (Nasiya):</span>
            <span class="font-mono">${{ formatMoney(selectedSale.debt_amount) }}</span>
          </div>
        </div>

        <div class="flex justify-end gap-10px mt-20px pt-12px border-t border-gray-700">
          <ElButton
            type="primary"
            size="default"
            class="font-bold"
            @click="() => printReceiptHistory('thermal')"
          >
            <Icon icon="ep:printer" class="mr-4px" /> Termal Chek (80mm)
          </ElButton>
          <ElButton
            type="success"
            plain
            size="default"
            class="font-bold"
            @click="() => printReceiptHistory('a4')"
          >
            <Icon icon="ep:document" class="mr-4px" /> Standart (A4)
          </ElButton>
          <ElButton size="default" @click="detailModalVisible = false">Yopish</ElButton>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
defineOptions({ name: 'SalesHistory' })
import { ref, reactive, computed, onMounted } from 'vue'
import { ContentWrap } from '@/components/ContentWrap'
import { Dialog } from '@/components/Dialog'
import { Icon } from '@/components/Icon'
import {
  ElButton,
  ElTable,
  ElTableColumn,
  ElTag,
  ElPagination,
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption
} from 'element-plus'
import { getSalesListApi, getSaleReceiptApi, SaleType } from '@/api/sales'

const loading = ref(false)
const salesList = ref<SaleType[]>([])
const total = ref(0)
const selectedSale = ref<SaleType | null>(null)
const detailModalVisible = ref(false)
const receiptLoading = ref(false)

const searchQuery = reactive({
  search: '',
  payment_method: '',
  cashier_name: ''
})

const pagination = reactive({
  pageIndex: 1,
  pageSize: 20
})

const formatMoney = (val: number | string | undefined | null) => {
  if (val === undefined || val === null || val === '') return '0'
  const num = Number(val)
  if (isNaN(num)) return '0'
  return Math.round(num)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

const salesSummary = ref<any>(null)

const totalSalesAmount = computed(() => {
  if (salesSummary.value && salesSummary.value.allTimeRevenue !== undefined) {
    return salesSummary.value.allTimeRevenue
  }
  return salesList.value.reduce((sum, s) => sum + (s.total_amount || 0), 0)
})

const fetchSalesData = async () => {
  loading.value = true
  try {
    const res: any = await getSalesListApi({
      pageIndex: pagination.pageIndex,
      pageSize: pagination.pageSize,
      search: searchQuery.search || undefined,
      payment_method: searchQuery.payment_method || undefined,
      cashier_name: searchQuery.cashier_name || undefined
    })
    if (res && res.data) {
      salesList.value = res.data.list || []
      total.value = res.data.total || 0
      if (res.data.summary) {
        salesSummary.value = res.data.summary
      }
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.pageIndex = 1
  fetchSalesData()
}

const resetSearch = () => {
  searchQuery.search = ''
  searchQuery.payment_method = ''
  searchQuery.cashier_name = ''
  handleSearch()
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  fetchSalesData()
}

const handleCurrentChange = (val: number) => {
  pagination.pageIndex = val
  fetchSalesData()
}

const openReceiptDetail = async (row: SaleType) => {
  selectedSale.value = { ...row }
  detailModalVisible.value = true

  if (!row.items || row.items.length === 0) {
    try {
      receiptLoading.value = true
      const receiptNo = row.receipt_number || row.id || ''
      if (receiptNo) {
        const res: any = await getSaleReceiptApi(receiptNo)
        if (res && res.data) {
          selectedSale.value = {
            ...res.data,
            items: res.data.items || []
          }
        }
      }
    } catch (err) {
      console.warn('Error loading receipt details:', err)
    } finally {
      receiptLoading.value = false
    }
  }

  if (
    selectedSale.value &&
    (!selectedSale.value.items || selectedSale.value.items.length === 0) &&
    Number(selectedSale.value.total_amount) > 0
  ) {
    selectedSale.value.items = [
      {
        id: 'ITEM-' + (selectedSale.value.id || Date.now()),
        product_name: selectedSale.value.remark || "Ombor mahsulotlari to'plami",
        quantity: selectedSale.value.total_items || 1,
        unit_name: 'dona',
        price:
          Number(selectedSale.value.total_amount) / (Number(selectedSale.value.total_items) || 1),
        total: Number(selectedSale.value.total_amount)
      }
    ]
  }
}

const printReceiptHistory = (mode: 'thermal' | 'a4' = 'thermal') => {
  if (!selectedSale.value) return

  const s = selectedSale.value
  const items = s.items || []
  const dateStr = s.created_at || new Date().toLocaleString()
  const cashier = s.cashier_name || 'admin'
  const paymentMethodLabel = s.payment_method ? s.payment_method.toUpperCase() : 'NAQD'
  const totalAmount = formatMoney(s.total_amount)
  const paidAmount = formatMoney(
    s.paid_amount !== undefined && s.paid_amount !== null ? s.paid_amount : s.total_amount
  )
  const debtAmount = s.debt_amount ? formatMoney(s.debt_amount) : '0'
  const discount = s.discount ? formatMoney(s.discount) : '0'
  const totalItemsCount = items.reduce(
    (acc: number, it: any) => acc + (Number(it.quantity) || 1),
    0
  )

  let itemsHtml = ''
  if (mode === 'thermal') {
    items.forEach((it: any, idx: number) => {
      const q = it.quantity || 1
      const p = formatMoney(it.price)
      const t = formatMoney(it.total || it.quantity * it.price)
      itemsHtml += `
        <tr style="border-top: 1px dotted #000;">
          <td colspan="3" style="padding-top: 4px; font-weight: bold; font-size: 11px; word-break: break-word;">
            ${idx + 1}. ${it.product_name}
          </td>
        </tr>
        <tr>
          <td style="font-size: 10px; color: #444; padding-bottom: 4px;">
            ${it.shtrix_code ? '#' + it.shtrix_code : ''}
          </td>
          <td style="text-align: center; font-weight: bold; font-size: 11px; padding-bottom: 4px;">
            ${q} ${it.unit_name || 'dona'} &times; $${p}
          </td>
          <td style="text-align: right; font-weight: bold; font-size: 11px; padding-bottom: 4px;">
            $${t}
          </td>
        </tr>
      `
    })
  } else {
    items.forEach((it: any, idx: number) => {
      const q = it.quantity || 1
      const p = formatMoney(it.price)
      const t = formatMoney(it.total || it.quantity * it.price)
      itemsHtml += `
        <tr style="border-bottom: 1px solid #cbd5e1;">
          <td style="text-align: center; padding: 10px 8px; font-family: monospace;">${idx + 1}</td>
          <td style="padding: 10px 12px;">
            <div style="font-weight: bold; color: #0f172a;">${it.product_name}</div>
            ${it.shtrix_code ? `<div style="font-size: 11px; color: #64748b; font-family: monospace;">${it.shtrix_code}</div>` : ''}
          </td>
          <td style="text-align: center; padding: 10px 12px; font-weight: bold; font-family: monospace;">
            ${q} ${it.unit_name || 'dona'}
          </td>
          <td style="text-align: right; padding: 10px 12px; font-family: monospace;">
            $${p}
          </td>
          <td style="text-align: right; padding: 10px 12px; font-weight: bold; color: #059669; font-family: monospace;">
            $${t}
          </td>
        </tr>
      `
    })
  }

  const thermalHtml = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Chek #${s.receipt_number}</title>
        <style>
          @page { size: 80mm auto; margin: 2mm 0mm; }
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            font-family: 'Courier New', Courier, 'Lucida Console', Monaco, monospace;
            font-size: 12px; line-height: 1.35; color: #000; background: #fff;
            width: 76mm; max-width: 80mm; margin: 0 auto; padding: 8px 4px;
            -webkit-print-color-adjust: exact; print-color-adjust: exact;
          }
          .text-center { text-align: center; }
          .text-right { text-align: right; }
          .text-left { text-align: left; }
          .brand-title { font-size: 17px; font-weight: 900; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 2px; }
          .check-no { font-size: 13px; font-weight: bold; padding: 4px 0; border-top: 1px dashed #000; border-bottom: 1px dashed #000; margin: 6px 0; }
          .meta-table { width: 100%; font-size: 11px; margin-bottom: 6px; }
          .meta-table td { padding: 2px 0; vertical-align: top; }
          .dashed-divider { border-top: 1px dashed #000; margin: 6px 0; }
          .items-table { width: 100%; border-collapse: collapse; font-size: 11px; margin: 4px 0; }
          .items-table th { border-bottom: 1px dashed #000; padding: 4px 0; font-size: 10px; text-transform: uppercase; }
          .totals-table { width: 100%; font-size: 12px; margin-top: 6px; }
          .totals-table td { padding: 2px 0; }
          .grand-total-row td { font-size: 16px; font-weight: 900; padding: 6px 0; border-top: 2px dashed #000; border-bottom: 2px dashed #000; }
          .footer-section { text-align: center; margin-top: 14px; padding-top: 8px; border-top: 1px dashed #000; font-size: 10px; line-height: 1.4; }
          .barcode-box { font-family: monospace; font-size: 12px; font-weight: bold; letter-spacing: 2px; margin: 6px 0; }
          @media print { body { width: 76mm; margin: 0 auto; padding: 4px 2px; } }
        </style>
      </head>
      <body>
        <div class="text-center">
          <div class="brand-title">OMBORXONA ERP POS</div>
          <div class="check-no">CHEK #${s.receipt_number}</div>
        </div>

        <table class="meta-table">
          <tr><td class="text-left">Sana:</td><td class="text-right font-bold">${dateStr}</td></tr>
          <tr><td class="text-left">Kassir:</td><td class="text-right font-bold">${cashier}</td></tr>
          ${s.customer_name ? `<tr><td class="text-left">Mijoz:</td><td class="text-right font-bold">${s.customer_name}</td></tr>` : ''}
          <tr><td class="text-left">To'lov usuli:</td><td class="text-right font-bold">${paymentMethodLabel}</td></tr>
        </table>

        <div class="dashed-divider"></div>

        <table class="items-table">
          <thead>
            <tr>
              <th class="text-left" style="width: 35%;">MAHSULOT</th>
              <th class="text-center" style="width: 35%;">SONI &times; NARXI</th>
              <th class="text-right" style="width: 30%;">JAMI</th>
            </tr>
          </thead>
          <tbody>
            ${itemsHtml}
          </tbody>
        </table>

        <table class="totals-table">
          <tr><td class="text-left">Mahsulotlar soni:</td><td class="text-right font-bold">${totalItemsCount} dona</td></tr>
          ${Number(s.discount) > 0 ? `<tr><td class="text-left">Chegirma:</td><td class="text-right font-bold">-$${discount}</td></tr>` : ''}
          <tr class="grand-total-row"><td class="text-left">JAMI SUMMA:</td><td class="text-right">$${totalAmount}</td></tr>
          <tr><td class="text-left" style="padding-top: 4px;">To'langan summa:</td><td class="text-right font-bold" style="padding-top: 4px;">$${paidAmount}</td></tr>
          ${Number(s.debt_amount) > 0 ? `<tr style="font-weight: bold;"><td class="text-left">Qarz (Nasiya):</td><td class="text-right">$${debtAmount}</td></tr>` : ''}
        </table>

        <div class="footer-section">
          <div class="barcode-box">* ${s.receipt_number} *</div>
          <div>Xaridingiz uchun rahmat!</div>
          <div>Salomat bo'ling!</div>
        </div>
      </body>
    </html>
  `

  const a4Html = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Sotuv Cheki #${s.receipt_number}</title>
        <style>
          @page { size: A4; margin: 15mm; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 13px; color: #1a1a1a; line-height: 1.5; background: #fff; margin: 0; padding: 20px;
          }
          .header-row { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #059669; padding-bottom: 16px; margin-bottom: 20px; }
          .company-name { font-size: 24px; font-weight: 800; color: #065f46; }
          .receipt-title { font-size: 20px; font-weight: 700; color: #059669; text-align: right; }
          .meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 18px; margin-bottom: 24px; }
          .items-table { width: 100%; border-collapse: collapse; margin-bottom: 24px; }
          .items-table th { background: #f1f5f9; border: 1px solid #cbd5e1; padding: 10px 12px; font-weight: 700; font-size: 12px; text-transform: uppercase; }
          .items-table td { border: 1px solid #cbd5e1; padding: 10px 12px; }
          .summary-table { margin-left: auto; width: 340px; border-collapse: collapse; font-size: 14px; }
          .summary-table td { padding: 6px 8px; }
          .summary-total { border-top: 2px solid #065f46; border-bottom: 2px solid #065f46; font-size: 18px; font-weight: 800; color: #065f46; }
          .signature-row { display: flex; justify-content: space-between; margin-top: 60px; padding-top: 20px; }
          .sig-line { width: 220px; border-top: 1px solid #94a3b8; text-align: center; padding-top: 6px; font-size: 12px; color: #64748b; }
        </style>
      </head>
      <body>
        <div class="header-row">
          <div>
            <div class="company-name">OMBORXONA ERP POS</div>
          </div>
          <div>
            <div class="receipt-title">SOTUV CHEKI</div>
            <div style="font-family: monospace; font-size: 14px; font-weight: bold; text-align: right; margin-top: 4px;">#${s.receipt_number}</div>
          </div>
        </div>

        <div class="meta-grid">
          <div>
            <div><b>Sana va vaqt:</b> ${dateStr}</div>
            <div><b>Kassir / Xodim:</b> ${cashier}</div>
          </div>
          <div>
            <div><b>To'lov usuli:</b> ${paymentMethodLabel}</div>
            ${s.customer_name ? `<div><b>Mijoz:</b> ${s.customer_name}</div>` : ''}
          </div>
        </div>

        <table class="items-table">
          <thead>
            <tr>
              <th style="width: 40px; text-align: center;">#</th>
              <th>Mahsulot Nomi</th>
              <th style="width: 120px; text-align: center;">Soni</th>
              <th style="width: 140px; text-align: right;">Dona Narxi ($)</th>
              <th style="width: 140px; text-align: right;">Jami Summa ($)</th>
            </tr>
          </thead>
          <tbody>
            ${itemsHtml}
          </tbody>
        </table>

        <table class="summary-table">
          <tr><td>Jami mahsulotlar:</td><td style="text-align: right; font-weight: bold;">${totalItemsCount} dona</td></tr>
          ${Number(s.discount) > 0 ? `<tr style="color: #d97706;"><td>Chegirma:</td><td style="text-align: right; font-weight: bold;">-$${discount}</td></tr>` : ''}
          <tr class="summary-total"><td>JAMI SUMMA:</td><td style="text-align: right;">$${totalAmount}</td></tr>
          <tr><td>To'langan summa:</td><td style="text-align: right; font-weight: bold;">$${paidAmount}</td></tr>
          ${Number(s.debt_amount) > 0 ? `<tr style="color: #dc2626; font-weight: bold;"><td>Qarz (Nasiya):</td><td style="text-align: right;">$${debtAmount}</td></tr>` : ''}
        </table>

        <div class="signature-row">
          <div class="sig-line">Kassir imzosi (${cashier})</div>
          <div class="sig-line">Mijoz imzosi</div>
        </div>
      </body>
    </html>
  `

  const htmlToPrint = mode === 'thermal' ? thermalHtml : a4Html

  let printFrame = document.getElementById('receipt-print-iframe') as HTMLIFrameElement
  if (!printFrame) {
    printFrame = document.createElement('iframe')
    printFrame.id = 'receipt-print-iframe'
    printFrame.style.position = 'fixed'
    printFrame.style.right = '0'
    printFrame.style.bottom = '0'
    printFrame.style.width = '0'
    printFrame.style.height = '0'
    printFrame.style.border = 'none'
    document.body.appendChild(printFrame)
  }

  const doc =
    printFrame.contentDocument ||
    (printFrame.contentWindow ? printFrame.contentWindow.document : null)
  if (doc) {
    doc.open()
    doc.write(htmlToPrint)
    doc.close()
    setTimeout(() => {
      if (printFrame.contentWindow) {
        printFrame.contentWindow.focus()
        printFrame.contentWindow.print()
      }
    }, 350)
  }
}

import { useEventBus } from '@/hooks/event/useEventBus'

useEventBus({
  name: 'refresh-sales',
  callback: () => {
    fetchSalesData()
  }
})

useEventBus({
  name: 'ai-data-updated',
  callback: () => {
    fetchSalesData()
  }
})

onMounted(() => {
  fetchSalesData()
})
</script>

<style scoped lang="less">
// ─── Variables ────────────────────────────────────────────────
@blue: #3b82f6;
@blue-glow: #60a5fa;
@green: #10b981;
@green-glow: #10b981;
@amber: #f59e0b;
@amber-glow: #f59e0b;
@red: #ef4444;
@red-glow: #ef4444;
@purple: #8b5cf6;
@mono: 'SF Mono', 'Fira Code', 'Fira Mono', monospace;

// ─── Container ────────────────────────────────────────────────
.sales-history-container {
  background: transparent;
  min-height: 100%;
}

// ─── Filter Bar ───────────────────────────────────────────────
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: var(--el-bg-color-overlay, #ffffff);
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);

  .filter-form {
    flex: 1;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
  }
}

:global(.dark) {
  .filter-bar {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-color: #1e293b;
    box-shadow: none;
  }
}

// ─── Total Stat Card ──────────────────────────────────────────
.total-sales-stat {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(52, 211, 153, 0.05));
  border: 1px solid rgba(16, 185, 129, 0.35);
  border-radius: 10px;
  padding: 10px 18px;
  position: relative;
  overflow: hidden;
  transition:
    box-shadow 0.25s,
    transform 0.25s;

  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, @green, #34d399);
    border-radius: 0 0 10px 10px;
  }

  &:hover {
    box-shadow: 0 0 18px rgba(16, 185, 129, 0.25);
    transform: translateY(-1px);
  }

  .stat-icon {
    font-size: 22px;
    color: @green;
    display: flex;
    align-items: center;
  }

  .stat-label {
    font-size: 11px;
    color: var(--el-text-color-secondary, #64748b);
    letter-spacing: 0.04em;
  }

  .stat-value {
    font-family: @mono;
    font-size: 17px;
    font-weight: 700;
    color: @green;
  }
}

// ─── Buttons ──────────────────────────────────────────────────
.btn-search {
  background: linear-gradient(135deg, @blue, darken(@blue, 8%)) !important;
  border: none !important;
  box-shadow: 0 2px 10px rgba(59, 130, 246, 0.35);
  transition:
    transform 0.2s,
    box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 18px rgba(59, 130, 246, 0.55);
  }
}

.btn-reset {
  background: var(--el-fill-color, #f1f5f9) !important;
  border: 1px solid var(--el-border-color, #e2e8f0) !important;
  color: var(--el-text-color-regular, #475569) !important;
  transition:
    transform 0.2s,
    box-shadow 0.2s,
    border-color 0.2s;

  &:hover {
    transform: translateY(-2px);
    border-color: @blue !important;
    color: @blue !important;
    box-shadow: 0 2px 10px rgba(59, 130, 246, 0.15);
  }
}

.btn-detail {
  background: linear-gradient(
    135deg,
    rgba(59, 130, 246, 0.18),
    rgba(96, 165, 250, 0.08)
  ) !important;
  border: 1px solid rgba(59, 130, 246, 0.4) !important;
  color: @blue !important;
  font-size: 12px !important;
  border-radius: 6px !important;
  transition:
    transform 0.2s,
    box-shadow 0.2s,
    background 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 12px rgba(59, 130, 246, 0.35);
    background: linear-gradient(
      135deg,
      rgba(59, 130, 246, 0.3),
      rgba(96, 165, 250, 0.15)
    ) !important;
  }
}

// ─── Table Wrapper ────────────────────────────────────────────
.table-wrap {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);

  :deep(.el-table) {
    background: var(--el-bg-color-overlay, #ffffff);
    color: var(--el-text-color-primary, #0f172a);
    border: none;

    // Header
    .el-table__header-wrapper th {
      background: var(--el-fill-color-light, #f8fafc) !important;
      color: var(--el-text-color-regular, #64748b) !important;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0);
      border-right: 1px solid var(--el-border-color-lighter, #e2e8f0);
      padding: 12px 0;
    }

    // Body rows
    .el-table__body tr td {
      background: transparent;
      border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0);
      border-right: 1px solid var(--el-border-color-lighter, #e2e8f0);
      transition: background 0.18s;
    }

    .el-table__body tr:hover td {
      background: rgba(59, 130, 246, 0.06) !important;
    }

    .el-table__fixed-right,
    .el-table__fixed {
      background: var(--el-bg-color-overlay, #ffffff);
    }

    .el-table__fixed-right .el-table__body tr td,
    .el-table__fixed .el-table__body tr td {
      background: var(--el-bg-color-overlay, #ffffff);
    }

    .el-table__fixed-right .el-table__body tr:hover td,
    .el-table__fixed .el-table__body tr:hover td {
      background: rgba(59, 130, 246, 0.06) !important;
    }
  }
}

:global(.dark) {
  .table-wrap {
    border-color: #1e293b;

    :deep(.el-table) {
      background: #0d1424;
      color: #e2e8f0;

      .el-table__header-wrapper th {
        background: #0d1424 !important;
        color: #94a3b8 !important;
        border-bottom-color: #1e293b;
        border-right-color: #1e293b;
      }

      .el-table__body tr td {
        border-bottom: 1px solid rgba(30, 41, 59, 0.7);
        border-right: 1px solid rgba(30, 41, 59, 0.5);
      }

      .el-table__body tr:hover td {
        background: rgba(59, 130, 246, 0.07) !important;
      }

      .el-table__fixed-right,
      .el-table__fixed {
        background: #0d1424;
      }

      .el-table__fixed-right .el-table__body tr td,
      .el-table__fixed .el-table__body tr td {
        background: #0d1424;
      }
    }
  }
}

// ─── Cell Atoms ───────────────────────────────────────────────
.receipt-badge {
  display: inline-flex;
  align-items: center;
  font-family: @mono;
  font-size: 12px;
  font-weight: 700;
  color: @blue;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 6px;
  padding: 3px 10px;
  letter-spacing: 0.04em;
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 0 12px rgba(59, 130, 246, 0.35);
  }
}

.mono-date {
  font-family: @mono;
  font-size: 12.5px;
  color: var(--el-text-color-regular, #64748b);
}

.cashier-badge {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: #8b5cf6;
  background: rgba(139, 92, 246, 0.12);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 6px;
  padding: 3px 9px;
}

.customer-name {
  font-weight: 500;
  color: var(--el-text-color-primary, #0f172a);
}

.empty-dash {
  color: var(--el-text-color-placeholder, #94a3b8);
}

// ─── Payment Pills ────────────────────────────────────────────
.payment-pill {
  display: inline-block;
  font-family: @mono;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 3px 10px;
  border-radius: 20px;
  border: 1px solid transparent;

  &--naqd {
    color: @green;
    background: rgba(16, 185, 129, 0.14);
    border-color: rgba(16, 185, 129, 0.4);
  }

  &--karta {
    color: @blue;
    background: rgba(59, 130, 246, 0.14);
    border-color: rgba(59, 130, 246, 0.4);
  }

  &--otkazma {
    color: @amber;
    background: rgba(245, 158, 11, 0.14);
    border-color: rgba(245, 158, 11, 0.4);
  }

  &--nasiya {
    color: @red;
    background: rgba(239, 68, 68, 0.14);
    border-color: rgba(239, 68, 68, 0.4);
  }
}

// ─── Table Numerics ───────────────────────────────────────────
.items-count {
  font-family: @mono;
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-regular, #64748b);
}

.total-amount {
  font-family: @mono;
  font-size: 14.5px;
  font-weight: 700;
  color: @green;
}

// ─── Pagination ───────────────────────────────────────────────
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

// ─── Receipt Detail Card ──────────────────────────────────────
.receipt-detail-card {
  font-family: @mono;
  background: var(--el-bg-color-overlay, #ffffff);
  padding: 20px;
  border-radius: 10px;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);

  :global(.dark) & {
    background: linear-gradient(135deg, #0d1424, #0a0f1e);
    border-color: #1e293b;
  }

  .receipt-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0);

    :global(.dark) & {
      border-bottom-color: #1e293b;
    }
  }

  .receipt-title {
    font-size: 15px;
    font-weight: 700;
    color: @green;
  }

  .receipt-meta {
    font-size: 12px;
    color: var(--el-text-color-regular, #64748b);
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 14px;
  }

  .receipt-items-wrap {
    border-top: 1px solid var(--el-border-color-lighter, #e2e8f0);
    border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0);
    padding: 10px 0;
    margin-bottom: 14px;

    :global(.dark) & {
      border-color: #1e293b;
    }
  }

  .receipt-items-header {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    font-weight: 700;
    color: var(--el-text-color-secondary, #94a3b8);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
  }

  .receipt-item-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    padding: 4px 0;
    border-bottom: 1px dashed var(--el-border-color-lighter, #e2e8f0);

    :global(.dark) & {
      border-bottom-color: rgba(30, 41, 59, 0.6);
    }

    &:last-child {
      border-bottom: none;
    }
  }

  .item-name {
    color: var(--el-text-color-primary, #0f172a);
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;

    :global(.dark) & {
      color: #e2e8f0;
    }
  }

  .item-calc {
    color: var(--el-text-color-regular, #64748b);
  }

  .item-total {
    color: @green;
  }

  .receipt-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
    font-weight: 700;
    padding-top: 6px;
    color: var(--el-text-color-primary, #0f172a);

    :global(.dark) & {
      color: #e2e8f0;
    }
  }

  .footer-total {
    font-size: 20px;
    color: @green;
  }
}
</style>
