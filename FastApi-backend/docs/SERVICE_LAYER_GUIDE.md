# FastAPI Service 层开发详细指南

## 1. Service 层概述

### 1.1 职责定义

Service 层是业务逻辑的核心层，负责：
- **业务逻辑处理**: 实现具体的业务规则和流程
- **事务管理**: 确保数据操作的一致性
- **数据验证**: 业务层面的数据验证
- **异常处理**: 业务异常的统一处理
- **调用协调**: 协调多个 DAO 层的操作

### 1.2 设计原则

- **单一职责**: 每个 Service 类只负责一个业务领域
- **依赖注入**: 通过构造函数注入依赖
- **异步编程**: 使用 async/await 语法
- **异常处理**: 统一的异常处理策略
- **日志记录**: 完整的操作日志记录

## 2. Service 层架构

### 2.1 基础结构

```python
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from utils.log_util import logger

class BaseService:
    """服务基类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def _handle_exception(self, operation: str, error: Exception):
        """统一异常处理"""
        logger.error(f"{operation}失败: {str(error)}")
        raise error

class UserService(BaseService):
    """用户服务类"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        # 初始化 DAO 对象
        self.user_dao = UserDAO(db)
        self.role_dao = RoleDAO(db)
```

### 2.2 依赖注入模式

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db

