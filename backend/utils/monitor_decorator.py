# -*- coding: utf-8 -*-
"""
监控装饰器
用于监控接口性能、异常情况和业务指标
"""

import functools
import time
import asyncio
from typing import Any, Callable, Dict, Optional
from datetime import datetime
from config.get_redis import RedisUtil
from utils.log_util import logger


def monitor_performance(
    operation_name: str = None,
    threshold_ms: int = 1000,
    alert_on_slow: bool = True,
    track_metrics: bool = True
):
    """
    性能监控装饰器
    
    Args:
        operation_name: 操作名称，用于标识监控指标
        threshold_ms: 性能阈值（毫秒），超过此值将记录警告
        alert_on_slow: 是否在慢操作时告警
        track_metrics: 是否跟踪性能指标
    
    Usage:
        @monitor_performance("get_user_list", threshold_ms=500)
        async def get_user_list():
            pass
    """
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                # 执行原函数
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # 计算执行时间
                execution_time = (time.time() - start_time) * 1000
                
                # 记录性能指标
                if track_metrics:
                    await _record_performance_metrics(operation, execution_time, success=True)
                
                # 慢操作告警
                if alert_on_slow and execution_time > threshold_ms:
                    logger.warning(
                        f'慢操作告警: {operation} 执行时间 {execution_time:.2f}ms 超过阈值 {threshold_ms}ms'
                    )
                    await _send_slow_operation_alert(operation, execution_time, threshold_ms)
                
                # 记录性能日志
                if execution_time > threshold_ms:
                    logger.warning(f'慢操作: {operation} 执行时间 {execution_time:.2f}ms')
                else:
                    logger.debug(f'操作完成: {operation} 执行时间 {execution_time:.2f}ms')
                
                return result
                
            except Exception as e:
                # 计算执行时间（即使失败）
                execution_time = (time.time() - start_time) * 1000
                
                # 记录失败指标
                if track_metrics:
                    await _record_performance_metrics(operation, execution_time, success=False)
                
                # 记录异常日志
                logger.error(f'操作失败: {operation} 执行时间 {execution_time:.2f}ms, 错误: {e}')
                
                # 发送异常告警
                await _send_exception_alert(operation, execution_time, str(e))
                
                raise
        
        return wrapper
    
    return decorator


def monitor_business_metrics(
    metric_name: str,
    increment: int = 1,
    tags: Optional[Dict[str, str]] = None
):
    """
    业务指标监控装饰器
    
    Args:
        metric_name: 指标名称
        increment: 增量值
        tags: 标签信息
    
    Usage:
        @monitor_business_metrics("user_login_success", tags={"source": "mobile"})
        async def user_login():
            pass
    """
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # 执行原函数
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # 记录业务指标
                await _record_business_metrics(metric_name, increment, tags)
                
                return result
                
            except Exception as e:
                # 记录失败指标
                await _record_business_metrics(f"{metric_name}_failed", increment, tags)
                raise
        
        return wrapper
    
    return decorator


def monitor_error_rate(
    operation_name: str = None,
    error_threshold: float = 0.1,  # 10%错误率阈值
    window_size: int = 100  # 滑动窗口大小
):
    """
    错误率监控装饰器
    
    Args:
        operation_name: 操作名称
        error_threshold: 错误率阈值
        window_size: 滑动窗口大小
    
    Usage:
        @monitor_error_rate("user_login", error_threshold=0.05)
        async def user_login():
            pass
    """
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                # 执行原函数
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # 记录成功
                await _record_operation_result(operation, success=True, window_size=window_size)
                
                return result
                
            except Exception as e:
                # 记录失败
                await _record_operation_result(operation, success=False, window_size=window_size)
                
                # 检查错误率
                error_rate = await _check_error_rate(operation, window_size)
                if error_rate > error_threshold:
                    logger.error(f'错误率告警: {operation} 错误率 {error_rate:.2%} 超过阈值 {error_threshold:.2%}')
                    await _send_error_rate_alert(operation, error_rate, error_threshold)
                
                raise
        
        return wrapper
    
    return decorator


async def _record_performance_metrics(operation: str, execution_time: float, success: bool):
    """记录性能指标"""
    try:
        redis = await RedisUtil.get_redis_pool()
        if redis:
            timestamp = datetime.now().isoformat()
            metric_key = f"metrics:performance:{operation}"
            
            # 记录执行时间
            await redis.zadd(f"{metric_key}:execution_time", {timestamp: execution_time})
            
            # 记录成功/失败次数
            await redis.hincrby(f"{metric_key}:counts", "total", 1)
            await redis.hincrby(f"{metric_key}:counts", "success" if success else "failed", 1)
            
            # 设置过期时间（保留7天）
            await redis.expire(f"{metric_key}:execution_time", 7 * 24 * 3600)
            await redis.expire(f"{metric_key}:counts", 7 * 24 * 3600)
            
    except Exception as e:
        logger.warning(f'记录性能指标失败: {e}')


