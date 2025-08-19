"""
邀请和分销相关API控制器
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ..middleware.auth_middleware import get_current_user, get_current_user_id
from ..service.invitation_service import InvitationService, RebateService
from ..dao.invitation_dao import InvitationDao, RebateConfigDao
from module_app.entity.do.app_user_do import AppUser
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# 创建路由器
invitation_router = APIRouter()

# ==================== 邀请管理接口 ====================

@invitation_router.post("/create", tags=["邀请管理"])
async def create_invitation(
    invitee_id: int = Body(..., description="被邀请人用户ID"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建邀请关系
    
    - **invitee_id**: 被邀请人用户ID
    - **current_user**: 当前认证用户（邀请人）
    """
    try:
        result = await InvitationService.create_invitation_chain(
            db=db,
            inviter_id=current_user.user_id,
            invitee_id=invitee_id
        )
        
        if result["success"]:
            return {
                "code": 200,
                "msg": result["message"],
                "data": result["data"],
                "success": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建邀请关系失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建邀请关系失败"
        )


@invitation_router.post("/accept", tags=["邀请管理"])
async def accept_invitation(
    invitation_code: str = Body(..., description="邀请码"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    接受邀请
    
    - **invitation_code**: 邀请码
    - **current_user**: 当前认证用户（被邀请人）
    """
    try:
        result = await InvitationService.accept_invitation(
            db=db,
            invitation_code=invitation_code,
            user_id=current_user.user_id
        )
        
        if result["success"]:
            return {
                "code": 200,
                "msg": result["message"],
                "data": result["data"],
                "success": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"接受邀请失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="接受邀请失败"
        )


@invitation_router.get("/info", tags=["邀请管理"])
async def get_invitation_info(
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户邀请信息
    
    - **current_user**: 当前认证用户
    """
    try:
        result = await InvitationService.get_user_invitation_info(
            db=db,
            user_id=current_user.user_id
        )
        
        if result["success"]:
            return {
                "code": 200,
                "msg": "获取邀请信息成功",
                "data": result["data"],
                "success": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取邀请信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取邀请信息失败"
        )


@invitation_router.get("/list", tags=["邀请管理"])
async def get_user_invitations(
    status: str = Query(None, description="邀请状态"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户邀请列表
    
    - **status**: 邀请状态（可选）
    - **current_user**: 当前认证用户
    """
    try:
        invitations = await InvitationDao.get_user_invitations(
            db=db,
            user_id=current_user.user_id,
            status=status
        )
        
        invitation_list = []
        for invitation in invitations:
            invitation_list.append({
                "invitation_id": invitation.invitation_id,
                "invitee_id": invitation.invitee_id,
                "invitation_code": invitation.invitation_code,
                "invitation_time": invitation.invitation_time,
                "accept_time": invitation.accept_time,
                "status": invitation.status,
                "level": invitation.level
            })
        
        return {
            "code": 200,
            "msg": "获取邀请列表成功",
            "data": {
                "invitations": invitation_list,
                "total": len(invitation_list)
            },
            "success": True
        }
        
    except Exception as e:
        logger.error(f"获取邀请列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取邀请列表失败"
        )


# ==================== 返佣管理接口 ====================

@invitation_router.get("/rebate/records", tags=["返佣管理"])
async def get_rebate_records(
    status: str = Query(None, description="返佣状态"),
    limit: int = Query(100, description="返回记录数量限制"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户返佣记录
    
    - **status**: 返佣状态（可选）
    - **limit**: 返回记录数量限制
    - **current_user**: 当前认证用户
    """
    try:
        records = await RebateConfigDao.get_user_rebate_records(
            db=db,
            user_id=current_user.user_id,
            status=status,
            limit=limit
        )
        
        record_list = []
        for record in records:
            record_list.append({
                "record_id": record.record_id,
                "order_id": record.order_id,
                "task_id": record.task_id,
                "invitee_id": record.invitee_id,
                "rebate_amount": float(record.rebate_amount),
                "rebate_rate": float(record.rebate_rate),
                "level": record.level,
                "rebate_source": record.rebate_source,
                "status": record.status,
                "process_time": record.process_time,
                "create_time": record.create_time
            })
        
        return {
            "code": 200,
            "msg": "获取返佣记录成功",
            "data": {
                "records": record_list,
                "total": len(record_list)
            },
            "success": True
        }
        
    except Exception as e:
        logger.error(f"获取返佣记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取返佣记录失败"
        )


@invitation_router.get("/rebate/statistics", tags=["返佣管理"])
async def get_rebate_statistics(
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户返佣统计
    
    - **current_user**: 当前认证用户
    """
    try:
        stats = await RebateConfigDao.get_rebate_statistics(
            db=db,
            user_id=current_user.user_id
        )
        
        return {
            "code": 200,
            "msg": "获取返佣统计成功",
            "data": stats,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"获取返佣统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取返佣统计失败"
        )


@invitation_router.get("/rebate/config", tags=["返佣管理"])
async def get_rebate_config(
    db: AsyncSession = Depends(get_db)
):
    """
    获取返佣配置
    
    返回所有层级的返佣配置信息
    """
    try:
        configs = await RebateConfigDao.get_all_configs(db)
        
        config_list = []
        for config in configs:
            config_list.append({
                "config_id": config.config_id,
                "level": config.level,
                "rebate_rate": float(config.rebate_rate),
                "min_amount": float(config.min_amount) if config.min_amount else None,
                "max_amount": float(config.max_amount) if config.max_amount else None,
                "status": config.status,
                "description": config.description
            })
        
        return {
            "code": 200,
            "msg": "获取返佣配置成功",
            "data": {
                "configs": config_list,
                "total": len(config_list)
            },
            "success": True
        }
        
    except Exception as e:
        logger.error(f"获取返佣配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取返佣配置失败"
        )


# ==================== 邀请统计接口 ====================

@invitation_router.get("/statistics", tags=["邀请统计"])
async def get_invitation_statistics(
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户邀请统计
    
    - **current_user**: 当前认证用户
    """
    try:
        stats = await InvitationDao.get_invitation_statistics(
            db=db,
            user_id=current_user.user_id
        )
        
        return {
            "code": 200,
            "msg": "获取邀请统计成功",
            "data": stats,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"获取邀请统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取邀请统计失败"
        )