class UserService:
    """用户服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_dao = UserDAO(db)
        self.role_dao = RoleDAO(db)
    
    @classmethod
    def create_service(cls, db: AsyncSession = Depends(get_db)):
        """创建服务实例的工厂方法"""
        return cls(db)

# 使用方式
@userController.get("/list")
async def get_user_list(
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService.create_service(db)
    return await user_service.get_user_list()
```

## 3. 业务逻辑实现

### 3.1 基础 CRUD 操作

#### 3.1.1 查询操作
```python
async def get_user_list(
    self, 
    page_num: int = 1, 
    page_size: int = 10, 
    filters: Dict[str, Any] = None
) -> PageResponseModel:
    """获取用户列表"""
    try:
        # 构建查询条件
        query_filters = self._build_query_filters(filters)
        
        # 获取总数
        total = await self.user_dao.count_users(query_filters)
        
        # 获取分页数据
        users = await self.user_dao.get_users(
            filters=query_filters,
            offset=(page_num - 1) * page_size,
            limit=page_size
        )
        
        # 转换为响应模型
        user_list = [self._convert_to_vo(user) for user in users]
        
        return PageResponseModel(
            rows=user_list,
            total=total,
            page_num=page_num,
            page_size=page_size
        )
        
    except Exception as e:
        await self._handle_exception("获取用户列表", e)

async def get_user_by_id(self, user_id: int) -> Optional[UserResponseModel]:
    """根据ID获取用户"""
    try:
        # 参数验证
        if user_id <= 0:
            raise ValueError("无效的用户ID")
        
        # 查询用户
        user = await self.user_dao.get_user_by_id(user_id)
        if not user:
            return None
        
        # 转换为响应模型
        return self._convert_to_vo(user)
        
    except Exception as e:
        await self._handle_exception(f"获取用户ID {user_id}", e)
```

#### 3.1.2 创建操作
```python
async def create_user(self, user_data: UserCreateModel) -> UserResponseModel:
    """创建用户"""
    try:
        # 业务验证
        await self._validate_user_creation(user_data)
        
        # 创建用户对象
        user = SysUser(
            user_name=user_data.user_name,
            nick_name=user_data.nick_name,
            email=user_data.email,
            password=hash_password(user_data.password),
            status=user_data.status,
            dept_id=user_data.dept_id,
            remark=user_data.remark
        )
        
        # 保存到数据库
        created_user = await self.user_dao.create_user(user)
        
        # 转换为响应模型
        return self._convert_to_vo(created_user)
        
    except Exception as e:
        await self._handle_exception("创建用户", e)

async def _validate_user_creation(self, user_data: UserCreateModel):
    """验证用户创建"""
    # 检查用户名是否已存在
    existing_user = await self.user_dao.get_user_by_username(user_data.user_name)
    if existing_user:
        raise ValueError(f"用户名 {user_data.user_name} 已存在")
    
    # 检查邮箱是否已存在
    if user_data.email:
        existing_email = await self.user_dao.get_user_by_email(user_data.email)
        if existing_email:
            raise ValueError(f"邮箱 {user_data.email} 已存在")
    
    # 检查部门是否存在
    if user_data.dept_id:
        dept = await self.dept_dao.get_dept_by_id(user_data.dept_id)
        if not dept:
            raise ValueError(f"部门ID {user_data.dept_id} 不存在")
```

#### 3.1.3 更新操作
```python
async def update_user(self, user_id: int, update_data: UserUpdateModel) -> bool:
    """更新用户"""
    try:
        # 检查用户是否存在
        existing_user = await self.user_dao.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError(f"用户ID {user_id} 不存在")
        
        # 业务验证
        await self._validate_user_update(user_id, update_data)
        
        # 构建更新数据
        update_dict = update_data.dict(exclude_unset=True)
        
        # 执行更新
        success = await self.user_dao.update_user(user_id, update_dict)
        
        if success:
            logger.info(f"用户 {user_id} 更新成功")
        
        return success
        
    except Exception as e:
        await self._handle_exception(f"更新用户 {user_id}", e)

async def _validate_user_update(self, user_id: int, update_data: UserUpdateModel):
    """验证用户更新"""
    # 检查邮箱是否被其他用户使用
    if update_data.email:
        existing_email = await self.user_dao.get_user_by_email(update_data.email)
        if existing_email and existing_email.id != user_id:
            raise ValueError(f"邮箱 {update_data.email} 已被其他用户使用")
    
    # 检查部门是否存在
    if update_data.dept_id:
        dept = await self.dept_dao.get_dept_by_id(update_data.dept_id)
        if not dept:
            raise ValueError(f"部门ID {update_data.dept_id} 不存在")
```

#### 3.1.4 删除操作
```python
async def delete_user(self, user_id: int) -> bool:
    """删除用户"""
    try:
        # 检查用户是否存在
        existing_user = await self.user_dao.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError(f"用户ID {user_id} 不存在")
        
        # 检查是否为系统管理员
        if existing_user.user_name == "admin":
            raise ValueError("不能删除系统管理员用户")
        
        # 检查用户是否有关联数据
        await self._check_user_dependencies(user_id)
        
        # 执行删除
        success = await self.user_dao.delete_user(user_id)
        
        if success:
            logger.info(f"用户 {user_id} 删除成功")
        
        return success
        
    except Exception as e:
        await self._handle_exception(f"删除用户 {user_id}", e)

async def _check_user_dependencies(self, user_id: int):
    """检查用户依赖关系"""
    # 检查是否有未完成的任务
    tasks = await self.task_dao.get_user_tasks(user_id)
    if tasks:
        raise ValueError("用户有未完成的任务，不能删除")
    
    # 检查是否有未处理的申请
    applications = await self.application_dao.get_user_applications(user_id)
    if applications:
        raise ValueError("用户有未处理的申请，不能删除")
```

### 3.2 复杂业务逻辑

#### 3.2.1 批量操作
```python
async def batch_delete_users(self, user_ids: List[int]) -> Dict[str, Any]:
    """批量删除用户"""
    try:
        results = {
            "success": [],
            "failed": [],
            "total": len(user_ids)
        }
        
        for user_id in user_ids:
            try:
                success = await self.delete_user(user_id)
                if success:
                    results["success"].append(user_id)
                else:
                    results["failed"].append({"id": user_id, "reason": "删除失败"})
            except Exception as e:
                results["failed"].append({"id": user_id, "reason": str(e)})
        
        logger.info(f"批量删除用户完成: 成功 {len(results['success'])} 个, 失败 {len(results['failed'])} 个")
        return results
        
    except Exception as e:
        await self._handle_exception("批量删除用户", e)

async def batch_update_user_status(self, user_ids: List[int], status: str) -> Dict[str, Any]:
    """批量更新用户状态"""
    try:
        # 验证状态值
        if status not in ["0", "1"]:
            raise ValueError("无效的状态值")
        
        # 批量更新
        success_count = await self.user_dao.batch_update_status(user_ids, status)
        
        logger.info(f"批量更新用户状态完成: 成功更新 {success_count} 个用户")
        
        return {
            "success_count": success_count,
            "total": len(user_ids),
            "status": status
        }
        
    except Exception as e:
        await self._handle_exception("批量更新用户状态", e)
```

#### 3.2.2 关联数据处理
```python
async def get_user_with_roles(self, user_id: int) -> UserWithRolesResponseModel:
    """获取用户及其角色信息"""
    try:
        # 获取用户基本信息
        user = await self.user_dao.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"用户ID {user_id} 不存在")
        
        # 获取用户角色
        user_roles = await self.role_dao.get_user_roles(user_id)
        
        # 获取角色权限
        role_permissions = []
        for role in user_roles:
            permissions = await self.permission_dao.get_role_permissions(role.id)
            role_permissions.append({
                "role_id": role.id,
                "role_name": role.role_name,
                "permissions": permissions
            })
        
        # 构建响应数据
        return UserWithRolesResponseModel(
            user=self._convert_to_vo(user),
            roles=role_permissions
        )
        
    except Exception as e:
        await self._handle_exception(f"获取用户角色信息 {user_id}", e)

async def assign_user_roles(self, user_id: int, role_ids: List[int]) -> bool:
    """分配用户角色"""
    try:
        # 检查用户是否存在
        user = await self.user_dao.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"用户ID {user_id} 不存在")
        
        # 检查角色是否存在
        for role_id in role_ids:
            role = await self.role_dao.get_role_by_id(role_id)
            if not role:
                raise ValueError(f"角色ID {role_id} 不存在")
        
        # 删除现有角色分配
        await self.role_dao.delete_user_roles(user_id)
        
        # 分配新角色
        for role_id in role_ids:
            await self.role_dao.assign_user_role(user_id, role_id)
        
        logger.info(f"用户 {user_id} 角色分配成功: {role_ids}")
        return True
        
    except Exception as e:
        await self._handle_exception(f"分配用户角色 {user_id}", e)
```

#### 3.2.3 业务规则验证
```python
async def change_user_password(self, user_id: int, old_password: str, new_password: str) -> bool:
    """修改用户密码"""
    try:
        # 获取用户信息
        user = await self.user_dao.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"用户ID {user_id} 不存在")
        
        # 验证旧密码
        if not verify_password(old_password, user.password):
            raise ValueError("旧密码不正确")
        
        # 验证新密码强度
        self._validate_password_strength(new_password)
        
        # 检查新密码是否与旧密码相同
        if old_password == new_password:
            raise ValueError("新密码不能与旧密码相同")
        
        # 更新密码
        hashed_password = hash_password(new_password)
        success = await self.user_dao.update_user(user_id, {"password": hashed_password})
        
        if success:
            logger.info(f"用户 {user_id} 密码修改成功")
        
        return success
        
    except Exception as e:
        await self._handle_exception(f"修改用户密码 {user_id}", e)

def _validate_password_strength(self, password: str):
    """验证密码强度"""
    if len(password) < 8:
        raise ValueError("密码长度不能少于8位")
    
    if not any(c.isupper() for c in password):
        raise ValueError("密码必须包含大写字母")
    
    if not any(c.islower() for c in password):
        raise ValueError("密码必须包含小写字母")
    
    if not any(c.isdigit() for c in password):
        raise ValueError("密码必须包含数字")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        raise ValueError("密码必须包含特殊字符")
```

## 4. 事务管理

### 4.1 基础事务处理

```python
async def create_user_with_profile(self, user_data: UserCreateModel, profile_data: UserProfileModel) -> UserResponseModel:
    """创建用户及其档案信息"""
    try:
        # 开始事务
        async with self.db.begin():
            # 创建用户
            user = SysUser(
                user_name=user_data.user_name,
                nick_name=user_data.nick_name,
                password=hash_password(user_data.password),
                status=user_data.status
            )
            created_user = await self.user_dao.create_user(user)
            
            # 创建用户档案
            profile = UserProfile(
                user_id=created_user.id,
                real_name=profile_data.real_name,
                id_card=profile_data.id_card,
                phone=profile_data.phone,
                address=profile_data.address
            )
            await self.profile_dao.create_profile(profile)
            
            # 提交事务
            await self.db.commit()
            
            return self._convert_to_vo(created_user)
            
    except Exception as e:
        # 回滚事务
        await self.db.rollback()
        await self._handle_exception("创建用户及档案", e)
```

### 4.2 复杂事务处理

```python
async def transfer_user_department(self, user_id: int, new_dept_id: int) -> bool:
    """用户部门调动"""
    try:
        async with self.db.begin():
            # 获取用户信息
            user = await self.user_dao.get_user_by_id(user_id)
            if not user:
                raise ValueError(f"用户ID {user_id} 不存在")
            
            # 获取新部门信息
            new_dept = await self.dept_dao.get_dept_by_id(new_dept_id)
            if not new_dept:
                raise ValueError(f"部门ID {new_dept_id} 不存在")
            
            # 检查用户是否有未完成的任务
            pending_tasks = await self.task_dao.get_user_pending_tasks(user_id)
            if pending_tasks:
                raise ValueError("用户有未完成的任务，不能调动部门")
            
            # 更新用户部门
            await self.user_dao.update_user(user_id, {"dept_id": new_dept_id})
            
            # 记录调动日志
            transfer_log = TransferLog(
                user_id=user_id,
                old_dept_id=user.dept_id,
                new_dept_id=new_dept_id,
                transfer_time=datetime.now(),
                operator_id=get_current_user_id()
            )
            await self.log_dao.create_transfer_log(transfer_log)
            
            # 发送通知
            await self.notification_service.send_dept_transfer_notification(
                user_id, user.dept_id, new_dept_id
            )
            
            await self.db.commit()
            logger.info(f"用户 {user_id} 部门调动成功: {user.dept_id} -> {new_dept_id}")
            return True
            
    except Exception as e:
        await self.db.rollback()
        await self._handle_exception(f"用户部门调动 {user_id}", e)
```

## 5. 缓存策略

### 5.1 基础缓存使用

```python
from utils.cache_decorator import cache

class UserService(BaseService):
    
    @cache(expire=300)  # 缓存5分钟
    async def get_user_by_id(self, user_id: int) -> Optional[UserResponseModel]:
        """获取用户信息（带缓存）"""
        user = await self.user_dao.get_user_by_id(user_id)
        if user:
            return self._convert_to_vo(user)
        return None
    
    @cache(expire=600, key_prefix="user_list")  # 缓存10分钟
    async def get_user_list(self, filters: Dict[str, Any] = None) -> List[UserResponseModel]:
        """获取用户列表（带缓存）"""
        users = await self.user_dao.get_users(filters=filters)
        return [self._convert_to_vo(user) for user in users]
```

### 5.2 缓存更新策略

```python
async def update_user(self, user_id: int, update_data: UserUpdateModel) -> bool:
    """更新用户（更新缓存）"""
    try:
        # 执行更新
        success = await self.user_dao.update_user(user_id, update_data.dict(exclude_unset=True))
        
        if success:
            # 清除相关缓存
            await self._clear_user_cache(user_id)
            logger.info(f"用户 {user_id} 更新成功，缓存已清除")
        
        return success
        
    except Exception as e:
        await self._handle_exception(f"更新用户 {user_id}", e)

async def _clear_user_cache(self, user_id: int):
    """清除用户相关缓存"""
    # 清除用户信息缓存
    cache_key = f"user:{user_id}"
    await self.redis.delete(cache_key)
    
    # 清除用户列表缓存
    await self.redis.delete("user_list:*")
    
    # 清除用户角色缓存
    await self.redis.delete(f"user_roles:{user_id}")
```

## 6. 异常处理

### 6.1 业务异常定义

```python
class UserServiceException(Exception):
    """用户服务异常基类"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class UserNotFoundException(UserServiceException):
    """用户不存在异常"""
    
    def __init__(self, user_id: int):
        super().__init__(f"用户ID {user_id} 不存在", "USER_NOT_FOUND")

