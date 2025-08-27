"""
订单相关数据对象实体类
"""

from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, Index
from sqlalchemy.sql import func
from datetime import datetime
from config.database import Base


class YozuanTaskOrder(Base):
    """任务订单表"""
    __tablename__ = "yozuan_task_order"
    
    order_id = Column(Integer, primary_key=True, autoincrement=True, comment="订单ID")
    task_id = Column(Integer, nullable=False, comment="任务ID")
    user_id = Column(Integer, nullable=False, comment="接单用户ID")
    order_status = Column(String(20), default="applied", comment="订单状态：applied/in_progress/completed/verified/rejected/cancelled")
    apply_time = Column(DateTime, default=func.now(), comment="报名时间")
    start_time = Column(DateTime, comment="开始时间")
    complete_time = Column(DateTime, comment="完成时间")
    verify_time = Column(DateTime, comment="验证时间")
    commission_amount = Column(DECIMAL(8, 2), comment="佣金金额")
    reject_reason = Column(Text, comment="驳回原因")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index("idx_task", "task_id"),
        Index("idx_user", "user_id"),
        Index("idx_status", "order_status"),
        Index("idx_apply_time", "apply_time"),
        Index("idx_order_composite", "user_id", "order_status", "apply_time"),
        {"comment": "游赚任务订单表"}
    )
    
    def __repr__(self):
        return f"<YozuanTaskOrder(order_id={self.order_id}, task_id={self.task_id}, user_id={self.user_id}, status='{self.order_status}')>"
