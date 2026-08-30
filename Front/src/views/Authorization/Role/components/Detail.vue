<script setup lang="tsx">
import { PropType, ref, unref, nextTick } from 'vue'
import { Descriptions, DescriptionsSchema } from '@/components/Descriptions'
import { ElTag, ElTree } from 'element-plus'
import { findIndex } from '@/utils'
import { getMenuListApi } from '@/api/menu'

defineProps({
  currentRow: {
    type: Object as PropType<any>,
    default: () => undefined
  }
})

const filterPermissionName = (value: string) => {
  const index = findIndex(unref(currentTreeData)?.permissionList || [], (item) => {
    return item.value === value
  })
  return (unref(currentTreeData)?.permissionList || [])[index].label ?? ''
}

const renderTag = (enable?: boolean) => {
  return <ElTag type={!enable ? 'danger' : 'success'}>{enable ? 'Faol' : "O'chirilgan"}</ElTag>
}

const treeRef = ref<typeof ElTree>()

const currentTreeData = ref()
const nodeClick = (treeData: any) => {
  currentTreeData.value = treeData
}

const treeData = ref<any[]>([])
const getMenuList = async () => {
  const res = await getMenuListApi()
  if (res) {
    treeData.value = res.data.list
    await nextTick()
  }
}
getMenuList()

const detailSchema = ref<DescriptionsSchema[]>([
  {
    field: 'roleName',
    label: 'Rol Nomi'
  },
  {
    field: 'status',
    label: 'Holati',
    slots: {
      default: (data: any) => {
        return renderTag(data.status === 1 || data.status === true)
      }
    }
  },
  {
    field: 'remark',
    label: 'Izoh',
    span: 24
  },
  {
    field: 'permissionList',
    label: 'Biriktirilgan Ruxsatlar & Menyular',
    span: 24,
    slots: {
      default: () => {
        return (
          <>
            <div class="flex w-full gap-16px">
              <div class="flex-1 p-12px rounded-12px border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)]">
                <ElTree
                  ref={treeRef}
                  node-key="id"
                  props={{ children: 'children', label: 'title' }}
                  highlight-current
                  expand-on-click-node={false}
                  data={treeData.value}
                  onNode-click={nodeClick}
                >
                  {{
                    default: (data) => {
                      return (
                        <span class="text-13px font-medium text-[var(--el-text-color-primary)]">
                          {data?.data?.title}
                        </span>
                      )
                    }
                  }}
                </ElTree>
              </div>
              <div class="flex-1 p-12px rounded-12px border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)] flex flex-wrap gap-8px content-start">
                {unref(currentTreeData) &&
                unref(currentTreeData)?.meta?.permission &&
                unref(currentTreeData)?.meta?.permission?.length > 0 ? (
                  unref(currentTreeData)?.meta?.permission?.map((v: string) => {
                    return (
                      <ElTag type="success" effect="light" class="font-bold">
                        {filterPermissionName(v)}
                      </ElTag>
                    )
                  })
                ) : (
                  <span class="text-slate-400 text-13px italic p-8px">
                    Ushbu menyu uchun biriktirilgan amallar yo'q
                  </span>
                )}
              </div>
            </div>
          </>
        )
      }
    }
  }
])
</script>

<template>
  <Descriptions :schema="detailSchema" :data="currentRow || {}" />
</template>
