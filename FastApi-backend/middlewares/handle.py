from fastapi import FastAPI
from middlewares.cors_middleware import add_cors_middleware
from middlewares.gzip_middleware import add_gzip_middleware
from middlewares.trace_middleware import add_trace_middleware
from middlewares.startup_check_middleware import StartupCheckMiddleware


def handle_middleware(app: FastAPI):
    """
    全局中间件处理
    """
    # 加载启动状态检查中间件（最高优先级）
    app.add_middleware(StartupCheckMiddleware)
    
    # 加载跨域中间件
    add_cors_middleware(app)
    # 加载gzip压缩中间件
    add_gzip_middleware(app)
    # 加载trace中间件
    add_trace_middleware(app)
