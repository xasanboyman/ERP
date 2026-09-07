<script setup lang="tsx">
import { reactive, ref, unref } from 'vue'
import { getRoleListApi, saveRoleApi, deleteRoleApi } from '@/api/role'
import { useTable } from '@/hooks/web/useTable'
import { useI18n } from '@/hooks/web/useI18n'
import { Table, TableColumn } from '@/components/Table'
import { ElTag, ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@/components/Search'
import { FormSchema } from '@/components/Form'
import { ContentWrap } from '@/components/ContentWrap'
import Write from './components/Write.vue'
import Detail from './components/Detail.vue'
import { ResizeDialog } from '@/components/Dialog'
import { BaseButton } from '@/components/Button'
import { Icon } from '@/components/Icon'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const dialogInitWidth = Math.min(window.innerWidth * 0.95, 1600)
const dialogInitHeight = Math.min(window.innerHeight * 0.92, 950)

const { t } = useI18n()

const searchParams = ref<{ roleName?: string; status?: number | string }>({})

const { tableRegister, tableState, tableMethods } = useTable({
  fetchDataApi: async () => {
    const res = await getRoleListApi()
    let list = res?.data?.list || (Array.isArray(res?.data) ? res.data : [])
    if (searchParams.value) {
      if (searchParams.value.roleName) {
        const kw = searchParams.value.roleName.toLowerCase().trim()
        list = list.filter((r: any) => (r.roleName || '').toLowerCase().includes(kw))
      }
      if (searchParams.value.status !== undefined && searchParams.value.status !== '') {
        list = list.filter((r: any) => Number(r.status) === Number(searchParams.value.status))
      }
    }
    return {
      list: list,
      total: list.length
    }
  }
})

const { dataList, loading, total } = tableState
const { getList } = tableMethods

useRealtimeSync('role', () => {
  getList()
})

const tableColumns = reactive<TableColumn[]>([
  {
    field: 'index',
    label: t('userDemo.index'),
    type: 'index'
  },
  {
    field: 'roleName',
    label: 'Rol Nomi'
  },
  {
    field: 'status',
    label: 'Holati',
    slots: {
      default: (data: any) => {
        return (
          <>
            <ElTag type={data.row.status === 0 ? 'danger' : 'success'}>
              {data.row.status === 1 ? 'Faol' : "O'chirilgan"}
            </ElTag>
          </>
        )
      }
    }
  },
  {
    field: 'createTime',
    label: t('tableDemo.displayTime')
  },
  {
    field: 'remark',
    label: 'Izoh'
  },
  {
    field: 'action',
    label: t('userDemo.action'),
    minWidth: 200,
    width: 200,
    slots: {
      default: (data: any) => {
        const row = data.row
        return (
          <div class="flex items-center gap-6px flex-nowrap whitespace-nowrap">
            <BaseButton type="primary" size="small" onClick={() => action(row, 'edit')}>
              {t('exampleDemo.edit')}
            </BaseButton>
            <BaseButton type="success" size="small" onClick={() => action(row, 'detail')}>
              {t('exampleDemo.detail')}
            </BaseButton>
            {row.roleName !== 'Super Administrator' && row.id !== '1' ? (
              <BaseButton type="danger" size="small" onClick={() => deleteRow(row)}>
                {t('exampleDemo.del')}
              </BaseButton>
            ) : null}
          </div>
        )
      }
    }
  }
])

const searchSchema = reactive<FormSchema[]>([
  {
    field: 'roleName',
    label: 'Rol Nomi',
    component: 'Input',
    componentProps: {
      placeholder: 'Rol nomi bo‘yicha qidirish...'
    }
  },
  {
    field: 'status',
    label: 'Holati',
    component: 'Select',
    componentProps: {
      placeholder: 'Barchasi',
      options: [
        { label: 'Barchasi', value: '' },
        { label: 'Faol', value: 1 },
        { label: "O'chirilgan", value: 0 }
      ]
    }
  }
])

const setSearchParams = (data: any) => {
  searchParams.value = data || {}
  getList()
}

const dialogVisible = ref(false)
const dialogTitle = ref('')

const currentRow = ref()
const actionType = ref('')

const writeRef = ref<ComponentRef<typeof Write>>()

const saveLoading = ref(false)

const action = (row: any, type: string) => {
  dialogTitle.value = type === 'edit' ? 'Rolni Tahrirlash va Ruxsatlar Studio' : "Rol Ma'lumotlari"
  actionType.value = type
  currentRow.value = row
  dialogVisible.value = true
}

const AddAction = () => {
  dialogTitle.value = 'Yangi Rol Yaratish va Ruxsatlar Studio'
  currentRow.value = undefined
  dialogVisible.value = true
  actionType.value = ''
}

const save = async () => {
  const write = unref(writeRef)
  const formData = await write?.submit()
  if (formData) {
    saveLoading.value = true
    try {
      const payload = {
        id: currentRow.value?.id || '',
        roleName: formData.roleName,
        status: formData.status,
        remark: formData.remark,
        permissions: formData.permissions || [],
        menu: formData.menu || []
      }
      const res = await saveRoleApi(payload)
      if (res && res.code === 0) {
        ElMessage.success('Rol muvaffaqiyatli saqlandi')
        dialogVisible.value = false
        getList()
      }
    } catch (e: any) {
      ElMessage.error(e.message || 'Saqlashda xatolik yuz berdi')
    } finally {
      saveLoading.value = false
    }
  }
}

const deleteRow = async (row: any) => {
  if (row.roleName === 'Super Administrator' || row.id === '1') {
    ElMessage.warning("Super Administrator tizimning asosiy roli bo'lib, uni o'chirib bo'lmaydi!")
    return
  }
  try {
    await ElMessageBox.confirm(
      `Haqiqatan ham "${row.roleName}" rolini o'chirmoqchimisiz? Ushbu rolga biriktirilgan xodimlar huquqlari o'zgarishi mumkin.`,
      "Rolni o'chirishni tasdiqlang",
      {
        confirmButtonText: "Ha, o'chirish",
        cancelButtonText: 'Bekor qilish',
        type: 'warning'
      }
    )
    const res = await deleteRoleApi({ id: row.id })
    if (res && res.code === 0) {
      ElMessage.success("Rol muvaffaqiyatli o'chirildi")
      getList()
    } else {
      ElMessage.error(res?.message || "O'chirishda xatolik yuz berdi")
    }
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || "O'chirishda xatolik yuz berdi")
    }
  }
}
</script>

