import axios, { AxiosError } from 'axios'
import { defaultRequestInterceptors, defaultResponseInterceptors } from './config'

import { AxiosInstance, InternalAxiosRequestConfig, RequestConfig, AxiosResponse } from './types'
import { ElMessage } from 'element-plus'
import { REQUEST_TIMEOUT } from '@/constants'

import { useUserStoreWithOut } from '@/store/modules/user'

export const PATH_URL = import.meta.env.VITE_API_BASE_PATH

const abortControllerMap: Map<string, AbortController> = new Map()

const axiosInstance: AxiosInstance = axios.create({
  timeout: REQUEST_TIMEOUT,
  baseURL: PATH_URL
})

axiosInstance.interceptors.request.use((res: InternalAxiosRequestConfig) => {
  if (res.url) {
    if (res.url.startsWith('/mock')) {
      res.url = res.url.replace(/^\/mock/, '')
    }
    const prefix = PATH_URL || '/api'
    const cleanPrefix = prefix.endsWith('/') ? prefix.slice(0, -1) : prefix
    if (res.url.startsWith(cleanPrefix)) {
      res.url = res.url.slice(cleanPrefix.length)
    }
  }
  const controller = new AbortController()
  const url = res.url || ''
  res.signal = controller.signal
  abortControllerMap.set(url, controller)
  return res
})

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

axiosInstance.interceptors.response.use(
  (res: AxiosResponse) => {
    const url = res.config.url || ''
    abortControllerMap.delete(url)
    return res
  },
  (error: AxiosError) => {
    console.log('err： ' + error) // for debug
    if (!isDeviceOrMobileRequest(error.config)) {
      if (error.response?.status === 401) {
        const userStore = useUserStoreWithOut()
        userStore.logout()
      } else if (error.response?.status === 403) {
        const detail =
          (error.response?.data as any)?.detail ||
          (error.response?.data as any)?.message ||
          "Sizda ushbu amalni bajarish uchun ruxsat yo'q!"
        ElMessage.error(detail)
      }
    }
    return Promise.reject(error)
  }
)

axiosInstance.interceptors.request.use(defaultRequestInterceptors)
axiosInstance.interceptors.response.use(defaultResponseInterceptors)

const service = {
  request: (config: RequestConfig) => {
    return new Promise((resolve, reject) => {
      if (config.interceptors?.requestInterceptors) {
        config = config.interceptors.requestInterceptors(config as any)
      }

      axiosInstance
        .request(config)
        .then((res) => {
          resolve(res)
        })
        .catch((err: any) => {
          reject(err)
        })
    })
  },
  cancelRequest: (url: string | string[]) => {
    const urlList = Array.isArray(url) ? url : [url]
    for (const _url of urlList) {
      abortControllerMap.get(_url)?.abort()
      abortControllerMap.delete(_url)
    }
  },
  cancelAllRequest() {
    for (const [_, controller] of abortControllerMap) {
      controller.abort()
    }
    abortControllerMap.clear()
  }
}

export default service
