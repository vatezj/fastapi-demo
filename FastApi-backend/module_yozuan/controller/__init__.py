"""
游赚模块控制器层
包含所有API接口的定义
"""

from .task_controller import router as task_router
from .order_controller import router as order_router
from .account_controller import router as account_router
from .admin import admin_router
from .invitation_controller import invitation_router
from .region_controller import router as region_router

__all__ = [
    "task_router",
    "order_router",
    "account_router", 
    "admin_router",
    "invitation_router",
    "region_router"
]
