# 数据库开发指南

## 概述

本文档描述了 RuoYi-FastAPI 项目的数据库开发规范，包括数据库设计、数据访问、性能优化等。

## 数据库设计规范

### 1. 命名规范

#### 表命名
- 使用小写字母和下划线
- 表名使用复数形式
- 系统表以 `sys_` 开头
- 业务表以模块名开头

```sql
-- 系统表
sys_user          -- 用户表
sys_role          -- 角色表
sys_menu          -- 菜单表
sys_dept          -- 部门表

-- 业务表
order_info        -- 订单信息表
product_detail    -- 产品详情表
```

#### 字段命名
- 使用小写字母和下划线
- 主键统一命名为 `id`
- 外键命名为 `表名_id`
- 时间字段使用 `create_time`、`update_time`

```sql
-- 标准字段
id                -- 主键ID
user_id           -- 用户ID
dept_id           -- 部门ID
create_time       -- 创建时间
update_time       -- 更新时间
create_by         -- 创建人
update_by         -- 更新人
```

#### 索引命名
- 主键索引：`PRIMARY`
- 唯一索引：`uk_字段名`
- 普通索引：`idx_字段名`
- 外键索引：`fk_表名_字段名`

```sql
-- 索引命名示例
PRIMARY KEY (id)                    -- 主键索引
UNIQUE KEY uk_username (username)   -- 唯一索引
KEY idx_dept_id (dept_id)           -- 普通索引
KEY idx_create_time (create_time)   -- 普通索引
```

### 2. 字段类型规范

#### 数值类型
```sql
-- 整数类型
TINYINT           -- 1字节，范围：-128到127
SMALLINT          -- 2字节，范围：-32768到32767
INT               -- 4字节，范围：-2147483648到2147483647
BIGINT            -- 8字节，范围：-9223372036854775808到9223372036854775807

-- 小数类型
DECIMAL(10,2)     -- 精确小数，总长度10位，小数2位
FLOAT             -- 单精度浮点数
DOUBLE            -- 双精度浮点数
```

#### 字符串类型
```sql
-- 固定长度字符串
CHAR(10)          -- 固定长度10字符，不足补空格

-- 可变长度字符串
VARCHAR(255)      -- 最大长度255字符，实际长度可变
TEXT              -- 长文本，最大65535字符
LONGTEXT          -- 超长文本，最大4294967295字符
```

#### 时间类型
```sql
-- 日期时间类型
DATE              -- 日期，格式：YYYY-MM-DD
TIME              -- 时间，格式：HH:MM:SS
DATETIME          -- 日期时间，格式：YYYY-MM-DD HH:MM:SS
TIMESTAMP         -- 时间戳，自动更新
YEAR              -- 年份，格式：YYYY
```

### 3. 表结构设计

