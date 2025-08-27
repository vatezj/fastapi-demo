"""
任务相关数据对象实体类
"""

from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, JSON, Index
from sqlalchemy.sql import func
from datetime import datetime
from config.database import Base


class YozuanTask(Base):
    """任务主表"""
    __tablename__ = "yozuan_task"
    
    task_id = Column(Integer, primary_key=True, autoincrement=True, comment="任务ID")
    publisher_id = Column(Integer, nullable=False, comment="发布者用户ID")
    task_type_id = Column(Integer, nullable=False, comment="任务类型ID")
    task_name = Column(String(100), nullable=False, comment="任务名称")
    task_description = Column(Text, comment="任务详细描述")
    task_quantity = Column(Integer, nullable=False, comment="任务总数量")
    completed_quantity = Column(Integer, default=0, comment="已完成数量")
    task_price = Column(DECIMAL(8, 2), nullable=False, comment="任务单价")
    total_amount = Column(DECIMAL(10, 2), nullable=False, comment="任务总金额")
    service_fee = Column(DECIMAL(8, 2), nullable=False, comment="平台手续费")
    task_tag = Column(String(50), comment="推广项目标签")
    completion_hours = Column(Integer, nullable=False, comment="报名后完成时限（小时）")
    review_hours = Column(Integer, nullable=False, comment="验证后审核时限（小时）")
    device_limit = Column(String(20), default="all", comment="设备限制：all/android/ios")
    area_scope = Column(Integer, default=1, comment="地区范围类型：1=全国，2=单个城市，3=多个城市")
    single_area_code = Column(String(6), comment="单个城市编码（仅当area_scope=2时有效）")
    frequency_limit = Column(String(20), default="once", comment="限制次数：once/daily/thrice")
    task_status = Column(String(20), default="draft", comment="任务状态：draft/pending/active/paused/completed/cancelled")
    start_time = Column(DateTime, comment="任务开始时间")
    end_time = Column(DateTime, comment="任务结束时间")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        Index("idx_publisher", "publisher_id"),
        Index("idx_type", "task_type_id"),
        Index("idx_status", "task_status"),
        Index("idx_create_time", "create_time"),
        Index("idx_task_composite", "task_type_id", "task_status", "create_time"),
        {"comment": "游赚任务主表"}
    )
    
    def __repr__(self):
        return f"<YozuanTask(task_id={self.task_id}, task_name='{self.task_name}', status='{self.task_status}')>"


class YozuanTaskType(Base):
    """任务类型表"""
    __tablename__ = "yozuan_task_type"
    
    type_id = Column(Integer, primary_key=True, autoincrement=True, comment="任务类型ID")
    type_name = Column(String(50), nullable=False, comment="任务类型名称")
    type_code = Column(String(20), unique=True, nullable=False, comment="任务类型代码")
    min_price = Column(DECIMAL(8, 2), nullable=False, comment="最小单价")
    min_quantity = Column(Integer, nullable=False, comment="最小数量")
    icon_url = Column(String(255), comment="类型图标URL")
    description = Column(Text, comment="类型描述")
    sort_order = Column(Integer, default=0, comment="排序权重")
    status = Column(Integer, default=1, comment="状态：1启用，0禁用")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<YozuanTaskType(type_id={self.type_id}, type_name='{self.type_name}', type_code='{self.type_code}')>"


class YozuanTaskStep(Base):
    """任务步骤表"""
    __tablename__ = "yozuan_task_step"
    
    step_id = Column(Integer, primary_key=True, autoincrement=True, comment="步骤ID")
    task_id = Column(Integer, nullable=False, comment="任务ID")
    step_order = Column(Integer, nullable=False, comment="步骤顺序")
    step_title = Column(String(100), nullable=False, comment="步骤标题")
    step_description = Column(Text, comment="步骤描述")
    step_type = Column(String(20), nullable=False, comment="步骤类型：link/image/text")
    step_content = Column(Text, comment="步骤内容（链接、图片URL或文本）")
    is_required = Column(Integer, default=1, comment="是否必填：1必填，0可选")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    
    __table_args__ = (
        Index("idx_task", "task_id"),
        Index("idx_order", "task_id", "step_order"),
        {"comment": "游赚任务步骤表"}
    )
    
    def __repr__(self):
        return f"<YozuanTaskStep(step_id={self.step_id}, task_id={self.task_id}, step_title='{self.step_title}')>"


class YozuanTaskTag(Base):
    """任务标签表"""
    __tablename__ = "yozuan_task_tag"
    
    tag_id = Column(Integer, primary_key=True, autoincrement=True, comment="标签ID")
    tag_name = Column(String(50), nullable=False, comment="标签名称")
    tag_code = Column(String(20), unique=True, nullable=False, comment="标签代码")
    tag_category = Column(String(30), comment="标签分类")
    description = Column(Text, comment="标签描述")
    status = Column(Integer, default=1, comment="状态：1启用，0禁用")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    
    __table_args__ = (
        Index("idx_category", "tag_category"),
        Index("idx_status", "status"),
        {"comment": "游赚任务标签表"}
    )
    
    def __repr__(self):
        return f"<YozuanTaskTag(tag_id={self.tag_id}, tag_name='{self.tag_name}', tag_code='{self.tag_code}')>"


class YozuanTaskCityRel(Base):
    """任务城市关联表"""
    __tablename__ = "yozuan_task_city_rel"
    
    rel_id = Column(Integer, primary_key=True, autoincrement=True, comment="关联ID")
    task_id = Column(Integer, nullable=False, comment="任务ID")
    area_code = Column(String(6), nullable=False, comment="城市编码")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    
    __table_args__ = (
        Index("idx_task_city", "task_id", "area_code"),
        {"comment": "任务城市关联表"}
    )
    
    def __repr__(self):
        return f"<YozuanTaskCityRel(task_id={self.task_id}, area_code={self.area_code})>"
