# -*- coding: utf-8 -*-
"""
APP控制器
包含所有APP相关的API接口
"""

from fastapi import APIRouter
from .auth_controller import router as auth_router
from .user_controller import router as user_router

# 创建主路由
app_router = APIRouter(prefix="/app/v1")

# 注册子路由
app_router.include_router(auth_router)
app_router.include_router(user_router)

__all__ = ["app_router", "auth_router", "user_router"] 