class DuplicateUsernameException(UserServiceException):
    """用户名重复异常"""
    
    def __init__(self, username: str):
        super().__init__(f"用户名 {username} 已存在", "DUPLICATE_USERNAME")

class InvalidPasswordException(UserServiceException):
    """密码无效异常"""
    
    def __init__(self, reason: str):
        super().__init__(f"密码无效: {reason}", "INVALID_PASSWORD")
```

### 6.2 异常处理策略

```python
async def _handle_exception(self, operation: str, error: Exception):
    """统一异常处理"""
    if isinstance(error, UserServiceException):
        # 业务异常，记录日志并重新抛出
        logger.warning(f"{operation}: {error.message}")
        raise error
    elif isinstance(error, ValueError):
        # 参数异常，转换为业务异常
        logger.warning(f"{operation}: 参数错误 - {error}")
        raise UserServiceException(str(error), "INVALID_PARAMETER")
    else:
        # 系统异常，记录错误日志并抛出通用异常
        logger.error(f"{operation}: 系统错误 - {str(error)}", exc_info=True)
        raise UserServiceException("系统内部错误", "SYSTEM_ERROR")
```

## 7. 日志记录

### 7.1 操作日志

```python
async def create_user(self, user_data: UserCreateModel) -> UserResponseModel:
    """创建用户"""
    try:
        # 记录操作开始
        logger.info(f"开始创建用户: {user_data.user_name}")
        
        # 业务验证
        await self._validate_user_creation(user_data)
        
        # 创建用户
        user = SysUser(
            user_name=user_data.user_name,
            nick_name=user_data.nick_name,
            email=user_data.email,
            password=hash_password(user_data.password)
        )
        
        created_user = await self.user_dao.create_user(user)
        
        # 记录操作成功
        logger.info(f"用户创建成功: ID={created_user.id}, 用户名={created_user.user_name}")
        
        return self._convert_to_vo(created_user)
        
    except Exception as e:
        # 记录操作失败
        logger.error(f"用户创建失败: {user_data.user_name}, 错误: {str(e)}")
        await self._handle_exception("创建用户", e)
