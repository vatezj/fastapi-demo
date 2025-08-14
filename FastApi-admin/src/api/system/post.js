import request from '@/utils/request'
const prefix = '/admin'
// 查询岗位列表
export function listPost(query) {
  return request({
    url: prefix + '/system/post/list',
    method: 'get',
    params: query
  })
}

// 查询岗位详细
export function getPost(postId) {
  return request({
    url: prefix + '/system/post/' + postId,
    method: 'get'
  })
}

// 新增岗位
export function addPost(data) {
  return request({
    url: prefix + '/system/post',
    method: 'post',
    data: data
  })
}

// 修改岗位
export function updatePost(data) {
  return request({
    url: prefix + '/system/post',
    method: 'put',
    data: data
  })
}

// 删除岗位
export function delPost(postId) {
  return request({
    url: prefix + '/system/post/' + postId,
    method: 'delete'
  })
}
