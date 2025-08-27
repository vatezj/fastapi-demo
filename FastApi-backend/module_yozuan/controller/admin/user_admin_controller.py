"""
用户管理后台控制器
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ...dao.account_dao import AccountDao
from ...dao.invitation_dao import InvitationDao, RebateConfigDao
from ...aspect.yozuan_auth import CheckYozuanInterfaceAuth, CheckYozuanSuperAuth
from ...annotation.yozuan_log import yozuan_user_log
from module_admin.service.login_service import LoginService
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_app.dao.app_user_dao import AppUserDao
from config.enums import BusinessType

router = APIRouter()


@router.get("/users", summary="获取用户列表", tags=["后台管理-用户管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:user:list'))])
async def get_admin_user_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_status: Optional[str] = Query(None, description="用户状态"),
    keyword: Optional[str] = Query(None, description="用户名/手机/邮箱关键词"),
    start_time: Optional[str] = Query(None, description="注册开始时间"),
    end_time: Optional[str] = Query(None, description="注册结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台获取用户列表
    
    ## 查询参数
    
    - **page**: 页码，从1开始
    - **size**: 每页数量，默认20，最大100
    - **user_status**: 用户状态筛选
    - **keyword**: 用户名/手机/邮箱关键词搜索
    - **start_time**: 注册开始时间筛选
    - **end_time**: 注册结束时间筛选
    
    ## 返回数据
    
    返回用户列表，包含用户基本信息、账户信息、邀请关系等
    """
    try:
        # TODO: 检查管理员权限
        
        user_dao = AppUserDao(db)
        result = await user_dao.get_admin_user_list(
            page=page,
            size=size,
            user_status=user_status,
            keyword=keyword,
            start_time=start_time,
            end_time=end_time
        )
        
        # 格式化返回数据
        users_data = []
        for user in result["users"]:
            users_data.append({
                "user_id": user.user_id,
                "user_name": user.user_name,
                "nick_name": user.nick_name,
                "email": user.email,
                "phone": user.phone,
                "sex": user.sex,
                "status": user.status,
                "register_time": user.create_time.isoformat() if user.create_time else None,
                "last_login_time": user.login_date.isoformat() if user.login_date else None,
                "last_login_ip": user.login_ip
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "users": users_data,
                "pagination": {
                    "page": result["page"],
                    "size": result["size"],
                    "total": result["total"],
                    "pages": result["pages"]
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )


@router.get("/users/{user_id}", summary="获取用户详情", tags=["后台管理-用户管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:user:query'))])
async def get_admin_user_detail(
    user_id: int,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台获取用户详情
    
    ## 路径参数
    
    - **user_id**: 用户ID
    
    ## 返回数据
    
    返回用户的完整信息，包括基本信息、账户信息、邀请关系等
    """
    try:
        # TODO: 检查管理员权限
        
        user_dao = AppUserDao(db)
        user = await user_dao.get_user_profile(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 获取账户信息
        account_dao = AccountDao(db)
        account = await account_dao.get_user_account(user_id)
        
        # 获取邀请关系
        invitation_dao = InvitationDao(db)
        invitations = await invitation_dao.get_user_invitation_tree(db, user_id)
        
        # 获取返佣记录
        rebate_dao = RebateConfigDao(db)
        rebate_records = await rebate_dao.get_user_rebate_records(db, user_id)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "user": {
                    "user_id": user.user_id,
                    "user_name": user.user_name,
                    "nick_name": user.nick_name,
                    "email": user.email,
                    "phone": user.phone,
                    "sex": user.sex,
                    "avatar": user.avatar,
                    "status": user.status,
                    "register_time": user.create_time.isoformat() if user.create_time else None,
                    "last_login_time": user.login_date.isoformat() if user.login_date else None,
                    "last_login_ip": user.login_ip,
                    "remark": user.remark
                },
                "account": {
                    "account_id": account.account_id if account else None,
                    "balance": float(account.balance) if account else 0.0,
                    "frozen_amount": float(account.frozen_amount) if account else 0.0,
                    "total_income": float(account.total_income) if account else 0.0,
                    "total_withdraw": float(account.total_withdraw) if account else 0.0,
                    "create_time": account.create_time.isoformat() if account and account.create_time else None
                } if account else None,
                "invitations": {
                    "inviter": invitations.get("inviter"),
                    "invitees": invitations.get("invitees", []),
                    "total_invitees": len(invitations.get("invitees", [])),
                    "invitation_code": invitations.get("invitation_code")
                } if invitations else None,
                "rebate_records": [
                    {
                        "record_id": record.record_id,
                        "rebate_amount": float(record.rebate_amount),
                        "rebate_rate": float(record.rebate_rate),
                        "level": record.level,
                        "rebate_source": record.rebate_source,
                        "status": record.status,
                        "process_time": record.process_time.isoformat() if record.process_time else None
                    }
                    for record in rebate_records
                ] if rebate_records else []
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户详情失败: {str(e)}"
        )


@router.put("/users/{user_id}/status", summary="更新用户状态", tags=["后台管理-用户管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:user:edit'))])
@yozuan_user_log(BusinessType.UPDATE)
async def update_user_status(
    user_id: int,
    status_data: Dict[str, Any] = Body(..., description="状态更新数据", example={
        "status": "1",
        "reason": "用户违规操作，暂时禁用"
    }),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台更新用户状态
    
    ## 路径参数
    
    - **user_id**: 用户ID
    
    ## 请求参数
    
    - **status**: 新的用户状态
    - **reason**: 状态变更原因
    
    ## 业务规则
    
    1. 只有管理员可以更新用户状态
    2. 状态变更会记录操作日志
    3. 禁用用户会影响其任务操作
    """
    try:
        # TODO: 检查管理员权限
        
        new_status = status_data["status"]
        reason = status_data.get("reason", "")
        
        # 验证状态值
        valid_statuses = ["0", "1"]  # 0: 禁用, 1: 启用
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的用户状态: {new_status}"
            )
        
        user_dao = AppUserDao(db)
        success = await user_dao.update_user_status(db, user_id, new_status)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户状态更新失败"
            )
        
        # TODO: 记录操作日志
        
        return {
            "code": 200,
            "msg": "用户状态更新成功",
            "data": {
                "user_id": user_id,
                "new_status": new_status,
                "reason": reason,
                "operator_id": current_user.user_id,
                "update_time": "current_time"  # TODO: 获取当前时间
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户状态失败: {str(e)}"
        )


@router.get("/user-statistics", summary="获取用户统计", tags=["后台管理-用户管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:user:list'))])
async def get_admin_user_statistics(
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """后台获取用户统计信息"""
    try:
        # TODO: 检查管理员权限
        
        user_dao = AppUserDao(db)
        stats = await user_dao.get_admin_user_statistics(
            db, start_time=start_time, end_time=end_time
        )
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "total_users": stats.get("total_users", 0),
                "active_users": stats.get("active_users", 0),
                "disabled_users": stats.get("disabled_users", 0),
                "new_users_today": stats.get("new_users_today", 0),
                "new_users_week": stats.get("new_users_week", 0),
                "new_users_month": stats.get("new_users_month", 0),
                "total_invitations": stats.get("total_invitations", 0),
                "daily_stats": stats.get("daily_stats", [])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户统计失败: {str(e)}"
        )


@router.get("/invitation-statistics", summary="获取邀请统计", tags=["后台管理-用户管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:user:list'))])
async def get_admin_invitation_statistics(
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """后台获取邀请统计信息"""
    try:
        # TODO: 检查管理员权限
        
        invitation_dao = InvitationDao(db)
        stats = await invitation_dao.get_invitation_statistics(
            db, start_time=start_time, end_time=end_time
        )
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "total_invitations": stats.get("total_invitations", 0),
                "accepted_invitations": stats.get("accepted_invitations", 0),
                "pending_invitations": stats.get("pending_invitations", 0),
                "level_1_invitations": stats.get("level_1_invitations", 0),
                "level_2_invitations": stats.get("level_2_invitations", 0),
                "level_3_invitations": stats.get("level_3_invitations", 0),
                "invitation_rate": stats.get("invitation_rate", 0.0),
                "daily_stats": stats.get("daily_stats", [])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取邀请统计失败: {str(e)}"
        )