#### 基础表结构
```sql
CREATE TABLE `sys_user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(100) NOT NULL COMMENT '密码',
    `email` VARCHAR(100) COMMENT '邮箱',
    `phone` VARCHAR(11) COMMENT '手机号',
    `status` CHAR(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `dept_id` BIGINT COMMENT '部门ID',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `create_by` BIGINT COMMENT '创建人',
    `update_by` BIGINT COMMENT '更新人',
    `remark` VARCHAR(500) COMMENT '备注',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_dept_id` (`dept_id`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户表';
```

#### 关联表设计
```sql
-- 用户角色关联表
CREATE TABLE `sys_user_role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '关联ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_role` (`user_id`, `role_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户角色关联表';

-- 角色菜单关联表
CREATE TABLE `sys_role_menu` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '关联ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `menu_id` BIGINT NOT NULL COMMENT '菜单ID',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_menu` (`role_id`, `menu_id`),
    KEY `idx_role_id` (`role_id`),
    KEY `idx_menu_id` (`menu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='角色菜单关联表';
```

## 数据访问层设计

### 1. 基础DAO类

```python
from typing import Generic, TypeVar, Type, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from module_admin.entity.do.base_do import BaseDO

T = TypeVar('T', bound=BaseDO)

class BaseDAO(Generic[T]):
    """基础数据访问对象"""
    
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """根据ID获取实体"""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[T]:
        """获取所有实体"""
        result = await self.db.execute(select(self.model))
        return result.scalars().all()
    
    async def get_by_condition(self, **kwargs) -> List[T]:
        """根据条件查询实体"""
        query = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, entity: T) -> T:
        """创建实体"""
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity
    
    async def update(self, id: int, update_data: dict) -> Optional[T]:
        """更新实体"""
        stmt = update(self.model).where(self.model.id == id).values(**update_data)
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount > 0:
            return await self.get_by_id(id)
        return None
    
    async def delete(self, id: int) -> bool:
        """删除实体"""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def count(self, **kwargs) -> int:
        """统计实体数量"""
        query = select(func.count(self.model.id))
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.scalar(query)
        return result or 0
```

### 2. 具体DAO实现

```python
from module_admin.entity.do.user_do import UserDO
from module_admin.entity.do.role_do import RoleDO
from module_admin.entity.do.dept_do import DeptDO

class UserDAO(BaseDAO[UserDO]):
    """用户数据访问对象"""
    
    async def get_by_username(self, username: str) -> Optional[UserDO]:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(UserDO).where(UserDO.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[UserDO]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(UserDO).where(UserDO.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_dept_id(self, dept_id: int) -> List[UserDO]:
        """根据部门ID获取用户列表"""
        result = await self.db.execute(
            select(UserDO).where(UserDO.dept_id == dept_id)
        )
        return result.scalars().all()
    
    async def get_users_with_roles(self, **kwargs) -> List[UserDO]:
        """获取用户列表（包含角色信息）"""
        query = (
            select(UserDO)
            .options(selectinload(UserDO.roles))
            .options(selectinload(UserDO.dept))
        )
        
        # 添加查询条件
        for key, value in kwargs.items():
            if hasattr(UserDO, key) and value is not None:
                query = query.where(getattr(UserDO, key) == value)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user_page(self, page_query, **kwargs) -> tuple[List[UserDO], int]:
        """分页获取用户列表"""
        # 构建查询条件
        query = select(UserDO)
        count_query = select(func.count(UserDO.id))
        
        for key, value in kwargs.items():
            if hasattr(UserDO, key) and value is not None:
                query = query.where(getattr(UserDO, key) == value)
                count_query = count_query.where(getattr(UserDO, key) == value)
        
        # 获取总数
        total = await self.db.scalar(count_query)
        
        # 分页查询
        offset = (page_query.page_num - 1) * page_query.page_size
        query = query.offset(offset).limit(page_query.page_size)
        
        # 添加排序
        if page_query.order_by_column:
            order_column = getattr(UserDO, page_query.order_by_column, UserDO.create_time)
            if page_query.is_asc == 'asc':
                query = query.order_by(order_column.asc())
            else:
                query = query.order_by(order_column.desc())
        else:
            query = query.order_by(UserDO.create_time.desc())
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return users, total
```

### 3. 复杂查询示例

```python
class RoleDAO(BaseDAO[RoleDO]):
    """角色数据访问对象"""
    
    async def get_roles_by_user_id(self, user_id: int) -> List[RoleDO]:
        """根据用户ID获取角色列表"""
        query = (
            select(RoleDO)
            .join(UserRoleDO, RoleDO.id == UserRoleDO.role_id)
            .where(UserRoleDO.user_id == user_id)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_roles_with_menus(self, **kwargs) -> List[RoleDO]:
        """获取角色列表（包含菜单信息）"""
        query = (
            select(RoleDO)
            .options(selectinload(RoleDO.menus))
        )
        
        # 添加查询条件
        for key, value in kwargs.items():
            if hasattr(RoleDO, key) and value is not None:
                query = query.where(getattr(RoleDO, key) == value)
        
        result = await self.db.execute(query)
        return result.scalars().all()

class DeptDAO(BaseDAO[DeptDO]):
    """部门数据访问对象"""
    
    async def get_dept_tree(self) -> List[DeptDO]:
        """获取部门树形结构"""
        # 获取所有部门
        depts = await self.get_all()
        
        # 构建树形结构
        dept_dict = {dept.id: dept for dept in depts}
        root_depts = []
        
        for dept in depts:
            if dept.parent_id == 0:
                root_depts.append(dept)
            else:
                parent = dept_dict.get(dept.parent_id)
                if parent:
                    if not hasattr(parent, 'children'):
                        parent.children = []
                    parent.children.append(dept)
        
        return root_depts
    
    async def get_dept_children(self, dept_id: int) -> List[DeptDO]:
        """获取子部门列表"""
        result = await self.db.execute(
            select(DeptDO).where(DeptDO.parent_id == dept_id)
        )
        return result.scalars().all()
```

## 事务管理

### 1. 基础事务管理

```python
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

class TransactionManager:
    """事务管理器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @asynccontextmanager
    async def transaction(self):
        """事务上下文管理器"""
        try:
            yield self.db
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e

# 使用示例
async def create_user_with_roles(user_data: dict, role_ids: List[int]):
    """创建用户并分配角色"""
    async with transaction_manager.transaction() as db:
        # 创建用户
        user = UserDO(**user_data)
        db.add(user)
        await db.flush()  # 获取用户ID
        
        # 分配角色
        for role_id in role_ids:
            user_role = UserRoleDO(user_id=user.id, role_id=role_id)
            db.add(user_role)
        
        # 事务自动提交
        return user
```

### 2. 嵌套事务处理

```python
class NestedTransactionManager:
    """嵌套事务管理器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._transaction_count = 0
    
    @asynccontextmanager
    async def transaction(self):
        """嵌套事务上下文管理器"""
        self._transaction_count += 1
        
        try:
            yield self.db
            
            self._transaction_count -= 1
            if self._transaction_count == 0:
                await self.db.commit()
        except Exception as e:
            self._transaction_count -= 1
            if self._transaction_count == 0:
                await self.db.rollback()
            raise e

# 使用示例
async def complex_business_operation():
    """复杂业务操作"""
    async with nested_transaction.transaction() as db:
        # 第一个操作
        await operation1(db)
        
        # 嵌套事务
        async with nested_transaction.transaction() as db2:
            await operation2(db2)
        
        # 第三个操作
        await operation3(db)
        
        # 只有最外层事务提交时才会真正提交
```

## 性能优化

### 1. 查询优化

#### 避免N+1查询
```python
# 错误的做法：N+1查询
async def get_users_with_roles_bad():
    users = await user_dao.get_all()
    for user in users:
        user.roles = await role_dao.get_roles_by_user_id(user.id)
    return users

# 正确的做法：使用JOIN查询
async def get_users_with_roles_good():
    query = (
        select(UserDO)
        .options(selectinload(UserDO.roles))
        .options(selectinload(UserDO.dept))
    )
    result = await db.execute(query)
    return result.scalars().all()
```

#### 分页查询优化
```python
async def get_user_page_optimized(page_query, **kwargs):
    """优化的分页查询"""
    # 使用子查询优化COUNT
    subquery = (
        select(UserDO.id)
        .where(*[getattr(UserDO, key) == value for key, value in kwargs.items() if value is not None])
        .subquery()
    )
    
    # 获取总数
    total = await db.scalar(select(func.count()).select_from(subquery))
    
    # 分页查询
    query = (
        select(UserDO)
        .where(UserDO.id.in_(select(subquery.c.id)))
        .offset((page_query.page_num - 1) * page_query.page_size)
        .limit(page_query.page_size)
        .order_by(UserDO.create_time.desc())
    )
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users, total
```

### 2. 索引优化

#### 复合索引设计
```sql
-- 用户表复合索引
CREATE TABLE `sys_user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100),
    `dept_id` BIGINT,
    `status` CHAR(1) DEFAULT '0',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_dept_status` (`dept_id`, `status`),           -- 复合索引
    KEY `idx_status_create_time` (`status`, `create_time`), -- 复合索引
    KEY `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

#### 索引使用原则
```sql
-- 1. 最左前缀原则
-- 可以使用索引：WHERE dept_id = 1 AND status = '0'
-- 不能使用索引：WHERE status = '0' (dept_id缺失)

-- 2. 避免在索引列上使用函数
-- 错误：WHERE DATE(create_time) = '2024-01-01'
-- 正确：WHERE create_time >= '2024-01-01 00:00:00' AND create_time < '2024-01-02 00:00:00'

-- 3. 避免使用 != 或 <> 操作符
-- 错误：WHERE status != '0'
-- 正确：WHERE status IN ('1', '2', '3')

-- 4. 避免使用LIKE '%xxx' 模式
-- 错误：WHERE username LIKE '%admin'
-- 正确：WHERE username LIKE 'admin%'
```

### 3. 连接池优化

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import QueuePool

# 数据库连接池配置
engine = create_async_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    poolclass=QueuePool,
    pool_size=DB_POOL_SIZE,           # 连接池大小
    max_overflow=DB_MAX_OVERFLOW,     # 最大溢出连接数
    pool_recycle=DB_POOL_RECYCLE,     # 连接回收时间
    pool_timeout=DB_POOL_TIMEOUT,     # 连接超时时间
    pool_pre_ping=True,               # 连接前ping检查
    pool_reset_on_return='commit'     # 连接返回时重置
)