```

### 7.2 性能日志

```python
import time
from functools import wraps

def log_performance(func):
    """性能日志装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} 执行完成，耗时: {execution_time:.3f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败，耗时: {execution_time:.3f}秒，错误: {str(e)}")
            raise
    return wrapper

class UserService(BaseService):
    
    @log_performance
    async def get_user_list(self, filters: Dict[str, Any] = None) -> List[UserResponseModel]:
        """获取用户列表（带性能日志）"""
        users = await self.user_dao.get_users(filters=filters)
        return [self._convert_to_vo(user) for user in users]
```

## 8. 测试策略

### 8.1 单元测试

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from module_admin.service.user_service import UserService
from module_admin.entity.vo.user_vo import UserCreateModel

class TestUserService:
    """用户服务测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock()
    
    @pytest.fixture
    def user_service(self, mock_db):
        """用户服务实例"""
        return UserService(mock_db)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_db):
        """测试用户创建成功"""
        # 准备测试数据
        user_data = UserCreateModel(
            user_name="testuser",
            nick_name="测试用户",
            password="Test123!",
            email="test@example.com"
        )
        
        # Mock DAO方法
        mock_db.user_dao.get_user_by_username.return_value = None
        mock_db.user_dao.get_user_by_email.return_value = None
        mock_db.user_dao.create_user.return_value = MagicMock(
            id=1,
            user_name="testuser",
            nick_name="测试用户"
        )
        
        # 执行测试
        result = await user_service.create_user(user_data)
        
        # 验证结果
        assert result.id == 1
        assert result.user_name == "testuser"
        assert result.nick_name == "测试用户"
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, user_service, mock_db):
        """测试创建重复用户名失败"""
        user_data = UserCreateModel(
            user_name="existinguser",
            nick_name="测试用户",
            password="Test123!"
        )
        
        # Mock DAO方法返回已存在的用户
        mock_db.user_dao.get_user_by_username.return_value = MagicMock()
        
        # 验证异常抛出
        with pytest.raises(ValueError, match="用户名 existinguser 已存在"):
            await user_service.create_user(user_data)
