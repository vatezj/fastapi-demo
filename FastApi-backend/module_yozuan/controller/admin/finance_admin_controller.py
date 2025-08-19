"""
财务管理后台控制器
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ...dao.account_dao import AccountDao
from ...dao.invitation_dao import RebateConfigDao
from ...enums.task_enums import TransactionType, TransactionStatus
from ...aspect.yozuan_auth import CheckYozuanInterfaceAuth, CheckYozuanFinanceAuth, CheckYozuanSuperAuth
from ...annotation.yozuan_log import yozuan_finance_log
from module_admin.service.login_service import LoginService
from module_admin.entity.vo.user_vo import CurrentUserModel
from config.enums import BusinessType

router = APIRouter()


@router.get("/transactions", summary="获取交易记录", tags=["后台管理-财务管理"],
           dependencies=[Depends(CheckYozuanFinanceAuth())])
async def get_admin_transactions(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    transaction_type: Optional[str] = Query(None, description="交易类型"),
    transaction_status: Optional[str] = Query(None, description="交易状态"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    min_amount: Optional[float] = Query(None, description="最小金额"),
    max_amount: Optional[float] = Query(None, description="最大金额"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台获取交易记录
    
    ## 查询参数
    
    - **page**: 页码，从1开始
    - **size**: 每页数量，默认20，最大100
    - **transaction_type**: 交易类型筛选
    - **transaction_status**: 交易状态筛选
    - **user_id**: 用户ID筛选
    - **min_amount**: 最小金额筛选
    - **max_amount**: 最大金额筛选
    - **start_time**: 开始时间筛选
    - **end_time**: 结束时间筛选
    
    ## 返回数据
    
    返回交易记录列表，包含交易详情、用户信息等
    """
    try:
        # TODO: 检查管理员权限
        
        account_dao = AccountDao(db)
        result = await account_dao.get_admin_transactions(
            page=page,
            size=size,
            transaction_type=transaction_type,
            transaction_status=transaction_status,
            user_id=user_id,
            min_amount=min_amount,
            max_amount=max_amount,
            start_time=start_time,
            end_time=end_time
        )
        
        # 格式化返回数据
        transactions_data = []
        for transaction in result["transactions"]:
            transactions_data.append({
                "transaction_id": transaction.transaction_id,
                "account_id": transaction.account_id,
                "user_id": getattr(transaction, 'user_id', ''),
                "user_name": getattr(transaction, 'user_name', ''),
                "transaction_type": transaction.transaction_type,
                "type_display": TransactionType.get_display_name(transaction.transaction_type),
                "amount": float(transaction.amount),
                "balance_before": float(transaction.balance_before),
                "balance_after": float(transaction.balance_after),
                "description": transaction.description,
                "status": transaction.status,
                "status_display": TransactionStatus.get_display_name(transaction.status),
                "related_id": transaction.related_id,
                "payment_method": getattr(transaction, 'payment_method', ''),
                "payment_channel": getattr(transaction, 'payment_channel', ''),
                "withdraw_method": getattr(transaction, 'withdraw_method', ''),
                "withdraw_account": getattr(transaction, 'withdraw_account', ''),
                "real_name": getattr(transaction, 'real_name', ''),
                "create_time": transaction.create_time.isoformat() if transaction.create_time else None,
                "update_time": transaction.update_time.isoformat() if transaction.update_time else None
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "transactions": transactions_data,
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
            detail=f"获取交易记录失败: {str(e)}"
        )


@router.get("/withdraw-applications", summary="获取提现申请", tags=["后台管理-财务管理"],
           dependencies=[Depends(CheckYozuanFinanceAuth())])
async def get_withdraw_applications(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    review_status: Optional[str] = Query(None, description="审核状态"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    min_amount: Optional[float] = Query(None, description="最小金额"),
    max_amount: Optional[float] = Query(None, description="最大金额"),
    start_time: Optional[str] = Query(None, description="申请开始时间"),
    end_time: Optional[str] = Query(None, description="申请结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台获取提现申请列表
    
    ## 查询参数
    
    - **page**: 页码，从1开始
    - **size**: 每页数量，默认20，最大100
    - **review_status**: 审核状态筛选
    - **user_id**: 用户ID筛选
    - **min_amount**: 最小金额筛选
    - **max_amount**: 最大金额筛选
    - **start_time**: 申请开始时间筛选
    - **end_time**: 申请结束时间筛选
    
    ## 返回数据
    
    返回提现申请列表，包含申请详情、用户信息等
    """
    try:
        # TODO: 检查管理员权限
        
        account_dao = AccountDao(db)
        result = await account_dao.get_admin_withdraw_applications(
            page=page,
            size=size,
            review_status=review_status,
            user_id=user_id,
            min_amount=min_amount,
            max_amount=max_amount,
            start_time=start_time,
            end_time=end_time
        )
        
        # 格式化返回数据
        applications_data = []
        for application in result["applications"]:
            applications_data.append({
                "transaction_id": application.transaction_id,
                "user_id": getattr(application, 'user_id', ''),
                "user_name": getattr(application, 'user_name', ''),
                "amount": float(application.amount),
                "withdraw_method": application.withdraw_method,
                "withdraw_account": application.withdraw_account,
                "real_name": application.real_name,
                "status": application.status,
                "status_display": TransactionStatus.get_display_name(application.status),
                "description": application.description,
                "create_time": application.create_time.isoformat() if application.create_time else None,
                "update_time": application.update_time.isoformat() if application.update_time else None
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "applications": applications_data,
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
            detail=f"获取提现申请失败: {str(e)}"
        )


@router.post("/withdraw-applications/{transaction_id}/review", summary="审核提现申请", tags=["后台管理-财务管理"],
           dependencies=[Depends(CheckYozuanFinanceAuth())])
@yozuan_finance_log(BusinessType.GRANT)
async def review_withdraw_application(
    transaction_id: int,
    review_data: Dict[str, Any] = Body(..., description="审核数据", example={
        "review_status": "approved",
        "review_comment": "提现申请审核通过",
        "reject_reason": ""
    }),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台审核提现申请
    
    ## 路径参数
    
    - **transaction_id**: 交易ID
    
    ## 请求参数
    
    - **review_status**: 审核状态，可选值：`approved`(通过), `rejected`(驳回)
    - **review_comment**: 审核意见
    - **reject_reason**: 驳回原因（驳回时必填）
    
    ## 业务规则
    
    1. 只有财务管理员可以审核提现申请
    2. 审核通过后提现状态变为成功
    3. 审核驳回后解冻用户余额
    4. 审核操作会记录操作日志
    """
    try:
        # TODO: 检查财务管理员权限
        
        review_status = review_data["review_status"]
        review_comment = review_data.get("review_comment", "")
        reject_reason = review_data.get("reject_reason", "")
        
        # 验证审核状态
        valid_statuses = ["approved", "rejected"]
        if review_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的审核状态: {review_status}"
            )
        
        # 验证驳回原因
        if review_status == "rejected" and not reject_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驳回时必须提供驳回原因"
            )
        
        account_dao = AccountDao(db)
        
        # 获取提现申请信息
        transaction = await account_dao.get_transaction_by_id(db, transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提现申请不存在"
            )
        
        if transaction.transaction_type != "withdraw":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该交易不是提现申请"
            )
        
        if transaction.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该提现申请已被处理"
            )
        
        # 执行审核
        if review_status == "approved":
            # 审核通过：更新交易状态
            success = await account_dao.update_transaction_status(
                db, transaction_id, "success", review_comment
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="提现申请审核失败"
                )
            
            message = "提现申请审核通过"
        else:
            # 审核驳回：更新交易状态、解冻余额
            success = await account_dao.update_transaction_status(
                db, transaction_id, "failed", reject_reason
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="提现申请驳回失败"
                )
            
            # 解冻用户余额
            user_id = getattr(transaction, 'user_id', None)
            if user_id:
                await account_dao.update_balance(
                    db, user_id, float(transaction.amount), "unfreeze"
                )
            
            message = "提现申请已驳回，余额已解冻"
        
        # TODO: 记录操作日志
        
        return {
            "code": 200,
            "msg": message,
            "data": {
                "transaction_id": transaction_id,
                "review_status": review_status,
                "review_comment": review_comment,
                "reject_reason": reject_reason,
                "reviewer_id": current_user.user_id,
                "review_time": "current_time"  # TODO: 获取当前时间
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审核提现申请失败: {str(e)}"
        )


@router.get("/finance-statistics", summary="获取财务统计", tags=["后台管理-财务管理"],
           dependencies=[Depends(CheckYozuanFinanceAuth())])
async def get_finance_statistics(
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """后台获取财务统计信息"""
    try:
        # TODO: 检查管理员权限
        
        account_dao = AccountDao(db)
        stats = await account_dao.get_finance_statistics(
            db, start_time=start_time, end_time=end_time
        )
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "total_recharge": stats.get("total_recharge", 0.0),
                "total_withdraw": stats.get("total_withdraw", 0.0),
                "total_commission": stats.get("total_commission", 0.0),
                "total_rebate": stats.get("total_rebate", 0.0),
                "pending_withdrawals": stats.get("pending_withdrawals", 0.0),
                "total_users": stats.get("total_users", 0),
                "active_accounts": stats.get("active_accounts", 0),
                "daily_stats": stats.get("daily_stats", [])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取财务统计失败: {str(e)}"
        )


@router.get("/rebate-config", summary="获取返佣配置", tags=["后台管理-财务管理"],
           dependencies=[Depends(CheckYozuanFinanceAuth())])
async def get_rebate_config(
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """后台获取返佣配置"""
    try:
        # TODO: 检查管理员权限
        
        rebate_dao = RebateConfigDao(db)
        configs = await rebate_dao.get_all_configs(db)
        
        configs_data = []
        for config in configs:
            configs_data.append({
                "config_id": config.config_id,
                "level": config.level,
                "rebate_rate": float(config.rebate_rate),
                "min_amount": float(config.min_amount) if config.min_amount else None,
                "max_amount": float(config.max_amount) if config.max_amount else None,
                "status": config.status,
                "description": config.description,
                "create_time": config.create_time.isoformat() if config.create_time else None,
                "update_time": config.update_time.isoformat() if config.update_time else None
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": configs_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取返佣配置失败: {str(e)}"
        )


@router.put("/rebate-config/{config_id}", summary="更新返佣配置", tags=["后台管理-财务管理"],
           dependencies=[Depends(CheckYozuanSuperAuth())])
@yozuan_finance_log(BusinessType.UPDATE)
async def update_rebate_config(
    config_id: int,
    config_data: Dict[str, Any] = Body(..., description="配置更新数据", example={
        "rebate_rate": 0.05,
        "min_amount": 10.00,
        "max_amount": 1000.00,
        "status": "enabled",
        "description": "一级返佣配置"
    }),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台更新返佣配置
    
    ## 路径参数
    
    - **config_id**: 配置ID
    
    ## 请求参数
    
    - **rebate_rate**: 返佣比例
    - **min_amount**: 最小返佣金额
    - **max_amount**: 最大返佣金额
    - **status**: 配置状态
    - **description**: 配置描述
    
    ## 业务规则
    
    1. 只有超级管理员可以更新返佣配置
    2. 返佣比例必须在合理范围内
    3. 配置更新会记录操作日志
    """
    try:
        # TODO: 检查超级管理员权限
        
        rebate_rate = config_data["rebate_rate"]
        min_amount = config_data.get("min_amount")
        max_amount = config_data.get("max_amount")
        config_status = config_data["status"]
        description = config_data.get("description", "")
        
        # 验证返佣比例
        if rebate_rate < 0 or rebate_rate > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="返佣比例必须在0-1之间"
            )
        
        # 验证金额范围
        if min_amount is not None and max_amount is not None:
            if min_amount > max_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="最小金额不能大于最大金额"
                )
        
        # 验证状态
        valid_statuses = ["enabled", "disabled"]
        if config_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的配置状态: {config_status}"
            )
        
        rebate_dao = RebateConfigDao(db)
        success = await rebate_dao.update_rebate_config(
            db, config_id, rebate_rate, min_amount, max_amount, config_status, description
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="返佣配置更新失败"
            )
        
        # TODO: 记录操作日志
        
        return {
            "code": 200,
            "msg": "返佣配置更新成功",
            "data": {
                "config_id": config_id,
                "rebate_rate": rebate_rate,
                "min_amount": min_amount,
                "max_amount": max_amount,
                "status": config_status,
                "description": description,
                "operator_id": current_user.user_id,
                "update_time": "current_time"  # TODO: 获取当前时间
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新返佣配置失败: {str(e)}"
        )
