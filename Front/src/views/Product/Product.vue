<template>
  <div class="ombor-container">
    <ContentWrap class="!mb-16px">
      <!-- Top Stat Cards -->
      <ElRow :gutter="16" class="stat-cards-row">
        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-info">
                <span class="stat-label">{{ t('erp.productTypesCount') }}</span>
                <div class="stat-number">
                  {{ stats.totalTypes }} <span class="stat-unit">{{ t('erp.typesCount') }}</span>
                </div>
              </div>
              <div class="stat-icon-wrapper">
                <Icon icon="ep:goods" :size="20" />
              </div>
            </div>
          </div>
        </ElCol>

        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-info">
                <span class="stat-label">{{ t('erp.totalWarehouseStock') }}</span>
                <div class="stat-number">
                  {{ formatMoney(stats.totalStock) }}
                  <span class="stat-unit">{{ t('erp.itemsCount') }}</span>
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
                <span class="stat-label">{{ t('erp.totalCostValue') }}</span>
                <div class="stat-number"> ${{ formatMoney(stats.totalCost) }} </div>
              </div>
              <div class="stat-icon-wrapper">
                <Icon icon="ep:money" :size="20" />
              </div>
            </div>
          </div>
        </ElCol>

        <ElCol :xs="24" :sm="12" :md="6" class="mb-12px">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-info">
                <span class="stat-label">{{ t('erp.totalSalesValueStat') }}</span>
                <div class="stat-number"> ${{ formatMoney(stats.totalPrice) }} </div>
              </div>
              <div class="stat-icon-wrapper">
                <Icon icon="ep:shopping-bag" :size="20" />
              </div>
            </div>
          </div>
        </ElCol>
      </ElRow>
    </ContentWrap>

    <ContentWrap>
      <!-- Low Stock Warning Alert Banner -->
      <transition name="el-zoom-in-top">
        <div
          v-if="lowStockItems.length > 0"
          class="mb-14px px-16px py-10px rounded-10px bg-amber-500/10 dark:bg-amber-500/15 border border-amber-500/35 flex items-center justify-between flex-wrap gap-2 text-xs"
        >
          <div class="flex items-center gap-8px text-amber-600 dark:text-amber-400 font-semibold">
            <Icon icon="ep:warning" class="text-16px text-amber-500" />
            <span>
              <strong>Kam qolgan mahsulotlar:</strong> {{ lowStockItems.length }} ta mahsulot minimal qoldiqdan kam qolgan. Omborga to'ldirish tavsiya etiladi!
            </span>
          </div>
          <div class="flex items-center gap-6px flex-wrap">
            <ElTag
              v-for="item in lowStockItems.slice(0, 4)"
              :key="item.id"
              size="small"
              type="warning"
              effect="plain"
              class="cursor-pointer"
              @click="openEditDialog(item)"
            >
              {{ item.productName }}: {{ item.quantityInStock }} {{ item.unit || 'dona' }}
            </ElTag>
            <span v-if="lowStockItems.length > 4" class="text-gray-400 text-10px">
              +yana {{ lowStockItems.length - 4 }} ta
            </span>
          </div>
        </div>
      </transition>

      <!-- Filter and Action Bar -->
      <div class="filter-action-bar">
        <ElForm
          :inline="true"
          :model="searchQuery"
          class="flex-1 flex flex-wrap items-center gap-12px"
        >
          <ElFormItem class="!mr-0">
            <ElInput
              v-model="searchQuery.productName"
              :placeholder="t('erp.searchProductAdv')"
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
              v-model="searchQuery.category"
              :placeholder="t('erp.allCategoriesFilter')"
              clearable
              class="category-select"
            >
              <ElOption :label="t('erp.drinksAndWater')" value="Ichimliklar va suvlar" />
              <ElOption :label="t('erp.dairyProducts')" value="Sut va sut mahsulotlari" />
              <ElOption :label="t('erp.saltAndSpices')" value="Tuz va ziravorlar" />
              <ElOption :label="t('erp.plasticsAndDishes')" value="Plastmassa va idishlar" />
              <ElOption :label="t('erp.foodProducts')" value="Oziq-ovqat mahsulotlari" />
              <ElOption :label="t('erp.otherCategory')" value="Boshqalar" />
            </ElSelect>
          </ElFormItem>

          <ElFormItem class="!mr-0">
            <ElButton type="primary" class="action-btn" @click="handleSearch">
              <Icon icon="ep:search" class="mr-4px" />{{ t('common.search') }}</ElButton
            >
            <ElButton @click="resetSearch">{{ t('common.reset') }}</ElButton>
          </ElFormItem>
        </ElForm>

        <div class="action-buttons flex gap-12px">
          <ElButton type="primary" size="large" class="add-btn shadow-btn" @click="openAddDialog">
            <Icon icon="ep:plus" class="mr-6px" />{{ t('erp.newProductEntry') }}</ElButton
          >
          <ElButton type="success" size="large" plain class="shadow-btn" @click="handleExportExcel">
            <Icon icon="ep:download" class="mr-6px" />{{ t('erp.exportExcel') }}</ElButton
          >
          <ElButton
            type="danger"
            size="large"
            plain
            :disabled="selectedIds.length === 0"
            @click="handleBatchDelete"
          >
            <Icon icon="ep:delete" class="mr-4px" /> {{ t('common.delete') }} ({{
              selectedIds.length
            }})
          </ElButton>
        </div>
      </div>

      <!-- Main Inventory Table -->
      <div class="table-wrapper mt-16px">
        <ElTable
          v-loading="loading"
          :data="tableData"
          style="width: 100%"
          border
          stripe
          class="custom-ombor-table cursor-pointer"
          @selection-change="handleSelectionChange"
          @row-click="handleRowClick"
        >
          <ElTableColumn type="selection" width="48" align="center" />

          <ElTableColumn :label="t('erp.image')" width="80" align="center">
            <template #default="scope">
              <div v-if="scope?.row" class="product-thumb-container">
                <img
                  :src="getProductMainImage(scope.row)"
                  :alt="scope.row.productName"
                  @error="handleImageError($event, scope.row.productName)"
                  class="product-thumb-img"
                />
              </div>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="shtrix_code" :label="t('erp.barcode')" width="175">
            <template #default="scope">
              <span v-if="scope?.row">
                <ElTag
                  v-if="scope.row.shtrix_code"
                  type="info"
                  effect="plain"
                  class="barcode-tag font-mono cursor-pointer hover:opacity-85 active:scale-95 transition-all select-none"
                  :title="t('erp.clickToCopy')"
                  @click.stop="copyBarcode(scope.row.shtrix_code)"
                >
                  {{ scope.row.shtrix_code }}
                </ElTag>
                <span v-else class="text-muted">—</span>
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="brand_name" :label="t('erp.brand')" width="130">
            <template #default="scope">
              <span v-if="scope?.row">
                <ElTag
                  v-if="scope.row.brand_name"
                  type="success"
                  effect="light"
                  class="brand-tag font-bold"
                >
                  {{ scope.row.brand_name }}
                </ElTag>
                <span v-else class="text-muted">—</span>
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="productName" :label="t('erp.productName')" min-width="280">
            <template #default="scope">
              <div v-if="scope?.row" class="product-name-cell">
                <div class="product-title" :title="scope.row.productName">{{
                  scope.row.productName
                }}</div>
                <div v-if="scope.row.attribute_name" class="product-subtitle">
                  {{ scope.row.attribute_name }}
                </div>
              </div>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="mxik_code" :label="t('erp.mxikCode')" width="180">
            <template #default="scope">
              <span v-if="scope?.row">
                <span v-if="scope.row.mxik_code" class="font-mono text-12px mxik-code-tag">
                  {{ scope.row.mxik_code }}
                </span>
                <span v-else class="text-muted">—</span>
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="quantityInStock"
            :label="t('erp.quantityInStock')"
            width="180"
            align="center"
          >
            <template #default="scope">
              <span v-if="scope?.row">
                <ElTag
                  :type="
                    (scope.row.quantityInStock || 0) <= 0
                      ? 'danger'
                      : (scope.row.quantityInStock || 0) <= (scope.row.min_stock !== undefined && scope.row.min_stock !== null ? scope.row.min_stock : 10)
                        ? 'warning'
                        : 'success'
                  "
                  effect="dark"
                  class="font-bold rounded-pill"
                >
                  <span v-if="(scope.row.quantityInStock || 0) <= 0">
                    Tugagan (0)
                  </span>
                  <span v-else-if="(scope.row.quantityInStock || 0) <= (scope.row.min_stock !== undefined && scope.row.min_stock !== null ? scope.row.min_stock : 10)" class="inline-flex items-center gap-4px">
                    <Icon icon="ep:warning" class="text-12px" />
                    <span>Kam: {{ formatMoney(scope.row.quantityInStock) }} (min: {{ scope.row.min_stock ?? 10 }})</span>
                  </span>
                  <span v-else>
                    {{ formatMoney(scope.row.quantityInStock) }} {{ scope.row.unit || 'dona' }}
                  </span>
                </ElTag>
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn prop="cost" :label="t('erp.costPriceDollar')" width="130" align="right">
            <template #default="scope">
              <span v-if="scope?.row" class="price-cost">${{ formatMoney(scope.row.cost) }}</span>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="price"
            :label="t('erp.sellingPriceDollar')"
            width="130"
            align="right"
          >
            <template #default="scope">
              <span v-if="scope?.row" class="price-sell">${{ formatMoney(scope.row.price) }}</span>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="category"
            :label="t('erp.category')"
            width="160"
            show-overflow-tooltip
          >
            <template #default="scope">
              <span v-if="scope?.row" class="category-badge" :title="scope.row.category">
                {{ scope.row.category || 'Boshqalar' }}
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn
            prop="expiration_date"
            :label="t('erp.expirationDate')"
            width="180"
            align="center"
          >
            <template #default="scope">
              <span v-if="scope?.row">
                <ElTag
                  v-if="scope.row.expiration_date"
                  :type="isExpired(scope.row.expiration_date) ? 'danger' : isExpiringSoon(scope.row.expiration_date) ? 'warning' : 'info'"
                  effect="plain"
                  class="font-mono text-12px inline-flex items-center gap-4px"
                >
                  <Icon icon="ep:calendar" :class="isExpired(scope.row.expiration_date) ? 'text-red-500' : isExpiringSoon(scope.row.expiration_date) ? 'text-amber-500' : 'text-gray-500'" />
                  <span>{{ scope.row.expiration_date }}</span>
                  <span v-if="isExpired(scope.row.expiration_date)" class="text-10px text-red-500 font-bold ml-2px">(O'tgan)</span>
                  <span v-else-if="isExpiringSoon(scope.row.expiration_date)" class="text-10px text-amber-500 font-bold ml-2px">(Yaqin)</span>
                </ElTag>
                <span v-else class="text-muted">—</span>
              </span>
            </template>
          </ElTableColumn>

          <ElTableColumn :label="t('erp.amallar')" width="130" fixed="right" align="center">
            <template #default="scope">
              <div v-if="scope?.row" class="flex justify-center gap-8px">
                <ElButton
                  size="small"
                  type="primary"
                  class="!px-8px"
                  @click.stop="openEditDialog(scope.row)"
                >
                  <Icon icon="ep:edit" :size="14" />
                </ElButton>
                <ElButton
                  size="small"
                  type="danger"
                  class="!px-8px"
                  @click.stop="handleDelete(scope.row)"
                >
                  <Icon icon="ep:delete" :size="14" />
                </ElButton>
              </div>
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
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </ContentWrap>

    <!-- Add/Edit Modal with Classifier Search -->
    <ResizeDialog
      v-model="dialogVisible"
      :title="
        dialogType === 'add' ? 'Yangi Mahsulot Kirim Qilish (Ombor)' : 'Mahsulotni Tahrirlash'
      "
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="700"
      :min-resize-height="450"
    >
      <div class="product-dialog-content">
        <!-- ADD MODE: 2-COLUMN SPLIT (LEFT: SEARCH/SCAN/STATUS/CALC/IMAGE; RIGHT: FORM) -->
        <div v-if="dialogType === 'add'" class="product-two-column-grid">
          <!-- LEFT PANEL -->
          <div class="product-panel-left">
            <!-- 1. Search & Scanner Card -->
            <div class="intake-card intake-search-card">
              <div
                class="flex items-center justify-between pb-8px mb-10px border-b border-blue-200/50 dark:border-blue-800/50"
              >
                <div class="flex items-center gap-6px">
                  <div
                    class="w-24px h-24px rounded-md bg-blue-500 text-white flex items-center justify-center shadow-xs"
                  >
                    <Icon icon="ep:aim" style="font-size: 13px" />
                  </div>
                  <span class="font-bold text-13px text-gray-900 dark:text-gray-100">
                    1. Qidirish & Skanerlash
                  </span>
                </div>
                <ElButton
                  size="small"
                  type="danger"
                  plain
                  class="!px-8px !py-3px !text-xs font-medium"
                  @click="resetForm"
                >
                  <Icon icon="ep:refresh-right" class="mr-3px" /> Tozalash
                </ElButton>
              </div>

              <!-- Barcode input -->
              <div class="mb-10px">
                <ElInput
                  ref="barcodeInputRef"
                  v-model="barcodeSearch"
                  placeholder="Shtrix-kodni skanerlang yoki kiriting..."
                  clearable
                  @input="(val: string) => (barcodeSearch = val.replace(/\D/g, ''))"
                  @keyup.enter="handleBarcodeScan"
                >
                  <template #prefix>
                    <Icon icon="ep:reading" class="text-gray-400" />
                  </template>
                  <template #append>
                    <ElButton
                      type="primary"
                      :loading="barcodeLoading"
                      class="!px-12px font-semibold"
                      @click="handleBarcodeScan"
                    >
                      <Icon icon="ep:aim" class="mr-3px" /> Izlash
                    </ElButton>
                  </template>
                </ElInput>
              </div>

              <!-- Search mode switcher -->
              <div class="mb-8px flex items-center justify-between flex-wrap gap-1">
                <ElRadioGroup
                  v-model="classifierSearchMode"
                  size="small"
                  class="custom-search-mode-radios"
                  @change="onClassifierSearchModeChange"
                >
                  <ElRadioButton label="extended">
                    <Icon icon="ep:lightning" class="mr-2px text-amber-500" /> Kengaytirilgan
                  </ElRadioButton>
                  <ElRadioButton label="simple">
                    <Icon icon="ep:search" class="mr-2px" /> Oddiy
                  </ElRadioButton>
                </ElRadioGroup>
                <span class="text-[11px] text-gray-400 font-medium">Tasnif Soliq (440k+)</span>
              </div>

              <!-- Remote classifier autocomplete -->
              <div>
                <ElSelect
                  v-model="selectedClassifierId"
                  filterable
                  remote
                  reserve-keyword
                  clearable
                  :fit-input-width="true"
                  popper-class="classifier-select-popper"
                  :placeholder="
                    classifierSearchMode === 'extended'
                      ? 'Tovar nomi yoki brendi (Pepsi, Cola, ruchka...)'
                      : 'Oddiy qidiruv...'
                  "
                  :remote-method="remoteSearchClassifier"
                  :loading="classifierLoading"
                  style="width: 100%"
                  @change="handleClassifierSelect"
                >
                  <template #prefix>
                    <Icon icon="ep:search" class="text-blue-500 mr-2px" />
                  </template>
                  <ElOption
                    v-for="item in classifierOptions"
                    :key="item.id || item.mxik_code || item.shtrix_code"
                    :label="`${item.brand_name ? '[' + item.brand_name + '] ' : ''}${item.mxik_name} ${item.attribute_name ? '(' + item.attribute_name + ')' : ''} [${item.shtrix_code || item.mxik_code}]`"
                    :value="item.id || item.mxik_code"
                    class="classifier-option-item"
                  >
                    <div class="classifier-item-card">
                      <div class="classifier-item-top">
                        <span v-if="item.brand_name" class="classifier-brand-tag">{{
                          item.brand_name
                        }}</span>
                        <span class="classifier-item-title">{{ item.mxik_name }}</span>
                      </div>
                      <div class="classifier-item-meta">
                        <span v-if="item.attribute_name" class="classifier-badge-attr">
                          <Icon icon="ep:box" class="mr-3px" />{{ item.attribute_name }}
                        </span>
                        <span v-if="item.shtrix_code" class="classifier-badge-code">
                          <Icon icon="ep:reading" class="mr-3px" />{{ item.shtrix_code }}
                        </span>
                      </div>
                    </div>
                  </ElOption>
                  <template #empty>
                    <div
                      v-if="classifierLoading"
                      class="p-12px text-center text-blue-400 text-xs flex items-center justify-center gap-6px"
                    >
                      <Icon icon="ep:loading" class="animate-spin text-14px" />
                      <span>Qidirilmoqda...</span>
                    </div>
                    <div
                      v-else-if="!lastClassifierQuery || lastClassifierQuery.length < 2"
                      class="p-12px text-center text-gray-400 text-xs flex items-center justify-center gap-6px"
                    >
                      <Icon icon="ep:info-filled" class="text-blue-400 text-13px" />
                      <span>Kamida 2 ta harf kiriting (Pepsi, Cola...)</span>
                    </div>
                    <div
                      v-else
                      class="p-12px text-center text-gray-400 text-xs flex items-center justify-center gap-6px"
                    >
                      <Icon icon="ep:warning" class="text-amber-400 text-13px" />
                      <span>"{{ lastClassifierQuery }}" bo'yicha topilmadi</span>
                    </div>
                  </template>
                </ElSelect>
              </div>
            </div>

            <!-- 2. Interactive Warehouse Status & Live Calculator Card -->
            <transition name="el-zoom-in-top" mode="out-in">
              <div
                v-if="existingProduct"
                key="existing"
                class="intake-card warehouse-status-card existing"
              >
                <div class="flex items-center justify-between pb-6px border-b border-emerald-500/25">
                  <div class="flex items-center gap-6px text-emerald-700 dark:text-emerald-300 font-bold text-xs">
                    <span class="relative flex h-2 w-2">
                      <span
                        class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
                      ></span>
                      <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span>Omborda Mavjud Mahsulot!</span>
                  </div>
                  <ElTag type="success" size="small" effect="dark" class="font-bold text-[10px]">
                    Bazada Bor
                  </ElTag>
                </div>

                <div class="grid grid-cols-3 gap-6px my-8px">
                  <div
                    class="metric-box bg-white/80 dark:bg-gray-800/80 p-6px rounded-6px border border-gray-200/70 dark:border-gray-700/70 text-center"
                  >
                    <div class="text-[10px] text-gray-500 dark:text-gray-400 font-medium leading-tight">
                      Ombor Qoldig'i
                    </div>
                    <div
                      class="text-13px font-bold font-mono text-gray-900 dark:text-white flex items-center justify-center gap-2px mt-2px"
                    >
                      <Icon icon="ep:lock" class="text-amber-500 text-11px" />
                      <span>{{ formatMoney(existingProduct.quantityInStock) }}</span>
                    </div>
                    <div class="text-[9px] text-gray-400">
                      {{ existingProduct.unit || 'dona' }}
                    </div>
                  </div>

                  <div
                    class="metric-box bg-white/80 dark:bg-gray-800/80 p-6px rounded-6px border border-gray-200/70 dark:border-gray-700/70 text-center"
                  >
                    <div class="text-[10px] text-gray-500 dark:text-gray-400 font-medium leading-tight">
                      Eski Tannarx
                    </div>
                    <div class="text-13px font-bold font-mono text-amber-600 dark:text-amber-400 mt-2px">
                      ${{ formatMoney(existingProduct.cost) }}
                    </div>
                    <div class="text-[9px] text-gray-400">avvalgi</div>
                  </div>

                  <div
                    class="metric-box bg-white/80 dark:bg-gray-800/80 p-6px rounded-6px border border-gray-200/70 dark:border-gray-700/70 text-center"
                  >
                    <div class="text-[10px] text-gray-500 dark:text-gray-400 font-medium leading-tight">
                      Eski Sotish
                    </div>
                    <div class="text-13px font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-2px">
                      ${{ formatMoney(existingProduct.price) }}
                    </div>
                    <div class="text-[9px] text-gray-400">avvalgi</div>
                  </div>
                </div>

                <!-- Live Dynamic Stock Formula Banner -->
                <div class="p-8px rounded-8px bg-emerald-500/10 border border-emerald-500/25">
                  <div
                    class="text-[11px] text-emerald-800 dark:text-emerald-300 font-medium mb-3px flex items-center justify-between"
                  >
                    <span class="flex items-center gap-4px">
                      <Icon icon="ep:circle-check" class="text-emerald-500 text-12px" />
                      Yangi umumiy qoldiq hisobi:
                    </span>
                    <span class="text-[10px] font-bold text-emerald-600 dark:text-emerald-400">
                      +{{ form.quantityInStock || 0 }} qo'shiladi
                    </span>
                  </div>
                  <div
                    class="font-mono font-bold text-xs text-emerald-700 dark:text-emerald-300 bg-white/90 dark:bg-black/40 px-8px py-4px rounded-6px flex items-center justify-between"
                  >
                    <span>{{ formatMoney(existingProduct.quantityInStock) }} + {{ formatMoney(form.quantityInStock || 0) }}</span>
                    <span class="text-13px text-emerald-600 dark:text-emerald-400 font-black">
                      = Jami {{ formatMoney((existingProduct.quantityInStock || 0) + (Number(form.quantityInStock) || 0)) }} {{ form.unit || 'dona' }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- If New Product -->
              <div v-else key="new" class="intake-card warehouse-status-card new-item">
                <div class="flex items-center gap-6px text-xs font-semibold text-blue-600 dark:text-blue-400">
                  <Icon icon="ep:circle-plus-filled" class="text-15px text-blue-500" />
                  <span>Yangi Mahsulot Kirimi</span>
                </div>
                <div class="text-[11px] text-gray-500 dark:text-gray-400 mt-4px leading-relaxed">
                  Ushbu tovar omborda hali mavjud emas. Yangi mahsulot sifatida saqlanadi.
                </div>
              </div>
            </transition>

            <!-- 3. Photo Upload Card -->
            <div class="intake-card photo-card">
              <div
                class="text-xs font-bold text-gray-700 dark:text-gray-300 mb-8px flex items-center justify-between"
              >
                <span class="flex items-center gap-6px">
                  <Icon icon="ep:picture" class="text-blue-500" /> Mahsulot Rasmi
                </span>
                <span
                  v-if="form.image_url"
                  class="text-[11px] text-red-500 cursor-pointer hover:underline"
                  @click="form.image_url = ''"
                >
                  Rasmni o'chirish
                </span>
              </div>
              <div class="flex items-center gap-12px">
                <div
                  v-if="form.image_url"
                  class="relative w-64px h-64px rounded-8px overflow-hidden border border-gray-300 dark:border-gray-700 flex-shrink-0 group shadow-xs"
                >
                  <img :src="form.image_url" class="w-full h-full object-cover" />
                  <div
                    class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity cursor-pointer"
                    @click="form.image_url = ''"
                  >
                    <Icon icon="ep:delete" class="text-white text-16px" />
                  </div>
                </div>
                <div
                  v-else
                  class="w-64px h-64px rounded-8px border-2 border-dashed border-gray-300 dark:border-gray-700 flex items-center justify-center flex-shrink-0 text-gray-400"
                >
                  <Icon icon="ep:picture" class="text-22px opacity-40" />
                </div>
                <div class="flex flex-col gap-4px flex-1">
                  <ElUpload
                    action="#"
                    :auto-upload="false"
                    :show-file-list="false"
                    accept="image/*"
                    @change="handleImageChange"
                  >
                    <ElButton size="small" type="primary" plain class="w-full">
                      <Icon icon="ep:upload" class="mr-4px" />
                      {{ form.image_url ? "O'zgartirish" : 'Rasm yuklash' }}
                    </ElButton>
                  </ElUpload>
                  <span class="text-[10px] text-gray-400">JPG, PNG, WEBP (maks 5MB)</span>
                </div>
              </div>
            </div>
          </div>

          <!-- RIGHT PANEL: Form Details -->
          <div class="product-panel-right flex-1 min-w-0">
            <ElForm
              ref="formRef"
              :model="form"
              :rules="rules"
              label-position="top"
              class="compact-modal-form"
            >
              <!-- Card 1: Asosiy Ma'lumotlar -->
              <div class="intake-form-section mb-10px">
                <div
                  class="section-title mb-8px flex items-center gap-6px text-xs font-bold text-gray-700 dark:text-gray-200"
                >
                  <Icon icon="ep:document" class="text-blue-500" />
                  <span>2. Mahsulot Asosiy Ma'lumotlari</span>
                </div>

                <!-- Product Name -->
                <ElFormItem :label="t('erp.productName')" prop="productName" class="!mb-10px">
                  <ElInput
                    v-model="form.productName"
                    placeholder="Masalan: Pepsi 1.5L PET"
                    class="font-medium"
                  />
                </ElFormItem>

                <!-- Row 1: Shtrix-kodi, Brend, MXIK -->
                <ElRow :gutter="10" class="!mb-0">
                  <ElCol :span="8">
                    <ElFormItem label="Shtrix-Kodi" prop="shtrix_code" class="!mb-8px">
                      <ElInput
                        v-model="form.shtrix_code"
                        placeholder="4780014680073"
                        @input="(val: string) => (form.shtrix_code = val.replace(/\D/g, ''))"
                        @blur="onShtrixCodeBlur"
                      />
                    </ElFormItem>
                  </ElCol>
                  <ElCol :span="8">
                    <ElFormItem label="Brend Nomi" prop="brand_name" class="!mb-8px">
                      <ElInput v-model="form.brand_name" placeholder="PEPSI, Shaffof" />
                    </ElFormItem>
                  </ElCol>
                  <ElCol :span="8">
                    <ElFormItem :label="t('erp.mxikCode')" prop="mxik_code" class="!mb-8px">
                      <ElInput v-model="form.mxik_code" placeholder="02201001001001002" />
                    </ElFormItem>
                  </ElCol>
                </ElRow>

                <!-- Row 2: SKU, O'lchov birligi, Atribut -->
                <ElRow :gutter="10" class="!mb-0">
                  <ElCol :span="8">
                    <ElFormItem label="SKU Raqami" prop="SKU" class="!mb-8px">
                      <ElInput v-model="form.SKU" placeholder="SKU-4780014680073" />
                    </ElFormItem>
                  </ElCol>
                  <ElCol :span="8">
                    <ElFormItem label="O'lchov Birligi" prop="unit" class="!mb-8px">
                      <ElInput v-model="form.unit" placeholder="dona, kg, litr..." />
                    </ElFormItem>
                  </ElCol>
                  <ElCol :span="8">
                    <ElFormItem label="Atribut / O'lcham" prop="attribute_name" class="!mb-8px">
                      <ElInput v-model="form.attribute_name" placeholder="PET idish 1,5 l." />
                    </ElFormItem>
                  </ElCol>
                </ElRow>
              </div>

              <!-- Card 2: Kirim Miqdori va Narxlar Karti -->
              <div
                class="pricing-card-wrapper p-10px rounded-10px border border-blue-500/25 bg-blue-50/25 dark:bg-blue-950/25 mb-10px"
              >
                <div class="flex items-center justify-between mb-8px">
                  <div
                    class="text-xs font-bold text-gray-800 dark:text-gray-200 flex items-center gap-6px"
                  >
                    <Icon icon="ep:coin" class="text-amber-500" />
                    <span>3. Kirim Miqdori va Narxlar ($)</span>
                  </div>
                  <div
                    v-if="form.cost > 0 && form.price > 0"
                    class="text-xs font-mono font-bold px-8px py-2px rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                  >
                    Kutilayotgan foyda: {{ profitAmount >= 0 ? '+' : '' }}${{ formatMoney(profitAmount) }} ({{ profitPercent }}% marja)
                  </div>
                </div>

                <ElRow :gutter="10" class="items-start !mb-0">
                  <!-- Quantity In Stock -->
                  <ElCol :span="8">
                    <ElFormItem
                      :label="existingProduct ? 'Yangi Kirim Soni (+)' : 'Ombor Qoldig\'i (Soni)'"
                      prop="quantityInStock"
                      class="!mb-4px"
                    >
                      <ElInputNumber
                        v-model="form.quantityInStock"
                        :min="1"
                        :step="1"
                        style="width: 100%"
                        placeholder="Kirim soni"
                      />
                      <div
                        v-if="existingProduct"
                        class="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono mt-2px font-bold"
                      >
                        +{{ form.quantityInStock || 0 }} dona qo'shiladi
                      </div>
                    </ElFormItem>
                  </ElCol>

                  <!-- Cost Price -->
                  <ElCol :span="8">
                    <ElFormItem :label="t('erp.costPriceDollar')" prop="cost" class="!mb-4px">
                      <ElInput
                        v-model="displayCost"
                        placeholder="Masalan: 10 000"
                        class="custom-price-input cost-input"
                      >
                        <template #prefix>
                          <span class="text-xs font-bold text-gray-400 font-mono">$</span>
                        </template>
                      </ElInput>
                      <div
                        v-if="existingProduct"
                        class="text-[10px] text-amber-500/90 font-mono mt-2px font-semibold"
                      >
                        Eski tannarx: ${{ formatMoney(existingProduct.cost) }}
                      </div>
                    </ElFormItem>
                  </ElCol>

                  <!-- Selling Price -->
                  <ElCol :span="8">
                    <ElFormItem :label="t('erp.sellingPriceDollar')" prop="price" class="!mb-4px">
                      <ElInput
                        v-model="displayPrice"
                        placeholder="Masalan: 13 000"
                        class="custom-price-input sell-input"
                      >
                        <template #prefix>
                          <span class="text-xs font-bold text-gray-400 font-mono">$</span>
                        </template>
                      </ElInput>
                      <div
                        v-if="existingProduct"
                        class="text-[10px] text-emerald-500/90 font-mono mt-2px font-semibold"
                      >
                        Eski sotuv: ${{ formatMoney(existingProduct.price) }}
                      </div>
                    </ElFormItem>
                  </ElCol>
                </ElRow>
              </div>

              <!-- Card 3: Ombor Qoidalari, Kategoriya, Muddat -->
              <div class="intake-form-section mb-8px">
                <ElRow :gutter="10" class="!mb-0">
                  <ElCol :span="8">
                    <ElFormItem :label="t('erp.category')" prop="category" class="!mb-8px">
                      <ElSelect
                        v-model="form.category"
                        filterable
                        allow-create
                        default-first-option
                        :placeholder="t('erp.kategoriyaniTanlang')"
                        style="width: 100%"
                      >
                        <ElOption :label="t('erp.drinksAndWater')" value="Ichimliklar va suvlar" />
                        <ElOption :label="t('erp.dairyProducts')" value="Sut va sut mahsulotlari" />
                        <ElOption :label="t('erp.saltAndSpices')" value="Tuz va ziravorlar" />
                        <ElOption :label="t('erp.plasticsAndDishes')" value="Plastmassa va idishlar" />
                        <ElOption :label="t('erp.foodProducts')" value="Oziq-ovqat mahsulotlari" />
                        <ElOption label="Maishiy texnika va elektronika" value="Maishiy texnika va elektronika" />
                        <ElOption label="Kiyim-kechak va poyabzal" value="Kiyim-kechak va poyabzal" />
                        <ElOption label="Qurilish va ta'mirlash" value="Qurilish va ta'mirlash" />
                        <ElOption label="Avtoehtiyot qismlar" value="Avtoehtiyot qismlar" />
                        <ElOption :label="t('erp.otherCategory')" value="Boshqalar" />
                      </ElSelect>
                    </ElFormItem>
                  </ElCol>

                  <ElCol :span="8">
                    <ElFormItem label="Kam qolganda ogohlantirish (min)" prop="min_stock" class="!mb-8px">
                      <ElInputNumber
                        v-model="form.min_stock"
                        :min="0"
                        :step="5"
                        style="width: 100%"
                        placeholder="10"
                      />
                    </ElFormItem>
                  </ElCol>

                  <ElCol :span="8">
                    <ElFormItem label="Yaroqlilik Muddati" prop="expiration_date" class="!mb-8px">
                      <ElDatePicker
                        v-model="form.expiration_date"
                        type="date"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        placeholder="YYYY-MM-DD"
                        style="width: 100%"
                      />
                    </ElFormItem>
                  </ElCol>
                </ElRow>

                <!-- Remark -->
                <ElFormItem :label="t('erp.izoh')" prop="remark" class="!mb-0">
                  <ElInput
                    v-model="form.remark"
                    type="textarea"
                    :rows="2"
                    placeholder="Mahsulot haqida qo'shimcha izoh..."
                  />
                </ElFormItem>
              </div>
            </ElForm>
          </div>
        </div>

        <!-- EDIT MODE: Symmetrical 2-Column -->
        <div v-else class="product-two-column-grid">
          <!-- LEFT PANEL: Image & Quick Overview -->
          <div class="product-panel-left">
            <div class="intake-card photo-card">
              <div
                class="text-xs font-bold text-gray-700 dark:text-gray-300 mb-8px flex items-center justify-between"
              >
                <span class="flex items-center gap-6px">
                  <Icon icon="ep:picture" class="text-blue-500" /> Mahsulot Rasmi
                </span>
                <span
                  v-if="form.image_url"
                  class="text-[11px] text-red-500 cursor-pointer hover:underline"
                  @click="form.image_url = ''"
                >
                  O'chirish
                </span>
              </div>
              <div class="flex flex-col items-center gap-10px">
                <div
                  v-if="form.image_url"
                  class="relative w-140px h-140px rounded-12px overflow-hidden border border-gray-300 dark:border-gray-700 group shadow-md"
                >
                  <img :src="form.image_url" class="w-full h-full object-cover" />
                  <div
                    class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity cursor-pointer"
                    @click="form.image_url = ''"
                  >
                    <Icon icon="ep:delete" class="text-white text-20px" />
                  </div>
                </div>
                <div
                  v-else
                  class="w-140px h-140px rounded-12px border-2 border-dashed border-gray-300 dark:border-gray-700 flex items-center justify-center text-gray-400"
                >
                  <Icon icon="ep:picture" class="text-36px opacity-40" />
                </div>
                <ElUpload
                  action="#"
                  :auto-upload="false"
                  :show-file-list="false"
                  accept="image/*"
                  @change="handleImageChange"
                >
                  <ElButton size="small" type="primary" plain>
                    <Icon icon="ep:upload" class="mr-4px" />
                    {{ form.image_url ? "Rasmni o'zgartirish" : 'Rasm yuklash' }}
                  </ElButton>
                </ElUpload>
              </div>
            </div>

            <!-- Quick Info -->
            <div class="intake-card warehouse-status-card">
              <div
                class="text-xs font-bold text-gray-700 dark:text-gray-300 mb-8px flex items-center gap-6px"
              >
                <Icon icon="ep:info-filled" class="text-blue-500" />
                <span>Tahrirlash Ma'lumoti</span>
              </div>
              <div class="space-y-6px text-xs">
                <div class="flex justify-between py-4px border-b border-gray-200/50 dark:border-gray-800/50">
                  <span class="text-gray-400">ID:</span>
                  <span class="font-mono font-bold">{{ form.id }}</span>
                </div>
                <div class="flex justify-between py-4px border-b border-gray-200/50 dark:border-gray-800/50">
                  <span class="text-gray-400">Shtrix-kod:</span>
                  <span class="font-mono font-bold">{{ form.shtrix_code || "Yo'q" }}</span>
                </div>
                <div class="flex justify-between py-4px">
                  <span class="text-gray-400">Hozirgi qoldiq:</span>
                  <span class="font-mono font-bold text-emerald-600 dark:text-emerald-400">
                    {{ formatMoney(form.quantityInStock) }} {{ form.unit || 'dona' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- RIGHT PANEL: Edit Form -->
          <div class="product-panel-right flex-1 min-w-0">
            <ElForm
              ref="formRef"
              :model="form"
              :rules="rules"
              label-position="top"
              class="compact-modal-form"
            >
              <!-- Name -->
              <ElFormItem :label="t('erp.productName')" prop="productName" class="!mb-10px">
                <ElInput v-model="form.productName" class="font-medium" />
              </ElFormItem>

              <!-- Codes -->
              <ElRow :gutter="10" class="!mb-0">
                <ElCol :span="8">
                  <ElFormItem label="Shtrix-Kodi" prop="shtrix_code" class="!mb-8px">
                    <ElInput
                      v-model="form.shtrix_code"
                      @input="(val: string) => (form.shtrix_code = val.replace(/\D/g, ''))"
                    />
                  </ElFormItem>
                </ElCol>
                <ElCol :span="8">
                  <ElFormItem label="Brend Nomi" prop="brand_name" class="!mb-8px">
                    <ElInput v-model="form.brand_name" />
                  </ElFormItem>
                </ElCol>
                <ElCol :span="8">
                  <ElFormItem :label="t('erp.mxikCode')" prop="mxik_code" class="!mb-8px">
                    <ElInput v-model="form.mxik_code" />
                  </ElFormItem>
                </ElCol>
              </ElRow>

              <ElRow :gutter="10" class="!mb-0">
                <ElCol :span="8">
                  <ElFormItem label="SKU Raqami" prop="SKU" class="!mb-8px">
                    <ElInput v-model="form.SKU" />
                  </ElFormItem>
                </ElCol>
                <ElCol :span="8">
                  <ElFormItem label="O'lchov Birligi" prop="unit" class="!mb-8px">
                    <ElInput v-model="form.unit" />
                  </ElFormItem>
                </ElCol>
                <ElCol :span="8">
                  <ElFormItem label="Atribut / O'lcham" prop="attribute_name" class="!mb-8px">
                    <ElInput v-model="form.attribute_name" />
                  </ElFormItem>
                </ElCol>
              </ElRow>

              <!-- Pricing Card -->
              <div
                class="pricing-card-wrapper p-10px rounded-10px border border-blue-500/25 bg-blue-50/25 dark:bg-blue-950/25 mb-10px"
              >
                <div class="flex items-center justify-between mb-8px">
                  <div
                    class="text-xs font-bold text-gray-800 dark:text-gray-200 flex items-center gap-6px"
                  >
                    <Icon icon="ep:coin" class="text-amber-500" />
                    <span>Ombor Qoldig'i va Narxlar ($)</span>
                  </div>
                  <div
                    v-if="form.cost > 0 && form.price > 0"
                    class="text-xs font-mono font-bold px-8px py-2px rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                  >
                    Kutilayotgan foyda: {{ profitAmount >= 0 ? '+' : '' }}${{ formatMoney(profitAmount) }} ({{ profitPercent }}% marja)
                  </div>
                </div>

                <ElRow :gutter="10" class="items-start !mb-0">
                  <ElCol :span="8">
                    <ElFormItem label="Ombor Qoldig'i (Soni)" prop="quantityInStock" class="!mb-4px">
                      <ElInputNumber v-model="form.quantityInStock" :min="0" :step="1" style="width: 100%" />
                    </ElFormItem>
                  </ElCol>
                  <ElCol :span="8">
                    <ElFormItem :label="t('erp.costPriceDollar')" prop="cost" class="!mb-4px">
                      <ElInput v-model="displayCost" class="custom-price-input cost-input">
                        <template #prefix><span class="text-xs font-bold text-gray-400 font-mono">$</span></template>
                      </ElInput>
                    </ElFormItem>
                  </ElCol>
                  <ElCol :span="8">
                    <ElFormItem :label="t('erp.sellingPriceDollar')" prop="price" class="!mb-4px">
                      <ElInput v-model="displayPrice" class="custom-price-input sell-input">
                        <template #prefix><span class="text-xs font-bold text-gray-400 font-mono">$</span></template>
                      </ElInput>
                    </ElFormItem>
                  </ElCol>
                </ElRow>
              </div>

              <!-- Category, Min Stock, Expiration -->
              <ElRow :gutter="10" class="!mb-0">
                <ElCol :span="8">
                  <ElFormItem :label="t('erp.category')" prop="category" class="!mb-8px">
                    <ElSelect v-model="form.category" filterable allow-create style="width: 100%">
                      <ElOption :label="t('erp.drinksAndWater')" value="Ichimliklar va suvlar" />
                      <ElOption :label="t('erp.dairyProducts')" value="Sut va sut mahsulotlari" />
                      <ElOption :label="t('erp.saltAndSpices')" value="Tuz va ziravorlar" />
                      <ElOption :label="t('erp.plasticsAndDishes')" value="Plastmassa va idishlar" />
                      <ElOption :label="t('erp.foodProducts')" value="Oziq-ovqat mahsulotlari" />
                      <ElOption label="Maishiy texnika va elektronika" value="Maishiy texnika va elektronika" />
                      <ElOption label="Kiyim-kechak va poyabzal" value="Kiyim-kechak va poyabzal" />
                      <ElOption label="Qurilish va ta'mirlash" value="Qurilish va ta'mirlash" />
                      <ElOption label="Avtoehtiyot qismlar" value="Avtoehtiyot qismlar" />
                      <ElOption :label="t('erp.otherCategory')" value="Boshqalar" />
                    </ElSelect>
                  </ElFormItem>
                </ElCol>
                <ElCol :span="8">
                  <ElFormItem label="Kam qolganda ogohlantirish (min)" prop="min_stock" class="!mb-8px">
                    <ElInputNumber v-model="form.min_stock" :min="0" :step="5" style="width: 100%" />
                  </ElFormItem>
                </ElCol>
                <ElCol :span="8">
                  <ElFormItem label="Yaroqlilik Muddati" prop="expiration_date" class="!mb-8px">
                    <ElDatePicker
                      v-model="form.expiration_date"
                      type="date"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                      style="width: 100%"
                    />
                  </ElFormItem>
                </ElCol>
              </ElRow>

              <!-- Remark -->
              <ElFormItem :label="t('erp.izoh')" prop="remark" class="!mb-0">
                <ElInput v-model="form.remark" type="textarea" :rows="2" />
              </ElFormItem>
            </ElForm>
          </div>
        </div>
      </div>

      <template #footer>
        <ElButton @click="dialogVisible = false">{{ t('common.cancel') }}</ElButton>
        <ElButton type="primary" :loading="submitLoading" @click="handleSubmit">{{
          t('common.save')
        }}</ElButton>
      </template>
    </ResizeDialog>

    <!-- Product Detail Resizable & Draggable Modal Dialog -->
    <ResizeDialog
      v-model="detailDialogVisible"
      title="Mahsulotning To'liq Tafsilotlari"
      storage-key="product_detail_full_v3"
      :init-width="dialogInitWidth"
      :init-height="dialogInitHeight"
      :min-resize-width="700"
      :min-resize-height="480"
    >
      <div
        v-if="detailProduct"
        class="product-detail-modal p-4px flex flex-col h-full space-y-20px text-[var(--el-text-color-primary)]"
      >
        <!-- Top Banner: Image & Main Title Header -->
        <div
          class="flex flex-col md:flex-row gap-24px items-center md:items-start bg-[var(--el-fill-color-light)] dark:bg-gray-900/90 p-24px rounded-16px border border-[var(--el-border-color-lighter)] dark:border-gray-800 shadow-sm"
        >
          <!-- Main Thumbnail / Gallery Image -->
          <div
            class="relative w-180px h-180px md:w-200px md:h-200px rounded-16px overflow-hidden border border-[var(--el-border-color-lighter)] dark:border-gray-700/80 shadow-md flex-shrink-0 bg-[var(--el-fill-color-blank)] dark:bg-gray-950 flex items-center justify-center group"
          >
            <ElImage
              v-if="getProductMainImage(detailProduct)"
              :src="getProductMainImage(detailProduct)"
              :preview-src-list="getProductImageGallery(detailProduct)"
              preview-teleported
              fit="cover"
              class="w-full h-full cursor-pointer group-hover:scale-108 transition-transform duration-300"
            >
              <template #error>
                <div
                  class="w-full h-full flex flex-col items-center justify-center text-[var(--el-text-color-placeholder)]"
                >
                  <Icon icon="ep:picture" class="text-44px" />
                  <span class="text-12px mt-6px">Rasm yo'q</span>
                </div>
              </template>
            </ElImage>
            <div
              v-else
              class="w-full h-full flex flex-col items-center justify-center text-[var(--el-text-color-placeholder)]"
            >
              <Icon icon="ep:picture" class="text-44px" />
              <span class="text-12px mt-6px">Rasm yo'q</span>
            </div>
          </div>

          <!-- Title & Badges Header -->
          <div class="flex-1 min-w-0 space-y-12px">
            <div class="flex flex-wrap items-center gap-10px">
              <ElTag
                v-if="detailProduct.category"
                type="primary"
                effect="dark"
                size="large"
                class="rounded-pill font-bold px-14px py-6px text-13px"
              >
                {{ detailProduct.category }}
              </ElTag>
              <ElTag
                v-if="detailProduct.brand_name"
                type="success"
                effect="light"
                size="large"
                class="rounded-pill font-bold px-14px py-6px text-13px"
              >
                {{ detailProduct.brand_name }}
              </ElTag>
              <ElTag
                :type="
                  (detailProduct.quantityInStock || 0) > 10
                    ? 'success'
                    : (detailProduct.quantityInStock || 0) > 0
                      ? 'warning'
                      : 'danger'
                "
                effect="dark"
                size="large"
                class="rounded-pill font-bold px-14px py-6px text-13px"
              >
                Omborda: {{ formatMoney(detailProduct.quantityInStock) }}
                {{ detailProduct.unit || 'dona' }}
              </ElTag>
            </div>

            <h2
              class="text-22px md:text-26px font-extrabold text-[var(--el-text-color-primary)] leading-snug break-words tracking-tight"
            >
              {{ detailProduct.productName }}
            </h2>

            <div
              v-if="detailProduct.attribute_name"
              class="text-15px text-[var(--el-text-color-secondary)] italic"
            >
              {{ detailProduct.attribute_name }}
            </div>

            <!-- Codes Grid -->
            <div class="flex flex-wrap gap-12px pt-8px">
              <div
                v-if="detailProduct.shtrix_code"
                class="text-14px font-mono bg-[var(--el-fill-color-light)] dark:bg-gray-800/90 px-12px py-6px rounded-8px border border-[var(--el-border-color-lighter)] dark:border-gray-700 text-blue-500 font-semibold shadow-sm"
              >
                <span class="text-[var(--el-text-color-secondary)] font-sans font-normal"
                  >Shtrix-kod:</span
                >
                {{ detailProduct.shtrix_code }}
              </div>
              <div
                v-if="detailProduct.mxik_code"
                class="text-14px font-mono bg-[var(--el-fill-color-light)] dark:bg-gray-800/90 px-12px py-6px rounded-8px border border-[var(--el-border-color-lighter)] dark:border-gray-700 text-purple-500 font-semibold shadow-sm"
              >
                <span class="text-[var(--el-text-color-secondary)] font-sans font-normal"
                  >MXIK:</span
                >
                {{ detailProduct.mxik_code }}
              </div>
              <div
                v-if="detailProduct.SKU"
                class="text-14px font-mono bg-[var(--el-fill-color-light)] dark:bg-gray-800/90 px-12px py-6px rounded-8px border border-[var(--el-border-color-lighter)] dark:border-gray-700 text-emerald-500 font-semibold shadow-sm"
              >
                <span class="text-[var(--el-text-color-secondary)] font-sans font-normal"
                  >SKU:</span
                >
                {{ detailProduct.SKU }}
              </div>
            </div>
          </div>
        </div>

        <!-- Financial Breakdown Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-18px">
          <!-- Cost Price -->
          <div
            class="bg-[var(--el-fill-color-light)] dark:bg-gray-900/90 p-18px rounded-14px border border-amber-500/30 shadow-md hover:border-amber-500/60 transition-colors"
          >
            <span class="text-14px text-[var(--el-text-color-secondary)] block mb-6px font-medium"
              >Tannarxi (Xarid)</span
            >
            <div class="text-28px font-mono font-extrabold text-amber-500">
              ${{ formatMoney(detailProduct.cost) }}
            </div>
          </div>

          <!-- Selling Price -->
          <div
            class="bg-[var(--el-fill-color-light)] dark:bg-gray-900/90 p-18px rounded-14px border border-emerald-500/30 shadow-md hover:border-emerald-500/60 transition-colors"
          >
            <span class="text-14px text-[var(--el-text-color-secondary)] block mb-6px font-medium"
              >Sotuv Narxi</span
            >
            <div class="text-28px font-mono font-extrabold text-emerald-500">
              ${{ formatMoney(detailProduct.price) }}
            </div>
          </div>

          <!-- Profit / Margin -->
          <div
            class="bg-[var(--el-fill-color-light)] dark:bg-gray-900/90 p-18px rounded-14px border border-blue-500/30 shadow-md hover:border-blue-500/60 transition-colors"
          >
            <span class="text-14px text-[var(--el-text-color-secondary)] block mb-6px font-medium"
              >Birlik Foyda (Marja)</span
            >
            <div class="text-28px font-mono font-extrabold text-blue-500">
              +${{ formatMoney((detailProduct.price || 0) - (detailProduct.cost || 0)) }}
            </div>
          </div>
        </div>

        <!-- Packaging Options Preview -->
        <div
          v-if="detailProduct.packagings && detailProduct.packagings.length > 0"
          class="bg-[var(--el-fill-color-light)] dark:bg-gray-900/90 rounded-14px p-16px border border-blue-500/40 shadow-sm space-y-10px"
        >
          <span class="text-14px font-bold text-blue-500 flex items-center gap-6px">
            <Icon icon="ep:box" /> Qadoqlash va Paket Turlari (Ko'p Birlikda Sotuv Narxlari):
          </span>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10px">
            <div
              v-for="pkg in detailProduct.packagings"
              :key="pkg.unit_name"
              class="p-10px rounded-10px bg-[var(--el-fill-color-blank)] border border-[var(--el-border-color)] flex justify-between items-center shadow-xs"
            >
              <div>
                <div class="font-bold text-13px text-[var(--el-text-color-primary)]">{{
                  pkg.unit_name
                }}</div>
                <div class="text-11px text-[var(--el-text-color-secondary)] font-mono mt-2px">
                  1 {{ pkg.unit_name }} = {{ pkg.conversion_factor }}
                  {{ detailProduct.unit || 'kg' }}
                </div>
                <div v-if="pkg.shtrix_code" class="text-10px text-blue-500 font-mono mt-1px">
                  Shtrix: {{ pkg.shtrix_code }}
                </div>
              </div>
              <div class="font-mono font-extrabold text-emerald-500 text-16px pl-8px">
                ${{ formatMoney(pkg.price) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 2-Column Responsive Extra Info & Description Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-20px flex-1">
          <!-- Extra Information Table -->
          <div
            class="bg-[var(--el-fill-color-light)] dark:bg-gray-900/80 rounded-14px p-20px border border-[var(--el-border-color-lighter)] dark:border-gray-800 space-y-12px text-15px flex flex-col justify-between shadow-sm"
          >
            <div class="space-y-12px">
              <div
                class="flex justify-between border-b border-[var(--el-border-color-lighter)] dark:border-gray-800 pb-8px"
              >
                <span class="text-[var(--el-text-color-secondary)]">ID / Kodi:</span>
                <span class="font-mono text-[var(--el-text-color-primary)] font-bold">{{
                  detailProduct.id
                }}</span>
              </div>
              <div
                class="flex justify-between border-b border-[var(--el-border-color-lighter)] dark:border-gray-800 pb-8px"
              >
                <span class="text-[var(--el-text-color-secondary)]">O'lchov Birligi:</span>
                <span class="font-bold text-[var(--el-text-color-primary)]">{{
                  detailProduct.unit || 'dona'
                }}</span>
              </div>
              <div
                class="flex justify-between border-b border-[var(--el-border-color-lighter)] dark:border-gray-800 pb-8px"
              >
                <span class="text-[var(--el-text-color-secondary)]"
                  >Jami Ombor Qiymati (Tannarx):</span
                >
                <span class="font-mono font-bold text-amber-500"
                  >${{
                    formatMoney((detailProduct.cost || 0) * (detailProduct.quantityInStock || 0))
                  }}</span
                >
              </div>
              <div
                class="flex justify-between border-b border-[var(--el-border-color-lighter)] dark:border-gray-800 pb-8px"
              >
                <span class="text-[var(--el-text-color-secondary)]"
                  >Jami Ombor Qiymati (Sotuv):</span
                >
                <span class="font-mono font-bold text-emerald-500"
                  >${{
                    formatMoney((detailProduct.price || 0) * (detailProduct.quantityInStock || 0))
                  }}</span
                >
              </div>
            </div>
            <div
              v-if="detailProduct.createTime"
              class="flex justify-between pt-8px border-t border-[var(--el-border-color-lighter)] dark:border-gray-800/60"
            >
              <span class="text-[var(--el-text-color-secondary)]">Qo'shilgan vaqti:</span>
              <span class="text-[var(--el-text-color-regular)] font-mono">{{
                detailProduct.createTime
              }}</span>
            </div>
          </div>

          <!-- Description / Izoh -->
          <div
            class="bg-[var(--el-fill-color-light)] dark:bg-gray-900/80 p-20px rounded-14px border border-[var(--el-border-color-lighter)] dark:border-gray-800 flex flex-col justify-between shadow-sm"
          >
            <div>
              <span
                class="text-13px text-[var(--el-text-color-secondary)] block mb-8px font-bold uppercase tracking-wider"
                >Qo'shimcha Izoh & Klassifikator:</span
              >
              <p
                class="text-15px text-[var(--el-text-color-regular)] leading-relaxed whitespace-pre-wrap"
              >
                {{ detailProduct.remark || "Ushbu mahsulot uchun qo'shimcha izoh kiritilmagan." }}
              </p>
            </div>
            <div
              class="pt-16px text-12px text-[var(--el-text-color-placeholder)] italic border-t border-[var(--el-border-color-lighter)] dark:border-gray-800/60 mt-12px"
            >
              Klassifikator va Tasnif Soliq orqali avtomatik tekshirilgan hamda tasdiqlangan.
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center w-full">
          <div class="flex gap-12px">
            <ElButton
              type="primary"
              plain
              size="large"
              class="!px-20px"
              @click="openEditFromDetail"
            >
              <Icon icon="ep:edit" class="mr-8px" />{{ t('common.edit') }}</ElButton
            >
            <ElButton type="danger" plain size="large" class="!px-20px" @click="deleteFromDetail">
              <Icon icon="ep:delete" class="mr-8px" />{{ t('common.delete') }}</ElButton
            >
          </div>
          <ElButton size="large" class="!px-24px" @click="detailDialogVisible = false">{{
            t('common.close')
          }}</ElButton>
        </div>
      </template>
    </ResizeDialog>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
defineOptions({ name: 'Product' })
import { ref, reactive, onMounted, computed, nextTick } from 'vue'

import { ContentWrap } from '@/components/ContentWrap'
import { ResizeDialog } from '@/components/Dialog'
import { Icon } from '@/components/Icon'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'
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
  ElRadioGroup,
  ElRadioButton,
  ElMessage,
  ElMessageBox,
  ElNotification,
  ElImage,
  ElUpload,
  FormInstance
} from 'element-plus'

import {
  getProductListApi,
  saveProductApi,
  deleteProductApi,
  checkExistingProductApi,
  uploadProductImageApi,
  searchClassifierApi,
  getClassifierByBarcodeApi,
  ProductType
} from '@/api/product'
import {
  getProductMainImage,
  getProductImageGallery,
  fetchTasnifPictureNames,
  handleImageError
} from '@/utils/productImages'

const dialogInitWidth = Math.min(window.innerWidth * 0.92, 1400)
const dialogInitHeight = Math.min(window.innerHeight * 0.88, 800)

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<ProductType[]>([])
const total = ref(0)
const selectedIds = ref<string[]>([])

const searchQuery = reactive({
  productName: '',
  category: ''
})

const pagination = reactive({
  pageIndex: 1,
  pageSize: 10
})

// Number formatting with space thousand separators (e.g. 1 500 000 or 1 000 000)
const formatMoney = (val: number | string | undefined | null) => {
  if (val === undefined || val === null || val === '') return '0'
  const num = Number(val)
  if (isNaN(num)) return '0'
  const isNegative = num < 0
  const absNum = Math.abs(Math.round(num))
  const formatted = absNum.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  return isNegative ? `-${formatted}` : formatted
}

// Stats calculation
const stats = computed(() => {
  const totalTypes = total.value
  let totalStock = 0
  let totalCost = 0
  let totalPrice = 0
  tableData.value.forEach((p) => {
    const qty = p.quantityInStock || 0
    totalStock += qty
    totalCost += (p.cost || 0) * qty
    totalPrice += (p.price || 0) * qty
  })
  return { totalTypes, totalStock, totalCost, totalPrice }
})

// Dialog and Classifier States
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const barcodeInputRef = ref<any>(null)
const barcodeSearch = ref('')
const barcodeLoading = ref(false)
const classifierLoading = ref(false)
const classifierSearchMode = ref<'extended' | 'simple'>('extended')
const lastClassifierQuery = ref('')
const classifierOptions = ref<any[]>([])
const selectedClassifierId = ref<number | string | undefined>(undefined)
const existingProduct = ref<ProductType | null>(null)
const checkingExistingLoading = ref(false)

const form = reactive<ProductType>({
  id: '',
  productName: '',
  SKU: '',
  category: 'Ichimliklar va suvlar',
  price: 0,
  cost: 0,
  quantityInStock: 1,
  status: 1,
  classifier_id: undefined,
  shtrix_code: '',
  mxik_code: '',
  brand_name: '',
  attribute_name: '',
  unit: 'dona',
  image_url: '',
  expiration_date: '',
  min_stock: 10,
  remark: ''
})

const hasAlertedLowStock = ref(false)

const lowStockItems = computed(() => {
  return tableData.value.filter((p) => {
    const threshold = p.min_stock !== undefined && p.min_stock !== null ? p.min_stock : 10
    return (p.quantityInStock || 0) <= threshold
  })
})

const profitAmount = computed(() => {
  if (!form.price || !form.cost) return 0
  return Number(form.price) - Number(form.cost)
})

const profitPercent = computed(() => {
  if (!form.cost || !form.price || Number(form.cost) <= 0) return 0
  const diff = Number(form.price) - Number(form.cost)
  return Math.round((diff / Number(form.cost)) * 100)
})

const isExpired = (dateStr?: string) => {
  if (!dateStr) return false
  const target = new Date(dateStr)
  if (isNaN(target.getTime())) return false
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  return target.getTime() < now.getTime()
}

const isExpiringSoon = (dateStr?: string) => {
  if (!dateStr) return false
  const target = new Date(dateStr)
  if (isNaN(target.getTime())) return false
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  const diffDays = Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  return diffDays >= 0 && diffDays <= 30
}

// Real-time space thousand separators formatting (e.g. 122 222 or 1 500 000)
const displayCost = computed({
  get: () => {
    if (form.cost === undefined || form.cost === null || form.cost === 0) return ''
    return form.cost.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set: (val: string) => {
    const digits = val.replace(/\D/g, '')
    form.cost = digits ? parseInt(digits, 10) : 0
  }
})

const displayPrice = computed({
  get: () => {
    if (form.price === undefined || form.price === null || form.price === 0) return ''
    return form.price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set: (val: string) => {
    const digits = val.replace(/\D/g, '')
    form.price = digits ? parseInt(digits, 10) : 0
  }
})

const copyBarcode = async (code: string) => {
  if (!code) return
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(code)
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = code
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
    ElMessage.success(`Shtrix kod nusxalandi: ${code}`)
  } catch {
    ElMessage.error('Nusxalashda xatolik yuz berdi')
  }
}

const validateCost = (_rule: any, _value: any, callback: any) => {
  if (form.cost === undefined || form.cost === null || form.cost < 0) {
    callback(new Error("Iltimos, tannarxini kiriting (0 dan katta bo'lishi shart)"))
  } else {
    callback()
  }
}

const validatePrice = (_rule: any, _value: any, callback: any) => {
  if (form.price === undefined || form.price === null || form.price <= 0) {
    callback(new Error("Iltimos, sotish narxini kiriting (0 dan katta bo'lishi shart)"))
  } else {
    callback()
  }
}

const rules = {
  productName: [{ required: true, message: 'Iltimos, mahsulot nomini kiriting', trigger: 'blur' }],
  SKU: [{ required: true, message: 'Iltimos, SKU kodingizni kiriting', trigger: 'blur' }],
  category: [{ required: true, message: 'Iltimos, kategoriyani tanlang', trigger: 'change' }],
  cost: [{ required: true, validator: validateCost, trigger: 'blur' }],
  price: [{ required: true, validator: validatePrice, trigger: 'blur' }]
}

const fetchTableData = async (silent = false) => {
  if (!silent) {
    loading.value = true
  }
  try {
    const res = await getProductListApi({
      productName: searchQuery.productName || undefined,
      category: searchQuery.category || undefined,
      pageIndex: pagination.pageIndex,
      pageSize: pagination.pageSize
    })
    if (res && res.data) {
      tableData.value = res.data.list || []
      total.value = res.data.total || 0

      // Low stock notification on initial page load (concise & punchy)
      if (!silent && !hasAlertedLowStock.value) {
        const lows = tableData.value.filter(
          (p) => (p.quantityInStock || 0) <= (p.min_stock !== undefined && p.min_stock !== null ? p.min_stock : 10)
        )
        if (lows.length > 0) {
          hasAlertedLowStock.value = true
          if (lows.length === 1) {
            ElMessage.warning(`"${lows[0].productName}" kam qoldi (${lows[0].quantityInStock} dona). Omborga to'ldiring!`)
          } else {
            ElMessage.warning(`${lows.length} ta mahsulot kam qoldi. Omborga to'ldiring!`)
          }
        }
      }

      // Pre-fetch real picture names from Tasnif API for all products
      Promise.all(
        (tableData.value || []).map((p) =>
          p.mxik_code ? fetchTasnifPictureNames(p.mxik_code) : Promise.resolve([])
        )
      )
    }
  } catch (error) {
    console.error('Failed to load ombor products:', error)
  } finally {
    if (!silent) {
      loading.value = false
    }
  }
}

// Subscribe to real-time product mutations for zero-flicker background sync
useRealtimeSync('product', () => {
  fetchTableData(true)
})

import { exportToExcel } from '@/utils/exportReport'

const exportLoading = ref(false)
const handleExportExcel = async () => {
  try {
    exportLoading.value = true
    ElMessage.info('Barcha mahsulotlar maʼlumotlari yuklanmoqda...')
    const res = await getProductListApi({
      pageIndex: 1,
      pageSize: 50000,
      productName: searchQuery.productName || undefined,
      category: searchQuery.category || undefined
    })
    const allProducts = res?.data?.list || tableData.value || []
    if (allProducts.length === 0) {
      ElMessage.warning('Eksport qilish uchun mahsulotlar mavjud emas')
      return
    }
    exportToExcel(
      'Barcha_Ombor_Mahsulotlari',
      [
        { key: 'id', title: 'ID / Kod' },
        { key: 'productName', title: 'Mahsulot Nomi' },
        { key: 'shtrix_code', title: 'Shtrix-Kod' },
        { key: 'category', title: 'Kategoriya' },
        { key: 'cost', title: 'Tannarx ($)', formatter: (v) => formatMoney(v || 0) },
        { key: 'price', title: 'Sotuv Narxi ($)', formatter: (v) => formatMoney(v || 0) },
        { key: 'quantityInStock', title: 'Qoldiq Miqdor' },
        { key: 'unit', title: 'O‘lchov Birligi' },
        { key: 'brand_name', title: 'Brend' }
      ],
      allProducts
    )
    ElMessage.success(`Barcha (${allProducts.length} ta) mahsulotlar Excel fayliga yuklab olindi!`)
  } catch (err: any) {
    console.error(err)
    ElMessage.error(err.message || 'Excelga eksport qilishda xatolik yuz berdi')
  } finally {
    exportLoading.value = false
  }
}

const handleSearch = () => {
  pagination.pageIndex = 1
  fetchTableData()
}

const resetSearch = () => {
  searchQuery.productName = ''
  searchQuery.category = ''
  handleSearch()
}

const handleSelectionChange = (selection: ProductType[]) => {
  selectedIds.value = selection.map((item) => item.id!).filter(Boolean)
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  fetchTableData()
}

const handleCurrentChange = (val: number) => {
  pagination.pageIndex = val
  fetchTableData()
}

// Classifier Autocomplete & Barcode Scan with Client-side Caching & Debounce
const classifierCacheMap = new Map<string, any[]>()
let searchDebounceTimer: any = null

const onClassifierSearchModeChange = () => {
  classifierCacheMap.clear()
  if (lastClassifierQuery.value) {
    remoteSearchClassifier(lastClassifierQuery.value)
  }
}

const remoteSearchClassifier = (query: string) => {
  if (!query || query.trim().length < 2) {
    classifierOptions.value = []
    lastClassifierQuery.value = ''
    return
  }
  const cleanQ = query.trim()
  lastClassifierQuery.value = cleanQ
  const cacheKey = `${classifierSearchMode.value}:${cleanQ}`
  if (classifierCacheMap.has(cacheKey)) {
    classifierOptions.value = classifierCacheMap.get(cacheKey) || []
    return
  }

  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)

  searchDebounceTimer = setTimeout(async () => {
    classifierLoading.value = true
    try {
      const res = await searchClassifierApi({
        search: cleanQ,
        mode: classifierSearchMode.value,
        page: 1,
        page_size: 25
      })
      if (res && res.data) {
        const list = Array.isArray(res.data) ? res.data : (res.data as any).list || []
        classifierOptions.value = list
        classifierCacheMap.set(cacheKey, list)
      }
    } catch (err) {
      console.error('Classifier search error:', err)
    } finally {
      classifierLoading.value = false
    }
  }, 150)
}

const checkAndApplyExistingProduct = async (criteria: {
  barcode?: string
  sku?: string
  name?: string
  classifierId?: string | number
}): Promise<ProductType | null> => {
  const barcode = (criteria.barcode || '').trim()
  const sku = (criteria.sku || '').trim()
  const name = (criteria.name || '').trim()
  const classifierId = criteria.classifierId ? String(criteria.classifierId).trim() : ''

  if (!barcode && !sku && !name && !classifierId) {
    return null
  }

  // 1. Fast check in current loaded tableData
  let found: ProductType | undefined = tableData.value.find((p) => {
    if (barcode && p.shtrix_code && String(p.shtrix_code).trim() === barcode) return true
    if (sku && p.SKU && p.SKU.toLowerCase() === sku.toLowerCase()) return true
    if (classifierId && p.classifier_id && String(p.classifier_id) === classifierId) return true
    if (name && p.productName && p.productName.toLowerCase() === name.toLowerCase()) return true
    return false
  })

  // 2. If not found in loaded tableData, query backend endpoint
  if (!found) {
    try {
      checkingExistingLoading.value = true
      const res: any = await checkExistingProductApi({
        barcode: barcode || undefined,
        sku: sku || undefined,
        name: name || undefined,
        classifier_id: classifierId || undefined
      })
      const info = res?.data?.data || (res?.data?.exists !== undefined ? res?.data : res)
      if (info && (info.exists || info.id) && (info.data || info.id)) {
        found = info.data || info
      }
    } catch (e) {
      console.warn('checkExistingProductApi warning:', e)
    } finally {
      checkingExistingLoading.value = false
    }
  }

  if (found) {
    existingProduct.value = found
    form.id = found.id || ''
    form.cost = found.cost || 0
    form.price = found.price || 0
    form.category = found.category || form.category || 'Ichimliklar va suvlar'
    form.unit = found.unit || 'dona'
    form.productName = found.productName || form.productName
    form.shtrix_code = found.shtrix_code || form.shtrix_code || barcode
    form.SKU = found.SKU || form.SKU || (barcode ? `SKU-${barcode}` : '')
    form.brand_name = found.brand_name || form.brand_name
    form.attribute_name = found.attribute_name || form.attribute_name
    form.mxik_code = found.mxik_code || form.mxik_code
    form.image_url = found.image_url || form.image_url
    form.remark = found.remark || form.remark
    form.min_stock = found.min_stock !== undefined && found.min_stock !== null ? found.min_stock : 10
    form.expiration_date = found.expiration_date || ''
    // Default the quantity field to 1 (new batch count)
    form.quantityInStock = 1

    ElNotification({
      title: 'Omborda mavjud mahsulot topildi!',
      message: `"${found.productName}" mahsuloti omborda mavjud. Hozirgi ombor qoldig'i: ${formatMoney(found.quantityInStock)} ${found.unit || 'dona'}. Eski tannarxi: $${formatMoney(found.cost)}, Eski sotish narxi: $${formatMoney(found.price)}. Yangi kirim sonini kiriting.`,
      type: 'warning',
      duration: 7000
    })

    return found
  }

  // Not found in warehouse: ensure product is treated as a clean new item
  existingProduct.value = null
  form.id = ''
  form.cost = 0
  form.price = 0
  form.quantityInStock = 1
  form.min_stock = 10
  form.expiration_date = ''

  return null
}

const clearProductFields = () => {
  existingProduct.value = null
  form.id = ''
  form.productName = ''
  form.SKU = ''
  form.category = 'Boshqalar'
  form.price = 0
  form.cost = 0
  form.quantityInStock = 1
  form.status = 1
  form.classifier_id = undefined
  form.shtrix_code = ''
  form.mxik_code = ''
  form.brand_name = ''
  form.attribute_name = ''
  form.unit = 'dona'
  form.image_url = ''
  form.min_stock = 10
  form.expiration_date = ''
  form.remark = ''
  form.packagings = []
}

const detectCategory = (item: any): string => {
  if (!item) return 'Boshqalar'
  const text = `${item.category_name || ''} ${item.group_name || ''} ${item.class_name || ''} ${item.position_name || ''} ${item.mxik_name || ''}`.toLowerCase()
  if (
    text.includes('ichimlik') ||
    text.includes('suv') ||
    text.includes('sok') ||
    text.includes('sharbat') ||
    text.includes('choy') ||
    text.includes('kofe') ||
    text.includes('napitk') ||
    text.includes('cola') ||
    text.includes('pepsi')
  ) {
    return 'Ichimliklar va suvlar'
  }
  if (
    text.includes('sut') ||
    text.includes('qatiq') ||
    text.includes('pishloq') ||
    text.includes('tvorog') ||
    text.includes('kefir') ||
    text.includes('yogurt') ||
    text.includes('qaymoq') ||
    text.includes('sariyog')
  ) {
    return 'Sut va sut mahsulotlari'
  }
  if (
    text.includes('tuz') ||
    text.includes('ziravor') ||
    text.includes('qalampir') ||
    text.includes('murch') ||
    text.includes('sous') ||
    text.includes('sirka')
  ) {
    return 'Tuz va ziravorlar'
  }
  if (
    text.includes('plast') ||
    text.includes('idish') ||
    text.includes('paket') ||
    text.includes('quti') ||
    text.includes('upakovka')
  ) {
    return 'Plastmassa va idishlar'
  }
  if (
    text.includes('elektr') ||
    text.includes('plita') ||
    text.includes('pech') ||
    text.includes('muzlat') ||
    text.includes('kir yuv') ||
    text.includes('televizor') ||
    text.includes('telefon') ||
    text.includes('gaz') ||
    text.includes('gefest') ||
    text.includes('artel') ||
    text.includes('konditsioner') ||
    text.includes('changyutgich')
  ) {
    return 'Maishiy texnika va elektronika'
  }
  if (
    text.includes('oziq') ||
    text.includes('non') ||
    text.includes('un') ||
    text.includes('shakar') ||
    text.includes('shokolad') ||
    text.includes('konfet') ||
    text.includes("go'sht") ||
    text.includes('kolbasa') ||
    text.includes('makaron') ||
    text.includes("yog'")
  ) {
    return 'Oziq-ovqat mahsulotlari'
  }
  if (
    text.includes('kiyim') ||
    text.includes('poyabzal') ||
    text.includes('shim') ||
    text.includes('kofta') ||
    text.includes('kurtka')
  ) {
    return 'Kiyim-kechak va poyabzal'
  }
  if (
    text.includes('qurilish') ||
    text.includes('sement') ||
    text.includes("bo'yoq") ||
    text.includes('mix') ||
    text.includes('truba')
  ) {
    return "Qurilish va ta'mirlash"
  }
  if (item.category_name && item.category_name.trim()) return item.category_name.trim()
  if (item.group_name && item.group_name.trim()) return item.group_name.trim()
  if (item.class_name && item.class_name.trim()) return item.class_name.trim()
  if (item.position_name && item.position_name.trim()) return item.position_name.trim()
  return 'Boshqalar'
}

const onShtrixCodeBlur = async () => {
  if (dialogType.value === 'add' && form.shtrix_code && form.shtrix_code.length >= 4) {
    await checkAndApplyExistingProduct({ barcode: form.shtrix_code })
  }
}

const applyClassifierToForm = async (item: any) => {
  if (!item) return

  // 1. Reset previous product data first so old prices/ids don't linger
  clearProductFields()

  // 2. Populate classifier attributes
  form.classifier_id = item.id ? String(item.id) : (item.mxik_code ? String(item.mxik_code) : '')
  form.productName = item.mxik_name || ''
  form.brand_name = item.brand_name || ''
  form.mxik_code = item.mxik_code || ''
  form.shtrix_code = item.shtrix_code || ''
  form.attribute_name = item.attribute_name || ''
  form.unit = item.unit || 'dona'
  form.category = detectCategory(item)
  if (item.shtrix_code) {
    form.SKU = `SKU-${item.shtrix_code}`
  } else if (item.mxik_code) {
    form.SKU = `SKU-${item.mxik_code}`
  }

  // Populate description (Izoh) from classifier fields
  const descParts: string[] = []
  if (item.position_name) descParts.push(item.position_name)
  if (item.subposition_name && item.subposition_name !== item.position_name) {
    descParts.push(item.subposition_name)
  }
  if (item.unit_group) descParts.push(`Qadoq: ${item.unit_group}`)

  form.remark = descParts.length > 0 ? descParts.join(' | ') : item.mxik_name || ''

  // 3. Clear search inputs
  barcodeSearch.value = ''
  selectedClassifierId.value = undefined

  // 4. Check if this product already exists in warehouse:
  const existing = await checkAndApplyExistingProduct({
    barcode: item.shtrix_code,
    sku: form.SKU,
    name: item.mxik_name,
    classifierId: form.classifier_id
  })

  if (!existing) {
    existingProduct.value = null
    form.id = ''
    form.cost = 0
    form.price = 0
    form.quantityInStock = 1
    ElMessage.success(`Klassifikator ma'lumotlari yuklandi: ${item.brand_name || item.mxik_name}`)
  }
}

const handleClassifierSelect = (val: number | string) => {
  if (!val) return
  const found = classifierOptions.value.find(
    (c) =>
      String(c.id) === String(val) ||
      String(c.mxik_code) === String(val) ||
      String(c.shtrix_code) === String(val)
  )
  if (found) {
    applyClassifierToForm(found)
  }
  selectedClassifierId.value = undefined
}

const handleBarcodeScan = async () => {
  const code = barcodeSearch.value.replace(/\D/g, '')
  if (!code) {
    ElMessage.warning('Iltimos, shtrix-kodni faqat raqamlarda kiriting')
    return
  }
  barcodeLoading.value = true
  try {
    // 1. Reset old product fields before scanning new barcode
    clearProductFields()

    // 2. First check if barcode already exists in warehouse!
    const existing = await checkAndApplyExistingProduct({ barcode: code })
    if (existing) {
      barcodeSearch.value = ''
      nextTick(() => {
        barcodeInputRef.value?.focus?.()
      })
      return
    }

    // 3. If not in warehouse, search Tasnif classifier
    const res = await getClassifierByBarcodeApi(code)
    if (res && res.data) {
      await applyClassifierToForm(res.data)
      barcodeSearch.value = ''
      nextTick(() => {
        barcodeInputRef.value?.focus?.()
      })
    } else {
      ElMessage.warning("Ushbu shtrix-kod bo'yicha klassifikator topilmadi")
      form.shtrix_code = code
      form.SKU = `SKU-${code}`
      form.category = 'Boshqalar'
      barcodeSearch.value = ''
      nextTick(() => {
        barcodeInputRef.value?.focus?.()
      })
    }
  } catch (err) {
    ElMessage.error("Shtrix-kod bo'yicha qidirishda xatolik")
  } finally {
    barcodeLoading.value = false
  }
}

const resetForm = () => {
  clearProductFields()
  barcodeSearch.value = ''
  selectedClassifierId.value = undefined
  classifierOptions.value = []
}

const handleImageChange = async (uploadFile: any) => {
  const file = uploadFile.raw
  if (!file) return
  try {
    const res = await uploadProductImageApi(file)
    if (res && res.data && res.data.url) {
      form.image_url = res.data.url
      ElMessage.success('Rasm muvaffaqiyatli yuklandi')
    }
  } catch (error) {
    console.error('Failed to upload image:', error)
    ElMessage.error('Rasm yuklashda xatolik yuz berdi')
  }
}

const openAddDialog = () => {
  dialogType.value = 'add'
  resetForm()
  dialogVisible.value = true
  nextTick(() => {
    barcodeInputRef.value?.focus?.()
  })
}

const openEditDialog = (row: ProductType) => {
  dialogType.value = 'edit'
  resetForm()
  Object.assign(form, row)
  form.min_stock = row.min_stock !== undefined && row.min_stock !== null ? row.min_stock : 10
  form.expiration_date = row.expiration_date || ''
  form.packagings = row.packagings ? JSON.parse(JSON.stringify(row.packagings)) : []
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (!form.SKU) {
          form.SKU = `SKU-${Date.now().toString().slice(-6)}`
        }

        const payload: any = { ...form }
        if (dialogType.value === 'add' && existingProduct.value) {
          payload.id = existingProduct.value.id
          payload.is_replenish = true
          payload.additional_qty = Number(form.quantityInStock) || 0
        }

        const res: any = await saveProductApi(payload)

        if (res && (res.is_existing || res.added_qty !== undefined)) {
          ElNotification({
            title: 'Ombor muvaffaqiyatli yangilandi!',
            message: `"${res.product_name || form.productName}" mahsulotiga +${res.added_qty || form.quantityInStock} dona qo'shildi. Ombordagi yangi umumiy qoldiq: ${formatMoney(res.total_stock)} dona!`,
            type: 'success',
            duration: 8000
          })
        } else {
          ElMessage.success(
            dialogType.value === 'add' ? "Mahsulot omborga qo'shildi" : 'Mahsulot tahrirlandi'
          )
        }

        dialogVisible.value = false
        fetchTableData()
      } catch (err) {
        ElMessage.error('Saqlashda xatolik yuz berdi')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = (row: ProductType) => {
  ElMessageBox.confirm(
    `"${row.productName}" mahsulotini o'chirishga ishonchingiz komilmi?`,
    'Ogohlantirish',
    {
      confirmButtonText: "O'chirish",
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteProductApi({ ids: [row.id!] })
      ElMessage.success("Mahsulot o'chirildi")
      fetchTableData()
    } catch (err) {
      ElMessage.error("O'chirishda xatolik yuz berdi")
    }
  })
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return
  ElMessageBox.confirm(
    `Tanlangan ${selectedIds.value.length} ta mahsulotni o'chirishga ishonchingiz komilmi?`,
    'Ogohlantirish',
    {
      confirmButtonText: "O'chirish",
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteProductApi({ ids: selectedIds.value })
      ElMessage.success("Mahsulotlar o'chirildi")
      selectedIds.value = []
      fetchTableData()
    } catch (err) {
      ElMessage.error("O'chirishda xatolik yuz berdi")
    }
  })
}

import { useEventBus } from '@/hooks/event/useEventBus'

useEventBus({
  name: 'refresh-products',
  callback: () => {
    fetchTableData()
  }
})

useEventBus({
  name: 'ai-data-updated',
  callback: () => {
    fetchTableData()
  }
})

onMounted(() => {
  fetchTableData()
})

const detailDialogVisible = ref(false)
const detailProduct = ref<ProductType | null>(null)

const handleRowClick = (row: ProductType, column: any) => {
  if (column && (column.type === 'selection' || column.label === 'Amallar')) {
    return
  }
  detailProduct.value = row
  detailDialogVisible.value = true
}

const openEditFromDetail = () => {
  if (detailProduct.value) {
    const target = detailProduct.value
    detailDialogVisible.value = false
    openEditDialog(target)
  }
}

const deleteFromDetail = () => {
  if (detailProduct.value) {
    const target = detailProduct.value
    detailDialogVisible.value = false
    handleDelete(target)
  }
}
</script>

<style scoped lang="less">
.ombor-container {
  .stat-card {
    padding: 16px;
    border-radius: 10px;
    background: var(--el-bg-color-overlay, #ffffff);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
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
    white-space: nowrap;
  }

  .stat-number {
    font-size: 20px;
    font-weight: 800;
    margin-top: 2px;
    color: var(--el-text-color-primary, #0f172a);
    font-family: 'SF Mono', monospace, ui-monospace;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
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
    width: 320px;
  }

  .category-select {
    width: 220px;
  }

  .add-btn {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    border: none;
    font-weight: 600;

    &:hover {
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
    }
  }

  .shadow-btn {
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
  }

  /* Table Custom High-Contrast Styling */
  .product-thumb-container {
    width: 44px;
    height: 44px;
    margin: 0 auto;
    border-radius: 10px;
    overflow: hidden;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;

    &:hover {
      transform: scale(1.08);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
  }
  :global(.dark) & .product-thumb-container {
    background: #1e293b;
    border-color: #334155;
  }

  .product-thumb-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    border-radius: 9px;
  }

  .barcode-tag {
    letter-spacing: 0.5px;
    padding: 3px 8px;
    border-radius: 6px;
  }

  .brand-tag {
    padding: 3px 10px;
    border-radius: 6px;
  }

  .product-name-cell {
    padding: 2px 0;
    max-width: 380px;
  }

  .product-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .product-subtitle {
    font-size: 12px;
    color: var(--el-text-color-secondary, #94a3b8);
    margin-top: 3px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .text-muted {
    color: var(--el-text-color-placeholder, #64748b);
  }

  .mxik-code-tag {
    color: #2563eb;
    background: rgba(59, 130, 246, 0.1);
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 600;
  }
  :global(.dark) & .mxik-code-tag {
    color: #60a5fa;
    background: rgba(59, 130, 246, 0.2);
  }

  .price-cost {
    font-weight: 700;
    color: #d97706;
    font-size: 14px;
    font-family: monospace, ui-monospace;
  }
  :global(.dark) & .price-cost {
    color: #fbbf24;
  }

  .price-sell {
    font-weight: 700;
    color: #059669;
    font-size: 14px;
    font-family: monospace, ui-monospace;
  }
  :global(.dark) & .price-sell {
    color: #34d399;
  }

  .category-badge {
    font-size: 13px;
    color: var(--el-text-color-regular, #475569);
    font-weight: 500;
    display: inline-block;
    max-width: 150px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    vertical-align: middle;
  }
  :global(.dark) & .category-badge {
    color: #cbd5e1;
  }

  .rounded-pill {
    border-radius: 20px;
    padding: 2px 12px;
  }

  /* Classifier Modal Styling */
  .classifier-picker-card {
    padding: 16px 18px;
    background: linear-gradient(
      135deg,
      rgba(59, 130, 246, 0.05) 0%,
      rgba(147, 197, 253, 0.08) 100%
    );
    border: 1px solid rgba(59, 130, 246, 0.25);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.04);
  }

  :global(.dark) & .classifier-picker-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
    border-color: rgba(59, 130, 246, 0.25);
  }

  .classifier-header {
    font-weight: 700;
    font-size: 14px;
    color: var(--el-color-primary, #3b82f6);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
  }

  .custom-search-mode-radios {
    :deep(.el-radio-button__inner) {
      font-weight: 500;
      font-size: 12px;
      padding: 6px 12px;
    }
  }

  /* Custom Formatted Price Inputs */
  .custom-price-input {
    :deep(.el-input__wrapper) {
      border-radius: 8px;
      box-shadow: 0 0 0 1px var(--el-border-color, #475569) inset;
      padding: 0 12px;
      background-color: var(--el-fill-color-blank, #1e293b);
    }
  }

  .cost-input {
    :deep(.el-input__inner) {
      color: #f59e0b !important;
      font-family: monospace, ui-monospace;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }
  }

  .sell-input {
    :deep(.el-input__inner) {
      color: #10b981 !important;
      font-family: monospace, ui-monospace;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }
  }

  .uneditable-stock-box {
    transition: all 0.2s ease;
    user-select: none;
    cursor: not-allowed;
  }

  .stock-summary-calc {
    box-shadow: 0 1px 3px rgba(16, 185, 129, 0.1);
  }

  /* Modern Two-Column Layout for Product Intake Modal */
  .product-dialog-content {
    padding: 2px;
  }

  .product-two-column-grid {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;

    @media (min-width: 992px) {
      flex-direction: row;
      align-items: flex-start;
    }
  }

  .product-panel-left {
    width: 100%;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;

    @media (min-width: 992px) {
      width: 380px;
    }

    @media (min-width: 1200px) {
      width: 440px;
    }
  }

  .product-panel-right {
    flex: 1;
    min-width: 0;
  }

  .intake-card {
    padding: 12px 14px;
    border-radius: 12px;
    border: 1px solid var(--el-border-color-lighter, #e2e8f0);
    background: var(--el-fill-color-blank, #ffffff);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  }

  :global(.dark) & .intake-card {
    background: #1e293b;
    border-color: #334155;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  }

  .intake-search-card {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.04) 0%, rgba(147, 197, 253, 0.08) 100%);
    border-color: rgba(59, 130, 246, 0.25);
  }

  :global(.dark) & .intake-search-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
    border-color: rgba(59, 130, 246, 0.3);
  }

  .warehouse-status-card.existing {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.06) 0%, rgba(52, 211, 153, 0.1) 100%);
    border-color: rgba(16, 185, 129, 0.35);
  }

  :global(.dark) & .warehouse-status-card.existing {
    background: linear-gradient(135deg, rgba(6, 78, 59, 0.25) 0%, rgba(4, 120, 87, 0.15) 100%);
    border-color: rgba(16, 185, 129, 0.4);
  }

  .warehouse-status-card.new-item {
    background: rgba(59, 130, 246, 0.04);
    border-color: rgba(59, 130, 246, 0.2);
  }

  :global(.dark) & .warehouse-status-card.new-item {
    background: rgba(30, 58, 138, 0.2);
    border-color: rgba(59, 130, 246, 0.25);
  }

  .compact-modal-form {
    :deep(.el-form-item) {
      margin-bottom: 10px;
    }
    :deep(.el-form-item__label) {
      font-size: 12px;
      font-weight: 600;
      line-height: 1.25;
      padding-bottom: 3px;
      color: var(--el-text-color-regular, #475569);
    }
    :deep(.el-input__inner),
    :deep(.el-input-number) {
      font-size: 13px;
    }
  }

  .pricing-card-wrapper {
    box-shadow: 0 1px 4px rgba(59, 130, 246, 0.06);
  }
}
</style>

<!-- Teleported Classifier Dropdown Popper Styling (Unscoped for document.body teleports) -->
<style lang="less">
.classifier-select-popper {
  width: var(--el-select-input-width, 100%) !important;
  min-width: 620px !important;
  max-width: 950px !important;
  border-radius: 12px !important;
  box-shadow:
    0 16px 36px -4px rgba(0, 0, 0, 0.16),
    0 4px 12px -2px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid #e2e8f0 !important;
  overflow: hidden !important;
  z-index: 9999 !important;

  .el-select-dropdown__wrap {
    max-height: 420px !important;
  }

  .el-select-dropdown__empty {
    padding: 16px 20px !important;
    white-space: normal !important;
    line-height: 1.5 !important;
  }

  .el-select-dropdown__list {
    padding: 6px 0 !important;
  }

  .el-select-dropdown__item {
    height: auto !important;
    min-height: 68px !important;
    line-height: 1.4 !important;
    padding: 10px 16px !important;
    white-space: normal !important;
    border-bottom: 1px solid #f1f5f9 !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    box-sizing: border-box !important;
    transition: background-color 0.15s ease !important;

    &:last-child {
      border-bottom: none !important;
    }

    &.hover,
    &:hover {
      background-color: #f0f7ff !important;
    }

    &.selected {
      background-color: #e0f2fe !important;
      font-weight: normal !important;
    }
  }

  .classifier-item-card {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
    cursor: pointer;
  }

  .classifier-item-top {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .classifier-brand-tag {
    display: inline-flex;
    align-items: center;
    background: #2563eb;
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
    letter-spacing: 0.3px;
    box-shadow: 0 1px 2px rgba(37, 99, 235, 0.25);
    flex-shrink: 0;
  }

  .classifier-item-title {
    font-size: 13.5px;
    font-weight: 600;
    color: #0f172a;
    line-height: 1.35;
    word-break: break-word;
  }

  .classifier-item-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    font-size: 11.5px;
  }

  .classifier-badge-attr {
    display: inline-flex;
    align-items: center;
    background: rgba(99, 102, 241, 0.08);
    color: #4f46e5;
    border: 1px solid rgba(99, 102, 241, 0.2);
    padding: 2px 8px;
    border-radius: 5px;
    font-weight: 500;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  }

  .classifier-badge-code {
    display: inline-flex;
    align-items: center;
    background: #f8fafc;
    color: #475569;
    border: 1px solid #e2e8f0;
    padding: 2px 8px;
    border-radius: 5px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 11px;
  }

  .classifier-item-group {
    font-size: 11.5px;
    color: #64748b;
    display: flex;
    align-items: center;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

html.dark .classifier-select-popper,
.dark .classifier-select-popper {
  background-color: #1e293b !important;
  border-color: #334155 !important;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6) !important;

  .el-select-dropdown__item {
    border-bottom-color: #334155 !important;

    &.hover,
    &:hover {
      background-color: rgba(59, 130, 246, 0.16) !important;
    }

    &.selected {
      background-color: rgba(59, 130, 246, 0.28) !important;
    }
  }

  .classifier-item-title {
    color: #f8fafc !important;
  }

  .classifier-brand-tag {
    background: #3b82f6 !important;
  }

  .classifier-badge-attr {
    background: rgba(99, 102, 241, 0.2) !important;
    color: #c7d2fe !important;
    border-color: rgba(99, 102, 241, 0.35) !important;
  }

  .classifier-badge-code {
    background: #0f172a !important;
    color: #cbd5e1 !important;
    border-color: #334155 !important;
  }

  .classifier-item-group {
    color: #94a3b8 !important;
  }
}
</style>
