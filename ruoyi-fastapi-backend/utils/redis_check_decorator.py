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
            if not hasattr(request.app.state, 'redis') or not request.app.state.redis:
                logger.warning(f'Redis未初始化，函数 {func.__name__} 将在无缓存模式下运行')
                # 设置一个标记，表示Redis不可用
                request.app.state.redis_available = False
            else:
                request.app.state.redis_available = True
        
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
        return await request.app.state.redis.get("key")
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
            if not hasattr(request.app.state, 'redis') or not request.app.state.redis:
                raise RuntimeError(f'函数 {func.__name__} 需要Redis服务，但Redis未初始化')
        
        # 调用原函数
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    return wrapper
