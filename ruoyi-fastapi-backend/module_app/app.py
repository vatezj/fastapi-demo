from fastapi import FastAPI
from config.env import AppConfig
from .controller.app_user_controller import app_user_router
from .controller.auth_controller import router as auth_router
from .controller.user_controller import router as user_router

# 创建专门的APP模块FastAPI应用
app_app = FastAPI(
    title=f'{AppConfig.app_name} - APP接口',
    description=f'{AppConfig.app_name}移动端APP接口文档 - 面向移动端开发者',
    version=AppConfig.app_version,
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
)

# 注册APP模块的路由
app_app.include_router(auth_router, prefix="/v1")
app_app.include_router(user_router, prefix="/v1")
app_app.include_router(app_user_router, prefix="/v1")
