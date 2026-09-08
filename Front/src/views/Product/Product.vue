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
            width="160"
            align="center"
          >
            <template #default="scope">
              <span v-if="scope?.row">
                <ElTag
                  :type="
                    (scope.row.quantityInStock || 0) > 10
                      ? 'success'
                      : (scope.row.quantityInStock || 0) > 0
                        ? 'warning'
                        : 'danger'
                  "
                  effect="dark"
                  class="font-bold rounded-pill"
                >
                  {{ formatMoney(scope.row.quantityInStock) }} {{ scope.row.unit || 'dona' }}
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
            width="160"
            align="center"
          >
            <template #default="scope">
              <span v-if="scope?.row">
                <ElTag
                  v-if="scope.row.expiration_date"
                  type="info"
                  effect="plain"
                  class="font-mono text-12px inline-flex items-center gap-4px"
                >
                  <Icon icon="ep:calendar" class="text-12px text-gray-500" />
                  <span>{{ scope.row.expiration_date }}</span>
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
      <div v-if="dialogType === 'add'" class="classifier-picker-card mb-20px">
        <div
          class="classifier-header flex items-center justify-between flex-wrap gap-2 pb-10px mb-12px border-b border-blue-200/50 dark:border-blue-800/50"
        >
          <div class="flex items-center gap-8px">
            <div
              class="w-26px h-26px rounded-lg bg-blue-500 text-white flex items-center justify-center shadow-sm"
            >
              <Icon icon="ep:search" style="font-size: 14px" />
            </div>
            <div>
              <span class="font-bold text-sm text-gray-900 dark:text-gray-100">
                1. Klassifikatordan Tanlash va Shtrix-Kodni Skanerlash
              </span>
              <span class="text-xs text-gray-400 ml-6px font-normal hidden sm:inline">
                (Formani bir zumda avtomatik to'ldirish)
              </span>
            </div>
          </div>
          <div
            class="flex items-center gap-6px px-2.5 py-1 rounded-full bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300 text-xs font-semibold"
          >
            <span class="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <Icon
              :icon="classifierSearchMode === 'extended' ? 'ep:lightning' : 'ep:search'"
              :class="classifierSearchMode === 'extended' ? 'text-amber-500' : 'text-blue-500'"
              style="font-size: 13px"
            />
            <span>{{
              classifierSearchMode === 'extended'
                ? 'Tasnif Soliq (440,000+ tovarlar)'
                : 'Oddiy qidiruv'
            }}</span>
          </div>
        </div>

        <div class="flex gap-10px mb-12px">
          <ElInput
            ref="barcodeInputRef"
            v-model="barcodeSearch"
            placeholder="Shtrix-kodni skanerlang yoki qo'lda kiriting (masalan: 4780022620153)..."
            clearable
            size="default"
            style="flex: 1"
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
                class="!px-16px font-semibold"
                @click="handleBarcodeScan"
              >
                <Icon icon="ep:aim" class="mr-4px" /> Kodni Izlash
              </ElButton>
            </template>
          </ElInput>
        </div>

        <div class="mb-10px flex items-center justify-between flex-wrap gap-2">
          <ElRadioGroup
            v-model="classifierSearchMode"
            size="small"
            class="custom-search-mode-radios"
            @change="onClassifierSearchModeChange"
          >
            <ElRadioButton label="extended">
              <Icon icon="ep:lightning" class="mr-4px text-amber-500" /> Matn bo'yicha
              kengaytirilgan qidiruv
            </ElRadioButton>
            <ElRadioButton label="simple">
              <Icon icon="ep:search" class="mr-4px" /> Matn bo'yicha qidirish
            </ElRadioButton>
          </ElRadioGroup>
          <span class="text-xs text-gray-500 italic">
            {{
              classifierSearchMode === 'extended'
                ? "Barcha tovarlar, brendlar va atributlar bo'yicha to'liq matnli qidiruv"
                : 'Faqat lokal bazadan oddiy qidiruv'
            }}
          </span>
        </div>

        <div>
          <ElSelect
            v-model="selectedClassifierId"
            filterable
            remote
            reserve-keyword
            clearable
            popper-class="classifier-select-popper"
            size="large"
            :placeholder="
              classifierSearchMode === 'extended'
                ? 'Tovar nomi yoki brendini yozing (masalan: Pepsi 1.5, Coca Cola, Shaffof, Dinay, ruchka...)'
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
                    <Icon icon="ep:reading" class="mr-3px" />Shtrix: {{ item.shtrix_code }}
                  </span>
                  <span v-if="item.mxik_code" class="classifier-badge-code">
                    <Icon icon="ep:document" class="mr-3px" />MXIK: {{ item.mxik_code }}
                  </span>
                </div>
                <div v-if="item.group_name" class="classifier-item-group">
                  <span>{{ item.group_name }}</span>
                </div>
              </div>
            </ElOption>
            <template #empty>
              <div class="p-16px text-center text-gray-400 text-xs">
                <Icon icon="ep:info-filled" class="mr-4px text-blue-400 align-middle" />
                <span v-if="classifierLoading">Qidirilmoqda...</span>
                <span v-else
                  >Tovar nomi yoki brendini qidirish uchun kamida 2 ta harf yozing (masalan: Pepsi,
                  Cola, Dinay)</span
                >
              </div>
            </template>
          </ElSelect>
        </div>
      </div>

      <!-- Existing Product Detection Alert Banner -->
      <transition name="el-zoom-in-top">
        <div
          v-if="dialogType === 'add' && existingProduct"
          class="existing-product-card mb-20px p-16px rounded-12px bg-amber-500/10 dark:bg-amber-500/15 border-2 border-amber-500/40 shadow-md"
        >
          <div
            class="flex items-center justify-between flex-wrap gap-2 mb-12px pb-8px border-b border-amber-500/20"
          >
            <div class="flex items-center gap-8px text-amber-500 font-bold text-base">
              <Icon icon="ep:warning-filled" class="text-20px animate-bounce" />
              <span>Omborda Mavjud Mahsulot Topildi!</span>
            </div>
            <ElTag type="warning" effect="dark" size="default" class="font-bold">
              <Icon icon="ep:box" class="mr-4px inline" />
              Bazada Mavjud
            </ElTag>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-10px mb-12px text-xs">
            <div
              class="stat-pill bg-white dark:bg-gray-800 p-10px rounded-8px border border-amber-300 dark:border-amber-800 shadow-sm"
            >
              <span class="text-gray-500 dark:text-gray-400 block mb-3px"
                >Hozirgi Ombor Qoldig'i:</span
              >
              <span class="font-mono font-bold text-base text-emerald-600 dark:text-emerald-400">
                {{ formatMoney(existingProduct.quantityInStock) }}
                {{ existingProduct.unit || 'dona' }}
              </span>
            </div>
            <div
              class="stat-pill bg-white dark:bg-gray-800 p-10px rounded-8px border border-amber-300 dark:border-amber-800 shadow-sm"
            >
              <span class="text-gray-500 dark:text-gray-400 block mb-3px">Eski Tannarxi:</span>
              <span class="font-mono font-bold text-base text-amber-600 dark:text-amber-400">
                ${{ formatMoney(existingProduct.cost) }}
              </span>
            </div>
            <div
              class="stat-pill bg-white dark:bg-gray-800 p-10px rounded-8px border border-amber-300 dark:border-amber-800 shadow-sm"
            >
              <span class="text-gray-500 dark:text-gray-400 block mb-3px">Eski Sotish Narxi:</span>
              <span class="font-mono font-bold text-base text-blue-600 dark:text-blue-400">
                ${{ formatMoney(existingProduct.price) }}
              </span>
            </div>
            <div
              class="stat-pill bg-white dark:bg-gray-800 p-10px rounded-8px border border-amber-300 dark:border-amber-800 shadow-sm"
            >
              <span class="text-gray-500 dark:text-gray-400 block mb-3px">Kategoriyasi:</span>
              <span class="font-semibold text-sm text-gray-800 dark:text-gray-200 truncate block">
                {{ existingProduct.category || 'Boshqalar' }}
              </span>
            </div>
          </div>

          <div
            class="stock-calc-banner p-10px rounded-8px bg-amber-500/20 dark:bg-amber-950/50 border border-amber-500/30 flex items-center justify-between flex-wrap gap-2 text-xs"
          >
            <div class="flex items-center gap-6px text-amber-900 dark:text-amber-200">
              <Icon icon="ep:info-filled" class="text-14px" />
              <span>Yangi kirim sonini kiriting. U avtomatik tarzda eski qoldiqqa qo'shiladi:</span>
            </div>
            <div
              class="font-mono font-bold text-sm text-emerald-600 dark:text-emerald-400 bg-white/80 dark:bg-black/40 px-10px py-4px rounded-6px border border-emerald-500/30"
            >
              Eski ({{ formatMoney(existingProduct.quantityInStock) }}) + Yangi ({{
                formatMoney(form.quantityInStock || 0)
              }}) = Jami
              {{
                formatMoney(
                  (existingProduct.quantityInStock || 0) + (Number(form.quantityInStock) || 0)
                )
              }}
              {{ form.unit || 'dona' }}
            </div>
          </div>
        </div>
      </transition>

      <ElForm ref="formRef" :model="form" :rules="rules" label-width="140px" class="modal-form">
        <ElRow :gutter="16">
          <ElCol :span="12">
            <ElFormItem label="Shtrix-Kodi" prop="shtrix_code">
              <ElInput
                v-model="form.shtrix_code"
                placeholder="Faqat raqamlar: 4780014680073"
                @input="(val: string) => (form.shtrix_code = val.replace(/\D/g, ''))"
                @blur="onShtrixCodeBlur"
              />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="Brend Nomi" prop="brand_name">
              <ElInput v-model="form.brand_name" placeholder="Masalan: PEPSI, Shaffof" />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElFormItem :label="t('erp.productName')" prop="productName">
          <ElInput v-model="form.productName" placeholder="Masalan: Pepsi 1.5L PET" />
        </ElFormItem>

        <ElRow :gutter="16">
          <ElCol :span="12">
            <ElFormItem label="Atribut / Olcham" prop="attribute_name">
              <ElInput v-model="form.attribute_name" placeholder="Masalan: PET idish 1,5 l." />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem :label="t('erp.mxikCode')" prop="mxik_code">
              <ElInput v-model="form.mxik_code" placeholder="Masalan: 02201001001001002" />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElRow :gutter="16">
          <ElCol :span="12">
            <ElFormItem label="SKU Raqami" prop="SKU">
              <ElInput v-model="form.SKU" placeholder="Masalan: SKU-4780014680073" />
            </ElFormItem>
          </ElCol>
          <ElCol :span="12">
            <ElFormItem label="O'lchov Birligi" prop="unit">
              <ElInput v-model="form.unit" placeholder="dona, kg, litr..." />
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElRow :gutter="16">
          <ElCol :span="8">
            <ElFormItem
              :label="
                dialogType === 'add' && existingProduct ? 'Yangi Kirim Soni' : 'Ombordagi Soni'
              "
              prop="quantityInStock"
            >
              <ElInputNumber
                v-model="form.quantityInStock"
                :min="1"
                :step="1"
                style="width: 100%"
              />
              <div
                v-if="dialogType === 'add' && existingProduct"
                class="text-11px text-emerald-500 font-mono mt-4px font-bold"
              >
                +{{ form.quantityInStock || 0 }} qo'shiladi -> Jami:
                {{ (existingProduct.quantityInStock || 0) + (Number(form.quantityInStock) || 0) }}
                dona
              </div>
            </ElFormItem>
          </ElCol>
          <ElCol :span="8">
            <ElFormItem :label="t('erp.costPriceDollar')" prop="cost">
              <ElInput
                v-model="displayCost"
                placeholder="0"
                class="custom-price-input cost-input"
              />
              <div
                v-if="dialogType === 'add' && existingProduct"
                class="text-10px text-gray-400 mt-2px"
              >
                Eski tannarx: ${{ formatMoney(existingProduct.cost) }}
              </div>
            </ElFormItem>
          </ElCol>
          <ElCol :span="8">
            <ElFormItem :label="t('erp.sellingPriceDollar')" prop="price">
              <ElInput
                v-model="displayPrice"
                placeholder="0"
                class="custom-price-input sell-input"
              />
              <div
                v-if="dialogType === 'add' && existingProduct"
                class="text-10px text-gray-400 mt-2px"
              >
                Eski sotuv: ${{ formatMoney(existingProduct.price) }}
              </div>
            </ElFormItem>
          </ElCol>
        </ElRow>

        <ElFormItem :label="t('erp.category')" prop="category">
          <ElSelect
            v-model="form.category"
            :placeholder="t('erp.kategoriyaniTanlang')"
            style="width: 100%"
          >
            <ElOption :label="t('erp.drinksAndWater')" value="Ichimliklar va suvlar" />
            <ElOption :label="t('erp.dairyProducts')" value="Sut va sut mahsulotlari" />
            <ElOption :label="t('erp.saltAndSpices')" value="Tuz va ziravorlar" />
            <ElOption :label="t('erp.plasticsAndDishes')" value="Plastmassa va idishlar" />
            <ElOption :label="t('erp.foodProducts')" value="Oziq-ovqat mahsulotlari" />
            <ElOption :label="t('erp.otherCategory')" value="Boshqalar" />
          </ElSelect>
        </ElFormItem>

        <ElFormItem label="Mahsulot Rasmi" prop="image_url">
          <div class="flex items-center gap-16px w-full">
            <div
              v-if="form.image_url"
              class="relative w-80px h-80px rounded-8px overflow-hidden border border-gray-700 group flex-shrink-0"
            >
              <img :src="form.image_url" class="w-full h-full object-cover" />
              <div
                class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity cursor-pointer"
                @click="form.image_url = ''"
              >
                <Icon icon="ep:delete" class="text-white text-18px" />
              </div>
            </div>
            <ElUpload
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              accept="image/*"
              @change="handleImageChange"
            >
              <ElButton type="primary" plain class="upload-img-btn">
                <Icon icon="ep:picture" class="mr-6px" />
                {{ form.image_url ? "Rasmni o'zgartirish" : 'Rasm yuklash' }}
              </ElButton>
            </ElUpload>
            <span class="text-12px text-gray-400">PNG, JPG, WEBP fayllari (maks 5MB)</span>
          </div>
        </ElFormItem>

        <ElFormItem :label="t('erp.izoh')" prop="remark">
          <ElInput
            v-model="form.remark"
            type="textarea"
            :rows="2"
            placeholder="Mahsulot haqida qo'shimcha izoh..."
          />
        </ElFormItem>
      </ElForm>

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
  remark: ''
})

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
  if (form.cost === undefined || form.cost === null || form.cost <= 0) {
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
  cost: [{ required: true, validator: validateCost, trigger: ['blur', 'change'] }],
  price: [{ required: true, validator: validatePrice, trigger: ['blur', 'change'] }]
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
  classifierId?: number
}): Promise<ProductType | null> => {
  const barcode = (criteria.barcode || '').trim()
  const sku = (criteria.sku || '').trim()
  const name = (criteria.name || '').trim()
  const classifierId = criteria.classifierId

  if (!barcode && !sku && !name && !classifierId) {
    return null
  }

  // 1. Fast check in current loaded tableData
  let found: ProductType | undefined = tableData.value.find((p) => {
    if (barcode && p.shtrix_code && p.shtrix_code === barcode) return true
    if (sku && p.SKU && p.SKU.toLowerCase() === sku.toLowerCase()) return true
    if (classifierId && p.classifier_id && p.classifier_id === classifierId) return true
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

  return null
}

const onShtrixCodeBlur = async () => {
  if (dialogType.value === 'add' && form.shtrix_code && form.shtrix_code.length >= 4) {
    await checkAndApplyExistingProduct({ barcode: form.shtrix_code })
  }
}

const applyClassifierToForm = async (item: any) => {
  if (!item) return
  form.classifier_id = item.id
  form.productName = item.mxik_name || ''
  form.brand_name = item.brand_name || ''
  form.mxik_code = item.mxik_code || ''
  form.shtrix_code = item.shtrix_code || ''
  form.attribute_name = item.attribute_name || ''
  form.unit = item.unit || 'dona'
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

  // Check if this product already exists in warehouse:
  const existing = await checkAndApplyExistingProduct({
    barcode: item.shtrix_code,
    sku: form.SKU,
    name: item.mxik_name,
    classifierId: item.id
  })

  if (!existing) {
    existingProduct.value = null
    ElMessage.success(`Klassifikator ma'lumotlari yuklandi: ${item.brand_name || item.mxik_name}`)
  }
}

const handleClassifierSelect = (val: number | string) => {
  const found = classifierOptions.value.find(
    (c) => c.id === val || c.mxik_code === val || c.shtrix_code === val
  )
  if (found) {
    applyClassifierToForm(found)
  }
}

const handleBarcodeScan = async () => {
  const code = barcodeSearch.value.replace(/\D/g, '')
  if (!code) {
    ElMessage.warning('Iltimos, shtrix-kodni faqat raqamlarda kiriting')
    return
  }
  barcodeLoading.value = true
  try {
    // 1. First check if barcode already exists in warehouse!
    const existing = await checkAndApplyExistingProduct({ barcode: code })
    if (existing) {
      barcodeSearch.value = ''
      nextTick(() => {
        barcodeInputRef.value?.focus?.()
      })
      return
    }

    // 2. If not in warehouse, search Tasnif classifier
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
  existingProduct.value = null
  form.id = ''
  form.productName = ''
  form.SKU = ''
  form.category = 'Ichimliklar va suvlar'
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
  form.expiration_date = ''
  form.remark = ''
  form.packagings = []
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
}
</style>

<!-- Teleported Classifier Dropdown Popper Styling (Unscoped for document.body teleports) -->
<style lang="less">
.classifier-select-popper {
  max-width: 820px !important;
  border-radius: 12px !important;
  box-shadow:
    0 16px 36px -4px rgba(0, 0, 0, 0.16),
    0 4px 12px -2px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid #e2e8f0 !important;
  overflow: hidden !important;

  .el-select-dropdown__wrap {
    max-height: 420px !important;
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
