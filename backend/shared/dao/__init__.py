# -*- coding: utf-8 -*-
"""
数据访问层
包含所有数据访问对象(DAO)的基础定义和实现
"""
from .base_dao import BaseDAO
from .user_dao import UserDAO

__all__ = ["BaseDAO", "UserDAO"] 