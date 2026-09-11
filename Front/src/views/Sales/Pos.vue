<template>
  <div class="sales-page-container">
    <!-- Top Analytics Stat Cards -->
    <ContentWrap class="!mb-16px">
      <ElRow :gutter="16" class="stat-cards-row">
        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-info">
                <span class="stat-label">{{ t('erp.todaySales') }}</span>
                <div class="stat-number">
                  {{ stats.todayCount }} <span class="stat-unit">{{ t('erp.receiptsCount') }}</span>
                </div>
                <div class="text-[11px] text-gray-400 mt-2px">
                  Jami: {{ stats.allTimeCount || salesTotal }} ta chek
                </div>
              </div>
              <div class="stat-icon-wrapper">
                <Icon icon="ep:tickets" :size="20" />
              </div>
            </div>
          </div>
        </ElCol>

        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-info">
                <span class="stat-label">{{ t('erp.soldProducts') }}</span>
                <div class="stat-number">
                  {{ formatMoney(stats.todayItems) }}
                  <span class="stat-unit">{{ t('erp.itemsCount') }}</span>
                </div>
                <div v-if="stats.allTimeItems" class="text-[11px] text-gray-400 mt-2px">
                  Jami: {{ formatMoney(stats.allTimeItems) }} dona
                </div>
              </div>
              <div class="stat-icon-wrapper">
                <Icon icon="ep:box" :size="20" />
              </div>
            </div>
          </div>
        </ElCol>

        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-info">
                <span class="stat-label">{{ t('erp.todayGrossRevenue') }}</span>
                <div class="stat-number"> ${{ formatMoney(stats.todayRevenue) }} </div>
                <div v-if="stats.allTimeRevenue" class="text-[11px] text-gray-400 mt-2px">
                  Jami: ${{ formatMoney(stats.allTimeRevenue) }}
                </div>
              </div>
              <div class="stat-icon-wrapper">
                <Icon icon="ep:money" :size="20" />
              </div>
            </div>
          </div>
        </ElCol>

        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div
            class="stat-card cursor-pointer hover:shadow-md transition-shadow"
            @click="openAuthModal"
          >
            <div class="stat-content">
              <div class="stat-info">
                <div class="flex items-center justify-between">
                  <span class="stat-label">{{ t('erp.currentCashier') }}</span>
                  <ElTag type="info" size="small" effect="plain" class="rounded-pill font-bold">
                    {{ activeRole }}
                  </ElTag>
                </div>
                <div class="stat-number flex items-center gap-6px mt-4px">
                  <span class="truncate max-w-180px">{{ activeCashier }}</span>
                </div>
              </div>
              <div class="stat-icon-wrapper">
                <Icon icon="ep:avatar" :size="22" />
              </div>
            </div>
          </div>
        </ElCol>
      </ElRow>
    </ContentWrap>

    <!-- Main Sales History & POS Action Bar -->
    <ContentWrap>
      <div class="filter-action-bar">
        <ElForm
          :inline="true"
          :model="searchQuery"
          class="flex-1 flex flex-wrap items-center gap-12px"
        >
          <ElFormItem class="!mr-0">
            <ElInput
              v-model="searchQuery.search"
              :placeholder="t('erp.searchReceiptPlaceholder')"
              clearable
              class="search-input"
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
              :placeholder="t('erp.allPaymentMethods')"
              clearable
              class="payment-select"
            >
              <ElOption :label="t('erp.cash')" value="naqd" />
              <ElOption :label="t('erp.card')" value="karta" />
              <ElOption :label="t('erp.debt')" value="nasiya" />
            </ElSelect>
          </ElFormItem>

          <ElFormItem class="!mr-0">
            <ElButton type="primary" @click="handleSearch">
              <Icon icon="ep:search" class="mr-4px" />{{ t('common.search') }}</ElButton
            >
            <ElButton @click="resetSearch">{{ t('common.reset') }}</ElButton>
          </ElFormItem>
        </ElForm>

        <div class="action-buttons flex gap-12px">
          <ElButton type="primary" size="large" class="pos-open-btn" @click="openPosModal">
            <Icon icon="ep:plus" class="mr-6px" /> {{ t('erp.newPosSale') }}
          </ElButton>
        </div>
      </div>

      <!-- Main Sales History Table -->
      <div class="table-wrapper mt-16px">
        <ElTable
          v-loading="loadingSales"
          :data="salesList"
          style="width: 100%"
          max-height="600px"
          border
          stripe
        >
          <ElTableColumn prop="receipt_number" :label="t('erp.receiptNumber')" min-width="240">
            <template #default="scope">
              <ElTag type="info" effect="plain" class="font-mono font-bold">
                {{ scope.row.receipt_number }}
              </ElTag>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="created_at" :label="t('erp.dateTime')" min-width="180">
            <template #default="scope">
              <span class="font-mono text-13px text-[var(--el-text-color-regular)] font-medium">{{
                scope.row.created_at
              }}</span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="cashier_name" :label="t('erp.cashier')" min-width="180">
            <template #default="scope">
              <span class="font-bold text-[var(--el-text-color-primary)]">
                {{ scope.row.cashier_name || activeCashier }}
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="payment_method"
            :label="t('erp.paymentStatus')"
            min-width="180"
            align="center"
          >
            <template #default="scope">
              <div v-if="(scope.row.debt_amount || 0) > 0" class="py-2px">
                <ElTag type="danger" effect="plain" class="font-bold uppercase rounded-pill mb-2px">
                  {{ t('erp.debt').toUpperCase() }}
                </ElTag>
                <div class="text-12px text-red-500 font-mono font-bold">
                  {{ t('erp.debtAmountColon') }} ${{ formatMoney(scope.row.debt_amount) }}
                </div>
              </div>
              <div v-else class="py-2px">
                <ElTag
                  :type="
                    scope.row.payment_method === 'naqd'
                      ? 'success'
                      : scope.row.payment_method === 'karta'
                        ? 'warning'
                        : 'info'
                  "
                  effect="plain"
                  class="font-bold uppercase rounded-pill"
                >
                  {{ getPaymentLabel(scope.row.payment_method) }}
                </ElTag>
              </div>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="total_items"
            :label="t('erp.productQuantity')"
            min-width="140"
            align="center"
          >
            <template #default="scope">
              <ElTag type="info" effect="plain" class="font-bold font-mono">
                {{ scope.row.total_items }} {{ t('erp.itemsCount') }}
              </ElTag>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="total_amount"
            :label="t('erp.totalAmountDollar')"
            min-width="160"
            align="right"
          >
            <template #default="scope">
              <span class="font-mono font-extrabold text-[var(--el-text-color-primary)] text-15px"
                >${{ formatMoney(scope.row.total_amount) }}</span
              >
            </template>
          </ElTableColumn>

          <ElTableColumn :label="t('erp.receipt')" width="100" align="center" fixed="right">
            <template #default="scope">
              <ElButton
                size="small"
                type="primary"
                plain
                class="font-bold px-12px"
                @click.stop="openReceiptDetail(scope.row)"
              >
                {{ t('erp.chekShort') }}
              </ElButton>
            </template>
          </ElTableColumn>
        </ElTable>
      </div>

      <!-- Pagination -->
      <div class="mt-20px flex justify-end">
        <ElPagination
          v-model:current-page="pagination.pageIndex"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="salesTotal"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </ContentWrap>

    <!-- Branch Management & Selection Modal -->
    <ResizeDialog
      v-model="branchModalVisible"
      title="Do'kon Filiallarini Boshqarish va Tahrirlash"
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="500"
      :min-resize-height="350"
      class="branch-dialog-wrap"
    >
      <div class="branch-modal-body p-4px">
        <div class="flex justify-between items-center mb-12px">
          <span class="text-13px text-[var(--el-text-color-primary)] font-bold"
            >Tizimdagi Filiallar Ro'yxati:</span
          >
          <ElButton type="primary" size="small" class="font-bold" @click="openCreateBranchForm">
            + Yangi Filial Qo'shish
          </ElButton>
        </div>

        <!-- Branch Table -->
        <ElTable :data="branchList" border stripe size="small" class="mb-14px">
          <ElTableColumn prop="code" label="Kodi" width="110" align="center">
            <template #default="scope">
              <span class="font-mono text-blue-500 dark:text-blue-400 font-bold">{{
                scope.row.code
              }}</span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="name" label="Filial Nomi" min-width="180">
            <template #default="scope">
              <span class="font-bold text-[var(--el-text-color-primary)]">{{
                scope.row.name
              }}</span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="address" label="Manzili" min-width="180" show-overflow-tooltip />
          <ElTableColumn prop="phone" :label="t('erp.phone')" width="140" />
          <ElTableColumn :label="t('erp.amallar')" width="130" align="center">
            <template #default="scope">
              <ElButton size="small" type="primary" plain @click="editBranch(scope.row)">{{
                t('common.edit')
              }}</ElButton>
              <ElButton
                size="small"
                type="danger"
                plain
                class="!px-6px"
                @click="deleteBranch(scope.row.id!)"
              >
                ×
              </ElButton>
            </template>
          </ElTableColumn>
        </ElTable>

        <!-- Branch Edit / Create Form -->
        <div
          v-if="editingBranch"
          class="branch-edit-card bg-[var(--el-fill-color-light)] p-14px rounded-xl border border-[var(--el-border-color-lighter)] dark:border-gray-700"
        >
          <div class="text-14px font-bold text-emerald-500 mb-10px">
            {{ editingBranch.id ? "Filial Ma'lumotlarini Tahrirlash" : 'Yangi Filial Yaratish' }}
          </div>
          <ElForm label-position="top" size="small" class="grid grid-cols-2 gap-10px">
            <ElFormItem label="Filial Nomi">
              <ElInput v-model="editingBranch.name" placeholder="Masalan: Yunusobod Filiali" />
            </ElFormItem>
            <ElFormItem label="Filial Kodi / SKU">
              <ElInput v-model="editingBranch.code" placeholder="FIL-01" />
            </ElFormItem>
            <ElFormItem label="Manzili">
              <ElInput
                v-model="editingBranch.address"
                placeholder="Toshkent sh., Yunusobod 4-mavze"
              />
            </ElFormItem>
            <ElFormItem label="Telefon Raqami">
              <ElInput v-model="editingBranch.phone" placeholder="+998 71 200-11-22" />
            </ElFormItem>
          </ElForm>
          <div class="flex justify-end gap-8px mt-10px">
            <ElButton size="small" @click="editingBranch = null">{{ t('common.cancel') }}</ElButton>
            <ElButton
              size="small"
              type="primary"
              class="font-bold px-16px"
              @click="saveBranchForm"
              >{{ t('common.save') }}</ElButton
            >
          </div>
        </div>
      </div>
    </ResizeDialog>

    <!-- Built-in Employee Authentication & Switcher Modal -->
    <ResizeDialog
      v-model="authModalVisible"
      title="Xodimlarni Autentifikatsiya Qilish va Almashtirish"
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="500"
      :min-resize-height="350"
      class="auth-dialog-wrap"
    >
      <div class="auth-modal-content p-4px">
        <div class="mb-14px text-13px text-[var(--el-text-color-regular)]">
          Tizimda ish smenasini boshlash uchun xodim / kassir profilingizni tanlang va parolingizni
          kiriting:
        </div>

        <!-- Employee Selection Grid -->
        <div
          class="employee-grid grid grid-cols-2 sm:grid-cols-3 gap-10px mb-16px max-h-240px overflow-y-auto pr-4px"
        >
          <div
            v-for="emp in employeeList"
            :key="emp.username"
            :class="['employee-card', { active: selectedEmployee?.username === emp.username }]"
            @click="selectEmployee(emp)"
          >
            <div
              class="emp-avatar bg-gradient-to-br from-blue-600 to-indigo-700 text-white font-bold text-16px rounded-full w-42px h-42px flex items-center justify-center shadow"
            >
              {{ emp.initials }}
            </div>
            <div class="emp-info min-w-0 flex-1">
              <div
                class="emp-name font-bold text-13px text-[var(--el-text-color-primary)] truncate"
                >{{ emp.full_name }}</div
              >
              <div
                class="emp-sub text-11px text-[var(--el-text-color-secondary)] font-mono flex justify-between items-center mt-2px"
              >
                <span class="truncate">{{ emp.username }}</span>
                <span
                  class="text-amber-500 font-semibold px-4px py-1px bg-[var(--el-fill-color)] rounded text-10px"
                  >{{ emp.role }}</span
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Authentication Form -->
        <div
          v-if="selectedEmployee"
          class="auth-form-box bg-[var(--el-fill-color-light)] p-16px rounded-xl border border-[var(--el-border-color-lighter)] dark:border-gray-700"
        >
          <div
            class="flex justify-between items-center mb-12px pb-8px border-b border-[var(--el-border-color-lighter)] dark:border-gray-800"
          >
            <span class="text-13px text-[var(--el-text-color-regular)] font-semibold">
              Tanlangan Xodim:
              <b class="text-emerald-500 font-bold text-15px">{{ selectedEmployee.full_name }}</b>
            </span>
            <ElTag type="warning" effect="dark" size="small" class="font-bold">
              {{ selectedEmployee.role }}
            </ElTag>
          </div>

          <ElForm label-position="top" size="large" @submit.prevent="handleAuthSubmit">
            <ElFormItem label="Xodim Paroli / PIN Kodi">
              <ElInput
                v-model="authForm.password"
                type="password"
                show-password
                placeholder="Parol kiriting (masalan: 123456 yoki admin)"
                class="auth-pass-input"
                @keyup.enter="handleAuthSubmit"
              />
            </ElFormItem>

            <ElButton
              type="primary"
              size="large"
              class="w-full font-bold auth-btn inline-flex items-center justify-center"
              :loading="authenticating"
              @click="handleAuthSubmit"
            >
              <Icon icon="ep:lock" class="mr-6px" />
              <span>TIZIMGA KIRISH (LOGIN)</span>
            </ElButton>
          </ElForm>
        </div>
      </div>
    </ResizeDialog>

    <!-- Built-in Resizable & Draggable POS Kassa Modal -->
    <ResizeDialog
      v-model="posModalVisible"
      :title="t('erp.newSaleRegister')"
      :init-width="posDialogInitWidth"
      :init-height="posDialogInitHeight"
      :min-resize-width="850"
      :min-resize-height="550"
      :auto-height="false"
      class="pos-dialog-wrap"
    >
      <div class="pos-dialog-body flex flex-col h-full">
        <ElRow :gutter="16" class="flex-1 min-h-0">
          <!-- Left Panel: Barcode Scanner & Product Catalog Table -->
          <ElCol :xs="24" :lg="16" class="flex flex-col h-full">
            <div class="pos-left-panel flex flex-col h-full">
              <!-- Scanner Bar with Batch Quantity Input -->
              <div class="mb-10px flex-shrink-0 flex gap-8px items-center">
                <div
                  class="flex items-center bg-[var(--el-fill-color-light)] dark:bg-gray-800 rounded-lg px-8px border border-[var(--el-border-color)] dark:border-gray-700 h-32px"
                >
                  <span class="text-11px text-[var(--el-text-color-secondary)] mr-6px font-bold">{{
                    t('erp.quantity')
                  }}</span>
                  <input
                    :value="scanQuantity"
                    type="text"
                    inputmode="numeric"
                    class="bg-transparent text-[var(--el-text-color-primary)] font-mono font-bold text-13px w-60px outline-none border-none text-center"
                    placeholder="1"
                    @focus="selectText"
                    @click="selectText"
                    @input="onScanQuantityInput"
                    @blur="validateScanQuantity"
                    @keyup.enter="validateScanQuantity"
                  />
                </div>
                <ElInput
                  ref="barcodeInputRef"
                  v-model="barcodeSearch"
                  :placeholder="t('erp.scanOrSearchPlaceholder')"
                  clearable
                  size="default"
                  class="pos-scanner-input flex-1"
                  @keyup.enter="handleBarcodeScan"
                >
                  <template #append>
                    <ElButton type="primary" @click="handleBarcodeScan">
                      + {{ t('common.add') }}
                    </ElButton>
                  </template>
                </ElInput>
              </div>

              <!-- Simple Category Filter Pills -->
              <div class="category-pills mb-10px flex flex-wrap gap-6px flex-shrink-0">
                <span
                  v-for="cat in categories"
                  :key="cat"
                  :class="['category-pill', { active: selectedCategory === cat }]"
                  @click="selectedCategory = cat"
                >
                  {{ t(cat) }}
                </span>
              </div>

              <!-- Product Picker Table with Rich Row Colouring for Selected Items -->
              <div class="pos-products-table-wrap flex-1 min-h-0">
                <ElTable
                  v-loading="loadingProducts"
                  :data="filteredProducts"
                  :row-class-name="tableRowClassName"
                  style="width: 100%; height: 100%"
                  border
                  stripe
                  size="small"
                  class="pos-product-picker-table"
                  @row-click="(row) => addToCart(row)"
                >
                  <ElTableColumn :label="t('erp.barcodeOrBrand')" width="170">
                    <template #default="scope">
                      <div class="font-mono text-11px text-blue-500 font-bold">
                        {{ scope.row.shtrix_code || scope.row.SKU || '—' }}
                      </div>
                      <span
                        v-if="scope.row.brand_name"
                        class="text-10px text-[var(--el-text-color-secondary)] block mt-2px"
                      >
                        {{ scope.row.brand_name }}
                      </span>
                    </template>
                  </ElTableColumn>

                  <ElTableColumn prop="productName" :label="t('erp.productName')" min-width="240">
                    <template #default="scope">
                      <div class="flex items-center gap-8px">
                        <ElImage
                          v-if="getProductMainImage(scope.row)"
                          :src="getProductMainImage(scope.row)"
                          :preview-src-list="getProductImageGallery(scope.row)"
                          preview-teleported
                          fit="cover"
                          class="w-32px h-32px rounded-6px flex-shrink-0 border border-gray-700 cursor-pointer hover:scale-110 transition-transform"
                        >
                          <template #error>
                            <img
                              :src="getProductFallbackAvatar(scope.row.productName)"
                              :alt="scope.row.productName"
                              @error="handleImageError($event, scope.row.productName)"
                              class="w-32px h-32px rounded-6px object-cover border border-gray-700 flex-shrink-0"
                            />
                          </template>
                        </ElImage>
                        <img
                          v-else
                          :src="getProductFallbackAvatar(scope.row.productName)"
                          :alt="scope.row.productName"
                          @error="handleImageError($event, scope.row.productName)"
                          class="w-32px h-32px rounded-6px object-cover border border-gray-700 flex-shrink-0"
                        />
                        <div
                          class="font-semibold text-13px text-[var(--el-text-color-primary)] leading-snug truncate"
                          :title="scope.row.productName"
                        >
                          {{ scope.row.productName }}
                        </div>
                      </div>
                    </template>
                  </ElTableColumn>

                  <ElTableColumn
                    prop="quantityInStock"
                    :label="t('erp.availableStock')"
                    width="135"
                    align="center"
                  >
                    <template #default="scope">
                      <ElTag
                        :type="
                          (scope.row.quantityInStock || 0) > 10
                            ? 'success'
                            : (scope.row.quantityInStock || 0) > 0
                              ? 'warning'
                              : 'danger'
                        "
                        effect="dark"
                        size="small"
                        class="font-mono font-bold text-11px rounded-pill"
                      >
                        {{ formatMoney(scope.row.quantityInStock) }}
                        {{ scope.row.unit || t('erp.itemsCount') }}
                      </ElTag>
                    </template>
                  </ElTableColumn>

                  <ElTableColumn
                    prop="price"
                    :label="t('erp.sellingPriceDollar')"
                    width="140"
                    align="right"
                  >
                    <template #default="scope">
                      <span class="font-bold text-emerald-500 font-mono text-14px"
                        >${{ formatMoney(scope.row.price) }}</span
                      >
                    </template>
                  </ElTableColumn>

                  <ElTableColumn :label="t('common.add')" width="95" align="center">
                    <template #default="scope">
                      <ElButton
                        size="small"
                        type="primary"
                        class="font-bold px-8px"
                        @click.stop="addToCart(scope.row)"
                      >
                        + {{ scanQuantity > 1 ? scanQuantity : '' }}
                      </ElButton>
                    </template>
                  </ElTableColumn>
                </ElTable>
              </div>
            </div>
          </ElCol>

          <!-- Right Panel: Cart & Checkout -->
          <ElCol :xs="24" :lg="8" class="flex flex-col h-full">
            <div class="pos-cart-panel flex flex-col justify-between h-full">
              <!-- Cart Header -->
              <div
                class="cart-header flex justify-between items-center mb-8px pb-8px border-b border-[var(--el-border-color-lighter)] dark:border-gray-700 flex-shrink-0"
              >
                <div class="flex items-center gap-8px">
                  <span class="font-bold text-14px text-[var(--el-text-color-primary)]">{{
                    t('erp.cartPosKassa')
                  }}</span>
                </div>
                <ElButton
                  v-if="cart.length > 0"
                  type="danger"
                  size="small"
                  text
                  @click="clearCart"
                  >{{ t('common.reset') }}</ElButton
                >
              </div>

              <!-- Cart Items List with Strict Real-time Stock Enforcement -->
              <div class="cart-items-container flex-1 min-h-0 overflow-y-auto mb-10px">
                <div
                  v-for="(item, idx) in cart"
                  :key="item.product_id + '_' + (item.unit_name || '')"
                  class="cart-item-row"
                >
                  <div class="item-info flex-1 pr-8px min-w-0">
                    <div
                      class="item-title font-semibold text-13px text-[var(--el-text-color-primary)] leading-snug break-words flex items-center gap-6px flex-wrap"
                    >
                      <span>{{ item.product_name }}</span>
                      <ElTag
                        v-if="item.unit_name"
                        type="primary"
                        size="small"
                        effect="dark"
                        class="font-mono text-10px px-6px rounded-pill"
                      >
                        {{ item.unit_name }}
                      </ElTag>
                    </div>

                    <!-- Unit Switcher (only shown if product has packaging options) -->
                    <div
                      v-if="getItemPackagings(item.product_id).length > 1"
                      class="mt-4px flex items-center gap-6px"
                    >
                      <span class="text-11px text-[var(--el-text-color-secondary)]"
                        >{{ t('erp.unit') }}:</span
                      >
                      <ElSelect
                        :model-value="item.unit_name || getItemUnit(item.product_id).toUpperCase()"
                        size="small"
                        class="w-150px text-11px"
                        @change="(val: string) => handleCartUnitChange(idx, val)"
                      >
                        <ElOption
                          v-for="pkg in getItemPackagings(item.product_id)"
                          :key="pkg.unit_name"
                          :label="`${pkg.unit_name} ($${formatMoney(pkg.price)})`"
                          :value="pkg.unit_name"
                        />
                      </ElSelect>
                    </div>

                    <div
                      class="item-sub text-11px text-[var(--el-text-color-secondary)] font-mono mt-3px"
                    >
                      ${{ formatMoney(item.price) }} × {{ item.quantity || 0 }} =
                      <span class="text-emerald-500 font-bold text-13px"
                        >${{
                          formatMoney(item.price * (parseFloat(String(item.quantity)) || 0))
                        }}</span
                      >
                      <span
                        v-if="item.conversion_factor && item.conversion_factor > 1"
                        class="text-blue-500 text-10px block mt-1px font-sans"
                      >
                        ({{ t('erp.warehouseUsage') }}:
                        {{
                          formatMoney(
                            (parseFloat(String(item.quantity)) || 0) * item.conversion_factor
                          )
                        }}
                        {{ getItemUnit(item.product_id) }})
                      </span>
                    </div>
                  </div>

                  <div class="item-qty-controls flex items-center gap-3px flex-shrink-0">
                    <ElButton size="small" circle @click.stop="decreaseQty(idx)">-</ElButton>

                    <input
                      :value="item.quantity"
                      type="text"
                      inputmode="decimal"
                      class="qty-direct-input font-bold font-mono text-center text-[var(--el-text-color-primary)] text-13px bg-[var(--el-fill-color-blank)] border border-[var(--el-border-color)] rounded px-4px py-2px w-65px outline-none focus:border-blue-500"
                      placeholder="1"
                      @focus="selectText"
                      @click="selectText"
                      @input="onItemQtyInput(idx, $event)"
                      @blur="validateItemQty(idx)"
                      @keyup.enter="validateItemQty(idx)"
                      @click.stop
                    />

                    <ElButton size="small" circle @click.stop="increaseQty(idx)">+</ElButton>
                    <ElButton
                      size="small"
                      type="danger"
                      circle
                      plain
                      class="ml-4px"
                      @click.stop="removeFromCart(idx)"
                    >
                      ×
                    </ElButton>
                  </div>
                </div>

                <div v-if="cart.length === 0" class="empty-cart-placeholder">
                  <div class="text-[var(--el-text-color-secondary)] font-semibold text-13px">{{
                    t('erp.cartEmpty')
                  }}</div>
                  <div class="text-[var(--el-text-color-placeholder)] text-11px mt-2px">{{
                    t('erp.pickProductHint')
                  }}</div>
                </div>
              </div>

              <!-- Checkout Controls Anchored at Bottom -->
              <div
                class="cart-checkout-section pt-8px border-t border-[var(--el-border-color-lighter)] dark:border-gray-700 flex-shrink-0"
              >
                <!-- Payment Method Selector (Clean 3-column Grid) -->
                <div class="mb-8px">
                  <label
                    class="block text-11px text-[var(--el-text-color-regular)] mb-4px font-semibold flex justify-between"
                  >
                    <span>{{ t('erp.selectPaymentMethod') }}</span>
                    <span class="text-blue-500 font-mono">{{
                      getPaymentLabel(checkoutForm.payment_method)
                    }}</span>
                  </label>
                  <div class="grid grid-cols-3 gap-6px">
                    <div
                      v-for="pm in paymentMethods"
                      :key="pm.key"
                      :class="[
                        'payment-method-card',
                        { active: checkoutForm.payment_method === pm.key }
                      ]"
                      @click="setPaymentMethod(pm.key as any)"
                    >
                      <Icon :icon="pm.icon" class="text-14px mr-4px" />
                      <span class="text-12px font-bold">{{ pm.label }}</span>
                    </div>
                  </div>
                </div>

                <!-- Paid Amount Input: ONLY SHOWS WHEN NASIYA / QARZ IS SELECTED -->
                <div
                  v-if="checkoutForm.payment_method === 'nasiya'"
                  class="mb-8px flex justify-between items-center bg-[var(--el-fill-color-light)] p-6px px-8px rounded-lg border border-[var(--el-border-color-lighter)] dark:border-gray-700"
                >
                  <span class="text-12px text-[var(--el-text-color-primary)] font-bold">{{
                    t('erp.paidAmountDollar')
                  }}</span>
                  <div class="flex items-center gap-4px">
                    <ElInput
                      v-model="displayPaidAmount"
                      placeholder="0"
                      style="width: 120px"
                      size="small"
                    />
                    <ElButton
                      size="small"
                      type="primary"
                      plain
                      class="text-10px px-6px"
                      @click="setFullPaid"
                      >{{ t('erp.fullPaid') }}</ElButton
                    >
                  </div>
                </div>

                <!-- Debtor / Customer Selection Input (ONLY FOR NASIYA) -->
                <div
                  v-if="checkoutForm.payment_method === 'nasiya'"
                  class="mb-8px p-8px rounded-lg bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-500/50 space-y-6px"
                >
                  <div
                    class="flex justify-between items-center text-11px font-bold text-red-600 dark:text-red-300"
                  >
                    <span>{{ t('erp.debtorCustomerName') }}</span>
                    <span v-if="selectedDebtorInfo" class="text-amber-500 font-mono text-11px">
                      {{ t('erp.oldDebtColon') }} ${{ formatMoney(selectedDebtorInfo.total_debt) }}
                    </span>
                  </div>

                  <ElSelect
                    v-model="checkoutForm.customer_name"
                    filterable
                    allow-create
                    default-first-option
                    :placeholder="t('erp.searchCustomerPlaceholder')"
                    size="small"
                    style="width: 100%"
                    @change="handleDebtorSelect"
                  >
                    <ElOption
                      v-for="d in debtorOptionsList"
                      :key="d.name"
                      :label="d.label"
                      :value="d.name"
                    />
                  </ElSelect>

                  <div
                    v-if="calculatedDebt > 0"
                    class="flex justify-between items-center text-12px pt-4px border-t border-red-200 dark:border-red-900/60"
                  >
                    <span class="text-red-600 dark:text-red-300 font-bold">{{
                      t('erp.newDebtAmount')
                    }}</span>
                    <span class="text-red-600 dark:text-red-400 font-mono font-bold text-15px"
                      >${{ formatMoney(calculatedDebt) }}</span
                    >
                  </div>
                </div>

                <!-- Total Summary -->
                <div class="total-summary-box mb-8px">
                  <div
                    class="flex justify-between items-center text-12px text-[var(--el-text-color-regular)] mb-4px"
                  >
                    <span>{{ t('erp.totalProducts') }}</span>
                    <span class="font-mono font-bold text-[var(--el-text-color-primary)]"
                      >${{ formatMoney(subtotal) }}</span
                    >
                  </div>
                  <div
                    class="flex justify-between items-center text-12px text-[var(--el-text-color-regular)] mb-6px"
                  >
                    <span>{{ t('erp.discountDollar') }}</span>
                    <ElInputNumber
                      v-model="checkoutForm.discount"
                      :min="0"
                      size="small"
                      style="width: 100px"
                    />
                  </div>
                  <div
                    class="flex justify-between items-center text-14px font-bold text-[var(--el-text-color-primary)] pt-4px border-t border-[var(--el-border-color-lighter)] dark:border-gray-700"
                  >
                    <span>{{ t('erp.totalPayment') }}</span>
                    <span class="text-emerald-500 font-mono text-20px font-bold"
                      >${{ formatMoney(grandTotal) }}</span
                    >
                  </div>
                </div>

                <ElButton
                  type="primary"
                  size="large"
                  class="w-full checkout-submit-btn"
                  :disabled="cart.length === 0"
                  :loading="submittingCheckout"
                  @click="handleCheckout"
                >
                  {{ t('erp.completeSale') }} (${{ formatMoney(grandTotal) }})
                </ElButton>
              </div>
            </div>
          </ElCol>
        </ElRow>
      </div>
    </ResizeDialog>

    <!-- Built-in Resizable & Draggable Receipt Print Modal -->
    <ResizeDialog
      v-model="receiptModalVisible"
      :title="t('erp.salesReceipt')"
      storage-key="sales_receipt_auto_fit_v4"
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="550"
      :min-resize-height="400"
      class="receipt-dialog-wrap"
    >
      <div
        v-if="selectedSale"
        id="receiptPrintArea"
        class="receipt-large-card font-mono"
        v-loading="receiptLoading"
      >
        <!-- Header Branding & Receipt Number -->
        <div
          class="receipt-header-branding text-center mb-16px pb-12px border-b-2 border-[var(--el-border-color)] dark:border-gray-700"
        >
          <div
            class="text-center font-bold text-22px text-[var(--el-text-color-primary)] tracking-wider uppercase"
          >
            OMBORXONA ERP POS
          </div>
          <div class="text-center text-12px text-[var(--el-text-color-secondary)] mt-2px">
            Filial:
            <span class="font-bold text-[var(--el-text-color-primary)]">{{
              activeBranchName
            }}</span>
          </div>
          <div
            class="inline-block bg-emerald-500/10 dark:bg-emerald-500/20 border border-emerald-500/30 px-12px py-4px rounded-full text-15px text-emerald-500 font-bold mt-8px"
          >
            CHEK #{{ selectedSale.receipt_number }}
          </div>
        </div>

        <!-- Spaced 5px Dashed Box for Metadata -->
        <div
          class="spaced-dashed-box text-14px mb-16px space-y-6px text-[var(--el-text-color-primary)]"
        >
          <div class="flex justify-between items-center">
            <span class="text-[var(--el-text-color-secondary)]">{{ t('erp.dateTimeColon') }}</span>
            <span class="font-bold text-[var(--el-text-color-primary)] font-mono">{{
              selectedSale.created_at
            }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-[var(--el-text-color-secondary)]">{{
              t('erp.cashierWorkerColon')
            }}</span>
            <span class="font-bold text-blue-500">{{
              selectedSale.cashier_name || activeCashier
            }}</span>
          </div>
          <div v-if="selectedSale.customer_name" class="flex justify-between items-center">
            <span class="text-[var(--el-text-color-secondary)]">Mijoz:</span>
            <span class="font-bold text-purple-500">{{ selectedSale.customer_name }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-[var(--el-text-color-secondary)]">{{
              t('erp.paymentMethodColon')
            }}</span>
            <span
              class="uppercase font-bold text-emerald-500 text-15px px-8px py-2px rounded bg-emerald-500/10 border border-emerald-500/20"
            >
              {{ getPaymentLabel(selectedSale.payment_method) }}
            </span>
          </div>
        </div>

        <!-- Receipt Line Items Table with clear Count, Unit Price, and Total -->
        <div class="receipt-items-section mb-16px">
          <div
            class="flex items-center font-bold text-12px text-[var(--el-text-color-secondary)] pb-8px border-b-2 border-[var(--el-border-color)] mb-8px uppercase tracking-wider"
          >
            <span class="w-32px text-center">#</span>
            <span class="flex-1 px-8px">MAHSULOT NOMI</span>
            <span class="w-130px text-center">SONI</span>
            <span class="w-120px text-right">NARXI</span>
            <span class="w-130px text-right">SUMMA</span>
          </div>

          <div
            v-if="selectedSale.items && selectedSale.items.length > 0"
            class="divide-y divide-[var(--el-border-color-lighter)]"
          >
            <div
              v-for="(item, idx) in selectedSale.items"
              :key="item.id || idx"
              class="flex items-center py-8px text-14px hover:bg-emerald-500/5 px-4px rounded transition-colors"
            >
              <span class="w-32px text-center text-12px text-gray-400 font-mono flex-shrink-0">{{
                idx + 1
              }}</span>
              <div class="flex-1 px-8px min-w-0">
                <span
                  class="font-bold text-[var(--el-text-color-primary)] leading-snug break-words block text-14px"
                >
                  {{ item.product_name }}
                </span>
                <div class="flex items-center gap-6px mt-2px text-11px">
                  <span v-if="item.shtrix_code" class="text-gray-400 font-mono text-10px">
                    {{ item.shtrix_code }}
                  </span>
                  <span
                    v-if="item.unit_name"
                    class="text-blue-500 font-bold bg-blue-500/10 px-6px py-0.5 rounded text-10px"
                  >
                    {{ item.unit_name }}
                  </span>
                </div>
              </div>
              <span
                class="w-130px text-center font-mono font-bold text-[var(--el-text-color-primary)] flex-shrink-0"
              >
                {{ formatMoney(item.quantity) }} {{ item.unit_name || 'dona' }}
              </span>
              <span
                class="w-120px text-right font-mono text-[var(--el-text-color-regular)] flex-shrink-0 text-13px"
              >
                ${{ formatMoney(item.price) }}
              </span>
              <span
                class="w-130px text-right font-mono font-bold text-emerald-500 flex-shrink-0 text-15px"
              >
                ${{ formatMoney(item.total || item.quantity * item.price) }}
              </span>
            </div>
          </div>
          <div
            v-else-if="!receiptLoading"
            class="text-center py-24px text-gray-400 text-13px bg-gray-500/5 rounded-8px"
          >
            <Icon icon="ep:info-filled" class="text-22px mb-6px text-amber-500 mx-auto block" />
            <div>Chekda mahsulotlar topilmadi</div>
          </div>
        </div>

        <!-- Spaced Dashed Divider -->
        <div class="spaced-dashed-divider"></div>

        <!-- Financial Summary -->
        <div class="receipt-financial-summary pt-6px space-y-6px text-15px">
          <div class="flex justify-between text-14px text-[var(--el-text-color-secondary)]">
            <span>Jami mahsulotlar soni:</span>
            <span class="font-mono font-bold text-[var(--el-text-color-primary)]">
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
            class="flex justify-between text-amber-500 text-15px"
          >
            <span>{{ t('erp.discountColon') }}</span>
            <span class="font-mono font-bold">-${{ formatMoney(selectedSale.discount) }}</span>
          </div>
          <div
            class="flex justify-between items-center font-bold text-20px text-[var(--el-text-color-primary)] pt-8px pb-8px border-y-2 border-[var(--el-border-color)] my-8px"
          >
            <span>{{ t('erp.totalSumUpper') }}</span>
            <span class="text-emerald-500 text-26px font-mono font-bold"
              >${{ formatMoney(selectedSale.total_amount) }}</span
            >
          </div>
          <div class="flex justify-between text-14px text-[var(--el-text-color-regular)]">
            <span>{{ t('erp.paidAmountColon') }}</span>
            <span class="font-mono font-bold text-[var(--el-text-color-primary)] text-16px">
              ${{
                formatMoney(
                  selectedSale.paid_amount !== undefined && selectedSale.paid_amount !== null
                    ? selectedSale.paid_amount
                    : selectedSale.total_amount
                )
              }}
            </span>
          </div>
          <div
            v-if="(selectedSale.debt_amount || 0) > 0"
            class="flex justify-between items-center text-15px text-red-500 font-bold bg-red-50 dark:bg-red-950/80 p-10px rounded-lg border border-red-200 dark:border-red-500/60 mt-8px"
          >
            <span>{{ t('erp.debtNasiyaColon').toUpperCase() }}</span>
            <span class="font-mono text-20px">${{ formatMoney(selectedSale.debt_amount) }}</span>
          </div>
        </div>

        <div
          class="text-center text-13px text-[var(--el-text-color-secondary)] mt-18px pt-10px border-t border-[var(--el-border-color-lighter)] tracking-wide font-sans"
        >
          {{ t('erp.thankYouEnjoy') }}
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-between flex-wrap gap-12px">
          <div class="flex items-center gap-8px">
            <ElTag v-if="selectedSale" type="success" effect="plain" class="font-bold">
              {{ (selectedSale.items || []).length }} xil mahsulot ({{
                (selectedSale.items || []).reduce(
                  (acc: number, it: any) => acc + (Number(it.quantity) || 1),
                  0
                )
              }}
              dona)
            </ElTag>
          </div>
          <div class="flex items-center gap-10px">
            <ElButton
              type="primary"
              size="large"
              class="font-bold px-18px"
              @click="() => printReceipt('thermal')"
            >
              <Icon icon="ep:printer" class="mr-6px" /> Termal Chek (80mm)
            </ElButton>
            <ElButton
              type="success"
              plain
              size="large"
              class="font-bold px-18px"
              @click="() => printReceipt('a4')"
            >
              <Icon icon="ep:document" class="mr-6px" /> Standart (A4)
            </ElButton>
            <ElButton size="large" @click="receiptModalVisible = false">{{
              t('common.close')
            }}</ElButton>
          </div>
        </div>
      </template>
    </ResizeDialog>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
