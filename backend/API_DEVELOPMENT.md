# API 开发规范

## 概述

本文档定义了 RuoYi-FastAPI 项目的 API 开发规范，包括接口设计、开发流程、代码规范等。

## API 设计原则

### 1. RESTful 设计
- 使用标准的 HTTP 方法 (GET, POST, PUT, DELETE)
- 资源使用名词而非动词
- 使用复数名词表示资源集合
- 使用嵌套结构表示资源关系

### 2. 统一响应格式
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": null,
    "timestamp": "2024-01-01T12:00:00"
}
```

### 3. 状态码规范
- **2xx**: 成功
  - 200: 请求成功
  - 201: 创建成功
  - 204: 无内容返回
- **4xx**: 客户端错误
  - 400: 请求参数错误
  - 401: 未授权
  - 403: 禁止访问
  - 404: 资源不存在
  - 409: 资源冲突
- **5xx**: 服务器错误
  - 500: 内部服务器错误
  - 502: 网关错误
  - 503: 服务不可用

## 控制器开发规范

### 1. 基本结构

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from utils.response_util import ResponseResult
from utils.page_util import PageQuery, PageResult
from module_admin.aspect.interface_auth import require_permissions
from module_admin.aspect.data_scope import require_data_scope

router = APIRouter(prefix="/user", tags=["用户管理"])

class UserController:
    def __init__(self):
        self.user_service = UserService()
    
    @router.get("/list", response_model=List[UserVO])
    @require_permissions(["system:user:list"])
    async def get_user_list(self, query: UserQuery = Depends()):
        """获取用户列表"""
        try:
            users = await self.user_service.get_user_list(query)
            return users
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取用户列表失败")
    
    @router.get("/page", response_model=PageResult[UserVO])
    @require_permissions(["system:user:list"])
    async def get_user_page(self, page_query: PageQuery = Depends()):
        """分页获取用户列表"""
        try:
            result = await self.user_service.get_user_page(page_query)
            return result
        except Exception as e:
            logger.error(f"分页获取用户列表失败: {e}")
            raise HTTPException(status_code=500, detail="分页获取用户列表失败")
    
    @router.get("/{user_id}", response_model=UserVO)
    @require_permissions(["system:user:query"])
    async def get_user_by_id(self, user_id: int):
        """根据ID获取用户信息"""
        try:
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            raise HTTPException(status_code=500, detail="获取用户信息失败")
    
    @router.post("/", response_model=ResponseResult)
    @require_permissions(["system:user:add"])
    async def create_user(self, user_data: UserCreateVO):
        """创建用户"""
        try:
            result = await self.user_service.create_user(user_data)
            return ResponseResult(code=200, msg="用户创建成功", data=result)
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            raise HTTPException(status_code=500, detail="创建用户失败")
    
    @router.put("/{user_id}", response_model=ResponseResult)
    @require_permissions(["system:user:edit"])
    async def update_user(self, user_id: int, user_data: UserUpdateVO):
        """更新用户信息"""
        try:
            result = await self.user_service.update_user(user_id, user_data)
            return ResponseResult(code=200, msg="用户更新成功", data=result)
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            raise HTTPException(status_code=500, detail="更新用户失败")
    
    @router.delete("/{user_id}", response_model=ResponseResult)
    @require_permissions(["system:user:remove"])
    async def delete_user(self, user_id: int):
        """删除用户"""
        try:
            await self.user_service.delete_user(user_id)
            return ResponseResult(code=200, msg="用户删除成功")
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            raise HTTPException(status_code=500, detail="删除用户失败")
    
    @router.delete("/batch", response_model=ResponseResult)
    @require_permissions(["system:user:remove"])
    async def batch_delete_users(self, user_ids: List[int]):
        """批量删除用户"""
        try:
            await self.user_service.batch_delete_users(user_ids)
            return ResponseResult(code=200, msg="批量删除成功")
        except Exception as e:
            logger.error(f"批量删除用户失败: {e}")
            raise HTTPException(status_code=500, detail="批量删除用户失败")

userController = UserController()
```

### 2. 路由装饰器规范

```python
# 基本路由
@router.get("/path")                    # GET 请求
@router.post("/path")                   # POST 请求
@router.put("/path")                    # PUT 请求
@router.delete("/path")                 # DELETE 请求
@router.patch("/path")                  # PATCH 请求

# 路径参数
@router.get("/{id}")                    # 路径参数
@router.get("/{id}/detail")             # 嵌套路径

# 查询参数
@router.get("/list")                    # 查询参数通过 Depends() 注入

# 响应模型
@router.get("/path", response_model=ResponseModel)

# 标签和描述
@router.get("/path", tags=["用户管理"], summary="获取用户列表")
```

### 3. 权限控制

