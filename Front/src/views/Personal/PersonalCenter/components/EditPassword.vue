<script setup lang="ts">
import { Form, FormSchema } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { reactive, ref } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
import { ElMessage, ElMessageBox, ElDivider } from 'element-plus'

const { required } = useValidator()

const formSchema = reactive<FormSchema[]>([
  {
    field: 'password',
    label: 'Eski parol',
    component: 'InputPassword',
    colProps: {
      span: 24
    }
  },
  {
    field: 'newPassword',
    label: 'Yangi parol',
    component: 'InputPassword',
    colProps: {
      span: 24
    },
    componentProps: {
      strength: true
    }
  },
  {
    field: 'newPassword2',
    label: 'Yangi parolni tasdiqlang',
    component: 'InputPassword',
    colProps: {
      span: 24
    },
    componentProps: {
      strength: true
    }
  }
])

const rules = reactive({
  password: [required()],
  newPassword: [
    required(),
    {
      asyncValidator: async (_, val, callback) => {
        const formData = await getFormData()
        const { newPassword2 } = formData
        if (val !== newPassword2) {
          callback(new Error('Yangi parol va tasdiqlovchi parol mos kelmadi'))
        } else {
          callback()
        }
      }
    }
  ],
  newPassword2: [
    required(),
    {
      asyncValidator: async (_, val, callback) => {
        const formData = await getFormData()
        const { newPassword } = formData
        if (val !== newPassword) {
          callback(new Error('Tasdiqlovchi parol va yangi parol mos kelmadi'))
        } else {
          callback()
        }
      }
    }
  ]
})

const { formRegister, formMethods } = useForm()
const { getFormData, getElFormExpose } = formMethods

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
          const formData = await getFormData()
          const currentUser = userStore.getUserInfo
          if (currentUser && formData.newPassword) {
            const payload = {
              id: currentUser.id,
              username: currentUser.username,
              password: formData.newPassword,
              full_name: currentUser.full_name,
              role: currentUser.role,
              roleId: currentUser.roleId,
              avatar: currentUser.avatar
            }
            const res = await saveUserApi(payload)
            if (res && res.data) {
              userStore.setUserInfo(res.data)
            }
          }
          ElMessage.success("Parol muvaffaqiyatli o'zgartirildi")
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
  <BaseButton type="primary" @click="save">O'zgartirishni tasdiqlash</BaseButton>
</template>