defineOptions({ name: 'SalesPos' })
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ContentWrap } from '@/components/ContentWrap'
import { ResizeDialog } from '@/components/Dialog'
import { Icon } from '@/components/Icon'
import { useUserStoreWithOut } from '@/store/modules/user'
import {
  ElRow,
  ElCol,
  ElButton,
  ElTable,
  ElTableColumn,
  ElTag,
  ElPagination,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElSelect,
  ElOption,
  ElMessage,
  ElMessageBox,
  ElNotification,
  ElImage
} from 'element-plus'

import { getProductListApi, ProductType } from '@/api/product'
import {
  getSalesListApi,
  checkoutSaleApi,
  getSaleReceiptApi,
  SaleItemType,
  SaleType
} from '@/api/sales'
import { getEmployeesAuthApi, loginApi } from '@/api/login'
import { getBranchListApi, saveBranchApi, deleteBranchApi, BranchType } from '@/api/branch'
import {
  getProductMainImage,
  getProductImageGallery,
  getProductFallbackAvatar,
  handleImageError
} from '@/utils/productImages'
import { useEventBus } from '@/hooks/event/useEventBus'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'
import { soundEffects } from '@/utils/soundEffects'
import { offlineQueue } from '@/utils/offlineQueue'

const dialogInitWidth = Math.min(window.innerWidth * 0.92, 1400)
const dialogInitHeight = Math.min(window.innerHeight * 0.88, 800)
const posDialogInitWidth = Math.min(window.innerWidth * 0.95, 1500)
const posDialogInitHeight = Math.min(window.innerHeight * 0.92, 850)

