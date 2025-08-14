# 权限系统开发指南

## 概述

本文档描述了 RuoYi-FastAPI 项目的权限系统设计和实现，包括认证、授权、权限控制等核心功能。

## 权限系统架构

### 1. 整体架构图

```
┌─────────────────────────────────────┐
│           前端应用 (Vue3)            │
├─────────────────────────────────────┤
│            API 网关层               │
├─────────────────────────────────────┤
│           认证中间件                │
│         (JWT Token 验证)            │
├─────────────────────────────────────┤
│           权限验证层                │
│      (接口权限 + 数据权限)           │
├─────────────────────────────────────┤
│           业务逻辑层                │
│         (Service + DAO)             │
├─────────────────────────────────────┤
│           数据存储层                │
│      (MySQL + Redis)                │
└─────────────────────────────────────┘
```

### 2. 权限模型设计

#### RBAC (基于角色的访问控制)
```
用户 (User) ←→ 角色 (Role) ←→ 权限 (Permission)
    ↓              ↓              ↓
  用户表      用户角色关联表     角色权限关联表
 sys_user    sys_user_role    sys_role_permission
```

#### 权限层次结构
```
系统权限
├── 用户管理
│   ├── 用户查看 (system:user:list)
│   ├── 用户新增 (system:user:add)
│   ├── 用户修改 (system:user:edit)
│   └── 用户删除 (system:user:remove)
├── 角色管理
│   ├── 角色查看 (system:role:list)
│   ├── 角色新增 (system:role:add)
│   ├── 角色修改 (system:role:edit)
│   └── 角色删除 (system:role:remove)
└── 菜单管理
    ├── 菜单查看 (system:menu:list)
    ├── 菜单新增 (system:menu:add)
    ├── 菜单修改 (system:menu:edit)
    └── 菜单删除 (system:menu:remove)
```

## 认证系统

### 1. JWT 认证实现

#### JWT 工具类
```python
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config.env import JwtSettings

class JWTUtil:
    """JWT工具类"""
    
    def __init__(self):
        self.secret_key = JwtSettings.jwt_secret_key
        self.algorithm = JwtSettings.jwt_algorithm
        self.expire_minutes = JwtSettings.jwt_expire_minutes
    
    def create_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建JWT令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """解码JWT令牌（不验证签名）"""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except jwt.PyJWTError:
            return None

jwt_util = JWTUtil()
```

#### 用户认证服务
```python
from passlib.context import CryptContext
from datetime import timedelta
from typing import Optional
from module_admin.entity.do.user_do import UserDO
from module_admin.dao.user_dao import UserDAO
from utils.jwt_util import jwt_util
from config.env import JwtSettings

class AuthService:
    """认证服务"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_dao = UserDAO()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return self.pwd_context.hash(password)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserDO]:
        """用户认证"""
        user = await self.user_dao.get_by_username(username)
        if not user:
            return None
        
        if not self.verify_password(password, user.password):
            return None
        
        if user.status != '0':  # 用户状态检查
            return None
        
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JwtSettings.jwt_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JwtSettings.jwt_secret_key, algorithm=JwtSettings.jwt_algorithm)
        
        return encoded_jwt
    
    async def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """用户登录"""
        user = await self.authenticate_user(username, password)
        if not user:
            return None
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=JwtSettings.jwt_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        # 获取用户权限
        permissions = await self.get_user_permissions(user.id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": JwtSettings.jwt_expire_minutes * 60,
            "user_info": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "permissions": permissions
            }
        }
```

### 2. 认证中间件

#### JWT 认证中间件
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from module_admin.entity.do.user_do import UserDO
from module_admin.dao.user_dao import UserDAO
from utils.jwt_util import jwt_util

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserDO:
    """获取当前用户"""
    token = credentials.credentials
    
    # 验证令牌
    payload = jwt_util.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌中缺少用户ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户信息
    user = await UserDAO().get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != '0':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_active_user(current_user: UserDO = Depends(get_current_user)) -> UserDO:
    """获取当前活跃用户"""
    if current_user.status != '0':
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user
```

## 权限验证系统

### 1. 接口权限验证

#### 权限验证装饰器
```python
from functools import wraps
from typing import List, Optional
from fastapi import HTTPException, Depends
from module_admin.entity.do.user_do import UserDO
from module_admin.dao.user_dao import UserDAO
from module_admin.dao.role_dao import RoleDAO

