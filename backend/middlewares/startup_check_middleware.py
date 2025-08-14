from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.log_util import logger


class StartupCheckMiddleware(BaseHTTPMiddleware):
    """
    启动状态检查中间件
    确保应用完全启动后才处理请求
    """
    
    async def dispatch(self, request: Request, call_next):
        # 检查应用是否完全启动
        if not hasattr(request.app.state, 'startup_complete') or not request.app.state.startup_complete:
            logger.warning(f'应用尚未完全启动，拒绝请求: {request.url.path}')
            return Response(
                content='{"code": 503, "msg": "服务正在启动中，请稍后重试"}',
                status_code=503,
                media_type="application/json"
            )
        
        # 应用已启动，继续处理请求
        response = await call_next(request)
        return response