const userStore = useUserStoreWithOut()

const activeCashier = computed(() => {
  const info = userStore.getUserInfo
  return info?.full_name || info?.username || 'Kassir_Sardor'
})

const activeRole = computed(() => {
  const info = userStore.getUserInfo
  return info?.role || 'Kassir'
})

const loadingSales = ref(false)
const loadingProducts = ref(false)
const submittingCheckout = ref(false)
const posModalVisible = ref(false)
const receiptModalVisible = ref(false)
const receiptLoading = ref(false)
const barcodeInputRef = ref<any>(null)

// Branch Management & Selection State
const branchList = ref<BranchType[]>([])
const selectedBranchId = ref<string>('')
const branchModalVisible = ref(false)
const editingBranch = ref<BranchType | null>(null)

const activeBranchName = computed(() => {
  const b = branchList.value.find((item) => item.id === selectedBranchId.value)
  return b ? b.name : 'Bosh Filial'
})

// Employee Authentication & Switcher State
const authModalVisible = ref(false)
const authenticating = ref(false)
const employeeList = ref<any[]>([])
const selectedEmployee = ref<any>(null)
const authForm = reactive({
  password: ''
})

const barcodeSearch = ref('')
const scanQuantity = ref<any>(1)
const selectedCategory = ref('Barchasi')

