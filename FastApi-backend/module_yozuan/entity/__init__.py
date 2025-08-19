"""
游赚模块实体层
包含数据对象(DO)和视图对象(VO)的定义
"""

from .do.task_do import YozuanTask
from .do.order_do import YozuanTaskOrder
from .do.account_do import YozuanUserAccount
from .do.verification_do import YozuanTaskVerification, YozuanTaskVerificationSubmit
from .do.region_do import YozuanRegion, YozuanTaskRegion

__all__ = [
    "YozuanTask",
    "YozuanTaskOrder", 
    "YozuanUserAccount",
    "YozuanTaskVerification",
    "YozuanTaskVerificationSubmit",
    "YozuanRegion",
    "YozuanTaskRegion"
]