def require_permissions(permissions: List[str]):
    """权限验证装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: UserDO = Depends(get_current_user), **kwargs):
            # 获取用户权限
            user_permissions = await get_user_permissions(current_user.id)
            
            # 验证权限
            for permission in permissions:
                if permission not in user_permissions:
                    raise HTTPException(
                        status_code=403,
                        detail=f"缺少权限: {permission}"
                    )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

async def get_user_permissions(user_id: int) -> List[str]:
    """获取用户权限列表"""
    # 获取用户角色
    user_roles = await RoleDAO().get_roles_by_user_id(user_id)
    
    # 获取角色权限
    permissions = set()
    for role in user_roles:
        role_permissions = await get_role_permissions(role.id)
        permissions.update(role_permissions)
    
    return list(permissions)

async def get_role_permissions(role_id: int) -> List[str]:
    """获取角色权限列表"""
    # 从缓存获取角色权限
    cache_key = f"role_permissions:{role_id}"
    cached_permissions = await redis_client.get(cache_key)
    
    if cached_permissions:
        return json.loads(cached_permissions)
    
    # 从数据库获取角色权限
    role_menus = await RoleDAO().get_role_menus(role_id)
    permissions = [menu.perms for menu in role_menus if menu.perms]
    
    # 缓存角色权限
    await redis_client.setex(cache_key, 3600, json.dumps(permissions))
    
    return permissions
```

#### 使用示例
```python
from fastapi import APIRouter, Depends
from module_admin.aspect.interface_auth import require_permissions

router = APIRouter(prefix="/user", tags=["用户管理"])

@router.get("/list")
@require_permissions(["system:user:list"])
async def get_user_list(current_user: UserDO = Depends(get_current_user)):
    """获取用户列表（需要用户查看权限）"""
    pass

@router.post("/")
@require_permissions(["system:user:add"])
async def create_user(user_data: UserCreateVO, current_user: UserDO = Depends(get_current_user)):
    """创建用户（需要用户新增权限）"""
    pass

@router.put("/{user_id}")
@require_permissions(["system:user:edit"])
async def update_user(user_id: int, user_data: UserUpdateVO, current_user: UserDO = Depends(get_current_user)):
    """更新用户（需要用户修改权限）"""
    pass

@router.delete("/{user_id}")
@require_permissions(["system:user:remove"])
async def delete_user(user_id: int, current_user: UserDO = Depends(get_current_user)):
    """删除用户（需要用户删除权限）"""
    pass
```

### 2. 数据权限控制

#### 数据权限装饰器
```python
from typing import Optional, List
from fastapi import Depends, Query

def require_data_scope(scope_type: str):
    """数据权限装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: UserDO = Depends(get_current_user), **kwargs):
            # 获取用户数据权限范围
            data_scope = await get_user_data_scope(current_user.id, scope_type)
            
            # 注入数据权限条件
            kwargs['data_scope'] = data_scope
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

async def get_user_data_scope(user_id: int, scope_type: str) -> Dict[str, Any]:
    """获取用户数据权限范围"""
    # 获取用户角色
    user_roles = await RoleDAO().get_roles_by_user_id(user_id)
    
    # 获取最大数据权限范围
    max_scope = 1  # 1:全部数据权限 2:自定义数据权限 3:本部门数据权限 4:本部门及以下数据权限 5:仅本人数据权限
    
    for role in user_roles:
        if role.data_scope < max_scope:
            max_scope = role.data_scope
    
    # 根据数据权限范围返回相应的查询条件
    if max_scope == 1:  # 全部数据权限
        return {"scope": "all"}
    elif max_scope == 2:  # 自定义数据权限
        dept_ids = await get_user_custom_dept_ids(user_id)
        return {"scope": "custom", "dept_ids": dept_ids}
    elif max_scope == 3:  # 本部门数据权限
        user_dept_id = await get_user_dept_id(user_id)
        return {"scope": "dept", "dept_id": user_dept_id}
    elif max_scope == 4:  # 本部门及以下数据权限
        user_dept_id = await get_user_dept_id(user_id)
        dept_ids = await get_dept_and_children_ids(user_dept_id)
        return {"scope": "dept_and_children", "dept_ids": dept_ids}
    elif max_scope == 5:  # 仅本人数据权限
        return {"scope": "self", "user_id": user_id}
    else:
        return {"scope": "self", "user_id": user_id}

