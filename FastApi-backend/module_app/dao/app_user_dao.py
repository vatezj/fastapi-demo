from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from ..entity.do.app_user_do import AppUser, AppUserProfile, AppLoginLog
from ..entity.vo.app_user_vo import AppUserQueryModel, AppLoginLogQueryModel
from datetime import datetime, timedelta


class AppUserDao:
    """APP用户数据访问层"""
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[AppUser]:
        """根据用户ID获取用户信息"""
        result = await db.execute(
            select(AppUser).where(AppUser.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, user_name: str) -> Optional[AppUser]:
        """根据用户名获取用户信息"""
        result = await db.execute(
            select(AppUser).where(AppUser.user_name == user_name)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[AppUser]:
        """根据手机号获取用户信息"""
        result = await db.execute(
            select(AppUser).where(AppUser.phone == phone)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[AppUser]:
        """根据邮箱获取用户信息"""
        result = await db.execute(
            select(AppUser).where(AppUser.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_with_profile(db: AsyncSession, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户信息及其详细信息"""
        # 获取用户基础信息
        user_result = await db.execute(
            select(AppUser).where(AppUser.user_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return None
        
        # 获取用户详细信息
        profile_result = await db.execute(
            select(AppUserProfile).where(AppUserProfile.user_id == user_id)
        )
        profile = profile_result.scalar_one_or_none()
        
        return {
            'user': user,
            'profile': profile
        }
    
    @staticmethod
    async def get_user_list(db: AsyncSession, query: AppUserQueryModel) -> List[AppUser]:
        """获取用户列表"""
        conditions = []
        
        if query.user_name:
            conditions.append(AppUser.user_name.like(f'%{query.user_name}%'))
        if query.nick_name:
            conditions.append(AppUser.nick_name.like(f'%{query.nick_name}%'))
        if query.email:
            conditions.append(AppUser.email.like(f'%{query.email}%'))
        if query.phone:
            conditions.append(AppUser.phone.like(f'%{query.phone}%'))
        if query.sex:
            conditions.append(AppUser.sex == query.sex)
        if query.status:
            conditions.append(AppUser.status == query.status)
        if query.begin_time:
            conditions.append(AppUser.create_time >= query.begin_time)
        if query.end_time:
            conditions.append(AppUser.create_time <= query.end_time)
        
        query_stmt = select(AppUser)
        if conditions:
            query_stmt = query_stmt.where(and_(*conditions))
        
        query_stmt = query_stmt.order_by(desc(AppUser.create_time))
        
        result = await db.execute(query_stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_user_count(db: AsyncSession, query: AppUserQueryModel) -> int:
        """获取用户总数"""
        conditions = []
        
        if query.user_name:
            conditions.append(AppUser.user_name.like(f'%{query.user_name}%'))
        if query.nick_name:
            conditions.append(AppUser.nick_name.like(f'%{query.nick_name}%'))
        if query.email:
            conditions.append(AppUser.email.like(f'%{query.email}%'))
        if query.phone:
            conditions.append(AppUser.phone.like(f'%{query.phone}%'))
        if query.sex:
            conditions.append(AppUser.sex == query.sex)
        if query.status:
            conditions.append(AppUser.status == query.status)
        if query.begin_time:
            conditions.append(AppUser.create_time >= query.begin_time)
        if query.end_time:
            conditions.append(AppUser.create_time <= query.end_time)
        
        query_stmt = select(func.count(AppUser.user_id))
        if conditions:
            query_stmt = query_stmt.where(and_(*conditions))
        
        result = await db.execute(query_stmt)
        return result.scalar()
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: Dict[str, Any]) -> AppUser:
        """创建用户"""
        user = AppUser(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def create_user_profile(db: AsyncSession, profile_data: Dict[str, Any]) -> AppUserProfile:
        """创建用户详细信息"""
        profile = AppUserProfile(**profile_data)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, update_data: Dict[str, Any]) -> bool:
        """更新用户信息"""
        result = await db.execute(
            update(AppUser)
            .where(AppUser.user_id == user_id)
            .values(**update_data)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def update_user_profile(db: AsyncSession, user_id: int, update_data: Dict[str, Any]) -> bool:
        """更新用户详细信息"""
        result = await db.execute(
            update(AppUserProfile)
            .where(AppUserProfile.user_id == user_id)
            .values(**update_data)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """删除用户"""
        result = await db.execute(
            delete(AppUser).where(AppUser.user_id == user_id)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def delete_users(db: AsyncSession, user_ids: List[int]) -> bool:
        """批量删除用户"""
        result = await db.execute(
            delete(AppUser).where(AppUser.user_id.in_(user_ids))
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def update_user_status(db: AsyncSession, user_id: int, status: str) -> bool:
        """更新用户状态"""
        result = await db.execute(
            update(AppUser)
            .where(AppUser.user_id == user_id)
            .values(status=status)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def update_user_password(db: AsyncSession, user_id: int, password: str) -> bool:
        """更新用户密码"""
        result = await db.execute(
            update(AppUser)
            .where(AppUser.user_id == user_id)
            .values(password=password)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def update_login_info(db: AsyncSession, user_id: int, login_ip: str) -> bool:
        """更新用户登录信息"""
        result = await db.execute(
            update(AppUser)
            .where(AppUser.user_id == user_id)
            .values(login_ip=login_ip, login_date=func.now())
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def check_username_exists(db: AsyncSession, user_name: str, exclude_user_id: Optional[int] = None) -> bool:
        """检查用户名是否存在"""
        conditions = [AppUser.user_name == user_name]
        if exclude_user_id:
            conditions.append(AppUser.user_id != exclude_user_id)
        
        result = await db.execute(
            select(func.count(AppUser.user_id)).where(and_(*conditions))
        )
        return result.scalar() > 0
    
    @staticmethod
    async def check_phone_exists(db: AsyncSession, phone: str, exclude_user_id: Optional[int] = None) -> bool:
        """检查手机号是否存在"""
        if not phone:
            return False
        
        conditions = [AppUser.phone == phone]
        if exclude_user_id:
            conditions.append(AppUser.user_id != exclude_user_id)
        
        result = await db.execute(
            select(func.count(AppUser.user_id)).where(and_(*conditions))
        )
        return result.scalar() > 0
    
    @staticmethod
    async def check_email_exists(db: AsyncSession, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """检查邮箱是否存在"""
        if not email:
            return False
        
        conditions = [AppUser.email == email]
        if exclude_user_id:
            conditions.append(AppUser.user_id != exclude_user_id)
        
        result = await db.execute(
            select(func.count(AppUser.user_id)).where(and_(*conditions))
        )
        return result.scalar() > 0
    
    @staticmethod
    async def get_users(db: AsyncSession, filters: Dict[str, Any] = None) -> List[AppUser]:
        """根据条件获取用户列表"""
        query = select(AppUser)
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    if key == 'user_name' and value:
                        conditions.append(AppUser.user_name.like(f'%{value}%'))
                    elif key == 'email' and value:
                        conditions.append(AppUser.email.like(f'%{value}%'))
                    elif key == 'phone' and value:
                        conditions.append(AppUser.phone.like(f'%{value}%'))
                    elif key == 'status' and value:
                        conditions.append(AppUser.status == value)
                    elif key == 'sex' and value:
                        conditions.append(AppUser.sex == value)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AppUser.create_time))
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_users_page(
        db: AsyncSession, 
        page_num: int, 
        page_size: int,
        user_name: str = None,
        email: str = None,
        phone: str = None,
        status: str = None,
        sex: str = None
    ) -> Dict[str, Any]:
        """分页获取用户列表"""
        # 构建查询条件
        conditions = []
        if user_name:
            conditions.append(AppUser.user_name.like(f'%{user_name}%'))
        if email:
            conditions.append(AppUser.email.like(f'%{email}%'))
        if phone:
            conditions.append(AppUser.phone.like(f'%{phone}%'))
        if status:
            conditions.append(AppUser.status == status)
        if sex:
            conditions.append(AppUser.sex == sex)
        
        # 获取总数
        count_query = select(func.count(AppUser.user_id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 获取分页数据
        query = select(AppUser)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AppUser.create_time))
        query = query.offset((page_num - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        return {
            'rows': users,
            'total': total,
            'page_num': page_num,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: int) -> Optional[AppUserProfile]:
        """获取用户档案信息"""
        result = await db.execute(
            select(AppUserProfile).where(AppUserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()


class AppLoginLogDao:
    """APP登录日志数据访问层"""
    
    @staticmethod
    async def create_login_log(db: AsyncSession, log_data: Dict[str, Any]) -> AppLoginLog:
        """创建登录日志"""
        log = AppLoginLog(**log_data)
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log
    
    @staticmethod
    async def get_login_logs(db: AsyncSession, filters: Dict[str, Any] = None) -> List[AppLoginLog]:
        """根据条件获取登录日志"""
        query = select(AppLoginLog)
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    if key == 'user_name' and value:
                        conditions.append(AppLoginLog.user_name.like(f'%{value}%'))
                    elif key == 'status' and value:
                        conditions.append(AppLoginLog.status == value)
                    elif key == 'start_time' and value:
                        conditions.append(AppLoginLog.login_time >= value)
                    elif key == 'end_time' and value:
                        conditions.append(AppLoginLog.login_time <= value)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AppLoginLog.login_time))
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_login_logs_page(
        db: AsyncSession,
        page_num: int,
        page_size: int,
        user_name: str = None,
        status: str = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> Dict[str, Any]:
        """分页获取登录日志"""
        # 构建查询条件
        conditions = []
        if user_name:
            conditions.append(AppLoginLog.user_name.like(f'%{user_name}%'))
        if status:
            conditions.append(AppLoginLog.status == status)
        if start_time:
            conditions.append(AppLoginLog.login_time >= start_time)
        if end_time:
            conditions.append(AppLoginLog.login_time <= end_time)
        
        # 获取总数
        count_query = select(func.count(AppLoginLog.log_id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 获取分页数据
        query = select(AppLoginLog)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AppLoginLog.login_time))
        query = query.offset((page_num - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return {
            'rows': logs,
            'total': total,
            'page_num': page_num,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    @staticmethod
    async def get_login_log_list(db: AsyncSession, query: AppLoginLogQueryModel, page_num: int = 1, page_size: int = 10) -> List[AppLoginLog]:
        """获取登录日志列表"""
        conditions = []
        
        if query.user_name:
            conditions.append(AppLoginLog.user_name.like(f'%{query.user_name}%'))
        if query.ipaddr:
            conditions.append(AppLoginLog.ipaddr.like(f'%{query.ipaddr}%'))
        if query.status:
            conditions.append(AppLoginLog.status == query.status)
        if query.begin_time:
            conditions.append(AppLoginLog.login_time >= query.begin_time)
        if query.end_time:
            conditions.append(AppLoginLog.login_time <= query.end_time)
        
        query_stmt = select(AppLoginLog)
        if conditions:
            query_stmt = query_stmt.where(and_(*conditions))
        
        query_stmt = query_stmt.order_by(desc(AppLoginLog.login_time))
        
        # 分页
        offset = (page_num - 1) * page_size
        query_stmt = query_stmt.offset(offset).limit(page_size)
        
        result = await db.execute(query_stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_login_log_count(db: AsyncSession, query: AppLoginLogQueryModel) -> int:
        """获取登录日志总数"""
        conditions = []
        
        if query.user_name:
            conditions.append(AppLoginLog.user_name.like(f'%{query.user_name}%'))
        if query.ipaddr:
            conditions.append(AppLoginLog.ipaddr.like(f'%{query.ipaddr}%'))
        if query.status:
            conditions.append(AppLoginLog.status == query.status)
        if query.begin_time:
            conditions.append(AppLoginLog.login_time >= query.begin_time)
        if query.end_time:
            conditions.append(AppLoginLog.login_time <= query.end_time)
        
        query_stmt = select(func.count(AppLoginLog.log_id))
        if conditions:
            query_stmt = query_stmt.where(and_(*conditions))
        
        result = await db.execute(query_stmt)
        return result.scalar()
    
    @staticmethod
    async def delete_login_logs(db: AsyncSession, log_ids: List[int]) -> bool:
        """批量删除登录日志"""
        result = await db.execute(
            delete(AppLoginLog).where(AppLoginLog.log_id.in_(log_ids))
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def clean_login_logs(db: AsyncSession, days: int = 30) -> bool:
        """清理指定天数前的登录日志"""
        clean_date = datetime.now() - timedelta(days=days)
        
        result = await db.execute(
            delete(AppLoginLog).where(AppLoginLog.login_time < clean_date)
        )
        await db.commit()
        return result.rowcount > 0
