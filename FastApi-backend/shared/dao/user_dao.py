# -*- coding: utf-8 -*-
"""
用户数据访问对象
"""

from typing import List, Optional
from sqlalchemy import select, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from shared.dao.base_dao import BaseDAO
from shared.entity.do.user_do import UserDO

class UserDAO(BaseDAO[UserDO]):
    """用户数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(UserDO, db)
    
    async def get_by_username(self, username: str) -> Optional[UserDO]:
        """根据用户名获取用户"""
        return await self.get_one_by_condition(user_name=username)
    
    async def get_by_email(self, email: str) -> Optional[UserDO]:
        """根据邮箱获取用户"""
        return await self.get_one_by_condition(email=email)
    
    async def get_by_phone(self, phone: str) -> Optional[UserDO]:
        """根据手机号获取用户"""
        return await self.get_one_by_condition(phone=phone)
    
    async def get_by_username_or_email(self, username_or_email: str) -> Optional[UserDO]:
        """根据用户名或邮箱获取用户"""
        from sqlalchemy import or_
        query = select(UserDO).where(
            and_(
                UserDO.del_flag == '0',
                or_(
                    UserDO.user_name == username_or_email,
                    UserDO.email == username_or_email
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_users_by_dept(self, dept_id: int) -> List[UserDO]:
        """根据部门ID获取用户列表"""
        return await self.get_by_condition(dept_id=dept_id)
    
    async def get_users_by_status(self, status: str) -> List[UserDO]:
        """根据状态获取用户列表"""
        return await self.get_by_condition(status=status)
    
    async def search_users(self, keyword: str, page: int = 1, size: int = 20) -> tuple[List[UserDO], int]:
        """搜索用户"""
        # 构建搜索条件
        search_conditions = or_(
            UserDO.user_name.like(f'%{keyword}%'),
            UserDO.nick_name.like(f'%{keyword}%'),
            UserDO.email.like(f'%{keyword}%'),
            UserDO.phone.like(f'%{keyword}%')
        )
        
        # 获取总数
        count_query = select(func.count(UserDO.user_id)).where(
            and_(
                UserDO.del_flag == '0',
                search_conditions
            )
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 获取分页数据
        query = select(UserDO).where(
            and_(
                UserDO.del_flag == '0',
                search_conditions
            )
        ).order_by(UserDO.create_time.desc())
        
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return users, total
    
    async def update_login_info(self, user_id: int, login_ip: str) -> bool:
        """更新用户登录信息"""
        from datetime import datetime
        
        update_data = {
            'login_ip': login_ip,
            'login_date': datetime.now()
        }
        
        result = await self.update(user_id, update_data)
        return result is not None
    
    async def update_password(self, user_id: int, new_password: str) -> bool:
        """更新用户密码"""
        update_data = {
            'password': new_password
        }
        
        result = await self.update(user_id, update_data)
        return result is not None
    
    async def get_user_count_by_dept(self, dept_id: int) -> int:
        """获取部门用户数量"""
        return await self.count(dept_id=dept_id)
    
    async def get_active_user_count(self) -> int:
        """获取活跃用户数量（状态为正常）"""
        return await self.count(status='0')
    
    async def get_users_by_ids(self, user_ids: List[int]) -> List[UserDO]:
        """根据用户ID列表获取用户"""
        if not user_ids:
            return []
        
        query = select(UserDO).where(
            and_(
                UserDO.del_flag == '0',
                UserDO.user_id.in_(user_ids)
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().all() 