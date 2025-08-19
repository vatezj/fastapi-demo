# 游赚模块权限控制系统

## 概述

游赚模块的权限控制系统基于 `module_admin` 的 RBAC（基于角色的访问控制）体系，为后台管理接口提供细粒度的权限控制。

## 权限架构

### 1. 权限装饰器

#### CheckYozuanInterfaceAuth
- **功能**: 校验用户是否具有指定的接口权限
- **用法**: `@router.get("/api", dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:task:list'))])`
- **支持**: 单个权限、权限列表、严格模式

#### CheckYozuanRoleAuth  
- **功能**: 基于角色校验用户权限
- **用法**: `dependencies=[Depends(CheckYozuanRoleAuth('yozuan_admin'))]`
- **支持**: 单个角色、角色列表、严格模式

#### CheckYozuanFinanceAuth
- **功能**: 财务权限专用检查器
- **用法**: `dependencies=[Depends(CheckYozuanFinanceAuth())]`
- **适用**: 充值、提现、返佣等财务敏感操作

#### CheckYozuanSuperAuth
- **功能**: 超级管理员权限检查器
- **用法**: `dependencies=[Depends(CheckYozuanSuperAuth())]`
- **适用**: 系统配置、敏感数据删除等高权限操作

## 权限标识体系

### 权限格式
格式: `yozuan:模块:操作`

### 权限标识列表

#### 任务管理权限
- `yozuan:task:list` - 任务列表查看
- `yozuan:task:query` - 任务详情查询
- `yozuan:task:add` - 任务新增
- `yozuan:task:edit` - 任务编辑
- `yozuan:task:remove` - 任务删除
- `yozuan:task:export` - 任务导出

#### 订单管理权限
- `yozuan:order:list` - 订单列表查看
- `yozuan:order:query` - 订单详情查询
- `yozuan:order:edit` - 订单编辑
- `yozuan:order:review` - 订单审核
- `yozuan:order:export` - 订单导出

#### 用户管理权限
- `yozuan:user:list` - 用户列表查看
- `yozuan:user:query` - 用户详情查询
- `yozuan:user:add` - 用户新增
- `yozuan:user:edit` - 用户编辑
- `yozuan:user:remove` - 用户删除
- `yozuan:user:export` - 用户导出

#### 财务管理权限
- `yozuan:finance:list` - 财务列表查看
- `yozuan:finance:query` - 财务详情查询
- `yozuan:finance:review` - 财务审核
- `yozuan:finance:export` - 财务导出
- `yozuan:finance:*` - 财务所有权限

#### 系统管理权限
- `yozuan:system:dashboard` - 系统仪表板
- `yozuan:system:config` - 系统配置
- `yozuan:system:region` - 地区管理
- `yozuan:system:monitor` - 系统监控

#### 通配符权限
- `*:*:*` - 系统超级管理员权限
- `yozuan:*:*` - 游赚模块超级管理员权限

## 角色定义

### 系统角色
- `admin` - 系统超级管理员（拥有所有权限）

### 游赚模块角色
- `yozuan_admin` - 游赚模块管理员（拥有游赚模块所有权限）
- `yozuan_finance` - 游赚财务管理员（拥有财务相关权限）
- `yozuan_cs` - 游赚客服（拥有用户管理和订单处理权限）
- `yozuan_operator` - 游赚运营（拥有任务和用户管理权限）

## 接口权限配置

### 任务管理后台 (`/v1/admin/task`)

| 接口 | 权限要求 | 说明 |
|-----|---------|-----|
| `GET /tasks` | `yozuan:task:list` | 获取任务列表 |
| `GET /tasks/{id}` | `yozuan:task:query` | 获取任务详情 |
| `PUT /tasks/{id}/status` | `yozuan:task:edit` | 更新任务状态 |
| `DELETE /tasks/{id}` | **超级管理员** | 删除任务 |
| `GET /task-types` | `yozuan:task:list` | 获取任务类型 |
| `GET /task-statistics` | `yozuan:task:list` | 获取任务统计 |

### 订单管理后台 (`/v1/admin/order`)

| 接口 | 权限要求 | 说明 |
|-----|---------|-----|
| `GET /orders` | `yozuan:order:list` | 获取订单列表 |
| `GET /orders/{id}` | `yozuan:order:query` | 获取订单详情 |
| `PUT /orders/{id}/status` | `yozuan:order:edit` | 更新订单状态 |
| `POST /orders/{id}/review` | `yozuan:order:review` | 审核订单完成 |
| `GET /order-statistics` | `yozuan:order:list` | 获取订单统计 |

### 用户管理后台 (`/v1/admin/user`)

| 接口 | 权限要求 | 说明 |
|-----|---------|-----|
| `GET /users` | `yozuan:user:list` | 获取用户列表 |
| `GET /users/{id}` | `yozuan:user:query` | 获取用户详情 |
| `PUT /users/{id}/status` | `yozuan:user:edit` | 更新用户状态 |
| `GET /user-statistics` | `yozuan:user:list` | 获取用户统计 |
| `GET /invitation-statistics` | `yozuan:user:list` | 获取邀请统计 |

