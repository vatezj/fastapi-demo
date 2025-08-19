"""
游赚模块配置
"""

from pydantic_settings import BaseSettings
from typing import List


class YozuanSettings(BaseSettings):
    """
    游赚模块配置
    """
    
    # 模块开关
    yozuan_enabled: bool = True
    
    # 数据库配置
    yozuan_db_prefix: str = "yozuan_"
    
    # 任务配置
    yozuan_task_max_steps: int = 10  # 最大步骤数
    yozuan_task_max_verifications: int = 5  # 最大验证要求数
    yozuan_task_min_price: float = 0.01  # 最小任务价格
    yozuan_task_max_price: float = 10000.00  # 最大任务价格
    
    # 订单配置
    yozuan_order_max_completion_hours: int = 168  # 最大完成时限（7天）
    yozuan_order_max_review_hours: int = 72  # 最大审核时限（3天）
    
    # 账户配置
    yozuan_account_min_withdraw: float = 1.00  # 最小提现金额
    yozuan_account_max_withdraw: float = 50000.00  # 最大提现金额
    
    # 返佣配置
    yozuan_rebate_max_levels: int = 3  # 最大返佣层级
    yozuan_rebate_min_rate: float = 0.01  # 最小返佣比例
    yozuan_rebate_max_rate: float = 0.30  # 最大返佣比例
    
    # 缓存配置
    yozuan_cache_enabled: bool = True
    yozuan_cache_expire_seconds: int = 3600  # 缓存过期时间（1小时）
    
    # 文件上传配置
    yozuan_upload_max_size: int = 10 * 1024 * 1024  # 最大文件大小（10MB）
    yozuan_upload_allowed_types: List[str] = [".jpg", ".jpeg", ".png", ".gif"]  # 允许的文件类型
    
    # 通知配置
    yozuan_notification_enabled: bool = True
    yozuan_notification_channels: List[str] = ["email", "sms", "push"]  # 通知渠道
    
    class Config:
        env_prefix = "YOZUAN_"
        case_sensitive = False


# 创建配置实例
yozuan_config = YozuanSettings()
