"""
地区相关实体类
"""

from sqlalchemy import Column, String, Integer, DateTime, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()


class YozuanRegion(Base):
    """地区表"""
    __tablename__ = "yozuan_region"
    
    region_code = Column(String(6), primary_key=True, comment="地区编码")
    region_name = Column(String(50), nullable=False, comment="地区名称")
    region_level = Column(Enum('country', 'province', 'city', 'county', name='region_level_enum'), 
                         nullable=False, comment="地区级别")
    parent_code = Column(String(6), comment="上级地区编码")
    full_name = Column(String(200), comment="完整地区名称路径")
    sort_order = Column(Integer, default=0, comment="排序")
    status = Column(Integer, default=1, comment="状态：1启用，0禁用")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    __table_args__ = {
        'comment': '地区表'
    }
    
    def __repr__(self):
        return f"<YozuanRegion(region_code={self.region_code}, region_name={self.region_name}, level={self.region_level})>"


class YozuanTaskRegion(Base):
    """任务地区关联表"""
    __tablename__ = "yozuan_task_region"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    task_id = Column(Integer, nullable=False, comment="任务ID")
    region_code = Column(String(6), nullable=False, comment="地区编码")
    region_level = Column(Enum('country', 'province', 'city', 'county', name='region_level_enum'), 
                         nullable=False, comment="地区级别")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    __table_args__ = {
        'comment': '任务地区关联表'
    }
    
    def __repr__(self):
        return f"<YozuanTaskRegion(id={self.id}, task_id={self.task_id}, region_code={self.region_code})>"
