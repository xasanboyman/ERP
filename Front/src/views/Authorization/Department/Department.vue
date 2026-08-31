<script setup lang="tsx">
import { ContentWrap } from '@/components/ContentWrap'
import { Search } from '@/components/Search'
import { ResizeDialog } from '@/components/Dialog'
import { useI18n } from '@/hooks/web/useI18n'
import { ElTag } from 'element-plus'
import { Table } from '@/components/Table'
import {
  getDepartmentApi,
  getDepartmentTableApi,
  saveDepartmentApi,
  deleteDepartmentApi
} from '@/api/department'
import type { DepartmentItem } from '@/api/department/types'
import { useTable } from '@/hooks/web/useTable'
import { ref, unref, reactive } from 'vue'
import Write from './components/Write.vue'
import Detail from './components/Detail.vue'
import { CrudSchema, useCrudSchemas } from '@/hooks/web/useCrudSchemas'
import { BaseButton } from '@/components/Button'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const dialogInitWidth = Math.min(window.innerWidth * 0.92, 1400)
const dialogInitHeight = Math.min(window.innerHeight * 0.88, 800)

const ids = ref<string[]>([])

const { tableRegister, tableState, tableMethods } = useTable({
  fetchDataApi: async () => {
    const { currentPage, pageSize } = tableState
    const res = await getDepartmentTableApi({
      pageIndex: unref(currentPage),
      pageSize: unref(pageSize),
      ...unref(searchParams)
    })
    return {
      list: res.data.list,
      total: res.data.total
    }
  },
  fetchDelApi: async () => {
    const res = await deleteDepartmentApi(unref(ids))
    return !!res
  }
})
const { loading, dataList, total, currentPage, pageSize } = tableState
const { getList, getElTableExpose, delList } = tableMethods

useRealtimeSync('department', () => {
  getList()
})

const searchParams = ref({})
const setSearchParams = (params: any) => {
  searchParams.value = params
  getList()
}

const { t } = useI18n()

const crudSchemas = reactive<CrudSchema[]>([
  {
    field: 'selection',
    search: {
      hidden: true
    },
    form: {
      hidden: true
    },
    detail: {
      hidden: true
    },
    table: {
      type: 'selection'
    }
  },
  {
    field: 'index',
    label: t('tableDemo.index'),
    type: 'index',
    search: {
      hidden: true
    },
    form: {
      hidden: true
    },
    detail: {
      hidden: true
    }
  },
  {
    field: 'departmentName',
    label: "Bo'lim / Filial Nomi",
    table: {
      slots: {
        default: (data: any) => {
          return (
            <span class="font-bold text-[var(--el-text-color-primary)]">
              {data.row.departmentName}
            </span>
          )
        }
      }
    },
    form: {
      component: 'Input',
      componentProps: {
        placeholder: "Bo'lim yoki filial nomini kiriting (masalan: Bosh Bo'lim, Chorsu Filiali...)"
      },
      colProps: {
        span: 24
      }
    },
    detail: {
      slots: {
        default: (data: any) => {
          return <>{data.departmentName}</>
        }
      }
    }
  },
  {
    field: 'parentId',
    label: "Yuqori Bo'lim (Ota bo'lim)",
    search: {
      hidden: true
    },
    form: {
      component: 'TreeSelect',
      componentProps: {
        nodeKey: 'id',
        checkStrictly: true,
        props: {
          label: 'departmentName',
          children: 'children'
        },
        placeholder: 'Tanlang (ixtiyoriy)'
      },
      optionApi: async () => {
        const res = await getDepartmentApi()
        return res.data.list
      },
      colProps: {
        span: 24
      }
    },
    detail: {
      hidden: true
    }
  },
  {
    field: 'status',
    label: t('userDemo.status'),
    search: {
      hidden: true
    },
    table: {
      slots: {
        default: (data: any) => {
          const status = data.row.status
          return (
            <>
              <ElTag type={status === 0 ? 'danger' : 'success'}>
                {status === 1 ? t('userDemo.enable') : t('userDemo.disable')}
              </ElTag>
            </>
          )
        }
      }
    },
    form: {
      component: 'Select',
      componentProps: {
        options: [
          {
            value: 1,
            label: t('userDemo.enable')
          },
          {
            value: 0,
            label: t('userDemo.disable')
          }
        ]
      },
      colProps: {
        span: 24
      }
    },
    detail: {
      slots: {
        default: (data: any) => {
          return (
            <>
              <ElTag type={data.status === 0 ? 'danger' : 'success'}>
                {data.status === 1 ? t('userDemo.enable') : t('userDemo.disable')}
              </ElTag>
            </>
          )
        }
      }
    }
  },
  {
    field: 'createTime',
    label: t('tableDemo.displayTime'),
    search: {
      hidden: true
    },
    form: {
      hidden: true
    }
  },
  {
    field: 'remark',
    label: t('userDemo.remark'),
    search: {
      hidden: true
    },
    form: {
      component: 'Input',
      componentProps: {
        type: 'textarea',
        rows: 3,
        placeholder: 'Izoh yozing...'
      },
      colProps: {
        span: 24
      }
    },
    detail: {
      slots: {
        default: (data: any) => {
          return <>{data.remark}</>
        }
      }
    }
  },
  {
    field: 'action',
    minWidth: '200px',
    width: '200px',
    label: t('tableDemo.action'),
    search: {
      hidden: true
    },
    form: {
      hidden: true
    },
    detail: {
      hidden: true
    },
    table: {
      slots: {
        default: (data: any) => {
          return (
            <div class="flex items-center gap-6px flex-nowrap whitespace-nowrap">
              <BaseButton type="primary" size="small" onClick={() => action(data.row, 'edit')}>
                {t('exampleDemo.edit')}
              </BaseButton>
              <BaseButton type="success" size="small" onClick={() => action(data.row, 'detail')}>
                {t('exampleDemo.detail')}
              </BaseButton>
              <BaseButton type="danger" size="small" onClick={() => delData(data.row)}>
                {t('exampleDemo.del')}
              </BaseButton>
            </div>
          )
        }
      }
    }
  }
])

