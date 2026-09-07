<script setup lang="tsx">
import { PropType, ref, unref, computed, watch, nextTick } from 'vue'
import { Descriptions, DescriptionsSchema } from '@/components/Descriptions'
import { ElTag, ElTree, ElInput } from 'element-plus'
import { Icon } from '@/components/Icon'
import { getMenuListApi } from '@/api/menu'
import { eachTree } from '@/utils/tree'

const props = defineProps({
  currentRow: {
    type: Object as PropType<any>,
    default: () => undefined
  }
})

const filterPermissionName = (value: string) => {
  const perms = unref(currentTreeData)?.permissionList || []
  const found = perms.find((item: any) => item.value === value)
  if (found?.label) return found.label
  if (value.endsWith(':view')) return 'Ko‘rish'
  if (value.endsWith(':create') || value.endsWith(':add')) return 'Qo‘shish'
  if (value.endsWith(':edit') || value.endsWith(':update')) return 'Tahrirlash'
  if (value.endsWith(':delete') || value.endsWith(':del')) return 'O‘chirish'
  if (value.endsWith(':export')) return 'Eksport'
  return value
}

const renderTag = (enable?: boolean) => {
  return <ElTag type={!enable ? 'danger' : 'success'}>{enable ? 'Faol' : "O'chirilgan"}</ElTag>
}

const treeRef = ref<any>()
const treeSearchKeyword = ref('')
const currentTreeData = ref<any>()
const treeData = ref<any[]>([])

const filterNode = (value: string, data: any) => {
  if (!value) return true
  const title = data.title || data.meta?.title || ''
  return title.toLowerCase().includes(value.toLowerCase())
}

watch(treeSearchKeyword, (val) => {
  unref(treeRef)?.filter(val)
})

const nodeClick = (treeNode: any) => {
  currentTreeData.value = treeNode
}

// Set of active permissions for the current role
const activePermissionSet = computed(() => {
  const set = new Set<string>()
  if (!props.currentRow) return set
  const perms = props.currentRow.permissions
  if (Array.isArray(perms)) {
    perms.forEach((p: any) => {
      if (typeof p === 'string') {
        set.add(p)
      } else if (p && typeof p === 'object') {
        if (p.path) set.add(p.path)
        if (p.meta && Array.isArray(p.meta.permission)) {
          p.meta.permission.forEach((action: string) => set.add(action))
        }
      }
    })
  }
  return set
})

const isSuperAdmin = computed(() => {
  if (!props.currentRow) return false
  const name = props.currentRow.roleName || ''
  return (
    name === 'Super Administrator' ||
    activePermissionSet.value.has('*.*.*') ||
    activePermissionSet.value.has('*')
  )
})

// Check if a specific action is granted
const isActionGranted = (actionVal: string, nodePath?: string) => {
  if (isSuperAdmin.value) return true
  const set = activePermissionSet.value
  if (set.has(actionVal)) return true
  if (nodePath && set.has(nodePath)) return true
  return false
}

// Compute active actions count for a node
const getNodeActionCounts = (node: any) => {
  const total = node.permissionList?.length || 0
  if (isSuperAdmin.value) return { active: total, total }
  if (!node.permissionList || total === 0) {
    const hasPath = node.path && activePermissionSet.value.has(node.path)
    return { active: hasPath ? 1 : 0, total: hasPath ? 1 : 0 }
  }
  const active = node.permissionList.filter((a: any) => isActionGranted(a.value, node.path)).length
  return { active, total }
}

const syncData = async () => {
  const res = await getMenuListApi()
  if (res && res.data) {
    treeData.value = res.data.list || []
    await nextTick()
    if (treeData.value.length > 0) {
      let firstActive: any = null
      eachTree(treeData.value, (node: any) => {
        if (!firstActive) {
          const counts = getNodeActionCounts(node)
          if (counts.active > 0) firstActive = node
        }
      })
      currentTreeData.value = firstActive || treeData.value[0]
    }
  }
}

watch(
  () => props.currentRow,
  () => {
    syncData()
  },
  { immediate: true }
)

