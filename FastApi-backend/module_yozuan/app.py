"""
游赚模块主入口文件
配置模块路由、中间件和依赖注入
参考 module_app 的入口文件结构
"""

from fastapi import FastAPI
from config.env import AppConfig
from config.yozuan_config import yozuan_config
from .controller import task_controller, task_publisher_controller, task_participant_controller
from .controller import order_controller, account_controller, invitation_controller, region_controller
from .controller.admin import (
    admin_controller, task_admin_controller, order_admin_router, 
    user_admin_router, finance_admin_router, system_admin_router
)
from exceptions.handle import handle_exception

# 创建专门的游赚模块FastAPI应用
yozuan_app = FastAPI(
    title=f'{AppConfig.app_name} - 游赚模块',
    description=f'{AppConfig.app_name}游赚任务接单平台模块 - 支持任务发布、接单、完成、验证、返佣等完整业务流程',
    version=AppConfig.app_version,
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
)

# 注册异常处理器到子应用
handle_exception(yozuan_app)

# 注册游赚模块的路由

# 任务公共路由 - 任务查询等公共接口
yozuan_app.include_router(
    task_controller.router,
    prefix="/v1/task",
    tags=["任务公共"]
)

# 任务发布者路由 - 任务发布者相关接口
yozuan_app.include_router(
    task_publisher_controller.router,
    prefix="/v1/task",
    tags=["任务发布者"]
)

# 任务参与者路由 - 任务参与者相关接口
yozuan_app.include_router(
    task_participant_controller.router,
    prefix="/v1/task",
    tags=["任务参与者"]
)

# 订单管理路由 - 订单相关接口
yozuan_app.include_router(
    order_controller.router,
    prefix="/v1/order",
    tags=["订单管理"]
)

# 账户管理路由 - 账户相关接口
yozuan_app.include_router(
    account_controller.router,
    prefix="/v1/account",
    tags=["账户管理"]
)

# 邀请管理路由 - 邀请相关接口
yozuan_app.include_router(
    invitation_controller.invitation_router,
    prefix="/v1/invitation",
    tags=["邀请管理"]
)

# 地区管理路由 - 地区相关接口
yozuan_app.include_router(
    region_controller.router,
    prefix="/v1/region",
    tags=["地区管理"]
)

# 管理员路由 - 管理员相关接口
yozuan_app.include_router(
    admin_controller.router,
    prefix="/v1/admin",
    tags=["管理员"]
)

# 任务管理员路由
yozuan_app.include_router(
    task_admin_controller.router,
    prefix="/v1/admin/task",
    tags=["任务管理员"]
)

# 订单管理员路由
yozuan_app.include_router(
    order_admin_router,
    prefix="/v1/admin/order",
    tags=["订单管理员"]
)

# 用户管理员路由
yozuan_app.include_router(
    user_admin_router,
    prefix="/v1/admin/user",
    tags=["用户管理员"]
)

# 财务管理员路由
yozuan_app.include_router(
    finance_admin_router,
    prefix="/v1/admin/finance",
    tags=["财务管理员"]
)

# 系统管理员路由
yozuan_app.include_router(
    system_admin_router,
    prefix="/v1/admin/system",
    tags=["系统管理员"]
)

# 配置CORS
from fastapi.middleware.cors import CORSMiddleware
yozuan_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:80',
        'http://127.0.0.1:80',
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置Gzip压缩
from fastapi.middleware.gzip import GZipMiddleware
yozuan_app.add_middleware(GZipMiddleware, minimum_size=1000)

# 启动事件
@yozuan_app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print(f"🚀 {AppConfig.app_name} 游赚模块启动成功")
    print(f"📖 API文档地址: http://localhost:{AppConfig.port}/yozuan/docs")
    print(f"🔧 配置信息: {yozuan_config}")

# 关闭事件
@yozuan_app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print(f"🛑 {AppConfig.app_name} 游赚模块已关闭")

# 健康检查接口
@yozuan_app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "module": "yozuan",
        "version": AppConfig.app_version,
        "message": "游赚模块运行正常"
    }

# 根路径重定向到文档
@yozuan_app.get("/", tags=["系统"])
async def root():
    """根路径重定向"""
    return {
        "message": f"欢迎使用 {AppConfig.app_name} 游赚模块",
        "docs_url": "/yozuan/docs",
        "version": AppConfig.app_version
    }