async def get_user_custom_dept_ids(user_id: int) -> List[int]:
    """获取用户自定义部门ID列表"""
    # 从用户角色部门关联表获取
    user_role_depts = await UserRoleDeptDAO().get_by_user_id(user_id)
    return [urd.dept_id for urd in user_role_depts]

async def get_dept_and_children_ids(dept_id: int) -> List[int]:
    """获取部门及其子部门ID列表"""
    dept_ids = [dept_id]
    
    # 递归获取子部门
    children = await DeptDAO().get_dept_children(dept_id)
    for child in children:
        child_ids = await get_dept_and_children_ids(child.id)
        dept_ids.extend(child_ids)
    
    return dept_ids
```

#### 使用示例
```python
@router.get("/list")
@require_permissions(["system:user:list"])
@require_data_scope("dept")
async def get_user_list(
    current_user: UserDO = Depends(get_current_user),
    data_scope: dict = Depends()
):
    """获取用户列表（带数据权限控制）"""
    # 根据数据权限范围构建查询条件
    query_conditions = {}
    
    if data_scope["scope"] == "all":
        # 全部数据权限，不添加额外条件
        pass
    elif data_scope["scope"] == "custom":
        # 自定义数据权限
        query_conditions["dept_id"] = data_scope["dept_ids"]
    elif data_scope["scope"] == "dept":
        # 本部门数据权限
        query_conditions["dept_id"] = data_scope["dept_id"]
    elif data_scope["scope"] == "dept_and_children":
        # 本部门及以下数据权限
        query_conditions["dept_id"] = data_scope["dept_ids"]
    elif data_scope["scope"] == "self":
        # 仅本人数据权限
        query_conditions["id"] = data_scope["user_id"]
    
    # 执行查询
    users = await user_service.get_user_list(**query_conditions)
    return users
```

## 菜单权限管理

### 1. 菜单权限模型

#### 菜单实体设计
```python
from sqlalchemy import Column, Integer, String, Boolean, Text
from module_admin.entity.do.base_do import BaseDO

class MenuDO(BaseDO):
    """菜单数据对象"""
    __tablename__ = "sys_menu"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="菜单ID")
    menu_name = Column(String(50), nullable=False, comment="菜单名称")
    parent_id = Column(Integer, default=0, comment="父菜单ID")
    order_num = Column(Integer, default=0, comment="显示顺序")
    path = Column(String(200), comment="路由地址")
    component = Column(String(255), comment="组件路径")
    is_frame = Column(Boolean, default=True, comment="是否为外链")
    menu_type = Column(String(1), comment="菜单类型（M目录 C菜单 F按钮）")
    visible = Column(Boolean, default=True, comment="菜单状态")
    perms = Column(String(100), comment="权限标识")
    icon = Column(String(100), comment="菜单图标")
    remark = Column(Text, comment="备注")
```

#### 菜单权限验证
```python
async def get_user_menus(user_id: int) -> List[Dict[str, Any]]:
    """获取用户菜单列表"""
    # 获取用户角色
    user_roles = await RoleDAO().get_roles_by_user_id(user_id)
    
    # 获取角色菜单
    role_menus = set()
    for role in user_roles:
        menus = await get_role_menus(role.id)
        role_menus.update(menus)
    
    # 构建菜单树
    menu_tree = build_menu_tree(list(role_menus))
    
    return menu_tree

