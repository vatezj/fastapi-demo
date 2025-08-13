from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.log_util import logger


class RedisCheckMiddleware(BaseHTTPMiddleware):
    """
    Redis状态检查中间件
    """
    
    async def dispatch(self, request: Request, call_next):
        # 检查Redis状态
        if hasattr(request.app.state, 'redis') and request.app.state.redis:
            # Redis正常，继续处理请求
            response = await call_next(request)
            return response
        else:
            # Redis未初始化，记录警告但继续处理请求
            logger.warning(f'Redis未初始化，请求路径: {request.url.path}')
            response = await call_next(request)
            return response
