# -*- coding: utf-8 -*-
"""
基础视图对象
所有视图对象的基类
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class BaseVO(BaseModel):
    """基础视图对象"""
    
    # 主键ID
    id: int = Field(..., description="主键ID")
    
    # 创建时间
    create_time: Optional[datetime] = Field(None, description="创建时间")
    
    # 更新时间
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    # 创建者
    create_by: Optional[str] = Field(None, description="创建者")
    
    # 更新者
    update_by: Optional[str] = Field(None, description="更新者")
    
    # 备注
    remark: Optional[str] = Field(None, description="备注")
    
    class Config:
        """Pydantic配置"""
        from_attributes = True  # 支持从ORM对象创建
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def to_dict(self, exclude_none: bool = True):
        """转换为字典"""
        data = self.dict()
        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}
        return data
    
    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建"""
        return cls.from_orm(obj) 