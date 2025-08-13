# -*- coding: utf-8 -*-
"""
用户数据对象
"""

from sqlalchemy import Column, String, Integer, DateTime, Text
from shared.entity.base.base_do import BaseDO

class UserDO(BaseDO):
    """用户数据对象"""
    
    __tablename__ = "sys_user"
    
    # 用户名
    username = Column(
        String(50), 
        unique=True, 
        nullable=False, 
        comment="用户名"
    )
    
    # 昵称
    nickname = Column(
        String(50), 
        default='', 
        comment="昵称"
    )
    
    # 邮箱
    email = Column(
        String(100), 
        unique=True, 
        nullable=False, 
        comment="邮箱"
    )
    
    # 手机号
    phone = Column(
        String(11), 
        default='', 
        comment="手机号"
    )
    
    # 密码
    password = Column(
        String(100), 
        nullable=False, 
        comment="密码"
    )
    
    # 头像
    avatar = Column(
        String(255), 
        default='', 
        comment="头像"
    )
    
    # 性别 (0: 未知, 1: 男, 2: 女)
    sex = Column(
        String(1), 
        default='0', 
        comment="性别"
    )
    
    # 状态 (0: 正常, 1: 停用)
    status = Column(
        String(1), 
        default='0', 
        comment="状态"
    )
    
    # 最后登录时间
    login_date = Column(
        DateTime, 
        comment="最后登录时间"
    )
    
    # 最后登录IP
    login_ip = Column(
        String(128), 
        default='', 
        comment="最后登录IP"
    )
    
    # 部门ID
    dept_id = Column(
        Integer, 
        comment="部门ID"
    )
    
    # 岗位ID
    post_id = Column(
        Integer, 
        comment="岗位ID"
    )
    
    # 个人简介
    profile = Column(
        Text, 
        comment="个人简介"
    )
    
    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>" 