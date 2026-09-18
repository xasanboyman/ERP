<script setup lang="tsx">
import { reactive, ref, watch, onMounted, unref } from 'vue'
import { Form, FormSchema } from '@/components/Form'
import { useI18n } from '@/hooks/web/useI18n'
import { ElCheckbox, ElLink, ElAlert } from 'element-plus'
import { useForm } from '@/hooks/web/useForm'
import { loginApi, getAdminRoleApi } from '@/api/login'
import { useAppStore } from '@/store/modules/app'
import { usePermissionStore } from '@/store/modules/permission'
import { useRouter } from 'vue-router'
import type { RouteLocationNormalizedLoaded, RouteRecordRaw } from 'vue-router'
import { UserType } from '@/api/login/types'
import { useValidator } from '@/hooks/web/useValidator'
import { Icon } from '@/components/Icon'
import { useUserStore } from '@/store/modules/user'
import { useTagsViewStore } from '@/store/modules/tagsView'
import { BaseButton } from '@/components/Button'
import { SUCCESS_CODE } from '@/constants'

const { required } = useValidator()

const appStore = useAppStore()

const userStore = useUserStore()

const tagsViewStore = useTagsViewStore()

const permissionStore = usePermissionStore()

const { currentRoute, addRoute, push } = useRouter()

const { t } = useI18n()

const rules = {
  username: [required()],
  password: [required()]
}

const schema = reactive<FormSchema[]>([
  {
    field: 'title',
    colProps: {
      span: 24
    },
    formItemProps: {
      slots: {
        default: () => {
          return (
            <h2 class="text-2xl font-bold text-center w-[100%] text-slate-800 dark:text-slate-100 mb-10px">
              {t('login.login')}
            </h2>
          )
        }
      }
    }
  },
  {
    field: 'username',
    label: t('login.username'),
    component: 'Input',
    colProps: {
      span: 24
    },
    componentProps: {
      placeholder: t('login.usernamePlaceholder')
    }
  },
  {
    field: 'password',
    label: t('login.password'),
    component: 'InputPassword',
    colProps: {
      span: 24
    },
    componentProps: {
      style: {
        width: '100%'
      },
      placeholder: t('login.passwordPlaceholder'),
      onKeydown: (_e: any) => {
        if (_e.key === 'Enter') {
          _e.stopPropagation()
          signIn()
        }
      }
    }
  },
  {
    field: 'error',
    colProps: {
      span: 24
    },
    formItemProps: {
      slots: {
        default: () => {
          if (!unref(errorMessage)) return null
          return (
            <ElAlert
              title={unref(errorMessage)}
              type="error"
              show-icon
              closable
              onClose={() => {
                errorMessage.value = ''
              }}
            />
          )
        }
      }
    }
  },
  {
    field: 'tool',
    colProps: {
      span: 24
    },
    formItemProps: {
      slots: {
        default: () => {
          return (
            <>
              <div class="flex justify-between items-center w-[100%]">
                <ElCheckbox v-model={remember.value} label={t('login.remember')} size="small" />
                <ElLink type="primary" underline={false}>
                  {t('login.forgetPassword')}
                </ElLink>
              </div>
            </>
          )
        }
      }
    }
  },
  {
    field: 'login',
    colProps: {
      span: 24
    },
    formItemProps: {
      slots: {
        default: () => {
          return (
            <div class="w-[100%]">
              <BaseButton loading={loading.value} type="primary" class="w-[100%]" onClick={signIn}>
                {t('login.login')}
              </BaseButton>
            </div>
          )
        }
      }
    }
  }
])

const iconSize = 30

const remember = ref(userStore.getRememberMe)

const errorMessage = ref('')

const initLoginInfo = () => {
  const savedUsername = userStore.getLoginInfo
  if (savedUsername && unref(remember)) {
    setValues({ username: savedUsername })
  }
}
onMounted(() => {
  initLoginInfo()
})

const { formRegister, formMethods } = useForm()
const { getFormData, getElFormExpose, setValues } = formMethods

const loading = ref(false)

const iconColor = '#999'

const hoverColor = 'var(--el-color-primary)'

const redirect = ref<string>('')

watch(
  () => currentRoute.value,
  (route: RouteLocationNormalizedLoaded) => {
    redirect.value = route?.query?.redirect as string
  },
  {
    immediate: true
  }
)

watch(
  () => remember.value,
  (newVal) => {
    userStore.setRememberMe(newVal)
    if (!newVal) {
      userStore.setLoginInfo(undefined)
    }
  }
)

