# -*- coding: utf-8 -*-
"""
用户数据对象
"""

from sqlalchemy import Column, String, Integer, DateTime, Text
from config.database import Base
from datetime import datetime

class UserDO(Base):
    """用户数据对象"""
    
    __tablename__ = "shared_user"
    
    # 用户ID
    user_id = Column(
        Integer, 
        primary_key=True, 
        autoincrement=True, 
        comment="用户ID"
    )
    
    # 用户名
    user_name = Column(
        String(50), 
        unique=True, 
        nullable=False, 
        comment="用户名"
    )
    
    # 昵称
    nick_name = Column(
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
    
    # 删除标志 (0: 存在, 2: 删除)
    del_flag = Column(
        String(1), 
        default='0', 
        comment="删除标志"
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
        String(1), 
        default='', 
        comment="创建者"
    )
    
    # 更新者
    update_by = Column(
        String(1), 
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
        return f"<User(user_id={self.user_id}, user_name={self.user_name}, email={self.email})>" 