### 财务管理后台 (`/v1/admin/finance`)

| 接口 | 权限要求 | 说明 |
|-----|---------|-----|
| `GET /transactions` | **财务权限** | 获取交易记录 |
| `GET /withdraw-applications` | **财务权限** | 获取提现申请 |
| `POST /withdraw-applications/{id}/review` | **财务权限** | 审核提现申请 |
| `GET /finance-statistics` | **财务权限** | 获取财务统计 |
| `GET /rebate-config` | **财务权限** | 获取返佣配置 |
| `PUT /rebate-config/{id}` | **超级管理员** | 更新返佣配置 |

### 系统管理后台 (`/v1/admin/system`)

| 接口 | 权限要求 | 说明 |
|-----|---------|-----|
| `GET /dashboard` | `yozuan:system:dashboard` | 获取系统仪表板 |
| `GET /regions` | `yozuan:system:region` | 获取地区列表 |
| `POST /regions` | **超级管理员** | 创建地区 |
| `PUT /regions/{code}` | **超级管理员** | 更新地区 |
| `DELETE /regions/{code}` | **超级管理员** | 删除地区 |
| `GET /system-config` | `yozuan:system:config` | 获取系统配置 |

## 权限检查流程

### 1. 认证流程
```
1. 客户端发送请求 -> 2. JWT Token 验证 -> 3. 获取用户信息 -> 4. 权限检查 -> 5. 接口访问
```

### 2. 权限验证逻辑
```python
def check_permission(user, required_perm):
    # 1. 超级管理员检查
    if '*:*:*' in user.permissions:
        return True
    
    # 2. 游赚模块超级管理员检查
    if 'yozuan:*:*' in user.permissions:
        return True
    
    # 3. 具体权限检查
    if required_perm in user.permissions:
        return True
    
    # 4. 权限不足
    raise PermissionException("权限不足")
```

### 3. 角色权限检查
```python
def check_role(user, required_role):
    user_roles = [role.role_key for role in user.roles]
    
    # 1. 系统管理员检查
    if 'admin' in user_roles:
        return True
    
    # 2. 具体角色检查
    if required_role in user_roles:
        return True
    
    # 3. 角色权限不足
    raise PermissionException("角色权限不足")
```

## 使用示例

### 1. 接口权限控制
```python
@router.get("/tasks", 
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:task:list'))])
async def get_tasks():
    # 接口实现
    pass
```

### 2. 角色权限控制
```python
@router.delete("/tasks/{task_id}", 
           dependencies=[Depends(CheckYozuanRoleAuth('yozuan_admin'))])
async def delete_task():
    # 接口实现
    pass
```

### 3. 财务权限控制
```python
@router.post("/withdraw/review", 
           dependencies=[Depends(CheckYozuanFinanceAuth())])
async def review_withdraw():
    # 接口实现
    pass
```

### 4. 超级管理员权限
```python
@router.put("/system/config", 
           dependencies=[Depends(CheckYozuanSuperAuth())])
async def update_config():
    # 接口实现
    pass
```

## 错误处理

### 权限异常
```python
# 权限不足时抛出异常
raise PermissionException(
    data='', 
    message='该用户无游赚模块接口权限: yozuan:task:list'
)
```

### 异常处理
- 权限不足返回 HTTP 403 Forbidden
- 未认证返回 HTTP 401 Unauthorized
- 统一错误格式返回

## 权限配置建议

### 1. 角色配置建议
```
游赚管理员 (yozuan_admin):
- yozuan:*:*

游赚财务 (yozuan_finance):
- yozuan:finance:*
- yozuan:order:list
- yozuan:order:query
- yozuan:user:list
- yozuan:user:query

游赚客服 (yozuan_cs):
- yozuan:user:list
- yozuan:user:query
- yozuan:user:edit
- yozuan:order:list
- yozuan:order:query
- yozuan:order:edit

游赚运营 (yozuan_operator):
- yozuan:task:list
- yozuan:task:query
- yozuan:task:edit
- yozuan:user:list
- yozuan:user:query
- yozuan:order:list
- yozuan:order:query
```

### 2. 最小权限原则
- 用户只分配必要的权限
- 避免过度授权
- 定期审查权限分配

### 3. 权限分离
- 财务权限独立管理
- 系统配置权限严格控制
- 敏感操作需要超级管理员权限

## 总结

游赚模块权限控制系统提供了：

- ✅ **完整的权限体系**: 基于 RBAC 的细粒度权限控制
- ✅ **灵活的权限配置**: 支持权限标识和角色双重控制
- ✅ **专业的财务权限**: 独立的财务权限管理
- ✅ **安全的系统权限**: 严格的超级管理员权限控制
- ✅ **统一的认证体系**: 复用 module_admin 的认证服务
- ✅ **清晰的权限文档**: 完整的权限标识和使用说明

这套权限系统确保了游赚平台后台管理的安全性和可管理性，为不同角色的管理员提供了合适的权限配置。
