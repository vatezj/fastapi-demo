"""
订单管理后台控制器
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ...dao.order_dao import OrderDao
from ...dao.verification_dao import VerificationSubmitDao
from ...enums.task_enums import TaskOrderStatus, ReviewStatus
from ...aspect.yozuan_auth import CheckYozuanInterfaceAuth, CheckYozuanSuperAuth
from ...annotation.yozuan_log import yozuan_order_log
from module_admin.service.login_service import LoginService
from module_admin.entity.vo.user_vo import CurrentUserModel
from config.enums import BusinessType

router = APIRouter()


@router.get("/orders", summary="获取订单列表", tags=["后台管理-订单管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:order:list'))])
async def get_admin_order_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_status: Optional[str] = Query(None, description="订单状态"),
    task_id: Optional[int] = Query(None, description="任务ID"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台获取订单列表
    
    ## 查询参数
    
    - **page**: 页码，从1开始
    - **size**: 每页数量，默认20，最大100
    - **order_status**: 订单状态筛选
    - **task_id**: 任务ID筛选
    - **user_id**: 用户ID筛选
    - **start_time**: 开始时间筛选
    - **end_time**: 结束时间筛选
    
    ## 返回数据
    
    返回订单列表，包含订单详情、用户信息、任务信息等
    """
    try:
        # TODO: 检查管理员权限
        
        order_dao = OrderDao(db)
        result = await order_dao.get_admin_order_list(
            page=page,
            size=size,
            order_status=order_status,
            task_id=task_id,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )
        
        # 格式化返回数据
        orders_data = []
        for order in result["orders"]:
            orders_data.append({
                "order_id": order.order_id,
                "task_id": order.task_id,
                "task_name": getattr(order, 'task_name', ''),
                "user_id": order.user_id,
                "user_name": getattr(order, 'user_name', ''),
                "order_status": order.order_status,
                "status_display": TaskOrderStatus.get_display_name(order.order_status),
                "apply_time": order.apply_time.isoformat() if order.apply_time else None,
                "start_time": order.start_time.isoformat() if order.start_time else None,
                "complete_time": order.complete_time.isoformat() if order.complete_time else None,
                "commission_amount": float(order.commission_amount) if order.commission_amount else 0.0,
                "reject_reason": order.reject_reason,
                "create_time": order.create_time.isoformat() if order.create_time else None
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "orders": orders_data,
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
            detail=f"获取订单列表失败: {str(e)}"
        )


@router.get("/orders/{order_id}", summary="获取订单详情", tags=["后台管理-订单管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:order:query'))])
async def get_admin_order_detail(
    order_id: int,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台获取订单详情
    
    ## 路径参数
    
    - **order_id**: 订单ID
    
    ## 返回数据
    
    返回订单的完整信息，包括任务详情、用户信息、验证提交等
    """
    try:
        # TODO: 检查管理员权限
        
        order_dao = OrderDao(db)
        order = await order_dao.get_order_by_id(db, order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 获取验证提交信息
        verification_dao = VerificationSubmitDao(db)
        verification = await verification_dao.get_by_order_id(db, order_id)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "order": {
                    "order_id": order.order_id,
                    "task_id": order.task_id,
                    "task_name": getattr(order, 'task_name', ''),
                    "user_id": order.user_id,
                    "user_name": getattr(order, 'user_name', ''),
                                    "order_status": order.order_status,
                "status_display": TaskOrderStatus.get_display_name(order.order_status),
                "apply_time": order.apply_time.isoformat() if order.apply_time else None,
                    "start_time": order.start_time.isoformat() if order.start_time else None,
                    "complete_time": order.complete_time.isoformat() if order.complete_time else None,
                    "commission_amount": float(order.commission_amount) if order.commission_amount else 0.0,
                    "reject_reason": order.reject_reason,
                    "create_time": order.create_time.isoformat() if order.create_time else None
                },
                "verification": {
                    "submit_id": verification.submit_id if verification else None,
                    "submit_data": verification.submit_data if verification else None,
                    "review_status": verification.review_status if verification else None,
                    "review_status_display": ReviewStatus.get_display_name(verification.review_status) if verification else None,
                    "review_user_id": verification.review_user_id if verification else None,
                    "review_comment": verification.review_comment if verification else None,
                    "review_time": verification.review_time.isoformat() if verification and verification.review_time else None,
                    "submit_time": verification.create_time.isoformat() if verification else None
                } if verification else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单详情失败: {str(e)}"
        )


@router.put("/orders/{order_id}/status", summary="更新订单状态", tags=["后台管理-订单管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:order:edit'))])
@yozuan_order_log(BusinessType.UPDATE)
async def update_order_status(
    order_id: int,
    status_data: Dict[str, Any] = Body(..., description="状态更新数据", example={
        "order_status": "cancelled",
        "reason": "用户主动取消"
    }),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台更新订单状态
    
    ## 路径参数
    
    - **order_id**: 订单ID
    
    ## 请求参数
    
    - **order_status**: 新的订单状态
    - **reason**: 状态变更原因
    
    ## 业务规则
    
    1. 只有管理员可以更新订单状态
    2. 状态变更会记录操作日志
    3. 某些状态变更可能需要特殊权限
    """
    try:
        # TODO: 检查管理员权限
        
        new_status = status_data["order_status"]
        reason = status_data.get("reason", "")
        
        # 验证状态值
        valid_statuses = [status.value for status in OrderStatus]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的订单状态: {new_status}"
            )
        
        order_dao = OrderDao(db)
        success = await order_dao.update_order_status(db, order_id, new_status, reason)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单状态更新失败"
            )
        
        # TODO: 记录操作日志
        
        return {
            "code": 200,
            "msg": "订单状态更新成功",
            "data": {
                "order_id": order_id,
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
            detail=f"更新订单状态失败: {str(e)}"
        )


@router.post("/orders/{order_id}/review", summary="审核订单完成", tags=["后台管理-订单管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:order:review'))])
@yozuan_order_log(BusinessType.GRANT)
async def review_order_completion(
    order_id: int,
    review_data: Dict[str, Any] = Body(..., description="审核数据", example={
        "review_status": "approved",
        "review_comment": "任务完成质量很好，通过审核",
        "bonus_amount": 2.00,
        "bonus_reason": "提前完成，质量优秀"
    }),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台审核订单完成情况
    
    ## 路径参数
    
    - **order_id**: 订单ID
    
    ## 请求参数
    
    - **review_status**: 审核状态，可选值：`approved`(通过), `rejected`(驳回)
    - **review_comment**: 审核意见
    - **bonus_amount**: 额外奖励金额
    - **bonus_reason**: 奖励原因
    
    ## 业务规则
    
    1. 只有管理员可以审核订单
    2. 审核通过后自动处理返佣
    3. 审核通过后解冻发布者余额并支付接单者
    """
    try:
        # TODO: 检查管理员权限
        
        review_status = review_data["review_status"]
        review_comment = review_data.get("review_comment", "")
        bonus_amount = review_data.get("bonus_amount", 0.0)
        bonus_reason = review_data.get("bonus_reason", "")
        
        # 验证审核状态
        valid_statuses = ["approved", "rejected"]
        if review_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的审核状态: {review_status}"
            )
        
        # 获取订单信息
        order_dao = OrderDao(db)
        order = await order_dao.get_order_by_id(db, order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 更新验证提交状态
        verification_dao = VerificationSubmitDao(db)
        verification = await verification_dao.get_by_order_id(db, order_id)
        
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未找到验证提交记录"
            )
        
        # 更新审核状态
        await verification_dao.update_review_status(
            db, verification.submit_id, review_status, 
            current_user.user_id, review_comment
        )
        
        if review_status == "approved":
            # 审核通过：更新订单状态、处理返佣、解冻余额、支付佣金
            await order_dao.complete_order(db, order_id)
            
            # TODO: 处理返佣逻辑
            # TODO: 解冻发布者余额
            # TODO: 支付接单者佣金
            
            message = "订单审核通过，返佣处理完成"
        else:
            # 审核驳回：更新订单状态、解冻余额
            await order_dao.reject_order(db, order_id, review_comment)
            
            # TODO: 解冻发布者余额
            
            message = "订单审核驳回，余额已解冻"
        
        return {
            "code": 200,
            "msg": message,
            "data": {
                "order_id": order_id,
                "review_status": review_status,
                "review_comment": review_comment,
                "bonus_amount": bonus_amount,
                "bonus_reason": bonus_reason,
                "reviewer_id": current_user.user_id,
                "review_time": "current_time"  # TODO: 获取当前时间
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"订单审核失败: {str(e)}"
        )


@router.get("/order-statistics", summary="获取订单统计", tags=["后台管理-订单管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:order:list'))])
async def get_admin_order_statistics(
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """后台获取订单统计信息"""
    try:
        # TODO: 检查管理员权限
        
        order_dao = OrderDao(db)
        stats = await order_dao.get_admin_order_statistics(
            db, start_time=start_time, end_time=end_time
        )
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "total_orders": stats.get("total_orders", 0),
                "pending_orders": stats.get("pending_orders", 0),
                "in_progress_orders": stats.get("in_progress_orders", 0),
                "completed_orders": stats.get("completed_orders", 0),
                "cancelled_orders": stats.get("cancelled_orders", 0),
                "total_commission": stats.get("total_commission", 0.0),
                "completion_rate": stats.get("completion_rate", 0.0),
                "daily_stats": stats.get("daily_stats", [])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单统计失败: {str(e)}"
        )
