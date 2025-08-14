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
        db: AsyncSession = Depends(get_db)
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
            hashed_password = PwdUtil.hash_password(user_data.password)
            
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
        db: AsyncSession = Depends(get_db)
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
            user_update_data = {}
            if user_data.nick_name is not None:
                user_update_data['nick_name'] = user_data.nick_name
            if user_data.email is not None:
                user_update_data['email'] = user_data.email
            if user_data.phone is not None:
                user_update_data['phone'] = user_data.phone
            if user_data.sex is not None:
                user_update_data['sex'] = user_data.sex
            if user_data.avatar is not None:
                user_update_data['avatar'] = user_data.avatar
            if user_data.status is not None:
                user_update_data['status'] = user_data.status
            if user_data.remark is not None:
                user_update_data['remark'] = user_data.remark
            user_update_data['update_time'] = datetime.now()
            
            # 更新用户信息
            if user_update_data:
                await AppUserDao.update_user(db, user_data.user_id, user_update_data)
            
            # 更新或创建用户档案
            profile_update_data = {}
            if user_data.real_name is not None:
                profile_update_data['real_name'] = user_data.real_name
            if user_data.id_card is not None:
                profile_update_data['id_card'] = user_data.id_card
            if user_data.birthday is not None:
                profile_update_data['birthday'] = user_data.birthday
            if user_data.address is not None:
                profile_update_data['address'] = user_data.address
            if user_data.education is not None:
                profile_update_data['education'] = user_data.education
            if user_data.occupation is not None:
                profile_update_data['occupation'] = user_data.occupation
            if user_data.income_level is not None:
                profile_update_data['income_level'] = user_data.income_level
            if user_data.marital_status is not None:
                profile_update_data['marital_status'] = user_data.marital_status
            if user_data.emergency_contact is not None:
                profile_update_data['emergency_contact'] = user_data.emergency_contact
            if user_data.emergency_phone is not None:
                profile_update_data['emergency_phone'] = user_data.emergency_phone
            
            if profile_update_data:
                profile_update_data['update_time'] = datetime.now()
                
                # 检查是否已有档案，如果没有则创建
                existing_profile = await AppUserDao.get_user_with_profile(db, user_data.user_id)
                if existing_profile and existing_profile['profile']:
                    await AppUserDao.update_user_profile(db, user_data.user_id, profile_update_data)
                else:
                    profile_update_data['user_id'] = user_data.user_id
                    profile_update_data['create_time'] = datetime.now()
                    await AppUserDao.create_user_profile(db, profile_update_data)
            
            return ResponseUtil.success("用户信息更新成功")
            
        except Exception as e:
            return ResponseUtil.error(f"更新用户信息失败: {str(e)}")
    
    @staticmethod
    async def delete_user(
        user_ids: List[int],
        db: AsyncSession = Depends(get_db)
    ) -> ResponseUtil:
        """删除APP用户"""
        try:
            if not user_ids:
                return ResponseUtil.error("请选择要删除的用户")
            
            # 批量删除用户
            success = await AppUserDao.delete_users(db, user_ids)
            if success:
                return ResponseUtil.success("用户删除成功")
            else:
                return ResponseUtil.error("用户删除失败")
                
        except Exception as e:
            return ResponseUtil.error(f"删除用户失败: {str(e)}")
    
    @staticmethod
    async def change_user_status(
        user_data: AppUserStatusModel,
        db: AsyncSession = Depends(get_db)
    ) -> ResponseUtil:
        """修改用户状态"""
        try:
            # 检查用户是否存在
            user = await AppUserDao.get_user_by_id(db, user_data.user_id)
            if not user:
                return ResponseUtil.error("用户不存在")
            
            # 更新用户状态
            success = await AppUserDao.update_user_status(db, user_data.user_id, user_data.status)
            if success:
                status_text = "启用" if user_data.status == '0' else "停用"
                return ResponseUtil.success(f"用户{status_text}成功")
            else:
                return ResponseUtil.error("状态修改失败")
                
        except Exception as e:
            return ResponseUtil.error(f"修改用户状态失败: {str(e)}")
    
    @staticmethod
    async def reset_user_password(
        password_data: AppResetPasswordModel,
        db: AsyncSession = Depends(get_db)
    ) -> ResponseUtil:
        """重置用户密码"""
        try:
            # 检查用户是否存在
            user = await AppUserDao.get_user_by_id(db, password_data.user_id)
            if not user:
                return ResponseUtil.error("用户不存在")
            
            # 加密新密码
            hashed_password = PwdUtil.hash_password(password_data.password)
            
            # 更新密码
            success = await AppUserDao.update_user_password(db, password_data.user_id, hashed_password)
            if success:
                return ResponseUtil.success("密码重置成功")
            else:
                return ResponseUtil.error("密码重置失败")
                
        except Exception as e:
            return ResponseUtil.error(f"重置密码失败: {str(e)}")
    
    @staticmethod
    async def get_user_list(
        query: AppUserPageQueryModel,
        db: AsyncSession = Depends(get_db)
    ) -> ResponseUtil:
        """获取用户列表（分页）"""
        try:
            # 获取用户列表
            users = await AppUserDao.get_user_list(db, query)
            
            # 获取总数
            total = await AppUserDao.get_user_count(db, query)
            
            # 计算分页信息
            page_info = {
                'page_num': query.page_num,
                'page_size': query.page_size,
                'total': total,
                'pages': (total + query.page_size - 1) // query.page_size
            }
            
            return ResponseUtil.success("获取用户列表成功", data={
                'list': users,
                'page_info': page_info
            })
            
        except Exception as e:
            return ResponseUtil.error(f"获取用户列表失败: {str(e)}")
    
    @staticmethod
    async def get_user_detail(
        user_id: int,
        db: AsyncSession = Depends(get_db)
    ) -> ResponseUtil:
        """获取用户详情"""
        try:
            user_info = await AppUserDao.get_user_with_profile(db, user_id)
            if not user_info:
                return ResponseUtil.error("用户不存在")
            
            return ResponseUtil.success("获取用户详情成功", data=user_info)
            
        except Exception as e:
            return ResponseUtil.error(f"获取用户详情失败: {str(e)}")
    
    @staticmethod
    async def app_login(
        login_data: AppLoginModel,
        request,
        db: AsyncSession = Depends(get_db)
    ) -> ResponseUtil:
        """APP用户登录"""
        try:
            # 验证用户名和密码
            user = await AppUserDao.get_user_by_username(db, login_data.user_name)
            if not user:
                return ResponseUtil.error("用户名或密码错误")
            
            if user.status != '0':
                return ResponseUtil.error("用户已被停用")
            
            if not PwdUtil.verify_password(login_data.password, user.password):
                return ResponseUtil.error("用户名或密码错误")
            
            # 获取客户端信息
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            # 更新登录信息
            await AppUserDao.update_login_info(db, user.user_id, client_ip)
            
            # 记录登录日志
            log_data = {
                'user_name': user.user_name,
                'ipaddr': client_ip,
                'login_location': '',  # 可以通过IP地址解析地理位置
                'browser': user_agent.get('browser', ''),
                'os': user_agent.get('os', ''),
                'status': '0',  # 登录成功
                'msg': '登录成功',
                'login_time': datetime.now()
            }
            await AppLoginLogDao.create_login_log(db, log_data)
            
            # 返回用户信息（不包含密码）
            user_info = {
                'user_id': user.user_id,
                'user_name': user.user_name,
                'nick_name': user.nick_name,
                'email': user.email,
                'phone': user.phone,
                'sex': user.sex,
                'avatar': user.avatar,
                'status': user.status,
                'login_ip': client_ip,
                'login_date': datetime.now()
            }
            
            return ResponseUtil.success("登录成功", data=user_info)
            
        except Exception as e:
            return ResponseUtil.error(f"登录失败: {str(e)}")
    
    @staticmethod
    async def app_register(
        register_data: AppRegisterModel,
        db: AsyncSession = Depends(get_db)
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
                'password': PwdUtil.hash_password(register_data.password),
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
        db: AsyncSession = Depends(get_db)
    ) -> ResponseUtil:
        """发送短信验证码"""
        try:
            # 这里应该集成短信服务商的API
            # 目前只是模拟发送
            code = "123456"  # 实际应该是随机生成的验证码
            
            # 可以将验证码存储到Redis中，设置过期时间
            # await redis.set(f"sms_code:{sms_data.phone}:{sms_data.type}", code, ex=300)
            
            return ResponseUtil.success("验证码发送成功", data={'code': code})
            
        except Exception as e:
            return ResponseUtil.error(f"发送验证码失败: {str(e)}")


