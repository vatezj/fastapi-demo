# 定时任务开发指南

## 概述

本文档描述了 RuoYi-FastAPI 项目的定时任务系统，包括任务调度、任务管理、监控等核心功能。

## 定时任务架构

### 1. 系统架构

```
┌─────────────────────────────────────┐
│           任务调度器                │
│         (APScheduler)               │
├─────────────────────────────────────┤
│           任务管理器                │
│      (任务注册、删除、修改)          │
├─────────────────────────────────────┤
│           任务执行器                │
│      (异步执行、异常处理)            │
├─────────────────────────────────────┤
│           任务存储                  │
│      (数据库 + Redis)               │
└─────────────────────────────────────┤
```

### 2. 核心组件

```python
# 任务调度器配置
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

class SchedulerManager:
    """任务调度管理器"""
    
    def __init__(self):
        # 任务存储配置
        jobstores = {
            'default': SQLAlchemyJobStore(url=DATABASE_URL)
        }
        
        # 执行器配置
        executors = {
            'default': AsyncIOExecutor()
        }
        
        # 调度器配置
        job_defaults = {
            'coalesce': False,      # 是否合并执行
            'max_instances': 3,     # 最大实例数
            'misfire_grace_time': 15  # 错过执行时间容忍度
        }
        
        # 创建调度器
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Shanghai'
        )
```

## 任务类型

### 1. Cron 任务

```python
# Cron表达式格式
# 秒 分 时 日 月 周
# * * * * * *

# 常用Cron表达式示例
CRON_EXAMPLES = {
    "每天凌晨2点执行": "0 0 2 * * *",
    "每周一上午9点执行": "0 0 9 * * 1",
    "每月1号中午12点执行": "0 0 12 1 * *",
    "每5分钟执行一次": "0 */5 * * * *",
    "每小时执行一次": "0 0 * * * *"
}

# Cron任务示例
@scheduler.scheduled_job('cron', hour=2, minute=0)
async def daily_cleanup_task():
    """每日清理任务"""
    logger.info("开始执行每日清理任务")
    try:
        # 清理过期数据
        await cleanup_expired_data()
        # 清理日志文件
        await cleanup_log_files()
        logger.info("每日清理任务执行完成")
    except Exception as e:
        logger.error(f"每日清理任务执行失败: {e}")
```

### 2. 间隔任务

```python
# 间隔任务示例
@scheduler.scheduled_job('interval', minutes=30)
async def health_check_task():
    """健康检查任务（每30分钟执行）"""
    logger.info("开始执行健康检查任务")
    try:
        # 检查数据库连接
        await check_database_health()
        # 检查Redis连接
        await check_redis_health()
        # 检查系统资源
        await check_system_resources()
        logger.info("健康检查任务执行完成")
    except Exception as e:
        logger.error(f"健康检查任务执行失败: {e}")

# 其他间隔配置
@scheduler.scheduled_job('interval', seconds=60)      # 每60秒
@scheduler.scheduled_job('interval', hours=2)         # 每2小时
@scheduler.scheduled_job('interval', days=1)          # 每1天
```

### 3. 一次性任务

```python
# 一次性任务示例
@scheduler.scheduled_job('date', run_date='2024-12-31 23:59:59')
async def year_end_task():
    """年末任务（2024年12月31日23:59:59执行）"""
    logger.info("开始执行年末任务")
    try:
        # 年度数据统计
        await generate_yearly_report()
        # 数据备份
        await backup_yearly_data()
        logger.info("年末任务执行完成")
    except Exception as e:
        logger.error(f"年末任务执行失败: {e}")

# 延迟执行任务
from datetime import datetime, timedelta

async def schedule_delayed_task(delay_seconds: int, task_func, *args, **kwargs):
    """调度延迟执行任务"""
    run_time = datetime.now() + timedelta(seconds=delay_seconds)
    
    scheduler.add_job(
        task_func,
        'date',
        run_date=run_time,
        args=args,
        kwargs=kwargs,
        id=f"delayed_task_{int(run_time.timestamp())}"
    )
    
    logger.info(f"延迟任务已调度，将在 {run_time} 执行")
```

