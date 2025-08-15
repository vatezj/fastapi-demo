# FastAPI DAO 层开发详细指南

## 1. DAO 层概述

### 1.1 职责定义

DAO (Data Access Object) 层是数据访问的核心层，负责：
- **数据库操作封装**: 封装所有数据库操作
- **SQL查询构建**: 使用 SQLAlchemy 构建查询
- **数据转换映射**: 数据库记录与对象的转换
- **连接管理**: 数据库连接的生命周期管理
- **事务控制**: 基础的事务操作

### 1.2 设计原则

- **单一职责**: 每个 DAO 类只负责一个数据实体
- **接口隔离**: 提供清晰的接口定义
- **异常处理**: 统一的数据库异常处理
- **性能优化**: 查询优化和连接池管理
- **类型安全**: 使用类型注解确保类型安全

## 2. DAO 层架构

### 2.1 基础结构

```python
from typing import List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from utils.log_util import logger

class BaseDAO:
    """DAO 基类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def _handle_db_exception(self, operation: str, error: Exception):
        """统一数据库异常处理"""
        logger.error(f"数据库操作失败 {operation}: {str(error)}")
        raise error

class UserDAO(BaseDAO):
    """用户数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
```

### 2.2 依赖注入模式

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db

class UserDAO(BaseDAO):
    """用户数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db)
    
    @classmethod
    def create_dao(cls, db: AsyncSession = Depends(get_db)):
        """创建 DAO 实例的工厂方法"""
        return cls(db)

# 使用方式
@userController.get("/list")
async def get_user_list(
    db: AsyncSession = Depends(get_db)
):
    user_dao = UserDAO.create_dao(db)
    return await user_dao.get_users()
```

## 3. 基础 CRUD 操作

### 3.1 查询操作

#### 3.1.1 单条记录查询
```python
async def get_user_by_id(self, user_id: int) -> Optional[SysUser]:
    """根据ID获取用户"""
    try:
        query = select(SysUser).where(SysUser.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        await self._handle_db_exception(f"根据ID获取用户 {user_id}", e)

async def get_user_by_username(self, username: str) -> Optional[SysUser]:
    """根据用户名获取用户"""
    try:
        query = select(SysUser).where(SysUser.user_name == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        await self._handle_db_exception(f"根据用户名获取用户 {username}", e)
```

#### 3.1.2 列表查询
```python
async def get_users(
    self, 
    filters: List[Any] = None, 
    offset: int = 0, 
    limit: int = 10,
    order_by: str = "id",
    order_desc: bool = True
) -> List[SysUser]:
    """获取用户列表"""
    try:
        query = select(SysUser)
        
        # 添加过滤条件
        if filters:
            for filter_condition in filters:
                query = query.where(filter_condition)
        
        # 添加排序
        if order_by == "id":
            if order_desc:
                query = query.order_by(SysUser.id.desc())
            else:
                query = query.order_by(SysUser.id.asc())
        
        # 添加分页
        query = query.offset(offset).limit(limit)
        
        # 执行查询
        result = await self.db.execute(query)
        return result.scalars().all()
        
    except Exception as e:
        await self._handle_db_exception("获取用户列表", e)
```

### 3.2 创建操作

```python
async def create_user(self, user: SysUser) -> SysUser:
    """创建用户"""
    try:
        # 设置创建时间
        user.create_time = datetime.now()
        user.update_time = datetime.now()
        
        # 添加到数据库
        self.db.add(user)
        await self.db.commit()
        
        # 刷新对象，获取自动生成的ID
        await self.db.refresh(user)
        
        logger.info(f"用户创建成功: ID={user.id}, 用户名={user.user_name}")
        return user
        
    except Exception as e:
        await self.db.rollback()
        await self._handle_db_exception("创建用户", e)
```

### 3.3 更新操作

```python
async def update_user(self, user_id: int, update_data: dict) -> bool:
    """更新用户"""
    try:
        # 构建更新查询
        query = update(SysUser).where(SysUser.id == user_id).values(
            **update_data,
            update_time=datetime.now()
        )
        
        # 执行更新
        result = await self.db.execute(query)
        await self.db.commit()
        
        # 检查更新结果
        updated_count = result.rowcount
        if updated_count > 0:
            logger.info(f"用户 {user_id} 更新成功")
        else:
            logger.warning(f"用户 {user_id} 更新失败，可能不存在")
        
        return updated_count > 0
        
    except Exception as e:
        await self.db.rollback()
        await self._handle_db_exception(f"更新用户 {user_id}", e)
```

### 3.4 删除操作

```python
async def delete_user(self, user_id: int) -> bool:
    """删除用户"""
    try:
        # 构建删除查询
        query = delete(SysUser).where(SysUser.id == user_id)
        
        # 执行删除
        result = await self.db.execute(query)
        await self.db.commit()
        
        # 检查删除结果
        deleted_count = result.rowcount
        if deleted_count > 0:
            logger.info(f"用户 {user_id} 删除成功")
        else:
            logger.warning(f"用户 {user_id} 删除失败，可能不存在")
        
        return deleted_count > 0
        
    except Exception as e:
        await self.db.rollback()
        await self._handle_db_exception(f"删除用户 {user_id}", e)
```

## 4. 高级查询操作

### 4.1 关联查询

#### 4.1.1 一对一关联
```python
async def get_user_with_profile(self, user_id: int) -> Optional[SysUser]:
    """获取用户及其档案信息"""
    try:
        query = select(SysUser).options(
            selectinload(SysUser.profile)
        ).where(SysUser.id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
        
    except Exception as e:
        await self._handle_db_exception(f"获取用户档案 {user_id}", e)
```

#### 4.1.2 一对多关联
```python
async def get_user_with_roles(self, user_id: int) -> Optional[SysUser]:
    """获取用户及其角色信息"""
    try:
        query = select(SysUser).options(
            selectinload(SysUser.roles)
        ).where(SysUser.id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
        
    except Exception as e:
        await self._handle_db_exception(f"获取用户角色 {user_id}", e)
```

### 4.2 复杂查询条件

```python
async def get_users_by_conditions(
    self,
    username: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[str] = None,
    dept_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[SysUser]:
    """根据条件查询用户"""
    try:
        query = select(SysUser)
        conditions = []
        
        # 用户名模糊查询
        if username:
            conditions.append(SysUser.user_name.like(f"%{username}%"))
        
        # 邮箱精确查询
        if email:
            conditions.append(SysUser.email == email)
        
        # 状态查询
        if status:
            conditions.append(SysUser.status == status)
        
        # 部门查询
        if dept_id:
            conditions.append(SysUser.dept_id == dept_id)
        
        # 时间范围查询
        if start_time:
            conditions.append(SysUser.create_time >= start_time)
        if end_time:
            conditions.append(SysUser.create_time <= end_time)
        
        # 添加条件
        if conditions:
            query = query.where(and_(*conditions))
        
        # 执行查询
        result = await self.db.execute(query)
        return result.scalars().all()
        
    except Exception as e:
        await self._handle_db_exception("条件查询用户", e)
```

## 5. 总结

DAO 层是 FastAPI 后端架构中的数据访问核心，负责所有数据库操作。本指南详细介绍了：

1. **基础架构**: DAO 层的设计原则和基础结构
2. **CRUD 操作**: 完整的增删改查操作实现
3. **高级查询**: 关联查询、复杂条件等
4. **异常处理**: 统一的数据库异常处理
5. **性能优化**: 查询优化和连接池管理

遵循这些指导原则，可以构建出高性能、高可靠、易维护的 DAO 层代码。
