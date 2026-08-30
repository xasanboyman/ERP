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
    <Dialog v-model="detailModalVisible" title="Chek Ma'lumotlari va Mahsulotlar" width="480px">
      <div v-if="selectedSale" class="receipt-detail-card">
        <div class="receipt-header">
          <span class="receipt-title">CHEK #{{ selectedSale.receipt_number }}</span>
          <span :class="['payment-pill', `payment-pill--${selectedSale.payment_method}`]">
            {{ selectedSale.payment_method }}
          </span>
        </div>

        <div class="receipt-meta">
          <div>Sana: {{ selectedSale.created_at }}</div>
          <div>Kassir: {{ selectedSale.cashier_name }}</div>
          <div v-if="selectedSale.customer_name">Mijoz: {{ selectedSale.customer_name }}</div>
        </div>

        <div class="receipt-items-wrap">
          <div class="receipt-items-header">
            <span>MAHSULOT</span>
            <span>SONI × NARXI = JAMI</span>
          </div>

          <div v-for="item in selectedSale.items" :key="item.id" class="receipt-item-row">
            <div class="flex flex-col">
              <span class="item-name">{{ item.product_name }}</span>
              <span v-if="item.unit_name" class="text-11px text-blue-500 font-bold"
                >Qadoq: {{ item.unit_name }}</span
              >
            </div>
            <span class="item-calc"
              >{{ item.quantity }} {{ item.unit_name || 'dona' }} × ${{ formatMoney(item.price) }} =
              <b class="item-total"
                >${{ formatMoney(item.total || item.quantity * item.price) }}</b
              ></span
            >
          </div>
        </div>

        <div class="receipt-footer">
          <span class="footer-label">JAMI SUMMA:</span>
          <span class="footer-total">${{ formatMoney(selectedSale.total_amount) }}</span>
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
import { getSalesListApi, SaleType } from '@/api/sales'

const loading = ref(false)
const salesList = ref<SaleType[]>([])
const total = ref(0)
const selectedSale = ref<SaleType | null>(null)
const detailModalVisible = ref(false)

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

const totalSalesAmount = computed(() => {
  return salesList.value.reduce((sum, s) => sum + (s.total_amount || 0), 0)
})

const fetchSalesData = async () => {
  loading.value = true
  try {
    const res = await getSalesListApi({
      pageIndex: pagination.pageIndex,
      pageSize: pagination.pageSize,
      search: searchQuery.search || undefined,
      payment_method: searchQuery.payment_method || undefined,
      cashier_name: searchQuery.cashier_name || undefined
    })
    if (res && res.data) {
      salesList.value = res.data.list || []
      total.value = res.data.total || 0
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

const openReceiptDetail = (row: SaleType) => {
  selectedSale.value = row
  detailModalVisible.value = true
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