```python
# 接口权限控制
@require_permissions(["system:user:list"])

# 数据权限控制
@require_data_scope("dept")

# 组合使用
@require_permissions(["system:user:list"])
@require_data_scope("dept")
async def get_user_list(self):
    pass
```

## 数据模型规范

### 1. 请求模型 (VO)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class UserCreateVO(BaseModel):
    """用户创建请求模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, description="密码")
    dept_id: int = Field(..., description="部门ID")
    role_ids: List[int] = Field(default=[], description="角色ID列表")
    status: str = Field(default="0", description="状态（0正常 1停用）")
    remark: Optional[str] = Field(None, max_length=500, description="备注")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('手机号只能包含数字')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "username": "testuser",
                "email": "test@example.com",
                "phone": "13800138000",
                "password": "123456",
                "dept_id": 1,
                "role_ids": [1, 2],
                "status": "0",
                "remark": "测试用户"
            }
        }

class UserUpdateVO(BaseModel):
    """用户更新请求模型"""
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=11)
    dept_id: Optional[int] = None
    role_ids: Optional[List[int]] = None
    status: Optional[str] = None
    remark: Optional[str] = Field(None, max_length=500)

class UserQuery(BaseModel):
    """用户查询请求模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dept_id: Optional[int] = None
    status: Optional[str] = None
    create_time_start: Optional[datetime] = None
    create_time_end: Optional[datetime] = None
