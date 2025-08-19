"""
游赚模块切面处理包
包含权限控制、数据权限、操作日志等切面功能
"""

from .yozuan_auth import CheckYozuanInterfaceAuth, CheckYozuanRoleAuth

__all__ = [
    "CheckYozuanInterfaceAuth",
    "CheckYozuanRoleAuth"
]