async def get_role_menus(role_id: int) -> List[MenuDO]:
    """获取角色菜单列表"""
    # 从缓存获取角色菜单
    cache_key = f"role_menus:{role_id}"
    cached_menus = await redis_client.get(cache_key)
    
    if cached_menus:
        return json.loads(cached_menus)
    
    # 从数据库获取角色菜单
    role_menus = await RoleDAO().get_role_menus(role_id)
    
    # 缓存角色菜单
    await redis_client.setex(cache_key, 3600, json.dumps([menu.to_dict() for menu in role_menus]))
    
    return role_menus

def build_menu_tree(menus: List[MenuDO]) -> List[Dict[str, Any]]:
    """构建菜单树"""
    menu_dict = {menu.id: menu.to_dict() for menu in menus}
    menu_tree = []
    
    for menu in menus:
        menu_data = menu.to_dict()
        
        if menu.parent_id == 0:
            # 根菜单
            menu_tree.append(menu_data)
        else:
            # 子菜单
            parent = menu_dict.get(menu.parent_id)
            if parent:
                if 'children' not in parent:
                    parent['children'] = []
                parent['children'].append(menu_data)
    
    # 按显示顺序排序
    def sort_menus(menu_list):
        menu_list.sort(key=lambda x: x.get('order_num', 0))
        for menu in menu_list:
            if 'children' in menu:
                sort_menus(menu['children'])
    
    sort_menus(menu_tree)
    return menu_tree
```

### 2. 前端权限控制

#### 路由权限控制
```javascript
// 路由守卫
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (!token && to.path !== '/login') {
    // 未登录，跳转到登录页
    next('/login')
    return
  }
  
  if (token && to.path === '/login') {
    // 已登录，跳转到首页
    next('/')
    return
  }
  
  if (token && to.path !== '/login') {
    // 已登录，检查权限
    const hasPermission = await checkRoutePermission(to)
    if (hasPermission) {
      next()
    } else {
      next('/403')
    }
  }
})

// 检查路由权限
async function checkRoutePermission(route) {
  const userMenus = JSON.parse(localStorage.getItem('userMenus') || '[]')
  const routePath = route.path
  
  // 检查路由是否在用户菜单中
  return checkMenuPermission(userMenus, routePath)
}

// 检查菜单权限
function checkMenuPermission(menus, path) {
  for (const menu of menus) {
    if (menu.path === path) {
      return true
    }
    if (menu.children && menu.children.length > 0) {
      if (checkMenuPermission(menu.children, path)) {
        return true
      }
    }
  }
  return false
}
```

#### 按钮权限控制
```javascript
// 按钮权限指令
Vue.directive('permission', {
  inserted(el, binding) {
    const { value } = binding
    const permissions = JSON.parse(localStorage.getItem('permissions') || '[]')
    
    if (value && !permissions.includes(value)) {
      el.parentNode && el.parentNode.removeChild(el)
    }
  }
})

// 使用示例
<template>
  <div>
    <!-- 需要用户新增权限 -->
    <el-button v-permission="'system:user:add'">新增用户</el-button>
    
    <!-- 需要用户修改权限 -->
    <el-button v-permission="'system:user:edit'">修改用户</el-button>
    
    <!-- 需要用户删除权限 -->
    <el-button v-permission="'system:user:remove'">删除用户</el-button>
  </div>