# 会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)
```

## 数据迁移

### 1. 版本管理

```python
# 数据库版本管理
class DatabaseMigration:
    """数据库迁移管理器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_version_table(self):
        """创建版本表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS `db_version` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `version` VARCHAR(50) NOT NULL,
            `description` VARCHAR(500),
            `applied_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            UNIQUE KEY `uk_version` (`version`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据库版本表';
        """
        await self.db.execute(text(create_table_sql))
        await self.db.commit()
    
    async def get_applied_versions(self) -> List[str]:
        """获取已应用的版本"""
        result = await self.db.execute(
            select(DbVersion.version).order_by(DbVersion.id)
        )
        return [row[0] for row in result.fetchall()]
    
    async def apply_migration(self, version: str, description: str, sql: str):
        """应用迁移"""
        try:
            # 执行SQL
            await self.db.execute(text(sql))
            
            # 记录版本
            version_record = DbVersion(version=version, description=description)
            self.db.add(version_record)
            await self.db.commit()
            
            logger.info(f"成功应用迁移版本: {version}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"应用迁移版本失败: {version}, 错误: {e}")
            raise
```

### 2. 迁移脚本示例

```python
# 迁移脚本
MIGRATIONS = [
    {
        "version": "1.0.0",
        "description": "初始化用户表",
        "sql": """
        CREATE TABLE `sys_user` (
            `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
            `username` VARCHAR(50) NOT NULL COMMENT '用户名',
            `password` VARCHAR(100) NOT NULL COMMENT '密码',
            `email` VARCHAR(100) COMMENT '邮箱',
            `status` CHAR(1) DEFAULT '0' COMMENT '状态',
            `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            PRIMARY KEY (`id`),
            UNIQUE KEY `uk_username` (`username`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
        """
    },
    {
        "version": "1.0.1",
        "description": "添加用户表索引",
        "sql": """
        ALTER TABLE `sys_user` 
        ADD KEY `idx_email` (`email`),
        ADD KEY `idx_create_time` (`create_time`);
        """
    }
]

# 执行迁移
async def run_migrations():
    """运行数据库迁移"""
    migration_manager = DatabaseMigration(db)
    
    # 创建版本表
    await migration_manager.create_version_table()
    
    # 获取已应用版本
    applied_versions = await migration_manager.get_applied_versions()
    
    # 应用未应用的迁移
    for migration in MIGRATIONS:
        if migration["version"] not in applied_versions:
            await migration_manager.apply_migration(
                migration["version"],
                migration["description"],
                migration["sql"]
            )
```

