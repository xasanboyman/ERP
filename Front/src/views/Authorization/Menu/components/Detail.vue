<script setup lang="tsx">
import { PropType, ref } from 'vue'
import { Descriptions, DescriptionsSchema } from '@/components/Descriptions'
import { Icon } from '@/components/Icon'
import { ElTag } from 'element-plus'

defineProps({
  currentRow: {
    type: Object as PropType<any>,
    default: () => undefined
  }
})

const renderTag = (enable?: boolean) => {
  return <ElTag type={!enable ? 'danger' : 'success'}>{enable ? 'Faol' : 'Nofaol'}</ElTag>
}

const detailSchema = ref<DescriptionsSchema[]>([
  {
    field: 'type',
    label: 'Menyu turi',
    span: 24,
    slots: {
      default: (data) => {
        const type = data.type
        return <>{type === 1 ? 'Menyu' : 'Katalog'}</>
      }
    }
  },
  {
    field: 'parentName',
    label: 'Ota menyu'
  },
  {
    field: 'meta.title',
    label: 'Menyu nomi'
  },
  {
    field: 'component',
    label: 'Komponent',
    slots: {
      default: (data) => {
        const component = data.component
        return (
          <>
            {component === '#'
              ? 'Tizim (Top katalog)'
              : component === '##'
                ? 'Ostki katalog'
                : component}
          </>
        )
      }
    }
  },
  {
    field: 'name',
    label: 'Komponent nomi'
  },
  {
    field: 'meta.icon',
    label: 'Belgi',
    slots: {
      default: (data) => {
        const icon = data.icon
        if (icon) {
          return (
            <>
              <Icon icon={icon} />
            </>
          )
        } else {
          return null
        }
      }
    }
  },
  {
    field: 'path',
    label: "Yo'l"
  },
  {
    field: 'meta.activeMenu',
    label: 'Faol menyu'
  },
  {
    field: 'permissionList',
    label: 'Ruxsatlar',
    span: 24,
    slots: {
      default: (data: any) => (
        <>
          {data?.permissionList?.map((v) => {
            return (
              <ElTag class="mr-1" key={v.value}>
                {v.label}
              </ElTag>
            )
          })}
        </>
      )
    }
  },
  {
    field: 'menuState',
    label: 'Holati',
    slots: {
      default: (data) => {
        return renderTag(data.menuState)
      }
    }
  },
  {
    field: 'meta.hidden',
    label: 'Yashirin',
    slots: {
      default: (data) => {
        return renderTag(data.enableHidden)
      }
    }
  },
  {
    field: 'meta.alwaysShow',
    label: "Har doim ko'rsatish",
    slots: {
      default: (data) => {
        return renderTag(data.enableDisplay)
      }
    }
  },
  {
    field: 'meta.noCache',
    label: 'Keshlamaslik',
    slots: {
      default: (data) => {
        return renderTag(data.enableCleanCache)
      }
    }
  },
  {
    field: 'meta.breadcrumb',
    label: 'Navigatsiya (Breadcrumb)',
    slots: {
      default: (data) => {
        return renderTag(data.enableShowCrumb)
      }
    }
  },
  {
    field: 'meta.affix',
    label: 'Birlashtirish',
    slots: {
      default: (data) => {
        return renderTag(data.enablePinnedTab)
      }
    }
  },
  {
    field: 'meta.noTagsView',
    label: 'Yashirin yorliq',
    slots: {
      default: (data) => {
        return renderTag(data.enableHiddenTab)
      }
    }
  },
  {
    field: 'meta.canTo',
    label: "O'tish mumkin",
    slots: {
      default: (data) => {
        return renderTag(data.enableSkip)
      }
    }
  }
])
</script>

<template>
  <Descriptions :schema="detailSchema" :data="currentRow || {}" />
</template>
