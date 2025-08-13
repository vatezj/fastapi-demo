# -*- coding: utf-8 -*-
"""
APP模块
专门为移动端APP提供API接口
"""

from .controller import app_router, app_user_router

__version__ = "1.0.0"
__author__ = "RuoYi Team"

__all__ = ["app_router", "app_user_router"] 