</template>
```

## 权限缓存管理

### 1. Redis 缓存策略

#### 权限缓存管理
```python
class PermissionCache:
    """权限缓存管理"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_prefix = "permission:"
        self.default_expire = 3600  # 默认过期时间1小时
    
    async def get_user_permissions(self, user_id: int) -> List[str]:
        """获取用户权限（带缓存）"""
        cache_key = f"{self.cache_prefix}user:{user_id}"
        
        # 尝试从缓存获取
        cached_permissions = await self.redis.get(cache_key)
        if cached_permissions:
            return json.loads(cached_permissions)
        
        # 从数据库获取
        permissions = await self._get_user_permissions_from_db(user_id)
        
        # 存入缓存
        await self.redis.setex(cache_key, self.default_expire, json.dumps(permissions))
        
        return permissions
    
    async def get_role_permissions(self, role_id: int) -> List[str]:
        """获取角色权限（带缓存）"""
        cache_key = f"{self.cache_prefix}role:{role_id}"
        
        # 尝试从缓存获取
        cached_permissions = await self.redis.get(cache_key)
        if cached_permissions:
            return json.loads(cached_permissions)
        
        # 从数据库获取
        permissions = await self._get_role_permissions_from_db(role_id)
        
        # 存入缓存
        await self.redis.setex(cache_key, self.default_expire, json.dumps(permissions))
        
        return permissions
    
    async def get_user_menus(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户菜单（带缓存）"""
        cache_key = f"{self.cache_prefix}menu:{user_id}"
        
        # 尝试从缓存获取
        cached_menus = await self.redis.get(cache_key)
        if cached_menus:
            return json.loads(cached_menus)
        
        # 从数据库获取
        menus = await self._get_user_menus_from_db(user_id)
        
        # 存入缓存
        await self.redis.setex(cache_key, self.default_expire, json.dumps(menus))
        
        return menus
    
    async def clear_user_cache(self, user_id: int):
        """清除用户相关缓存"""
        cache_keys = [
            f"{self.cache_prefix}user:{user_id}",
            f"{self.cache_prefix}menu:{user_id}"
        ]
        
        for key in cache_keys:
            await self.redis.delete(key)
    
    async def clear_role_cache(self, role_id: int):
        """清除角色相关缓存"""
        cache_keys = [
            f"{self.cache_prefix}role:{role_id}"
        ]
        
        # 清除所有用户的菜单缓存（因为角色变更会影响用户菜单）
        user_keys = await self.redis.keys(f"{self.cache_prefix}menu:*")
        if user_keys:
            await self.redis.delete(*user_keys)
        
        for key in cache_keys:
            await self.redis.delete(key)
    
    async def clear_all_cache(self):
        """清除所有权限缓存"""
        cache_keys = await self.redis.keys(f"{self.cache_prefix}*")
        if cache_keys:
            await self.redis.delete(*cache_keys)
```

### 2. 缓存更新策略

#### 权限变更缓存更新
```python
class PermissionUpdateService:
    """权限更新服务"""
    
    def __init__(self):
        self.permission_cache = PermissionCache(redis_client)
    
    async def update_user_permissions(self, user_id: int):
        """更新用户权限缓存"""
        await self.permission_cache.clear_user_cache(user_id)
        logger.info(f"已更新用户 {user_id} 的权限缓存")
    
    async def update_role_permissions(self, role_id: int):
        """更新角色权限缓存"""
        await self.permission_cache.clear_role_cache(role_id)
        logger.info(f"已更新角色 {role_id} 的权限缓存")
    
    async def update_menu_permissions(self, menu_id: int):
        """更新菜单权限缓存"""
        # 清除所有用户的菜单缓存
        await self.permission_cache.clear_all_cache()
        logger.info(f"已更新菜单 {menu_id} 的权限缓存")
    
    async def batch_update_permissions(self, user_ids: List[int] = None, role_ids: List[int] = None):
        """批量更新权限缓存"""
        if user_ids:
            for user_id in user_ids:
                await self.update_user_permissions(user_id)
        
        if role_ids:
            for role_id in role_ids:
                await self.update_role_permissions(role_id)
        
        logger.info("批量权限缓存更新完成")
```

## 权限审计日志

### 1. 操作日志记录

#### 权限操作日志
```python
from module_admin.entity.do.log_do import OperLogDO
from module_admin.dao.log_dao import OperLogDAO

