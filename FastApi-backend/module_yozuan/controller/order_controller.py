"""
订单管理控制器
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ..dao.order_dao import OrderDao
from ..enums.task_enums import TaskOrderStatus, get_display_name, TASK_ORDER_STATUS_DISPLAY

router = APIRouter()


@router.get("/", summary="获取我的订单列表")
async def get_my_orders(
    status: Optional[str] = Query(None, description="订单状态"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的订单列表"""
    try:
        # TODO: 从当前用户获取user_id
        user_id = 1  # 临时写死，实际应该从JWT token获取
        
        order_dao = OrderDao(db)
        result = await order_dao.get_user_orders(
            user_id=user_id,
            status=status,
            page=page,
            size=size
        )
        
        # 格式化返回数据
        orders_data = []
        for order in result["orders"]:
            orders_data.append({
                "order_id": order.order_id,
                "task_id": order.task_id,
                "order_status": order.order_status,
                "status_display": get_display_name(order.order_status, TASK_ORDER_STATUS_DISPLAY),
                "apply_time": order.apply_time.isoformat() if order.apply_time else None,
                "start_time": order.start_time.isoformat() if order.start_time else None,
                "complete_time": order.complete_time.isoformat() if order.complete_time else None,
                "verify_time": order.verify_time.isoformat() if order.verify_time else None,
                "commission_amount": float(order.commission_amount) if order.commission_amount else None,
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
        raise HTTPException(status_code=500, detail=f"获取订单列表失败: {str(e)}")


@router.get("/{order_id}", summary="获取订单详情")
async def get_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取订单详情"""
    try:
        # TODO: 从当前用户获取user_id
        user_id = 1  # 临时写死，实际应该从JWT token获取
        
        order_dao = OrderDao(db)
        order = await order_dao.get_order_by_id(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 检查权限：只能查看自己的订单
        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权访问此订单")
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "order_id": order.order_id,
                "task_id": order.task_id,
                "order_status": order.order_status,
                "status_display": get_display_name(order.order_status, TASK_ORDER_STATUS_DISPLAY),
                "apply_time": order.apply_time.isoformat() if order.apply_time else None,
                "start_time": order.start_time.isoformat() if order.start_time else None,
                "complete_time": order.complete_time.isoformat() if order.complete_time else None,
                "verify_time": order.verify_time.isoformat() if order.verify_time else None,
                "commission_amount": float(order.commission_amount) if order.commission_amount else None,
                "reject_reason": order.reject_reason,
                "create_time": order.create_time.isoformat() if order.create_time else None,
                "update_time": order.update_time.isoformat() if order.update_time else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订单详情失败: {str(e)}")


@router.get("/statistics/summary", summary="获取订单统计")
async def get_order_statistics(db: AsyncSession = Depends(get_db)):
    """获取当前用户的订单统计信息"""
    try:
        # TODO: 从当前用户获取user_id
        user_id = 1  # 临时写死，实际应该从JWT token获取
        
        order_dao = OrderDao(db)
        stats = await order_dao.get_order_statistics(user_id)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "status_counts": stats["status_counts"],
                "total_commission": stats["total_commission"],
                "total_orders": stats["total_orders"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订单统计失败: {str(e)}")


@router.get("/status/options", summary="获取订单状态选项")
async def get_order_status_options():
    """获取订单状态选项，用于前端下拉框"""
    from ..enums.task_enums import get_enum_choices, TaskOrderStatus, TASK_ORDER_STATUS_DISPLAY
    
    return {
        "code": 200,
        "msg": "获取成功",
        "data": get_enum_choices(TaskOrderStatus, TASK_ORDER_STATUS_DISPLAY)
    }
