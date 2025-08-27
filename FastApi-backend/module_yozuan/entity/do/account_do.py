"""
账户相关数据对象实体类
"""

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Index
from sqlalchemy.sql import func
from datetime import datetime
from config.database import Base


class YozuanUserAccount(Base):
    """用户账户表"""
    __tablename__ = "yozuan_user_account"
    
    account_id = Column(Integer, primary_key=True, autoincrement=True, comment="账户ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    balance = Column(DECIMAL(10, 2), default=0.00, comment="账户余额")
    frozen_amount = Column(DECIMAL(10, 2), default=0.00, comment="冻结金额")
    total_income = Column(DECIMAL(10, 2), default=0.00, comment="总收入")
    total_withdraw = Column(DECIMAL(10, 2), default=0.00, comment="总提现")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index("uk_user", "user_id", unique=True),
        {"comment": "游赚用户账户表"}
    )
    
    def __repr__(self):
        return f"<YozuanUserAccount(account_id={self.account_id}, user_id={self.user_id}, balance={self.balance})>"


class YozuanAccountTransaction(Base):
    """资金变动记录表"""
    __tablename__ = "yozuan_account_transaction"
    
    transaction_id = Column(Integer, primary_key=True, autoincrement=True, comment="交易ID")
    account_id = Column(Integer, nullable=False, comment="账户ID")
    transaction_type = Column(String(20), nullable=False, comment="交易类型：recharge/withdraw/task_commission/rebate/fee")
    amount = Column(DECIMAL(10, 2), nullable=False, comment="交易金额")
    balance_before = Column(DECIMAL(10, 2), nullable=False, comment="交易前余额")
    balance_after = Column(DECIMAL(10, 2), nullable=False, comment="交易后余额")
    description = Column(String(255), comment="交易描述")
    status = Column(String(20), default="pending", comment="交易状态：pending/success/failed")
    related_id = Column(Integer, comment="关联ID（任务ID、订单ID等）")
    
    # 充值相关字段
    payment_method = Column(String(20), comment="支付方式：alipay/wechat/bank")
    payment_channel = Column(String(20), comment="支付渠道：web/app/h5")
    
    # 提现相关字段
    withdraw_method = Column(String(20), comment="提现方式：alipay/wechat/bank")
    withdraw_account = Column(String(100), comment="提现账户（手机号、银行卡号等）")
    real_name = Column(String(50), comment="真实姓名")
    
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index("idx_account", "account_id"),
        Index("idx_type", "transaction_type"),
        Index("idx_status", "status"),
        Index("idx_create_time", "create_time"),
        Index("idx_transaction_composite", "account_id", "transaction_type", "create_time"),
        {"comment": "游赚账户交易记录表"}
    )
    
    def __repr__(self):
        return f"<YozuanAccountTransaction(transaction_id={self.transaction_id}, account_id={self.account_id}, type='{self.transaction_type}', amount={self.amount})>"