## 任务管理

### 1. 任务注册

```python
class TaskRegistry:
    """任务注册器"""
    
    def __init__(self):
        self.scheduler = scheduler
        self.registered_tasks = {}
    
    def register_task(self, task_id: str, task_func, trigger_type: str, **trigger_args):
        """注册任务"""
        try:
            # 添加任务到调度器
            job = self.scheduler.add_job(
                task_func,
                trigger=trigger_type,
                id=task_id,
                **trigger_args
            )
            
            # 记录注册的任务
            self.registered_tasks[task_id] = {
                'job': job,
                'func': task_func,
                'trigger_type': trigger_type,
                'trigger_args': trigger_args
            }
            
            logger.info(f"任务注册成功: {task_id}")
            return job
            
        except Exception as e:
            logger.error(f"任务注册失败: {task_id}, 错误: {e}")
            raise
    
    def register_cron_task(self, task_id: str, task_func, cron_expression: str):
        """注册Cron任务"""
        # 解析Cron表达式
        cron_parts = cron_expression.split()
        if len(cron_parts) != 6:
            raise ValueError("Cron表达式格式错误，应为6个字段")
        
        second, minute, hour, day, month, day_of_week = cron_parts
        
        return self.register_task(
            task_id=task_id,
            task_func=task_func,
            trigger_type='cron',
            second=second,
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week
        )
    
    def register_interval_task(self, task_id: str, task_func, **interval_args):
        """注册间隔任务"""
        return self.register_task(
            task_id=task_id,
            task_func=task_func,
            trigger_type='interval',
            **interval_args
        )
    
    def register_date_task(self, task_id: str, task_func, run_date: datetime):
        """注册一次性任务"""
        return self.register_task(
            task_id=task_id,
            task_func=task_func,
            trigger_type='date',
            run_date=run_date
        )

# 使用示例
task_registry = TaskRegistry()

# 注册Cron任务
task_registry.register_cron_task(
    "daily_cleanup",
    daily_cleanup_task,
    "0 0 2 * * *"  # 每天凌晨2点
)

# 注册间隔任务
task_registry.register_interval_task(
    "health_check",
    health_check_task,
    minutes=30
)

# 注册一次性任务
task_registry.register_date_task(
    "year_end",
    year_end_task,
    datetime(2024, 12, 31, 23, 59, 59)
)
```

### 2. 任务控制

```python
class TaskController:
    """任务控制器"""
    
    def __init__(self):
        self.scheduler = scheduler
    
    def start_task(self, task_id: str):
        """启动任务"""
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                job.resume()
                logger.info(f"任务启动成功: {task_id}")
            else:
                logger.warning(f"任务不存在: {task_id}")
        except Exception as e:
            logger.error(f"任务启动失败: {task_id}, 错误: {e}")
    
    def stop_task(self, task_id: str):
        """停止任务"""
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                job.pause()
                logger.info(f"任务停止成功: {task_id}")
            else:
                logger.warning(f"任务不存在: {task_id}")
        except Exception as e:
            logger.error(f"任务停止失败: {task_id}, 错误: {e}")
    
    def remove_task(self, task_id: str):
        """移除任务"""
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                job.remove()
                logger.info(f"任务移除成功: {task_id}")
            else:
                logger.warning(f"任务不存在: {task_id}")
        except Exception as e:
            logger.error(f"任务移除失败: {task_id}, 错误: {e}")
    
    def modify_task(self, task_id: str, **trigger_args):
        """修改任务触发器"""
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                job.reschedule(**trigger_args)
                logger.info(f"任务修改成功: {task_id}")
            else:
                logger.warning(f"任务不存在: {task_id}")
        except Exception as e:
            logger.error(f"任务修改失败: {task_id}, 错误: {e}")
    
    def get_task_status(self, task_id: str) -> dict:
        """获取任务状态"""
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                return {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time,
                    'trigger': str(job.trigger),
                    'func_name': job.func.__name__,
                    'args': job.args,
                    'kwargs': job.kwargs
                }
            else:
                return None
        except Exception as e:
            logger.error(f"获取任务状态失败: {task_id}, 错误: {e}")
            return None
    
    def get_all_tasks(self) -> List[dict]:
        """获取所有任务"""
        try:
            jobs = self.scheduler.get_jobs()
            return [self.get_task_status(job.id) for job in jobs]
        except Exception as e:
            logger.error(f"获取所有任务失败: {e}")
            return []
```

