import re
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import Network, NotBlank, Size, Xss
from typing import List, Literal, Optional, Union
from exceptions.exception import ModelValidatorException
from module_admin.annotation.pydantic_annotation import as_query


# 基础模型配置
class BaseAppUserModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)


# APP用户基础信息模型
class AppUserModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_id: Optional[int] = Field(default=None, description='用户ID')
    user_name: Optional[str] = Field(default=None, description='用户账号')
    nick_name: Optional[str] = Field(default=None, description='用户昵称')
    email: Optional[str] = Field(default=None, description='用户邮箱')
    phone: Optional[str] = Field(default=None, description='手机号码')
    sex: Optional[str] = Field(default=None, description='用户性别（0男 1女 2未知）')
    avatar: Optional[str] = Field(default=None, description='用户头像')
    password: Optional[str] = Field(default=None, description='密码')
    status: Optional[str] = Field(default=None, description='帐号状态（0正常 1停用）')
    login_ip: Optional[str] = Field(default=None, description='最后登录IP')
    login_date: Optional[datetime] = Field(default=None, description='最后登录时间')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')


# APP用户详细信息模型
class AppUserProfileModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    profile_id: Optional[int] = Field(default=None, description='详细信息ID')
    user_id: Optional[int] = Field(default=None, description='用户ID')
    real_name: Optional[str] = Field(default=None, description='真实姓名')
    id_card: Optional[str] = Field(default=None, description='身份证号')
    birthday: Optional[date] = Field(default=None, description='出生日期')
    address: Optional[str] = Field(default=None, description='居住地址')
    education: Optional[str] = Field(default=None, description='学历')
    occupation: Optional[str] = Field(default=None, description='职业')
    income_level: Optional[str] = Field(default=None, description='收入水平')
    marital_status: Optional[str] = Field(default=None, description='婚姻状况（0未婚 1已婚 2离异 3丧偶）')
    emergency_contact: Optional[str] = Field(default=None, description='紧急联系人')
    emergency_phone: Optional[str] = Field(default=None, description='紧急联系电话')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')


# APP登录日志模型
class AppLoginLogModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    log_id: Optional[int] = Field(default=None, description='访问ID')
    user_name: Optional[str] = Field(default=None, description='用户账号')
    ipaddr: Optional[str] = Field(default=None, description='登录IP地址')
    login_location: Optional[str] = Field(default=None, description='登录地点')
    browser: Optional[str] = Field(default=None, description='浏览器类型')
    os: Optional[str] = Field(default=None, description='操作系统')
    status: Optional[str] = Field(default=None, description='登录状态（0成功 1失败）')
    msg: Optional[str] = Field(default=None, description='提示消息')
    login_time: Optional[datetime] = Field(default=None, description='访问时间')


# APP用户完整信息模型（包含详细信息）
class AppUserInfoModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user: AppUserModel = Field(..., description='用户基础信息')
    profile: Optional[AppUserProfileModel] = Field(default=None, description='用户详细信息')


# APP当前用户信息模型
class AppCurrentUserModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_id: int = Field(..., description='用户ID')
    user_name: str = Field(..., description='用户账号')
    nick_name: str = Field(..., description='用户昵称')
    email: Optional[str] = Field(default=None, description='用户邮箱')
    phone: Optional[str] = Field(default=None, description='手机号码')
    sex: Optional[str] = Field(default=None, description='用户性别')
    avatar: Optional[str] = Field(default=None, description='用户头像')
    status: str = Field(..., description='帐号状态')
    login_ip: Optional[str] = Field(default=None, description='最后登录IP')
    login_date: Optional[datetime] = Field(default=None, description='最后登录时间')
    profile: Optional[AppUserProfileModel] = Field(default=None, description='用户详细信息')


# APP用户详情模型（用于查询单个用户）
class AppUserDetailModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user: AppUserModel = Field(..., description='用户基础信息')
    profile: Optional[AppUserProfileModel] = Field(default=None, description='用户详细信息')


# APP用户档案响应模型
class AppUserProfileResponseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    profile: AppUserProfileModel = Field(..., description='用户详细信息')


