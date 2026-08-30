<script setup lang="ts">
import { ElDrawer, ElDivider, ElMessage } from 'element-plus'
import { ref, unref, watch, computed } from 'vue'
import { useI18n } from '@/hooks/web/useI18n'
import { ThemeSwitch } from '@/components/ThemeSwitch'
import { Icon } from '@/components/Icon'
import { useAppStore } from '@/store/modules/app'
import { setCssVar } from '@/utils'
import ColorRadioPicker from './components/ColorRadioPicker.vue'
import InterfaceDisplay from './components/InterfaceDisplay.vue'
import LayoutRadioPicker from './components/LayoutRadioPicker.vue'
import { useStorage } from '@/hooks/web/useStorage'
import { useClipboard } from '@vueuse/core'

const { clear: storageClear } = useStorage('localStorage')

const appStore = useAppStore()

const { t } = useI18n()

const drawer = computed({
  get: () => appStore.getSettingDrawer,
  set: (val: boolean) => appStore.setSettingDrawer(val)
})

// 主题色相关
const systemTheme = ref(appStore.getTheme.elColorPrimary)
watch(
  () => appStore.getTheme.elColorPrimary,
  (val) => {
    if (val) systemTheme.value = val
  }
)

const setSystemTheme = (color: string) => {
  setCssVar('--el-color-primary', color)
  appStore.setTheme({ elColorPrimary: color })
  const leftMenuBgColor = appStore.getTheme.leftMenuBgColor || '#001529'
  setMenuTheme(leftMenuBgColor)
}

// 头部主题相关
const headerTheme = ref(appStore.getTheme.topHeaderBgColor || '')
watch(
  () => appStore.getTheme.topHeaderBgColor,
  (val) => {
    if (val) headerTheme.value = val
  }
)

const setHeaderTheme = (color: string) => {
  appStore.setHeaderTheme(color)
}

// 菜单主题相关
const menuTheme = ref(appStore.getTheme.leftMenuBgColor || '')
watch(
  () => appStore.getTheme.leftMenuBgColor,
  (val) => {
    if (val) menuTheme.value = val
  }
)

const setMenuTheme = (color: string) => {
  appStore.setMenuTheme(color)
}

// 监听layout变化，重置一些主题色
// watch(
//   () => layout.value,
//   (n) => {
//     if (n === 'top' && !appStore.getIsDark) {
//       headerTheme.value = '#fff'
//       setHeaderTheme('#fff')
//     } else {
//       setMenuTheme(unref(menuTheme))
//     }
//   }
// )

// 拷贝
const copyConfig = async () => {
  const { copy, copied, isSupported } = useClipboard({
    source: JSON.stringify({
      theme: unref(systemTheme),
      headerTheme: unref(headerTheme),
      menuTheme: unref(menuTheme)
    })
  })
  if (!isSupported) {
    ElMessage.error(t('setting.copyFailed'))
  } else {
    await copy()
    if (unref(copied)) {
      ElMessage.success(t('setting.copySuccess'))
    }
  }
}

// 清空缓存
const clear = () => {
  storageClear()
  window.location.reload()
}
</script>

<template>
  <!-- Floating Setting Gear Button (Color matches Asosiy urg'u rangi) -->
  <div
    class="setting-fixed-btn"
    :style="{ backgroundColor: systemTheme || 'var(--el-color-primary)' }"
    title="Loyiha Sozlamalari"
    @click="drawer = true"
  >
    <Icon icon="vi-ant-design:setting-outlined" class="setting-gear-icon" />
  </div>

  <ElDrawer v-model="drawer" direction="rtl" size="350px" :z-index="4000">
    <template #header>
      <span class="text-16px font-700">{{ t('setting.projectSetting') }}</span>
    </template>

    <div class="text-center">
      <!-- 主题 -->
      <ElDivider>{{ t('setting.theme') }}</ElDivider>
      <ThemeSwitch />

      <!-- 布局 -->
      <ElDivider>{{ t('setting.layout') }}</ElDivider>
      <LayoutRadioPicker />

      <!-- 系统主题 -->
      <ElDivider>{{ t('setting.systemTheme') }}</ElDivider>
      <ColorRadioPicker
        v-model="systemTheme"
        :schema="[
          '#409eff',
          '#009688',
          '#536dfe',
          '#ff5c93',
          '#ee4f12',
          '#0096c7',
          '#9c27b0',
          '#ff9800'
        ]"
        @change="setSystemTheme"
      />

      <!-- 头部主题 -->
      <ElDivider>{{ t('setting.headerTheme') }}</ElDivider>
      <ColorRadioPicker
        v-model="headerTheme"
        :schema="[
          '#fff',
          '#151515',
          '#5172dc',
          '#e74c3c',
          '#24292e',
          '#394664',
          '#009688',
          '#383f45'
        ]"
        @change="setHeaderTheme"
      />

      <!-- 菜单主题 -->
      <ElDivider>{{ t('setting.menuTheme') }}</ElDivider>
      <ColorRadioPicker
        v-model="menuTheme"
        :schema="[
          '#fff',
          '#001529',
          '#212121',
          '#273352',
          '#191b24',
          '#383f45',
          '#001628',
          '#344058'
        ]"
        @change="setMenuTheme"
      />
    </div>

    <!-- 界面显示 -->
    <ElDivider>{{ t('setting.interfaceDisplay') }}</ElDivider>
    <InterfaceDisplay />

    <ElDivider />
    <div>
      <BaseButton type="primary" class="w-full" @click="copyConfig">{{
        t('setting.copy')
      }}</BaseButton>
    </div>
    <div class="mt-5px">
      <BaseButton type="danger" class="w-full" @click="clear">
        {{ t('setting.clearAndReset') }}
      </BaseButton>
    </div>
  </ElDrawer>
</template>

<style lang="less" scoped>
@prefix-cls: ~'@{adminNamespace}-setting';

.@{prefix-cls} {
  border-radius: 6px 0 0 6px;
}

.setting-fixed-btn {
  position: fixed;
  top: 45%;
  right: 0;
  z-index: 3000;
  width: 42px;
  height: 42px;
  background-color: var(--el-color-primary, #409eff);
  color: #ffffff;
  border-radius: 6px 0 0 6px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
  transition: all 0.25s ease;

  &:hover {
    filter: brightness(1.12);
    transform: scale(1.08);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
  }

  .setting-gear-icon {
    font-size: 20px;
    color: #ffffff;
  }
}
</style>
