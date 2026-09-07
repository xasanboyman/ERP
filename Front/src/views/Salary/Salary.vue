<template>
  <div class="salary-page">
    <ContentWrap>
      <!-- Filter and Bulk Actions Bar -->
      <div class="toolbar flex flex-wrap justify-between items-center gap-12px mb-16px">
        <el-form
          :inline="true"
          :model="searchQuery"
          class="flex-1 flex flex-wrap items-center gap-12px !mb-0"
        >
          <el-form-item :label="t('erp.reportMonth')" class="!mr-0">
            <el-date-picker
              v-model="selectedMonthStr"
              type="month"
              format="YYYY-MM"
              value-format="YYYY-MM"
              :placeholder="t('erp.oyniTanlang')"
              style="width: 140px"
              :clearable="false"
            />
          </el-form-item>
          <el-form-item :label="t('erp.workerFullName')" class="!mr-0">
            <el-input
              v-model="searchQuery.name"
              :placeholder="t('erp.workerNameSearch')"
              clearable
              style="width: 160px"
              prefix-icon="ep:search"
            />
          </el-form-item>
          <el-form-item :label="t('erp.paymentStatus')" class="!mr-0">
            <el-select
              v-model="searchQuery.status"
              :placeholder="t('erp.selectStatus')"
              clearable
              style="width: 150px"
            >
              <el-option :label="t('erp.paid')" value="paid">
                <span class="flex items-center gap-6px">
                  <Icon icon="ep:circle-check" class="text-emerald-500" />
                  <span>{{ t('erp.paid') }}</span>
                </span>
              </el-option>
              <el-option :label="t('erp.pending')" value="unpaid">
                <span class="flex items-center gap-6px">
                  <Icon icon="ep:timer" class="text-amber-500" />
                  <span>{{ t('erp.pending') }}</span>
                </span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item class="!mr-0">
            <el-button type="primary" @click="handleSearch">
              <Icon icon="ep:search" class="mr-4px" />{{ t('common.search') }}</el-button
            >
            <el-button @click="resetSearch">{{ t('common.reset') }}</el-button>
          </el-form-item>
        </el-form>
        <div class="flex items-center gap-8px">
          <el-button type="primary" plain @click="handleExportExcel">
            <Icon icon="ep:download" class="mr-4px" />{{ t('erp.exportExcel') }}</el-button
          >
          <el-button type="success" class="action-btn-success" @click="openPayoutDialog">
            <Icon icon="ep:wallet" class="mr-4px" />{{ t('erp.distributePayroll') }}</el-button
          >
        </div>
      </div>

      <!-- Main Salary Table -->
      <el-table
        v-loading="loading"
        :data="filteredWorkerRows"
        style="width: 100%"
        border
        class="custom-salary-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="45" align="center" />
        <el-table-column prop="name" :label="t('erp.workerFullName')" min-width="190">
          <template #default="scope">
            <div class="cursor-pointer py-2px" @click="openWorkerDetails(scope.row)">
              <div
                class="font-bold text-[var(--el-text-color-primary)] hover:text-blue-500 transition-colors whitespace-nowrap"
              >
                {{ scope.row.name }}
              </div>
              <div
                class="text-[var(--el-text-color-secondary)] opacity-80 mt-1px text-[12px] whitespace-nowrap flex items-center gap-4px"
              >
                <span>{{ scope.row.role || 'Oddiy xodim' }}</span>
                <span
                  v-if="scope.row.departmentName && scope.row.departmentName !== '—'"
                  class="text-gray-400 opacity-60"
                  >•</span
                >
                <span
                  v-if="scope.row.departmentName && scope.row.departmentName !== '—'"
                  class="text-[var(--el-text-color-regular)] font-medium"
                >
                  {{ scope.row.departmentName }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="currentBaseSalary"
          :label="t('erp.baseDollar')"
          min-width="135"
          align="right"
        >
          <template #default="scope">
            <span class="font-mono font-bold text-[var(--el-text-color-primary)] whitespace-nowrap">
              ${{ formatMoney(scope?.row?.currentBaseSalary) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          :label="`${t('erp.prevMonth')} (${prevMonthStr})`"
          min-width="155"
          align="right"
        >
          <template #default="scope">
            <div v-if="scope.row.prevMonthPaid" class="font-mono whitespace-nowrap text-right">
              <div class="text-emerald-600 dark:text-emerald-400 font-bold"
                >${{ formatMoney(scope.row.prevMonthPaid.netSalary) }}</div
              >
              <div
                class="text-emerald-600 dark:text-emerald-400 text-[11px] font-medium leading-tight mt-1px inline-flex items-center gap-3px"
              >
                <Icon icon="ep:check" class="text-11px" />
                <span>{{ t('erp.paid') }}</span>
              </div>
            </div>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column
          :label="`${t('erp.selectedMonth')} (${selectedMonthStr})`"
          min-width="165"
          align="right"
        >
          <template #default="scope">
            <span class="font-mono text-[var(--el-text-color-primary)] font-bold whitespace-nowrap">
              ${{ formatMoney(scope.row.selectedMonthCalc.baseSalary) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="t('erp.bonusDollar')" min-width="110" align="right">
          <template #default="scope">
            <span
              v-if="scope.row.selectedMonthCalc.bonus > 0"
              class="font-mono text-emerald-600 dark:text-emerald-400 font-bold whitespace-nowrap"
            >
              +${{ formatMoney(scope.row.selectedMonthCalc.bonus) }}
            </span>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('erp.penaltyDollar')" min-width="130" align="right">
          <template #default="scope">
            <span
              v-if="scope.row.selectedMonthCalc.penalty > 0"
              class="font-mono text-rose-600 dark:text-rose-400 font-bold whitespace-nowrap"
            >
              -${{ formatMoney(scope.row.selectedMonthCalc.penalty) }}
            </span>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('erp.netSalaryDollar')" min-width="145" align="right">
          <template #default="scope">
            <span
              class="font-mono font-black text-emerald-600 dark:text-emerald-400 whitespace-nowrap"
            >
              ${{ formatMoney(scope.row.selectedMonthCalc.netSalary) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="t('erp.holati')" min-width="115" align="center">
          <template #default="scope">
            <el-tag
              :type="scope.row.isSelectedMonthPaid ? 'success' : 'warning'"
              size="small"
              effect="dark"
              round
              class="font-bold whitespace-nowrap"
            >
              {{ scope.row.isSelectedMonthPaid ? t('erp.paid') : t('erp.pending') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          :label="`${t('erp.nextMonth')} (${nextMonthStr})`"
          min-width="165"
          align="right"
        >
          <template #default="scope">
            <div v-if="scope.row.nextMonthPaid" class="font-mono whitespace-nowrap text-right">
              <div class="text-emerald-600 dark:text-emerald-400 font-bold"
                >${{ formatMoney(scope.row.nextMonthPaid.netSalary) }}</div
              >
              <div
                class="text-emerald-600 dark:text-emerald-400 font-medium text-[11px] leading-tight mt-1px inline-flex items-center gap-3px"
              >
                <Icon icon="ep:check" class="text-11px" />
                <span>{{ t('erp.inAdvance') }}</span>
              </div>
            </div>
            <span v-else class="text-gray-400 font-normal whitespace-nowrap text-[12px]">{{
              t('erp.kutilmoqda')
            }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('erp.amallar')" width="125" fixed="right" align="center">
          <template #default="scope">
            <div class="flex items-center justify-center gap-4px">
              <el-button
                size="small"
                type="primary"
                link
                class="!font-bold !px-4px"
                @click="openWorkerDetails(scope.row)"
                >{{ t('common.detail') }}</el-button
              >
              <el-button
                v-if="!scope.row.isSelectedMonthPaid"
                size="small"
                type="success"
                link
                class="!font-bold !px-4px"
                @click="quickPaySingleWorker(scope.row)"
              >
                To'lash
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- Worker Details & Full Payment History Dialog -->
      <ResizeDialog
        v-model="detailsDialogVisible"
        :title="
          selectedWorker
            ? `${selectedWorker.name} — ${t('erp.salaryPaymentHistory')}`
            : t('erp.workerSalaryHistory')
        "
        :width="detailsDialogWidth"
        :height="detailsDialogHeight"
        :min-resize-width="750"
        :min-resize-height="450"
      >
        <div v-if="selectedWorker" class="worker-details-content flex flex-col h-full">
          <!-- Worker Info Banner -->
          <div
            class="flex flex-wrap justify-between items-center p-14px mb-16px rounded-8px bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
          >
            <div>
              <div class="font-bold text-[1.15em] text-[var(--el-text-color-primary)] mb-2px">{{
                selectedWorker.name
              }}</div>
              <div class="text-[0.9em] text-gray-500 flex items-center gap-8px">
                <span
                  class="bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 px-8px py-2px rounded font-medium"
                  >{{ selectedWorker.role }}</span
                >
                <span>{{ t('erp.department') }}: {{ selectedWorker.departmentName || '—' }}</span>
              </div>
            </div>
            <div class="flex items-center gap-20px font-mono text-[1em]">
              <div
                >{{ t('erp.baseSalaryLabel') }}:
                <b class="text-emerald-600 dark:text-emerald-400 font-bold"
                  >${{ formatMoney(selectedWorker.baseSalary) }}</b
                ></div
              >
              <div
                >{{ t('erp.totalPaid') }}:
                <b class="text-emerald-600 dark:text-emerald-400 font-bold"
                  >${{ formatMoney(selectedWorkerTotalPaid) }}</b
                ></div
              >
              <div
                >{{ t('erp.totalBonus') }}:
                <b class="text-blue-600 dark:text-blue-400 font-bold"
                  >+${{ formatMoney(selectedWorkerTotalBonus) }}</b
                ></div
              >
              <div
                >{{ t('erp.totalDeductions') }}:
                <b class="text-rose-600 dark:text-rose-400 font-bold"
                  >-${{ formatMoney(selectedWorkerTotalDeduction) }}</b
                ></div
              >
            </div>
          </div>

          <el-tabs v-model="detailsActiveTab" class="flex-1 flex flex-col overflow-hidden">
            <!-- All Payments History Tab -->
            <el-tab-pane
              :label="`${t('erp.allPaymentsHistory')} (${selectedWorkerSalaries.length} ta)`"
              name="salaries"
              class="h-full flex flex-col"
            >
              <div
                v-if="selectedWorkerSalaries.length === 0"
                class="text-center py-40px text-gray-400"
              >
                {{ t('erp.noPaymentsYet') }}
              </div>

              <el-table
                v-else
                :data="selectedWorkerSalaries"
                border
                style="width: 100%"
                height="460"
                class="flex-1"
              >
                <el-table-column prop="id" :label="t('erp.transactionId')" width="120">
                  <template #default="{ row }">
                    <span class="font-mono text-blue-600 dark:text-blue-400 font-bold">{{
                      row.id
                    }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="payDate" :label="t('erp.paymentDate')" width="120">
                  <template #default="{ row }">
                    <span class="font-mono text-[var(--el-text-color-regular)]">{{
                      row.payDate
                    }}</span>
                  </template>
                </el-table-column>
                <el-table-column :label="t('erp.reportMonth')" width="130" align="center">
                  <template #default="{ row }">
                    <el-tag size="small" type="primary" effect="light" class="font-mono font-bold">
                      {{ getSalaryPeriodMonth(row) || 'Joriy oy' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="remark"
                  :label="t('erp.remarkInfo')"
                  min-width="190"
                  show-overflow-tooltip
                >
                  <template #default="{ row }">
                    <span>{{ row.remark || '—' }}</span>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="baseSalary"
                  :label="t('erp.baseDollar')"
                  width="120"
                  align="right"
                >
                  <template #default="{ row }">
                    <span class="font-mono font-medium whitespace-nowrap"
                      >${{ formatMoney(row.baseSalary) }}</span
                    >
                  </template>
                </el-table-column>
                <el-table-column
                  prop="allowance"
                  :label="t('erp.bonusDollar')"
                  width="120"
                  align="right"
                >
                  <template #default="{ row }">
                    <span
                      v-if="row.allowance > 0"
                      class="font-mono text-emerald-600 dark:text-emerald-400 font-bold whitespace-nowrap"
                      >+${{ formatMoney(row.allowance) }}</span
                    >
                    <span v-else class="text-gray-400">—</span>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="deduction"
                  :label="t('erp.penaltyDollar')"
                  width="120"
                  align="right"
                >
                  <template #default="{ row }">
                    <span
                      v-if="row.deduction > 0"
                      class="font-mono text-rose-600 dark:text-rose-400 font-bold whitespace-nowrap"
                      >-${{ formatMoney(row.deduction) }}</span
                    >
                    <span v-else class="text-gray-400">—</span>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="netSalary"
                  :label="t('erp.paidAmountDollar')"
                  width="150"
                  align="right"
                >
                  <template #default="{ row }">
                    <span
                      class="font-mono font-black text-emerald-600 dark:text-emerald-400 whitespace-nowrap"
                    >
                      ${{ formatMoney(row.netSalary) }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="status" :label="t('erp.holati')" width="110" align="center">
                  <template #default>
                    <el-tag type="success" effect="plain" class="font-bold">{{
                      t('erp.tolangan')
                    }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="t('common.delete')" width="85" align="center">
                  <template #default="{ row }">
                    <el-button type="danger" link @click="deletePaymentRecord(row)">
                      <Icon icon="ep:delete" :size="16" />
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <!-- Adjustments Log Tab -->
            <el-tab-pane
              :label="`${t('erp.adjustmentsBonusPenalty')} (${selectedWorkerAdjustments.length} ta)`"
              name="adjustments"
              class="h-full flex flex-col"
            >
              <div
                v-if="selectedWorkerAdjustments.length === 0"
                class="text-center py-40px text-gray-400"
              >
                {{ t('erp.noAdjustmentsYet') }}
              </div>

              <el-table
                v-else
                :data="selectedWorkerAdjustments"
                border
                style="width: 100%"
                height="460"
                class="flex-1"
              >
                <el-table-column
                  prop="period_month"
                  :label="t('erp.reportMonth')"
                  width="130"
                  align="center"
                >
                  <template #default="{ row }">
                    <span class="font-mono">{{ row.period_month || '—' }}</span>
                  </template>
                </el-table-column>
                <el-table-column :label="t('erp.docType')" width="140">
                  <template #default="{ row }">
                    <el-tag
                      :type="row.document_type === 'bonus' ? 'success' : 'danger'"
                      effect="light"
                      class="font-bold"
                    >
                      {{
                        row.document_type === 'bonus'
                          ? 'Mukofot'
                          : row.document_type === 'advance'
                            ? 'Avans'
                            : 'Jarima'
                      }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="amount" label="Miqdori ($)" width="150" align="right">
                  <template #default="{ row }">
                    <span
                      class="font-mono font-bold whitespace-nowrap"
                      :class="
                        row.document_type === 'bonus'
                          ? 'text-emerald-600 dark:text-emerald-400'
                          : 'text-rose-600 dark:text-rose-400'
                      "
                    >
                      {{ row.document_type === 'bonus' ? '+' : '-' }}${{ formatMoney(row.amount) }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="description"
                  :label="t('erp.reasonRemark')"
                  min-width="220"
                  show-overflow-tooltip
                >
                  <template #default="{ row }">
                    <span>{{ row.description || '—' }}</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </div>

        <template #footer>
          <div class="flex justify-end">
            <el-button @click="detailsDialogVisible = false">{{ t('common.close') }}</el-button>
          </div>
        </template>
      </ResizeDialog>

      <!-- Bulk Payout Dialog -->
      <ResizeDialog
        v-model="payoutDialogVisible"
        title="Oylik Ish Haqlarini Tarqatish (Payroll)"
        :width="dialogInitWidth"
        :height="dialogInitHeight"
        :min-resize-width="750"
        :min-resize-height="450"
      >
        <div v-loading="payoutLoading" class="payout-dialog-content flex flex-col h-full">
          <!-- Top Month Selector -->
          <div
            class="month-selector-bar flex flex-wrap justify-between items-center gap-12px mb-16px p-12px rounded-8px bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700"
          >
            <div class="flex items-center gap-10px">
              <span class="font-bold text-14px">Qaysi oy uchun hisoblanmoqda:</span>
              <el-date-picker
                v-model="selectedPayoutMonth"
                type="month"
                :placeholder="t('erp.oyniTanlang')"
                value-format="YYYY-MM"
                format="YYYY-MM"
                :clearable="false"
                class="!w-150px"
                @change="handlePayoutMonthChange"
              />
            </div>
            <div class="flex items-center gap-10px">
              <el-input
                v-model="workerFilterText"
                placeholder="Xodimlarni saralash..."
                clearable
                prefix-icon="ep:search"
                style="width: 220px"
              />
            </div>
          </div>

          <!-- Payout Table -->
          <div class="payout-table-wrapper flex-1 overflow-auto mb-16px">
            <el-table :data="filteredPayoutWorkers" border style="width: 100%" height="360">
              <el-table-column width="50" align="center">
                <template #header>
                  <el-checkbox
                    v-model="selectAllWorkers"
                    :indeterminate="isIndeterminate"
                    :disabled="payableWorkersCount === 0"
                    @change="handleSelectAllChange"
                  />
                </template>
                <template #default="scope">
                  <el-checkbox
                    v-model="scope.row.selected"
                    :disabled="scope.row.isAlreadyPaidForMonth"
                  />
                </template>
              </el-table-column>

              <el-table-column :label="t('erp.workerFullName')" min-width="180">
                <template #default="scope">
                  <div class="font-bold text-14px text-[var(--el-text-color-primary)]">{{
                    scope.row.name
                  }}</div>
                  <div class="text-12px text-gray-500">{{ scope.row.role }}</div>
                </template>
              </el-table-column>

              <el-table-column :label="t('erp.holati')" width="130" align="center">
                <template #default="scope">
                  <el-tag
                    v-if="scope.row.isAlreadyPaidForMonth"
                    type="success"
                    effect="dark"
                    class="font-bold text-12px inline-flex items-center gap-4px"
                  >
                    <Icon icon="ep:check" class="text-12px" />
                    <span>{{ t('erp.paid') }}</span>
                  </el-tag>
                  <el-tag v-else type="warning" effect="plain" class="font-bold text-12px">
                    To'lanmagan
                  </el-tag>
                </template>
              </el-table-column>

              <el-table-column label="Asosiy Oylik" width="140" align="right">
                <template #default="scope">
                  <span class="font-mono text-14px font-bold whitespace-nowrap"
                    >${{ formatMoney(scope.row.baseSalary) }}</span
                  >
                </template>
              </el-table-column>

              <el-table-column label="Mukofot (+)" width="140" align="right">
                <template #default="scope">
                  <span
                    v-if="scope.row.totalBonus > 0"
                    class="font-mono text-14px font-bold text-emerald-600 dark:text-emerald-400 whitespace-nowrap"
                  >
                    +${{ formatMoney(scope.row.totalBonus) }}
                  </span>
                  <span v-else class="text-13px text-gray-400">—</span>
                </template>
              </el-table-column>

              <el-table-column :label="t('erp.deductionMinus')" width="140" align="right">
                <template #default="scope">
                  <span
                    v-if="scope.row.totalPenalty > 0"
                    class="font-mono text-14px font-bold text-rose-600 dark:text-rose-400 whitespace-nowrap"
                  >
                    -${{ formatMoney(scope.row.totalPenalty) }}
                  </span>
                  <span v-else class="text-13px text-gray-400">—</span>
                </template>
              </el-table-column>

              <el-table-column label="Sof To'lov ($)" width="160" align="right">
                <template #default="scope">
                  <span
                    class="font-mono font-black text-emerald-600 dark:text-emerald-400 text-15px whitespace-nowrap"
                  >
                    ${{ formatMoney(scope.row.netSalary) }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- Total Calculation Strip -->
          <div
            class="payout-summary-card mb-12px p-12px rounded-8px bg-slate-100 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700"
          >
            <div class="flex flex-wrap items-center justify-between gap-12px">
              <div>
                <span class="text-12px text-gray-500">Tanlangan xodimlar: </span>
                <span class="font-bold text-blue-600">{{ selectedWorkersList.length }} nafar</span>
              </div>
              <div class="text-right">
                <span class="text-12px text-gray-500 mr-8px"
                  >JAMI TO'LOV ({{ selectedPayoutMonth }}):</span
                >
                <span class="font-mono font-black text-18px text-emerald-600 dark:text-emerald-400"
                  >${{ formatMoney(selectedTotalNet) }}</span
                >
              </div>
            </div>
          </div>

          <!-- Remark input -->
          <div class="remark-box mb-10px">
            <el-input
              v-model="payoutRemark"
              type="textarea"
              :rows="2"
              :placeholder="`${selectedPayoutMonth} oyi uchun oylik maosh to'lovi`"
            />
          </div>
        </div>

        <template #footer>
          <span class="dialog-footer flex justify-between items-center">
            <div class="text-12px text-gray-500 dark:text-gray-400">
              * Korrektirovkalar avtomatik ravishda {{ selectedPayoutMonth }} oyi maoshiga qo'shildi
              va ushlab qolindi.
            </div>
            <div class="flex gap-10px">
              <el-button @click="payoutDialogVisible = false">{{ t('common.cancel') }}</el-button>
              <el-button
                type="success"
                class="action-btn-success font-bold"
                :loading="submitLoading"
                :disabled="selectedWorkersList.length === 0"
                @click="submitPayout"
              >
                <Icon icon="ep:wallet" class="mr-4px" /> {{ selectedWorkersList.length }} ta xodimga
                tarqatish (${{ formatMoney(selectedTotalNet) }})
              </el-button>
            </div>
          </span>
        </template>
      </ResizeDialog>
    </ContentWrap>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
import { ref, reactive, computed, onMounted } from 'vue'
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
  ElCheckbox,
  ElDatePicker,
  ElDialog,
  ElTabs,
  ElTabPane
} from 'element-plus'
import { ContentWrap } from '@/components/ContentWrap'
import { ResizeDialog } from '@/components/Dialog'
import { Icon } from '@/components/Icon'
import { getSalaryListApi, deleteSalaryApi, bulkSalaryPayoutApi } from '@/api/salary'
import type { SalaryType } from '@/api/salary'
import { getWorkerListApi } from '@/api/worker'
import { getAdjustmentListApi } from '@/api/staff_hr'
import { formatMoney } from '@/utils'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'
import { exportToExcel } from '@/utils/exportReport'

const dialogInitWidth =
  typeof window !== 'undefined' ? Math.min(window.innerWidth * 0.92, 1150) : 1150
const dialogInitHeight =
  typeof window !== 'undefined' ? Math.min(window.innerHeight * 0.88, 720) : 720

const detailsDialogWidth =
  typeof window !== 'undefined' ? Math.min(window.innerWidth * 0.94, 1260) : 1260
const detailsDialogHeight =
  typeof window !== 'undefined' ? Math.min(window.innerHeight * 0.88, 760) : 760

// Helper for Months
const getCurrentMonthString = () => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

const getPrevMonthString = (monthStr: string) => {
  if (!monthStr) return ''
  const [y, m] = monthStr.split('-').map(Number)
  const d = new Date(y, m - 1 - 1, 1)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

const getNextMonthString = (monthStr: string) => {
  if (!monthStr) return ''
  const [y, m] = monthStr.split('-').map(Number)
  const d = new Date(y, m - 1 + 1, 1)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

const getSalaryPeriodMonth = (s: any): string => {
  if (!s) return ''
  if (s.period_month) return s.period_month
  const rem = s.remark || ''
  const match = rem.match(/\b(20\d{2}-\d{2})\b/)
  if (match) return match[1]
  if (s.payDate && s.payDate.length >= 7) return s.payDate.slice(0, 7)
  return ''
}

const isSalaryForMonth = (s: any, targetMonth: string): boolean => {
  if (!targetMonth || !s) return false
  return getSalaryPeriodMonth(s) === targetMonth && s.status === 'paid'
}

const selectedMonthStr = ref(getCurrentMonthString())
const prevMonthStr = computed(() => getPrevMonthString(selectedMonthStr.value))
const nextMonthStr = computed(() => getNextMonthString(selectedMonthStr.value))

const loading = ref(false)
const rawWorkers = ref<any[]>([])
const rawSalaries = ref<SalaryType[]>([])
const rawAdjustments = ref<any[]>([])
const selectedIds = ref<string[]>([])

const searchQuery = reactive({
  name: '',
  status: ''
})

// Load All Data & Rebuild Clean Employee View
const loadData = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    const [workersRes, salariesRes, adjsRes] = await Promise.all([
      getWorkerListApi({ pageIndex: 1, pageSize: 200 }),
      getSalaryListApi({ pageIndex: 1, pageSize: 1000 }),
      getAdjustmentListApi()
    ])

    rawWorkers.value = (workersRes?.data as any)?.list || workersRes?.data || []
    rawSalaries.value = (salariesRes?.data as any)?.list || salariesRes?.data || []
    rawAdjustments.value = (adjsRes?.data as any)?.list || adjsRes?.data || []
  } catch (err) {
    console.error('Failed to load salary data:', err)
  } finally {
    if (!silent) loading.value = false
  }
}

const handleSearch = () => {
  // Triggers reactive filter
}

const resetSearch = () => {
  searchQuery.name = ''
  searchQuery.status = ''
  selectedMonthStr.value = getCurrentMonthString()
}

const handleSelectionChange = (selection: any[]) => {
  selectedIds.value = selection.map((item) => item.id)
}

// Build Unique Employee Rows
const workerRows = computed(() => {
  const targetMonth = selectedMonthStr.value
  const pMonth = prevMonthStr.value
  const nMonth = nextMonthStr.value

  return rawWorkers.value.map((w) => {
    const wId = String(w.id)
    const currentBase = Number(w.baseSalary || 0)

    // All salary payment logs for this worker
    const workerSalaries = rawSalaries.value.filter((s) => String(s.workerId) === wId)

    // Prev Month Paid Record
    const prevMonthPaid = workerSalaries.find((s) => isSalaryForMonth(s, pMonth))

    // Selected Month Paid Record
    const selectedMonthPaid = workerSalaries.find((s) => isSalaryForMonth(s, targetMonth))
    const isSelectedMonthPaid = !!selectedMonthPaid

    // Next Month Paid Record
    const nextMonthPaid = workerSalaries.find((s) => isSalaryForMonth(s, nMonth))
    const isNextMonthPaid = !!nextMonthPaid

    // Adjustments for Selected Month
    const activeAdjs = rawAdjustments.value.filter((a: any) => {
      if (String(a.workerId) !== wId) return false
      if (!a.period_month || a.period_month === targetMonth) return true
      // Carry over from already-paid past months
      if (
        a.period_month < targetMonth &&
        workerSalaries.some((s) => isSalaryForMonth(s, a.period_month))
      ) {
        return true
      }
      return false
    })

    const bonusSum = activeAdjs
      .filter((a) =>
        ['bonus', 'mukofot', 'reward'].includes(String(a.document_type || '').toLowerCase())
      )
      .reduce((sum, a) => sum + Number(a.amount || 0), 0)

    const penaltySum = activeAdjs
      .filter(
        (a) => !['bonus', 'mukofot', 'reward'].includes(String(a.document_type || '').toLowerCase())
      )
      .reduce((sum, a) => sum + Number(a.amount || 0), 0)

    const calculatedNet = Math.max(0, currentBase + bonusSum - penaltySum)

    const monthBase = selectedMonthPaid ? Number(selectedMonthPaid.baseSalary || 0) : currentBase
    const monthBonus = selectedMonthPaid ? Number(selectedMonthPaid.allowance || 0) : bonusSum
    const monthPenalty = selectedMonthPaid ? Number(selectedMonthPaid.deduction || 0) : penaltySum
    const netSalary = selectedMonthPaid ? Number(selectedMonthPaid.netSalary || 0) : calculatedNet

    return {
      id: wId,
      name: w.name || 'Xodim',
      role: w.role || 'Oddiy xodim',
      departmentName: w.departmentName || '—',
      departmentId: w.departmentId,
      currentBaseSalary: currentBase,
      prevMonthPaid,
      selectedMonthPaid,
      isSelectedMonthPaid,
      nextMonthPaid,
      isNextMonthPaid,
      selectedMonthCalc: {
        baseSalary: monthBase,
        bonus: monthBonus,
        penalty: monthPenalty,
        netSalary
      },
      historyCount: workerSalaries.length
    }
  })
})

// Filtered Employees for Main Table
const filteredWorkerRows = computed(() => {
  const kw = searchQuery.name.trim().toLowerCase()
  const st = searchQuery.status

  return workerRows.value.filter((w) => {
    if (kw) {
      const matchName = w.name.toLowerCase().includes(kw)
      const matchRole = w.role.toLowerCase().includes(kw)
      const matchDept = (w.departmentName || '').toLowerCase().includes(kw)
      if (!matchName && !matchRole && !matchDept) return false
    }
    if (st === 'paid' && !w.isSelectedMonthPaid) return false
    if (st === 'unpaid' && w.isSelectedMonthPaid) return false
    return true
  })
})

// ---------------- Details Dialog Logic ----------------
const detailsDialogVisible = ref(false)
const detailsActiveTab = ref('salaries')
const selectedWorker = ref<any>(null)

const openWorkerDetails = (row: any) => {
  selectedWorker.value = row
  detailsActiveTab.value = 'salaries'
  detailsDialogVisible.value = true
}

const selectedWorkerSalaries = computed(() => {
  if (!selectedWorker.value) return []
  return rawSalaries.value
    .filter((s) => String(s.workerId) === String(selectedWorker.value.id))
    .slice()
    .sort((a, b) => {
      const dateDiff = (b.payDate || '').localeCompare(a.payDate || '')
      if (dateDiff !== 0) return dateDiff
      return (b.id || '').localeCompare(a.id || '')
    })
})

const selectedWorkerAdjustments = computed(() => {
  if (!selectedWorker.value) return []
  return rawAdjustments.value.filter((a) => String(a.workerId) === String(selectedWorker.value.id))
})

const selectedWorkerTotalPaid = computed(() => {
  return selectedWorkerSalaries.value.reduce(
    (sum, s) => sum + Math.max(0, Number(s.netSalary) || 0),
    0
  )
})

const selectedWorkerTotalBonus = computed(() => {
  return selectedWorkerAdjustments.value
    .filter((a) => a.document_type === 'bonus')
    .reduce((sum, a) => sum + (Number(a.amount) || 0), 0)
})

const selectedWorkerTotalDeduction = computed(() => {
  return selectedWorkerAdjustments.value
    .filter((a) => a.document_type === 'penalty' || a.document_type === 'advance')
    .reduce((sum, a) => sum + (Number(a.amount) || 0), 0)
})

const deletePaymentRecord = (row: any) => {
  ElMessageBox.confirm(
    `Ushbu to'lov yozuvini (ID: ${row.id}) o'chirishni tasdiqlaysizmi?`,
    'Eslatma',
    {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(async () => {
      const res = await deleteSalaryApi({ ids: [row.id] })
      if (res && res.code === 0) {
        ElMessage.success("To'lov yozuvi o'chirildi")
        loadData(true)
      }
    })
    .catch(() => {})
}

// Single Quick Pay for 1 Worker
const quickPaySingleWorker = async (worker: any) => {
  ElMessageBox.confirm(
    `${worker.name} ga ${selectedMonthStr.value} oyi uchun $${formatMoney(worker.selectedMonthCalc.netSalary)} maosh to'lashni tasdiqlaysizmi?`,
    "Maosh To'lovi",
    {
      confirmButtonText: "To'lash",
      cancelButtonText: 'Bekor qilish',
      type: 'success'
    }
  )
    .then(async () => {
      loading.value = true
      try {
        const payload = {
          period_month: selectedMonthStr.value,
          items: [
            {
              workerId: worker.id,
              baseSalary: worker.selectedMonthCalc.baseSalary || worker.currentBaseSalary,
              allowance: worker.selectedMonthCalc.bonus,
              deduction: worker.selectedMonthCalc.penalty,
              remark: `${selectedMonthStr.value} oyi maosh to'lovi`
            }
          ]
        }
        const res = await bulkSalaryPayoutApi(payload)
        if (res && (res.code === 0 || res.data)) {
          ElMessage.success(`${worker.name} ga maosh to'landi!`)
          loadData(true)
        }
      } catch (err) {
        console.error(err)
      } finally {
        loading.value = false
      }
    })
    .catch(() => {})
}

// ---------------- Bulk Payout Dialog Logic ----------------
interface PayoutWorkerItem {
  workerId: string
  name: string
  role: string
  baseSalary: number
  totalBonus: number
  totalPenalty: number
  netSalary: number
  selected: boolean
  isAlreadyPaidForMonth: boolean
}

const payoutDialogVisible = ref(false)
const payoutLoading = ref(false)
const submitLoading = ref(false)
const payoutWorkers = ref<PayoutWorkerItem[]>([])
const selectedPayoutMonth = ref(getCurrentMonthString())
const workerFilterText = ref('')
const payoutRemark = ref('')

const computePayoutWorkers = async () => {
  payoutLoading.value = true
  try {
    const targetMonth = selectedPayoutMonth.value
    const items: PayoutWorkerItem[] = []

    for (const w of rawWorkers.value) {
      const wId = String(w.id)
      const currentBase = Number(w.baseSalary || 0)

      const workerSalaries = rawSalaries.value.filter(
        (s) => String(s.workerId) === wId && s.status === 'paid'
      )
      const paidRecord = workerSalaries.find((s) => isSalaryForMonth(s, targetMonth))
      const isAlreadyPaidForMonth = !!paidRecord

      let baseSalary = currentBase
      let totalBonus = 0
      let totalPenalty = 0
      let netSalary = currentBase

      if (isAlreadyPaidForMonth && paidRecord) {
        // Use EXACT immutable historical paid numbers
        baseSalary = Number(paidRecord.baseSalary || 0)
        totalBonus = Number(paidRecord.allowance || 0)
        totalPenalty = Number(paidRecord.deduction || 0)
        netSalary = Number(paidRecord.netSalary || 0)
      } else {
        // Unpaid target month: calculate dynamically from worker current base salary + active adjustments
        const wAdjs = rawAdjustments.value.filter((a: any) => {
          if (String(a.workerId) !== wId) return false
          if (!a.period_month || a.period_month === targetMonth) return true
          if (
            a.period_month < targetMonth &&
            workerSalaries.some((s) => isSalaryForMonth(s, a.period_month))
          ) {
            return true
          }
          return false
        })

        totalBonus = wAdjs
          .filter((a) =>
            ['bonus', 'mukofot', 'reward'].includes(String(a.document_type || '').toLowerCase())
          )
          .reduce((sum, a) => sum + Number(a.amount || 0), 0)

        totalPenalty = wAdjs
          .filter(
            (a) =>
              !['bonus', 'mukofot', 'reward'].includes(String(a.document_type || '').toLowerCase())
          )
          .reduce((sum, a) => sum + Number(a.amount || 0), 0)

        netSalary = Math.max(0, currentBase + totalBonus - totalPenalty)
      }

      items.push({
        workerId: wId,
        name: w.name || 'Xodim',
        role: w.role || 'Xodim',
        baseSalary,
        totalBonus,
        totalPenalty,
        netSalary,
        selected: !isAlreadyPaidForMonth,
        isAlreadyPaidForMonth
      })
    }

    payoutWorkers.value = items
  } catch (err) {
    console.error(err)
  } finally {
    payoutLoading.value = false
  }
}

const openPayoutDialog = async () => {
  payoutDialogVisible.value = true
  selectedPayoutMonth.value = selectedMonthStr.value || getCurrentMonthString()
  payoutRemark.value = ''
  workerFilterText.value = ''
  await computePayoutWorkers()
}

const handlePayoutMonthChange = () => {
  computePayoutWorkers()
}

const filteredPayoutWorkers = computed(() => {
  const q = workerFilterText.value.trim().toLowerCase()
  if (!q) return payoutWorkers.value
  return payoutWorkers.value.filter(
    (w) => w.name.toLowerCase().includes(q) || w.role.toLowerCase().includes(q)
  )
})

const selectedWorkersList = computed(() => {
  return payoutWorkers.value.filter((w) => w.selected && !w.isAlreadyPaidForMonth)
})

const payableWorkers = computed(() => {
  return payoutWorkers.value.filter((w) => !w.isAlreadyPaidForMonth)
})

const payableWorkersCount = computed(() => payableWorkers.value.length)

const selectAllWorkers = computed({
  get: () => payableWorkers.value.length > 0 && payableWorkers.value.every((w) => w.selected),
  set: (val: boolean) => {
    payoutWorkers.value.forEach((w) => {
      if (!w.isAlreadyPaidForMonth) w.selected = val
    })
  }
})

const isIndeterminate = computed(() => {
  const selectedCount = selectedWorkersList.value.length
  return selectedCount > 0 && selectedCount < payableWorkers.value.length
})

const handleSelectAllChange = (val: any) => {
  payoutWorkers.value.forEach((w) => {
    if (!w.isAlreadyPaidForMonth) w.selected = !!val
  })
}

const selectedTotalNet = computed(() => {
  return selectedWorkersList.value.reduce((sum, w) => sum + w.netSalary, 0)
})

const submitPayout = async () => {
  const selected = selectedWorkersList.value
  if (selected.length === 0) {
    ElMessage.warning("Iltimos, kamida bitta to'lanmagan xodimni tanlang!")
    return
  }

  const month = selectedPayoutMonth.value
  const payload = {
    period_month: month,
    items: selected.map((w) => ({
      workerId: w.workerId,
      baseSalary: w.baseSalary,
      allowance: w.totalBonus,
      deduction: w.totalPenalty,
      period_month: month,
      remark: payoutRemark.value || `${month} oyi maosh to'lovi`
    }))
  }

  submitLoading.value = true
  try {
    const res = await bulkSalaryPayoutApi(payload)
    if (res && (res.code === 0 || res.data)) {
      ElMessage.success(`${selected.length} ta xodimga ${month} oyi maoshi tarqatildi!`)
      payoutDialogVisible.value = false
      loadData(true)
    }
  } catch (err) {
    console.error(err)
  } finally {
    submitLoading.value = false
  }
}

const handleExportExcel = () => {
  if (workerRows.value.length === 0) {
    ElMessage.warning('Eksport qilish uchun xodimlar mavjud emas')
    return
  }
  exportToExcel(
    `Oylik_Maoshlar_Hisoboti_${selectedMonthStr.value}`,
    [
      { key: 'name', title: 'Xodim Ismi' },
      { key: 'role', title: 'Lavozimi' },
      { key: 'departmentName', title: "Bo'limi" },
      { key: 'baseSalary', title: 'Asosiy Oylik ($)', formatter: (v) => formatMoney(v || 0) },
      {
        key: 'selectedMonthCalc',
        title: `${selectedMonthStr.value} Sof Hisob ($)`,
        formatter: (v) => formatMoney(v?.netSalary || 0)
      },
      {
        key: 'isSelectedMonthPaid',
        title: `${selectedMonthStr.value} Holati`,
        formatter: (v) => (v ? "To'langan" : "To'lanmagan")
      }
    ],
    workerRows.value
  )
}

useRealtimeSync(['salary', 'worker', 'staff_adjustment', 'staff_hr'], () => {
  loadData(true)
})

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="less">
.salary-page {
  padding-bottom: 20px;
}

.custom-salary-table {
  border-radius: 8px;
  overflow: hidden;

  :deep(.el-table__header) th {
    background-color: var(--el-fill-color-light) !important;
    .cell {
      white-space: nowrap !important;
      word-break: keep-all !important;
      padding: 10px 14px;
      font-weight: 700;
    }
  }

  :deep(.el-table__body) td {
    .cell {
      white-space: nowrap;
      padding: 10px 14px;
      line-height: 1.4;
    }
  }
}
</style>
