"""
验证相关数据访问对象
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from ..entity.do.verification_do import YozuanTaskVerification, YozuanTaskVerificationSubmit
from ..enums.task_enums import ReviewStatus


class VerificationDao:
    """验证数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task_verifications(self, task_id: int, verifications_data: List[Dict[str, Any]]) -> List[YozuanTaskVerification]:
        """创建任务验证要求"""
        verifications = []
        for verification_data in verifications_data:
            verification_data["task_id"] = task_id
            verification = YozuanTaskVerification(**verification_data)
            verifications.append(verification)
        
        self.db.add_all(verifications)
        await self.db.commit()
        
        # 刷新获取ID
        for verification in verifications:
            await self.db.refresh(verification)
        
        return verifications
    
    async def get_task_verifications(self, task_id: int) -> List[YozuanTaskVerification]:
        """获取任务验证要求"""
        query = select(YozuanTaskVerification).where(
            YozuanTaskVerification.task_id == task_id
        ).order_by(YozuanTaskVerification.verification_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_task_verifications(self, task_id: int, verifications_data: List[Dict[str, Any]]) -> List[YozuanTaskVerification]:
        """更新任务验证要求（先删除旧的，再创建新的）"""
        # 删除旧的验证要求
        delete_query = delete(YozuanTaskVerification).where(YozuanTaskVerification.task_id == task_id)
        await self.db.execute(delete_query)
        
        # 创建新的验证要求
        return await self.create_task_verifications(task_id, verifications_data)
    
    async def delete_task_verifications(self, task_id: int) -> bool:
        """删除任务验证要求"""
        query = delete(YozuanTaskVerification).where(YozuanTaskVerification.task_id == task_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0


class VerificationSubmitDao:
    """验证提交数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_verification_submit(self, submit_data: Dict[str, Any]) -> YozuanTaskVerificationSubmit:
        """创建验证提交"""
        submit = YozuanTaskVerificationSubmit(**submit_data)
        self.db.add(submit)
        await self.db.commit()
        await self.db.refresh(submit)
        return submit
    
    async def get_verification_submit(self, submit_id: int) -> Optional[YozuanTaskVerificationSubmit]:
        """根据ID获取验证提交"""
        query = select(YozuanTaskVerificationSubmit).where(
            YozuanTaskVerificationSubmit.submit_id == submit_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_order_verification_submit(self, order_id: int) -> Optional[YozuanTaskVerificationSubmit]:
        """根据订单ID获取验证提交"""
        query = select(YozuanTaskVerificationSubmit).where(
            YozuanTaskVerificationSubmit.order_id == order_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_verification_submit(self, submit_id: int, update_data: Dict[str, Any]) -> bool:
        """更新验证提交"""
        query = update(YozuanTaskVerificationSubmit).where(
            YozuanTaskVerificationSubmit.submit_id == submit_id
        ).values(**update_data)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def approve_verification(self, submit_id: int, review_user_id: int, review_comment: str = None) -> bool:
        """审核通过验证"""
        return await self.update_verification_submit(
            submit_id,
            {
                "review_status": ReviewStatus.APPROVED,
                "review_user_id": review_user_id,
                "review_comment": review_comment,
                "review_time": func.now()
            }
        )
    
    async def reject_verification(self, submit_id: int, review_user_id: int, review_comment: str) -> bool:
        """审核驳回验证"""
        return await self.update_verification_submit(
            submit_id,
            {
                "review_status": ReviewStatus.REJECTED,
                "review_user_id": review_user_id,
                "review_comment": review_comment,
                "review_time": func.now()
            }
        )
    
    async def get_pending_verifications(self, publisher_id: int, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取待审核的验证列表（发布者的任务）"""
        # 这里需要关联查询，暂时返回空结果
        # TODO: 实现关联查询逻辑
        return {
            "verifications": [],
            "total": 0,
            "page": page,
            "size": size,
            "pages": 0
        }
    
    async def get_verification_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取验证统计信息"""
        # 统计各种状态的验证数量
        status_counts = {}
        for status in ReviewStatus:
            count_query = select(func.count(YozuanTaskVerificationSubmit.submit_id)).where(
                and_(YozuanTaskVerificationSubmit.review_user_id == user_id,
                     YozuanTaskVerificationSubmit.review_status == status.value)
            )
            count_result = await self.db.execute(count_query)
            status_counts[status.value] = count_result.scalar()
        
        return {
            "status_counts": status_counts,
            "total_reviews": sum(status_counts.values())
        }
