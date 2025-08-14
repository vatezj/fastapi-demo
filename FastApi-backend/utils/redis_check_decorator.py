#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis状态检查装饰器
用于在访问Redis之前检查Redis是否已初始化
"""

import functools
import asyncio
from typing import Callable, Any
from fastapi import Request
from config.get_redis import RedisUtil
from utils.log_util import logger


def check_redis_state(func: Callable) -> Callable:
    """
    Redis状态检查装饰器
    
    用法:
    @check_redis_state
    async def some_function(request: Request, ...):
        # 函数内部可以直接访问 request.app.state.redis
        # 装饰器会自动检查Redis状态
        pass
    """
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # 查找Request参数
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            for value in kwargs.values():
                if isinstance(value, Request):
                    request = value
                    break
        
        if request and hasattr(request, 'app') and hasattr(request.app, 'state'):
            # 检查Redis状态
            try:
                redis = await RedisUtil.get_redis_pool()
                if redis:
                    request.app.state.redis_available = True
                    logger.debug(f'Redis可用，函数 {func.__name__} 将在缓存模式下运行')
                else:
                    request.app.state.redis_available = False
                    logger.warning(f'Redis不可用，函数 {func.__name__} 将在无缓存模式下运行')
            except Exception as e:
                request.app.state.redis_available = False
                logger.warning(f'Redis状态检查失败: {e}，函数 {func.__name__} 将在无缓存模式下运行')
        
        # 调用原函数
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            logger.error(f'函数 {func.__name__} 执行失败: {e}')
            raise
    
    return wrapper


def safe_redis_operation(operation: str = "操作"):
    """
    安全的Redis操作装饰器
    
    用法:
    @safe_redis_operation("获取配置")
    async def get_config(request: Request):
        redis = await RedisUtil.get_redis_pool()
        if redis:
            return await redis.get("key")
        return None
    """
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                logger.error(f'Redis {operation}失败: {e}')
                # 返回默认值或None
                return None
        
        return wrapper
    
    return decorator


def redis_required(func: Callable) -> Callable:
    """
    Redis必需装饰器 - 如果Redis不可用则抛出异常
    
    用法:
    @redis_required
    async def critical_function(request: Request):
        # 此函数必须在Redis可用时才能执行
        pass
    """
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # 查找Request参数
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            for value in kwargs.values():
                if isinstance(value, Request):
                    request = value
                    break
        
        if request and hasattr(request, 'app') and hasattr(request.app, 'state'):
            try:
                redis = await RedisUtil.get_redis_pool()
                if not redis:
                    raise RuntimeError(f'函数 {func.__name__} 需要Redis服务，但Redis不可用')
            except Exception as e:
                raise RuntimeError(f'函数 {func.__name__} 需要Redis服务，但Redis状态检查失败: {e}')
        
        # 调用原函数
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    return wrapper
