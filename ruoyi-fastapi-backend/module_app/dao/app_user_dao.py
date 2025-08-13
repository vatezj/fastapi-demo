from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from shared.entity.do.app_user_do import AppUser, AppUserProfile, AppLoginLog
from shared.entity.vo.app_user_vo import AppUserQueryModel, AppLoginLogQueryModel


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
        from datetime import datetime, timedelta
        clean_date = datetime.now() - timedelta(days=days)
        
        result = await db.execute(
            delete(AppLoginLog).where(AppLoginLog.login_time < clean_date)
        )
        await db.commit()
        return result.rowcount > 0
