"""
邀请和分销相关数据实体
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared.entity.base.base_do import BaseDO


class YozuanUserInvitation(BaseDO):
    """用户邀请关系表"""
    __tablename__ = "yozuan_user_invitation"
    
    invitation_id = Column(Integer, primary_key=True, autoincrement=True, comment="邀请ID")
    inviter_id = Column(Integer, ForeignKey("app_user.user_id"), nullable=False, comment="邀请人用户ID")
    invitee_id = Column(Integer, ForeignKey("app_user.user_id"), nullable=False, comment="被邀请人用户ID")
    invitation_code = Column(String(32), nullable=False, comment="邀请码")
    invitation_time = Column(DateTime, default=func.now(), comment="邀请时间")
    accept_time = Column(DateTime, nullable=True, comment="接受邀请时间")
    status = Column(String(20), default="pending", comment="邀请状态：pending-待接受, accepted-已接受, expired-已过期")
    level = Column(Integer, default=1, comment="邀请层级：1-一级, 2-二级, 3-三级")
    parent_invitation_id = Column(Integer, ForeignKey("yozuan_user_invitation.invitation_id"), nullable=True, comment="上级邀请ID")
    
    # 关系
    inviter = relationship("AppUser", foreign_keys=[inviter_id], backref="sent_invitations")
    invitee = relationship("AppUser", foreign_keys=[invitee_id], backref="received_invitations")
    parent_invitation = relationship("YozuanUserInvitation", remote_side=[invitation_id], backref="child_invitations")
    
    __table_args__ = (
        Index("idx_inviter_id", "inviter_id"),
        Index("idx_invitee_id", "invitee_id"),
        Index("idx_invitation_code", "invitation_code"),
        Index("idx_parent_invitation_id", "parent_invitation_id"),
        Index("idx_status", "status"),
        Index("idx_level", "level"),
        {"comment": "用户邀请关系表"}
    )
    
    def __repr__(self):
        return f"<YozuanUserInvitation(invitation_id={self.invitation_id}, inviter_id={self.inviter_id}, invitee_id={self.invitee_id}, level={self.level})>"


class YozuanRebateConfig(BaseDO):
    """返佣配置表"""
    __tablename__ = "yozuan_rebate_config"
    
    config_id = Column(Integer, primary_key=True, autoincrement=True, comment="配置ID")
    level = Column(Integer, nullable=False, comment="返佣层级：1-一级, 2-二级, 3-三级")
    rebate_rate = Column(DECIMAL(5, 4), nullable=False, comment="返佣比例：0.0001-1.0000")
    min_amount = Column(DECIMAL(10, 2), default=0.00, comment="最小返佣金额")
    max_amount = Column(DECIMAL(10, 2), nullable=True, comment="最大返佣金额")
    status = Column(String(20), default="enabled", comment="状态：enabled-启用, disabled-禁用")
    description = Column(Text, nullable=True, comment="配置说明")
    
    __table_args__ = (
        Index("idx_level", "level"),
        Index("idx_status", "status"),
        {"comment": "返佣配置表"}
    )
    
    def __repr__(self):
        return f"<YozuanRebateConfig(config_id={self.config_id}, level={self.level}, rebate_rate={self.rebate_rate})>"


class YozuanRebateRecord(BaseDO):
    """返佣记录表"""
    __tablename__ = "yozuan_rebate_record"
    
    record_id = Column(Integer, primary_key=True, autoincrement=True, comment="记录ID")
    order_id = Column(Integer, ForeignKey("yozuan_task_order.order_id"), nullable=False, comment="任务订单ID")
    inviter_id = Column(Integer, ForeignKey("app_user.user_id"), nullable=False, comment="邀请人用户ID")
    invitee_id = Column(Integer, ForeignKey("app_user.user_id"), nullable=False, comment="被邀请人用户ID")
    task_id = Column(Integer, ForeignKey("yozuan_task.task_id"), nullable=False, comment="任务ID")
    rebate_amount = Column(DECIMAL(10, 2), nullable=False, comment="返佣金额")
    rebate_rate = Column(DECIMAL(5, 4), nullable=False, comment="返佣比例")
    level = Column(Integer, nullable=False, comment="返佣层级：1-一级, 2-二级, 3-三级")
    rebate_source = Column(String(20), default="task_completion", comment="返佣来源：task_completion-任务完成, task_publish-任务发布")
    status = Column(String(20), default="pending", comment="状态：pending-待处理, processed-已处理, failed-处理失败")
    process_time = Column(DateTime, nullable=True, comment="处理时间")
    remark = Column(Text, nullable=True, comment="备注")
    
    # 关系
    order = relationship("YozuanTaskOrder", backref="rebate_records")
    inviter = relationship("AppUser", foreign_keys=[inviter_id], backref="rebate_records")
    invitee = relationship("AppUser", foreign_keys=[invitee_id], backref="received_rebates")
    task = relationship("YozuanTask", backref="rebate_records")
    
    __table_args__ = (
        Index("idx_order_id", "order_id"),
        Index("idx_inviter_id", "inviter_id"),
        Index("idx_invitee_id", "invitee_id"),
        Index("idx_task_id", "task_id"),
        Index("idx_level", "level"),
        Index("idx_status", "status"),
        Index("idx_rebate_source", "rebate_source"),
        {"comment": "返佣记录表"}
    )
    
    def __repr__(self):
        return f"<YozuanRebateRecord(record_id={self.record_id}, order_id={self.order_id}, inviter_id={self.inviter_id}, rebate_amount={self.rebate_amount})>"
