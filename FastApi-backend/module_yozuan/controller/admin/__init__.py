"""
后台管理控制器模块
"""

from .admin_controller import router as admin_router
from .task_admin_controller import router as task_admin_router
from .order_admin_controller import router as order_admin_router
from .user_admin_controller import router as user_admin_router
from .finance_admin_controller import router as finance_admin_router
from .system_admin_controller import router as system_admin_router

__all__ = [
    "admin_router",
    "task_admin_router", 
    "order_admin_router",
    "user_admin_router",
    "finance_admin_router",
    "system_admin_router"
]
