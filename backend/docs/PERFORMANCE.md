# 性能优化指南

## 概述

本文档描述了 RuoYi-FastAPI 项目的性能优化策略，包括数据库优化、缓存优化、异步处理等。

## 性能分析

### 1. 性能指标

```python
# 关键性能指标
PERFORMANCE_METRICS = {
    "response_time": {
        "p50": "< 100ms",    # 50%请求响应时间
        "p95": "< 200ms",    # 95%请求响应时间
        "p99": "< 500ms"     # 99%请求响应时间
    },
    "throughput": {
        "requests_per_second": "> 1000",  # 每秒请求数
        "concurrent_users": "> 100"       # 并发用户数
    },
    "resource_usage": {
        "cpu_usage": "< 70%",     # CPU使用率
        "memory_usage": "< 80%",  # 内存使用率
        "disk_io": "< 80%"        # 磁盘I/O使用率
    }
}
```

### 2. 性能监控

```python
import time
import psutil
from functools import wraps
from typing import Callable, Any

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
    
    def monitor_function(self, func_name: str = None):
        """函数性能监控装饰器"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                start_cpu = psutil.cpu_percent()
                start_memory = psutil.virtual_memory().used
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    end_cpu = psutil.cpu_percent()
                    end_memory = psutil.virtual_memory().used
                    
                    self.record_metrics(
                        func_name or func.__name__,
                        execution_time,
                        end_cpu - start_cpu,
                        end_memory - start_memory
                    )
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                start_cpu = psutil.cpu_percent()
                start_memory = psutil.virtual_memory().used
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    end_cpu = psutil.cpu_percent()
                    end_memory = psutil.virtual_memory().used
                    
                    self.record_metrics(
                        func_name or func.__name__,
                        execution_time,
                        end_cpu - start_cpu,
                        end_memory - start_memory
                    )
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def record_metrics(self, func_name: str, execution_time: float, 
                       cpu_delta: float, memory_delta: int):
        """记录性能指标"""
        if func_name not in self.metrics:
            self.metrics[func_name] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'avg_time': 0,
                'total_cpu': 0,
                'total_memory': 0
            }
        
        metrics = self.metrics[func_name]
        metrics['count'] += 1
        metrics['total_time'] += execution_time
        metrics['min_time'] = min(metrics['min_time'], execution_time)
        metrics['max_time'] = max(metrics['max_time'], execution_time)
        metrics['avg_time'] = metrics['total_time'] / metrics['count']
        metrics['total_cpu'] += cpu_delta
        metrics['total_memory'] += memory_delta
    
    def get_performance_report(self) -> dict:
        """获取性能报告"""
        return self.metrics

# 使用示例
performance_monitor = PerformanceMonitor()

@performance_monitor.monitor_function("get_user_list")
async def get_user_list():
    """获取用户列表（带性能监控）"""
    await asyncio.sleep(0.1)  # 模拟业务逻辑
    return ["user1", "user2", "user3"]
```

## 数据库优化

### 1. 查询优化

#### 避免N+1查询
```python
# 错误的做法：N+1查询
async def get_users_with_roles_bad():
    """获取用户列表（包含角色信息）- 错误做法"""
    users = await user_dao.get_all()
    
    # 这里会导致N+1查询问题
    for user in users:
        user.roles = await role_dao.get_roles_by_user_id(user.id)
    
    return users

# 正确的做法：使用JOIN查询
async def get_users_with_roles_good():
    """获取用户列表（包含角色信息）- 正确做法"""
    query = (
        select(UserDO)
        .options(selectinload(UserDO.roles))
        .options(selectinload(UserDO.dept))
    )
    
    result = await db.execute(query)
    return result.scalars().all()

# 使用原生SQL优化复杂查询
async def get_users_with_complex_info():
    """获取用户复杂信息（使用原生SQL）"""
    sql = """
    SELECT 
        u.id,
        u.username,
        u.email,
        u.status,
        d.dept_name,
        GROUP_CONCAT(r.role_name) as role_names
    FROM sys_user u
    LEFT JOIN sys_dept d ON u.dept_id = d.id
    LEFT JOIN sys_user_role ur ON u.id = ur.user_id
    LEFT JOIN sys_role r ON ur.role_id = r.id
    WHERE u.status = '0'
    GROUP BY u.id
    ORDER BY u.create_time DESC
    """
    
    result = await db.execute(text(sql))
    return result.fetchall()
```

