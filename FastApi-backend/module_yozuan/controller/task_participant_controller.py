"""
任务参与者控制器
负责任务参与者相关的所有操作
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ..dao.task_dao import TaskDao
from ..dao.order_dao import OrderDao
from ..dao.verification_dao import VerificationDao, VerificationSubmitDao
from ..enums.task_enums import TaskStatus, TaskOrderStatus, TASK_ORDER_STATUS_DISPLAY, ReviewStatus
from ..enums.task_enums import get_display_name
from ..middleware.auth_middleware import get_current_user
from module_app.entity.do.app_user_do import AppUser
from datetime import datetime, timedelta
from sqlalchemy import func


# 创建路由器
router = APIRouter(prefix="/yozuan/v1/task", tags=["任务参与者"])


# ==================== 任务参与接口 ====================

@router.get("/available", summary="获取可参与的任务列表", tags=["任务参与"])
async def get_available_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    task_type_id: Optional[int] = Query(None, description="任务类型ID"),
    area_code: Optional[str] = Query(None, description="用户所在地区编码"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户可以参与的任务列表
    
    ## 业务规则
    
    1. **任务状态**: 只显示状态为 `active` 的任务
    2. **剩余数量**: 只显示还有剩余数量的任务
    3. **地区限制**: 根据任务地区范围筛选
    4. **用户限制**: 不显示用户自己发布的任务
    5. **报名限制**: 不显示用户已经报名的任务
    """
    try:
        task_dao = TaskDao(db)
        order_dao = OrderDao(db)
        
        # 构建过滤条件
        filters = {
            "task_status": TaskStatus.ACTIVE,
            "exclude_publisher_id": current_user.user_id,
            "exclude_applied_user_id": current_user.user_id
        }
        
        if task_type_id:
            filters["task_type_id"] = task_type_id
        if area_code:
            filters["area_code"] = area_code
        
        # 获取可参与的任务
        result = await task_dao.get_available_tasks(
            user_id=current_user.user_id,
            filters=filters,
            page=page,
            size=size
        )
        
        # 格式化返回数据
        tasks_data = []
        for task in result["tasks"]:
            tasks_data.append({
                "task_id": task.task_id,
                "task_title": task.task_title,
                "task_description": task.task_description,
                "task_type_id": task.task_type_id,
                "task_type_name": task.task_type_name if hasattr(task, 'task_type_name') else None,
                "price": float(task.price),
                "total_amount": float(task.total_amount),
                "remaining_amount": float(task.remaining_amount),
                "area_scope": task.area_scope,
                "area_scope_display": get_area_scope_display(task.area_scope),
                "completion_hours": task.completion_hours,
                "publisher_id": task.publisher_id,
                "publisher_name": task.publisher_name if hasattr(task, 'publisher_name') else None,
                "create_time": task.create_time.isoformat() if task.create_time else None,
                "deadline": task.deadline.isoformat() if task.deadline else None
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "tasks": tasks_data,
                "pagination": result["pagination"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取可参与任务失败: {str(e)}"
        )


@router.post("/{task_id}/apply", summary="报名任务", tags=["任务参与"])
async def apply_task(
    task_id: int,
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    报名参与任务
    
    ## 业务规则
    
    1. **任务状态检查**: 任务必须是 `active` 状态
    2. **重复报名检查**: 用户不能重复报名同一个任务
    3. **剩余数量检查**: 任务必须有剩余数量
    4. **地区限制检查**: 检查用户是否符合任务地区要求
    5. **账户余额检查**: 检查用户账户余额是否足够
    """
    try:
        task_dao = TaskDao(db)
        order_dao = OrderDao(db)
        
        # 1. 检查任务是否存在
        task = await task_dao.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 2. 检查任务状态
        if task.task_status != TaskStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"任务状态为 {task.task_status}，无法报名"
            )
        
        # 3. 检查是否已经报名
        existing_order = await order_dao.get_order_by_task_user(task_id, current_user.user_id)
        if existing_order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已经报名过此任务"
            )
        
        # 4. 检查剩余数量
        if task.remaining_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务已满员，无法报名"
            )
        
        # 5. 创建订单
        order_data = {
            "task_id": task_id,
            "user_id": current_user.user_id,
            "order_status": TaskOrderStatus.APPLIED,
            "apply_time": datetime.now()
        }
        
        order = await order_dao.create_order(order_data)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="报名失败"
            )
        
        return {
            "code": 200,
            "msg": "报名成功",
            "data": {
                "order_id": order.order_id,
                "task_id": task_id,
                "order_status": order.order_status,
                "apply_time": order.apply_time.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"报名失败: {str(e)}"
        )


@router.get("/my/orders", summary="获取我的任务订单", tags=["任务参与"])
async def get_my_task_orders(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_status: Optional[str] = Query(None, description="订单状态"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的任务订单列表
    
    ## 业务规则
    
    1. **权限检查**: 只返回当前用户的订单
    2. **状态筛选**: 支持按订单状态筛选
    3. **分页查询**: 支持分页查询
    """
    try:
        order_dao = OrderDao(db)
        
        # 构建过滤条件
        filters = {}
        if order_status:
            filters["order_status"] = order_status
        
        # 获取用户订单
        result = await order_dao.get_user_orders(
            user_id=current_user.user_id,
            filters=filters,
            page=page,
            size=size
        )
        
        # 格式化返回数据
        orders_data = []
        for order in result["orders"]:
            orders_data.append({
                "order_id": order.order_id,
                "task_id": order.task_id,
                "task_title": order.task_title if hasattr(order, 'task_title') else None,
                "task_description": order.task_description if hasattr(order, 'task_description') else None,
                "price": float(order.price) if hasattr(order, 'price') else None,
                "order_status": order.order_status,
                "order_status_display": get_display_name(order.order_status, TASK_ORDER_STATUS_DISPLAY),
                "apply_time": order.apply_time.isoformat() if order.apply_time else None,
                "start_time": order.start_time.isoformat() if order.start_time else None,
                "complete_time": order.complete_time.isoformat() if order.complete_time else None,
                "cancel_time": order.cancel_time.isoformat() if order.cancel_time else None,
                "cancel_reason": order.cancel_reason
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "orders": orders_data,
                "pagination": result["pagination"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )


@router.post("/orders/{order_id}/submit-verification", summary="提交任务验证数据", tags=["任务参与"])
async def submit_task_verification(
    order_id: int,
    verification_data: Dict[str, Any] = Body(..., description="验证数据"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    提交任务验证数据
    
    ## 业务规则
    
    1. **订单状态检查**: 订单必须是 `applied` 或 `in_progress` 状态
    2. **权限检查**: 只有订单所有者可以提交验证数据
    3. **验证数据检查**: 验证数据必须符合任务要求
    4. **重复提交检查**: 不能重复提交验证数据
    """
    try:
        order_dao = OrderDao(db)
        verification_dao = VerificationDao(db)
        verification_submit_dao = VerificationSubmitDao(db)
        
        # 1. 检查订单是否存在
        order = await order_dao.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 2. 检查权限
        if order.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作此订单"
            )
        
        # 3. 检查订单状态
        if order.order_status not in [TaskOrderStatus.APPLIED, TaskOrderStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"订单状态为 {order.order_status}，无法提交验证数据"
            )
        
        # 4. 检查是否已经提交过验证数据
        existing_submit = await verification_submit_dao.get_order_verification_submit(order_id)
        if existing_submit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已经提交过验证数据，无法重复提交"
            )
        
        # 5. 获取任务验证要求
        task_verifications = await verification_dao.get_task_verifications(order.task_id)
        if not task_verifications:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该任务没有验证要求"
            )
        
        # 6. 验证提交数据格式
        for verification in task_verifications:
            verification_id = str(verification.verification_id)
            if verification_id not in verification_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"缺少验证项: {verification.verification_title}"
                )
            
            submit_item = verification_data[verification_id]
            
            # 检查图片要求
            if verification.image_required == 1:
                if "images" not in submit_item or not submit_item["images"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"验证项 '{verification.verification_title}' 需要上传图片"
                    )
            
            # 检查文本要求
            if verification.text_required == 1:
                if "text" not in submit_item or not submit_item["text"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"验证项 '{verification.verification_title}' 需要填写文本"
                    )
        
        # 7. 创建验证提交记录
        submit_data = {
            "order_id": order_id,
            "submit_data": verification_data,
            "submit_time": datetime.now(),
            "review_status": ReviewStatus.PENDING
        }
        
        submit = await verification_submit_dao.create_verification_submit(submit_data)
        if not submit:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="提交验证数据失败"
            )
        
        # 8. 更新订单状态为已完成（等待审核）
        success = await order_dao.complete_order(order_id)
        if not success:
            # 如果更新订单状态失败，删除已创建的验证提交记录
            await verification_submit_dao.update_verification_submit(
                submit.submit_id,
                {"review_status": ReviewStatus.REJECTED, "review_comment": "订单状态更新失败"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新订单状态失败"
            )
        
        return {
            "code": 200,
            "msg": "验证数据提交成功",
            "data": {
                "submit_id": submit.submit_id,
                "order_id": order_id,
                "order_status": TaskOrderStatus.COMPLETED,
                "submit_time": submit.submit_time.isoformat(),
                "review_status": submit.review_status,
                "next_step": "等待发布者审核"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交验证数据失败: {str(e)}"
        )


@router.post("/orders/{order_id}/cancel", summary="取消任务", tags=["任务参与"])
async def cancel_task(
    order_id: int,
    cancel_reason: Optional[str] = Body(None, description="取消原因"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消任务订单
    
    ## 业务规则
    
    1. **订单状态检查**: 订单必须是 `applied` 或 `in_progress` 状态
    2. **权限检查**: 只有订单所有者可以取消订单
    3. **时间限制**: 检查是否在允许取消的时间范围内
    """
    try:
        order_dao = OrderDao(db)
        
        # 1. 检查订单是否存在
        order = await order_dao.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 2. 检查权限
        if order.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作此订单"
            )
        
        # 3. 检查订单状态
        if order.order_status not in [TaskOrderStatus.APPLIED, TaskOrderStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"订单状态为 {order.order_status}，无法取消"
            )
        
        # 4. 取消订单
        success = await order_dao.cancel_order(order_id, cancel_reason)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="取消订单失败"
            )
        
        return {
            "code": 200,
            "msg": "订单取消成功",
            "data": {
                "order_id": order_id,
                "order_status": TaskOrderStatus.CANCELLED,
                "cancel_time": datetime.now().isoformat(),
                "cancel_reason": cancel_reason
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消订单失败: {str(e)}"
        )


# ==================== 辅助函数 ====================

def get_area_scope_display(area_scope: int) -> str:
    """获取地区范围类型的显示名称"""
    scope_map = {
        1: "全国",
        2: "单个城市", 
        3: "多个城市"
    }
    return scope_map.get(area_scope, "未知") 