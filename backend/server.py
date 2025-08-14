from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.env import AppConfig
from config.get_db import init_create_table
from config.get_redis import RedisUtil
from config.get_scheduler import SchedulerUtil
from exceptions.handle import handle_exception
from middlewares.handle import handle_middleware
from module_admin.app import admin_app
from module_app.app import app_app
from sub_applications.handle import handle_sub_applications
from utils.common_util import worship
from utils.log_util import logger


# 生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f'{AppConfig.app_name}开始启动')
    worship()
    
    # 设置启动状态
    app.state.startup_complete = False
    app.state.redis = None
    
    try:
        # 初始化数据库表
        await init_create_table()
        logger.info('数据库表初始化完成')
        
        # 初始化Redis连接
        redis = await RedisUtil.create_redis_pool()
        if redis:
            app.state.redis = redis
            logger.info('Redis连接初始化完成')
            
            # 初始化系统字典和配置缓存
            try:
                await RedisUtil.init_sys_dict(redis)
                await RedisUtil.init_sys_config(redis)
                logger.info('系统缓存初始化完成')
            except Exception as e:
                logger.error(f'系统缓存初始化失败：{e}')
        else:
            logger.warning('Redis连接失败，应用将在无缓存模式下运行')
            app.state.redis = None
        
        # 初始化调度器
        try:
            await SchedulerUtil.init_system_scheduler()
            logger.info('系统调度器初始化完成')
        except Exception as e:
            logger.error(f'系统调度器初始化失败：{e}')
        
        # 标记启动完成
        app.state.startup_complete = True
        logger.info(f'{AppConfig.app_name}启动成功')
        
    except Exception as e:
        logger.error(f'应用启动失败：{e}')
        app.state.startup_complete = False
        raise
    
    yield
    
    # 应用关闭时的清理工作
    try:
        if hasattr(app.state, 'redis') and app.state.redis:
            await RedisUtil.close_redis_pool(app)
    except Exception as e:
        logger.error(f'关闭Redis连接失败：{e}')
    
    try:
        await SchedulerUtil.close_system_scheduler()
    except Exception as e:
        logger.error(f'关闭系统调度器失败：{e}')


# 初始化FastAPI对象
app = FastAPI(
    title=AppConfig.app_name,
    description=f'{AppConfig.app_name}主应用 - 统一入口',
    version=AppConfig.app_version,
    lifespan=lifespan,
    docs_url=None,  # 禁用主服务的docs
    redoc_url=None,  # 禁用主服务的redoc
    openapi_url=None,  # 禁用主服务的openapi
)

# 挂载子应用
handle_sub_applications(app)

# 挂载后台管理模块应用
app.mount("/admin", admin_app, name="admin_module")

# 挂载APP模块应用
app.mount("/app", app_app, name="app_module")

# 加载中间件处理方法
handle_middleware(app)
# 加载全局异常处理方法
handle_exception(app)


# 路由注册已完成在各自的模块中