const products = ref<ProductType[]>([])
const salesList = ref<SaleType[]>([])
const salesTotal = ref(0)
const selectedSale = ref<SaleType | null>(null)

const categories = [
  'Barchasi',
  'Ichimliklar va suvlar',
  'Sut va sut mahsulotlari',
  'Tuz va ziravorlar',
  'Plastmassa va idishlar',
  'Oziq-ovqat mahsulotlari'
]

const paymentMethods = computed(() => [
  { key: 'naqd', label: t('erp.cash'), icon: 'ep:money' },
  { key: 'karta', label: t('erp.card'), icon: 'ep:credit-card' },
  { key: 'nasiya', label: t('erp.debt'), icon: 'ep:document' }
])

const getPaymentLabel = (method?: string) => {
  if (!method || method === 'naqd') return t('erp.cash').toUpperCase()
  if (method === 'karta') return t('erp.card').toUpperCase()
  if (method === 'nasiya') return t('erp.debt').toUpperCase()
  return method.toUpperCase()
}

const fetchBranches = async () => {
  try {
    const res: any = await getBranchListApi()
    const list = Array.isArray(res) ? res : res?.data?.list || res?.data || []
    branchList.value = list
    if (list.length > 0 && !selectedBranchId.value) {
      selectedBranchId.value = list[0].id!
    }
  } catch (err) {
    console.error('Failed to fetch branches', err)
  }
}

const openCreateBranchForm = () => {
  editingBranch.value = {
    name: '',
    code: `FIL-0${branchList.value.length + 1}`,
    address: '',
    phone: ''
  }
}

const editBranch = (b: BranchType) => {
  editingBranch.value = { ...b }
}

const saveBranchForm = async () => {
  if (!editingBranch.value || !editingBranch.value.name.trim()) {
    ElMessage.warning('Filial nomini kiriting!')
    return
  }
  try {
    const res: any = await saveBranchApi(editingBranch.value)
    if (res && (res.code === 0 || res.data)) {
      ElMessage.success(res.message || 'Filial muvaffaqiyatli saqlandi')
      editingBranch.value = null
      fetchBranches()
    }
  } catch (err: any) {
    ElMessage.error(err?.message || 'Filialni saqlashda xatolik!')
  }
}

const deleteBranch = async (bId: string) => {
  try {
    const res = await deleteBranchApi(bId)
    if (res && res.code === 0) {
      ElMessage.success("Filial o'chirildi")
      if (selectedBranchId.value === bId) {
        selectedBranchId.value = ''
      }
      fetchBranches()
    }
  } catch (err: any) {
    ElMessage.error("Filialni o'chirishda xatolik!")
  }
}

const getCartItemQty = (productId?: string) => {
  if (!productId) return 0
  const found = cart.value.find((c) => c.product_id === productId)
  return found ? found.quantity : 0
}

const tableRowClassName = ({ row }: { row: ProductType }) => {
  const qty = getCartItemQty(row.id)
  return qty > 0 ? 'selected-cart-row' : ''
}

const openAuthModal = async () => {
  authModalVisible.value = true

  authForm.password = ''
  try {
    const res = await getEmployeesAuthApi()
    if (res && res.data) {
      employeeList.value = res.data
      if (res.data.length > 0) {
        selectedEmployee.value = res.data[0]
      }
    }
  } catch (err) {
    console.error('Failed to load employee list', err)
  }
}

const selectEmployee = (emp: any) => {
  selectedEmployee.value = emp
  authForm.password = ''
}

const handleAuthSubmit = async () => {
  if (!selectedEmployee.value) return
  authenticating.value = true
  try {
    const res: any = await loginApi({
      username: selectedEmployee.value.username,
      password: authForm.password || '123456'
    })

    if (res && res.data) {
      userStore.setUserInfo(res.data)
      if (res.data.token) {
        userStore.setToken(res.data.token)
      }

      ElNotification({
        title: 'Xodim Muvaffaqiyatli Almashtirildi!',
        message: `Xodim: ${res.data.full_name || res.data.username} (${res.data.role || 'Kassir'}) | Smena faollashtirildi`,
        type: 'success',
        duration: 4000
      })

      authModalVisible.value = false
    }
  } catch (err: any) {
    const msg = err?.response?.data?.message || "Autentifikatsiya paroli noto'g'ri!"
    ElMessage.error(msg)
  } finally {
    authenticating.value = false
  }
}

