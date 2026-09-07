<script setup lang="ts">
import { ElRow, ElCol, ElSkeleton } from 'element-plus'
import { CountTo } from '@/components/CountTo'
import { ref } from 'vue'
import { Icon } from '@/components/Icon'
import { useI18n } from '@/hooks/web/useI18n'
import { getProductListApi } from '@/api/product'
import { getWorkerListApi } from '@/api/worker'
import { getSalaryListApi } from '@/api/salary'
import { getOutputListApi } from '@/api/staff_hr'
import { getSalesListApi } from '@/api/sales'

const { t } = useI18n()
const loading = ref(true)

const financialData = ref({
  grossRevenue: 0,
  cogs: 0,
  staffSalaries: 0,
  shortTermOutputs: 0,
  totalPayroll: 0,
  totalExpenses: 0,
  realNetProfit: 0,
  profitMargin: 0
})

const formatNum = (val: number) => {
  return parseFloat((val || 0).toFixed(2))
}

const loadData = async () => {
  loading.value = true
  try {
    const [prodRes, workerRes, salaryRes, outputRes, salesRes] = await Promise.allSettled([
      getProductListApi({ pageIndex: 1, pageSize: 500 }),
      getWorkerListApi({ pageIndex: 1, pageSize: 500 }),
      getSalaryListApi({ pageIndex: 1, pageSize: 500 }),
      getOutputListApi(),
      getSalesListApi({ pageIndex: 1, pageSize: 500 })
    ])

    const products =
      prodRes.status === 'fulfilled' && prodRes.value?.data?.list ? prodRes.value.data.list : []
    const workers =
      workerRes.status === 'fulfilled' && workerRes.value?.data?.list
        ? workerRes.value.data.list
        : []
    const salaries =
      salaryRes.status === 'fulfilled' && salaryRes.value?.data?.list
        ? salaryRes.value.data.list
        : []
    const outputs =
      outputRes.status === 'fulfilled' && outputRes.value?.data?.list
        ? outputRes.value.data.list
        : []
    const sales =
      salesRes.status === 'fulfilled' && salesRes.value?.data?.list ? salesRes.value.data.list : []

    // 1. Gross Revenue
    const totalSales = sales.reduce(
      (sum: number, s: any) => sum + (parseFloat(s.total_amount || s.total) || 0),
      0
    )
    const totalInventoryRetail = products.reduce(
      (sum: number, p: any) => sum + (p.price || 0) * (p.quantityInStock || 0),
      0
    )
    const totalInventoryCost = products.reduce(
      (sum: number, p: any) => sum + (p.cost || 0) * (p.quantityInStock || 0),
      0
    )

    const costRatio = totalInventoryRetail > 0 ? totalInventoryCost / totalInventoryRetail : 0
    const revenue = totalSales > 0 ? totalSales : totalInventoryRetail || 0
    const cogs = totalSales > 0 ? revenue * costRatio : totalInventoryCost || 0

    // 2. Staff Salaries (Faqat haqiqatda to'langan maoshlar)
    const paidSalaries = salaries
      .filter((s: any) => (s.status || '').toLowerCase() === 'paid')
      .reduce((sum: number, s: any) => sum + (parseFloat(s.netSalary) || 0), 0)

    // 3. Short-term Worker Outputs (Vyrabotka)
    const shortTerm = outputs.reduce((sum: number, o: any) => sum + (parseFloat(o.amount) || 0), 0)

    // 4. Totals & Real Net Profit
    const payroll = paidSalaries + shortTerm
    const expenses = cogs + payroll
    const netProfit = revenue - expenses
    const margin = revenue > 0 ? (netProfit / revenue) * 100 : 0

    financialData.value = {
      grossRevenue: revenue,
      cogs: cogs,
      staffSalaries: paidSalaries,
      shortTermOutputs: shortTerm,
      totalPayroll: payroll,
      totalExpenses: expenses,
      realNetProfit: netProfit,
      profitMargin: parseFloat(margin.toFixed(1))
    }
  } catch (e) {
    console.error('Executive Panel Data Load Error:', e)
  } finally {
    loading.value = false
  }
}