# APP用户查询模型
class AppUserQueryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_name: Optional[str] = Field(default=None, description='用户账号')
    nick_name: Optional[str] = Field(default=None, description='用户昵称')
    email: Optional[str] = Field(default=None, description='用户邮箱')
    phone: Optional[str] = Field(default=None, description='手机号码')
    sex: Optional[str] = Field(default=None, description='用户性别')
    status: Optional[str] = Field(default=None, description='帐号状态')
    begin_time: Optional[datetime] = Field(default=None, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')


# APP用户分页查询模型
class AppUserPageQueryModel(AppUserQueryModel):
    page_num: int = Field(1, description='页码')
    page_size: int = Field(10, description='每页数量')


# APP添加用户模型
class AppAddUserModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_name: str = Field(..., description='用户账号')
    nick_name: str = Field(..., description='用户昵称')
    email: Optional[str] = Field(default=None, description='用户邮箱')
    phone: Optional[str] = Field(default=None, description='手机号码')
    sex: Optional[str] = Field(default='0', description='用户性别')
    avatar: Optional[str] = Field(default=None, description='用户头像')
    password: str = Field(..., description='密码')
    status: Optional[str] = Field(default='0', description='帐号状态')
    remark: Optional[str] = Field(default=None, description='备注')
    
    # 详细信息
    real_name: Optional[str] = Field(default=None, description='真实姓名')
    id_card: Optional[str] = Field(default=None, description='身份证号')
    birthday: Optional[date] = Field(default=None, description='出生日期')
    address: Optional[str] = Field(default=None, description='居住地址')
    education: Optional[str] = Field(default=None, description='学历')
    occupation: Optional[str] = Field(default=None, description='职业')
    income_level: Optional[str] = Field(default=None, description='收入水平')
    marital_status: Optional[str] = Field(default=None, description='婚姻状况')
    emergency_contact: Optional[str] = Field(default=None, description='紧急联系人')
    emergency_phone: Optional[str] = Field(default=None, description='紧急联系电话')


# APP编辑用户模型
class AppEditUserModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_id: int = Field(..., description='用户ID')
    nick_name: Optional[str] = Field(default=None, description='用户昵称')
    email: Optional[str] = Field(default=None, description='用户邮箱')
    phone: Optional[str] = Field(default=None, description='手机号码')
    sex: Optional[str] = Field(default=None, description='用户性别')
    avatar: Optional[str] = Field(default=None, description='用户头像')
    status: Optional[str] = Field(default=None, description='帐号状态')
    remark: Optional[str] = Field(default=None, description='备注')
    
    # 详细信息
    real_name: Optional[str] = Field(default=None, description='真实姓名')
    id_card: Optional[str] = Field(default=None, description='身份证号')
    birthday: Optional[date] = Field(default=None, description='出生日期')
    address: Optional[str] = Field(default=None, description='居住地址')
    education: Optional[str] = Field(default=None, description='学历')
    occupation: Optional[str] = Field(default=None, description='职业')
    income_level: Optional[str] = Field(default=None, description='收入水平')
    marital_status: Optional[str] = Field(default=None, description='婚姻状况')
    emergency_contact: Optional[str] = Field(default=None, description='紧急联系人')
    emergency_phone: Optional[str] = Field(default=None, description='紧急联系电话')


# APP重置密码模型
class AppResetPasswordModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_id: int = Field(..., description='用户ID')
    password: str = Field(..., description='新密码')


# APP登录模型
class AppLoginModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_name: str = Field(..., description='用户账号')
    password: str = Field(..., description='密码')
    code: Optional[str] = Field(default=None, description='验证码')
    uuid: Optional[str] = Field(default=None, description='验证码标识')


# APP注册模型
class AppRegisterModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_name: str = Field(..., description='用户账号')
    nick_name: str = Field(..., description='用户昵称')
    email: Optional[str] = Field(default=None, description='用户邮箱')
    phone: Optional[str] = Field(default=None, description='手机号码')
    password: str = Field(..., description='密码')
    confirm_password: str = Field(..., description='确认密码')
    code: Optional[str] = Field(default=None, description='验证码')
    uuid: Optional[str] = Field(default=None, description='验证码标识')


# APP短信验证码模型
class AppSmsCodeModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    phone: str = Field(..., description='手机号码')
    type: str = Field(..., description='验证码类型（login:登录 register:注册 reset:重置）')


# APP用户状态模型
class AppUserStatusModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_id: int = Field(..., description='用户ID')
    status: str = Field(..., description='状态（0正常 1停用）')


# APP删除用户模型
class AppDeleteUserModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_ids: List[int] = Field(..., description='用户ID列表')


# APP登录日志查询模型
class AppLoginLogQueryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    user_name: Optional[str] = Field(default=None, description='用户账号')
    ipaddr: Optional[str] = Field(default=None, description='登录IP地址')
    status: Optional[str] = Field(default=None, description='登录状态')
    begin_time: Optional[datetime] = Field(default=None, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')


# APP登录日志分页查询模型
class AppLoginLogPageQueryModel(AppLoginLogQueryModel):
    page_num: int = Field(1, description='页码')
    page_size: int = Field(10, description='每页数量')


# APP登录日志响应模型
class AppLoginLogResponseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    
    log_id: int = Field(..., description='访问ID')
    user_name: str = Field(..., description='用户账号')
    ipaddr: str = Field(..., description='登录IP地址')
    login_location: str = Field(..., description='登录地点')
    browser: str = Field(..., description='浏览器类型')
    os: str = Field(..., description='操作系统')
    status: str = Field(..., description='登录状态')
    msg: str = Field(..., description='提示消息')
    login_time: datetime = Field(..., description='访问时间')


# 工具函数：转换为驼峰命名
def to_camel(string: str) -> str:
    """将下划线命名转换为驼峰命名"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
