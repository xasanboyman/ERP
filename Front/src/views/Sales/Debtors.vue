<template>
  <div class="debtors-page">
    <!-- ─── Stat Cards ─────────────────────────────────────────── -->
    <ContentWrap class="!mb-12px">
      <ElRow :gutter="14">
        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div class="scard">
            <div class="scard-top">
              <div class="scard-label">{{ t('erp.totalDebts') }}</div>
              <div class="scard-icon"><Icon icon="ep:money" :size="20" /></div>
            </div>
            <div class="scard-value">${{ formatMoney(stats.total_debt) }}</div>
          </div>
        </ElCol>
        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div class="scard">
            <div class="scard-top">
              <div class="scard-label">{{ t('erp.activeDebtors') }}</div>
              <div class="scard-icon"><Icon icon="ep:user-filled" :size="20" /></div>
            </div>
            <div class="scard-value"
              >{{ stats.active_debtors_count
              }}<span class="scard-unit"> {{ t('erp.unitsCount') }}</span></div
            >
          </div>
        </ElCol>
        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div class="scard">
            <div class="scard-top">
              <div class="scard-label">{{ t('erp.totalRepaid') }}</div>
              <div class="scard-icon"><Icon icon="ep:wallet" :size="20" /></div>
            </div>
            <div class="scard-value">${{ formatMoney(stats.total_repaid) }}</div>
          </div>
        </ElCol>
        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div class="scard">
            <div class="scard-top">
              <div class="scard-label">{{ t('erp.totalCustomers') }}</div>
              <div class="scard-icon"><Icon icon="ep:data-analysis" :size="20" /></div>
            </div>
            <div class="scard-value"
              >{{ debtorsList.length
              }}<span class="scard-unit"> {{ t('erp.unitsCount') }}</span></div
            >
          </div>
        </ElCol>
      </ElRow>
    </ContentWrap>

    <!-- ─── Filter Bar ─────────────────────────────────────────── -->
    <ContentWrap>
      <div class="toolbar">
        <div class="toolbar-left">
          <ElInput
            v-model="searchQuery.search"
            :placeholder="t('erp.searchNameOrPhone')"
            clearable
            class="toolbar-search"
            @keyup.enter="fetchDebtors"
          >
            <template #prefix><Icon icon="ep:search" /></template>
          </ElInput>

          <ElSelect v-model="searchQuery.status" class="toolbar-select" @change="fetchDebtors">
            <ElOption :label="t('erp.allStatuses')" value="all" />
            <ElOption :label="t('erp.activeDebts')" value="active" />
            <ElOption :label="t('erp.settledDebts')" value="settled" />
          </ElSelect>

          <ElButton type="primary" @click="() => fetchDebtors()">
            <Icon icon="ep:search" class="mr-4px" />{{ t('common.search') }}</ElButton
          >
          <ElButton @click="resetFilter">{{ t('common.reset') }}</ElButton>
        </div>

        <div class="flex items-center gap-10px">
          <ElButton type="primary" size="large" plain @click="handleExportExcel">
            <Icon icon="ep:download" class="mr-6px" />{{ t('erp.exportExcel') }}</ElButton
          >
          <ElButton type="success" size="large" class="repay-btn" @click="openRepayModal()">
            <Icon icon="ep:money" class="mr-6px" />{{ t('erp.repayDebt') }}</ElButton
          >
        </div>
      </div>

      <!-- ─── Table ──────────────────────────────────────────────── -->
      <ElTable
        v-loading="loading"
        :data="debtorsList"
        border
        style="width: 100%"
        class="debtors-table cursor-pointer"
        @row-click="(row) => openHistoryModal(row.name)"
        @sort-change="handleSortChange"
        :row-class-name="rowClass"
      >
        <!-- Mijoz -->
        <ElTableColumn
          :label="t('erp.customerDebtor')"
          min-width="240"
          sortable="custom"
          prop="name"
        >
          <template #default="{ row }">
            <div
              class="debtor-cell cursor-pointer"
              :title="t('erp.qarzdorlikTarixiniKorishUchunBosing')"
            >
              <div
                class="debtor-avatar"
                :class="row.total_debt > 0 ? 'avatar-red' : 'avatar-green'"
              >
                {{ row.name.charAt(0).toUpperCase() }}
                <div class="avatar-ring"></div>
              </div>
              <div class="debtor-info">
                <div class="debtor-name">{{ row.name }}</div>
                <div v-if="row.phone" class="debtor-phone">
                  <Icon icon="ep:phone" :size="10" /> {{ row.phone }}
                </div>
                <!-- Mini progress bar -->
                <div v-if="row.total_initial_debt > 0" class="mini-progress-wrap">
                  <div
                    class="mini-progress-fill"
                    :class="row.total_debt > 0 ? 'fill-red' : 'fill-green'"
                    :style="{
                      width: Math.round((1 - row.total_debt / row.total_initial_debt) * 100) + '%'
                    }"
                  ></div>
                </div>
                <div v-if="row.total_initial_debt > 0" class="mini-progress-pct">
                  {{ Math.round((1 - row.total_debt / row.total_initial_debt) * 100) }}%
                  {{ t('erp.tolangan').toLowerCase() }}
                </div>
              </div>
            </div>
          </template>
        </ElTableColumn>

        <!-- Dastlabki -->
        <ElTableColumn
          :label="t('erp.initialDebt')"
          min-width="140"
          align="right"
          sortable="custom"
          prop="total_initial_debt"
        >
          <template #default="{ row }">
            <span class="mono gray">${{ formatMoney(row.total_initial_debt) }}</span>
          </template>
        </ElTableColumn>

        <!-- Qaytarilgan -->
        <ElTableColumn
          :label="t('erp.repaid')"
          min-width="135"
          align="right"
          sortable="custom"
          prop="total_repaid"
        >
          <template #default="{ row }">
            <span class="mono green font-bold">${{ formatMoney(row.total_repaid) }}</span>
          </template>
        </ElTableColumn>

        <!-- Qolgan -->
        <ElTableColumn
          :label="t('erp.remainingDebt')"
          min-width="165"
          align="right"
          sortable="custom"
          prop="total_debt"
        >
          <template #default="{ row }">
            <span v-if="row.total_debt > 0" class="debt-badge">
              ${{ formatMoney(row.total_debt) }}
            </span>
            <span v-else class="settled-badge">{{ t('erp.settledBadge') }}</span>
          </template>
        </ElTableColumn>

        <!-- Bitimlar -->
        <ElTableColumn
          :label="t('erp.deals')"
          width="86"
          align="center"
          sortable="custom"
          prop="sales_count"
        >
          <template #default="{ row }">
            <span class="count-badge">{{ row.sales_count }}</span>
          </template>
        </ElTableColumn>

        <!-- Oxirgi -->
        <ElTableColumn
          :label="t('erp.lastTransaction')"
          min-width="148"
          sortable="custom"
          prop="last_sale_date"
        >
          <template #default="{ row }">
            <span class="mono gray-sm">{{ row.last_sale_date }}</span>
          </template>
        </ElTableColumn>

        <!-- Amallar -->
        <ElTableColumn :label="t('erp.amallar')" width="210" fixed="right" align="center">
          <template #default="{ row }">
            <ElButton
              v-if="row.total_debt > 0"
              size="small"
              type="success"
              @click.stop="openRepayModal(row)"
            >
              <Icon icon="ep:money" class="mr-3px" />{{ t('erp.repay') }}</ElButton
            >
            <ElButton size="small" type="primary" plain @click.stop="openHistoryModal(row.name)">
              <Icon icon="ep:document" class="mr-3px" />{{ t('erp.history') }}</ElButton
            >
          </template>
        </ElTableColumn>
      </ElTable>
    </ContentWrap>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- REPAY MODAL                                                -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <ResizeDialog
      v-model="repayModalVisible"
      :title="t('erp.repayModalTitle')"
      storage-key="repay_v5"
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="500"
      :min-resize-height="500"
    >
      <div class="repay-wrap">
        <!-- Header -->
        <div class="repay-header">
          <div>
            <div class="rh-label">{{ t('erp.debtorCustomer') }}</div>
            <div class="rh-name">{{ repayForm.customer_name || '—' }}</div>
          </div>
          <div class="text-right">
            <div class="rh-label">{{ t('erp.existingDebt') }}</div>
            <div class="rh-debt">${{ formatMoney(repayTargetDebt) }}</div>
          </div>
        </div>

        <ElForm label-position="top" class="mt-16px space-y-2px">
          <!-- Debtor selector -->
          <ElFormItem>
            <template #label
              ><span class="flabel">{{ t('erp.selectOrEnterCustomer') }}</span></template
            >
            <ElSelect
              v-model="repayForm.customer_name"
              filterable
              allow-create
              default-first-option
              :placeholder="t('erp.ismiYokiTanlang')"
              style="width: 100%"
              @change="onRepayDebtorChange"
            >
              <ElOption
                v-for="d in debtorsList"
                :key="d.name"
                :label="`${d.name}${d.total_debt > 0 ? '  —  Qarz: $' + formatMoney(d.total_debt) : '  ✓'}`"
                :value="d.name"
              />
            </ElSelect>
          </ElFormItem>

          <!-- Phone -->
          <ElFormItem>
            <template #label>
              <span class="flabel"
                >Telefon <span class="flabel-hint">(+998 99 999 99 99)</span></span
              >
            </template>
            <ElInput
              v-model="repayForm.customer_phone"
              placeholder="+998 99 984 72 31"
              style="width: 100%"
              @blur="formatPhoneInput"
            >
              <template #prefix><Icon icon="ep:phone" /></template>
            </ElInput>
          </ElFormItem>

          <!-- Amount -->
          <ElFormItem>
            <template #label
              ><span class="flabel">{{ t('erp.repayAmountDollar') }}</span></template
            >
            <ElInput
              v-model="displayRepayAmount"
              :placeholder="t('erp.enterAmount')"
              size="large"
              class="amount-input"
            />
            <div class="pct-btns">
              <ElButton size="small" plain @click="setPercentageRepay(0.25)">25%</ElButton>
              <ElButton size="small" plain @click="setPercentageRepay(0.5)">50%</ElButton>
              <ElButton size="small" plain @click="setPercentageRepay(0.75)">75%</ElButton>
              <ElButton size="small" type="success" plain @click="setFullRepay"
                >To'liq (${{ formatMoney(repayTargetDebt) }})</ElButton
              >
            </div>
          </ElFormItem>

          <!-- Payment method -->
          <ElFormItem>
            <template #label
              ><span class="flabel">{{ t('erp.paymentMethodLabel') }}</span></template
            >
            <ElRadioGroup v-model="repayForm.payment_method" size="large" style="width: 100%">
              <ElRadioButton value="naqd">💵 Naqd</ElRadioButton>
              <ElRadioButton value="karta">💳 Karta</ElRadioButton>
              <ElRadioButton value="otkazma">{{ t('erp.transferPayment') }}</ElRadioButton>
            </ElRadioGroup>
          </ElFormItem>

          <!-- Remark -->
          <ElFormItem>
            <template #label
              ><span class="flabel">{{ t('erp.izoh') }}</span></template
            >
            <ElInput
              v-model="repayForm.remark"
              type="textarea"
              :rows="2"
              :placeholder="t('erp.additionalRemark')"
            />
          </ElFormItem>
        </ElForm>
      </div>

      <template #footer>
        <div class="flex justify-between items-center">
          <div class="text-14px text-gray-400"
            >{{ t('erp.afterPaymentRemaining')
            }}<span class="font-bold text-amber-400 ml-4px">
              ${{ formatMoney(Math.max(0, repayTargetDebt - repayForm.amount)) }}
            </span>
          </div>
          <div class="flex gap-10px">
            <ElButton @click="repayModalVisible = false">{{ t('common.cancel') }}</ElButton>
            <ElButton
              type="success"
              size="large"
              class="font-bold px-20px"
              :loading="submittingRepay"
              @click="submitDebtRepayment"
            >
              <Icon icon="ep:check" class="mr-6px" /> {{ t('erp.acceptPayment') }} (${{
                formatMoney(repayForm.amount)
              }})
            </ElButton>
          </div>
        </div>
      </template>
    </ResizeDialog>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- HISTORY MODAL                                              -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <ResizeDialog
      v-model="historyModalVisible"
      :title="t('erp.debtHistory')"
      storage-key="history_v5"
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="700"
      :min-resize-height="560"
    >
      <div v-if="debtorDetail" class="history-wrap">
        <!-- Customer header -->
        <div class="hist-header">
          <div class="hist-avatar">{{ debtorDetail.customer_name.charAt(0).toUpperCase() }}</div>
          <div class="flex-1">
            <div class="hist-name">{{ debtorDetail.customer_name }}</div>
            <div v-if="debtorDetail.phone" class="hist-phone">
              <Icon icon="ep:phone" :size="12" /> {{ debtorDetail.phone }}
            </div>
          </div>
          <div class="hist-debt-summary">
            <div class="hds-item">
              <span class="hds-label">{{ t('erp.nasiyaSales') }}</span>
              <span class="hds-val blue"
                >${{
                  formatMoney(
                    debtorDetail.sales?.reduce((a: number, s: any) => a + s.total_amount, 0)
                  )
                }}</span
              >
            </div>
            <div class="hds-item">
              <span class="hds-label">Qaytarilgan</span>
              <span class="hds-val green"
                >${{
                  formatMoney(debtorDetail.payments?.reduce((a: number, p: any) => a + p.amount, 0))
                }}</span
              >
            </div>
            <div class="hds-item">
              <span class="hds-label">Qolgan Qarz</span>
              <span class="hds-val red">${{ formatMoney(debtorDetail.total_debt) }}</span>
            </div>
          </div>
        </div>

        <!-- Nasiya sales table -->
        <div class="hist-section">
          <div class="hist-section-title">
            <Icon icon="ep:tickets" class="text-blue-400 mr-6px" />
            {{ t('erp.nasiyaSales') }}
            <span class="hist-count">{{ debtorDetail.sales?.length || 0 }} ta sotuv</span>
          </div>
          <ElTable :data="debtorDetail.sales" border stripe size="small" style="width: 100%">
            <ElTableColumn label="Chek #" min-width="195">
              <template #default="{ row }">
                <span class="chk-link" @click="openSaleReceiptDetail(row.receipt_number)">
                  🧾 {{ row.receipt_number }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="created_at" label="Sana" min-width="145" />
            <ElTableColumn prop="cashier_name" :label="t('erp.cashier')" min-width="120">
              <template #default="{ row }">
                <span class="text-amber-400 text-12px font-semibold">{{ row.cashier_name }}</span>
              </template>
            </ElTableColumn>
            <ElTableColumn label="Jami ($)" align="right" min-width="110">
              <template #default="{ row }"
                ><span class="mono">${{ formatMoney(row.total_amount) }}</span></template
              >
            </ElTableColumn>
            <ElTableColumn label="To'langan ($)" align="right" min-width="120">
              <template #default="{ row }"
                ><span class="mono green">${{ formatMoney(row.paid_amount) }}</span></template
              >
            </ElTableColumn>
            <ElTableColumn :label="t('erp.debtDollar')" align="right" min-width="110">
              <template #default="{ row }">
                <span :class="row.debt_amount > 0 ? 'mono red font-bold' : 'mono text-gray-500'"
                  >${{ formatMoney(row.debt_amount) }}</span
                >
              </template>
            </ElTableColumn>
            <ElTableColumn label="Mahsulot" align="center" width="90">
              <template #default="{ row }">
                <ElTag type="info" effect="plain" size="small">{{ row.total_items }} ta</ElTag>
              </template>
            </ElTableColumn>
          </ElTable>
        </div>

        <!-- Payment history table -->
        <div class="hist-section mt-16px">
          <div class="hist-section-title">
            <Icon icon="ep:wallet" class="text-emerald-400 mr-6px" />
            {{ t('erp.repaymentHistory') }}
            <span class="hist-count">{{ debtorDetail.payments?.length || 0 }} ta to'lov</span>
          </div>
          <div v-if="!debtorDetail.payments?.length" class="hist-empty">
            {{ t('erp.noRepaymentsYet') }}
          </div>
          <ElTable
            v-else
            :data="debtorDetail.payments"
            border
            stripe
            size="small"
            style="width: 100%"
          >
            <ElTableColumn label="To'lov Chek #" min-width="215">
              <template #default="{ row }">
                <span class="chk-link green" @click="openPaymentReceiptDetail(row.receipt_number)">
                  💳 {{ row.receipt_number }}
                </span>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="created_at" label="Sana" min-width="145" />
            <ElTableColumn prop="cashier_name" :label="t('erp.cashier')" min-width="120">
              <template #default="{ row }">
                <span class="text-amber-400 text-12px font-semibold">{{ row.cashier_name }}</span>
              </template>
            </ElTableColumn>
            <ElTableColumn label="To'langan ($)" align="right" min-width="130">
              <template #default="{ row }">
                <span class="mono green font-bold">${{ formatMoney(row.amount) }}</span>
              </template>
            </ElTableColumn>
            <ElTableColumn label="Usul" align="center" width="100">
              <template #default="{ row }">
                <ElTag size="small" type="success" effect="dark" class="uppercase font-bold">{{
                  row.payment_method
                }}</ElTag>
              </template>
            </ElTableColumn>
            <ElTableColumn :label="t('erp.izoh')" min-width="130">
              <template #default="{ row }">
                <span class="text-12px text-gray-400">{{ row.remark || '—' }}</span>
              </template>
            </ElTableColumn>
          </ElTable>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center">
          <ElButton
            v-if="debtorDetail?.total_debt > 0"
            type="success"
            @click="openRepayFromHistory"
          >
            <Icon icon="ep:money" class="mr-6px" />{{ t('erp.repayDebt') }}</ElButton
          >
          <ElButton @click="historyModalVisible = false">{{ t('common.close') }}</ElButton>
        </div>
      </template>
    </ResizeDialog>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- SALE RECEIPT DETAIL (clicking CHK in Nasiya table)        -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <ResizeDialog
      v-model="saleReceiptDetailVisible"
      :title="`Sotuv Cheki — ${saleReceiptData?.receipt_number || ''}`"
      storage-key="sale_receipt_v3"
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="620"
      :min-resize-height="520"
    >
      <div v-if="saleReceiptData" class="receipt-detail">
        <!-- Meta grid -->
        <div class="meta-grid">
          <div class="meta-box">
            <div class="meta-label">Chek Raqami</div>
            <div class="meta-val blue mono">{{ saleReceiptData.receipt_number }}</div>
          </div>
          <div class="meta-box">
            <div class="meta-label">Sana va Vaqt</div>
            <div class="meta-val mono">{{ saleReceiptData.created_at }}</div>
          </div>
          <div class="meta-box">
            <div class="meta-label">Kassir / Xodim</div>
            <div class="meta-val amber">{{ saleReceiptData.cashier_name }}</div>
          </div>
          <div class="meta-box">
            <div class="meta-label">{{ t('erp.paymentMethodLabel') }}</div>
            <div class="meta-val green uppercase">{{ saleReceiptData.payment_method }}</div>
          </div>
          <div class="meta-box">
            <div class="meta-label">Mijoz Ismi</div>
            <div class="meta-val">{{ saleReceiptData.customer_name || '—' }}</div>
          </div>
          <div class="meta-box">
            <div class="meta-label">Telefon</div>
            <div class="meta-val mono">{{ saleReceiptData.customer_phone || '—' }}</div>
          </div>
        </div>

        <!-- Items -->
        <div class="hist-section-title mt-14px mb-8px">
          <Icon icon="ep:goods" class="text-blue-400 mr-6px" />{{ t('erp.soldProducts')
          }}<span class="hist-count">{{ saleReceiptData.total_items }} ta</span>
        </div>
        <ElTable :data="saleReceiptData.items" border stripe size="small" style="width: 100%">
          <ElTableColumn type="index" label="#" width="46" align="center" />
          <ElTableColumn prop="product_name" label="Mahsulot" min-width="230" />
          <ElTableColumn prop="shtrix_code" label="Shtrix Kod" min-width="130">
            <template #default="{ row }"
              ><span class="mono gray-sm">{{ row.shtrix_code || '—' }}</span></template
            >
          </ElTableColumn>
          <ElTableColumn prop="quantity" label="Miqdor" align="center" width="80" />
          <ElTableColumn label="Narx ($)" align="right" width="110">
            <template #default="{ row }"
              ><span class="mono">${{ formatMoney(row.price) }}</span></template
            >
          </ElTableColumn>
          <ElTableColumn label="Jami ($)" align="right" width="120">
            <template #default="{ row }"
              ><span class="mono font-bold text-[var(--el-text-color-primary)]"
                >${{ formatMoney(row.total) }}</span
              ></template
            >
          </ElTableColumn>
        </ElTable>

        <!-- Financial summary -->
        <div class="fin-summary">
          <div class="fin-box">
            <div class="fin-label">Jami Mahsulot</div>
            <div class="fin-val white">${{ formatMoney(saleReceiptData.total_amount) }}</div>
          </div>
          <div class="fin-box">
            <div class="fin-label">Chegirma</div>
            <div class="fin-val amber">-${{ formatMoney(saleReceiptData.discount) }}</div>
          </div>
          <div class="fin-box">
            <div class="fin-label">{{ t('erp.tolangan') }}</div>
            <div class="fin-val blue">${{ formatMoney(saleReceiptData.paid_amount) }}</div>
          </div>
          <div class="fin-box">
            <div class="fin-label">{{ t('erp.nasiyaDebt') }}</div>
            <div :class="saleReceiptData.debt_amount > 0 ? 'fin-val red' : 'fin-val gray-text'"
              >${{ formatMoney(saleReceiptData.debt_amount) }}</div
            >
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-10px">
          <ElButton @click="saleReceiptDetailVisible = false">{{ t('common.close') }}</ElButton>
        </div>
      </template>
    </ResizeDialog>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- PAYMENT RECEIPT DETAIL (clicking QARZ-CHK in payment table) -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <ResizeDialog
      v-model="paymentDetailVisible"
      :title="`To'lov Cheki — ${paymentDetailData?.receipt_number || ''}`"
      storage-key="pay_receipt_detail_v2"
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="500"
      :min-resize-height="420"
    >
      <div v-if="paymentDetailData" class="pay-receipt-card">
        <div class="pr-brand">
          <div class="pr-brand-title">{{ t('erp.debtPaymentReceipt') }}</div>
          <div class="pr-receipt-no">{{ paymentDetailData.receipt_number }}</div>
        </div>

        <div class="pr-grid">
          <div class="pr-row">
            <span class="pr-key">Mijoz:</span>
            <span class="pr-val white font-bold">{{ paymentDetailData.customer_name }}</span>
          </div>
          <div class="pr-row" v-if="paymentDetailData.customer_phone">
            <span class="pr-key">Telefon:</span>
            <span class="pr-val mono">{{ paymentDetailData.customer_phone }}</span>
          </div>
          <div class="pr-row">
            <span class="pr-key">Kassir:</span>
            <span class="pr-val amber">{{ paymentDetailData.cashier_name }}</span>
          </div>
          <div class="pr-row">
            <span class="pr-key">Sana:</span>
            <span class="pr-val mono">{{ paymentDetailData.created_at }}</span>
          </div>
          <div class="pr-row">
            <span class="pr-key">To'lov Usuli:</span>
            <span class="pr-val uppercase green font-bold">{{
              paymentDetailData.payment_method
            }}</span>
          </div>
          <div v-if="paymentDetailData.remark" class="pr-row">
            <span class="pr-key">Izoh:</span>
            <span class="pr-val gray-text">{{ paymentDetailData.remark }}</span>
          </div>
        </div>

        <div class="pr-amount-highlight">
          <div class="prah-label">{{ t('erp.repaidDebtAmount') }}</div>
          <div class="prah-amount">${{ formatMoney(paymentDetailData.amount) }}</div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-10px">
          <ElButton type="primary" @click="() => window.print()"
            ><Icon icon="ep:printer" class="mr-4px" />Chop etish</ElButton
          >
          <ElButton @click="paymentDetailVisible = false">{{ t('common.close') }}</ElButton>
        </div>
      </template>
    </ResizeDialog>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- QUICK PAYMENT RECEIPT (after paying debt)                  -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <ResizeDialog
      v-model="quickReceiptVisible"
      :title="t('erp.debtPaymentConfirmReceipt')"
      storage-key="quick_receipt_v2"
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="480"
      :min-resize-height="380"
    >
      <div v-if="latestPaymentReceipt" class="pay-receipt-card">
        <div class="pr-brand">
          <div class="pr-brand-title">{{ t('erp.debtPaymentReceipt') }}</div>
          <div class="pr-receipt-no">{{ latestPaymentReceipt.receipt_number }}</div>
        </div>
        <div class="pr-grid">
          <div class="pr-row">
            <span class="pr-key">Mijoz:</span>
            <span class="pr-val white font-bold">{{ latestPaymentReceipt.customer_name }}</span>
          </div>
          <div class="pr-row">
            <span class="pr-key">Kassir:</span>
            <span class="pr-val amber">{{ latestPaymentReceipt.cashier_name }}</span>
          </div>
          <div class="pr-row">
            <span class="pr-key">Sana:</span>
            <span class="pr-val mono">{{ latestPaymentReceipt.created_at }}</span>
          </div>
          <div class="pr-row">
            <span class="pr-key">To'lov Usuli:</span>
            <span class="pr-val uppercase green font-bold">{{
              latestPaymentReceipt.payment_method
            }}</span>
          </div>
        </div>
        <div class="pr-amount-highlight">
          <div class="prah-label">To'langan Summa</div>
          <div class="prah-amount">${{ formatMoney(latestPaymentReceipt.amount) }}</div>
        </div>
        <div class="pr-remaining">
          <span class="text-gray-400">{{ t('erp.remainingTotalDebt') }}</span>
          <span class="font-bold text-red-400 ml-6px"
            >${{ formatMoney(latestPaymentReceipt.remaining_total_debt) }}</span
          >
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-10px">
          <ElButton type="primary" @click="() => window.print()"
            ><Icon icon="ep:printer" class="mr-4px" />Print</ElButton
          >
          <ElButton @click="quickReceiptVisible = false">{{ t('common.close') }}</ElButton>
        </div>
      </template>
    </ResizeDialog>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
defineOptions({ name: 'SalesDebtors' })
import { ref, reactive, computed, onMounted } from 'vue'
import { ContentWrap } from '@/components/ContentWrap'
import { ResizeDialog } from '@/components/Dialog'
import { Icon } from '@/components/Icon'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'
import {
  ElRow,
  ElCol,
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption,
  ElButton,
  ElTable,
  ElTableColumn,
  ElTag,
  ElRadioGroup,
  ElRadioButton,
  ElMessage,
  ElNotification
} from 'element-plus'
import {
  getDebtorsApi,
  getDebtorDetailApi,
  repayDebtApi,
  getSaleReceiptApi,
  getPaymentReceiptApi
} from '@/api/sales'

const window = globalThis

const dialogInitWidth = Math.min(window.innerWidth * 0.92, 1400)
const dialogInitHeight = Math.min(window.innerHeight * 0.88, 800)

// ── State ─────────────────────────────────────────────────────────────────
const loading = ref(false)
const submittingRepay = ref(false)

const repayModalVisible = ref(false)
const historyModalVisible = ref(false)
const quickReceiptVisible = ref(false)
const saleReceiptDetailVisible = ref(false)
const paymentDetailVisible = ref(false)

const stats = reactive({ total_debt: 0, total_repaid: 0, active_debtors_count: 0 })
const searchQuery = reactive({ search: '', status: 'all' })

const debtorsList = ref<any[]>([])
const debtorDetail = ref<any>(null)
const latestPaymentReceipt = ref<any>(null)
const saleReceiptData = ref<any>(null)
const paymentDetailData = ref<any>(null)

const repayForm = reactive({
  customer_name: '',
  customer_phone: '',
  amount: 0,
  payment_method: 'naqd',
  remark: ''
})

// ── Helpers ────────────────────────────────────────────────────────────────
const formatMoney = (val: number | string | null | undefined) => {
  if (val === undefined || val === null || val === '') return '0'
  const n = Number(val)
  return isNaN(n)
    ? '0'
    : Math.round(n)
        .toString()
        .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

const formatPhone = (raw: string) => {
  const d = raw.replace(/\D/g, '')
  if (!d) return ''
  const norm = d.startsWith('998') ? d : '998' + d
  const t = norm.slice(0, 12)
  const p = [t.slice(3, 5), t.slice(5, 8), t.slice(8, 10), t.slice(10, 12)]
  return (
    '+998' +
    p
      .filter(Boolean)
      .map((s) => ' ' + s)
      .join('')
  )
}

const formatPhoneInput = () => {
  if (repayForm.customer_phone) repayForm.customer_phone = formatPhone(repayForm.customer_phone)
}

// ── Computed ───────────────────────────────────────────────────────────────
const displayRepayAmount = computed({
  get: () =>
    repayForm.amount ? repayForm.amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') : '',
  set: (v: string) => {
    const d = v.replace(/\D/g, '')
    repayForm.amount = d ? parseInt(d) : 0
  }
})

const repayTargetDebt = computed(() => {
  const m = debtorsList.value.find((d) => d.name === repayForm.customer_name)
  return m ? m.total_debt : 0
})

// ── Column sort handler (used by @sort-change on ElTable) ─────────────────
const handleSortChange = ({ prop, order }: { prop: string; order: string | null }) => {
  if (!prop || !order) {
    // Restore original fetch order
    fetchDebtors()
    return
  }
  const asc = order === 'ascending'
  debtorsList.value = [...debtorsList.value].sort((a, b) => {
    const va = a[prop]
    const vb = b[prop]
    // Numeric columns
    if (typeof va === 'number' || typeof vb === 'number') {
      return asc ? Number(va) - Number(vb) : Number(vb) - Number(va)
    }
    // String / date columns
    const sa = String(va ?? '')
    const sb = String(vb ?? '')
    return asc ? sa.localeCompare(sb) : sb.localeCompare(sa)
  })
}

// ── Data fetching ──────────────────────────────────────────────────────────
const fetchDebtors = async (silent = false) => {
  if (!silent) {
    loading.value = true
  }
  try {
    const res: any = await getDebtorsApi({
      search: searchQuery.search || undefined,
      status: searchQuery.status !== 'all' ? searchQuery.status : undefined
    })
    if (res?.data) {
      debtorsList.value = res.data.list || []
      stats.total_debt = res.data.total_debt || 0
      stats.total_repaid = res.data.total_repaid || 0
      stats.active_debtors_count = res.data.active_debtors_count || 0
    }
  } catch {
    if (!silent) {
      ElMessage.error('Qarzdorlarni yuklashda xatolik')
    }
  } finally {
    if (!silent) {
      loading.value = false
    }
  }
}

// Silently update debtor balances when payments or credit sales occur
useRealtimeSync(['debt', 'sale'], () => {
  fetchDebtors(true)
})

import { exportToExcel } from '@/utils/exportReport'

const handleExportExcel = () => {
  if (debtorsList.value.length === 0) {
    ElMessage.warning("Eksport qilish uchun ma'lumot mavjud emas")
    return
  }
  exportToExcel(
    'Qarzdorlar_Hisoboti',
    [
      { key: 'name', title: 'Mijoz Ismi' },
      { key: 'phone', title: 'Telefon Raqami' },
      { key: 'total_debt', title: 'Umumiy Qarz ($)', formatter: (v) => formatMoney(v || 0) },
      { key: 'total_repaid', title: 'To‘langan ($)', formatter: (v) => formatMoney(v || 0) },
      { key: 'current_balance', title: 'Qolgan Qarz ($)', formatter: (v) => formatMoney(v || 0) },
      {
        key: 'status',
        title: 'Holati',
        formatter: (v) => (v === 'settled' ? 'Yopilgan' : 'Faol Qarz')
      },
      { key: 'last_sale_date', title: 'Oxirgi Xarid Sanasi' }
    ],
    debtorsList.value
  )
  ElMessage.success('Qarzdorlar hisoboti Excel fayliga yuklab olindi!')
}

const resetFilter = () => {
  searchQuery.search = ''
  searchQuery.status = 'all'
  fetchDebtors()
}

// ── Repay ──────────────────────────────────────────────────────────────────
const openRepayModal = (row?: any) => {
  if (row) {
    repayForm.customer_name = row.name
    repayForm.customer_phone = row.phone ? formatPhone(row.phone) : '+998 '
  } else {
    repayForm.customer_name = ''
    repayForm.customer_phone = '+998 '
  }
  repayForm.amount = 0
  repayForm.payment_method = 'naqd'
  repayForm.remark = ''
  repayModalVisible.value = true
}

const onRepayDebtorChange = (name: string) => {
  const m = debtorsList.value.find((d) => d.name === name)
  repayForm.customer_phone = m?.phone ? formatPhone(m.phone) : '+998 '
}

const setPercentageRepay = (r: number) => {
  repayForm.amount = Math.round(repayTargetDebt.value * r)
}
const setFullRepay = () => {
  repayForm.amount = repayTargetDebt.value
}

const submitDebtRepayment = async () => {
  if (!repayForm.customer_name.trim()) {
    ElMessage.warning('Mijozni tanlang!')
    return
  }
  if (!repayForm.amount || repayForm.amount <= 0) {
    ElMessage.warning('Summani kiriting!')
    return
  }
  submittingRepay.value = true
  try {
    const res: any = await repayDebtApi({
      customer_name: repayForm.customer_name.trim(),
      customer_phone: repayForm.customer_phone.trim(),
      amount: repayForm.amount,
      payment_method: repayForm.payment_method,
      cashier_name: 'admin',
      remark: repayForm.remark
    })
    if (res?.data) {
      latestPaymentReceipt.value = res.data
      repayModalVisible.value = false
      quickReceiptVisible.value = true
      ElNotification({
        title: "To'lov qabul qilindi!",
        message: `$${formatMoney(repayForm.amount)} to'landi.`,
        type: 'success',
        duration: 5000
      })
      fetchDebtors()
    }
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || 'Xatolik yuz berdi')
  } finally {
    submittingRepay.value = false
  }
}

// ── History ────────────────────────────────────────────────────────────────
const openHistoryModal = async (name: string) => {
  try {
    const res: any = await getDebtorDetailApi(name)
    if (res?.data) {
      debtorDetail.value = res.data
      historyModalVisible.value = true
    }
  } catch {
    ElMessage.error('Tarixni yuklashda xatolik')
  }
}

const openRepayFromHistory = () => {
  if (!debtorDetail.value) return
  historyModalVisible.value = false
  openRepayModal({ name: debtorDetail.value.customer_name, phone: debtorDetail.value.phone })
}

// ── Receipt detail viewers ─────────────────────────────────────────────────
const openSaleReceiptDetail = async (receiptNo: string) => {
  try {
    const res: any = await getSaleReceiptApi(receiptNo)
    if (res?.data) {
      saleReceiptData.value = res.data
      saleReceiptDetailVisible.value = true
    }
  } catch {
    ElMessage.error("Chek ma'lumotlarini yuklashda xatolik")
  }
}

const openPaymentReceiptDetail = async (receiptNo: string) => {
  try {
    const res: any = await getPaymentReceiptApi(receiptNo)
    if (res?.data) {
      paymentDetailData.value = res.data
      paymentDetailVisible.value = true
    }
  } catch {
    ElMessage.error("To'lov cheki ma'lumotlarini yuklashda xatolik")
  }
}

// ── Row class for hover colouring ─────────────────────────────────────────────
const rowClass = ({ row }: { row: any }) => (row.total_debt > 0 ? 'row-debt' : 'row-settled')

import { useEventBus } from '@/hooks/event/useEventBus'

useEventBus({
  name: 'refresh-debtors',
  callback: () => {
    fetchDebtors()
  }
})

useEventBus({
  name: 'ai-data-updated',
  callback: () => {
    fetchDebtors()
  }
})

onMounted(fetchDebtors)
</script>

<style scoped lang="less">
// ── Page ────────────────────────────────────────────────────────────────────
.debtors-page {
  padding: 8px;
}

// ── Stat Cards ───────────────────────────────────────────────────────────────
.scard {
  position: relative;
  overflow: hidden;
  padding: 16px;
  border-radius: 10px;
  background: var(--el-bg-color-overlay, #ffffff);
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
  cursor: default;

  &:hover {
    border-color: var(--el-border-color, #cbd5e1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }

  .scard-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .scard-icon {
    width: 38px;
    height: 38px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--el-fill-color-light, #f1f5f9);
    color: var(--el-text-color-primary, #334155);
  }
  .scard-value {
    font-size: 22px;
    font-weight: 800;
    font-family: 'SF Mono', monospace, ui-monospace;
    color: var(--el-text-color-primary, #0f172a);
    line-height: 1.2;
  }
  .scard-unit {
    font-size: 13px;
    font-weight: 500;
    opacity: 0.7;
  }
  .scard-label {
    font-size: 12px;
    color: var(--el-text-color-secondary, #64748b);
    font-weight: 600;
  }
}

:global(.dark) {
  .scard {
    background: #1e293b;
    border-color: #334155;
    box-shadow: none;

    &:hover {
      border-color: #475569;
    }

    .scard-icon {
      background: #334155;
      color: #f8fafc;
    }
  }
}

@keyframes pulseUp {
  0%,
  100% {
    transform: translateY(0);
    opacity: 0.8;
  }
  50% {
    transform: translateY(-3px);
    opacity: 1;
  }
}
@keyframes shimmer {
  0% {
    background-position: -200% center;
  }
  100% {
    background-position: 200% center;
  }
}

// ── Toolbar ──────────────────────────────────────────────────────────────────
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
  padding: 14px 16px;
  background: var(--el-bg-color-overlay, #ffffff);
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);

  .toolbar-left {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    flex: 1;
  }
  .toolbar-search {
    width: 230px;
  }
  .toolbar-select {
    width: 180px;
  }
  .repay-btn {
    font-weight: 700;
    background: linear-gradient(135deg, #059669, #10b981) !important;
    border-color: transparent !important;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);
    transition:
      box-shadow 0.2s,
      transform 0.15s;
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 24px rgba(16, 185, 129, 0.5);
    }
  }
}

:global(.dark) {
  .toolbar {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    border-color: #1e293b;
    box-shadow: none;
  }
}

// ── Table ────────────────────────────────────────────────────────────────────
.debtors-table {
  border-radius: 12px;
  overflow: hidden;

  :deep(.el-table__row) {
    transition:
      background 0.18s,
      box-shadow 0.18s;
    &:hover > td {
      background: rgba(59, 130, 246, 0.06) !important;
    }
    &.row-debt:hover > td {
      background: rgba(239, 68, 68, 0.07) !important;
    }
    &.row-settled:hover > td {
      background: rgba(16, 185, 129, 0.06) !important;
    }
  }
  :deep(.el-table__header th) {
    background: var(--el-fill-color-light, #f8fafc) !important;
    color: var(--el-text-color-regular, #64748b);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 700;
  }

  :global(.dark) & {
    :deep(.el-table__header th) {
      background: #0d1424 !important;
      color: #94a3b8;
    }
  }

  // Debtor cell
  .debtor-cell {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .debtor-avatar {
    position: relative;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 16px;
    flex-shrink: 0;
    transition: transform 0.2s;
    &:hover {
      transform: scale(1.08);
    }

    &.avatar-red {
      background: rgba(239, 68, 68, 0.12);
      border: 1.5px solid rgba(239, 68, 68, 0.4);
      color: #dc2626;
    }
    &.avatar-green {
      background: rgba(16, 185, 129, 0.12);
      border: 1.5px solid rgba(16, 185, 129, 0.4);
      color: #059669;
    }
    .avatar-ring {
      position: absolute;
      inset: -3px;
      border-radius: 50%;
      border: 1px solid rgba(0, 0, 0, 0.06);
    }
  }

  :global(.dark) & {
    .debtor-avatar.avatar-red {
      background: linear-gradient(135deg, rgba(127, 29, 29, 0.8), rgba(185, 28, 28, 0.5));
      border-color: rgba(239, 68, 68, 0.5);
      color: #fca5a5;
      box-shadow: 0 0 12px rgba(239, 68, 68, 0.25);
    }
    .debtor-avatar.avatar-green {
      background: linear-gradient(135deg, rgba(6, 78, 59, 0.8), rgba(4, 120, 87, 0.5));
      border-color: rgba(16, 185, 129, 0.5);
      color: #6ee7b7;
      box-shadow: 0 0 12px rgba(16, 185, 129, 0.2);
    }
    .debtor-avatar .avatar-ring {
      border-color: rgba(255, 255, 255, 0.06);
    }
  }

  .debtor-info {
    min-width: 0;
    flex: 1;
  }
  .debtor-name {
    font-size: 14px;
    font-weight: 700;
    color: var(--el-text-color-primary, #0f172a);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  :global(.dark) & .debtor-name {
    color: #f1f5f9;
  }

  .debtor-phone {
    font-size: 11px;
    color: var(--el-text-color-secondary, #64748b);
    font-family: monospace;
    margin-top: 1px;
    display: flex;
    align-items: center;
    gap: 3px;
  }
  // Mini debt progress bar
  .mini-progress-wrap {
    height: 3px;
    background: var(--el-fill-color, rgba(0, 0, 0, 0.08));
    border-radius: 2px;
    overflow: hidden;
    margin-top: 5px;
    .mini-progress-fill {
      height: 100%;
      border-radius: 2px;
      transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
      &.fill-red {
        background: linear-gradient(90deg, #ef4444, #f97316);
      }
      &.fill-green {
        background: linear-gradient(90deg, #10b981, #34d399);
      }
    }
  }
  .mini-progress-pct {
    font-size: 10px;
    color: var(--el-text-color-secondary, #64748b);
    margin-top: 2px;
  }
}

// ── Badges ────────────────────────────────────────────────────────────────────
.debt-badge {
  display: inline-block;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #dc2626;
  font-family: 'SF Mono', monospace, ui-monospace;
  font-size: 14px;
  font-weight: 800;
  padding: 3px 12px;
  border-radius: 8px;
  white-space: nowrap;
}
:global(.dark) {
  .debt-badge {
    background: linear-gradient(135deg, rgba(127, 29, 29, 0.5), rgba(185, 28, 28, 0.3));
    border-color: rgba(239, 68, 68, 0.4);
    color: #fca5a5;
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.15);
  }
}

.settled-badge {
  display: inline-block;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #059669;
  font-size: 12px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
}
:global(.dark) {
  .settled-badge {
    background: rgba(4, 120, 87, 0.2);
    color: #34d399;
  }
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
}
:global(.dark) {
  .count-badge {
    background: rgba(59, 130, 246, 0.12);
    color: #60a5fa;
  }
}

// ── Shared atoms ─────────────────────────────────────────────────────────────
.mono {
  font-family: 'SF Mono', monospace, ui-monospace;
  font-size: 13px;
}
.gray {
  color: var(--el-text-color-regular, #475569);
}
.gray-sm {
  color: var(--el-text-color-secondary, #64748b);
  font-size: 12px;
}
.green {
  color: #059669;
}
.blue {
  color: #2563eb;
}
.red {
  color: #dc2626;
}
.amber {
  color: #d97706;
}
.white {
  color: var(--el-text-color-primary, #0f172a);
}
.gray-text {
  color: var(--el-text-color-secondary, #64748b);
}
.font-bold {
  font-weight: 700;
}

:global(.dark) {
  .green {
    color: #34d399;
  }
  .blue {
    color: #60a5fa;
  }
  .red {
    color: #f87171;
  }
  .amber {
    color: #fbbf24;
  }
  .white {
    color: #f3f4f6;
  }
  .gray {
    color: #94a3b8;
  }
}

// ── Clickable CHK links ───────────────────────────────────────────────────────
.chk-link {
  font-family: monospace, ui-monospace;
  font-size: 12px;
  font-weight: 700;
  color: #2563eb;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.15s;

  &:hover {
    color: #1d4ed8;
    background: rgba(59, 130, 246, 0.12);
    text-decoration: underline;
  }
  &.green {
    color: #059669;
    &:hover {
      color: #047857;
      background: rgba(16, 185, 129, 0.1);
    }
  }
}
:global(.dark) {
  .chk-link {
    color: #60a5fa;
    &:hover {
      color: #93c5fd;
    }
    &.green {
      color: #34d399;
      &:hover {
        color: #6ee7b7;
      }
    }
  }
}

// ── Repay form ────────────────────────────────────────────────────────────────
.repay-wrap {
  padding: 0 2px;
}

.repay-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-radius: 12px;
  background: var(--el-fill-color-light, #f8fafc);
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  margin-bottom: 2px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  .rh-label {
    font-size: 11px;
    color: var(--el-text-color-secondary, #64748b);
    margin-bottom: 3px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .rh-name {
    font-size: 20px;
    font-weight: 800;
    color: var(--el-text-color-primary, #0f172a);
  }
  .rh-debt {
    font-size: 28px;
    font-weight: 900;
    color: #ef4444;
    font-family: 'SF Mono', monospace;
  }
}

:global(.dark) {
  .repay-header {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(17, 24, 39, 0.9));
    border-color: rgba(239, 68, 68, 0.2);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    .rh-name {
      color: #f1f5f9;
    }
    .rh-debt {
      color: #f87171;
      text-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
    }
  }
}

.flabel {
  font-size: 13px;
  font-weight: 700;
  color: var(--el-text-color-primary, #0f172a);
}
.flabel-hint {
  font-size: 11px;
  font-weight: 400;
  color: var(--el-text-color-secondary, #64748b);
}

.pct-btns {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.amount-input {
  :deep(.el-input__inner) {
    color: #10b981 !important;
    font-family: 'SF Mono', monospace, ui-monospace;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.02em;
  }
}

// ── History dialog ────────────────────────────────────────────────────────────
.history-wrap {
  padding: 0 2px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.hist-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: var(--el-fill-color-light, #f8fafc);
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

:global(.dark) {
  .hist-header {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(17, 24, 39, 0.9));
    border-color: #1e293b;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  }
}

.hist-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.25));
  border: 2px solid rgba(239, 68, 68, 0.4);
  color: #ef4444;
  font-size: 22px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

:global(.dark) {
  .hist-avatar {
    background: linear-gradient(135deg, rgba(127, 29, 29, 0.7), rgba(185, 28, 28, 0.4));
    color: #fca5a5;
    box-shadow: 0 0 16px rgba(239, 68, 68, 0.2);
  }
}

.hist-name {
  font-size: 20px;
  font-weight: 800;
  color: var(--el-text-color-primary, #0f172a);
}
:global(.dark) .hist-name {
  color: #f1f5f9;
}
.hist-phone {
  font-size: 12px;
  color: var(--el-text-color-secondary, #64748b);
  font-family: monospace;
  margin-top: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.hist-debt-summary {
  display: flex;
  gap: 24px;
  align-items: center;
  margin-left: auto;
  .hds-item {
    text-align: right;
  }
  .hds-label {
    font-size: 10px;
    color: var(--el-text-color-secondary, #64748b);
    display: block;
    margin-bottom: 2px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .hds-val {
    font-size: 18px;
    font-weight: 800;
    font-family: 'SF Mono', monospace;
    &.blue {
      color: #3b82f6;
    }
    &.green {
      color: #10b981;
    }
    &.red {
      color: #ef4444;
    }
  }
}

.hist-section-title {
  display: flex;
  align-items: center;
  font-size: 11px;
  font-weight: 800;
  color: var(--el-text-color-secondary, #64748b);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
  padding: 0 2px;
  .hist-count {
    margin-left: 8px;
    font-size: 11px;
    font-weight: 500;
    color: var(--el-text-color-regular, #475569);
    text-transform: none;
    letter-spacing: 0;
    background: var(--el-fill-color, #e2e8f0);
    padding: 1px 8px;
    border-radius: 20px;
  }
}

.hist-empty {
  padding: 24px;
  text-align: center;
  color: var(--el-text-color-secondary, #64748b);
  font-size: 13px;
  background: var(--el-fill-color-light, #f8fafc);
  border-radius: 8px;
  border: 1px dashed var(--el-border-color-lighter, #e2e8f0);
}
.hist-section {
}

// ── Receipt detail ────────────────────────────────────────────────────────────
.receipt-detail {
  padding: 0 2px;
}

.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  .meta-box {
    background: var(--el-fill-color-light, #f8fafc);
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
    border-radius: 10px;
    padding: 12px 16px;
    transition: border-color 0.15s;
    &:hover {
      border-color: var(--el-color-primary-light-5);
    }
    .meta-label {
      font-size: 10px;
      color: var(--el-text-color-secondary, #64748b);
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.06em;
      margin-bottom: 4px;
    }
    .meta-val {
      font-size: 14px;
      font-weight: 700;
      color: var(--el-text-color-primary, #0f172a);
      &.blue {
        color: #3b82f6;
      }
      &.amber {
        color: #f59e0b;
      }
      &.green {
        color: #10b981;
      }
      &.mono {
        font-family: monospace;
      }
    }
  }
}

:global(.dark) {
  .meta-grid .meta-box {
    background: rgba(15, 23, 42, 0.7);
    border-color: #1e293b;
    .meta-val {
      color: #f1f5f9;
    }
  }
}

.fin-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-top: 14px;
  .fin-box {
    background: var(--el-fill-color-light, #f8fafc);
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
    border-radius: 10px;
    padding: 12px 14px;
    .fin-label {
      font-size: 10px;
      color: var(--el-text-color-secondary, #64748b);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 4px;
      font-weight: 600;
    }
    .fin-val {
      font-size: 18px;
      font-weight: 800;
      font-family: 'SF Mono', monospace;
      &.white {
        color: var(--el-text-color-primary, #0f172a);
      }
      &.amber {
        color: #f59e0b;
      }
      &.blue {
        color: #3b82f6;
      }
      &.red {
        color: #ef4444;
      }
      &.gray-text {
        color: #64748b;
      }
    }
  }
}

:global(.dark) {
  .fin-summary .fin-box {
    background: rgba(15, 23, 42, 0.7);
    border-color: #1e293b;
    .fin-val.white {
      color: #f1f5f9;
    }
  }
}

// ── Payment receipt card ──────────────────────────────────────────────────────
.pay-receipt-card {
  background: var(--el-bg-color-overlay, #ffffff);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  font-family: 'SF Mono', monospace, ui-monospace;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

:global(.dark) {
  .pay-receipt-card {
    background: linear-gradient(160deg, #080e1c 0%, #0d1528 100%);
    border-color: #1e293b;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  }
}

.pr-brand {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px dashed var(--el-border-color-lighter, #e2e8f0);
  .pr-brand-title {
    font-size: 13px;
    font-weight: 800;
    color: #3b82f6;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }
  .pr-receipt-no {
    font-size: 14px;
    font-weight: 700;
    color: #10b981;
    margin-top: 6px;
  }
}

:global(.dark) {
  .pr-brand {
    border-bottom-color: rgba(255, 255, 255, 0.08);
    .pr-brand-title {
      color: #93c5fd;
    }
    .pr-receipt-no {
      color: #34d399;
    }
  }
}

.pr-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
  .pr-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border-radius: 8px;
    background: var(--el-fill-color-light, #f8fafc);
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  }
  .pr-key {
    font-size: 11px;
    color: var(--el-text-color-secondary, #64748b);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .pr-val {
    font-size: 13px;
    font-weight: 700;
    color: var(--el-text-color-primary, #0f172a);
    font-family: monospace;
    &.white {
      color: var(--el-text-color-primary, #0f172a);
    }
    &.amber {
      color: #f59e0b;
    }
    &.green {
      color: #10b981;
    }
    &.mono {
      font-family: monospace;
    }
    &.gray-text {
      color: #64748b;
    }
  }
}

:global(.dark) {
  .pr-grid .pr-row {
    background: rgba(255, 255, 255, 0.03);
    border-color: rgba(255, 255, 255, 0.05);
    .pr-val {
      color: #cbd5e1;
      &.white {
        color: #f1f5f9;
      }
    }
  }
}

.pr-amount-highlight {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(16, 185, 129, 0.04));
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  margin-bottom: 16px;
  .prah-label {
    font-size: 11px;
    color: #10b981;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
    display: block;
  }
  .prah-amount {
    font-size: 40px;
    font-weight: 900;
    color: #10b981;
  }
}

.pr-remaining {
  text-align: center;
  font-size: 13px;
  padding-top: 10px;
  border-top: 1px dashed var(--el-border-color-lighter, #e2e8f0);
  color: var(--el-text-color-secondary, #64748b);
}
</style>
