# -*- coding: utf-8 -*-
"""
缓存装饰器
用于优化接口性能，减少重复计算和数据库查询
"""

import functools
import hashlib
import json
import asyncio
from typing import Any, Callable, Optional, Union
from datetime import datetime, timedelta
from config.get_redis import RedisUtil
from utils.log_util import logger


def cache_result(
    expire_time: int = 300,
    key_prefix: str = "cache",
    include_args: bool = True,
    include_kwargs: bool = True,
    cache_none: bool = False
):
    """
    缓存函数结果的装饰器
    
    Args:
        expire_time: 缓存过期时间（秒），默认5分钟
        key_prefix: 缓存键前缀
        include_args: 是否将函数参数包含在缓存键中
        include_kwargs: 是否将函数关键字参数包含在缓存键中
        cache_none: 是否缓存None结果
    
    Usage:
        @cache_result(expire_time=600, key_prefix="user_list")
        async def get_user_list(page_num: int, page_size: int):
            # 函数逻辑
            pass
    """
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(
                func, args, kwargs, key_prefix, include_args, include_kwargs
            )
            
            # 尝试从缓存获取结果
            try:
                redis = await RedisUtil.get_redis_pool()
                if redis:
                    cached_result = await redis.get(cache_key)
                    if cached_result:
                        logger.debug(f'缓存命中: {cache_key}')
                        return json.loads(cached_result)
            except Exception as e:
                logger.warning(f'缓存读取失败: {e}')
            
            # 执行原函数
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                # 缓存结果
                if result is not None or cache_none:
                    try:
                        if redis:
                            await redis.setex(
                                cache_key, 
                                expire_time, 
                                json.dumps(result, ensure_ascii=False, default=str)
                            )
                            logger.debug(f'缓存写入成功: {cache_key}, 过期时间: {expire_time}秒')
                    except Exception as e:
                        logger.warning(f'缓存写入失败: {e}')
                
                return result
            except Exception as e:
                logger.error(f'函数执行失败: {e}')
                raise
        
        return wrapper
    
    return decorator


def cache_invalidate(
    key_pattern: str,
    pattern_type: str = "exact"  # "exact", "prefix", "suffix", "contains"
):
    """
    缓存失效装饰器
    
    Args:
        key_pattern: 缓存键模式
        pattern_type: 匹配类型
    
    Usage:
        @cache_invalidate("user_list:*")
        async def update_user(user_id: int):
            # 更新用户后，清除相关缓存
            pass
    """
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 执行原函数
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # 清除相关缓存
            try:
                redis = await RedisUtil.get_redis_pool()
                if redis:
                    await _invalidate_cache(redis, key_pattern, pattern_type)
                    logger.debug(f'缓存失效成功: {key_pattern}')
            except Exception as e:
                logger.warning(f'缓存失效失败: {e}')
            
            return result
        
        return wrapper
    
    return decorator


def _generate_cache_key(
    func: Callable, 
    args: tuple, 
    kwargs: dict, 
    prefix: str, 
    include_args: bool, 
    include_kwargs: bool
) -> str:
    """生成缓存键"""
    key_parts = [prefix, func.__module__, func.__name__]
    
    if include_args and args:
        # 过滤掉不可序列化的参数（如数据库连接）
        serializable_args = []
        for arg in args:
            if _is_serializable(arg):
                serializable_args.append(str(arg))
        if serializable_args:
            key_parts.extend(serializable_args)
    
    if include_kwargs and kwargs:
        # 过滤掉不可序列化的关键字参数
        serializable_kwargs = {}
        for key, value in kwargs.items():
            if _is_serializable(value):
                serializable_kwargs[key] = str(value)
        if serializable_kwargs:
            key_parts.append(json.dumps(serializable_kwargs, sort_keys=True))
    
    # 生成MD5哈希作为缓存键
    key_string = ":".join(key_parts)
    return f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"


def _is_serializable(obj: Any) -> bool:
    """检查对象是否可序列化"""
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


async def _invalidate_cache(redis, key_pattern: str, pattern_type: str):
    """清除匹配的缓存"""
    try:
        if pattern_type == "exact":
            # 精确匹配
            await redis.delete(key_pattern)
        elif pattern_type == "prefix":
            # 前缀匹配
            keys = await redis.keys(f"{key_pattern}*")
            if keys:
                await redis.delete(*keys)
        elif pattern_type == "suffix":
            # 后缀匹配
            keys = await redis.keys(f"*{key_pattern}")
            if keys:
                await redis.delete(*keys)
        elif pattern_type == "contains":
            # 包含匹配
            keys = await redis.keys(f"*{key_pattern}*")
            if keys:
                await redis.delete(*keys)
    except Exception as e:
        logger.error(f'清除缓存失败: {e}')


# 预定义的缓存键模式
class CacheKeys:
    """缓存键常量"""
    APP_USER_LIST = "app:user:list"
    APP_USER_DETAIL = "app:user:detail"
    APP_LOGIN_LOG_LIST = "app:loginlog:list"
    APP_STATS_OVERVIEW = "app:stats:overview"
    
    @staticmethod
    def user_list(page_num: int, page_size: int, **filters) -> str:
        """生成用户列表缓存键"""
        filter_str = ":".join([f"{k}={v}" for k, v in sorted(filters.items()) if v is not None])
        return f"{CacheKeys.APP_USER_LIST}:{page_num}:{page_size}:{filter_str}"
    
    @staticmethod
    def user_detail(user_id: int) -> str:
        """生成用户详情缓存键"""
        return f"{CacheKeys.APP_USER_DETAIL}:{user_id}"
    
    @staticmethod
    def login_log_list(page_num: int, page_size: int, **filters) -> str:
        """生成登录日志列表缓存键"""
        filter_str = ":".join([f"{k}={v}" for k, v in sorted(filters.items()) if v is not None])
        return f"{CacheKeys.APP_LOGIN_LOG_LIST}:{page_num}:{page_size}:{filter_str}"
    
    @staticmethod
    def stats_overview() -> str:
        """生成统计概览缓存键"""
        return CacheKeys.APP_STATS_OVERVIEW


# 便捷的缓存装饰器
def cache_user_list(expire_time: int = 300):
    """缓存用户列表的装饰器"""
    return cache_result(expire_time=expire_time, key_prefix="app:user:list")


def cache_user_detail(expire_time: int = 600):
    """缓存用户详情的装饰器"""
    return cache_result(expire_time=expire_time, key_prefix="app:user:detail")


def cache_login_log_list(expire_time: int = 300):
    """缓存登录日志列表的装饰器"""
    return cache_result(expire_time=expire_time, key_prefix="app:loginlog:list")


def cache_stats_overview(expire_time: int = 60):
    """缓存统计概览的装饰器"""
    return cache_result(expire_time=expire_time, key_prefix="app:stats:overview")


def invalidate_user_cache():
    """失效用户相关缓存的装饰器"""
    return cache_invalidate("app:user:*", "prefix")


def invalidate_login_log_cache():
    """失效登录日志相关缓存的装饰器"""
    return cache_invalidate("app:loginlog:*", "prefix")


def invalidate_stats_cache():
    """失效统计相关缓存的装饰器"""
    return cache_invalidate("app:stats:*", "prefix")
