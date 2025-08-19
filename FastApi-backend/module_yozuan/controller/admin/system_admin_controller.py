"""
系统管理后台控制器
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ...dao.region_dao import RegionDao
from ...aspect.yozuan_auth import CheckYozuanInterfaceAuth, CheckYozuanSuperAuth
from ...annotation.yozuan_log import yozuan_system_log
from module_admin.service.login_service import LoginService
from module_admin.entity.vo.user_vo import CurrentUserModel
from config.yozuan_config import yozuan_config
from config.enums import BusinessType

router = APIRouter()


@router.get("/dashboard", summary="获取系统仪表板", tags=["后台管理-系统管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:system:dashboard'))])
async def get_system_dashboard(
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台获取系统仪表板数据
    
    ## 返回数据
    
    返回系统的整体统计信息，包括用户、任务、订单、财务等数据
    """
    try:
        # TODO: 检查管理员权限
        
        # 这里应该从各个DAO获取统计数据
        # 暂时返回配置信息作为示例
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "system_info": {
                    "module_name": "游赚模块",
                    "version": "1.0.0",
                    "status": "running"
                },
                "config_summary": {
                    "task_limits": {
                        "max_price": yozuan_config.yozuan_task_max_price,
                        "max_quantity": yozuan_config.yozuan_task_max_quantity,
                        "max_duration": yozuan_config.yozuan_task_max_duration
                    },
                    "account_limits": {
                        "min_withdraw": yozuan_config.yozuan_account_min_withdraw,
                        "max_withdraw": yozuan_config.yozuan_account_max_withdraw
                    },
                    "rebate_limits": {
                        "max_levels": yozuan_config.yozuan_rebate_max_levels,
                        "max_rate": yozuan_config.yozuan_rebate_max_rate
                    }
                },
                "quick_stats": {
                    "total_users": 0,  # TODO: 从DAO获取
                    "total_tasks": 0,  # TODO: 从DAO获取
                    "total_orders": 0,  # TODO: 从DAO获取
                    "total_transactions": 0  # TODO: 从DAO获取
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统仪表板失败: {str(e)}"
        )


