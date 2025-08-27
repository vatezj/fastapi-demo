"""
验证相关数据对象实体类
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from sqlalchemy.sql import func
from datetime import datetime
from config.database import Base


class YozuanTaskVerification(Base):
    """任务验证表"""
    __tablename__ = "yozuan_task_verification"
    
    verification_id = Column(Integer, primary_key=True, autoincrement=True, comment="验证ID")
    task_id = Column(Integer, nullable=False, comment="任务ID")
    verification_title = Column(String(100), nullable=False, comment="验证标题")
    verification_description = Column(Text, comment="验证说明")
    verification_type = Column(String(20), nullable=False, comment="验证类型：image/text/both")
    image_required = Column(Integer, default=0, comment="是否需要图片：1需要，0不需要")
    text_required = Column(Integer, default=0, comment="是否需要文本：1需要，0不需要")
    text_placeholder = Column(String(255), comment="文本输入提示")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    
    __table_args__ = (
        Index("idx_task", "task_id"),
        {"comment": "游赚任务验证表"}
    )
    
    def __repr__(self):
        return f"<YozuanTaskVerification(verification_id={self.verification_id}, task_id={self.task_id}, title='{self.verification_title}')>"


class YozuanTaskVerificationSubmit(Base):
    """任务验证提交表"""
    __tablename__ = "yozuan_task_verification_submit"
    
    submit_id = Column(Integer, primary_key=True, autoincrement=True, comment="提交ID")
    order_id = Column(Integer, nullable=False, comment="订单ID")
    submit_data = Column(JSON, nullable=False, comment="提交的验证数据，包含所有验证内容")
    submit_time = Column(DateTime, default=func.now(), comment="提交时间")
    review_status = Column(String(20), default="pending", comment="审核状态：pending/approved/rejected")
    review_time = Column(DateTime, comment="审核时间")
    review_user_id = Column(Integer, comment="审核用户ID")
    review_comment = Column(Text, comment="审核意见")
    
    __table_args__ = (
        Index("idx_order", "order_id"),
        Index("idx_status", "review_status"),
        {"comment": "游赚任务验证提交表"}
    )
    
    def __repr__(self):
        return f"<YozuanTaskVerificationSubmit(submit_id={self.submit_id}, order_id={self.order_id}, status='{self.review_status}')>"
