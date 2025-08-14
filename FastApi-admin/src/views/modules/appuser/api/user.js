import request from '@/utils/request'
const prefix = '/app/v1/admin'
// 查询APP用户信息列表
export function listUser(query) {
  return request({
    url: prefix + '/user/list',
    method: 'get',
    params: query
  })
}

// 查询APP用户信息详细
export function getUser(userId) {
  return request({
    url: prefix + '/user/' + userId,
    method: 'get'
  })
}

// 新增APP用户信息
export function addUser(data) {
  return request({
    url: prefix + '/user',
    method: 'post',
    data: data
  })
}

// 修改APP用户信息
export function updateUser(data) {
  return request({
    url: prefix + '/user',
    method: 'put',
    data: data
  })
}

// 删除APP用户信息
export function delUser(userId) {
  return request({
    url: prefix + '/user/' + userId,
    method: 'delete'
  })
}
