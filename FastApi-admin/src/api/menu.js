import request from '@/utils/request'
const prefix = '/admin'
// 获取路由
export const getRouters = () => {
  return request({
    url: prefix + '/getRouters',
    method: 'get'
  })
}