// @ts-ignore
const { allSchemas } = useCrudSchemas(crudSchemas)

const dialogVisible = ref(false)
const dialogTitle = ref('')

const currentRow = ref<DepartmentItem | null>(null)
const actionType = ref('')

const AddAction = () => {
  dialogTitle.value = t('exampleDemo.add')
  currentRow.value = {
    status: 1
  } as any
  dialogVisible.value = true
  actionType.value = ''
}

const delLoading = ref(false)

const delData = async (row: DepartmentItem | null) => {
  const elTableExpose = await getElTableExpose()
  ids.value = row
    ? [row.id]
    : elTableExpose?.getSelectionRows().map((v: DepartmentItem) => v.id) || []
  delLoading.value = true
  await delList(unref(ids).length).finally(() => {
    delLoading.value = false
  })
}

const action = (row: DepartmentItem, type: string) => {
  dialogTitle.value = t(type === 'edit' ? 'exampleDemo.edit' : 'exampleDemo.detail')
  actionType.value = type
  currentRow.value = row
  dialogVisible.value = true
}

const writeRef = ref<ComponentRef<typeof Write>>()

const saveLoading = ref(false)

const save = async () => {
  const write = unref(writeRef)
  const formData = await write?.submit()
  if (formData) {
    saveLoading.value = true
    const res = await saveDepartmentApi(formData)
      .catch(() => {})
      .finally(() => {
        saveLoading.value = false
      })
    if (res) {
      dialogVisible.value = false
      currentPage.value = 1
      getList()
    }
  }
}
</script>

<template>
  <ContentWrap>
    <Search :schema="allSchemas.searchSchema" @search="setSearchParams" @reset="setSearchParams" />

    <div class="mb-10px flex gap-8px">
      <BaseButton type="primary" @click="AddAction">{{ t('exampleDemo.add') }}</BaseButton>
      <BaseButton :loading="delLoading" type="danger" @click="delData(null)">
        {{ t('exampleDemo.del') }}
      </BaseButton>
    </div>

    <Table
      v-model:pageSize="pageSize"
      v-model:currentPage="currentPage"
      :columns="allSchemas.tableColumns"
      :data="dataList"
      :loading="loading"
      :pagination="{
        total: total
      }"
      @register="tableRegister"
    />
  </ContentWrap>

  <ResizeDialog
    v-model="dialogVisible"
    :title="dialogTitle"
    :init-width="dialogInitWidth"
    :init-height="dialogInitHeight"
    :min-resize-width="500"
    :min-resize-height="380"
    class="dept-custom-dialog"
  >
    <div class="p-12px flex-1 h-full min-h-0">
      <Write
        v-if="actionType !== 'detail'"
        ref="writeRef"
        :form-schema="allSchemas.formSchema"
        :current-row="currentRow"
      />

      <Detail
        v-if="actionType === 'detail'"
        :detail-schema="allSchemas.detailSchema"
        :current-row="currentRow"
      />
    </div>

    <template #footer>
      <div class="flex justify-end gap-10px pt-8px border-t border-gray-700">
        <BaseButton
          v-if="actionType !== 'detail'"
          type="primary"
          :loading="saveLoading"
          @click="save"
        >
          {{ t('exampleDemo.save') }}
        </BaseButton>
        <BaseButton @click="dialogVisible = false">{{ t('dialogDemo.close') }}</BaseButton>
      </div>
    </template>
  </ResizeDialog>
</template>

<style lang="less">
.dept-custom-dialog {
  &.el-dialog {
    background: var(--el-bg-color-overlay, #ffffff) !important;
    border: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
    border-radius: 12px !important;

    .el-dialog__header {
      padding: 14px 20px !important;
      background: var(--el-fill-color-light, #f8fafc) !important;
      border-bottom: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
    }

    .el-dialog__body {
      padding: 16px !important;
      background: var(--el-bg-color-overlay, #ffffff) !important;
    }

    .el-dialog__footer {
      padding: 12px 20px !important;
      border-top: 1px solid var(--el-border-color-lighter, #e2e8f0) !important;
      background: var(--el-fill-color-light, #f8fafc) !important;
    }
  }
}

:global(.dark) {
  .dept-custom-dialog {
    &.el-dialog {
      background: #1f2937 !important;
      border-color: #374151 !important;

      .el-dialog__header {
        background: #1f2937 !important;
        border-bottom-color: #374151 !important;
      }

      .el-dialog__body {
        background: #1f2937 !important;
      }

      .el-dialog__footer {
        background: #111827 !important;
        border-top-color: #374151 !important;
      }
    }
  }
}
</style>
