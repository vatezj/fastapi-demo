import request from '@/utils/request'
const prefix = '/admin'
// 获取服务信息
export function getServer() {
  return request({
    url:  prefix + '/monitor/server',
    method: 'get'
  })
}