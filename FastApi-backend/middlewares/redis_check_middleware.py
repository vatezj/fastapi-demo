from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from config.get_redis import RedisUtil
from utils.log_util import logger


class RedisCheckMiddleware(BaseHTTPMiddleware):
    """
    Redis状态检查中间件
    """
    
    async def dispatch(self, request: Request, call_next):
        # 检查Redis状态
        try:
            redis = await RedisUtil.get_redis_pool()
            if redis:
                # Redis正常，继续处理请求
                response = await call_next(request)
                return response
            else:
                # Redis不可用，记录警告但继续处理请求
                logger.warning(f'Redis不可用，请求路径: {request.url.path}')
                response = await call_next(request)
                return response
        except Exception as e:
            # Redis状态检查失败，记录错误但继续处理请求
            logger.error(f'Redis状态检查失败: {e}，请求路径: {request.url.path}')
            response = await call_next(request)
            return response