class PermissionAuditService:
    """权限审计服务"""
    
    def __init__(self):
        self.oper_log_dao = OperLogDAO()
    
    async def log_permission_operation(
        self,
        user_id: int,
        username: str,
        operation: str,
        target: str,
        target_id: int,
        details: str,
        ip_address: str,
        user_agent: str
    ):
        """记录权限操作日志"""
        oper_log = OperLogDO(
            title=f"权限{operation}",
            business_type=1,  # 权限管理
            method=f"permission.{operation}",
            request_method="POST",
            operator_type=1,  # 后台用户
            oper_name=username,
            oper_url=f"/permission/{operation}",
            oper_ip=ip_address,
            oper_location="",
            oper_param=json.dumps({
                "target": target,
                "target_id": target_id,
                "details": details
            }),
            json_result="",
            status=0,  # 成功
            error_msg="",
            oper_time=datetime.now(),
            cost_time=0,
            user_agent=user_agent
        )
        
        await self.oper_log_dao.create(oper_log)
    
    async def log_login_attempt(
        self,
        username: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        error_msg: str = ""
    ):
        """记录登录尝试日志"""
        oper_log = OperLogDO(
            title="用户登录",
            business_type=0,  # 登录
            method="auth.login",
            request_method="POST",
            operator_type=1,  # 后台用户
            oper_name=username,
            oper_url="/auth/login",
            oper_ip=ip_address,
            oper_location="",
            oper_param=json.dumps({"username": username}),
            json_result="",
            status=0 if success else 1,  # 0成功 1失败
            error_msg=error_msg,
            oper_time=datetime.now(),
            cost_time=0,
            user_agent=user_agent
        )
        
        await self.oper_log_dao.create(oper_log)
```

### 2. 权限变更通知

#### 权限变更事件
```python
from typing import List
from datetime import datetime

class PermissionChangeEvent:
    """权限变更事件"""
    
    def __init__(self, event_type: str, user_ids: List[int], details: str):
        self.event_type = event_type
        self.user_ids = user_ids
        self.details = details
        self.timestamp = datetime.now()

class PermissionNotificationService:
    """权限变更通知服务"""
    
    def __init__(self):
        self.redis_client = redis_client
    
    async def notify_permission_change(self, event: PermissionChangeEvent):
        """通知权限变更"""
        # 发送WebSocket通知
        await self.send_websocket_notification(event)
        
        # 发送邮件通知（可选）
        await self.send_email_notification(event)
        
        # 记录通知日志
        await self.log_notification(event)
    
    async def send_websocket_notification(self, event: PermissionChangeEvent):
        """发送WebSocket通知"""
        notification_data = {
            "type": "permission_change",
            "event_type": event.event_type,
            "details": event.details,
            "timestamp": event.timestamp.isoformat()
        }
        
        # 向相关用户发送通知
        for user_id in event.user_ids:
            channel = f"user:{user_id}"
            await self.redis_client.publish(channel, json.dumps(notification_data))
    
    async def send_email_notification(self, event: PermissionChangeEvent):
        """发送邮件通知"""
        # 获取用户邮箱
        user_emails = await self.get_user_emails(event.user_ids)
        
        # 发送邮件
        for email in user_emails:
            await self.send_email(
                to_email=email,
                subject="权限变更通知",
                content=f"您的权限已发生变更：{event.details}"
            )
    
    async def log_notification(self, event: PermissionChangeEvent):
        """记录通知日志"""
        log_data = {
            "event_type": event.event_type,
            "user_ids": event.user_ids,
            "details": event.details,
            "timestamp": event.timestamp.isoformat()
        }
        
        await self.redis_client.lpush("permission_notifications", json.dumps(log_data))
        await self.redis_client.ltrim("permission_notifications", 0, 999)  # 保留最近1000条
```

## 安全防护

### 1. 密码安全

#### 密码策略
```python
import re
from typing import Tuple

class PasswordPolicy:
    """密码策略"""
    
    def __init__(self):
        self.min_length = 8
        self.max_length = 20
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special_chars = True
        self.forbidden_patterns = [
            r"123456",
            r"password",
            r"admin",
            r"qwerty"
        ]
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """验证密码强度"""
        # 长度检查
        if len(password) < self.min_length:
            return False, f"密码长度不能少于{self.min_length}位"
        
        if len(password) > self.max_length:
            return False, f"密码长度不能超过{self.max_length}位"
        
        # 复杂度检查
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            return False, "密码必须包含大写字母"
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            return False, "密码必须包含小写字母"
        
        if self.require_digits and not re.search(r'\d', password):
            return False, "密码必须包含数字"
        
        if self.require_special_chars and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "密码必须包含特殊字符"
        
        # 禁止模式检查
        for pattern in self.forbidden_patterns:
            if re.search(pattern, password, re.IGNORECASE):
                return False, f"密码不能包含常见弱密码模式"
        
        return True, "密码强度符合要求"
    
    def get_password_strength(self, password: str) -> int:
        """获取密码强度等级（1-5）"""
        score = 0
        
        # 长度得分
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        
        # 复杂度得分
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        
        return min(score, 5)