defineExpose({
  loadData
})

loadData()
</script>

<template>
  <ElRow :gutter="18" justify="space-between" class="financial-panels mb-20px">
    <!-- Card 1: Jami Savdo Tushumi -->
    <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
      <div class="panel-card card-blue">
        <ElSkeleton :loading="loading" animated :rows="2">
          <template #default>
            <div class="panel-body">
              <div class="panel-meta">
                <div class="panel-header-line">
                  <span class="panel-tag">{{ t('analysis.grossRevenue') }}</span>
                </div>
                <div class="panel-value text-blue">
                  $<CountTo
                    :start-val="0"
                    :end-val="formatNum(financialData.grossRevenue)"
                    :duration="2000"
                    :decimals="0"
                  />
                </div>
                <div class="panel-subtext">
                  <span class="badge-growth">{{ t('analysis.salesAndTurnover') }}</span>
                </div>
              </div>
              <div class="panel-icon-box bg-blue-glow">
                <Icon icon="ep:money" :size="24" class="text-white" />
              </div>
            </div>
            <div class="card-accent-bar bg-blue"></div>
          </template>
        </ElSkeleton>
      </div>
    </ElCol>

    <!-- Card 2: Mahsulotlar Tannarxi (COGS) -->
    <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
      <div class="panel-card card-amber">
        <ElSkeleton :loading="loading" animated :rows="2">
          <template #default>
            <div class="panel-body">
              <div class="panel-meta">
                <div class="panel-header-line">
                  <span class="panel-tag">{{ t('analysis.cogs') }}</span>
                </div>
                <div class="panel-value text-amber">
                  $<CountTo
                    :start-val="0"
                    :end-val="formatNum(financialData.cogs)"
                    :duration="2000"
                    :decimals="0"
                  />
                </div>
                <div class="panel-subtext">
                  <span class="text-muted">{{
                    t('analysis.revenueShare', {
                      percent: Math.round(
                        (financialData.cogs / (financialData.grossRevenue || 1)) * 100
                      )
                    })
                  }}</span>
                </div>
              </div>
              <div class="panel-icon-box bg-amber-glow">
                <Icon icon="ep:goods" :size="24" class="text-white" />
              </div>
            </div>
            <div class="card-accent-bar bg-amber"></div>
          </template>
        </ElSkeleton>
      </div>
    </ElCol>

    <!-- Card 3: Xodimlar va Ishchilar Maoshi -->
    <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
      <div class="panel-card card-purple">
        <ElSkeleton :loading="loading" animated :rows="2">
          <template #default>
            <div class="panel-body">
              <div class="panel-meta">
                <div class="panel-header-line">
                  <span class="panel-tag">{{ t('analysis.totalPayroll') }}</span>
                </div>
                <div class="panel-value text-purple">
                  $<CountTo
                    :start-val="0"
                    :end-val="formatNum(financialData.totalPayroll)"
                    :duration="2000"
                    :decimals="0"
                  />
                </div>
                <div class="panel-subtext">
                  <span class="text-muted"
                    >{{ t('analysis.permanentStaff') }}: ${{
                      Math.round(financialData.staffSalaries)
                        .toString()
                        .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
                    }}
                    | {{ t('analysis.shortTerm') }}: ${{
                      Math.round(financialData.shortTermOutputs)
                        .toString()
                        .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
                    }}</span
                  >
                </div>
              </div>
              <div class="panel-icon-box bg-purple-glow">
                <Icon icon="ep:user-filled" :size="24" class="text-white" />
              </div>
            </div>
            <div class="card-accent-bar bg-purple"></div>
          </template>
        </ElSkeleton>
      </div>
    </ElCol>

    <!-- Card 4: Haqiqiy Sof Foyda (REAL NET PROFIT) -->
    <ElCol :xl="6" :lg="6" :md="12" :sm="12" :xs="24" class="mb-14px">
      <div
        class="panel-card"
        :class="
          financialData.realNetProfit >= 0
            ? 'card-emerald highlight-profit'
            : 'card-rose highlight-loss'
        "
      >
        <ElSkeleton :loading="loading" animated :rows="2">
          <template #default>
            <div class="panel-body">
              <div class="panel-meta">
                <div class="panel-header-line flex items-center justify-between">
                  <span
                    class="panel-tag font-bold"
                    :class="
                      financialData.realNetProfit >= 0
                        ? 'text-emerald-600 dark:text-emerald-300'
                        : 'text-rose-600 dark:text-rose-400'
                    "
                  >
                    {{ t('analysis.realNetProfit') }}
                  </span>
                  <span :class="financialData.realNetProfit >= 0 ? 'profit-badge' : 'loss-badge'">
                    {{ financialData.profitMargin >= 0 ? '+' : ''
                    }}{{ financialData.profitMargin }}%
                  </span>
                </div>
                <div
                  class="panel-value font-extrabold"
                  :class="financialData.realNetProfit >= 0 ? 'text-emerald' : 'text-rose'"
                >
                  {{ financialData.realNetProfit < 0 ? '-' : '' }}$<CountTo
                    :start-val="0"
                    :end-val="formatNum(Math.abs(financialData.realNetProfit))"
                    :duration="2200"
                    :decimals="0"
                  />
                </div>
                <div class="panel-subtext">
                  <span
                    :class="
                      financialData.realNetProfit >= 0
                        ? 'text-emerald-600 dark:text-emerald-400 font-semibold'
                        : 'text-rose-600 dark:text-rose-400 font-semibold'
                    "
                  >
                    {{ t('analysis.afterSalaries') }}
                  </span>
                </div>
              </div>
              <div
                class="panel-icon-box"
                :class="
                  financialData.realNetProfit >= 0
                    ? 'bg-emerald-glow text-emerald-700 pulse-emerald'
                    : 'bg-rose-glow text-rose-700 pulse-rose'
                "
              >
                <Icon icon="ep:wallet-filled" :size="24" class="text-white" />
              </div>
            </div>
            <div
              class="card-accent-bar"
              :class="financialData.realNetProfit >= 0 ? 'bg-emerald' : 'bg-rose'"
            ></div>
          </template>
        </ElSkeleton>
      </div>
    </ElCol>
  </ElRow>