#### 分页查询优化
```python
async def get_user_page_optimized(page_query, **kwargs):
    """优化的分页查询"""
    # 使用子查询优化COUNT
    subquery = (
        select(UserDO.id)
        .where(*[getattr(UserDO, key) == value 
                for key, value in kwargs.items() if value is not None])
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

# 使用游标分页（适用于大数据量）
async def get_user_page_cursor(cursor: str = None, limit: int = 20):
    """游标分页查询"""
    if cursor:
        # 使用游标查询下一页
        query = (
            select(UserDO)
            .where(UserDO.id > int(cursor))
            .order_by(UserDO.id)
            .limit(limit)
        )
    else:
        # 查询第一页
        query = (
            select(UserDO)
            .order_by(UserDO.id)
            .limit(limit)
        )
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # 返回下一页游标
    next_cursor = str(users[-1].id) if users else None
    
    return {
        'users': users,
        'next_cursor': next_cursor,
        'has_more': len(users) == limit
    }
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
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_dept_status` (`dept_id`, `status`),           -- 复合索引
    KEY `idx_status_create_time` (`status`, `create_time`), -- 复合索引
    KEY `idx_email` (`email`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 角色表索引
CREATE TABLE `sys_role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `role_name` VARCHAR(50) NOT NULL,
    `role_key` VARCHAR(50) NOT NULL,
    `sort_order` INT DEFAULT 0,
    `status` CHAR(1) DEFAULT '0',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_key` (`role_key`),
    KEY `idx_status_sort` (`status`, `sort_order`),        -- 复合索引
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';
```

#### 索引使用分析
```sql
-- 使用EXPLAIN分析查询计划
EXPLAIN SELECT * FROM sys_user 
WHERE dept_id = 1 AND status = '0' 
ORDER BY create_time DESC;

-- 分析结果示例
-- id: 1
-- select_type: SIMPLE
-- table: sys_user
-- type: ref
-- possible_keys: idx_dept_status,idx_status_create_time
-- key: idx_dept_status
-- key_len: 9
-- ref: const,const
-- rows: 10
-- Extra: Using where; Using filesort

-- 优化建议：添加复合索引 (dept_id, status, create_time)
ALTER TABLE sys_user ADD KEY `idx_dept_status_time` (`dept_id`, `status`, `create_time`);
```

### 3. 连接池优化

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import QueuePool

# 数据库连接池配置
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 生产环境关闭SQL日志
    poolclass=QueuePool,
    pool_size=20,              # 连接池大小
    max_overflow=30,           # 最大溢出连接数
    pool_recycle=3600,         # 连接回收时间（秒）
    pool_timeout=30,           # 连接超时时间（秒）
    pool_pre_ping=True,        # 连接前ping检查
    pool_reset_on_return='commit',  # 连接返回时重置
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False
    }
)

# 会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 连接池监控
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

## 缓存优化

### 1. Redis缓存策略

#### 多级缓存
```python
import asyncio
from typing import Any, Optional
import json

class MultiLevelCache:
    """多级缓存管理器"""
    
    def __init__(self, redis_client, local_cache_size=1000):
        self.redis = redis_client
        self.local_cache = {}
        self.local_cache_size = local_cache_size
        self.cache_hits = 0
        self.cache_misses = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        # 第一级：本地缓存
        if key in self.local_cache:
            self.cache_hits += 1
            return self.local_cache[key]
        
        # 第二级：Redis缓存
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                data = json.loads(cached_data)
                # 更新本地缓存
                self._update_local_cache(key, data)
                self.cache_hits += 1
                return data
        except Exception as e:
            logger.error(f"Redis缓存获取失败: {e}")
        
        self.cache_misses += 1
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        """设置缓存数据"""
        try:
            # 设置Redis缓存
            await self.redis.setex(key, expire, json.dumps(value))
            
            # 更新本地缓存
            self._update_local_cache(key, value)
        except Exception as e:
            logger.error(f"Redis缓存设置失败: {e}")
    
    def _update_local_cache(self, key: str, value: Any):
        """更新本地缓存"""
        # 如果本地缓存已满，删除最旧的条目
        if len(self.local_cache) >= self.local_cache_size:
            oldest_key = next(iter(self.local_cache))
            del self.local_cache[oldest_key]
        
        self.local_cache[key] = value
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            "local_cache_size": len(self.local_cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": f"{hit_rate:.2%}"
        }

# 使用示例
cache_manager = MultiLevelCache(redis_client)

@cache_manager.cache(expire=300)
async def get_user_by_id(user_id: int) -> Optional[UserDO]:
    """根据ID获取用户（带缓存）"""
    user = await user_dao.get_by_id(user_id)
    return UserDO.from_orm(user) if user else None
```

#### 缓存装饰器
```python
def cache(expire: int = 300, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            await cache_manager.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator

# 使用示例
@cache(expire=600, key_prefix="user")
async def get_user_permissions(user_id: int) -> List[str]:
    """获取用户权限（带缓存）"""
    user_roles = await role_dao.get_roles_by_user_id(user_id)
    
    permissions = []
    for role in user_roles:
        role_permissions = await get_role_permissions(role.id)
        permissions.extend(role_permissions)
    
    return list(set(permissions))
```

### 2. 缓存更新策略

```python
class CacheUpdateStrategy:
    """缓存更新策略"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
    
    async def update_user_cache(self, user_id: int):
        """更新用户相关缓存"""
        # 清除用户基本信息缓存
        await self.cache_manager.delete(f"user:info:{user_id}")
        
        # 清除用户权限缓存
        await self.cache_manager.delete(f"user:permissions:{user_id}")
        
        # 清除用户菜单缓存
        await self.cache_manager.delete(f"user:menus:{user_id}")
        
        # 清除用户列表缓存
        await self.cache_manager.delete_pattern("user:list:*")
    
    async def update_role_cache(self, role_id: int):
        """更新角色相关缓存"""
        # 清除角色权限缓存
        await self.cache_manager.delete(f"role:permissions:{role_id}")
        
        # 清除所有用户的权限缓存（因为角色变更会影响用户权限）
        await self.cache_manager.delete_pattern("user:permissions:*")
        
        # 清除所有用户的菜单缓存
        await self.cache_manager.delete_pattern("user:menus:*")
    
    async def update_menu_cache(self, menu_id: int):
        """更新菜单相关缓存"""
        # 清除所有用户的菜单缓存
        await self.cache_manager.delete_pattern("user:menus:*")
        
        # 清除菜单树缓存
        await self.cache_manager.delete("menu:tree")
    
    async def clear_all_cache(self):
        """清除所有缓存"""
        await self.cache_manager.delete_pattern("*")

# 使用示例
cache_strategy = CacheUpdateStrategy(cache_manager)

async def update_user(user_id: int, user_data: dict):
    """更新用户信息"""
    # 更新数据库
    updated_user = await user_service.update_user(user_id, user_data)
    
    # 更新相关缓存
    await cache_strategy.update_user_cache(user_id)
    
    return updated_user
```

## 异步处理优化

### 1. 异步任务处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Any, Callable

class AsyncTaskProcessor:
    """异步任务处理器"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_tasks_concurrently(self, tasks: List[Callable], *args, **kwargs) -> List[Any]:
        """并发处理任务"""
        # 创建异步任务
        async_tasks = []
        for task in tasks:
            if asyncio.iscoroutinefunction(task):
                # 异步函数
                async_tasks.append(task(*args, **kwargs))
            else:
                # 同步函数，在线程池中执行
                loop = asyncio.get_event_loop()
                async_tasks.append(loop.run_in_executor(self.thread_pool, task, *args, **kwargs))
        
        # 并发执行所有任务
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"任务 {i} 执行失败: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def process_tasks_with_semaphore(self, tasks: List[Callable], 
                                         max_concurrent: int = 5, *args, **kwargs) -> List[Any]:
        """使用信号量控制并发数"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(task):
            async with semaphore:
                if asyncio.iscoroutinefunction(task):
                    return await task(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(self.thread_pool, task, *args, **kwargs)
        
        # 创建任务
        async_tasks = [process_with_semaphore(task) for task in tasks]
        
        # 执行任务
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        return results
    
    async def process_tasks_batch(self, tasks: List[Callable], 
                                 batch_size: int = 10, *args, **kwargs) -> List[Any]:
        """分批处理任务"""
        all_results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await self.process_tasks_concurrently(batch, *args, **kwargs)
            all_results.extend(batch_results)
            
            # 批次间延迟，避免过载
            if i + batch_size < len(tasks):
                await asyncio.sleep(0.1)
        
        return all_results

# 使用示例
task_processor = AsyncTaskProcessor(max_workers=20)

async def process_user_batch(user_ids: List[int]):
    """批量处理用户数据"""
    # 定义任务列表
    tasks = [
        lambda user_id: process_single_user(user_id),
        lambda user_id: update_user_statistics(user_id),
        lambda user_id: send_notification(user_id)
    ]
    
    # 并发处理所有用户
    results = await task_processor.process_tasks_with_semaphore(
        tasks, max_concurrent=5, user_ids=user_ids
    )
    
    return results
```

### 2. 异步队列处理

```python
import asyncio
from asyncio import Queue
from typing import Any, Callable
import time

class AsyncQueueProcessor:
    """异步队列处理器"""
    
    def __init__(self, max_workers: int = 10, max_queue_size: int = 1000):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.queue = Queue(maxsize=max_queue_size)
        self.workers = []
        self.running = False
    
    async def start_workers(self):
        """启动工作线程"""
        self.running = True
        
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"启动了 {self.max_workers} 个工作线程")
    
    async def stop_workers(self):
        """停止工作线程"""
        self.running = False
        
        # 等待所有工作线程完成
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
            self.workers.clear()
        
        logger.info("所有工作线程已停止")
    
    async def _worker(self, worker_name: str):
        """工作线程函数"""
        while self.running:
            try:
                # 从队列获取任务
                task_data = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                if task_data is None:  # 停止信号
                    break
                
                # 处理任务
                await self._process_task(task_data)
                
                # 标记任务完成
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"工作线程 {worker_name} 处理任务失败: {e}")
    
    async def _process_task(self, task_data: dict):
        """处理单个任务"""
        try:
            task_func = task_data['func']
            args = task_data.get('args', [])
            kwargs = task_data.get('kwargs', {})
            
            start_time = time.time()
            
            if asyncio.iscoroutinefunction(task_func):
                result = await task_func(*args, **kwargs)
            else:
                result = task_func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            logger.info(f"任务执行完成，耗时: {execution_time:.2f}秒")
            
            return result
            
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            raise
    