import request from '@/axios'

export const getAIConfigApi = (username?: string) => {
  return request.get({ url: '/ai/config', params: { username } })
}

export const executeAIActionApi = (data: { action: string; params: any; username?: string }) => {
  return request.post({ url: '/ai/execute', data })
}
