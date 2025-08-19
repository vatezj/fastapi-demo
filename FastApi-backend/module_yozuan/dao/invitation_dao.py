"""
邀请和分销相关数据访问对象
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from typing import List, Optional, Dict, Any
from ..entity.do.invitation_do import YozuanUserInvitation, YozuanRebateConfig, YozuanRebateRecord
from module_app.entity.do.app_user_do import AppUser
import secrets
import string


class InvitationDao:
    """邀请关系数据访问对象"""
    
    @staticmethod
    async def create_invitation(
        db: AsyncSession,
        inviter_id: int,
        invitee_id: int,
        parent_invitation_id: Optional[int] = None,
        level: int = 1
    ) -> YozuanUserInvitation:
        """创建邀请关系"""
        # 生成邀请码
        invitation_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        invitation = YozuanUserInvitation(
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            invitation_code=invitation_code,
            parent_invitation_id=parent_invitation_id,
            level=level
        )
        
        db.add(invitation)
        await db.commit()
        await db.refresh(invitation)
        return invitation
    
    @staticmethod
    async def get_invitation_by_code(
        db: AsyncSession,
        invitation_code: str
    ) -> Optional[YozuanUserInvitation]:
        """根据邀请码获取邀请关系"""
        query = select(YozuanUserInvitation).where(
            YozuanUserInvitation.invitation_code == invitation_code,
            YozuanUserInvitation.status == "pending"
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_invitations(
        db: AsyncSession,
        user_id: int,
        status: Optional[str] = None
    ) -> List[YozuanUserInvitation]:
        """获取用户的邀请关系"""
        query = select(YozuanUserInvitation)
        conditions = [YozuanUserInvitation.inviter_id == user_id]
        
        if status:
            conditions.append(YozuanUserInvitation.status == status)
        
        query = query.where(and_(*conditions))
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_user_invitation_tree(
        db: AsyncSession,
        user_id: int,
        max_level: int = 3
    ) -> List[YozuanUserInvitation]:
        """获取用户的邀请树（多级邀请关系）"""
        query = select(YozuanUserInvitation).where(
            and_(
                YozuanUserInvitation.inviter_id == user_id,
                YozuanUserInvitation.level <= max_level,
                YozuanUserInvitation.status == "accepted"
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def accept_invitation(
        db: AsyncSession,
        invitation_id: int
    ) -> bool:
        """接受邀请"""
        query = update(YozuanUserInvitation).where(
            YozuanUserInvitation.invitation_id == invitation_id
        ).values(
            status="accepted",
            accept_time=func.now()
        )
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def get_invitation_statistics(
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """获取邀请统计信息"""
        # 统计各层级的邀请数量
        query = select(
            YozuanUserInvitation.level,
            func.count(YozuanUserInvitation.invitation_id).label("count")
        ).where(
            and_(
                YozuanUserInvitation.inviter_id == user_id,
                YozuanUserInvitation.status == "accepted"
            )
        ).group_by(YozuanUserInvitation.level)
        
        result = await db.execute(query)
        level_counts = {row.level: row.count for row in result}
        
        return {
            "total_invitations": sum(level_counts.values()),
            "level_1_count": level_counts.get(1, 0),
            "level_2_count": level_counts.get(2, 0),
            "level_3_count": level_counts.get(3, 0)
        }


class RebateConfigDao:
    """返佣配置数据访问对象"""
    
    @staticmethod
    async def get_all_configs(
        db: AsyncSession
    ) -> List[YozuanRebateConfig]:
        """获取所有返佣配置"""
        query = select(YozuanRebateConfig).where(
            YozuanRebateConfig.status == "enabled"
        ).order_by(YozuanRebateConfig.level)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_config_by_level(
        db: AsyncSession,
        level: int
    ) -> Optional[YozuanRebateConfig]:
        """根据层级获取返佣配置"""
        query = select(YozuanRebateConfig).where(
            and_(
                YozuanRebateConfig.level == level,
                YozuanRebateConfig.status == "enabled"
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_rebate_record(
        db: AsyncSession,
        order_id: int,
        inviter_id: int,
        invitee_id: int,
        task_id: int,
        rebate_amount: float,
        rebate_rate: float,
        level: int,
        rebate_source: str = "task_completion"
    ) -> YozuanRebateRecord:
        """创建返佣记录"""
        record = YozuanRebateRecord(
            order_id=order_id,
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            task_id=task_id,
            rebate_amount=rebate_amount,
            rebate_rate=rebate_rate,
            level=level,
            rebate_source=rebate_source
        )
        
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record
    
    @staticmethod
    async def get_user_rebate_records(
        db: AsyncSession,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[YozuanRebateRecord]:
        """获取用户的返佣记录"""
        query = select(YozuanRebateRecord).where(
            YozuanRebateRecord.inviter_id == user_id
        )
        
        if status:
            query = query.where(YozuanRebateRecord.status == status)
        
        query = query.order_by(YozuanRebateRecord.create_time.desc()).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_rebate_status(
        db: AsyncSession,
        record_id: int,
        status: str,
        remark: Optional[str] = None
    ) -> bool:
        """更新返佣记录状态"""
        query = update(YozuanRebateRecord).where(
            YozuanRebateRecord.record_id == record_id
        ).values(
            status=status,
            process_time=func.now(),
            remark=remark
        )
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def get_rebate_statistics(
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """获取返佣统计信息"""
        # 统计总返佣金额
        total_query = select(
            func.sum(YozuanRebateRecord.rebate_amount).label("total_amount")
        ).where(
            and_(
                YozuanRebateRecord.inviter_id == user_id,
                YozuanRebateRecord.status == "processed"
            )
        )
        total_result = await db.execute(total_query)
        total_amount = total_result.scalar() or 0
        
        # 统计各层级的返佣金额
        level_query = select(
            YozuanRebateRecord.level,
            func.sum(YozuanRebateRecord.rebate_amount).label("level_amount")
        ).where(
            and_(
                YozuanRebateRecord.inviter_id == user_id,
                YozuanRebateRecord.status == "processed"
            )
        ).group_by(YozuanRebateRecord.level)
        
        level_result = await db.execute(level_query)
        level_amounts = {row.level: float(row.level_amount) for row in level_result}
        
        return {
            "total_rebate_amount": float(total_amount),
            "level_1_amount": level_amounts.get(1, 0.0),
            "level_2_amount": level_amounts.get(2, 0.0),
            "level_3_amount": level_amounts.get(3, 0.0)
        }