## 数据备份与恢复

### 1. 备份策略

```python
import subprocess
import os
from datetime import datetime

class DatabaseBackup:
    """数据库备份管理器"""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.backup_dir = "backups"
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    async def backup_mysql(self) -> str:
        """MySQL数据库备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.backup_dir}/mysql_backup_{timestamp}.sql"
        
        # MySQL备份命令
        cmd = [
            "mysqldump",
            f"--host={self.db_config['host']}",
            f"--port={self.db_config['port']}",
            f"--user={self.db_config['username']}",
            f"--password={self.db_config['password']}",
            "--single-transaction",
            "--routines",
            "--triggers",
            self.db_config['database'],
            ">", backup_file
        ]
        
        try:
            subprocess.run(cmd, shell=True, check=True)
            logger.info(f"MySQL备份成功: {backup_file}")
            return backup_file
        except subprocess.CalledProcessError as e:
            logger.error(f"MySQL备份失败: {e}")
            raise
    
    async def backup_postgresql(self) -> str:
        """PostgreSQL数据库备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.backup_dir}/postgresql_backup_{timestamp}.sql"
        
        # PostgreSQL备份命令
        cmd = [
            "pg_dump",
            f"--host={self.db_config['host']}",
            f"--port={self.db_config['port']}",
            f"--username={self.db_config['username']}",
            f"--dbname={self.db_config['database']}",
            "--no-password",
            "--verbose",
            "--clean",
            "--no-owner",
            f"--file={backup_file}"
        ]
        
        # 设置环境变量
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']
        
        try:
            subprocess.run(cmd, env=env, check=True)
            logger.info(f"PostgreSQL备份成功: {backup_file}")
            return backup_file
        except subprocess.CalledProcessError as e:
            logger.error(f"PostgreSQL备份失败: {e}")
            raise
```