// High-visibility Stock Warning Popup Dialog
const showStockWarningModal = (
  productName: string,
  maxStock: number,
  requestedQty: number,
  unitName?: string,
  conversionFactor: number = 1,
  baseUnit: string = 'kg'
) => {
  const reqBaseQty = requestedQty * conversionFactor
  const maxAllowedPackages =
    conversionFactor > 0 ? Math.floor(maxStock / conversionFactor) : Math.floor(maxStock)
  const unitInfo = unitName
    ? `\n• Qadoq turi: ${unitName} (Koeffitsient: ${conversionFactor} ${baseUnit})`
    : ''

  ElMessageBox.alert(
    `Omborda yetarli mahsulot mavjud emas!\n\n• Mahsulot: ${productName}${unitInfo}\n• Ombordagi mavjud ombor: ${maxStock} ${baseUnit}\n• Siz kiritgan talab: ${reqBaseQty} ${baseUnit} (${requestedQty} dona x ${conversionFactor} ${baseUnit})\n\nMiqdor avtomatik ravishda maksimal ${maxAllowedPackages} donaga (${maxAllowedPackages * conversionFactor} ${baseUnit}) o'zgartirildi.`,
    'OMBOR OGOHLANTIRISHI',
    {
      confirmButtonText: 'Tushundim',
      type: 'warning',
      customClass: 'stock-warning-message-box',
      center: true,
      buttonSize: 'large'
    }
  )
}

const searchQuery = reactive({
  search: '',
  payment_method: ''
})

const pagination = reactive({
  pageIndex: 1,
  pageSize: 10
})

const cart = ref<SaleItemType[]>([])

const checkoutForm = reactive({
  cashier_name: activeCashier.value,
  customer_name: '',
  customer_phone: '',
  payment_method: 'naqd' as 'naqd' | 'karta' | 'nasiya',
  paid_amount: 0,
  discount: 0,
  remark: ''
})

const formatMoney = (val: number | string | undefined | null) => {
  if (val === undefined || val === null || val === '') return '0'
  const num = Number(val)
  if (isNaN(num)) return '0'
  return Math.round(num)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

const displayPaidAmount = computed({
  get: () => {
    if (
      checkoutForm.paid_amount === undefined ||
      checkoutForm.paid_amount === null ||
      checkoutForm.paid_amount === 0
    )
      return ''
    return checkoutForm.paid_amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set: (val: string) => {
    const digits = val.replace(/\D/g, '')
    checkoutForm.paid_amount = digits ? parseInt(digits, 10) : 0
  }
})

const debtorOptionsList = computed(() => {
  const map: Record<string, { name: string; total_debt: number; phone?: string }> = {}
  const list = salesList.value || []

  list.forEach((s) => {
    if (s.customer_name && s.customer_name.trim()) {
      const name = s.customer_name.trim()
      if (!map[name]) {
        map[name] = { name, total_debt: 0, phone: s.customer_phone || '' }
      }
      map[name].total_debt += s.debt_amount || 0
    }
  })

  const preseeded = [
    { name: 'Kassir_Sardor', total_debt: 8131, phone: '+998901234567' },
    { name: 'Jamshid Aka', total_debt: 1250, phone: '+998935551122' },
    { name: 'Otabek Rahimov', total_debt: 430, phone: '+998974443322' }
  ]

  preseeded.forEach((p) => {
    if (!map[p.name]) {
      map[p.name] = p
    }
  })

  return Object.values(map).map((d) => ({
    name: d.name,
    total_debt: d.total_debt,
    label:
      d.total_debt > 0
        ? `${d.name} (${t('erp.oldDebtColon')} $${formatMoney(d.total_debt)})`
        : d.name
  }))
})

const selectedDebtorInfo = computed(() => {
  if (!checkoutForm.customer_name || !checkoutForm.customer_name.trim()) return null
  return (
    debtorOptionsList.value.find(
      (d) => d.name.toLowerCase() === checkoutForm.customer_name.trim().toLowerCase()
    ) || null
  )
})

const handleDebtorSelect = (val: string) => {
  if (val) {
    checkoutForm.customer_name = val
  }
}

const subtotal = computed(() => {
  return cart.value.reduce(
    (sum, item) => sum + item.price * (parseFloat(String(item.quantity)) || 0),
    0
  )
})

const grandTotal = computed(() => {
  return Math.max(0, subtotal.value - (checkoutForm.discount || 0))
})

const calculatedDebt = computed(() => {
  if (checkoutForm.payment_method !== 'nasiya') {
    return 0
  }
  const paid = checkoutForm.paid_amount || 0
  return Math.max(0, grandTotal.value - paid)
})

const salesSummary = ref<any>(null)

const stats = computed(() => {
  // If backend returned summary, prioritize it!
  if (salesSummary.value && salesSummary.value.todayCount !== undefined) {
    const todayCount = Number(salesSummary.value.todayCount) || 0
    const todayItems = Number(salesSummary.value.todayItems) || 0
    const todayRevenue = Number(salesSummary.value.todayRevenue) || 0
    const allTimeCount = Number(salesSummary.value.allTimeCount) || salesTotal.value || 0
    const allTimeRevenue = Number(salesSummary.value.allTimeRevenue) || 0
    const allTimeItems = Number(salesSummary.value.allTimeItems) || 0
    const avgReceipt = todayCount > 0 ? todayRevenue / todayCount : 0
    return {
      todayCount,
      todayItems,
      todayRevenue,
      allTimeCount,
      allTimeRevenue,
      allTimeItems,
      avgReceipt
    }
  }

  // Fallback: Client-side local date calculation
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  const todayStr = `${y}-${m}-${d}`

  let todayCount = 0
  let todayItems = 0
  let todayRevenue = 0

  salesList.value.forEach((s) => {
    const createdStr = (s.created_at || '').slice(0, 10)
    if (createdStr === todayStr) {
      todayCount++
      todayItems += Number(s.total_items) || 0
      todayRevenue += Number(s.total_amount) || 0
    }
  })

  const avgReceipt = todayCount > 0 ? todayRevenue / todayCount : 0
  return {
    todayCount,
    todayItems,
    todayRevenue,
    allTimeCount: salesTotal.value,
    allTimeRevenue: 0,
    allTimeItems: 0,
    avgReceipt
  }
})

const fetchSalesData = async (silent = false) => {
  if (!silent) {
    loadingSales.value = true
  }
  try {
    const res: any = await getSalesListApi({
      pageIndex: pagination.pageIndex,
      pageSize: pagination.pageSize,
      search: searchQuery.search || undefined,
      payment_method: searchQuery.payment_method || undefined
    })
    if (res && res.data) {
      salesList.value = res.data.list || []
      salesTotal.value = res.data.total || 0
      if (res.data.summary) {
        salesSummary.value = res.data.summary
      }
    }
  } catch (err) {
    console.error(err)
  } finally {
    if (!silent) {
      loadingSales.value = false
    }
  }
}

const fetchProducts = async (silent = false) => {
  if (!silent) {
    loadingProducts.value = true
  }
  try {
    const res = await getProductListApi({ pageIndex: 1, pageSize: 100 })
    if (res && res.data) {
      products.value = res.data.list || []
    }
  } catch (err) {
    console.error(err)
  } finally {
    if (!silent) {
      loadingProducts.value = false
    }
  }
}

// Automatically sync latest products, sales, and pushes in background
useRealtimeSync(['product', 'sale', 'sales_push'], () => {
  fetchProducts(true)
  fetchSalesData(true)
})

useEventBus({
  name: 'refresh-products',
  callback: () => {
    fetchProducts()
  }
})

useEventBus({
  name: 'ai-data-updated',
  callback: () => {
    fetchProducts()
  }
})

const handleSearch = () => {
  pagination.pageIndex = 1
  fetchSalesData()
}

const resetSearch = () => {
  searchQuery.search = ''
  searchQuery.payment_method = ''
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

const resetCheckoutState = () => {
  cart.value = []
  barcodeSearch.value = ''
  scanQuantity.value = 1
  selectedCategory.value = 'Barchasi'
  checkoutForm.customer_name = ''
  checkoutForm.customer_phone = ''
  checkoutForm.payment_method = 'naqd'
  checkoutForm.paid_amount = 0
  checkoutForm.discount = 0
  checkoutForm.remark = ''
  checkoutForm.cashier_name = activeCashier.value
}

const openPosModal = () => {
  resetCheckoutState()
  fetchProducts()
  posModalVisible.value = true
  setTimeout(() => {
    barcodeInputRef.value?.focus?.()
  }, 200)
}

const setPaymentMethod = (method: 'naqd' | 'karta' | 'nasiya') => {
  checkoutForm.payment_method = method
  if (method === 'nasiya') {
    checkoutForm.paid_amount = 0
  } else {
    checkoutForm.paid_amount = grandTotal.value
  }
}

const setFullPaid = () => {
  checkoutForm.paid_amount = grandTotal.value
}

const filteredProducts = computed(() => {
  let list = products.value
  if (selectedCategory.value !== 'Barchasi') {
    list = list.filter((p) => p.category === selectedCategory.value)
  }
  if (barcodeSearch.value.trim()) {
    const query = barcodeSearch.value.trim().toLowerCase()
    list = list.filter(
      (p) =>
        (p.productName || '').toLowerCase().includes(query) ||
        (p.shtrix_code || '').toLowerCase().includes(query) ||
        (p.brand_name || '').toLowerCase().includes(query)
    )
  }
  return list
})

const selectText = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input && input.select) {
    setTimeout(() => {
      input.select()
    }, 10)
  }
}

const onScanQuantityInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  const raw = input.value.replace(/[^0-9.]/g, '')
  scanQuantity.value = raw
}

const validateScanQuantity = () => {
  const num = parseFloat(String(scanQuantity.value))
  if (isNaN(num) || num < 1) {
    scanQuantity.value = 1
  } else {
    scanQuantity.value = Number(num.toFixed(3))
  }
}

const onItemQtyInput = (idx: number, event: Event) => {
  const item = cart.value[idx]
  if (!item) return
  const input = event.target as HTMLInputElement
  const raw = input.value.replace(/[^0-9.]/g, '')
  const parts = raw.split('.')
  let sanitized = raw
  if (parts.length > 2) {
    sanitized = parts[0] + '.' + parts.slice(1).join('')
  }
  item.quantity = sanitized as any
  if (checkoutForm.payment_method !== 'nasiya') {
    checkoutForm.paid_amount = grandTotal.value
  }
}

const formatPackagingStock = (stock?: number, factor?: number) => {
  if (!stock || !factor || factor <= 0) return 0
  const count = stock / factor
  return count >= 10 ? Math.floor(count) : Number(count.toFixed(1))
}

const getProductStock = (productId?: string) => {
  if (!productId) return 0
  const prod = products.value.find((p) => p.id === productId)
  return prod ? prod.quantityInStock || 0 : 0
}