<template>
  <ContentWrap>
    <Search :schema="searchSchema" @reset="setSearchParams" @search="setSearchParams" />
    <div class="mb-14px flex items-center justify-between">
      <div class="flex items-center gap-10px">
        <BaseButton type="primary" @click="AddAction">
          <Icon icon="vi-ep:plus" class="mr-4px" />
          {{ t('exampleDemo.add') }}
        </BaseButton>
        <BaseButton type="default" @click="getList">
          <Icon icon="vi-ep:refresh" class="mr-4px" />
          Yangilash
        </BaseButton>
      </div>
      <div class="text-13px text-slate-500 font-medium">
        Jami: <span class="font-bold text-blue-600 dark:text-blue-400">{{ total }}</span> ta rol
      </div>
    </div>
    <Table
      :columns="tableColumns"
      default-expand-all
      node-key="id"
      :data="dataList"
      :loading="loading"
      :pagination="{
        total
      }"
      @register="tableRegister"
    />
  </ContentWrap>

  <ResizeDialog
    v-model="dialogVisible"
    :title="dialogTitle"
    :init-width="dialogInitWidth"
    :init-height="dialogInitHeight"
    :min-resize-width="750"
    :min-resize-height="500"
    class="role-custom-dialog"
  >
    <div class="p-2px h-full flex flex-col flex-1 min-h-0">
      <Write v-if="actionType !== 'detail'" ref="writeRef" :current-row="currentRow" />
      <Detail v-else :current-row="currentRow" />
    </div>

    <template #footer>
      <div class="flex justify-end items-center gap-14px px-8px py-6px">
        <BaseButton
          v-if="actionType === 'detail'"
          type="primary"
          :style="{
            paddingLeft: 'var(--app-button-px, 24px)',
            paddingRight: 'var(--app-button-px, 24px)',
            paddingTop: 'var(--app-button-py, 11px)',
            paddingBottom: 'var(--app-button-py, 11px)',
            fontSize: 'var(--app-font-size, 14px)'
          }"
          class="font-bold rounded-xl shadow-lg shadow-indigo-500/20 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 border-none transition-all"
          @click="action(currentRow, 'edit')"
        >
          {t('exampleDemo.edit')}
        </BaseButton>
        <BaseButton
          v-if="actionType !== 'detail'"
          type="primary"
          :style="{
            paddingLeft: 'var(--app-button-px, 28px)',
            paddingRight: 'var(--app-button-px, 28px)',
            paddingTop: 'var(--app-button-py, 11px)',
            paddingBottom: 'var(--app-button-py, 11px)',
            fontSize: 'var(--app-font-size, 14px)'
          }"
          class="font-bold rounded-xl shadow-lg shadow-indigo-500/20 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 border-none transition-all"
          :loading="saveLoading"
          @click="save"
          >{{ t('common.save') }}</BaseButton
        >
        <BaseButton
          :style="{
            paddingLeft: 'var(--app-button-px, 22px)',
            paddingRight: 'var(--app-button-px, 22px)',
            paddingTop: 'var(--app-button-py, 11px)',
            paddingBottom: 'var(--app-button-py, 11px)',
            fontSize: 'var(--app-font-size, 14px)'
          }"
          class="font-medium rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-800 text-slate-200 transition-all"
          @click="dialogVisible = false"
          >{{ t('common.close') }}</BaseButton
        >
      </div>
    </template>
  </ResizeDialog>
