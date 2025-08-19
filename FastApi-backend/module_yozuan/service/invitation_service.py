"""
邀请和分销相关业务逻辑服务
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from ..dao.invitation_dao import InvitationDao, RebateConfigDao
from ..entity.do.invitation_do import YozuanUserInvitation, YozuanRebateConfig, YozuanRebateRecord
from module_app.entity.do.app_user_do import AppUser
from module_app.dao.app_user_dao import AppUserDao
from ..dao.account_dao import AccountDao
from ..dao.task_dao import TaskDao
from ..dao.order_dao import OrderDao
from config.yozuan_config import yozuan_config
import logging

logger = logging.getLogger(__name__)


class InvitationService:
    """邀请关系业务逻辑服务"""
    
    @staticmethod
    async def create_invitation_chain(
        db: AsyncSession,
        inviter_id: int,
        invitee_id: int
    ) -> Dict[str, Any]:
        """
        创建完整的邀请链（支持3级分销）
        
        Args:
            db: 数据库会话
            inviter_id: 邀请人ID
            invitee_id: 被邀请人ID
            
        Returns:
            Dict: 邀请结果
        """
        try:
            # 1. 检查被邀请人是否已经存在邀请关系
            existing_invitation = await InvitationDao.get_user_invitations(
                db, invitee_id, status="accepted"
            )
            if existing_invitation:
                return {
                    "success": False,
                    "message": "该用户已经被邀请过了"
                }
            
            # 2. 获取邀请人的邀请树
            inviter_tree = await InvitationDao.get_user_invitation_tree(
                db, inviter_id, max_level=2
            )
            
            # 3. 计算邀请层级
            current_level = 1
            parent_invitation_id = None
            
            # 如果邀请人本身是被邀请的，则计算层级
            if inviter_tree:
                # 找到邀请人的最高层级
                max_inviter_level = max(inv.level for inv in inviter_tree)
                current_level = min(max_inviter_level + 1, 3)
                
                # 如果邀请人是一级邀请，则新用户是二级
                if max_inviter_level == 1:
                    current_level = 2
                    # 找到邀请人的邀请记录作为父级
                    for inv in inviter_tree:
                        if inv.level == 1:
                            parent_invitation_id = inv.invitation_id
                            break
                # 如果邀请人是二级邀请，则新用户是三级
                elif max_inviter_level == 2:
                    current_level = 3
                    # 找到邀请人的邀请记录作为父级
                    for inv in inviter_tree:
                        if inv.level == 2:
                            parent_invitation_id = inv.invitation_id
                            break
            
            # 4. 创建邀请关系
            invitation = await InvitationDao.create_invitation(
                db=db,
                inviter_id=inviter_id,
                invitee_id=invitee_id,
                parent_invitation_id=parent_invitation_id,
                level=current_level
            )
            
            # 5. 为新用户创建账户
            await AccountDao.create_user_account(db, invitee_id)
            
            return {
                "success": True,
                "message": "邀请创建成功",
                "data": {
                    "invitation_id": invitation.invitation_id,
                    "invitation_code": invitation.invitation_code,
                    "level": invitation.level,
                    "status": invitation.status
                }
            }
            
        except Exception as e:
            logger.error(f"创建邀请关系失败: {e}")
            return {
                "success": False,
                "message": f"创建邀请关系失败: {str(e)}"
            }
    
    @staticmethod
    async def accept_invitation(
        db: AsyncSession,
        invitation_code: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        接受邀请
        
        Args:
            db: 数据库会话
            invitation_code: 邀请码
            user_id: 接受邀请的用户ID
            
        Returns:
            Dict: 接受结果
        """
        try:
            # 1. 验证邀请码
            invitation = await InvitationDao.get_invitation_by_code(
                db, invitation_code
            )
            if not invitation:
                return {
                    "success": False,
                    "message": "邀请码无效或已过期"
                }
            
            # 2. 检查邀请是否属于当前用户
            if invitation.invitee_id != user_id:
                return {
                    "success": False,
                    "message": "邀请码不属于当前用户"
                }
            
            # 3. 接受邀请
            success = await InvitationDao.accept_invitation(
                db, invitation.invitation_id
            )
            
            if success:
                return {
                    "success": True,
                    "message": "邀请接受成功",
                    "data": {
                        "invitation_id": invitation.invitation_id,
                        "level": invitation.level,
                        "inviter_id": invitation.inviter_id
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "邀请接受失败"
                }
                
        except Exception as e:
            logger.error(f"接受邀请失败: {e}")
            return {
                "success": False,
                "message": f"接受邀请失败: {str(e)}"
            }
    
    @staticmethod
    async def get_user_invitation_info(
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """
        获取用户邀请信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            Dict: 邀请信息
        """
        try:
            # 1. 获取邀请统计
            invitation_stats = await InvitationDao.get_invitation_statistics(
                db, user_id
            )
            
            # 2. 获取返佣统计
            rebate_stats = await RebateConfigDao.get_rebate_statistics(
                db, user_id
            )
            
            # 3. 获取邀请码
            user_invitations = await InvitationDao.get_user_invitations(
                db, user_id, status="pending"
            )
            invitation_codes = [inv.invitation_code for inv in user_invitations]
            
            return {
                "success": True,
                "data": {
                    "invitation_statistics": invitation_stats,
                    "rebate_statistics": rebate_stats,
                    "invitation_codes": invitation_codes,
                    "max_level": yozuan_config.yozuan_rebate_max_levels
                }
            }
            
        except Exception as e:
            logger.error(f"获取用户邀请信息失败: {e}")
            return {
                "success": False,
                "message": f"获取邀请信息失败: {str(e)}"
            }


class RebateService:
    """返佣业务逻辑服务"""
    
    @staticmethod
    async def process_task_completion_rebate(
        db: AsyncSession,
        order_id: int,
        task_id: int,
        user_id: int,
        task_amount: float
    ) -> Dict[str, Any]:
        """
        处理任务完成返佣
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            task_id: 任务ID
            user_id: 完成任务用户ID
            task_amount: 任务金额
            
        Returns:
            Dict: 返佣处理结果
        """
        try:
            # 1. 获取返佣配置
            rebate_configs = await RebateConfigDao.get_all_configs(db)
            if not rebate_configs:
                return {
                    "success": False,
                    "message": "返佣配置不存在"
                }
            
            # 2. 获取用户的邀请链
            user_invitations = await InvitationDao.get_user_invitations(
                db, user_id, status="accepted"
            )
            
            if not user_invitations:
                return {
                    "success": True,
                    "message": "用户无邀请关系，无需返佣",
                    "data": {"rebate_count": 0}
                }
            
            # 3. 处理各级返佣
            rebate_records = []
            total_rebate_amount = 0
            
            for invitation in user_invitations:
                if invitation.level > yozuan_config.yozuan_rebate_max_levels:
                    continue
                
                # 获取对应层级的返佣配置
                config = next(
                    (c for c in rebate_configs if c.level == invitation.level), 
                    None
                )
                
                if not config or config.status != "enabled":
                    continue
                
                # 计算返佣金额
                rebate_amount = task_amount * float(config.rebate_rate)
                
                # 检查最小和最大返佣金额
                if config.min_amount and rebate_amount < float(config.min_amount):
                    rebate_amount = float(config.min_amount)
                if config.max_amount and rebate_amount > float(config.max_amount):
                    rebate_amount = float(config.max_amount)
                
                # 创建返佣记录
                rebate_record = await RebateConfigDao.create_rebate_record(
                    db=db,
                    order_id=order_id,
                    inviter_id=invitation.inviter_id,
                    invitee_id=user_id,
                    task_id=task_id,
                    rebate_amount=rebate_amount,
                    rebate_rate=float(config.rebate_rate),
                    level=invitation.level,
                    rebate_source="task_completion"
                )
                
                rebate_records.append(rebate_record)
                total_rebate_amount += rebate_amount
                
                # 更新邀请人账户余额
                await AccountDao.update_balance(
                    db, invitation.inviter_id, rebate_amount, "add"
                )
            
            return {
                "success": True,
                "message": "返佣处理成功",
                "data": {
                    "rebate_count": len(rebate_records),
                    "total_rebate_amount": total_rebate_amount,
                    "rebate_records": [
                        {
                            "record_id": record.record_id,
                            "inviter_id": record.inviter_id,
                            "level": record.level,
                            "rebate_amount": float(record.rebate_amount)
                        }
                        for record in rebate_records
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"处理任务完成返佣失败: {e}")
            return {
                "success": False,
                "message": f"处理返佣失败: {str(e)}"
            }
    
    # 注意：任务发布返佣已移除，返佣只在任务完成并通过审核后处理
    # 这样可以确保返佣的公平性和准确性