const getItemPackagings = (productId?: string) => {
  if (!productId) return []
  const prod = products.value.find((p) => p.id === productId)
  if (!prod) return []
  const list: any[] = []
  const baseUnit = prod.unit || 'kg'
  const hasBase = (prod.packagings || []).some(
    (p) =>
      p.conversion_factor === 1.0 ||
      p.unit_name.toLowerCase() === baseUnit.toLowerCase() ||
      p.is_base_unit
  )
  if (!hasBase) {
    list.push({
      unit_name: `${baseUnit.toUpperCase()} (1 ${baseUnit})`,
      conversion_factor: 1.0,
      price: prod.price || 0,
      cost: prod.cost || 0,
      is_base_unit: true
    })
  }
  if (prod.packagings && prod.packagings.length > 0) {
    list.push(...prod.packagings)
  }
  return list
}

const getItemUnit = (productId?: string) => {
  if (!productId) return 'kg'
  const prod = products.value.find((p) => p.id === productId)
  return prod?.unit || 'kg'
}

const handleCartUnitChange = (cartIdx: number, newUnitName: string) => {
  const item = cart.value[cartIdx]
  if (!item) return
  const packagings = getItemPackagings(item.product_id)
  const matchedPkg = packagings.find((p) => p.unit_name === newUnitName)

  if (matchedPkg) {
    item.unit_name = matchedPkg.unit_name
    item.conversion_factor = matchedPkg.conversion_factor
    item.price = matchedPkg.price
    validateItemQty(cartIdx)
  }
}

const handleBarcodeScan = () => {
  let raw = barcodeSearch.value.trim()
  if (!raw) return

  let qty = scanQuantity.value || 1

  if (raw.includes('*')) {
    const parts = raw.split('*')
    if (parts.length === 2 && !isNaN(Number(parts[0]))) {
      qty = parseFloat(parts[0])
      raw = parts[1].trim()
    }
  } else if (raw.toLowerCase().includes('x')) {
    const parts = raw.toLowerCase().split('x')
    if (parts.length === 2 && !isNaN(Number(parts[0]))) {
      qty = parseFloat(parts[0])
      raw = parts[1].trim()
    }
  }

  let selectedPkg: any = null
  const found = products.value.find((p) => {
    if (p.shtrix_code === raw || (p.productName || '').toLowerCase() === raw.toLowerCase()) {
      return true
    }
    if (p.packagings) {
      const matchPkg = p.packagings.find((pkg) => pkg.shtrix_code === raw)
      if (matchPkg) {
        selectedPkg = matchPkg
        return true
      }
    }
    return false
  })

  if (found) {
    addToCart(found, qty, selectedPkg)
    barcodeSearch.value = ''
    scanQuantity.value = 1
  } else if (filteredProducts.value.length === 1) {
    addToCart(filteredProducts.value[0], qty)
    barcodeSearch.value = ''
    scanQuantity.value = 1
  } else {
    soundEffects.playWarning()
    ElMessage.warning('Mahsulot topilmadi!')
  }
}

const addToCart = (
  prod: ProductType,
  qtyToAdd: number = Number(scanQuantity.value) || 1,
  targetPkg: any = null
) => {
  const amount = Math.max(0.001, Number(qtyToAdd) || 1)
  const maxStock = prod.quantityInStock || 0
  const baseUnit = prod.unit || 'kg'

  const selectedPkg = targetPkg || prod.selected_packaging
  const unitName = selectedPkg ? selectedPkg.unit_name : undefined
  const conversionFactor = selectedPkg ? selectedPkg.conversion_factor || 1.0 : 1.0
  const price = selectedPkg ? selectedPkg.price : prod.price || 0

  if (maxStock <= 0) {
    soundEffects.playWarning()
    showStockWarningModal(prod.productName, 0, amount, unitName, conversionFactor, baseUnit)
    return
  }

  // Calculate current total required base stock for this product across all other cart items
  const otherCartBaseQty = cart.value
    .filter((c) => c.product_id === prod.id && c.unit_name !== unitName)
    .reduce((sum, c) => sum + c.quantity * (c.conversion_factor || 1.0), 0)

  const existingIdx = cart.value.findIndex(
    (c) => c.product_id === prod.id && c.unit_name === unitName
  )
  const currentCartQty = existingIdx >= 0 ? cart.value[existingIdx].quantity : 0
  const requestedTotalQty = currentCartQty + amount
  const requestedBaseQty = requestedTotalQty * conversionFactor + otherCartBaseQty

  if (requestedBaseQty > maxStock) {
    soundEffects.playWarning()
    showStockWarningModal(
      prod.productName,
      maxStock,
      requestedTotalQty,
      unitName,
      conversionFactor,
      baseUnit
    )
    const availableForThisPkg = Math.max(0, maxStock - otherCartBaseQty)
    const maxAllowedPackages =
      conversionFactor > 0
        ? conversionFactor === 1
          ? Number(availableForThisPkg.toFixed(3))
          : Math.floor(availableForThisPkg / conversionFactor)
        : 0
    if (existingIdx >= 0) {
      cart.value[existingIdx].quantity = maxAllowedPackages > 0 ? maxAllowedPackages : 1
    } else if (maxAllowedPackages > 0) {
      cart.value.push({
        product_id: prod.id!,
        product_name: prod.productName,
        shtrix_code: prod.shtrix_code,
        price: price,
        cost: prod.cost || 0,
        quantity: maxAllowedPackages,
        unit_name: unitName,
        conversion_factor: conversionFactor
      })
    }
    if (checkoutForm.payment_method !== 'nasiya') {
      checkoutForm.paid_amount = grandTotal.value
    }
    return
  }

  soundEffects.playScanSuccess()
  if (existingIdx >= 0) {
    cart.value[existingIdx].quantity = Number(requestedTotalQty.toFixed(3))
  } else {
    cart.value.push({
      product_id: prod.id!,
      product_name: prod.productName,
      shtrix_code: prod.shtrix_code,
      price: price,
      cost: prod.cost || 0,
      quantity: Number(amount.toFixed(3)),
      unit_name: unitName,
      conversion_factor: conversionFactor
    })
  }
  if (checkoutForm.payment_method !== 'nasiya') {
    checkoutForm.paid_amount = grandTotal.value
  }
  const uLabel = unitName ? ` [${unitName}]` : ` [${baseUnit}]`
  ElMessage.success(`'${prod.productName}'${uLabel} (${amount} dona) savatga qo'shildi`)
}

const increaseQty = (idx: number) => {
  const item = cart.value[idx]
  const curr = parseFloat(String(item.quantity)) || 0
  const prod = products.value.find((p) => p.id === item.product_id)
  const maxStock = prod ? prod.quantityInStock || 0 : 0
  const conversionFactor = item.conversion_factor || 1.0
  const baseUnit = prod ? prod.unit || 'kg' : 'kg'
  const newQty = Number((curr + 1).toFixed(3))

  const otherCartBaseQty = cart.value
    .filter((c, cIdx) => c.product_id === item.product_id && cIdx !== idx)
    .reduce(
      (sum, c) => sum + (parseFloat(String(c.quantity)) || 0) * (c.conversion_factor || 1.0),
      0
    )

  const reqBaseQty = newQty * conversionFactor + otherCartBaseQty

  if (reqBaseQty > maxStock) {
    showStockWarningModal(
      item.product_name,
      maxStock,
      newQty,
      item.unit_name,
      conversionFactor,
      baseUnit
    )
    const available = Math.max(0, maxStock - otherCartBaseQty)
    const maxAllowed =
      conversionFactor > 0
        ? conversionFactor === 1
          ? Number(available.toFixed(3))
          : Math.floor(available / conversionFactor)
        : available
    item.quantity = maxAllowed > 0 ? maxAllowed : 1
    return
  }
  item.quantity = newQty
  if (checkoutForm.payment_method !== 'nasiya') {
    checkoutForm.paid_amount = grandTotal.value
  }
}

const decreaseQty = (idx: number) => {
  const curr = parseFloat(String(cart.value[idx].quantity)) || 1
  if (curr > 1) {
    cart.value[idx].quantity = Number((curr - 1).toFixed(3))
  } else {
    removeFromCart(idx)
  }
  if (checkoutForm.payment_method !== 'nasiya') {
    checkoutForm.paid_amount = grandTotal.value
  }
}

const validateItemQty = (idx: number) => {
  const item = cart.value[idx]
  if (!item) return
  const parsed = parseFloat(String(item.quantity))
  item.quantity = isNaN(parsed) || parsed <= 0 ? 1 : Number(parsed.toFixed(3))
  const prod = products.value.find((p) => p.id === item.product_id)
  const maxStock = prod ? prod.quantityInStock || 0 : 99999
  const conversionFactor = item.conversion_factor || 1.0
  const baseUnit = prod ? prod.unit || 'kg' : 'kg'

  const otherCartBaseQty = cart.value
    .filter((c, cIdx) => c.product_id === item.product_id && cIdx !== idx)
    .reduce(
      (sum, c) => sum + (parseFloat(String(c.quantity)) || 0) * (c.conversion_factor || 1.0),
      0
    )

  const reqBaseQty = item.quantity * conversionFactor + otherCartBaseQty

  if (reqBaseQty > maxStock) {
    showStockWarningModal(
      item.product_name,
      maxStock,
      item.quantity,
      item.unit_name,
      conversionFactor,
      baseUnit
    )
    const available = Math.max(0, maxStock - otherCartBaseQty)
    const maxAllowed =
      conversionFactor > 0
        ? conversionFactor === 1
          ? Number(available.toFixed(3))
          : Math.floor(available / conversionFactor)
        : available
    item.quantity = maxAllowed > 0 ? maxAllowed : 1
  }
  if (checkoutForm.payment_method !== 'nasiya') {
    checkoutForm.paid_amount = grandTotal.value
  }
}

const removeFromCart = (idx: number) => {
  soundEffects.playItemRemove()
  cart.value.splice(idx, 1)
  if (checkoutForm.payment_method !== 'nasiya') {
    checkoutForm.paid_amount = grandTotal.value
  }
}

const clearCart = () => {
  soundEffects.playItemRemove()
  resetCheckoutState()
}