@router.get("/regions", summary="获取地区列表", tags=["后台管理-系统管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:system:region'))])
async def get_admin_regions(
    level: Optional[str] = Query(None, description="地区级别：country,province,city,county"),
    parent_code: Optional[str] = Query(None, description="上级地区编码"),
    keyword: Optional[str] = Query(None, description="地区名称关键词"),
    status: Optional[int] = Query(None, description="状态：1启用，0禁用"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台获取地区列表
    
    ## 查询参数
    
    - **level**: 地区级别筛选
    - **parent_code**: 上级地区编码筛选
    - **keyword**: 地区名称关键词搜索
    - **status**: 状态筛选
    - **page**: 页码，从1开始
    - **size**: 每页数量，默认20，最大100
    
    ## 返回数据
    
    返回地区列表，包含地区信息、层级关系等
    """
    try:
        # TODO: 检查管理员权限
        
        region_dao = RegionDao(db)
        result = await region_dao.get_admin_regions(
            level=level,
            parent_code=parent_code,
            keyword=keyword,
            status=status,
            page=page,
            size=size
        )
        
        # 格式化返回数据
        regions_data = []
        for region in result["regions"]:
            regions_data.append({
                "region_code": region.region_code,
                "region_name": region.region_name,
                "region_level": region.region_level,
                "parent_code": region.parent_code,
                "full_name": region.full_name,
                "sort_order": region.sort_order,
                "status": region.status,
                "create_time": region.create_time.isoformat() if region.create_time else None,
                "update_time": region.update_time.isoformat() if region.update_time else None
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "regions": regions_data,
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
            detail=f"获取地区列表失败: {str(e)}"
        )


@router.post("/regions", summary="创建地区", tags=["后台管理-系统管理"],
           dependencies=[Depends(CheckYozuanSuperAuth())])
@yozuan_system_log(BusinessType.INSERT)
async def create_admin_region(
    region_data: Dict[str, Any] = Body(..., description="地区数据", example={
        "region_code": "110000",
        "region_name": "北京市",
        "region_level": "province",
        "parent_code": "100000",
        "full_name": "中国/北京市",
        "sort_order": 1,
        "status": 1
    }),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台创建地区
    
    ## 请求参数
    
    - **region_code**: 地区编码（必填）
    - **region_name**: 地区名称（必填）
    - **region_level**: 地区级别（必填）
    - **parent_code**: 上级地区编码
    - **full_name**: 完整地区名称路径
    - **sort_order**: 排序
    - **status**: 状态
    
    ## 业务规则
    
    1. 只有超级管理员可以创建地区
    2. 地区编码必须唯一
    3. 地区级别必须符合层级关系
    """
    try:
        # TODO: 检查超级管理员权限
        
        region_code = region_data["region_code"]
        region_name = region_data["region_name"]
        region_level = region_data["region_level"]
        parent_code = region_data.get("parent_code")
        full_name = region_data.get("full_name", "")
        sort_order = region_data.get("sort_order", 0)
        region_status = region_data.get("status", 1)
        
        # 验证地区编码
        if not region_code or len(region_code) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="地区编码必须是6位数字"
            )
        
        # 验证地区名称
        if not region_name or len(region_name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="地区名称不能为空且长度不能少于2位"
            )
        
        # 验证地区级别
        valid_levels = ["country", "province", "city", "county"]
        if region_level not in valid_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的地区级别: {region_level}"
            )
        
        # 验证状态
        valid_statuses = [0, 1]
        if region_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值: {region_status}"
            )
        
        region_dao = RegionDao(db)
        
        # 检查地区编码是否已存在
        existing_region = await region_dao.get_region_by_code(db, region_code)
        if existing_region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="地区编码已存在"
            )
        
        # 创建地区
        region = await region_dao.create_region(
            db, region_code, region_name, region_level, 
            parent_code, full_name, sort_order, region_status
        )
        
        return {
            "code": 200,
            "msg": "地区创建成功",
            "data": {
                "region_code": region.region_code,
                "region_name": region.region_name,
                "region_level": region.region_level,
                "parent_code": region.parent_code,
                "full_name": region.full_name,
                "sort_order": region.sort_order,
                "status": region.status,
                "create_time": region.create_time.isoformat() if region.create_time else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建地区失败: {str(e)}"
        )


@router.put("/regions/{region_code}", summary="更新地区", tags=["后台管理-系统管理"],
           dependencies=[Depends(CheckYozuanSuperAuth())])
@yozuan_system_log(BusinessType.UPDATE)
async def update_admin_region(
    region_code: str,
    region_data: Dict[str, Any] = Body(..., description="地区更新数据", example={
        "region_name": "北京市（更新）",
        "full_name": "中国/北京市（更新）",
        "sort_order": 2,
        "status": 1
    }),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台更新地区
    
    ## 路径参数
    
    - **region_code**: 地区编码
    
    ## 请求参数
    
    - **region_name**: 地区名称
    - **full_name**: 完整地区名称路径
    - **sort_order**: 排序
    - **status**: 状态
    
    ## 业务规则
    
    1. 只有超级管理员可以更新地区
    2. 地区编码不能修改
    3. 地区级别不能修改
    """
    try:
        # TODO: 检查超级管理员权限
        
        region_name = region_data.get("region_name")
        full_name = region_data.get("full_name")
        sort_order = region_data.get("sort_order")
        region_status = region_data.get("status")
        
        # 验证地区名称
        if region_name is not None and (not region_name or len(region_name.strip()) < 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="地区名称不能为空且长度不能少于2位"
            )
        
        # 验证状态
        if region_status is not None and region_status not in [0, 1]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值: {region_status}"
            )
        
        region_dao = RegionDao(db)
        
        # 检查地区是否存在
        existing_region = await region_dao.get_region_by_code(db, region_code)
        if not existing_region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="地区不存在"
            )
        
        # 更新地区
        success = await region_dao.update_region(
            db, region_code, region_name, full_name, sort_order, region_status
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="地区更新失败"
            )
        
        # 获取更新后的地区信息
        updated_region = await region_dao.get_region_by_code(db, region_code)
        
        return {
            "code": 200,
            "msg": "地区更新成功",
            "data": {
                "region_code": updated_region.region_code,
                "region_name": updated_region.region_name,
                "region_level": updated_region.region_level,
                "parent_code": updated_region.parent_code,
                "full_name": updated_region.full_name,
                "sort_order": updated_region.sort_order,
                "status": updated_region.status,
                "update_time": updated_region.update_time.isoformat() if updated_region.update_time else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新地区失败: {str(e)}"
        )


@router.delete("/regions/{region_code}", summary="删除地区", tags=["后台管理-系统管理"],
           dependencies=[Depends(CheckYozuanSuperAuth())])
@yozuan_system_log(BusinessType.DELETE)
async def delete_admin_region(
    region_code: str,
    reason: str = Body(..., description="删除原因"),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    后台删除地区
    
    ## 路径参数
    
    - **region_code**: 地区编码
    
    ## 请求参数
    
    - **reason**: 删除原因
    
    ## 业务规则
    
    1. 只有超级管理员可以删除地区
    2. 有下级地区的地区不能删除
    3. 被任务使用的地区不能删除
    4. 删除操作会记录操作日志
    """
    try:
        # TODO: 检查超级管理员权限
        
        region_dao = RegionDao(db)
        
        # 检查地区是否存在
        existing_region = await region_dao.get_region_by_code(db, region_code)
        if not existing_region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="地区不存在"
            )
        
        # 检查是否有下级地区
        child_regions = await region_dao.get_child_regions(db, region_code)
        if child_regions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该地区有下级地区，不能删除"
            )
        
        # TODO: 检查是否被任务使用
        
        # 执行删除
        success = await region_dao.delete_region(db, region_code)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="地区删除失败"
            )
        
        # TODO: 记录操作日志
        
        return {
            "code": 200,
            "msg": "地区删除成功",
            "data": {
                "region_code": region_code,
                "region_name": existing_region.region_name,
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
            detail=f"删除地区失败: {str(e)}"
        )


@router.get("/system-config", summary="获取系统配置", tags=["后台管理-系统管理"],
           dependencies=[Depends(CheckYozuanInterfaceAuth('yozuan:system:config'))])
async def get_system_config(
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """后台获取系统配置信息"""
    try:
        # TODO: 检查管理员权限
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "module_config": {
                    "module_switch": yozuan_config.yozuan_module_switch,
                    "database_prefix": yozuan_config.yozuan_database_prefix
                },
                "task_config": {
                    "max_price": yozuan_config.yozuan_task_max_price,
                    "max_quantity": yozuan_config.yozuan_task_max_quantity,
                    "max_duration": yozuan_config.yozuan_task_max_duration,
                    "min_price": yozuan_config.yozuan_task_min_price
                },
                "order_config": {
                    "max_concurrent": yozuan_config.yozuan_order_max_concurrent,
                    "auto_cancel_time": yozuan_config.yozuan_order_auto_cancel_time
                },
                "account_config": {
                    "min_withdraw": yozuan_config.yozuan_account_min_withdraw,
                    "max_withdraw": yozuan_config.yozuan_account_max_withdraw,
                    "min_recharge": yozuan_config.yozuan_account_min_recharge,
                    "max_recharge": yozuan_config.yozuan_account_max_recharge
                },
                "rebate_config": {
                    "max_levels": yozuan_config.yozuan_rebate_max_levels,
                    "max_rate": yozuan_config.yozuan_rebate_max_rate,
                    "min_amount": yozuan_config.yozuan_rebate_min_amount
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统配置失败: {str(e)}"
        )
