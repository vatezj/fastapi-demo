#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis安全访问装饰器
用于在Redis不可用时提供安全的降级处理
"""

import functools
import asyncio
from typing import Callable, Any, Optional
from fastapi import Request
from config.get_redis import RedisUtil
from utils.log_util import logger


def safe_redis_access(func: Callable) -> Callable:
    """
    Redis安全访问装饰器
    
    用法:
    @safe_redis_access
    async def some_function(request: Request, ...):
        # 函数内部可以直接使用 redis 变量
        # 装饰器会自动处理Redis不可用的情况
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
        
        # 获取Redis连接
        redis = None
        if request:
            try:
                redis = await RedisUtil.get_redis_pool()
            except Exception as e:
                logger.warning(f'获取Redis连接失败: {e}')
        
        # 将redis添加到kwargs中，供函数使用
        kwargs['redis'] = redis
        
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


def redis_required(func: Callable) -> Callable:
    """
    Redis必需装饰器 - 如果Redis不可用则抛出异常
    
    用法:
    @redis_required
    async def critical_function(request: Request, redis=None):
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
        
        # 获取Redis连接
        redis = None
        if request:
            try:
                redis = await RedisUtil.get_redis_pool()
            except Exception as e:
                logger.error(f'获取Redis连接失败: {e}')
                raise RuntimeError(f'函数 {func.__name__} 需要Redis服务，但Redis不可用')
        
        if not redis:
            raise RuntimeError(f'函数 {func.__name__} 需要Redis服务，但Redis不可用')
        
        # 将redis添加到kwargs中，供函数使用
        kwargs['redis'] = redis
        
        # 调用原函数
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    return wrapper


def redis_optional(func: Callable) -> Callable:
    """
    Redis可选装饰器 - 如果Redis不可用则跳过相关操作
    
    用法:
    @redis_optional
    async def optional_function(request: Request, redis=None):
        # 此函数可以在Redis不可用时运行，跳过Redis相关操作
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
        
        # 获取Redis连接
        redis = None
        if request:
            try:
                redis = await RedisUtil.get_redis_pool()
            except Exception as e:
                logger.warning(f'获取Redis连接失败: {e}')
        
        # 将redis添加到kwargs中，供函数使用
        kwargs['redis'] = redis
        
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