const handleCheckout = async () => {
  if (cart.value.length === 0) return

  if (
    checkoutForm.payment_method === 'nasiya' &&
    (!checkoutForm.customer_name || !checkoutForm.customer_name.trim())
  ) {
    soundEffects.playWarning()
    ElMessage.warning("Iltimos, nasiya to'lovi uchun qarzdor/mijoz ismini kiriting!")
    return
  }

  // Normalize all quantities and aggregate requirements
  const requiredStockByProduct: Record<string, number> = {}
  for (const item of cart.value) {
    if (!item.product_id) continue
    const factor = item.conversion_factor || 1.0
    const qty = parseFloat(String(item.quantity)) || 1
    item.quantity = qty
    requiredStockByProduct[item.product_id] =
      (requiredStockByProduct[item.product_id] || 0) + qty * factor
  }

  for (const [prodId, totalReq] of Object.entries(requiredStockByProduct)) {
    const prod = products.value.find((p) => p.id === prodId)
    const maxStock = prod ? prod.quantityInStock || 0 : 0
    const baseUnit = prod ? prod.unit || 'kg' : 'kg'
    if (totalReq > maxStock) {
      soundEffects.playWarning()
      showStockWarningModal(
        prod?.productName || 'Mahsulot',
        maxStock,
        totalReq,
        undefined,
        1.0,
        baseUnit
      )
      return
    }
  }

  submittingCheckout.value = true
  const paidVal =
    checkoutForm.payment_method === 'nasiya' ? checkoutForm.paid_amount || 0 : grandTotal.value
  try {
    const res: any = await checkoutSaleApi({
      cashier_name: activeCashier.value,
      customer_name:
        checkoutForm.payment_method === 'nasiya' ? checkoutForm.customer_name.trim() : undefined,
      payment_method: checkoutForm.payment_method,
      total_amount: grandTotal.value,
      paid_amount: paidVal,
      debt_amount: calculatedDebt.value,
      discount: checkoutForm.discount || 0,
      total_items: cart.value.reduce((sum, it) => sum + (parseFloat(String(it.quantity)) || 1), 0),
      items: cart.value
    })

    if (res && res.data) {
      soundEffects.playCheckoutSuccess()
      selectedSale.value = {
        ...res.data,
        paid_amount: res.data.paid_amount !== undefined ? res.data.paid_amount : paidVal,
        debt_amount:
          res.data.debt_amount !== undefined ? res.data.debt_amount : calculatedDebt.value,
        payment_method: res.data.payment_method || checkoutForm.payment_method,
        discount: res.data.discount !== undefined ? res.data.discount : checkoutForm.discount || 0,
        cashier_name: activeCashier.value,
        items: [...cart.value]
      }

      ElNotification({
        title: 'Sotuv muvaffaqiyatli!',
        message: `Filial: ${activeBranchName.value} | Kassir: ${activeCashier.value} | Chek #${res.data.receipt_number} ($${formatMoney(res.data.total_amount)})`,
        type: 'success',
        duration: 5000
      })

      // Completely reset checkout form and cart for subsequent sales
      resetCheckoutState()

      posModalVisible.value = false
      receiptModalVisible.value = true
    }
  } catch (err: any) {
    if (!navigator.onLine || err.code === 'ERR_NETWORK' || !err.response) {
      // Offline network failure - queue the sale and auto-purge on reconnect
      offlineQueue.enqueue({
        title: `Sotuv: $${formatMoney(grandTotal.value)} (${activeCashier.value})`,
        url: '/api/sales/checkout',
        method: 'POST',
        payload: {
          cashier_name: activeCashier.value,
          customer_name:
            checkoutForm.payment_method === 'nasiya'
              ? checkoutForm.customer_name.trim()
              : undefined,
          payment_method: checkoutForm.payment_method,
          paid_amount: paidVal,
          debt_amount: calculatedDebt.value,
          discount: checkoutForm.discount || 0,
          items: [...cart.value]
        }
      })
      soundEffects.playCheckoutSuccess()
      resetCheckoutState()
      posModalVisible.value = false
    } else {
      soundEffects.playWarning()
      const msg = err?.response?.data?.detail || 'Sotuvni yakunlashda xatolik yuz berdi'
      ElMessage.error(msg)
    }
  } finally {
    submittingCheckout.value = false
  }
}

const openReceiptDetail = async (row: SaleType) => {
  selectedSale.value = { ...row }
  receiptModalVisible.value = true

  // If items array is missing or empty, fetch the complete receipt with items from the server
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
      console.warn('Error fetching receipt detail:', err)
    } finally {
      receiptLoading.value = false
    }
  }

  // Fallback safety if items is still empty and total_amount > 0
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

