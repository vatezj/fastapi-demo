# -*- coding: utf-8 -*-
"""
基础数据对象
所有数据库实体的基类
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseDO(Base):
    """基础数据对象"""
    
    __abstract__ = True
    
    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    
    # 创建时间
    create_time = Column(
        DateTime, 
        default=datetime.now, 
        comment="创建时间"
    )
    
    # 更新时间
    update_time = Column(
        DateTime, 
        default=datetime.now, 
        onupdate=datetime.now, 
        comment="更新时间"
    )
    
    # 逻辑删除标记 (0: 正常, 1: 删除)
    del_flag = Column(
        String(1), 
        default='0', 
        comment="逻辑删除标记"
    )
    
    # 创建者
    create_by = Column(
        String(64), 
        default='', 
        comment="创建者"
    )
    
    # 更新者
    update_by = Column(
        String(64), 
        default='', 
        comment="更新者"
    )
    
    # 备注
    remark = Column(
        String(500), 
        default='', 
        comment="备注"
    )
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(**data) 