async def _record_business_metrics(metric_name: str, increment: int, tags: Optional[Dict[str, str]] = None):
    """记录业务指标"""
    try:
        redis = await RedisUtil.get_redis_pool()
        if redis:
            timestamp = datetime.now().isoformat()
            tag_str = ":".join([f"{k}={v}" for k, v in (tags or {}).items()])
            metric_key = f"metrics:business:{metric_name}"
            if tag_str:
                metric_key = f"{metric_key}:{tag_str}"
            
            # 记录指标值
            await redis.hincrby(metric_key, "value", increment)
            await redis.hset(metric_key, "last_update", timestamp)
            
            # 设置过期时间（保留30天）
            await redis.expire(metric_key, 30 * 24 * 3600)
            
    except Exception as e:
        logger.warning(f'记录业务指标失败: {e}')


async def _record_operation_result(operation: str, success: bool, window_size: int):
    """记录操作结果"""
    try:
        redis = await RedisUtil.get_redis_pool()
        if redis:
            timestamp = datetime.now().isoformat()
            result_key = f"metrics:error_rate:{operation}"
            
            # 记录结果到滑动窗口
            await redis.zadd(result_key, {timestamp: 1 if success else 0})
            
            # 移除超出窗口的数据
            await redis.zremrangebyrank(result_key, 0, -window_size-1)
            
            # 设置过期时间
            await redis.expire(result_key, 24 * 3600)
            
    except Exception as e:
        logger.warning(f'记录操作结果失败: {e}')


async def _check_error_rate(operation: str, window_size: int) -> float:
    """检查错误率"""
    try:
        redis = await RedisUtil.get_redis_pool()
        if redis:
            result_key = f"metrics:error_rate:{operation}"
            
            # 获取窗口内的结果
            results = await redis.zrange(result_key, 0, -1, withscores=True)
            
            if not results:
                return 0.0
            
            # 计算错误率
            total = len(results)
            failed = sum(1 for _, score in results if score == 0)
            
            return failed / total if total > 0 else 0.0
            
    except Exception as e:
        logger.warning(f'检查错误率失败: {e}')
    
    return 0.0


async def _send_slow_operation_alert(operation: str, execution_time: float, threshold_ms: int):
    """发送慢操作告警"""
    try:
        redis = await RedisUtil.get_redis_pool()
        if redis:
            alert_key = f"alerts:slow_operation:{datetime.now().strftime('%Y%m%d')}"
            alert_data = {
                "type": "slow_operation",
                "operation": operation,
                "execution_time": execution_time,
                "threshold": threshold_ms,
                "timestamp": datetime.now().isoformat(),
                "message": f"操作 {operation} 执行时间 {execution_time:.2f}ms 超过阈值 {threshold_ms}ms"
            }
            
            await redis.lpush(alert_key, str(alert_data))
            await redis.expire(alert_key, 24 * 3600)
            
    except Exception as e:
        logger.warning(f'发送慢操作告警失败: {e}')


async def _send_exception_alert(operation: str, execution_time: float, error_message: str):
    """发送异常告警"""
    try:
        redis = await RedisUtil.get_redis_pool()
        if redis:
            alert_key = f"alerts:exception:{datetime.now().strftime('%Y%m%d')}"
            alert_data = {
                "type": "exception",
                "operation": operation,
                "execution_time": execution_time,
                "error_message": error_message,
                "timestamp": datetime.now().isoformat(),
                "message": f"操作 {operation} 执行失败: {error_message}"
            }
            
            await redis.lpush(alert_key, str(alert_data))
            await redis.expire(alert_key, 24 * 3600)
            
    except Exception as e:
        logger.warning(f'发送异常告警失败: {e}')


async def _send_error_rate_alert(operation: str, error_rate: float, threshold: float):
    """发送错误率告警"""
    try:
        redis = await RedisUtil.get_redis_pool()
        if redis:
            alert_key = f"alerts:error_rate:{datetime.now().strftime('%Y%m%d')}"
            alert_data = {
                "type": "error_rate",
                "operation": operation,
                "error_rate": error_rate,
                "threshold": threshold,
                "timestamp": datetime.now().isoformat(),
                "message": f"操作 {operation} 错误率 {error_rate:.2%} 超过阈值 {threshold:.2%}"
            }
            
            await redis.lpush(alert_key, str(alert_data))
            await redis.expire(alert_key, 24 * 3600)
            
    except Exception as e:
        logger.warning(f'发送错误率告警失败: {e}')


# 便捷的监控装饰器
def monitor_user_operations(operation_name: str):
    """监控用户相关操作的装饰器"""
    return monitor_performance(
        operation_name=operation_name,
        threshold_ms=500,
        alert_on_slow=True,
        track_metrics=True
    )


def monitor_login_operations(operation_name: str):
    """监控登录相关操作的装饰器"""
    return monitor_performance(
        operation_name=operation_name,
        threshold_ms=2000,
        alert_on_slow=True,
        track_metrics=True
    )


def monitor_stats_operations(operation_name: str):
    """监控统计相关操作的装饰器"""
    return monitor_performance(
        operation_name=operation_name,
        threshold_ms=1000,
        alert_on_slow=True,
        track_metrics=True
    )


def track_user_metrics(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """跟踪用户相关指标的装饰器"""
    return monitor_business_metrics(metric_name, tags=tags)


def track_login_metrics(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """跟踪登录相关指标的装饰器"""
    return monitor_business_metrics(metric_name, tags=tags)
