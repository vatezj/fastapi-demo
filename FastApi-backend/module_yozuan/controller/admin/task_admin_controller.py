"""
任务管理后台控制器
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ...dao.task_dao import TaskDao, TaskTypeDao, TaskStepDao, TaskTagDao
from ...dao.region_dao import TaskRegionDao
from ...enums.task_enums import TaskStatus, DeviceLimit, FrequencyLimit, TaskStepType, TaskVerificationType
from ...aspect.yozuan_auth import CheckYozuanInterfaceAuth, CheckYozuanSuperAuth
from ...annotation.yozuan_log import yozuan_task_log
from module_admin.service.login_service import LoginService
from module_admin.entity.vo.user_vo import CurrentUserModel
from config.enums import BusinessType

router = APIRouter()


@router.get("/tasks", summary="获取任务列表", tags=["后台管理-任务管理"], 
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:task:list'))])
async def get_admin_task_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    task_status: Optional[str] = Query(None, description="任务状态"),
    task_type_id: Optional[int] = Query(None, description="任务类型ID"),
    publisher_id: Optional[int] = Query(None, description="发布者ID"),
    keyword: Optional[str] = Query(None, description="任务名称关键词"),
    min_price: Optional[float] = Query(None, description="最小价格"),
    max_price: Optional[float] = Query(None, description="最大价格"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台获取任务列表
    
    ## 查询参数
    
    - **page**: 页码，从1开始
    - **size**: 每页数量，默认20，最大100
    - **task_status**: 任务状态筛选
    - **task_type_id**: 任务类型筛选
    - **publisher_id**: 发布者ID筛选
    - **keyword**: 任务名称关键词搜索
    - **min_price**: 最小价格筛选
    - **max_price**: 最大价格筛选
    - **start_time**: 开始时间筛选
    - **end_time**: 结束时间筛选
    
    ## 返回数据
    
    返回任务列表，包含任务详情、发布者信息、统计数据等
    """
    try:
        # 权限检查已通过依赖注入完成
        
        task_dao = TaskDao(db)
        result = await task_dao.get_admin_task_list(
            page=page,
            size=size,
            task_status=task_status,
            task_type_id=task_type_id,
            publisher_id=publisher_id,
            keyword=keyword,
            min_price=min_price,
            max_price=max_price,
            start_time=start_time,
            end_time=end_time
        )
        
        # 格式化返回数据
        tasks_data = []
        for task in result["tasks"]:
            tasks_data.append({
                "task_id": task.task_id,
                "task_name": task.task_name,
                "task_type_id": task.task_type_id,
                "task_price": float(task.task_price),
                "task_quantity": task.task_quantity,
                "task_status": task.task_status,
                "status_display": TaskStatus.get_display_name(task.task_status),
                "device_limit": task.device_limit,
                "device_limit_display": DeviceLimit.get_display_name(task.device_limit),
                "frequency_limit": task.frequency_limit,
                "frequency_limit_display": FrequencyLimit.get_display_name(task.frequency_limit),
                "publisher_id": task.publisher_id,
                "publisher_name": getattr(task, 'publisher_name', ''),
                "create_time": task.create_time.isoformat() if task.create_time else None,
                "update_time": task.update_time.isoformat() if task.update_time else None,
                "total_applications": getattr(task, 'total_applications', 0),
                "completed_orders": getattr(task, 'completed_orders', 0),
                "total_amount": float(task.task_price) * task.task_quantity
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "tasks": tasks_data,
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
            detail=f"获取任务列表失败: {str(e)}"
        )


@router.get("/tasks/{task_id}", summary="获取任务详情", tags=["后台管理-任务管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:task:query'))])
async def get_admin_task_detail(
    task_id: int,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台获取任务详情
    
    ## 路径参数
    
    - **task_id**: 任务ID
    
    ## 返回数据
    
    返回任务的完整信息，包括步骤、验证要求、地区等
    """
    try:
        # TODO: 检查管理员权限
        
        task_dao = TaskDao(db)
        task = await task_dao.get_task_with_details(db, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 获取任务步骤
        step_dao = TaskStepDao(db)
        steps = await step_dao.get_task_steps(db, task_id)
        
        # 获取任务验证要求
        verification_dao = TaskDao(db)  # 这里需要创建VerificationDao
        verifications = await verification_dao.get_task_verifications(db, task_id)
        
        # 获取任务地区
        region_dao = TaskRegionDao(db)
        regions = await region_dao.get_task_regions(db, task_id)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "task": {
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "task_type_id": task.task_type_id,
                    "task_price": float(task.task_price),
                    "task_quantity": task.task_quantity,
                    "task_status": task.task_status,
                    "status_display": TaskStatus.get_display_name(task.task_status),
                    "device_limit": task.device_limit,
                    "device_limit_display": DeviceLimit.get_display_name(task.device_limit),
                    "frequency_limit": task.frequency_limit,
                    "frequency_limit_display": FrequencyLimit.get_display_name(task.frequency_limit),
                    "task_description": task.task_description,
                    "publisher_id": task.publisher_id,
                    "publisher_name": getattr(task, 'publisher_name', ''),
                    "create_time": task.create_time.isoformat() if task.create_time else None,
                    "update_time": task.update_time.isoformat() if task.update_time else None
                },
                "steps": [
                    {
                        "step_id": step.step_id,
                        "step_order": step.step_order,
                        "step_type": step.step_type,
                        "step_type_display": TaskStepType.get_display_name(step.step_type),
                        "step_content": step.step_content,
                        "step_images": step.step_images
                    }
                    for step in steps
                ],
                "verifications": [
                    {
                        "verification_id": v.verification_id,
                        "verification_title": v.verification_title,
                        "verification_type": v.verification_type,
                        "verification_type_display": TaskVerificationType.get_display_name(v.verification_type),
                        "image_required": v.image_required,
                        "text_required": v.text_required,
                        "text_placeholder": v.text_placeholder
                    }
                    for v in verifications
                ],
                "regions": [
                    {
                        "region_code": r.region_code,
                        "region_name": r.region_name,
                        "region_level": r.region_level
                    }
                    for r in regions
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务详情失败: {str(e)}"
        )


@router.put("/tasks/{task_id}/status", summary="更新任务状态", tags=["后台管理-任务管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:task:edit'))])
@yozuan_task_log(BusinessType.UPDATE)
async def update_task_status(
    task_id: int,
    status_data: Dict[str, Any] = Body(..., description="状态更新数据", example={
        "task_status": "suspended",
        "reason": "任务内容违规，暂停发布"
    }),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台更新任务状态
    
    ## 路径参数
    
    - **task_id**: 任务ID
    
    ## 请求参数
    
    - **task_status**: 新的任务状态
    - **reason**: 状态变更原因
    
    ## 业务规则
    
    1. 只有管理员可以更新任务状态
    2. 状态变更会记录操作日志
    3. 某些状态变更可能需要特殊权限
    """
    try:
        # TODO: 检查管理员权限
        
        new_status = status_data["task_status"]
        reason = status_data.get("reason", "")
        
        # 验证状态值
        valid_statuses = [status.value for status in TaskStatus]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的任务状态: {new_status}"
            )
        
        task_dao = TaskDao(db)
        success = await task_dao.update_task_status(db, task_id, new_status)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务状态更新失败"
            )
        
        # TODO: 记录操作日志
        
        return {
            "code": 200,
            "msg": "任务状态更新成功",
            "data": {
                "task_id": task_id,
                "old_status": "previous_status",  # TODO: 获取原状态
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
            detail=f"更新任务状态失败: {str(e)}"
        )


@router.delete("/tasks/{task_id}", summary="删除任务", tags=["后台管理-任务管理"],
           dependencies=[Depends(CheckYozuanSuperAuth())])
@yozuan_task_log(BusinessType.DELETE)
async def delete_admin_task(
    task_id: int,
    reason: str = Body(..., description="删除原因"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台删除任务
    
    ## 路径参数
    
    - **task_id**: 任务ID
    
    ## 请求参数
    
    - **reason**: 删除原因
    
    ## 业务规则
    
    1. 只有超级管理员可以删除任务
    2. 删除任务会同时删除相关的步骤、验证要求等
    3. 已有人接单的任务不能直接删除
    4. 删除操作会记录操作日志
    """
    try:
        # TODO: 检查超级管理员权限
        
        task_dao = TaskDao(db)
        
        # 检查任务是否可以删除
        task = await task_dao.get_task_with_details(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 检查是否有进行中的订单
        # TODO: 实现订单检查逻辑
        
        # 执行删除
        success = await task_dao.delete_task(db, task_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务删除失败"
            )
        
        # TODO: 记录操作日志
        
        return {
            "code": 200,
            "msg": "任务删除成功",
            "data": {
                "task_id": task_id,
                "reason": reason,
                "operator_id": current_user.user_id,
                "delete_time": "current_time"  # TODO: 获取当前时间
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除任务失败: {str(e)}"
        )


@router.get("/task-types", summary="获取任务类型列表", tags=["后台管理-任务管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:task:list'))])
async def get_admin_task_types(
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """后台获取任务类型列表"""
    try:
        # TODO: 检查管理员权限
        
        task_type_dao = TaskTypeDao(db)
        task_types = await task_type_dao.get_all_task_types(db)
        
        types_data = []
        for task_type in task_types:
            types_data.append({
                "type_id": task_type.type_id,
                "type_name": task_type.type_name,
                "type_code": task_type.type_code,
                "type_description": getattr(task_type, 'type_description', ''),
                "status": getattr(task_type, 'status', 'enabled'),
                "create_time": task_type.create_time.isoformat() if task_type.create_time else None
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": types_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务类型失败: {str(e)}"
        )


@router.get("/task-statistics", summary="获取任务统计", tags=["后台管理-任务管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:task:list'))])
async def get_admin_task_statistics(
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """后台获取任务统计信息"""
    try:
        # TODO: 检查管理员权限
        
        task_dao = TaskDao(db)
        stats = await task_dao.get_admin_task_statistics(
            db, start_time=start_time, end_time=end_time
        )
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "total_tasks": stats.get("total_tasks", 0),
                "active_tasks": stats.get("active_tasks", 0),
                "completed_tasks": stats.get("completed_tasks", 0),
                "suspended_tasks": stats.get("suspended_tasks", 0),
                "total_amount": stats.get("total_amount", 0.0),
                "total_orders": stats.get("total_orders", 0),
                "completion_rate": stats.get("completion_rate", 0.0),
                "daily_stats": stats.get("daily_stats", [])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务统计失败: {str(e)}"
        )