const detailSchema = ref<DescriptionsSchema[]>([
  {
    field: 'roleName',
    label: 'Rol Nomi',
    slots: {
      default: (data: any) => {
        return (
          <div class="flex items-center gap-10px">
            <span class="font-bold text-15px text-[var(--el-text-color-primary)]">
              {data.roleName}
            </span>
            {isSuperAdmin.value ? (
              <ElTag type="danger" effect="dark" class="font-bold">
                Tizimning to'liq huquqi (*.*.*)
              </ElTag>
            ) : (
              <ElTag type="primary" effect="light" class="font-bold">
                Maxsus Ruxsatlar
              </ElTag>
            )}
          </div>
        )
      }
    }
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
    span: 24,
    slots: {
      default: (data: any) => {
        return (
          <span class="text-slate-600 dark:text-slate-300 italic">
            {data.remark || "Izoh ko'rsatilmagan"}
          </span>
        )
      }
    }
  },
  {
    field: 'permissionList',
    label: 'Biriktirilgan Ruxsatlar & Menyular',
    span: 24,
    slots: {
      default: () => {
        const currentNode = unref(currentTreeData)
        const counts = currentNode ? getNodeActionCounts(currentNode) : { active: 0, total: 0 }
        const perms = currentNode?.permissionList || []

        return (
          <div class="flex w-full gap-16px h-450px min-h-0">
            {/* Left Tree Column */}
            <div class="w-1/2 p-12px rounded-16px border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)] dark:bg-slate-900/60 dark:border-slate-800 flex flex-col min-h-0">
              <div class="mb-10px flex-shrink-0">
                <ElInput
                  v-model={treeSearchKeyword.value}
                  placeholder="Menyuni qidirish..."
                  clearable
                  prefix-icon="vi-ep:search"
                  size="small"
                />
              </div>
              <div class="flex-1 overflow-y-auto min-h-0 pr-4px custom-role-tree">
                <ElTree
                  ref={treeRef}
                  node-key="id"
                  props={{ children: 'children', label: 'title' }}
                  highlight-current
                  default-expand-all
                  expand-on-click-node={false}
                  filter-node-method={filterNode}
                  data={treeData.value}
                  onNode-click={nodeClick}
                >
                  {{
                    default: (data: any) => {
                      const nodeCounts = getNodeActionCounts(data.data)
                      const isSelected = unref(currentTreeData)?.id === data.data.id
                      const hasAccess = nodeCounts.active > 0 || isSuperAdmin.value

                      return (
                        <div
                          class={`flex items-center justify-between w-full py-6px px-8px rounded-lg transition-all ${
                            isSelected
                              ? 'bg-blue-500/15 text-blue-600 dark:text-blue-400 font-bold'
                              : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200/50 dark:hover:bg-slate-800/50'
                          }`}
                        >
                          <div class="flex items-center gap-6px min-w-0 flex-1">
                            <Icon
                              icon={data.data.icon || data.data.meta?.icon || 'vi-ep:document'}
                              size={15}
                              class={hasAccess ? 'text-blue-500' : 'text-slate-400'}
                            />
                            <span class="truncate text-13px">
                              {data.data.title || data.data.meta?.title}
                            </span>
                          </div>
                          {nodeCounts.total > 0 && (
                            <span
                              class={`text-11px px-6px py-1px rounded-full font-bold ml-6px flex-shrink-0 ${
                                nodeCounts.active > 0
                                  ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                                  : 'bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
                              }`}
                            >
                              {nodeCounts.active}/{nodeCounts.total}
                            </span>
                          )}
                        </div>
                      )
                    }
                  }}
                </ElTree>
              </div>
            </div>

            {/* Right Action Column */}
            <div class="w-1/2 p-14px rounded-16px border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)] dark:bg-slate-900/60 dark:border-slate-800 flex flex-col min-h-0">
              <div class="flex items-center justify-between pb-10px mb-12px border-b border-[var(--el-border-color-lighter)] dark:border-slate-800 flex-shrink-0">
                <div class="flex items-center gap-8px font-bold text-14px text-emerald-600 dark:text-emerald-400">
                  <Icon icon="vi-ep:operation" size={17} />
                  <span>Amallar: {currentNode?.title || 'Menyuni tanlang'}</span>
                </div>
                {currentNode && perms.length > 0 && (
                  <ElTag
                    type={counts.active > 0 ? 'success' : 'info'}
                    size="small"
                    class="font-bold"
                  >
                    {counts.active} ta ruxsat faol
                  </ElTag>
                )}
              </div>

              <div class="flex-1 overflow-y-auto min-h-0 pr-4px flex flex-col gap-8px">
                {isSuperAdmin.value && (
                  <div class="p-10px rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-300 text-12px flex items-center gap-8px mb-6px">
                    <Icon icon="vi-ep:circle-check-filled" size={18} class="text-emerald-600" />
                    <span>
                      Super Administrator ushbu bo'limdagi barcha amallarga to'liq kirish huquqiga
                      ega.
                    </span>
                  </div>
                )}

                {perms.length > 0 ? (
                  perms.map((p: any) => {
                    const granted = isActionGranted(p.value, currentNode?.path)
                    return (
                      <div
                        key={p.value}
                        class={`flex items-center justify-between p-10px rounded-xl border transition-all ${
                          granted
                            ? 'bg-emerald-50 border-emerald-300/80 text-emerald-900 dark:bg-emerald-950/40 dark:border-emerald-600/40 dark:text-emerald-200'
                            : 'bg-white border-slate-200 text-slate-400 dark:bg-slate-900/40 dark:border-slate-800 dark:text-slate-500 opacity-70'
                        }`}
                      >
                        <div class="flex items-center gap-10px">
                          <div
                            class={`w-24px h-24px rounded-lg flex items-center justify-center ${
                              granted
                                ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-300'
                                : 'bg-slate-100 text-slate-400 dark:bg-slate-800'
                            }`}
                          >
                            <Icon icon={granted ? 'vi-ep:check' : 'vi-ep:close'} size={14} />
                          </div>
                          <span
                            class={`text-13px ${granted ? 'font-bold text-slate-800 dark:text-slate-100' : 'font-medium'}`}
                          >
                            {p.label || filterPermissionName(p.value)}
                          </span>
                        </div>

                        <ElTag
                          type={granted ? 'success' : 'info'}
                          size="small"
                          effect={granted ? 'dark' : 'plain'}
                          class="font-bold"
                        >
                          {granted ? 'Ruxsat bor' : 'Cheklangan'}
                        </ElTag>
                      </div>
                    )
                  })
                ) : (
                  <div class="text-slate-400 text-13px italic p-16px text-center">
                    Ushbu menyu uchun alohida amallar mavjud emas
                  </div>
                )}
              </div>
            </div>
          </div>
        )
      }
    }
  }
])
</script>

<template>
  <div class="h-full flex flex-col">
    <Descriptions :schema="detailSchema" :data="currentRow || {}" />
  </div>
</template>
