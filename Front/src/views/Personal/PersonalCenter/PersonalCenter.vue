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
import ConnectedDevices from './components/ConnectedDevices.vue'

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
    roleList: u?.role ? [u.role] : ['Foydalanuvchi']
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
  <div class="flex w-100% h-100%">
    <ContentWrap title="Shaxsiy ma'lumotlar" class="w-400px">
      <div class="flex justify-center items-center">
        <div
          class="avatar w-[150px] h-[150px] relative cursor-pointer"
          @click="dialogVisible = true"
        >
          <ElImage
            class="w-[150px] h-[150px] rounded-full"
            :src="userInfo?.avatarUrl || defaultAvatar"
            fit="fill"
          />
        </div>
      </div>
      <ElDivider />
      <div class="flex justify-between items-center">
        <div>Akkaunt:</div>
        <div>{{ userInfo?.username }}</div>
      </div>
      <ElDivider />
      <div class="flex justify-between items-center">
        <div>Taxallus:</div>
        <div>{{ userInfo?.realName }}</div>
      </div>
      <ElDivider />
      <div class="flex justify-between items-center">
        <div>Telefon raqami:</div>
        <div>{{ userInfo?.phoneNumber ?? '-' }}</div>
      </div>
      <ElDivider />
      <div class="flex justify-between items-center">
        <div>Elektron pochta:</div>
        <div>{{ userInfo?.email ?? '-' }}</div>
      </div>
      <ElDivider />
      <div class="flex justify-between items-center">
        <div>Roli:</div>
        <div>
          <template v-if="userInfo?.roleList?.length">
            <ElTag v-for="item in userInfo?.roleList || []" :key="item" class="ml-2 mb-w"
              >{{ item }}
            </ElTag>
          </template>
          <template v-else>-</template>
        </div>
      </div>
      <ElDivider />
    </ContentWrap>
    <ContentWrap title="Asosiy ma'lumotlar" class="flex-[3] ml-20px">
      <ElTabs v-model="activeName">
        <ElTabPane label="Asosiy ma'lumotlar" name="first">
          <EditInfo :user-info="userInfo" />
        </ElTabPane>
        <ElTabPane label="Parolni o'zgartirish" name="second">
          <EditPassword />
        </ElTabPane>
        <ElTabPane label="Ulangan qurilmalar" name="third">
          <ConnectedDevices />
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
