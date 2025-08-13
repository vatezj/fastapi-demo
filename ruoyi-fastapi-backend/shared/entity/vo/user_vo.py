# -*- coding: utf-8 -*-
"""
用户视图对象
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from shared.entity.base.base_vo import BaseVO

class UserBaseVO(BaseVO):
    """用户基础视图对象"""
    
    # 用户名
    username: str = Field(..., description="用户名")
    
    # 昵称
    nickname: Optional[str] = Field(None, description="昵称")
    
    # 邮箱
    email: str = Field(..., description="邮箱")
    
    # 手机号
    phone: Optional[str] = Field(None, description="手机号")
    
    # 头像
    avatar: Optional[str] = Field(None, description="头像")
    
    # 性别
    sex: Optional[str] = Field(None, description="性别")
    
    # 状态
    status: str = Field(..., description="状态")
    
    # 部门ID
    dept_id: Optional[int] = Field(None, description="部门ID")
    
    # 岗位ID
    post_id: Optional[int] = Field(None, description="岗位ID")
    
    # 个人简介
    profile: Optional[str] = Field(None, description="个人简介")

class UserCreateVO(BaseModel):
    """用户创建视图对象"""
    
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    email: EmailStr = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    sex: Optional[str] = Field(None, pattern=r'^[012]$', description="性别")
    dept_id: Optional[int] = Field(None, description="部门ID")
    post_id: Optional[int] = Field(None, description="岗位ID")
    profile: Optional[str] = Field(None, max_length=500, description="个人简介")

class UserUpdateVO(BaseModel):
    """用户更新视图对象"""
    
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    sex: Optional[str] = Field(None, pattern=r'^[012]$', description="性别")
    avatar: Optional[str] = Field(None, max_length=255, description="头像")
    dept_id: Optional[int] = Field(None, description="部门ID")
    post_id: Optional[int] = Field(None, description="岗位ID")
    profile: Optional[str] = Field(None, max_length=500, description="个人简介")
    status: Optional[str] = Field(None, pattern=r'^[01]$', description="状态")

class UserPasswordVO(BaseModel):
    """用户密码视图对象"""
    
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    confirm_password: str = Field(..., description="确认密码")
    
    def validate_passwords(self):
        """验证密码"""
        if self.new_password != self.confirm_password:
            raise ValueError("新密码和确认密码不一致")
        if self.old_password == self.new_password:
            raise ValueError("新密码不能与旧密码相同")
        return True 