```

### 8.2 集成测试

```python
@pytest.mark.asyncio
async def test_user_creation_integration(test_db):
    """测试用户创建集成"""
    # 创建服务实例
    user_service = UserService(test_db)
    
    # 准备测试数据
    user_data = UserCreateModel(
        user_name="integration_user",
        nick_name="集成测试用户",
        password="Test123!",
        email="integration@example.com"
    )
    
    # 执行创建
    result = await user_service.create_user(user_data)
    
    # 验证结果
    assert result.user_name == "integration_user"
    
    # 验证数据库中的数据
    db_user = await test_db.execute(
        select(SysUser).where(SysUser.user_name == "integration_user")
    )
    db_user = db_user.scalar_one()
    assert db_user.nick_name == "集成测试用户"
```

## 9. 性能优化

### 9.1 查询优化

```python
async def get_users_with_roles(self, user_ids: List[int]) -> List[UserWithRolesModel]:
    """获取用户及其角色信息（批量查询优化）"""
    try:
        # 批量查询用户
        users = await self.user_dao.get_users_by_ids(user_ids)
        
        # 批量查询用户角色
        user_roles = await self.role_dao.get_users_roles(user_ids)
        
        # 批量查询角色权限
        role_ids = list(set([ur.role_id for ur in user_roles]))
        role_permissions = await self.permission_dao.get_roles_permissions(role_ids)
        
        # 构建响应数据
        result = []
        for user in users:
            user_role_list = [ur for ur in user_roles if ur.user_id == user.id]
            user_permissions = []
            
            for user_role in user_role_list:
                role_perm = [rp for rp in role_permissions if rp.role_id == user_role.role_id]
                user_permissions.extend(role_perm)
            
            result.append(UserWithRolesModel(
                user=self._convert_to_vo(user),
                roles=user_role_list,
                permissions=user_permissions
            ))
        
        return result
        
    except Exception as e:
        await self._handle_exception("获取用户角色信息", e)