const printReceipt = (mode: 'thermal' | 'a4' = 'thermal') => {
  if (!selectedSale.value) return

  const s = selectedSale.value
  const items = s.items || []
  const dateStr = s.created_at || new Date().toLocaleString()
  const cashier = s.cashier_name || activeCashier.value
  const branch = activeBranchName.value
  const paymentMethodLabel = getPaymentLabel(s.payment_method)
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
          @page {
            size: 80mm auto;
            margin: 2mm 0mm;
          }
          * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
          }
          body {
            font-family: 'Courier New', Courier, 'Lucida Console', Monaco, monospace;
            font-size: 12px;
            line-height: 1.35;
            color: #000;
            background: #fff;
            width: 76mm;
            max-width: 80mm;
            margin: 0 auto;
            padding: 8px 4px;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
          .text-center { text-align: center; }
          .text-right { text-align: right; }
          .text-left { text-align: left; }
          .font-bold { font-weight: bold; }
          .brand-title {
            font-size: 17px;
            font-weight: 900;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 2px;
          }
          .brand-sub {
            font-size: 11px;
            margin-bottom: 4px;
          }
          .check-no {
            font-size: 13px;
            font-weight: bold;
            padding: 4px 0;
            border-top: 1px dashed #000;
            border-bottom: 1px dashed #000;
            margin: 6px 0;
          }
          .meta-table {
            width: 100%;
            font-size: 11px;
            margin-bottom: 6px;
          }
          .meta-table td {
            padding: 2px 0;
            vertical-align: top;
          }
          .dashed-divider {
            border-top: 1px dashed #000;
            margin: 6px 0;
          }
          .items-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            margin: 4px 0;
          }
          .items-table th {
            border-bottom: 1px dashed #000;
            padding: 4px 0;
            font-size: 10px;
            text-transform: uppercase;
          }
          .totals-table {
            width: 100%;
            font-size: 12px;
            margin-top: 6px;
          }
          .totals-table td {
            padding: 2px 0;
          }
          .grand-total-row td {
            font-size: 16px;
            font-weight: 900;
            padding: 6px 0;
            border-top: 2px dashed #000;
            border-bottom: 2px dashed #000;
          }
          .footer-section {
            text-align: center;
            margin-top: 14px;
            padding-top: 8px;
            border-top: 1px dashed #000;
            font-size: 10px;
            line-height: 1.4;
          }
          .barcode-box {
            font-family: monospace;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 2px;
            margin: 6px 0;
          }
          @media print {
            body {
              width: 76mm;
              margin: 0 auto;
              padding: 4px 2px;
            }
          }
        </style>
      </head>
      <body>
        <div class="text-center">
          <div class="brand-title">OMBORXONA ERP POS</div>
          <div class="brand-sub">${branch}</div>
          <div class="check-no">CHEK #${s.receipt_number}</div>
        </div>

        <table class="meta-table">
          <tr>
            <td class="text-left">Sana:</td>
            <td class="text-right font-bold">${dateStr}</td>
          </tr>
          <tr>
            <td class="text-left">Kassir:</td>
            <td class="text-right font-bold">${cashier}</td>
          </tr>
          ${
            s.customer_name
              ? `
          <tr>
            <td class="text-left">Mijoz:</td>
            <td class="text-right font-bold">${s.customer_name}</td>
          </tr>`
              : ''
          }
          <tr>
            <td class="text-left">To'lov usuli:</td>
            <td class="text-right font-bold">${paymentMethodLabel.toUpperCase()}</td>
          </tr>
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
          <tr>
            <td class="text-left">Mahsulotlar soni:</td>
            <td class="text-right font-bold">${totalItemsCount} dona</td>
          </tr>
          ${
            Number(s.discount) > 0
              ? `
          <tr>
            <td class="text-left">Chegirma:</td>
            <td class="text-right font-bold">-$${discount}</td>
          </tr>`
              : ''
          }
          <tr class="grand-total-row">
            <td class="text-left">JAMI SUMMA:</td>
            <td class="text-right">$${totalAmount}</td>
          </tr>
          <tr>
            <td class="text-left" style="padding-top: 4px;">To'langan summa:</td>
            <td class="text-right font-bold" style="padding-top: 4px;">$${paidAmount}</td>
          </tr>
          ${
            Number(s.debt_amount) > 0
              ? `
          <tr style="color: #000; font-weight: bold;">
            <td class="text-left">Qarz (Nasiya):</td>
            <td class="text-right">$${debtAmount}</td>
          </tr>`
              : ''
          }
        </table>

        <div class="footer-section">
          <div class="barcode-box">* ${s.receipt_number} *</div>
          <div>Xaridingiz uchun rahmat!</div>
          <div>Salomat bo'ling, yana kuting!</div>
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
            font-size: 13px;
            color: #1a1a1a;
            line-height: 1.5;
            background: #fff;
            margin: 0;
            padding: 20px;
          }
          .header-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #059669;
            padding-bottom: 16px;
            margin-bottom: 20px;
          }
          .company-name { font-size: 24px; font-weight: 800; color: #065f46; }
          .receipt-title { font-size: 20px; font-weight: 700; color: #059669; text-align: right; }
          .meta-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 24px;
          }
          .items-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
          }
          .items-table th {
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
            padding: 10px 12px;
            font-weight: 700;
            font-size: 12px;
            text-transform: uppercase;
          }
          .summary-table {
            margin-left: auto;
            width: 340px;
            border-collapse: collapse;
            font-size: 14px;
          }
          .summary-table td { padding: 6px 8px; }
          .summary-total {
            border-top: 2px solid #065f46;
            border-bottom: 2px solid #065f46;
            font-size: 18px;
            font-weight: 800;
            color: #065f46;
          }
          .signature-row {
            display: flex;
            justify-content: space-between;
            margin-top: 60px;
            padding-top: 20px;
          }
          .sig-line {
            width: 220px;
            border-top: 1px solid #94a3b8;
            text-align: center;
            padding-top: 6px;
            font-size: 12px;
            color: #64748b;
          }
        </style>
      </head>
      <body>
        <div class="header-row">
          <div>
            <div class="company-name">OMBORXONA ERP POS</div>
            <div style="color: #64748b; font-size: 13px; margin-top: 4px;">Filial: ${branch}</div>
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
            <div><b>To'lov usuli:</b> ${paymentMethodLabel.toUpperCase()}</div>
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
          <tr>
            <td>Jami mahsulotlar:</td>
            <td style="text-align: right; font-weight: bold;">${totalItemsCount} dona</td>
          </tr>
          ${
            Number(s.discount) > 0
              ? `
          <tr style="color: #d97706;">
            <td>Chegirma:</td>
            <td style="text-align: right; font-weight: bold;">-$${discount}</td>
          </tr>`
              : ''
          }
          <tr class="summary-total">
            <td>JAMI SUMMA:</td>
            <td style="text-align: right;">$${totalAmount}</td>
          </tr>
          <tr>
            <td>To'langan summa:</td>
            <td style="text-align: right; font-weight: bold;">$${paidAmount}</td>
          </tr>
          ${
            Number(s.debt_amount) > 0
              ? `
          <tr style="color: #dc2626; font-weight: bold;">
            <td>Qarz (Nasiya):</td>
            <td style="text-align: right;">$${debtAmount}</td>
          </tr>`
              : ''
          }
        </table>

        <div class="signature-row">
          <div class="sig-line">Kassir imzosi (${cashier})</div>
          <div class="sig-line">Mijoz imzosi</div>
        </div>
      </body>
    </html>
  `

  const htmlToPrint = mode === 'thermal' ? thermalHtml : a4Html

  // Use hidden iframe to avoid popup blocker issues and ensure smooth direct print
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
  } else {
    const printWindow = window.open('', '_blank', 'width=800,height=900')
    if (printWindow) {
      printWindow.document.write(htmlToPrint)
      printWindow.document.close()
      setTimeout(() => {
        printWindow.focus()
        printWindow.print()
        printWindow.close()
      }, 350)
    } else {
      window.print()
    }
  }
}

const loadPendingCart = (customItems?: any[]) => {
  fetchBranches()
  fetchSalesData()
  fetchProducts()
  const pendingCartStr = sessionStorage.getItem('PENDING_POS_CART')
  let items = customItems
  if (!items && pendingCartStr) {
    try {
      items = JSON.parse(pendingCartStr)
    } catch (e) {
      sessionStorage.removeItem('PENDING_POS_CART')
    }
  }
  if (Array.isArray(items) && items.length > 0) {
    cart.value = items.map((it: any) => ({
      product_id: String(it.product_id),
      product_name: it.product_name || `Mahsulot ${it.product_id}`,
      shtrix_code: it.shtrix_code || String(it.product_id),
      price: Number(it.price || 0),
      cost: Number(it.cost || 0),
      quantity: Number(it.quantity || 1),
      total: Number(it.price || 0) * Number(it.quantity || 1)
    }))
    posModalVisible.value = true
    sessionStorage.removeItem('PENDING_POS_CART')
  }
}

const handlePendingCartEvent = (e: any) => {
  loadPendingCart(e.detail)
}

onMounted(() => {
  fetchBranches()
  fetchSalesData()
  loadPendingCart()
  window.addEventListener('LOAD_PENDING_POS_CART', handlePendingCartEvent)
})

onUnmounted(() => {
  window.removeEventListener('LOAD_PENDING_POS_CART', handlePendingCartEvent)
})
</script>

<style lang="less">
/* Clean Dynamic Dialog Wrappers for Light and Dark Modes */
.pos-dialog-wrap,
.branch-dialog-wrap,
.auth-dialog-wrap,
.receipt-dialog-wrap {
  &.el-dialog {
    background: var(--el-bg-color-overlay, #ffffff) !important;
    border-radius: 14px !important;
    border: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.12) !important;
    display: flex !important;
    flex-direction: column !important;
    max-width: 98vw !important;

    .el-dialog__header {
      height: 50px !important;
      padding: 0 16px !important;
      flex-shrink: 0 !important;
      background: var(--el-fill-color-light, #f8fafc) !important;
      border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
      margin: 0 !important;
      display: flex !important;
      align-items: center !important;
    }

    .el-dialog__body {
      flex: 1 !important;
      padding: 14px 18px !important;
      background: var(--el-bg-color-overlay, #ffffff) !important;
      color: var(--el-text-color-primary) !important;
      overflow: hidden !important;
      display: flex !important;
      flex-direction: column !important;

      > .el-scrollbar {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;

        > .el-scrollbar__wrap {
          flex: 1 !important;
          display: flex !important;
          flex-direction: column !important;
          overflow: hidden !important;

          > .el-scrollbar__view {
            height: 100% !important;
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
          }
        }
      }
    }

    .el-dialog__footer {
      border-top: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
      padding: 12px 20px !important;
      background: var(--el-fill-color-light, #f8fafc) !important;
    }
  }
}

:global(.dark) {
  .pos-dialog-wrap,
  .branch-dialog-wrap,
  .auth-dialog-wrap,
  .receipt-dialog-wrap {
    &.el-dialog {
      background: #111827 !important;
      border-color: #374151 !important;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7) !important;

      .el-dialog__header {
        background: #1f2937 !important;
        border-bottom-color: #374151 !important;
      }

      .el-dialog__body {
        background: #111827 !important;
      }

      .el-dialog__footer {
        background: #1f2937 !important;
        border-top-color: #374151 !important;
      }
    }
  }
}

/* High-Visibility Stock Warning Alert Box */
.stock-warning-message-box {
  background: var(--el-bg-color-overlay, #ffffff) !important;
  border: 2px solid #f59e0b !important;
  border-radius: 12px !important;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15) !important;

  .el-message-box__title {
    color: #d97706 !important;
    font-weight: 800 !important;
    font-size: 18px !important;
  }

  .el-message-box__message {
    color: var(--el-text-color-primary, #0f172a) !important;
    font-size: 15px !important;
    white-space: pre-line !important;
    line-height: 1.6 !important;
  }

  .el-message-box__btns .el-button--primary {
    background: #f59e0b !important;
    border-color: #f59e0b !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    padding: 10px 24px !important;
    border-radius: 8px !important;

    &:hover {
      background: #d97706 !important;
      border-color: #d97706 !important;
    }
  }
}

:global(.dark) {
  .stock-warning-message-box {
    background: #1f2937 !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7) !important;
    .el-message-box__title {
      color: #fbbf24 !important;
    }
    .el-message-box__message {
      color: #f3f4f6 !important;
    }
  }
}
</style>

<style scoped lang="less">
.sales-page-container {
  /* Employee Switcher Grid & Cards */
  .employee-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: var(--el-fill-color-light, #f8fafc);
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.15s ease;

    &:hover {
      border-color: #3b82f6;
      background: rgba(37, 99, 235, 0.08);
    }

    &.active {
      border-color: #10b981;
      background: rgba(16, 185, 129, 0.12);
    }
  }

  :global(.dark) & {
    .employee-card {
      background: #1f2937;
      border-color: #374151;

      &:hover {
        background: rgba(37, 99, 235, 0.2);
      }

      &.active {
        background: rgba(16, 185, 129, 0.25);
      }
    }
  }

  .auth-btn {
    background: #2563eb;
    border: none;
    border-radius: 8px;
    letter-spacing: 0.05em;

    &:hover {
      background: #1d4ed8;
    }
  }

  /* Stat Cards */
  .stat-card {
    padding: 16px;
    border-radius: 10px;
    background: var(--el-bg-color-overlay, #ffffff);
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    transition: all 0.2s ease;

    &:hover {
      border-color: var(--el-border-color, #cbd5e1);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
  }

  :global(.dark) & {
    .stat-card {
      background: #1e293b;
      border-color: #334155;
      box-shadow: none;

      &:hover {
        border-color: #475569;
      }
    }
  }

  .stat-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .stat-info {
    flex: 1;
    min-width: 0;
  }

  .stat-label {
    font-size: 12px;
    color: var(--el-text-color-secondary, #64748b);
    font-weight: 600;
  }

  .stat-number {
    font-size: 20px;
    font-weight: 800;
    margin-top: 2px;
    color: var(--el-text-color-primary, #0f172a);
    font-family: 'SF Mono', monospace, ui-monospace;
  }

  .stat-unit {
    font-size: 12px;
    font-weight: 500;
    color: var(--el-text-color-secondary, #64748b);
  }

  .stat-icon-wrapper {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    background: var(--el-fill-color-light, #f1f5f9);
    color: var(--el-text-color-primary, #334155);
  }

  :global(.dark) & {
    .stat-icon-wrapper {
      background: #334155;
      color: #f8fafc;
    }
  }

  .filter-action-bar {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
  }

  .search-input {
    width: 300px;
  }
  .payment-select {
    width: 200px;
  }

  .pos-open-btn {
    background: #10b981;
    border: none;
    font-weight: 600;
    border-radius: 8px;

    &:hover {
      background: #059669;
    }
  }

  .rounded-pill {
    border-radius: 16px;
    padding: 2px 10px;
  }

  /* POS Modal Internal Layout */
  .pos-left-panel,
  .pos-cart-panel {
    background: var(--el-bg-color-overlay, #ffffff);
    border-radius: 10px;
    padding: 12px;
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  }

  :global(.dark) & {
    .pos-left-panel,
    .pos-cart-panel {
      background: #1e293b;
      border-color: #334155;
    }
  }

  .pos-products-table-wrap {
    :deep(.el-table) {
      border-radius: 8px;
      overflow: hidden;

      .el-table__body-wrapper {
        overflow-y: auto;
      }
    }
  }

  .category-pill {
    display: inline-flex;
    align-items: center;
    padding: 5px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
    background: var(--el-fill-color, #f1f5f9);
    color: var(--el-text-color-regular, #475569);
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
    cursor: pointer;
    transition: all 0.15s ease;
    user-select: none;

    &:hover {
      background: var(--el-fill-color-dark, #e2e8f0);
      color: var(--el-color-primary);
    }

    &.active {
      background: #2563eb;
      color: #ffffff;
      border-color: #2563eb;
    }
  }

  :global(.dark) & {
    .category-pill {
      background: #334155;
      color: #cbd5e1;
      border-color: #475569;

      &:hover {
        background: #475569;
        color: #ffffff;
      }

      &.active {
        background: #2563eb;
        color: #ffffff;
      }
    }
  }

  /* Rich Distinct Row Background Colouring for Cart/Selected Items */
  .pos-product-picker-table {
    :deep(.selected-cart-row) {
      background: linear-gradient(
        90deg,
        rgba(14, 165, 233, 0.18) 0%,
        rgba(20, 184, 166, 0.18) 100%
      ) !important;

      td.el-table__cell {
        background-color: transparent !important;
        border-top: 1px solid rgba(14, 165, 233, 0.4) !important;
        border-bottom: 1px solid rgba(14, 165, 233, 0.4) !important;
      }

      &:hover td.el-table__cell {
        background-color: rgba(14, 165, 233, 0.25) !important;
      }
    }

    :deep(.el-table__row) {
      cursor: pointer;
      transition: all 0.15s ease;
      &:hover td.el-table__cell {
        background-color: rgba(37, 99, 235, 0.1) !important;
      }
    }
  }

  .cart-items-container {
    padding-right: 2px;
  }

  .empty-cart-placeholder {
    padding: 40px 10px;
    text-align: center;
  }

  .cart-item-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 10px;
    margin-bottom: 6px;
    background: var(--el-fill-color-light, #f8fafc);
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
    color: var(--el-text-color-primary, #0f172a);
  }

  :global(.dark) & {
    .cart-item-row {
      background: #0f172a;
      border-color: #334155;
      color: #f8fafc;
    }
  }

  .qty-direct-input {
    -moz-appearance: textfield;
    &::-webkit-outer-spin-button,
    &::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }
  }

  .payment-method-card {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px;
    border-radius: 8px;
    background: var(--el-fill-color-light, #f8fafc);
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
    color: var(--el-text-color-regular, #475569);
    cursor: pointer;
    transition: all 0.15s ease;
    user-select: none;

    &:hover {
      border-color: #2563eb;
      color: #2563eb;
    }

    &.active {
      background: rgba(37, 99, 235, 0.12);
      border-color: #2563eb;
      color: #2563eb;
    }
  }

  :global(.dark) & {
    .payment-method-card {
      background: #0f172a;
      border-color: #334155;
      color: #cbd5e1;

      &:hover {
        border-color: #3b82f6;
        color: #60a5fa;
      }

      &.active {
        background: rgba(37, 99, 235, 0.25);
        border-color: #3b82f6;
        color: #60a5fa;
      }
    }
  }

  .total-summary-box {
    padding: 10px;
    background: var(--el-fill-color-light, #f8fafc);
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
  }

  :global(.dark) & {
    .total-summary-box {
      background: #0f172a;
      border-color: #334155;
    }
  }

  .checkout-submit-btn {
    background: #10b981;
    border: none;
    font-weight: 700;
    border-radius: 8px;

    &:not(:disabled):hover {
      background: #059669;
    }
  }

  /* Large High-Contrast Receipt Card with 5px Spaced Dashes */
  .receipt-large-card {
    background: var(--el-bg-color-overlay, #ffffff);
    color: var(--el-text-color-primary, #0f172a);
    padding: 24px;
    border-radius: 12px;
    border: 2px dashed var(--el-border-color, #cbd5e1);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  }

  :global(.dark) & {
    .receipt-large-card {
      background: #0b1120;
      color: #f3f4f6;
      border-color: #4b5563;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
  }

  /* Spaced 5px Dashed Metadata Box */
  .spaced-dashed-box {
    padding: 14px 18px;
    border-radius: 8px;
    background-color: var(--el-fill-color-light, rgba(241, 245, 249, 0.7));
    border: 1px dashed var(--el-border-color, #cbd5e1);
  }

  :global(.dark) & {
    .spaced-dashed-box {
      background-color: rgba(31, 41, 55, 0.4);
      border-color: #4b5563;
    }
  }

  /* Spaced 5px Dashed Horizontal Line */
  .spaced-dashed-divider {
    height: 1px;
    width: 100%;
    border-top: 1px dashed var(--el-border-color, #cbd5e1);
    margin: 16px 0;
  }

  :global(.dark) & {
    .spaced-dashed-divider {
      border-top-color: #4b5563;
    }
  }
}
</style>