// 登录
const signIn = async () => {
  const formRef = await getElFormExpose()
  await formRef?.validate(async (isValid) => {
    if (isValid) {
      loading.value = true
      errorMessage.value = ''
      const formData = await getFormData<UserType>()

      try {
        const res = await loginApi(formData)

        if (res && res.code === SUCCESS_CODE && (res.data as any)?.token) {
          // 是否记住我 - 只保存用户名
          if (unref(remember)) {
            userStore.setLoginInfo(formData.username)
          } else {
            userStore.setLoginInfo(undefined)
          }
          userStore.setRememberMe(unref(remember))
          userStore.setToken((res.data as any).token)
          userStore.setUserInfo(res.data)
          // Wipe all visited tagsView tabs from any previous session!
          tagsViewStore.clearAll()
          // 是否使用动态路由
          if (appStore.getDynamicRouter) {
            getRole()
          } else {
            await permissionStore.generateRoutes('static').catch(() => {})
            permissionStore.getAddRouters.forEach((route) => {
              addRoute(route as RouteRecordRaw) // 动态添加可访问路由表
            })
            const targetPath =
              redirect.value && redirect.value !== '/404' && redirect.value !== '/login'
                ? redirect.value
                : permissionStore.addRouters[0]?.path || '/sales/pos'
            push({ path: targetPath })
          }
        } else {
          errorMessage.value =
            (res as any)?.message ||
            'Kirish muvaffaqiyatsiz tugadi, iltimos foydalanuvchi nomi va parolni tekshiring'
        }
      } catch (error: any) {
        errorMessage.value =
          error?.message ||
          'Kirish muvaffaqiyatsiz tugadi, iltimos foydalanuvchi nomi va parolni tekshiring'
      } finally {
        loading.value = false
      }
    }
  })
}

const extractAllRoutePaths = (routes: any[], parent = ''): string[] => {
  let result: string[] = []
  for (const r of routes) {
    if (!r.path || r.meta?.hidden) continue
    const full = r.path.startsWith('/')
      ? r.path
      : `${parent}/${r.path}`.replace(/\/+/g, '/')
    result.push(full.toLowerCase().replace(/\/$/, ''))
    if (r.children && r.children.length > 0) {
      result = result.concat(extractAllRoutePaths(r.children, full))
    }
  }
  return result
}

const getFirstRoutePath = (routes: any[]): string => {
  if (!routes || routes.length === 0) return '/login'
  for (const route of routes) {
    if (route.meta?.hidden) continue
    if (route.children && route.children.length > 0) {
      for (const child of route.children) {
        if (child.meta?.hidden) continue
        const parentPath = route.path.startsWith('/') ? route.path : `/${route.path}`
        const childPath = child.path.startsWith('/') ? child.path : `/${child.path}`
        return parentPath === '/' ? childPath : `${parentPath}/${childPath}`.replace(/\/+/g, '/')
      }
    } else if (route.path) {
      return route.path.startsWith('/') ? route.path : `/${route.path}`
    }
  }
  return '/login'
}

// 获取角色信息
const getRole = async () => {
  const res = await getAdminRoleApi()
  if (res) {
    let routers: any = res.data || []
    if (!Array.isArray(routers)) {
      if (routers && typeof routers === 'object' && Array.isArray(routers.list)) {
        routers = routers.list
      } else {
        routers = []
      }
    }
    userStore.setRoleRouters(routers)
    appStore.getDynamicRouter && appStore.getServerDynamicRouter
      ? await permissionStore.generateRoutes('server', routers).catch(() => {})
      : await permissionStore.generateRoutes('frontEnd', routers).catch(() => {})

    permissionStore.getAddRouters.forEach((route) => {
      addRoute(route as RouteRecordRaw) // 动态添加可访问路由表
    })
    permissionStore.setIsAddRouters(true)

    const allowedPaths = extractAllRoutePaths(permissionStore.getRouters)
    tagsViewStore.pruneUnauthorizedViews(allowedPaths)

    const firstAllowed = getFirstRoutePath(permissionStore.getAddRouters)
    const userInfo = userStore.getUserInfo
    const roleStr = String(userInfo?.role || '').toLowerCase()
    const isCashier = roleStr.includes('cashier') || roleStr.includes('kassir')

    let targetPath = firstAllowed
    if (
      redirect.value &&
      redirect.value !== '/404' &&
      redirect.value !== '/login' &&
      redirect.value !== '/'
    ) {
      const cleanRedirect = redirect.value.toLowerCase().replace(/\/$/, '')
      const isRedirectAllowed =
        allowedPaths.includes(cleanRedirect) &&
        (!isCashier ||
          (!cleanRedirect.startsWith('/dashboard') &&
            !cleanRedirect.startsWith('/sales/debtors') &&
            !cleanRedirect.startsWith('/hr') &&
            !cleanRedirect.startsWith('/authorization') &&
            !cleanRedirect.startsWith('/company')))

      if (isRedirectAllowed) {
        targetPath = redirect.value
      }
    }

    if (
      isCashier &&
      (!targetPath ||
        targetPath.startsWith('/dashboard') ||
        targetPath.startsWith('/sales/debtors') ||
        targetPath === '/login' ||
        targetPath === '/')
    ) {
      targetPath = '/sales/pos'
    }

    push({ path: targetPath })
  }
}
</script>

<template>
  <Form
    :schema="schema"
    :rules="rules"
    label-position="top"
    hide-required-asterisk
    size="large"
    class="dark:(border-1 border-[var(--el-border-color)] border-solid)"
    @register="formRegister"
  />
</template>
