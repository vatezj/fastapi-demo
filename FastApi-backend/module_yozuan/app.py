"""
游赚模块主入口文件
配置模块路由、中间件和依赖注入
参考 module_app 的入口文件结构
"""

from fastapi import FastAPI
from config.env import AppConfig
from config.yozuan_config import yozuan_config
from .controller import task_controller, order_controller, account_controller, invitation_controller, region_controller
from .controller.admin import (
    admin_controller, task_admin_controller, order_admin_router, 
    user_admin_router, finance_admin_router, system_admin_router
)

# 创建专门的游赚模块FastAPI应用
yozuan_app = FastAPI(
    title=f'{AppConfig.app_name} - 游赚模块',
    description=f'{AppConfig.app_name}游赚任务接单平台模块 - 支持任务发布、接单、完成、验证、返佣等完整业务流程',
    version=AppConfig.app_version,
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
)

# 注册游赚模块的路由

# 任务管理路由 - 任务相关接口
yozuan_app.include_router(
    task_controller.router,
    prefix="/v1/task",
    tags=["任务管理"]
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

# 管理接口路由 - 后台管理接口
yozuan_app.include_router(
    admin_controller.router,
    prefix="/v1/admin",
    tags=["管理接口"]
)

# 任务管理后台路由
yozuan_app.include_router(
    task_admin_controller.router,
    prefix="/v1/admin/task",
    tags=["后台管理-任务管理"]
)

# 订单管理后台路由
yozuan_app.include_router(
    order_admin_router,
    prefix="/v1/admin/order",
    tags=["后台管理-订单管理"]
)

# 用户管理后台路由
yozuan_app.include_router(
    user_admin_router,
    prefix="/v1/admin/user",
    tags=["后台管理-用户管理"]
)

# 财务管理后台路由
yozuan_app.include_router(
    finance_admin_router,
    prefix="/v1/admin/finance",
    tags=["后台管理-财务管理"]
)

# 系统管理后台路由
yozuan_app.include_router(
    system_admin_router,
    prefix="/v1/admin/system",
    tags=["后台管理-系统管理"]
)

# 邀请和分销路由
yozuan_app.include_router(
    invitation_controller.invitation_router,
    prefix="/v1/invitation",
    tags=["邀请分销"]
)

# 地区管理路由
yozuan_app.include_router(
    region_controller.router,
    prefix="/v1/region",
    tags=["地区管理"]
)

# 模块信息接口
@yozuan_app.get("/info", tags=["模块信息"])
async def get_module_info():
    """获取游赚模块信息"""
    return {
        "module": "yozuan",
        "name": "游赚任务接单平台",
        "version": AppConfig.app_version,
        "description": "支持任务发布、接单、完成、验证、返佣等完整业务流程",
        "features": [
            "任务管理",
            "订单管理", 
            "账户管理",
            "分销返佣",
            "权限控制"
        ],
        "api_docs": "/docs",
        "openapi_spec": "/openapi.json"
    }

# 健康检查接口
@yozuan_app.get("/health", tags=["系统监控"])
async def health_check():
    """游赚模块健康检查"""
    return {
        "status": "healthy",
        "module": "yozuan",
        "timestamp": "2025-08-15T12:00:00Z"
    }

# 配置信息接口
@yozuan_app.get("/config", tags=["系统监控"])
async def get_module_config():
    """获取游赚模块配置信息"""
    return {
        "module": "yozuan",
        "enabled": yozuan_config.yozuan_enabled,
        "db_prefix": yozuan_config.yozuan_db_prefix,
        "task_config": {
            "max_steps": yozuan_config.yozuan_task_max_steps,
            "max_verifications": yozuan_config.yozuan_task_max_verifications,
            "min_price": yozuan_config.yozuan_task_min_price,
            "max_price": yozuan_config.yozuan_task_max_price
        },
        "order_config": {
            "max_completion_hours": yozuan_config.yozuan_order_max_completion_hours,
            "max_review_hours": yozuan_config.yozuan_order_max_review_hours
        },
        "account_config": {
            "min_withdraw": yozuan_config.yozuan_account_min_withdraw,
            "max_withdraw": yozuan_config.yozuan_account_max_withdraw
        },
        "rebate_config": {
            "max_levels": yozuan_config.yozuan_rebate_max_levels,
            "min_rate": yozuan_config.yozuan_rebate_min_rate,
            "max_rate": yozuan_config.yozuan_rebate_max_rate
        }
    }
