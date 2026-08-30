<script lang="ts" setup>
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
import { FormSchema, Form } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { useValidator } from '@/hooks/web/useValidator'
import { reactive, ref, watch } from 'vue'
import { ElDivider, ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  userInfo: {
    type: Object,
    default: () => ({})
  }
})

const { required, phone, maxlength, email } = useValidator()

const formSchema = reactive<FormSchema[]>([
  {
    field: 'realName',
    label: 'Taxallus',
    component: 'Input',
    colProps: {
      span: 24
    }
  },
  {
    field: 'phoneNumber',
    label: 'Telefon raqami',
    component: 'Input',
    colProps: {
      span: 24
    }
  },
  {
    field: 'email',
    label: 'Elektron pochta',
    component: 'Input',
    colProps: {
      span: 24
    }
  }
])

const rules = reactive({
  realName: [required(), maxlength(50)],
  phoneNumber: [phone()],
  email: [email()]
})

const { formRegister, formMethods } = useForm()
const { setValues, getElFormExpose } = formMethods

watch(
  () => props.userInfo,
  (value) => {
    setValues(value)
  },
  {
    immediate: true,
    deep: true
  }
)

import { saveUserApi } from '@/api/login'
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()

const saveLoading = ref(false)
const save = async () => {
  const elForm = await getElFormExpose()
  const valid = await elForm?.validate().catch((err) => {
    console.log(err)
  })
  if (valid) {
    ElMessageBox.confirm("O'zgarishlarni saqlashni tasdiqlaysizmi?", 'Eslatma', {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    })
      .then(async () => {
        try {
          saveLoading.value = true
          const { getFormData } = formMethods
          const formData = await getFormData()
          const currentUser = userStore.getUserInfo
          if (currentUser) {
            const payload = {
              id: currentUser.id,
              username: currentUser.username,
              full_name: formData.realName,
              phone: formData.phoneNumber,
              email: formData.email,
              role: currentUser.role,
              roleId: currentUser.roleId,
              avatar: currentUser.avatar
            }
            const res = await saveUserApi(payload)
            if (res && res.data) {
              userStore.setUserInfo(res.data)
            }
          }
          ElMessage.success("Muvaffaqiyatli o'zgartirildi")
        } catch (error: any) {
          ElMessage.error(error.message || 'Xatolik yuz berdi')
        } finally {
          saveLoading.value = false
        }
      })
      .catch(() => {})
  }
}
</script>

<template>
  <Form :rules="rules" @register="formRegister" :schema="formSchema" />
  <ElDivider />
  <BaseButton type="primary" @click="save">{{ t('common.save') }}</BaseButton>
</template>