### 2. 恢复策略

```python
class DatabaseRestore:
    """数据库恢复管理器"""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
    
    async def restore_mysql(self, backup_file: str):
        """MySQL数据库恢复"""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"备份文件不存在: {backup_file}")
        
        # MySQL恢复命令
        cmd = [
            "mysql",
            f"--host={self.db_config['host']}",
            f"--port={self.db_config['port']}",
            f"--user={self.db_config['username']}",
            f"--password={self.db_config['password']}",
            self.db_config['database'],
            "<", backup_file
        ]
        
        try:
            subprocess.run(cmd, shell=True, check=True)
            logger.info(f"MySQL恢复成功: {backup_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"MySQL恢复失败: {e}")
            raise
    
    async def restore_postgresql(self, backup_file: str):
        """PostgreSQL数据库恢复"""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"备份文件不存在: {backup_file}")
        
        # PostgreSQL恢复命令
        cmd = [
            "psql",
            f"--host={self.db_config['host']}",
            f"--port={self.db_config['port']}",
            f"--username={self.db_config['username']}",
            f"--dbname={self.db_config['database']}",
            "--no-password",
            "--verbose",
            f"--file={backup_file}"
        ]
        
        # 设置环境变量
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']
        
        try:
            subprocess.run(cmd, env=env, check=True)
            logger.info(f"PostgreSQL恢复成功: {backup_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"PostgreSQL恢复失败: {e}")
            raise
```

## 监控与维护

### 1. 性能监控

```python
import time
from functools import wraps

def monitor_query_performance(func):
    """查询性能监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 记录慢查询
            if execution_time > 1.0:  # 超过1秒的查询
                logger.warning(f"慢查询检测: {func.__name__}, 执行时间: {execution_time:.3f}秒")
            
            # 记录查询统计
            logger.info(f"查询执行: {func.__name__}, 执行时间: {execution_time:.3f}秒")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"查询异常: {func.__name__}, 执行时间: {execution_time:.3f}秒, 错误: {e}")
            raise
    
    return wrapper

# 使用示例
@monitor_query_performance
async def get_user_by_id(self, user_id: int) -> Optional[UserDO]:
    """根据ID获取用户（带性能监控）"""
    result = await self.db.execute(
        select(UserDO).where(UserDO.id == user_id)
    )
    return result.scalar_one_or_none()
```

### 2. 连接池监控

```python
class ConnectionPoolMonitor:
    """连接池监控器"""
    
    def __init__(self, engine):
        self.engine = engine
    
    def get_pool_status(self) -> dict:
        """获取连接池状态"""
        pool = self.engine.pool
        
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
    
    def log_pool_status(self):
        """记录连接池状态"""
        status = self.get_pool_status()
        logger.info(f"连接池状态: {status}")
        
        # 检查连接池健康状态
        if status["checked_out"] > status["pool_size"] * 0.8:
            logger.warning("连接池使用率过高，可能存在连接泄漏")
        
        if status["invalid"] > 0:
            logger.warning(f"检测到 {status['invalid']} 个无效连接")
```

## 最佳实践

### 1. 查询优化原则
- 使用索引优化查询性能
- 避免SELECT *，只查询需要的字段
- 使用分页查询避免大量数据返回
- 合理使用JOIN，避免N+1查询
- 使用EXPLAIN分析查询执行计划

### 2. 事务管理原则
- 事务范围要小，避免长事务
- 合理设置事务隔离级别
- 及时提交或回滚事务
- 避免在事务中进行耗时操作

### 3. 连接池管理原则
- 根据并发量合理设置连接池大小
- 定期监控连接池状态
- 及时处理连接泄漏问题
- 使用连接池预热提高性能

### 4. 数据安全原则
- 定期备份数据库
- 实施数据加密策略
- 控制数据库访问权限
- 记录数据库操作日志

---

**注意**: 本文档会持续更新，请关注最新版本。如有问题，请通过 Issues 反馈。 