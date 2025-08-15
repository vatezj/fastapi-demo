# -*- coding: utf-8 -*-
"""
用户基础服务
"""

from typing import List, Optional, Dict, Any
from shared.service.base_service import BaseService
from shared.dao.user_dao import UserDAO
from shared.entity.do.user_do import UserDO
from shared.entity.vo.user_vo import UserBaseVO, UserCreateVO, UserUpdateVO

class UserBaseService(BaseService[UserDO, UserBaseVO]):
    """用户基础服务"""
    
    def __init__(self, user_dao: UserDAO):
        super().__init__(user_dao)
        self.user_dao = user_dao
    
    async def get_by_username(self, username: str) -> Optional[UserDO]:
        """根据用户名获取用户"""
        return await self.user_dao.get_by_username(username)
    
    async def get_by_email(self, email: str) -> Optional[UserDO]:
        """根据邮箱获取用户"""
        return await self.user_dao.get_by_email(email)
    
    async def get_by_phone(self, phone: str) -> Optional[UserDO]:
        """根据手机号获取用户"""
        return await self.user_dao.get_by_phone(phone)
    
    async def get_by_username_or_email(self, username_or_email: str) -> Optional[UserDO]:
        """根据用户名或邮箱获取用户"""
        return await self.user_dao.get_by_username_or_email(username_or_email)
    
    async def get_users_by_dept(self, dept_id: int) -> List[UserDO]:
        """根据部门ID获取用户列表"""
        return await self.user_dao.get_users_by_dept(dept_id)
    
    async def get_users_by_status(self, status: str) -> List[UserDO]:
        """根据状态获取用户列表"""
        return await self.user_dao.get_users_by_status(status)
    
    async def search_users(self, keyword: str, page: int = 1, size: int = 20) -> tuple[List[UserDO], int]:
        """搜索用户"""
        return await self.user_dao.search_users(keyword, page, size)
    
    async def update_login_info(self, user_id: int, login_ip: str) -> bool:
        """更新用户登录信息"""
        return await self.user_dao.update_login_info(user_id, login_ip)
    
    async def update_password(self, user_id: int, new_password: str) -> bool:
        """更新用户密码"""
        return await self.user_dao.update_password(user_id, new_password)
    
    async def get_user_count_by_dept(self, dept_id: int) -> int:
        """获取部门用户数量"""
        return await self.user_dao.get_user_count_by_dept(dept_id)
    
    async def get_active_user_count(self) -> int:
        """获取活跃用户数量"""
        return await self.user_dao.get_active_user_count()
    
    async def get_users_by_ids(self, user_ids: List[int]) -> List[UserDO]:
        """根据用户ID列表获取用户"""
        return await self.user_dao.get_users_by_ids(user_ids)
    
    async def create_user(self, user_data: UserCreateVO, create_by: str = "") -> UserDO:
        """创建用户"""
        from datetime import datetime
        
        # 检查用户名是否已存在
        if await self.exists(user_name=user_data.username):
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否已存在
        if await self.exists(email=user_data.email):
            raise ValueError("邮箱已存在")
        
        # 检查手机号是否已存在
        if user_data.phone and await self.exists(phone=user_data.phone):
            raise ValueError("手机号已存在")
        
        # 创建用户实体
        user_entity = UserDO(
            user_name=user_data.username,
            nick_name=user_data.nickname or user_data.username,
            email=user_data.email,
            phone=user_data.phone,
            password=user_data.password,  # 注意：实际使用时需要加密
            sex=user_data.sex or '0',
            dept_id=user_data.dept_id,
            post_id=user_data.post_id,
            profile=user_data.profile,
            create_by=create_by,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        
        return await self.create(user_entity)
    
    async def update_user(self, user_id: int, user_data: UserUpdateVO, update_by: str = "") -> Optional[UserDO]:
        """更新用户"""
        from datetime import datetime
        
        # 检查用户是否存在
        existing_user = await self.get_by_id(user_id)
        if not existing_user:
            raise ValueError("用户不存在")
        
        # 检查邮箱是否已被其他用户使用
        if user_data.email and user_data.email != existing_user.email:
            if await self.exists(email=user_data.email):
                raise ValueError("邮箱已被其他用户使用")
        
        # 检查手机号是否已被其他用户使用
        if user_data.phone and user_data.phone != existing_user.phone:
            if await self.exists(phone=user_data.phone):
                raise ValueError("手机号已被其他用户使用")
        
        # 准备更新数据
        update_data = user_data.dict(exclude_unset=True)
        update_data['update_by'] = update_by
        update_data['update_time'] = datetime.now()
        
        return await self.update(user_id, update_data)
    
    async def delete_user(self, user_id: int, delete_by: str = "") -> bool:
        """删除用户"""
        # 检查用户是否存在
        existing_user = await self.get_by_id(user_id)
        if not existing_user:
            raise ValueError("用户不存在")
        
        # 逻辑删除
        return await self.delete(user_id)
    
    def validate_password(self, password: str) -> bool:
        """验证密码强度"""
        if len(password) < 6:
            return False
        
        # 检查是否包含数字和字母
        has_digit = any(c.isdigit() for c in password)
        has_letter = any(c.isalpha() for c in password)
        
        return has_digit and has_letter
    
    def validate_phone(self, phone: str) -> bool:
        """验证手机号格式"""
        import re
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone)) 