### 3. 任务执行器

```python
class TaskExecutor:
    """任务执行器"""
    
    def __init__(self):
        self.scheduler = scheduler
    
    async def execute_task(self, task_func, *args, **kwargs):
        """执行任务"""
        task_id = f"task_{int(time.time())}"
        start_time = time.time()
        
        try:
            logger.info(f"开始执行任务: {task_id}")
            
            # 执行任务
            if asyncio.iscoroutinefunction(task_func):
                result = await task_func(*args, **kwargs)
            else:
                result = task_func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            logger.info(f"任务执行完成: {task_id}, 耗时: {execution_time:.2f}秒")
            
            # 记录执行日志
            await self.log_task_execution(task_id, task_func.__name__, True, execution_time, result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"任务执行失败: {task_id}, 错误: {e}, 耗时: {execution_time:.2f}秒")
            
            # 记录执行日志
            await self.log_task_execution(task_id, task_func.__name__, False, execution_time, str(e))
            
            raise
    
    async def log_task_execution(self, task_id: str, task_name: str, success: bool, 
                                execution_time: float, result: Any):
        """记录任务执行日志"""
        try:
            log_data = {
                'task_id': task_id,
                'task_name': task_name,
                'success': success,
                'execution_time': execution_time,
                'result': str(result) if result else None,
                'execution_time': datetime.now(),
                'create_time': datetime.now()
            }
            
            # 保存到数据库
            await self.save_task_log(log_data)
            
        except Exception as e:
            logger.error(f"记录任务执行日志失败: {e}")
    
    async def save_task_log(self, log_data: dict):
        """保存任务执行日志"""
        # 这里应该调用DAO层保存日志
        # 为了简化示例，直接打印
        logger.info(f"任务执行日志: {log_data}")
```

## 任务监控

### 1. 执行状态监控

```python
class TaskMonitor:
    """任务监控器"""
    
    def __init__(self):
        self.scheduler = scheduler
        self.monitoring = False
    
    def start_monitoring(self):
        """开始监控"""
        if not self.monitoring:
            self.scheduler.add_listener(self.task_listener, EVENT_ALL)
            self.monitoring = True
            logger.info("任务监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        if self.monitoring:
            self.scheduler.remove_listener(self.task_listener, EVENT_ALL)
            self.monitoring = False
            logger.info("任务监控已停止")
    
    def task_listener(self, event):
        """任务事件监听器"""
        if event.code == EVENT_JOB_EXECUTED:
            logger.info(f"任务执行成功: {event.job_id}")
            # 记录成功执行统计
            self.record_success_execution(event.job_id)
            
        elif event.code == EVENT_JOB_ERROR:
            logger.error(f"任务执行失败: {event.job_id}, 错误: {event.exception}")
            # 记录失败执行统计
            self.record_failed_execution(event.job_id, event.exception)
            
        elif event.code == EVENT_JOB_ADDED:
            logger.info(f"任务已添加: {event.job_id}")
            
        elif event.code == EVENT_JOB_REMOVED:
            logger.info(f"任务已移除: {event.job_id}")
            
        elif event.code == EVENT_JOB_MODIFIED:
            logger.info(f"任务已修改: {event.job_id}")
    
    def record_success_execution(self, job_id: str):
        """记录成功执行统计"""
        # 这里应该更新数据库中的统计信息
        logger.info(f"记录任务成功执行: {job_id}")
    
    def record_failed_execution(self, job_id: str, exception: Exception):
        """记录失败执行统计"""
        # 这里应该更新数据库中的统计信息
        logger.error(f"记录任务失败执行: {job_id}, 异常: {exception}")
```

