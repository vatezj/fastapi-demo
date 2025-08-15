from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from config.get_db import get_db
from ..dao.app_user_dao import AppUserDao, AppLoginLogDao
from ..entity.vo.app_user_vo import (
    AppAddUserModel, AppEditUserModel, AppUserQueryModel, AppUserPageQueryModel,
    AppResetPasswordModel, AppLoginModel, AppRegisterModel, AppSmsCodeModel,
    AppUserStatusModel, AppDeleteUserModel, AppLoginLogQueryModel, AppLoginLogPageQueryModel
)
from utils.response_util import ResponseUtil
from utils.pwd_util import PwdUtil
# 移除不存在的导入
from datetime import datetime


class AppUserService:
    """APP用户服务层"""
    
    @staticmethod
    async def create_user(
        user_data: AppAddUserModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """创建APP用户"""
        try:
            # 检查用户名是否已存在
            if await AppUserDao.check_username_exists(db, user_data.user_name):
                return ResponseUtil.error("用户名已存在")
            
            # 检查手机号是否已存在
            if user_data.phone and await AppUserDao.check_phone_exists(db, user_data.phone):
                return ResponseUtil.error("手机号已存在")
            
            # 检查邮箱是否已存在
            if user_data.email and await AppUserDao.check_email_exists(db, user_data.email):
                return ResponseUtil.error("邮箱已存在")
            
            # 加密密码
            hashed_password = PwdUtil.get_password_hash(user_data.password)
            
            # 准备用户数据
            user_dict = {
                'user_name': user_data.user_name,
                'nick_name': user_data.nick_name,
                'email': user_data.email,
                'phone': user_data.phone,
                'sex': user_data.sex,
                'avatar': user_data.avatar,
                'password': hashed_password,
                'status': user_data.status,
                'remark': user_data.remark,
                'create_time': datetime.now()
            }
            
            # 创建用户
            user = await AppUserDao.create_user(db, user_dict)
            
            # 如果有详细信息，创建用户档案
            if any([user_data.real_name, user_data.id_card, user_data.birthday, 
                   user_data.address, user_data.education, user_data.occupation,
                   user_data.income_level, user_data.marital_status,
                   user_data.emergency_contact, user_data.emergency_phone]):
                
                profile_dict = {
                    'user_id': user.user_id,
                    'real_name': user_data.real_name,
                    'id_card': user_data.id_card,
                    'birthday': user_data.birthday,
                    'address': user_data.address,
                    'education': user_data.education,
                    'occupation': user_data.occupation,
                    'income_level': user_data.income_level,
                    'marital_status': user_data.marital_status,
                    'emergency_contact': user_data.emergency_contact,
                    'emergency_phone': user_data.emergency_phone,
                    'create_time': datetime.now()
                }
                
                await AppUserDao.create_user_profile(db, profile_dict)
            
            return ResponseUtil.success("用户创建成功", data={'user_id': user.user_id})
            
        except Exception as e:
            return ResponseUtil.error(f"创建用户失败: {str(e)}")
    
    @staticmethod
    async def update_user(
        user_data: AppEditUserModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """更新APP用户信息"""
        try:
            # 检查用户是否存在
            user = await AppUserDao.get_user_by_id(db, user_data.user_id)
            if not user:
                return ResponseUtil.error("用户不存在")
            
            # 检查手机号是否已被其他用户使用
            if user_data.phone and await AppUserDao.check_phone_exists(db, user_data.phone, user_data.user_id):
                return ResponseUtil.error("手机号已被其他用户使用")
            
            # 检查邮箱是否已被其他用户使用
            if user_data.email and await AppUserDao.check_email_exists(db, user_data.email, user_data.user_id):
                return ResponseUtil.error("邮箱已被其他用户使用")
            
            # 准备更新数据
            update_dict = {
                'nick_name': user_data.nick_name,
                'email': user_data.email,
                'phone': user_data.phone,
                'sex': user_data.sex,
                'avatar': user_data.avatar,
                'remark': user_data.remark,
                'update_time': datetime.now()
            }
            
            # 移除None值
            update_dict = {k: v for k, v in update_dict.items() if v is not None}
            
            # 更新用户
            success = await AppUserDao.update_user(db, user_data.user_id, update_dict)
            
            if success:
                return ResponseUtil.success("用户更新成功")
            else:
                return ResponseUtil.error("用户更新失败")
                
        except Exception as e:
            return ResponseUtil.error(f"更新用户失败: {str(e)}")
    
    @staticmethod
    async def get_user_list(
        query_model: AppUserQueryModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """获取APP用户列表"""
        try:
            # 构建查询条件
            filters = {}
            if query_model.user_name:
                filters['user_name'] = query_model.user_name
            if query_model.email:
                filters['email'] = query_model.email
            if query_model.phone:
                filters['phone'] = query_model.phone
            if query_model.status:
                filters['status'] = query_model.status
            if query_model.sex:
                filters['sex'] = query_model.sex
            
            # 获取用户列表
            users = await AppUserDao.get_users(db, filters)
            
            return ResponseUtil.success("获取用户列表成功", data=users)
            
        except Exception as e:
            return ResponseUtil.error(f"获取用户列表失败: {str(e)}")
    
    @staticmethod
    async def get_user_page(
        page_query: AppUserPageQueryModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """分页获取APP用户列表"""
        try:
            # 获取分页数据
            result = await AppUserDao.get_users_page(
                db, 
                page_query.page_num, 
                page_query.page_size, 
                page_query.user_name,
                page_query.email,
                page_query.phone,
                page_query.status,
                page_query.sex
            )
            
            return ResponseUtil.success("获取用户分页成功", data=result)
            
        except Exception as e:
            return ResponseUtil.error(f"获取用户分页失败: {str(e)}")
    
    @staticmethod
    async def get_user_detail(
        user_id: int,
        db: AsyncSession
    ) -> ResponseUtil:
        """获取APP用户详情"""
        try:
            # 获取用户信息
            user = await AppUserDao.get_user_by_id(db, user_id)
            if not user:
                return ResponseUtil.error("用户不存在")
            
            # 获取用户档案信息
            profile = await AppUserDao.get_user_profile(db, user_id)
            
            # 构建返回数据
            user_info = {
                'user_id': user.user_id,
                'user_name': user.user_name,
                'nick_name': user.nick_name,
                'email': user.email,
                'phone': user.phone,
                'sex': user.sex,
                'avatar': user.avatar,
                'status': user.status,
                'login_ip': user.login_ip,
                'login_date': user.login_date,
                'create_time': user.create_time,
                'update_time': user.update_time,
                'remark': user.remark,
                'profile': profile
            }
            
            return ResponseUtil.success("获取用户详情成功", data=user_info)
            
        except Exception as e:
            return ResponseUtil.error(f"获取用户详情失败: {str(e)}")
    
    @staticmethod
    async def delete_user(
        delete_model: AppDeleteUserModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """删除APP用户"""
        try:
            # 检查用户是否存在
            user = await AppUserDao.get_user_by_id(db, delete_model.user_id)
            if not user:
                return ResponseUtil.error("用户不存在")
            
            # 删除用户
            success = await AppUserDao.delete_user(db, delete_model.user_id)
            
            if success:
                return ResponseUtil.success("用户删除成功")
            else:
                return ResponseUtil.error("用户删除失败")
                
        except Exception as e:
            return ResponseUtil.error(f"删除用户失败: {str(e)}")
    
    @staticmethod
    async def reset_password(
        reset_model: AppResetPasswordModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """重置APP用户密码"""
        try:
            # 检查用户是否存在
            user = await AppUserDao.get_user_by_id(db, reset_model.user_id)
            if not user:
                return ResponseUtil.error("用户不存在")
            
            # 加密新密码
            hashed_password = PwdUtil.get_password_hash(reset_model.new_password)
            
            # 更新密码
            success = await AppUserDao.update_user(db, reset_model.user_id, {
                'password': hashed_password,
                'update_time': datetime.now()
            })
            
            if success:
                return ResponseUtil.success("密码重置成功")
            else:
                return ResponseUtil.error("密码重置失败")
                
        except Exception as e:
            return ResponseUtil.error(f"重置密码失败: {str(e)}")
    
    @staticmethod
    async def change_user_status(
        status_model: AppUserStatusModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """更改APP用户状态"""
        try:
            # 检查用户是否存在
            user = await AppUserDao.get_user_by_id(db, status_model.user_id)
            if not user:
                return ResponseUtil.error("用户不存在")
            
            # 更新状态
            success = await AppUserDao.update_user(db, status_model.user_id, {
                'status': status_model.status,
                'update_time': datetime.now()
            })
            
            if success:
                status_text = "启用" if status_model.status == "0" else "停用"
                return ResponseUtil.success(f"用户{status_text}成功")
            else:
                return ResponseUtil.error("更改用户状态失败")
                
        except Exception as e:
            return ResponseUtil.error(f"更改用户状态失败: {str(e)}")
    
    @staticmethod
    async def app_login(
        login_data: AppLoginModel,
        request,
        db: AsyncSession
    ) -> ResponseUtil:
        """APP用户登录"""
        try:
            # 验证用户名和密码
            user = await AppUserDao.get_user_by_username(db, login_data.user_name)
            if not user:
                return ResponseUtil.error("用户名或密码错误")
            
            if not PwdUtil.verify_password(login_data.password, user.password):
                return ResponseUtil.error("用户名或密码错误")
            
            if user.status != "0":
                return ResponseUtil.error("用户已被停用")
            
            # 更新登录信息
            await AppUserDao.update_user(db, user.user_id, {
                'login_ip': request.client.host,
                'login_date': datetime.now(),
                'update_time': datetime.now()
            })
            
            # 记录登录日志
            log_data = {
                'user_name': user.user_name,
                'ipaddr': request.client.host,
                'status': '0',
                'msg': '登录成功',
                'login_time': datetime.now()
            }
            await AppLoginLogDao.create_login_log(db, log_data)
            
            # 构建用户信息
            user_info = {
                'user_id': user.user_id,
                'user_name': user.user_name,
                'nick_name': user.nick_name,
                'email': user.email,
                'phone': user.phone,
                'sex': user.sex,
                'avatar': user.avatar,
                'status': user.status,
                'login_ip': request.client.host,
                'login_date': datetime.now()
            }
            
            return ResponseUtil.success("登录成功", data=user_info)
            
        except Exception as e:
            return ResponseUtil.error(f"登录失败: {str(e)}")
    
    @staticmethod
    async def app_register(
        register_data: AppRegisterModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """APP用户注册"""
        try:
            # 验证密码确认
            if register_data.password != register_data.confirm_password:
                return ResponseUtil.error("两次输入的密码不一致")
            
            # 检查用户名是否已存在
            if await AppUserDao.check_username_exists(db, register_data.user_name):
                return ResponseUtil.error("用户名已存在")
            
            # 检查手机号是否已存在
            if register_data.phone and await AppUserDao.check_phone_exists(db, register_data.phone):
                return ResponseUtil.error("手机号已存在")
            
            # 检查邮箱是否已存在
            if register_data.email and await AppUserDao.check_email_exists(db, register_data.email):
                return ResponseUtil.error("邮箱已存在")
            
            # 创建用户
            user_dict = {
                'user_name': register_data.user_name,
                'nick_name': register_data.nick_name,
                'email': register_data.email,
                'phone': register_data.phone,
                'password': PwdUtil.get_password_hash(register_data.password),
                'status': '0',
                'create_time': datetime.now()
            }
            
            user = await AppUserDao.create_user(db, user_dict)
            
            return ResponseUtil.success("注册成功", data={'user_id': user.user_id})
            
        except Exception as e:
            return ResponseUtil.error(f"注册失败: {str(e)}")
    
    @staticmethod
    async def send_sms_code(
        sms_data: AppSmsCodeModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """发送短信验证码"""
        try:
            # 这里应该集成短信服务
            # 目前只是模拟发送成功
            return ResponseUtil.success("验证码发送成功", data={'code': '123456'})
            
        except Exception as e:
            return ResponseUtil.error(f"发送验证码失败: {str(e)}")
    
    @staticmethod
    async def get_login_logs(
        query_model: AppLoginLogQueryModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """获取登录日志"""
        try:
            # 构建查询条件
            filters = {}
            if query_model.user_name:
                filters['user_name'] = query_model.user_name
            if query_model.status:
                filters['status'] = query_model.status
            if query_model.start_time:
                filters['start_time'] = query_model.start_time
            if query_model.end_time:
                filters['end_time'] = query_model.end_time
            
            # 获取登录日志
            logs = await AppLoginLogDao.get_login_logs(db, filters)
            
            return ResponseUtil.success("获取登录日志成功", data=logs)
            
        except Exception as e:
            return ResponseUtil.error(f"获取登录日志失败: {str(e)}")
    
    @staticmethod
    async def get_login_logs_page(
        page_query: AppLoginLogPageQueryModel,
        db: AsyncSession
    ) -> ResponseUtil:
        """分页获取登录日志"""
        try:
            # 获取分页数据
            result = await AppLoginLogDao.get_login_logs_page(
                db,
                page_query.page_num,
                page_query.page_size,
                page_query.user_name,
                page_query.status,
                page_query.start_time,
                page_query.end_time
            )
            
            return ResponseUtil.success("获取登录日志分页成功", data=result)
            
        except Exception as e:
            return ResponseUtil.error(f"获取登录日志分页失败: {str(e)}")
