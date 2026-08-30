import { AxiosResponse, InternalAxiosRequestConfig } from './types'
import { ElMessage } from 'element-plus'
import { SUCCESS_CODE, TRANSFORM_REQUEST_DATA } from '@/constants'
import { useUserStoreWithOut } from '@/store/modules/user'
import { objToFormData } from '@/utils'

const defaultRequestInterceptors = (config: InternalAxiosRequestConfig) => {
  if (
    config.method === 'post' &&
    config.headers['Content-Type'] === 'application/x-www-form-urlencoded'
  ) {
    config.data = new URLSearchParams(config.data).toString()
  } else if (
    TRANSFORM_REQUEST_DATA &&
    config.method === 'post' &&
    config.headers['Content-Type'] === 'multipart/form-data' &&
    !(config.data instanceof FormData)
  ) {
    config.data = objToFormData(config.data)
  }
  if (config.method === 'get' && config.params) {
    let url = config.url as string
    url += '?'
    const keys = Object.keys(config.params)
    for (const key of keys) {
      if (config.params[key] !== void 0 && config.params[key] !== null) {
        url += `${key}=${encodeURIComponent(config.params[key])}&`
      }
    }
    url = url.substring(0, url.length - 1)
    config.params = {}
    config.url = url
  }
  return config
}

const isDeviceOrMobileRequest = (config?: any) => {
  const url = config?.url || ''
  const hasDeviceTokenHeader = !!(
    config?.headers &&
    (config.headers['X-Device-Token'] || config.headers['x-device-token'])
  )
  const isMobilePath = typeof window !== 'undefined' && window.location.hash.includes('/mobile')
  const isDeviceEndpoint =
    url.includes('/device/') ||
    url.includes('/sales/push-pc-sale') ||
    url.includes('/sales/phone-checkout')
  return hasDeviceTokenHeader || isMobilePath || isDeviceEndpoint
}

const defaultResponseInterceptors = (response: AxiosResponse) => {
  if (response?.config?.responseType === 'blob') {
    // 如果是文件流，直接过
    return response
  } else if (response?.data?.code === SUCCESS_CODE) {
    return response.data
  } else {
    if (response?.data?.message && !isDeviceOrMobileRequest(response?.config)) {
      ElMessage.error(response.data.message)
    }
    if (!isDeviceOrMobileRequest(response?.config)) {
      if (response?.data?.code === 401 || response?.data?.code === 403) {
        const userStore = useUserStoreWithOut()
        userStore.logout()
      }
    }
    return response.data
  }
}

export { defaultResponseInterceptors, defaultRequestInterceptors }