password_policy = PasswordPolicy()
```

### 2. 登录安全

#### 登录限制
```python
class LoginSecurityService:
    """登录安全服务"""
    
    def __init__(self):
        self.redis_client = redis_client
        self.max_failed_attempts = 5
        self.lockout_duration = 1800  # 30分钟
        self.max_attempts_window = 3600  # 1小时
    
    async def check_login_attempts(self, username: str, ip_address: str) -> Tuple[bool, str]:
        """检查登录尝试次数"""
        # 检查IP锁定
        ip_lock_key = f"login:ip_lock:{ip_address}"
        if await self.redis_client.exists(ip_lock_key):
            return False, "IP地址已被锁定，请稍后再试"
        
        # 检查用户名锁定
        user_lock_key = f"login:user_lock:{username}"
        if await self.redis_client.exists(user_lock_key):
            return False, "账户已被锁定，请稍后再试"
        
        # 检查失败次数
        failed_key = f"login:failed:{username}:{ip_address}"
        failed_count = await self.redis_client.get(failed_key)
        
        if failed_count and int(failed_count) >= self.max_failed_attempts:
            # 锁定账户
            await self.redis_client.setex(user_lock_key, self.lockout_duration, "locked")
            return False, "登录失败次数过多，账户已被锁定"
        
        return True, "可以登录"
    
    async def record_login_attempt(self, username: str, ip_address: str, success: bool):
        """记录登录尝试"""
        if success:
            # 登录成功，清除失败记录
            failed_key = f"login:failed:{username}:{ip_address}"
            await self.redis_client.delete(failed_key)
        else:
            # 登录失败，增加失败计数
            failed_key = f"login:failed:{username}:{ip_address}"
            failed_count = await self.redis_client.incr(failed_key)
            await self.redis_client.expire(failed_key, self.max_attempts_window)
            
            # 检查是否需要锁定IP
            if failed_count >= self.max_failed_attempts * 2:
                ip_lock_key = f"login:ip_lock:{ip_address}"
                await self.redis_client.setex(ip_lock_key, self.lockout_duration, "locked")
    
    async def is_ip_whitelisted(self, ip_address: str) -> bool:
        """检查IP是否在白名单中"""
        whitelist_key = "login:ip_whitelist"
        whitelist = await self.redis_client.smembers(whitelist_key)
        return ip_address in whitelist
    
    async def add_ip_to_whitelist(self, ip_address: str):
        """添加IP到白名单"""
        whitelist_key = "login:ip_whitelist"
        await self.redis_client.sadd(whitelist_key, ip_address)
    
    async def remove_ip_from_whitelist(self, ip_address: str):
        """从白名单移除IP"""
        whitelist_key = "login:ip_whitelist"
        await self.redis_client.srem(whitelist_key, ip_address)
```

## 最佳实践

### 1. 权限设计原则
- **最小权限原则**: 用户只拥有完成工作所需的最小权限
- **职责分离**: 不同角色承担不同的职责，避免权限集中
- **权限继承**: 合理设计权限继承关系，避免重复配置
- **动态权限**: 支持运行时动态调整权限，提高系统灵活性

### 2. 安全防护原则
- **多层防护**: 实现多层安全防护，提高系统安全性
- **实时监控**: 实时监控权限使用情况，及时发现异常
- **审计追踪**: 完整记录权限操作日志，支持安全审计
- **定期评估**: 定期评估权限配置，及时调整不合理权限

### 3. 性能优化原则
- **合理缓存**: 合理使用缓存，减少权限验证开销
- **批量操作**: 支持批量权限操作，提高系统效率
- **异步处理**: 使用异步处理，提高系统响应速度
- **资源控制**: 控制权限验证资源消耗，避免影响系统性能

---

**注意**: 本文档会持续更新，请关注最新版本。如有问题，请通过 Issues 反馈。 