</template>

<style lang="less">
.role-custom-dialog {
  &.el-dialog {
    background: var(--el-bg-color-overlay, #ffffff) !important;
    border: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
    border-radius: 20px !important;
    box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.12) !important;
    display: flex !important;
    flex-direction: column !important;

    .el-dialog__header {
      padding: 16px 24px !important;
      border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
      background: var(--el-fill-color-light, #f8fafc) !important;
      border-top-left-radius: 20px;
      border-top-right-radius: 20px;
      flex-shrink: 0 !important;

      .el-dialog__title {
        font-weight: 700 !important;
        font-size: var(--app-title-size, 17px) !important;
        color: var(--el-text-color-primary, #0f172a) !important;
      }
    }

    .el-dialog__body {
      padding: 20px 24px !important;
      background: var(--el-bg-color-overlay, #ffffff) !important;
      flex: 1 !important;
      min-height: 0 !important;
      display: flex !important;
      flex-direction: column !important;
      overflow: hidden !important;

      .el-form-item {
        margin-bottom: 10px !important;
      }

      .el-form-item__label {
        font-weight: 600 !important;
        font-size: 13px !important;
        color: var(--el-text-color-primary, #0f172a) !important;
        padding-bottom: 3px !important;
        line-height: 1.2 !important;
      }
    }

    .el-dialog__footer {
      padding: 14px 24px !important;
      border-top: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
      background: var(--el-fill-color-light, #f8fafc) !important;
      border-bottom-left-radius: 20px;
      border-bottom-right-radius: 20px;
      flex-shrink: 0 !important;
    }
  }
}

:global(.dark) {
  .role-custom-dialog {
    &.el-dialog {
      background: #0b0f19 !important;
      border-color: #1e293b !important;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9) !important;

      .el-dialog__header {
        border-bottom-color: #1e293b !important;
        background: #0f172a !important;
        .el-dialog__title {
          color: #f1f5f9 !important;
        }
      }

      .el-dialog__body {
        background: #080c14 !important;
        .el-form-item__label {
          color: #94a3b8 !important;
        }
        .el-input__wrapper,
        .el-textarea__inner,
        .el-select__wrapper {
          background: #0f172a !important;
          border: 1px solid #1e293b !important;
          box-shadow: none !important;
          color: #f8fafc !important;
        }
      }

      .el-dialog__footer {
        border-top-color: #1e293b !important;
        background: #0f172a !important;
      }
    }
  }
}
</style>
