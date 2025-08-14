# APP模块 - 模块化架构设计

## 📱 模块概述

APP模块是一个独立的FastAPI应用，专门为移动端APP提供服务。该模块采用了模块化设计，既可以为移动端用户提供服务，也可以为后台管理系统提供管理接口。

## 🏗️ 架构设计

### 模块结构
```
module_app/
├── app.py                          # 主应用入口
├── controller/                     # 控制器层
│   ├── auth_controller.py         # 认证控制器（移动端）
│   ├── user_controller.py         # 用户控制器（移动端）
│   ├── app_user_controller.py     # APP用户控制器（移动端）
│   └── admin_interface_controller.py  # 后台管理接口控制器
├── service/                        # 服务层
├── dao/                           # 数据访问层
└── entity/                        # 实体层
```

### 接口分类

#### 1. 移动端接口 (`/app/v1/*`)
- **认证接口**: `/app/v1/auth/*` - 登录、注册、短信验证等
- **用户接口**: `/app/v1/user/*` - 用户信息、个人资料等
- **APP用户接口**: `/app/v1/user/*` - 用户管理、状态修改等

#### 2. 后台管理接口 (`/app/v1/admin/*`)
- **用户管理**: `/app/v1/admin/user/*` - 用户CRUD、状态管理、密码重置等
- **登录日志**: `/app/v1/admin/login-log/*` - 登录日志查询、清空等
- **统计信息**: `/app/v1/admin/stats/*` - 用户统计、概览信息等

## 🔌 接口详情

### 移动端接口

#### 认证接口
- `POST /app/v1/auth/login` - 用户登录
- `POST /app/v1/auth/register` - 用户注册
- `POST /app/v1/auth/send-sms` - 发送短信验证码

#### 用户接口
- `GET /app/v1/user/profile` - 获取用户资料
- `PUT /app/v1/user/profile` - 更新用户资料
- `PUT /app/v1/user/password` - 修改密码

#### APP用户接口
- `GET /app/v1/user/list` - 获取用户列表（分页）
- `GET /app/v1/user/{user_id}` - 获取用户详情
- `POST /app/v1/user/add` - 新增用户
- `PUT /app/v1/user/edit` - 编辑用户
- `DELETE /app/v1/user/delete` - 删除用户
- `PUT /app/v1/user/status` - 修改用户状态
- `PUT /app/v1/user/reset-password` - 重置密码

### 后台管理接口

#### 用户管理
- `GET /app/v1/admin/user/list` - 获取用户列表（分页）
- `GET /app/v1/admin/user/{user_id}` - 获取用户详情
- `POST /app/v1/admin/user/add` - 新增用户
- `PUT /app/v1/admin/user/edit` - 编辑用户
- `DELETE /app/v1/admin/user/delete` - 删除用户
- `PUT /app/v1/admin/user/status` - 修改用户状态
- `PUT /app/v1/admin/user/reset-password` - 重置密码

#### 登录日志管理
- `GET /app/v1/admin/login-log/list` - 获取登录日志列表（分页）
- `DELETE /app/v1/admin/login-log/clear` - 清空登录日志

#### 统计信息
- `GET /app/v1/admin/stats/overview` - 获取统计概览

## 🔐 权限控制

### 移动端接口
- 无需特殊权限，面向普通用户
- 部分接口需要用户登录状态

### 后台管理接口
- 需要后台管理系统权限
- 建议集成到现有的权限系统中
- 可以通过中间件进行权限验证

## 📊 数据模型

#### 模块内部实体
- `AppUser` - APP用户实体
- `AppUserProfile` - 用户资料实体
- `AppLoginLog` - 登录日志实体

#### 数据传输对象
- `AppAddUserModel` - 新增用户模型
- `AppEditUserModel` - 编辑用户模型
- `AppUserPageQueryModel` - 用户分页查询模型
- `AppLoginLogPageQueryModel` - 登录日志分页查询模型

## 🚀 使用方式

### 1. 移动端调用
```javascript
// 用户登录
const response = await fetch('/app/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_name: 'testuser',
        password: 'password123'
    })
});
```

### 2. 后台管理调用
```javascript
// 获取用户列表
const response = await fetch('/app/v1/admin/user/list?page_num=1&page_size=10', {
    method: 'GET',
    headers: { 'Authorization': 'Bearer your-token' }
});
```

## 🔧 配置说明

### 环境变量
- `APP_NAME` - 应用名称
- `APP_VERSION` - 应用版本
- `APP_ROOT_PATH` - 应用根路径

### 数据库配置
- 使用共享的数据库连接
- 支持MySQL和PostgreSQL

### Redis配置
- 使用共享的Redis连接
- 支持缓存和会话管理

## 📝 开发规范

### 1. 接口命名
- 移动端接口使用简洁的RESTful风格
- 后台管理接口添加`/admin`前缀
- 使用统一的响应格式

### 2. 错误处理
- 统一的异常处理机制
- 详细的错误日志记录
- 友好的错误信息返回

### 3. 日志记录
- 操作日志记录
- 错误日志记录
- 性能监控日志

## 🔄 扩展性

### 1. 新增功能模块
- 在`controller`目录下添加新的控制器
- 在`service`目录下添加对应的服务
- 在`app.py`中注册新的路由

### 2. 权限扩展
- 可以集成现有的权限系统
- 支持角色和权限的细粒度控制
- 支持数据权限控制

### 3. 监控扩展
- 支持性能监控
- 支持业务指标监控
- 支持告警机制

## 📚 相关文档

- [API接口文档](./docs/api.md)
- [数据库设计文档](./docs/database.md)
- [部署指南](./docs/deployment.md)
- [测试指南](./docs/testing.md)
