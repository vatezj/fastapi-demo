from redis import asyncio as aioredis
from redis.exceptions import AuthenticationError, TimeoutError, RedisError
from config.database import AsyncSessionLocal
from config.env import RedisConfig
from utils.log_util import logger


class RedisUtil:
    """
    Redis相关方法
    """
    
    # 全局Redis连接缓存
    _redis_pool = None
    _redis_available = False

    @classmethod
    async def create_redis_pool(cls) -> aioredis.Redis:
        """
        应用启动时初始化redis连接

        :return: Redis连接对象
        """
        logger.info('开始连接redis...')
        try:
            redis = await aioredis.from_url(
                url=f'redis://{RedisConfig.redis_host}',
                port=RedisConfig.redis_port,
                username=RedisConfig.redis_username if RedisConfig.redis_username else None,
                password=RedisConfig.redis_password if RedisConfig.redis_password else None,
                db=RedisConfig.redis_database,
                encoding='utf-8',
                decode_responses=True,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            
            # 测试连接
            connection = await redis.ping()
            if connection:
                logger.info('redis连接成功')
                # 缓存Redis连接
                cls._redis_pool = redis
                cls._redis_available = True
                return redis
            else:
                logger.error('redis连接失败')
                cls._redis_available = False
                return None
                
        except AuthenticationError as e:
            logger.error(f'redis用户名或密码错误，详细错误信息：{e}')
            cls._redis_available = False
            return None
        except TimeoutError as e:
            logger.error(f'redis连接超时，详细错误信息：{e}')
            cls._redis_available = False
            return None
        except RedisError as e:
            logger.error(f'redis连接错误，详细错误信息：{e}')
            cls._redis_available = False
            return None
        except Exception as e:
            logger.error(f'redis连接未知错误：{e}')
            cls._redis_available = False
            return None

    @classmethod
    async def get_redis_pool(cls) -> aioredis.Redis:
        """
        获取Redis连接池，如果不存在则创建
        
        :return: Redis连接对象或None
        """
        if cls._redis_pool and cls._redis_available:
            try:
                # 测试连接是否仍然有效
                await cls._redis_pool.ping()
                return cls._redis_pool
            except Exception as e:
                logger.warning(f'Redis连接已失效，重新创建: {e}')
                cls._redis_pool = None
                cls._redis_available = False
        
        # 创建新的连接
        return await cls.create_redis_pool()

    @classmethod
    def is_redis_available(cls) -> bool:
        """
        检查Redis是否可用
        
        :return: Redis是否可用
        """
        return cls._redis_available and cls._redis_pool is not None

    @classmethod
    async def close_redis_pool(cls, app=None):
        """
        应用关闭时关闭redis连接

        :param app: fastapi对象（可选）
        :return:
        """
        try:
            if app and hasattr(app.state, 'redis') and app.state.redis:
                await app.state.redis.close()
                logger.info('关闭应用状态中的Redis连接成功')
            
            if cls._redis_pool:
                await cls._redis_pool.close()
                cls._redis_pool = None
                cls._redis_available = False
                logger.info('关闭全局Redis连接成功')
                
        except Exception as e:
            logger.error(f'关闭redis连接失败：{e}')

    @classmethod
    async def init_sys_dict(cls, redis):
        """
        应用启动时缓存字典表

        :param redis: redis对象
        :return:
        """
        if not redis:
            logger.warning('Redis未连接，跳过字典缓存初始化')
            return
            
        try:
            # 使用延迟导入避免循环导入
            from module_admin.service.dict_service import DictDataService
            async with AsyncSessionLocal() as session:
                await DictDataService.init_cache_sys_dict_services(session, redis)
        except Exception as e:
            logger.error(f'初始化字典缓存失败：{e}')

    @classmethod
    async def init_sys_config(cls, redis):
        """
        应用启动时缓存参数配置表

        :param redis: redis对象
        :return:
        """
        if not redis:
            logger.warning('Redis未连接，跳过配置缓存初始化')
            return
            
        try:
            # 使用延迟导入避免循环导入
            from module_admin.service.config_service import ConfigService
            async with AsyncSessionLocal() as session:
                await ConfigService.init_cache_sys_config_services(session, redis)
        except Exception as e:
            logger.error(f'初始化配置缓存失败：{e}')

    @classmethod
    def get_redis_from_app(cls, app) -> aioredis.Redis:
        """
        从应用状态获取Redis连接，如果不存在则返回None
        
        :param app: FastAPI应用实例
        :return: Redis连接对象或None
        """
        try:
            if hasattr(app.state, 'redis') and app.state.redis:
                return app.state.redis
            else:
                logger.warning('应用状态中没有Redis连接，尝试使用全局连接')
                return cls._redis_pool if cls.is_redis_available() else None
        except Exception as e:
            logger.error(f'获取Redis连接失败：{e}')
            return None