</template>

<style lang="less" scoped>
.financial-panels {
  .panel-card {
    background: var(--el-bg-color-overlay, #ffffff);
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 14px 30px rgba(0, 0, 0, 0.09);
    }

    &.card-blue {
      border-color: rgba(59, 130, 246, 0.25);
    }
    &.card-amber {
      border-color: rgba(245, 158, 11, 0.25);
    }
    &.card-purple {
      border-color: rgba(139, 92, 246, 0.25);
    }
    &.card-rose {
      border-color: rgba(244, 63, 94, 0.35);
    }
    &.highlight-profit {
      background: linear-gradient(
        135deg,
        rgba(16, 185, 129, 0.08) 0%,
        rgba(5, 150, 105, 0.16) 100%
      );
      border: 1px solid rgba(16, 185, 129, 0.45);
      box-shadow: 0 6px 24px rgba(16, 185, 129, 0.16);

      &:hover {
        box-shadow: 0 16px 36px rgba(16, 185, 129, 0.26);
      }
    }
    &.highlight-loss {
      background: linear-gradient(135deg, rgba(244, 63, 94, 0.08) 0%, rgba(225, 29, 72, 0.16) 100%);
      border: 1px solid rgba(244, 63, 94, 0.45);
      box-shadow: 0 6px 24px rgba(244, 63, 94, 0.16);

      &:hover {
        box-shadow: 0 16px 36px rgba(244, 63, 94, 0.26);
      }
    }
  }

  .card-accent-bar {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    opacity: 0.85;

    &.bg-blue {
      background: linear-gradient(90deg, #3b82f6, #60a5fa);
    }
    &.bg-amber {
      background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }
    &.bg-purple {
      background: linear-gradient(90deg, #8b5cf6, #c084fc);
    }
    &.bg-emerald {
      background: linear-gradient(90deg, #10b981, #34d399);
    }
    &.bg-rose {
      background: linear-gradient(90deg, #f43f5e, #fb7185);
    }
  }

  .panel-body {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }

  .panel-meta {
    flex: 1;
  }

  .panel-header-line {
    margin-bottom: 4px;
  }

  .panel-tag {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--el-text-color-secondary, #64748b);
  }

  .panel-value {
    font-size: 25px;
    font-weight: 800;
    margin: 4px 0 6px 0;
    color: var(--el-text-color-primary, #0f172a);
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
    &.text-rose {
      color: #e11d48;
    }
  }

  .panel-subtext {
    font-size: 11px;
    font-weight: 500;
  }

  .text-muted {
    color: var(--el-text-color-secondary, #94a3b8);
  }

  .badge-growth {
    color: #2563eb;
    background: rgba(37, 99, 235, 0.1);
    padding: 2px 7px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 11px;
  }

  .profit-badge {
    font-size: 11px;
    font-weight: 800;
    color: #ffffff;
    background: #10b981;
    padding: 2px 8px;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(16, 185, 129, 0.4);
  }

  .loss-badge {
    font-size: 11px;
    font-weight: 800;
    color: #ffffff;
    background: #f43f5e;
    padding: 2px 8px;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(244, 63, 94, 0.4);
  }

  .panel-icon-box {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-shrink: 0;

    &.bg-blue-glow {
      background: linear-gradient(135deg, #3b82f6, #1d4ed8);
      box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
    }
    &.bg-amber-glow {
      background: linear-gradient(135deg, #f59e0b, #d97706);
      box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4);
    }
    &.bg-purple-glow {
      background: linear-gradient(135deg, #8b5cf6, #6d28d9);
      box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
    }
    &.bg-emerald-glow {
      background: linear-gradient(135deg, #10b981, #059669);
      box-shadow: 0 6px 18px rgba(16, 185, 129, 0.45);
    }
    &.bg-rose-glow {
      background: linear-gradient(135deg, #f43f5e, #be123c);
      box-shadow: 0 6px 18px rgba(244, 63, 94, 0.45);
    }
  }

  .pulse-emerald,
  .pulse-rose {
    animation: pulseGlow 2.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
}

:global(.dark) {
  .financial-panels {
    .panel-card {
      background: #0f172a;
      border-color: #1e293b;

      .panel-tag {
        color: #94a3b8;
      }

      .panel-value {
        color: #f8fafc;
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
        &.text-rose {
          color: #fb7185;
        }
      }

      &.card-blue {
        border-color: rgba(59, 130, 246, 0.35);
      }
      &.card-amber {
        border-color: rgba(245, 158, 11, 0.35);
      }
      &.card-purple {
        border-color: rgba(139, 92, 246, 0.35);
      }
      &.card-rose {
        border-color: rgba(244, 63, 94, 0.45);
      }

      &.highlight-profit {
        background: linear-gradient(
          135deg,
          rgba(16, 185, 129, 0.15) 0%,
          rgba(5, 150, 105, 0.28) 100%
        );
        border-color: rgba(16, 185, 129, 0.6);
        box-shadow: 0 6px 28px rgba(16, 185, 129, 0.25);
      }

      &.highlight-loss {
        background: linear-gradient(
          135deg,
          rgba(244, 63, 94, 0.18) 0%,
          rgba(225, 29, 72, 0.32) 100%
        );
        border-color: rgba(244, 63, 94, 0.65);
        box-shadow: 0 6px 28px rgba(244, 63, 94, 0.3);
      }
    }
  }
}

@keyframes pulseGlow {
  0%,
  100% {
    transform: scale(1);
    filter: brightness(1);
  }
  50% {
    transform: scale(1.06);
    filter: brightness(1.15);
  }
}
</style>