### 2. 性能监控

```python
class TaskPerformanceMonitor:
    """任务性能监控器"""
    
    def __init__(self):
        self.execution_stats = {}
    
    def record_execution_time(self, task_id: str, execution_time: float):
        """记录任务执行时间"""
        if task_id not in self.execution_stats:
            self.execution_stats[task_id] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'avg_time': 0
            }
        
        stats = self.execution_stats[task_id]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['min_time'] = min(stats['min_time'], execution_time)
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['avg_time'] = stats['total_time'] / stats['count']
    
    def get_performance_report(self) -> dict:
        """获取性能报告"""
        report = {
            'total_tasks': len(self.execution_stats),
            'task_details': {}
        }
        
        for task_id, stats in self.execution_stats.items():
            report['task_details'][task_id] = {
                'execution_count': stats['count'],
                'total_execution_time': stats['total_time'],
                'min_execution_time': stats['min_time'],
                'max_execution_time': stats['max_time'],
                'avg_execution_time': stats['avg_time']
            }
        
        return report
    
    def get_slow_tasks(self, threshold: float = 1.0) -> List[dict]:
        """获取慢任务列表"""
        slow_tasks = []
        
        for task_id, stats in self.execution_stats.items():
            if stats['avg_time'] > threshold:
                slow_tasks.append({
                    'task_id': task_id,
                    'avg_execution_time': stats['avg_time'],
                    'execution_count': stats['count']
                })
        
        # 按平均执行时间排序
        slow_tasks.sort(key=lambda x: x['avg_execution_time'], reverse=True)
        return slow_tasks
```

## 任务配置管理

### 1. 配置文件

```python
# config/scheduler_config.py
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class TaskConfig:
    """任务配置"""
    task_id: str
    task_name: str
    task_func: str
    trigger_type: str
    trigger_args: Dict[str, Any]
    enabled: bool = True
    description: str = ""

# 默认任务配置
DEFAULT_TASKS = [
    TaskConfig(
        task_id="daily_cleanup",
        task_name="每日清理任务",
        task_func="cleanup_service.daily_cleanup",
        trigger_type="cron",
        trigger_args={"hour": 2, "minute": 0},
        description="清理过期数据和日志文件"
    ),
    TaskConfig(
        task_id="health_check",
        task_name="健康检查任务",
        task_func="health_service.system_health_check",
        trigger_type="interval",
        trigger_args={"minutes": 30},
        description="检查系统健康状态"
    ),
    TaskConfig(
        task_id="data_backup",
        task_name="数据备份任务",
        task_func="backup_service.daily_backup",
        trigger_type="cron",
        trigger_args={"hour": 3, "minute": 0},
        description="每日数据备份"
    )
]
```

### 2. 配置加载器

```python
class TaskConfigLoader:
    """任务配置加载器"""
    
    def __init__(self):
        self.config_file = "config/tasks.json"
        self.default_tasks = DEFAULT_TASKS
    
    def load_config(self) -> List[TaskConfig]:
        """加载任务配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                tasks = []
                for task_data in config_data:
                    task = TaskConfig(**task_data)
                    tasks.append(task)
                
                logger.info(f"从配置文件加载了 {len(tasks)} 个任务")
                return tasks
            else:
                logger.info("配置文件不存在，使用默认配置")
                return self.default_tasks
                
        except Exception as e:
            logger.error(f"加载任务配置失败: {e}")
            return self.default_tasks
    
    def save_config(self, tasks: List[TaskConfig]):
        """保存任务配置"""
        try:
            config_data = []
            for task in tasks:
                config_data.append({
                    'task_id': task.task_id,
                    'task_name': task.task_name,
                    'task_func': task.task_func,
                    'trigger_type': task.trigger_type,
                    'trigger_args': task.trigger_args,
                    'enabled': task.enabled,
                    'description': task.description
                })
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info("任务配置保存成功")
            
        except Exception as e:
            logger.error(f"保存任务配置失败: {e}")
```

