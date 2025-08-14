from fastapi import Request
from config.enums import RedisInitKeyConfig
from config.get_redis import RedisUtil
from module_admin.entity.vo.cache_vo import CacheInfoModel, CacheMonitorModel
from module_admin.entity.vo.common_vo import CrudResponseModel
from utils.log_util import logger


class CacheService:
    """
    缓存监控模块服务层
    """

    @classmethod
    async def get_cache_monitor_statistical_info_services(cls, request: Request):
        """
        获取缓存监控信息service

        :param request: Request对象
        :return: 缓存监控信息
        """
        try:
            # 获取Redis连接
            redis = await RedisUtil.get_redis_pool()
            if not redis:
                logger.warning('Redis不可用，返回默认缓存监控信息')
                return CacheMonitorModel(commandStats=[], dbSize=0, info={})
            
            info = await redis.info()
            db_size = await redis.dbsize()
            command_stats_dict = await redis.info('commandstats')
            command_stats = [
                dict(name=key.split('_')[1], value=str(value.get('calls'))) for key, value in command_stats_dict.items()
            ]
            result = CacheMonitorModel(commandStats=command_stats, dbSize=db_size, info=info)

            return result
            
        except Exception as e:
            logger.error(f'获取缓存监控信息失败: {e}')
            return CacheMonitorModel(commandStats=[], dbSize=0, info={})

    @classmethod
    async def get_cache_monitor_cache_name_services(cls):
        """
        获取缓存名称列表信息service

        :return: 缓存名称列表信息
        """
        name_list = []
        for key_config in RedisInitKeyConfig:
            name_list.append(
                CacheInfoModel(
                    cacheKey='',
                    cacheName=key_config.key,
                    cacheValue='',
                    remark=key_config.remark,
                )
            )

        return name_list

    @classmethod
    async def get_cache_monitor_cache_key_services(cls, request: Request, cache_name: str):
        """
        获取缓存键名列表信息service

        :param request: Request对象
        :param cache_name: 缓存名称
        :return: 缓存键名列表信息
        """
        try:
            # 获取Redis连接
            redis = await RedisUtil.get_redis_pool()
            if not redis:
                logger.warning('Redis不可用，返回空缓存键列表')
                return []
            
            cache_keys = await redis.keys(f'{cache_name}*')
            cache_key_list = [key.split(':', 1)[1] for key in cache_keys if key.startswith(f'{cache_name}:')]

            return cache_key_list
            
        except Exception as e:
            logger.error(f'获取缓存键列表失败: {e}')
            return []

    @classmethod
    async def get_cache_monitor_cache_value_services(cls, request: Request, cache_name: str, cache_key: str):
        """
        获取缓存内容信息service

        :param request: Request对象
        :param cache_name: 缓存名称
        :param cache_key: 缓存键名
        :return: 缓存内容信息
        """
        try:
            # 获取Redis连接
            redis = await RedisUtil.get_redis_pool()
            if not redis:
                logger.warning('Redis不可用，返回默认缓存信息')
                return CacheInfoModel(cacheKey=cache_key, cacheName=cache_name, cacheValue=None, remark='Redis不可用')
            
            cache_value = await redis.get(f'{cache_name}:{cache_key}')

            return CacheInfoModel(cacheKey=cache_key, cacheName=cache_name, cacheValue=cache_value, remark='')
            
        except Exception as e:
            logger.error(f'获取缓存值失败: {e}')
            return CacheInfoModel(cacheKey=cache_key, cacheName=cache_name, cacheValue=None, remark=f'获取失败: {str(e)}')

    @classmethod
    async def clear_cache_monitor_cache_name_services(cls, request: Request, cache_name: str):
        """
        清除缓存名称对应所有键值service

        :param request: Request对象
        :param cache_name: 缓存名称
        :return: 操作缓存响应信息
        """
        try:
            # 获取Redis连接
            redis = await RedisUtil.get_redis_pool()
            if not redis:
                logger.warning('Redis不可用，跳过缓存清理操作')
                return CrudResponseModel(is_success=True, message=f'{cache_name}对应键值清除成功（Redis不可用）')
            
            cache_keys = await redis.keys(f'{cache_name}*')
            if cache_keys:
                await redis.delete(*cache_keys)

            return CrudResponseModel(is_success=True, message=f'{cache_name}对应键值清除成功')
            
        except Exception as e:
            logger.error(f'清除缓存名称失败: {e}')
            return CrudResponseModel(is_success=False, message=f'清除失败: {str(e)}')

    @classmethod
    async def clear_cache_monitor_cache_key_services(cls, request: Request, cache_key: str):
        """
        清除缓存名称对应所有键值service

        :param request: Request对象
        :param cache_key: 缓存键名
        :return: 操作缓存响应信息
        """
        try:
            # 获取Redis连接
            redis = await RedisUtil.get_redis_pool()
            if not redis:
                logger.warning('Redis不可用，跳过缓存清理操作')
                return CrudResponseModel(is_success=True, message=f'{cache_key}清除成功（Redis不可用）')
            
            cache_keys = await redis.keys(f'*{cache_key}')
            if cache_keys:
                await redis.delete(*cache_keys)

            return CrudResponseModel(is_success=True, message=f'{cache_key}清除成功')
            
        except Exception as e:
            logger.error(f'清除缓存键失败: {e}')
            return CrudResponseModel(is_success=False, message=f'清除失败: {str(e)}')

    @classmethod
    async def clear_cache_monitor_all_services(cls, request: Request):
        """
        清除所有缓存service

        :param request: Request对象
        :return: 操作缓存响应信息
        """
        try:
            # 获取Redis连接
            redis = await RedisUtil.get_redis_pool()
            if not redis:
                logger.warning('Redis不可用，跳过缓存清理操作')
                return CrudResponseModel(is_success=True, message='所有缓存清除成功（Redis不可用）')
            
            cache_keys = await redis.keys()
            if cache_keys:
                await redis.delete(*cache_keys)
            
            await RedisUtil.init_sys_dict(redis)
            await RedisUtil.init_sys_config(redis)

            return CrudResponseModel(is_success=True, message='所有缓存清除成功')
            
        except Exception as e:
            logger.error(f'清除所有缓存失败: {e}')
            return CrudResponseModel(is_success=False, message=f'清除失败: {str(e)}')
