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
                  class="font-mono text-12px"
                >
                  📅 {{ scope.row.expiration_date }}
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
        <div class="classifier-header">
          <Icon icon="ep:search" class="mr-6px" />
          <span>1. Klassifikatordan Tanlash va Shtrix-Kodni Skanerlash</span>
        </div>

        <div class="flex gap-12px mb-12px">
          <ElInput
            ref="barcodeInputRef"
            v-model="barcodeSearch"
            placeholder="Shtrix-kod skanerlang (faqat raqamlar)..."
            clearable
            style="flex: 1"
            @input="(val: string) => (barcodeSearch = val.replace(/\D/g, ''))"
            @keyup.enter="handleBarcodeScan"
          >
            <template #append>
              <ElButton type="primary" @click="handleBarcodeScan">
                <Icon icon="ep:aim" class="mr-4px" /> Kodni Izlash
              </ElButton>
            </template>
          </ElInput>
        </div>

        <div>
          <ElSelect
            v-model="selectedClassifierId"
            filterable
            remote
            reserve-keyword
            placeholder="411,000+ Klassifikator bazasidan izlang (masalan: Pepsi 1.5, Shaffof)..."
            :remote-method="remoteSearchClassifier"
            :loading="classifierLoading"
            style="width: 100%"
            @change="handleClassifierSelect"
          >
            <ElOption
              v-for="item in classifierOptions"
              :key="item.id"
              :label="`${item.brand_name ? '[' + item.brand_name + '] ' : ''}${item.mxik_name} ${item.attribute_name ? '(' + item.attribute_name + ')' : ''} [${item.shtrix_code || item.mxik_code}]`"
              :value="item.id"
            />
          </ElSelect>
        </div>
      </div>

      <ElForm ref="formRef" :model="form" :rules="rules" label-width="140px" class="modal-form">
        <ElRow :gutter="16">
          <ElCol :span="12">
            <ElFormItem label="Shtrix-Kodi" prop="shtrix_code">
              <ElInput
                v-model="form.shtrix_code"
                placeholder="Faqat raqamlar: 4780014680073"
                @input="(val: string) => (form.shtrix_code = val.replace(/\D/g, ''))"
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
            <ElFormItem label="Ombordagi Soni" prop="quantityInStock">
              <ElInputNumber
                v-model="form.quantityInStock"
                :min="0"
                :step="1"
                style="width: 100%"
              />
            </ElFormItem>
          </ElCol>
          <ElCol :span="8">
            <ElFormItem :label="t('erp.costPriceDollar')" prop="cost">
              <ElInput
                v-model="displayCost"
                placeholder="0"
                class="custom-price-input cost-input"
              />
            </ElFormItem>
          </ElCol>
          <ElCol :span="8">
            <ElFormItem :label="t('erp.sellingPriceDollar')" prop="price">
              <ElInput
                v-model="displayPrice"
                placeholder="0"
                class="custom-price-input sell-input"
              />
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
            <Icon icon="ep:box" /> 📦 Qadoqlash va Paket Turlari (Ko'p Birlikda Sotuv Narxlari):
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
const classifierLoading = ref(false)
const classifierOptions = ref<any[]>([])
const selectedClassifierId = ref<number | string | undefined>(undefined)

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

const handleExportExcel = () => {
  if (tableData.value.length === 0) {
    ElMessage.warning('Eksport qilish uchun mahsulotlar mavjud emas')
    return
  }
  exportToExcel(
    'Ombor_Mahsulotlari',
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
    tableData.value
  )
  ElMessage.success('Mahsulotlar ro‘yxati Excel fayliga yuklab olindi!')
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

const remoteSearchClassifier = (query: string) => {
  if (!query || query.trim().length < 2) {
    classifierOptions.value = []
    return
  }
  const cleanQ = query.trim()
  if (classifierCacheMap.has(cleanQ)) {
    classifierOptions.value = classifierCacheMap.get(cleanQ) || []
    return
  }

  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)

  searchDebounceTimer = setTimeout(async () => {
    classifierLoading.value = true
    try {
      const res = await searchClassifierApi({ search: cleanQ, page: 1, page_size: 20 })
      if (res && res.data) {
        const list = Array.isArray(res.data) ? res.data : (res.data as any).list || []
        classifierOptions.value = list
        classifierCacheMap.set(cleanQ, list)
      }
    } catch (err) {
      console.error(err)
    } finally {
      classifierLoading.value = false
    }
  }, 120)
}

const applyClassifierToForm = (item: any) => {
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

  ElMessage.success(`Klassifikator ma'lumotlari yuklandi: ${item.brand_name || item.mxik_name}`)
}

const handleClassifierSelect = (val: number) => {
  const found = classifierOptions.value.find((c) => c.id === val)
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
  try {
    const res = await getClassifierByBarcodeApi(code)
    if (res && res.data) {
      applyClassifierToForm(res.data)
      barcodeSearch.value = ''
      nextTick(() => {
        barcodeInputRef.value?.focus?.()
      })
    } else {
      ElMessage.warning("Ushbu shtrix-kod bo'yicha klassifikator topilmadi")
      barcodeSearch.value = ''
      nextTick(() => {
        barcodeInputRef.value?.focus?.()
      })
    }
  } catch (err) {
    ElMessage.error("Shtrix-kod bo'yicha qidirishda xatolik")
  }
}

const resetForm = () => {
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
        const res: any = await saveProductApi(form)

        if (res && res.is_existing) {
          ElNotification({
            title: 'Omborda mavjud mahsulot!',
            message: `"${res.product_name || form.productName}" mahsuloti omborda mavjud bo'lgani uchun uning soniga +${res.added_qty || form.quantityInStock} dona qo'shildi. Jami ombordagi soni: ${formatMoney(res.total_stock)} dona!`,
            type: 'warning',
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
    padding: 14px 16px;
    background: rgba(59, 130, 246, 0.06);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 8px;
  }

  .classifier-header {
    font-weight: 700;
    font-size: 14px;
    color: var(--el-color-primary, #3b82f6);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
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
