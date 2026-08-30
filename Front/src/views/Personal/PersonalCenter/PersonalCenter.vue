<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
import { ContentWrap } from '@/components/ContentWrap'
import { ref, unref } from 'vue'
import { ElDivider, ElImage, ElTag, ElTabPane, ElTabs, ElButton, ElMessage } from 'element-plus'
import defaultAvatar from '@/assets/imgs/avatar.jpg'
import UploadAvatar from './components/UploadAvatar.vue'
import { Dialog } from '@/components/Dialog'
import EditInfo from './components/EditInfo.vue'
import EditPassword from './components/EditPassword.vue'

import { useUserStore } from '@/store/modules/user'
import { updateUserAvatarApi } from '@/api/login'
import { computed } from 'vue'

const userStore = useUserStore()

const userInfo = computed(() => {
  const u = userStore.getUserInfo
  return {
    id: u?.id || 1,
    username: u?.username || 'Foydalanuvchi',
    realName: u?.full_name || u?.username || 'Foydalanuvchi',
    phoneNumber: (u as any)?.phone || (u as any)?.phoneNumber || '',
    email: (u as any)?.email || '',
    avatarUrl: u?.avatar || '',
    roleList: u?.role ? [u.role] : ['Super Administrator']
  }
})

const activeName = ref('first')

const dialogVisible = ref(false)

const uploadAvatarRef = ref<ComponentRef<typeof UploadAvatar>>()
const avatarLoading = ref(false)
const saveAvatar = async () => {
  try {
    avatarLoading.value = true
    const base64 = unref(uploadAvatarRef)?.getBase64()
    const currentUser = userStore.getUserInfo
    if (base64 && currentUser?.username) {
      const res = await updateUserAvatarApi({
        username: currentUser.username,
        avatar: base64
      })
      if (res && res.data) {
        userStore.setUserInfo(res.data)
      }
    }
    ElMessage.success("Profil rasmi muvaffaqiyatli o'zgartirildi")
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || 'Xatolik yuz berdi')
  } finally {
    avatarLoading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col md:flex-row gap-20px w-full h-full">
    <ContentWrap title="Shaxsiy ma'lumotlar" class="w-full md:w-360px flex-shrink-0">
      <div class="flex flex-col justify-center items-center py-10px">
        <div
          class="avatar w-[130px] h-[130px] relative cursor-pointer group rounded-full overflow-hidden shadow-md border-2 border-[var(--el-border-color)]"
          @click="dialogVisible = true"
        >
          <ElImage
            class="w-full h-full object-cover"
            :src="userInfo?.avatarUrl || defaultAvatar"
            fit="cover"
          />
          <div
            class="absolute inset-0 bg-black/40 text-white text-12px font-bold flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
          >
            O'zgartirish
          </div>
        </div>
        <div class="mt-12px text-16px font-bold text-[var(--el-text-color-primary)]">
          {{ userInfo?.realName }}
        </div>
        <div class="text-13px text-[var(--el-text-color-secondary)]">@{{ userInfo?.username }}</div>
      </div>
      <ElDivider class="!my-12px" />
      <div class="flex justify-between items-center py-6px text-14px">
        <div class="text-[var(--el-text-color-regular)]">Foydalanuvchi:</div>
        <div class="font-mono font-medium">{{ userInfo?.username }}</div>
      </div>
      <ElDivider class="!my-8px" />
      <div class="flex justify-between items-center py-6px text-14px">
        <div class="text-[var(--el-text-color-regular)]">To'liq ism:</div>
        <div class="font-medium">{{ userInfo?.realName }}</div>
      </div>
      <ElDivider class="!my-8px" />
      <div class="flex justify-between items-center py-6px text-14px">
        <div class="text-[var(--el-text-color-regular)]">Telefon raqami:</div>
        <div class="font-mono font-medium">{{ userInfo?.phoneNumber || '—' }}</div>
      </div>
      <ElDivider class="!my-8px" />
      <div class="flex justify-between items-center py-6px text-14px">
        <div class="text-[var(--el-text-color-regular)]">Elektron pochta:</div>
        <div class="font-medium">{{ userInfo?.email || '—' }}</div>
      </div>
      <ElDivider class="!my-8px" />
      <div class="flex justify-between items-center py-6px text-14px">
        <div class="text-[var(--el-text-color-regular)]">Tizimdagi roli:</div>
        <div>
          <ElTag
            v-for="item in userInfo?.roleList || []"
            :key="item"
            type="success"
            effect="plain"
            class="font-bold"
          >
            {{ item }}
          </ElTag>
        </div>
      </div>
    </ContentWrap>
    <ContentWrap title="Profilni tahrirlash" class="flex-1">
      <ElTabs v-model="activeName">
        <ElTabPane label="Asosiy ma'lumotlar" name="first">
          <div class="py-10px max-w-600px">
            <EditInfo :user-info="userInfo" />
          </div>
        </ElTabPane>
        <ElTabPane label="Parolni o'zgartirish" name="second">
          <div class="py-10px max-w-600px">
            <EditPassword />
          </div>
        </ElTabPane>
      </ElTabs>
    </ContentWrap>
  </div>

  <Dialog v-model="dialogVisible" title="Profil rasmini o'zgartirish" width="800px">
    <UploadAvatar ref="uploadAvatarRef" :url="userInfo?.avatarUrl || defaultAvatar" />

    <template #footer>
      <ElButton type="primary" :loading="avatarLoading" @click="saveAvatar">{{
        t('common.save')
      }}</ElButton>
      <ElButton @click="dialogVisible = false">{{ t('common.close') }}</ElButton>
    </template>
  </Dialog>
</template>

<style lang="less" scoped>
.avatar {
  position: relative;

  &::after {
    position: absolute;
    top: 0;
    left: 0;
    display: flex;
    width: 100%;
    height: 100%;
    font-size: 50px;
    color: #fff;
    background-color: rgb(0 0 0 / 40%);
    border-radius: 50%;
    content: '+';
    opacity: 0;
    justify-content: center;
    align-items: center;
  }

  &:hover {
    &::after {
      opacity: 1;
    }
  }
}
</style>
