"""
任务管理控制器 - 公共接口
负责任务相关的公共查询接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ..dao.task_dao import TaskDao, TaskTypeDao, TaskStepDao, TaskTagDao
from ..dao.region_dao import TaskRegionDao
from ..enums.task_enums import TaskStatus, TaskStepType, TaskVerificationType
from ..enums.task_enums import get_display_name, TASK_STATUS_DISPLAY, TASK_STEP_TYPE_DISPLAY
from ..middleware.auth_middleware import get_current_user, get_current_user_id
from module_app.entity.do.app_user_do import AppUser


def get_area_scope_display(area_scope: int) -> str:
    """获取地区范围类型的显示名称"""
    scope_map = {
        1: "全国",
        2: "单个城市", 
        3: "多个城市"
    }
    return scope_map.get(area_scope, "未知")


def get_display_name(value: str, display_map: Dict[str, str]) -> str:
    """获取显示名称"""
    return display_map.get(value, value)


# 创建路由器
router = APIRouter(prefix="/yozuan/v1/task", tags=["任务公共"])


# ==================== 公共查询接口 ====================

@router.get("/types", summary="获取任务类型列表")
async def get_task_types(
    db: AsyncSession = Depends(get_db)
):
    """获取任务类型列表"""
    try:
        task_type_dao = TaskTypeDao(db)
        types = await task_type_dao.get_all_task_types()  # 修复方法名
        
        types_data = []
        for task_type in types:
            types_data.append({
                "type_id": task_type.type_id,
                "type_name": task_type.type_name,
                "type_code": task_type.type_code,
                "description": task_type.description
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


@router.get("/tags", summary="获取任务标签列表")
async def get_task_tags(
    db: AsyncSession = Depends(get_db)
):
    """获取任务标签列表"""
    try:
        task_tag_dao = TaskTagDao(db)
        tags = await task_tag_dao.get_all_tags()
        
        tags_data = []
        for tag in tags:
            tags_data.append({
                "tag_id": tag.tag_id,
                "tag_name": tag.tag_name,
                "tag_code": tag.tag_code,
                "description": tag.description
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": tags_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务标签失败: {str(e)}"
        )


@router.get("/", summary="获取任务列表")
async def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    task_type_id: Optional[int] = Query(None, description="任务类型ID"),
    task_status: Optional[str] = Query(None, description="任务状态"),
    area_scope: Optional[int] = Query(None, description="地区范围"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取任务列表（公共接口，无需登录）
    """
    try:
        task_dao = TaskDao(db)
        
        # 构建过滤条件
        filters = {}
        if task_type_id:
            filters["task_type_id"] = task_type_id
        if task_status:
            filters["task_status"] = task_status
        if area_scope:
            filters["area_scope"] = area_scope
        if min_price is not None:
            filters["min_price"] = min_price
        if max_price is not None:
            filters["max_price"] = max_price
        
        # 使用get_available_tasks方法，但传入一个不存在的用户ID来获取所有任务
        result = await task_dao.get_available_tasks(
            user_id=0,  # 使用0作为特殊值，表示获取所有任务
            filters=filters,
            page=page,
            size=size
        )
        
        # 格式化返回数据
        tasks_data = []
        for task in result["tasks"]:
            tasks_data.append({
                "task_id": task.task_id,
                "task_name": task.task_name,
                "task_description": task.task_description,
                "task_price": float(task.task_price),
                "task_quantity": task.task_quantity,
                "completed_quantity": task.completed_quantity,
                "remaining_quantity": task.task_quantity - task.completed_quantity,
                "task_type_name": getattr(task, 'task_type_name', '未知类型'),
                "area_scope": task.area_scope,
                "area_scope_display": get_area_scope_display(task.area_scope),
                "task_status": task.task_status,
                "status_display": get_display_name(task.task_status, TASK_STATUS_DISPLAY),
                "completion_hours": task.completion_hours,
                "create_time": task.create_time.isoformat() if task.create_time else None
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


@router.get("/{task_id}", summary="获取任务详情")
async def get_task_detail(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取任务详情（公共接口，无需登录）
    
    ## 路径参数
    
    - **task_id**: 任务ID
    """
    try:
        task_dao = TaskDao(db)
        
        # 获取任务详情
        task = await task_dao.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 格式化返回数据
        task_data = {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "task_description": task.task_description,
            "task_price": float(task.task_price),
            "task_quantity": task.task_quantity,
            "completed_quantity": task.completed_quantity,
            "remaining_quantity": task.task_quantity - task.completed_quantity,
            "task_type_name": getattr(task, 'task_type_name', '未知类型'),
            "area_scope": task.area_scope,
            "area_scope_display": get_area_scope_display(task.area_scope),
            "task_status": task.task_status,
            "status_display": get_display_name(task.task_status, TASK_STATUS_DISPLAY),
            "completion_hours": task.completion_hours,
            "review_hours": task.review_hours,
            "device_limit": task.device_limit,
            "frequency_limit": task.frequency_limit,
            "task_tag": task.task_tag,
            "create_time": task.create_time.isoformat() if task.create_time else None,
            "start_time": task.start_time.isoformat() if task.start_time else None,
            "end_time": task.end_time.isoformat() if task.end_time else None
        }
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": task_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务详情失败: {str(e)}"
        )


@router.get("/status/options", summary="获取任务状态选项")
async def get_task_status_options():
    """获取任务状态选项"""
    return {
        "code": 200,
        "msg": "获取成功",
        "data": [
            {"value": "draft", "label": "草稿"},
            {"value": "pending", "label": "待审核"},
            {"value": "active", "label": "进行中"},
            {"value": "paused", "label": "已暂停"},
            {"value": "completed", "label": "已完成"},
            {"value": "cancelled", "label": "已取消"}
        ]
    }


@router.get("/step-types/options", summary="获取步骤类型选项")
async def get_step_type_options():
    """获取步骤类型选项"""
    return {
        "code": 200,
        "msg": "获取成功",
        "data": [
            {"value": "link", "label": "链接"},
            {"value": "image", "label": "图片"},
            {"value": "text", "label": "文本"}
        ]
    }


@router.get("/verification-types/options", summary="获取验证类型选项")
async def get_verification_type_options():
    """获取验证类型选项"""
    return {
        "code": 200,
        "msg": "获取成功",
        "data": [
            {"value": "image", "label": "仅图片"},
            {"value": "text", "label": "仅文本"},
            {"value": "both", "label": "图片和文本都需要"}
        ]
    }
