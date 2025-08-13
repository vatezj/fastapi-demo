# 系统架构设计

## 概述

本文档描述了 RuoYi-FastAPI 项目的系统架构设计，包括整体架构、模块设计、技术选型等。

## 整体架构

### 1. 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                       前端层 (Vue3)                          │
├─────────────────────────────────────────────────────────────┤
│                       网关层 (Nginx)                        │
├─────────────────────────────────────────────────────────────┤
│                    API 网关 (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│                    应用层 (Application)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  用户管理   │ │  系统管理   │ │  业务模块   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    服务层 (Service)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  业务逻辑   │ │  事务管理   │ │  缓存管理   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    数据访问层 (DAO)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  数据查询   │ │  数据操作   │ │  数据转换   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    数据存储层 (Storage)                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   MySQL    │ │    Redis    │ │  文件存储   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 2. 分层架构设计

#### 表现层 (Presentation Layer)
- **职责**: 处理HTTP请求，参数验证，响应格式化
- **组件**: FastAPI 路由、中间件、异常处理器
- **特点**: 无状态、可扩展、支持异步

#### 应用层 (Application Layer)
- **职责**: 业务流程编排，事务管理，服务协调
- **组件**: 业务服务、应用服务、工作流引擎
- **特点**: 业务逻辑集中、事务边界清晰

#### 领域层 (Domain Layer)
- **职责**: 核心业务规则，领域模型，业务实体
- **组件**: 领域服务、领域事件、业务规则
- **特点**: 业务核心、规则稳定、技术无关

#### 基础设施层 (Infrastructure Layer)
- **职责**: 数据持久化，外部服务集成，技术实现
- **组件**: 数据访问对象、外部API客户端、消息队列
- **特点**: 技术实现、可替换、配置化

## 核心模块设计

### 1. 用户权限模块

```python
# 模块结构
module_admin/
├── controller/
│   ├── user_controller.py      # 用户管理控制器
│   ├── role_controller.py      # 角色管理控制器
│   ├── menu_controller.py      # 菜单管理控制器
│   └── dept_controller.py      # 部门管理控制器
├── service/
│   ├── user_service.py         # 用户业务逻辑
│   ├── role_service.py         # 角色业务逻辑
│   ├── menu_service.py         # 菜单业务逻辑
│   └── dept_service.py         # 部门业务逻辑
├── dao/
│   ├── user_dao.py             # 用户数据访问
│   ├── role_dao.py             # 角色数据访问
│   ├── menu_dao.py             # 菜单数据访问
│   └── dept_dao.py             # 部门数据访问
└── entity/
    ├── do/                     # 数据对象
    └── vo/                     # 视图对象
```

#### 权限控制流程
```
用户请求 → 认证中间件 → 权限验证 → 数据权限 → 业务处理 → 响应返回
    ↓           ↓         ↓         ↓         ↓         ↓
  JWT验证    Token解析   接口权限   数据范围   业务逻辑   结果返回
```

### 2. 系统管理模块

```python
# 模块结构
module_admin/
├── controller/
│   ├── config_controller.py    # 系统配置控制器
│   ├── dict_controller.py      # 字典管理控制器
│   ├── notice_controller.py    # 通知公告控制器
│   └── log_controller.py       # 日志管理控制器
├── service/
│   ├── config_service.py       # 配置管理服务
│   ├── dict_service.py         # 字典管理服务
│   ├── notice_service.py       # 通知公告服务
│   └── log_service.py          # 日志管理服务
└── dao/
    ├── config_dao.py           # 配置数据访问
    ├── dict_dao.py             # 字典数据访问
    ├── notice_dao.py           # 通知公告数据访问
    └── log_dao.py              # 日志数据访问
```

### 3. 代码生成模块

```python
# 模块结构
module_generator/
├── controller/
│   └── gen_controller.py       # 代码生成控制器
├── service/
│   └── gen_service.py          # 代码生成服务
├── dao/
│   └── gen_dao.py              # 代码生成数据访问
└── templates/                   # 代码模板
    ├── python/                  # Python代码模板
    ├── vue/                     # Vue前端模板
    ├── sql/                     # SQL脚本模板
    └── js/                      # JavaScript API模板
```

#### 代码生成流程
```
数据库表 → 表结构分析 → 模板渲染 → 代码生成 → 文件输出
    ↓         ↓         ↓         ↓         ↓
  元数据    字段信息    变量替换    代码生成    文件保存
```

### 4. 定时任务模块

```python
# 模块结构
module_task/
├── __init__.py
├── scheduler_test.py            # 定时任务测试
└── tasks/                       # 任务定义
    ├── __init__.py
    ├── system_tasks.py          # 系统任务
    └── business_tasks.py        # 业务任务
```

## 技术架构

### 1. 异步架构

#### 异步处理流程
```python
# 异步请求处理
async def handle_request():
    # 1. 接收请求
    request_data = await receive_request()
    
    # 2. 并行处理多个任务
    user_task = asyncio.create_task(get_user_info())
    role_task = asyncio.create_task(get_role_info())
    dept_task = asyncio.create_task(get_dept_info())
    
    # 3. 等待所有任务完成
    user_info, role_info, dept_info = await asyncio.gather(
        user_task, role_task, dept_task
    )
    
    # 4. 返回结果
    return combine_results(user_info, role_info, dept_info)
```

#### 异步数据库操作
```python
# 异步数据库连接池
class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.session_factory = None
    
    async def init_database(self):
        """初始化数据库连接"""
        self.engine = create_async_engine(
            DATABASE_URL,
            echo=DB_ECHO,
            pool_size=DB_POOL_SIZE,
            max_overflow=DB_MAX_OVERFLOW,
            pool_recycle=DB_POOL_RECYCLE,
            pool_timeout=DB_POOL_TIMEOUT
        )
        
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        async with self.session_factory() as session:
            yield session
```

### 2. 缓存架构

#### 缓存层次结构
```
应用层缓存 → Redis缓存 → 数据库
    ↓           ↓         ↓
  内存缓存   分布式缓存   持久化存储
```

#### 缓存策略
```python
# 缓存装饰器
def cache(expire: int = 300, key_prefix: str = ""):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            await redis_client.setex(
                cache_key, 
                expire, 
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator
```

### 3. 安全架构

#### 认证流程
```
用户登录 → 验证凭据 → 生成JWT → 返回Token → 后续请求携带Token
    ↓         ↓         ↓         ↓              ↓
  用户名密码   数据库验证   签名加密   客户端存储     中间件验证
```

#### 权限控制
```python
# 权限验证装饰器
def require_permissions(permissions: List[str]):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 获取当前用户
            current_user = get_current_user()
            
            # 检查用户权限
            user_permissions = await get_user_permissions(current_user.id)
            
            # 验证权限
            for permission in permissions:
                if permission not in user_permissions:
                    raise PermissionException(f"缺少权限: {permission}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 数据权限控制
def require_data_scope(scope_type: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 获取当前用户
            current_user = get_current_user()
            
            # 获取数据权限范围
            data_scope = await get_user_data_scope(current_user.id, scope_type)
            
            # 注入数据权限条件
            kwargs['data_scope'] = data_scope
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## 数据架构

### 1. 数据库设计

#### 核心表结构
```sql
-- 用户表
CREATE TABLE sys_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    email VARCHAR(100) COMMENT '邮箱',
    phone VARCHAR(11) COMMENT '手机号',
    status CHAR(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
    dept_id BIGINT COMMENT '部门ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark VARCHAR(500) COMMENT '备注'
);

-- 角色表
CREATE TABLE sys_role (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '角色ID',
    role_name VARCHAR(50) NOT NULL COMMENT '角色名称',
    role_key VARCHAR(50) NOT NULL UNIQUE COMMENT '角色权限字符串',
    sort_order INT DEFAULT 0 COMMENT '显示顺序',
    status CHAR(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark VARCHAR(500) COMMENT '备注'
);

-- 菜单表
CREATE TABLE sys_menu (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '菜单ID',
    menu_name VARCHAR(50) NOT NULL COMMENT '菜单名称',
    parent_id BIGINT DEFAULT 0 COMMENT '父菜单ID',
    order_num INT DEFAULT 0 COMMENT '显示顺序',
    path VARCHAR(200) COMMENT '路由地址',
    component VARCHAR(255) COMMENT '组件路径',
    is_frame TINYINT DEFAULT 1 COMMENT '是否为外链（0是 1否）',
    menu_type CHAR(1) COMMENT '菜单类型（M目录 C菜单 F按钮）',
    visible CHAR(1) DEFAULT '0' COMMENT '菜单状态（0显示 1隐藏）',
    perms VARCHAR(100) COMMENT '权限标识',
    icon VARCHAR(100) COMMENT '菜单图标',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark VARCHAR(500) COMMENT '备注'
);
```

#### 表关系设计
```
sys_user (用户表)
    ↓ (多对多)
sys_user_role (用户角色关联表)
    ↓ (多对多)
sys_role (角色表)
    ↓ (多对多)
sys_role_menu (角色菜单关联表)
    ↓ (多对多)
sys_menu (菜单表)

sys_dept (部门表)
    ↓ (一对多)
sys_user (用户表)
```

### 2. 数据访问模式

#### Repository模式
```python
# 基础Repository接口
class BaseRepository(Generic[T]):
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
    
    async def create(self, entity: T) -> T:
        """创建实体"""
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity
    
    async def update(self, entity: T) -> T:
        """更新实体"""
        await self.db.commit()
        await self.db.refresh(entity)
        return entity
    
    async def delete(self, entity: T) -> None:
        """删除实体"""
        await self.db.delete(entity)
        await self.db.commit()

# 具体Repository实现
class UserRepository(BaseRepository[UserDO]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserDO, db)
    
    async def get_by_username(self, username: str) -> Optional[UserDO]:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(UserDO).where(UserDO.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_dept_id(self, dept_id: int) -> List[UserDO]:
        """根据部门ID获取用户列表"""
        result = await self.db.execute(
            select(UserDO).where(UserDO.dept_id == dept_id)
        )
        return result.scalars().all()
```

## 部署架构

### 1. 单机部署

```
┌─────────────────────────────────────┐
│              Nginx                  │
│         (反向代理/负载均衡)           │
├─────────────────────────────────────┤
│           FastAPI 应用              │
│         (多进程/多线程)              │
├─────────────────────────────────────┤
│              MySQL                  │
│              Redis                  │
└─────────────────────────────────────┘
```

### 2. 集群部署

```
┌─────────────────────────────────────┐
│              Nginx                  │
│         (反向代理/负载均衡)           │
├─────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐   │
│  │ FastAPI 1   │ │ FastAPI 2   │   │
│  │  (进程1)    │ │  (进程2)    │   │
│  └─────────────┘ └─────────────┘   │
├─────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐   │
│  │   MySQL     │ │    Redis    │   │
│  │  (主从)     │ │   (集群)    │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

### 3. 容器化部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "9099:9099"
    environment:
      - DB_HOST=mysql
      - REDIS_HOST=redis
    depends_on:
      - mysql
      - redis
    networks:
      - app-network

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: ruoyi-fastapi
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - app-network

  redis:
    image: redis:7.0
    volumes:
      - redis-data:/data
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
    networks:
      - app-network

volumes:
  mysql-data:
  redis-data:

networks:
  app-network:
    driver: bridge
```

## 性能架构

### 1. 性能优化策略

#### 数据库优化
- 使用连接池管理数据库连接
- 实现读写分离
- 合理使用索引
- 优化SQL查询语句

#### 缓存优化
- 实现多级缓存
- 使用缓存预热
- 实现缓存穿透防护
- 合理设置过期时间

#### 异步优化
- 使用异步数据库操作
- 实现异步任务处理
- 使用异步HTTP客户端
- 实现并发控制

### 2. 监控指标

#### 系统指标
- CPU使用率
- 内存使用率
- 磁盘I/O
- 网络I/O

#### 应用指标
- 响应时间
- 吞吐量
- 错误率
- 并发数

#### 业务指标
- 用户活跃度
- 业务处理量
- 数据增长量
- 系统可用性

## 扩展架构

### 1. 微服务架构

```
┌─────────────────────────────────────┐
│              API 网关               │
├─────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐   │
│  │  用户服务   │ │  订单服务   │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │  商品服务   │ │  支付服务   │   │
│  └─────────────┘ └─────────────┘   │
├─────────────────────────────────────┤
│             消息队列                 │
├─────────────────────────────────────┤
│             配置中心                 │
└─────────────────────────────────────┘
```

### 2. 事件驱动架构

```python
# 事件发布
class EventPublisher:
    async def publish(self, event: BaseEvent):
        """发布事件"""
        # 发布到消息队列
        await self.message_queue.publish(event)
        
        # 本地事件处理
        await self.local_event_handler.handle(event)

# 事件订阅
class EventSubscriber:
    async def subscribe(self, event_type: str, handler: EventHandler):
        """订阅事件"""
        await self.message_queue.subscribe(event_type, handler)
    
    async def handle_event(self, event: BaseEvent):
        """处理事件"""
        handler = self.get_handler(event.type)
        if handler:
            await handler.handle(event)
```

## 总结

RuoYi-FastAPI 采用分层架构设计，具有以下特点：

1. **清晰的分层结构**: 表现层、应用层、领域层、基础设施层职责明确
2. **异步处理能力**: 支持高并发、高性能的异步处理
3. **模块化设计**: 功能模块独立，便于维护和扩展
4. **安全可靠**: 完善的权限控制和数据安全机制
5. **易于扩展**: 支持微服务架构和事件驱动架构
6. **性能优化**: 多级缓存、连接池、异步处理等优化策略

这种架构设计使得系统具有良好的可维护性、可扩展性和性能表现。 