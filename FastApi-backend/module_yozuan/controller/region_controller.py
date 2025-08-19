"""
地区管理控制器
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ..dao.region_dao import RegionDao, TaskRegionDao
from ..middleware.auth_middleware import get_current_user
from module_app.entity.do.app_user_do import AppUser

router = APIRouter()


@router.get("/list", summary="获取地区列表", tags=["地区管理"])
async def get_regions(
    level: Optional[str] = Query(None, description="地区级别：country,province,city,county"),
    parent_code: Optional[str] = Query(None, description="上级地区编码"),
    keyword: Optional[str] = Query(None, description="地区名称关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取地区列表
    
    ## 查询参数
    
    - **level**: 地区级别筛选
        - `country`: 国家级
        - `province`: 省级
        - `city`: 市级
        - `county`: 县级
    
    - **parent_code**: 上级地区编码，用于获取子地区
    
    - **keyword**: 地区名称关键词，支持模糊搜索
    
    - **limit**: 返回数量限制，默认20，最大100
    
    ## 返回数据
    
    返回地区列表，包含地区编码、名称、级别、完整名称等信息
    """
    try:
        region_dao = RegionDao(db)
        
        if level:
            # 按级别获取
            regions = await region_dao.get_regions_by_level(level)
        elif parent_code:
            # 按上级地区获取
            regions = await region_dao.get_regions_by_parent(parent_code)
        elif keyword:
            # 按关键词搜索
            regions = await region_dao.search_regions(keyword, limit)
        else:
            # 获取所有省级地区
            regions = await region_dao.get_regions_by_level('province')
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": [
                {
                    "region_code": r.region_code,
                    "region_name": r.region_name,
                    "region_level": r.region_level,
                    "parent_code": r.parent_code,
                    "full_name": r.full_name,
                    "sort_order": r.sort_order
                }
                for r in regions
            ],
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取地区列表失败: {str(e)}"
        )


@router.get("/tree", summary="获取地区树形结构", tags=["地区管理"])
async def get_region_tree(db: AsyncSession = Depends(get_db)):
    """
    获取完整的地区树形结构
    
    ## 返回数据
    
    返回树形结构的地区数据，包含层级关系和子地区信息
    """
    try:
        region_dao = RegionDao(db)
        tree = await region_dao.get_region_tree()
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": tree,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取地区树形结构失败: {str(e)}"
        )


@router.get("/{region_code}", summary="获取地区详情", tags=["地区管理"])
async def get_region_detail(
    region_code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    根据地区编码获取地区详情
    
    ## 路径参数
    
    - **region_code**: 地区编码（6位数字）
    
    ## 返回数据
    
    返回地区详细信息，包含上级地区、子地区等信息
    """
    try:
        region_dao = RegionDao(db)
        region = await region_dao.get_region_by_code(region_code)
        
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="地区不存在"
            )
        
        # 获取子地区
        children = await region_dao.get_regions_by_parent(region_code)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "region_code": region.region_code,
                "region_name": region.region_name,
                "region_level": region.region_level,
                "parent_code": region.parent_code,
                "full_name": region.full_name,
                "sort_order": region.sort_order,
                "children": [
                    {
                        "region_code": c.region_code,
                        "region_name": c.region_name,
                        "region_level": c.region_level,
                        "full_name": c.full_name
                    }
                    for c in children
                ]
            },
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取地区详情失败: {str(e)}"
        )


@router.get("/task/{task_id}/regions", summary="获取任务的地区信息", tags=["地区管理"])
async def get_task_regions(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定任务的地区关联信息
    
    ## 路径参数
    
    - **task_id**: 任务ID
    
    ## 返回数据
    
    返回任务关联的所有地区信息
    """
    try:
        task_region_dao = TaskRegionDao(db)
        regions = await task_region_dao.get_task_regions_with_info(task_id)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": regions,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务地区信息失败: {str(e)}"
        )


@router.get("/statistics/overview", summary="获取地区统计概览", tags=["地区管理"])
async def get_region_statistics(db: AsyncSession = Depends(get_db)):
    """
    获取地区统计概览
    
    ## 返回数据
    
    返回地区数量统计和任务分布统计
    """
    try:
        task_region_dao = TaskRegionDao(db)
        stats = await task_region_dao.get_region_statistics()
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": stats,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取地区统计失败: {str(e)}"
        )


@router.get("/search/suggestions", summary="获取地区搜索建议", tags=["地区管理"])
async def get_region_suggestions(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="建议数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取地区搜索建议
    
    ## 查询参数
    
    - **keyword**: 搜索关键词，至少1个字符
    
    - **limit**: 建议数量，默认10，最大50
    
    ## 返回数据
    
    返回匹配的地区建议列表，用于搜索框自动补全
    """
    try:
        region_dao = RegionDao(db)
        suggestions = await region_dao.search_regions(keyword, limit)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": [
                {
                    "region_code": r.region_code,
                    "region_name": r.region_name,
                    "region_level": r.region_level,
                    "full_name": r.full_name,
                    "display_text": f"{r.region_name} ({r.full_name})"
                }
                for r in suggestions
            ],
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取地区搜索建议失败: {str(e)}"
        )