```

### 9.2 缓存优化

```python
async def get_user_by_username(self, username: str) -> Optional[UserResponseModel]:
    """根据用户名获取用户（多级缓存）"""
    try:
        # 第一级缓存：内存缓存
        cache_key = f"user_username:{username}"
        cached_user = self._memory_cache.get(cache_key)
        if cached_user:
            return cached_user
        
        # 第二级缓存：Redis缓存
        redis_user = await self.redis.get(cache_key)
        if redis_user:
            user_data = json.loads(redis_user)
            # 更新内存缓存
            self._memory_cache.set(cache_key, user_data, expire=60)
            return user_data
        
        # 数据库查询
        user = await self.user_dao.get_user_by_username(username)
        if user:
            user_data = self._convert_to_vo(user)
            
            # 更新缓存
            await self.redis.setex(cache_key, 300, json.dumps(user_data.dict()))
            self._memory_cache.set(cache_key, user_data, expire=60)
            
            return user_data
        
        return None
        
    except Exception as e:
        await self._handle_exception(f"根据用户名获取用户 {username}", e)
```

## 10. 总结

Service 层是 FastAPI 后端架构中的核心层，负责实现复杂的业务逻辑。本指南详细介绍了：

1. **基础架构**: Service 层的设计原则和基础结构
2. **业务逻辑**: CRUD 操作、复杂业务逻辑的实现
3. **事务管理**: 基础事务和复杂事务的处理
4. **缓存策略**: 缓存的使用和更新策略
5. **异常处理**: 业务异常的定义和处理
6. **日志记录**: 操作日志和性能日志
7. **测试策略**: 单元测试和集成测试
8. **性能优化**: 查询优化和缓存优化

遵循这些指导原则，可以构建出高质量、高性能、易维护的 Service 层代码。
