from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class AppUser(Base):
    """APP用户信息表"""
    __tablename__ = 'app_user'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    user_name = Column(String(30), nullable=False, unique=True, comment='用户账号')
    nick_name = Column(String(30), nullable=False, comment='用户昵称')
    email = Column(String(50), default='', comment='用户邮箱')
    phone = Column(String(11), default='', comment='手机号码')
    sex = Column(String(1), default='0', comment='用户性别（0男 1女 2未知）')
    avatar = Column(String(100), default='', comment='用户头像')
    password = Column(String(50), default='', comment='密码')
    status = Column(String(1), default='0', comment='帐号状态（0正常 1停用）')
    login_ip = Column(String(128), default='', comment='最后登录IP')
    login_date = Column(DateTime, default=None, comment='最后登录时间')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), default=None, comment='备注')


class AppUserProfile(Base):
    """APP用户详细信息表"""
    __tablename__ = 'app_user_profile'
    
    profile_id = Column(Integer, primary_key=True, autoincrement=True, comment='详细信息ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    real_name = Column(String(30), default='', comment='真实姓名')
    id_card = Column(String(18), default='', comment='身份证号')
    birthday = Column(Date, default=None, comment='出生日期')
    address = Column(String(200), default='', comment='居住地址')
    education = Column(String(20), default='', comment='学历')
    occupation = Column(String(50), default='', comment='职业')
    income_level = Column(String(20), default='', comment='收入水平')
    marital_status = Column(String(1), default='0', comment='婚姻状况（0未婚 1已婚 2离异 3丧偶）')
    emergency_contact = Column(String(30), default='', comment='紧急联系人')
    emergency_phone = Column(String(11), default='', comment='紧急联系电话')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class AppLoginLog(Base):
    """APP用户登录日志表"""
    __tablename__ = 'app_login_log'
    
    log_id = Column(Integer, primary_key=True, autoincrement=True, comment='访问ID')
    user_name = Column(String(50), default='', comment='用户账号')
    ipaddr = Column(String(128), default='', comment='登录IP地址')
    login_location = Column(String(255), default='', comment='登录地点')
    browser = Column(String(50), default='', comment='浏览器类型')
    os = Column(String(50), default='', comment='操作系统')
    status = Column(String(1), default='0', comment='登录状态（0成功 1失败）')
    msg = Column(String(255), default='', comment='提示消息')
    login_time = Column(DateTime, default=datetime.now, comment='访问时间')