```

### 2. 响应模型 (VO)

```python
class UserVO(BaseModel):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    dept_id: int = Field(..., description="部门ID")
    dept_name: Optional[str] = Field(None, description="部门名称")
    role_names: List[str] = Field(default=[], description="角色名称列表")
    status: str = Field(..., description="状态")
    status_text: str = Field(..., description="状态文本")
    create_time: datetime = Field(..., description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    remark: Optional[str] = Field(None, description="备注")
    
    class Config:
        from_attributes = True

class PageResult(BaseModel):
    """分页响应模型"""
    total: int = Field(..., description="总记录数")
    rows: List[UserVO] = Field(..., description="数据列表")
    page_num: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
```

## 分页查询规范

### 1. 分页参数

```python
class PageQuery(BaseModel):
    """分页查询参数"""
    page_num: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页大小")
    order_by_column: Optional[str] = Field(None, description="排序字段")
    is_asc: str = Field(default="desc", description="排序方向（asc/desc）")
    
    @validator('is_asc')
    def validate_is_asc(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('排序方向只能是 asc 或 desc')
        return v
```

### 2. 分页实现

```python
async def get_user_page(self, page_query: PageQuery) -> PageResult[UserVO]:
    """分页获取用户列表"""
    # 构建查询条件
    query = select(UserDO)
    
    # 添加查询条件
    if page_query.username:
        query = query.where(UserDO.username.like(f"%{page_query.username}%"))
    
    if page_query.dept_id:
        query = query.where(UserDO.dept_id == page_query.dept_id)
    
    if page_query.status:
        query = query.where(UserDO.status == page_query.status)
    
    # 添加排序
    if page_query.order_by_column:
        order_column = getattr(UserDO, page_query.order_by_column, UserDO.create_time)
        if page_query.is_asc == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
    else:
        query = query.order_by(UserDO.create_time.desc())
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await self.db.scalar(count_query)
    
    # 分页查询
    offset = (page_query.page_num - 1) * page_query.page_size
    query = query.offset(offset).limit(page_query.page_size)
    
    # 执行查询
    result = await self.db.execute(query)
    users = result.scalars().all()
    
    # 转换为VO
    user_vos = [UserVO.from_orm(user) for user in users]
    
    return PageResult(
        total=total,
        rows=user_vos,
        page_num=page_query.page_num,
        page_size=page_query.page_size
    )
```

## 错误处理规范

### 1. 自定义异常

```python
class BusinessException(Exception):
    """业务异常"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)

class ValidationException(Exception):
    """验证异常"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class PermissionException(Exception):
    """权限异常"""
    def __init__(self, message: str = "权限不足"):
        self.message = message
        super().__init__(self.message)
```

### 2. 异常处理中间件

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from exceptions.business_exception import BusinessException
from exceptions.validation_exception import ValidationException
from exceptions.permission_exception import PermissionException

async def exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    if isinstance(exc, BusinessException):
        return JSONResponse(
            status_code=exc.code,
            content={
                "code": exc.code,
                "msg": exc.message,
                "data": None,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    elif isinstance(exc, ValidationException):
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "msg": exc.message,
                "data": None,
                "field": exc.field,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    elif isinstance(exc, PermissionException):
        return JSONResponse(
            status_code=403,
            content={
                "code": 403,
                "msg": exc.message,
                "data": None,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # 其他异常
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": "服务器内部错误",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }
    )
```

## 接口文档规范

### 1. 接口描述

```python
@router.get("/list", 
    response_model=List[UserVO],
    summary="获取用户列表",
    description="根据查询条件获取用户列表，支持分页和排序",
    response_description="用户列表数据")
async def get_user_list(self, query: UserQuery = Depends()):
    """
    获取用户列表
    
    - **username**: 用户名（模糊查询）
    - **email**: 邮箱（模糊查询）
    - **dept_id**: 部门ID
    - **status**: 状态（0正常 1停用）
    - **create_time_start**: 创建时间开始
    - **create_time_end**: 创建时间结束
    
    返回用户列表数据
    """
    pass
```

### 2. 响应示例

```python
class UserVO(BaseModel):
    """用户响应模型"""
    id: int = Field(..., description="用户ID", example=1)
    username: str = Field(..., description="用户名", example="admin")
    email: str = Field(..., description="邮箱", example="admin@example.com")
    status: str = Field(..., description="状态", example="0")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "status": "0"
            }
        }
```

## 性能优化

### 1. 数据库查询优化

```python
# 使用 select_from 避免 N+1 查询
async def get_user_with_roles(self, user_id: int) -> UserVO:
    """获取用户信息（包含角色）"""
    query = (
        select(UserDO)
        .outerjoin(UserRoleDO, UserDO.id == UserRoleDO.user_id)
        .outerjoin(RoleDO, UserRoleDO.role_id == RoleDO.id)
        .where(UserDO.id == user_id)
    )
    
    result = await self.db.execute(query)
    user = result.scalars().first()
    
    return UserVO.from_orm(user)

# 使用 exists 优化子查询
async def check_username_exists(self, username: str, exclude_id: int = None) -> bool:
    """检查用户名是否存在"""
    query = select(UserDO.id).where(UserDO.username == username)
    
    if exclude_id:
        query = query.where(UserDO.id != exclude_id)
    
    query = select(exists().where(query))
    result = await self.db.scalar(query)
    
    return result
```

### 2. 缓存策略

```python
from utils.cache_util import cache

@cache(expire=300)  # 缓存5分钟
async def get_user_by_id(self, user_id: int) -> UserVO:
    """根据ID获取用户信息（带缓存）"""
    user = await self.user_dao.get_by_id(user_id)
    return UserVO.from_orm(user) if user else None

async def update_user(self, user_id: int, user_data: UserUpdateVO) -> UserVO:
    """更新用户信息（清除缓存）"""
    user = await self.user_dao.update(user_id, user_data)
    
    # 清除相关缓存
    await self.cache_util.delete(f"user:{user_id}")
    await self.cache_util.delete_pattern("user:list:*")
    
    return UserVO.from_orm(user)
```

## 测试规范

### 1. 单元测试

```python
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

class TestUserController:
    """用户控制器测试"""
    
    @pytest.mark.asyncio
    async def test_get_user_list(self, client: AsyncClient):
        """测试获取用户列表"""
        response = await client.get("/user/list")
        assert response.status_code == 200
        
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
    
    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient):
        """测试创建用户"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123456",
            "dept_id": 1
        }
        
        response = await client.post("/user/", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "用户创建成功"
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, client: AsyncClient):
        """测试获取不存在的用户"""
        response = await client.get("/user/99999")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "用户不存在"
```

### 2. 集成测试

```python
@pytest.mark.asyncio
async def test_user_workflow(self, client: AsyncClient):
    """测试用户完整工作流程"""
    # 1. 创建用户
    user_data = {
        "username": "workflow_user",
        "email": "workflow@example.com",
        "password": "123456",
        "dept_id": 1
    }
    
    create_response = await client.post("/user/", json=user_data)
    assert create_response.status_code == 200
    
    # 2. 获取用户列表
    list_response = await client.get("/user/list")
    assert list_response.status_code == 200
    
    # 3. 更新用户
    update_data = {"email": "updated@example.com"}
    user_id = 1  # 假设用户ID为1
    
    update_response = await client.put(f"/user/{user_id}", json=update_data)
    assert update_response.status_code == 200
    
    # 4. 删除用户
    delete_response = await client.delete(f"/user/{user_id}")
    assert delete_response.status_code == 200
```

## 最佳实践

### 1. 代码组织
- 保持控制器简洁，业务逻辑放在服务层
- 使用依赖注入管理服务实例
- 实现统一的异常处理
- 添加详细的日志记录

### 2. 性能考虑
- 使用异步操作提高并发性能
- 合理使用缓存减少数据库查询
- 实现分页查询避免大量数据返回
- 优化数据库查询语句

### 3. 安全考虑
- 实现完整的权限验证
- 验证和清理用户输入
- 记录敏感操作日志
- 实现接口限流保护

### 4. 可维护性
- 编写清晰的文档和注释
- 使用类型注解提高代码可读性
- 实现统一的错误处理
- 编写完整的测试用例

---

**注意**: 本文档会持续更新，请关注最新版本。如有问题，请通过 Issues 反馈。