## 使用示例

### 1. 基本使用

```python
# 1. 启动调度器
scheduler.start()

# 2. 注册任务
task_registry = TaskRegistry()

# 注册Cron任务
task_registry.register_cron_task(
    "daily_cleanup",
    daily_cleanup_task,
    "0 0 2 * * *"
)

# 注册间隔任务
task_registry.register_interval_task(
    "health_check",
    health_check_task,
    minutes=30
)

# 3. 启动监控
task_monitor = TaskMonitor()
task_monitor.start_monitoring()

# 4. 任务控制
task_controller = TaskController()

# 获取所有任务
all_tasks = task_controller.get_all_tasks()
print(f"当前共有 {len(all_tasks)} 个任务")

# 获取特定任务状态
task_status = task_controller.get_task_status("daily_cleanup")
if task_status:
    print(f"任务状态: {task_status}")
```

### 2. 动态任务管理

```python
# 动态添加任务
async def add_dynamic_task():
    """动态添加任务示例"""
    # 创建一个新任务
    async def dynamic_task():
        logger.info("动态任务执行中...")
        await asyncio.sleep(5)
        logger.info("动态任务执行完成")
    
    # 注册任务（每5分钟执行一次）
    task_registry.register_interval_task(
        "dynamic_task",
        dynamic_task,
        minutes=5
    )
    
    logger.info("动态任务已添加")

# 动态修改任务
async def modify_dynamic_task():
    """动态修改任务示例"""
    # 修改任务执行频率（改为每10分钟执行一次）
    task_controller.modify_task(
        "dynamic_task",
        minutes=10
    )
    
    logger.info("动态任务已修改")

# 动态移除任务
async def remove_dynamic_task():
    """动态移除任务示例"""
    # 移除任务
    task_controller.remove_task("dynamic_task")
    
    logger.info("动态任务已移除")
```

### 3. 任务执行监控

```python
# 启动性能监控
performance_monitor = TaskPerformanceMonitor()

# 包装任务函数以记录执行时间
def monitor_execution_time(func):
    """监控执行时间的装饰器"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            performance_monitor.record_execution_time(func.__name__, execution_time)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            performance_monitor.record_execution_time(func.__name__, execution_time)
            raise
    return wrapper

# 使用装饰器监控任务
@monitor_execution_time
async def monitored_task():
    """被监控的任务"""
    await asyncio.sleep(2)
    logger.info("监控任务执行完成")

# 注册监控任务
task_registry.register_interval_task(
    "monitored_task",
    monitored_task,
    minutes=1
)

# 定期获取性能报告
async def get_performance_report():
    """获取性能报告"""
    while True:
        await asyncio.sleep(60)  # 每分钟获取一次
        
        # 获取整体性能报告
        report = performance_monitor.get_performance_report()
        logger.info(f"性能报告: {report}")
        
        # 获取慢任务列表
        slow_tasks = performance_monitor.get_slow_tasks(threshold=1.0)
        if slow_tasks:
            logger.warning(f"发现慢任务: {slow_tasks}")

# 启动性能监控
asyncio.create_task(get_performance_report())
```

## 最佳实践

### 1. 任务设计原则
- **单一职责**: 每个任务只负责一个特定功能
- **幂等性**: 任务可以重复执行而不产生副作用
- **异常处理**: 完善的异常处理和日志记录
- **资源管理**: 合理管理任务执行资源

### 2. 性能优化原则
- **异步执行**: 使用异步函数提高执行效率
- **批量处理**: 批量处理数据减少执行次数
- **资源控制**: 控制任务并发数和资源使用
- **缓存策略**: 合理使用缓存减少重复计算

### 3. 监控运维原则
- **实时监控**: 实时监控任务执行状态
- **性能分析**: 定期分析任务执行性能
- **告警机制**: 建立任务异常告警机制
- **日志管理**: 完善的日志记录和管理

---

**注意**: 本文档会持续更新，请关注最新版本。如有问题，请通过 Issues 反馈。 