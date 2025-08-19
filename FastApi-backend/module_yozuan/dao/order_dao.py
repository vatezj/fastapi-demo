"""
订单相关数据访问对象
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from ..entity.do.order_do import YozuanTaskOrder
from ..enums.task_enums import TaskOrderStatus


class OrderDao:
    """订单数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_order(self, order_data: Dict[str, Any]) -> YozuanTaskOrder:
        """创建订单"""
        order = YozuanTaskOrder(**order_data)
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def get_order_by_id(self, order_id: int) -> Optional[YozuanTaskOrder]:
        """根据ID获取订单"""
        query = select(YozuanTaskOrder).where(YozuanTaskOrder.order_id == order_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_order_by_task_user(self, task_id: int, user_id: int) -> Optional[YozuanTaskOrder]:
        """根据任务ID和用户ID获取订单"""
        query = select(YozuanTaskOrder).where(
            and_(YozuanTaskOrder.task_id == task_id, YozuanTaskOrder.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_orders(self, user_id: int, status: Optional[str] = None,
                            page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取用户的订单列表"""
        query = select(YozuanTaskOrder).where(YozuanTaskOrder.user_id == user_id)
        
        if status:
            query = query.where(YozuanTaskOrder.order_status == status)
        
        # 计算总数
        count_query = select(func.count(YozuanTaskOrder.order_id)).where(
            YozuanTaskOrder.user_id == user_id
        )
        if status:
            count_query = count_query.where(YozuanTaskOrder.order_status == status)
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # 分页查询
        query = query.order_by(YozuanTaskOrder.apply_time.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        return {
            "orders": orders,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    async def get_task_orders(self, task_id: int, status: Optional[str] = None,
                            page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取任务的订单列表"""
        query = select(YozuanTaskOrder).where(YozuanTaskOrder.task_id == task_id)
        
        if status:
            query = query.where(YozuanTaskOrder.order_status == status)
        
        # 计算总数
        count_query = select(func.count(YozuanTaskOrder.order_id)).where(
            YozuanTaskOrder.task_id == task_id
        )
        if status:
            count_query = count_query.where(YozuanTaskOrder.order_status == status)
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # 分页查询
        query = query.order_by(YozuanTaskOrder.apply_time.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        return {
            "orders": orders,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    async def update_order(self, order_id: int, update_data: Dict[str, Any]) -> bool:
        """更新订单"""
        query = update(YozuanTaskOrder).where(YozuanTaskOrder.order_id == order_id).values(**update_data)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def update_order_status(self, order_id: int, status: str, **kwargs) -> bool:
        """更新订单状态"""
        update_data = {"order_status": status}
        update_data.update(kwargs)
        return await self.update_order(order_id, update_data)
    
    async def start_order(self, order_id: int) -> bool:
        """开始订单"""
        return await self.update_order_status(
            order_id, 
            TaskOrderStatus.IN_PROGRESS,
            start_time=func.now()
        )
    
    async def complete_order(self, order_id: int) -> bool:
        """完成订单"""
        return await self.update_order_status(
            order_id,
            TaskOrderStatus.COMPLETED,
            complete_time=func.now()
        )
    
    async def verify_order(self, order_id: int, commission_amount: float) -> bool:
        """验证订单"""
        return await self.update_order_status(
            order_id,
            TaskOrderStatus.VERIFIED,
            verify_time=func.now(),
            commission_amount=commission_amount
        )
    
    async def reject_order(self, order_id: int, reject_reason: str) -> bool:
        """驳回订单"""
        return await self.update_order_status(
            order_id,
            TaskOrderStatus.REJECTED,
            reject_reason=reject_reason
        )
    
    async def cancel_order(self, order_id: int) -> bool:
        """取消订单"""
        return await self.update_order_status(order_id, TaskOrderStatus.CANCELLED)
    
    async def delete_order(self, order_id: int) -> bool:
        """删除订单"""
        query = delete(YozuanTaskOrder).where(YozuanTaskOrder.order_id == order_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def check_user_can_apply_task(self, task_id: int, user_id: int) -> bool:
        """检查用户是否可以报名任务"""
        # 检查是否已经报名
        existing_order = await self.get_order_by_task_user(task_id, user_id)
        if existing_order:
            return False
        
        # 检查任务是否还有剩余数量
        # 这里需要结合任务表查询，暂时返回True
        return True
    
    async def get_order_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取用户订单统计"""
        # 统计各种状态的订单数量
        status_counts = {}
        for status in TaskOrderStatus:
            count_query = select(func.count(YozuanTaskOrder.order_id)).where(
                and_(YozuanTaskOrder.user_id == user_id, YozuanTaskOrder.order_status == status.value)
            )
            count_result = await self.db.execute(count_query)
            status_counts[status.value] = count_result.scalar()
        
        # 统计总佣金
        commission_query = select(func.sum(YozuanTaskOrder.commission_amount)).where(
            and_(YozuanTaskOrder.user_id == user_id, YozuanTaskOrder.order_status == TaskOrderStatus.VERIFIED.value)
        )
        commission_result = await self.db.execute(commission_query)
        total_commission = commission_result.scalar() or 0
        
        return {
            "status_counts": status_counts,
            "total_commission": float(total_commission),
            "total_orders": sum(status_counts.values())
        }
