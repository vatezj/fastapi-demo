"""
游赚项目任务相关枚举定义
用于替代数据库ENUM类型，提供更好的灵活性和可维护性
"""

from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待审核
    ACTIVE = "active"         # 进行中
    PAUSED = "paused"         # 已暂停
    COMPLETED = "completed"   # 已完成
    CANCELLED = "cancelled"   # 已取消


class TaskStepType(str, Enum):
    """任务步骤类型枚举"""
    LINK = "link"     # 链接
    IMAGE = "image"   # 图片
    TEXT = "text"     # 文本


class TaskVerificationType(str, Enum):
    """任务验证类型枚举"""
    IMAGE = "image"   # 仅图片
    TEXT = "text"     # 仅文本
    BOTH = "both"     # 图片和文本都需要


class TaskOrderStatus(str, Enum):
    """任务订单状态枚举"""
    APPLIED = "applied"           # 已报名
    IN_PROGRESS = "in_progress"   # 进行中
    COMPLETED = "completed"       # 已完成
    VERIFIED = "verified"         # 已验证
    REJECTED = "rejected"         # 已驳回
    CANCELLED = "cancelled"       # 已取消


class ReviewStatus(str, Enum):
    """审核状态枚举"""
    PENDING = "pending"   # 待审核
    APPROVED = "approved" # 已通过
    REJECTED = "rejected" # 已驳回


class DeviceLimit(str, Enum):
    """设备限制枚举"""
    ALL = "all"         # 全部设备
    ANDROID = "android" # 仅安卓
    IOS = "ios"         # 仅iOS


class FrequencyLimit(str, Enum):
    """限制次数枚举"""
    ONCE = "once"       # 每人一次
    DAILY = "daily"     # 每日一次
    THRICE = "thrice"   # 每人三次


class TransactionType(str, Enum):
    """交易类型枚举"""
    RECHARGE = "recharge"           # 充值
    WITHDRAW = "withdraw"           # 提现
    TASK_COMMISSION = "task_commission"  # 任务佣金
    REBATE = "rebate"               # 返佣
    FEE = "fee"                     # 手续费
    TASK_FREEZE = "task_freeze"     # 任务冻结
    TASK_UNFREEZE = "task_unfreeze" # 任务解冻


class TransactionStatus(str, Enum):
    """交易状态枚举"""
    PENDING = "pending" # 处理中
    SUCCESS = "success" # 成功
    FAILED = "failed"   # 失败


class RebateSource(str, Enum):
    """返佣来源枚举"""
    TASK_FEE = "task_fee"   # 任务手续费
    COMMISSION = "commission"  # 任务佣金


class FeeType(str, Enum):
    """手续费类型枚举"""
    FIXED = "fixed"         # 固定金额
    PERCENTAGE = "percentage"  # 百分比


# 枚举值到显示名称的映射
TASK_STATUS_DISPLAY = {
    TaskStatus.DRAFT: "草稿",
    TaskStatus.PENDING: "待审核",
    TaskStatus.ACTIVE: "进行中",
    TaskStatus.PAUSED: "已暂停",
    TaskStatus.COMPLETED: "已完成",
    TaskStatus.CANCELLED: "已取消"
}

TASK_STEP_TYPE_DISPLAY = {
    TaskStepType.LINK: "链接",
    TaskStepType.IMAGE: "图片",
    TaskStepType.TEXT: "文本"
}

TASK_VERIFICATION_TYPE_DISPLAY = {
    TaskVerificationType.IMAGE: "仅图片",
    TaskVerificationType.TEXT: "仅文本",
    TaskVerificationType.BOTH: "图片和文本"
}

TASK_ORDER_STATUS_DISPLAY = {
    TaskOrderStatus.APPLIED: "已报名",
    TaskOrderStatus.IN_PROGRESS: "进行中",
    TaskOrderStatus.COMPLETED: "已完成",
    TaskOrderStatus.VERIFIED: "已验证",
    TaskOrderStatus.REJECTED: "已驳回",
    TaskOrderStatus.CANCELLED: "已取消"
}

REVIEW_STATUS_DISPLAY = {
    ReviewStatus.PENDING: "待审核",
    ReviewStatus.APPROVED: "已通过",
    ReviewStatus.REJECTED: "已驳回"
}

DEVICE_LIMIT_DISPLAY = {
    DeviceLimit.ALL: "全部设备",
    DeviceLimit.ANDROID: "仅安卓",
    DeviceLimit.IOS: "仅iOS"
}

FREQUENCY_LIMIT_DISPLAY = {
    FrequencyLimit.ONCE: "每人一次",
    FrequencyLimit.DAILY: "每日一次",
    FrequencyLimit.THRICE: "每人三次"
}

TRANSACTION_TYPE_DISPLAY = {
    TransactionType.RECHARGE: "充值",
    TransactionType.WITHDRAW: "提现",
    TransactionType.TASK_COMMISSION: "任务佣金",
    TransactionType.REBATE: "返佣",
    TransactionType.FEE: "手续费",
    TransactionType.TASK_FREEZE: "任务冻结",
    TransactionType.TASK_UNFREEZE: "任务解冻"
}

TRANSACTION_STATUS_DISPLAY = {
    TransactionStatus.PENDING: "处理中",
    TransactionStatus.SUCCESS: "成功",
    TransactionStatus.FAILED: "失败"
}

REBATE_SOURCE_DISPLAY = {
    RebateSource.TASK_FEE: "任务手续费",
    RebateSource.COMMISSION: "任务佣金"
}

FEE_TYPE_DISPLAY = {
    FeeType.FIXED: "固定金额",
    FeeType.PERCENTAGE: "百分比"
}


def get_display_name(enum_value, display_mapping):
    """获取枚举值的显示名称"""
    return display_mapping.get(enum_value, str(enum_value))


def get_enum_by_display_name(display_name, enum_class, display_mapping):
    """根据显示名称获取枚举值"""
    for enum_value, name in display_mapping.items():
        if name == display_name:
            return enum_value
    return None


def get_enum_choices(enum_class, display_mapping):
    """获取枚举的选择项列表，用于表单和API"""
    return [(value.value, name) for value, name in display_mapping.items()]