class AppLoginLogService:
    """APP登录日志服务层"""
    
    @staticmethod
    async def get_login_log_list(
        query: AppLoginLogPageQueryModel,
        db: AsyncSession = Depends(get_db)
    ) -> ResponseUtil:
        """获取登录日志列表（分页）"""
        try:
            # 获取登录日志列表
            logs = await AppLoginLogDao.get_login_log_list(
                db, query, query.page_num, query.page_size
            )
            
            # 获取总数
            total = await AppLoginLogDao.get_login_log_count(db, query)
            
            # 计算分页信息
            page_info = {
                'page_num': query.page_num,
                'page_size': query.page_size,
                'total': total,
                'pages': (total + query.page_size - 1) // query.page_size
            }
            
            return ResponseUtil.success("获取登录日志成功", data={
                'list': logs,
                'page_info': page_info
            })
            
        except Exception as e:
            return ResponseUtil.error(f"获取登录日志失败: {str(e)}")
    
    @staticmethod
    async def delete_login_logs(
        log_ids: List[int],
        db: AsyncSession = Depends(get_db)
    ) -> ResponseUtil:
        """删除登录日志"""
        try:
            if not log_ids:
                return ResponseUtil.error("请选择要删除的日志")
            
            success = await AppLoginLogDao.delete_login_logs(db, log_ids)
            if success:
                return ResponseUtil.success("日志删除成功")
            else:
                return ResponseUtil.error("日志删除失败")
                
        except Exception as e:
            return ResponseUtil.error(f"删除日志失败: {str(e)}")
    
    @staticmethod
    async def clean_login_logs(
        days: int = 30,
        db: AsyncSession = Depends(get_db)
    ) -> ResponseUtil:
        """清理登录日志"""
        try:
            success = await AppLoginLogDao.clean_login_logs(db, days)
            if success:
                return ResponseUtil.success(f"成功清理{days}天前的登录日志")
            else:
                return ResponseUtil.error("清理登录日志失败")
                
        except Exception as e:
            return ResponseUtil.error(f"清理登录日志失败: {str(e)}")
