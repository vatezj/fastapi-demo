"""
地区数据控制器
提供地区数据的API接口
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from config.get_db import get_db
from ..service.region_service import RegionService
from shared.utils.response_util import ResponseUtil

router = APIRouter()


@router.get("/provinces", summary="获取所有省份", tags=["地区数据"])
async def get_all_provinces(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有省份列表
    
    ## 响应说明
    
    ### 成功响应
    ```json
    {
        "code": 200,
        "msg": "获取成功",
        "data": [
            {
                "region_code": "110000",
                "region_name": "北京市",
                "center_coords": "116.407387,39.904179",
                "citycode": "010"
            }
        ],
        "success": true
    }
    ```
    """
    try:
        region_service = RegionService(db)
        provinces = await region_service.get_all_provinces()
        
        return ResponseUtil.success(
            data=provinces,
            msg="获取省份列表成功"
        )
    except Exception as e:
        return ResponseUtil.error(f"获取省份列表失败: {str(e)}")


@router.get("/cities/{province_code}", summary="根据省份获取城市", tags=["地区数据"])
async def get_cities_by_province(
    province_code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    根据省份编码获取城市列表
    
    ## 路径参数
    
    - **province_code** (string, 必填): 省份编码，如：110000
    
    ## 响应说明
    
    ### 成功响应
    ```json
    {
        "code": 200,
        "msg": "获取成功",
        "data": [
            {
                "region_code": "110100",
                "region_name": "北京城区",
                "center_coords": "116.405285,39.904989",
                "citycode": "010"
            }
        ],
        "success": true
    }
    ```
    """
    try:
        region_service = RegionService(db)
        cities = await region_service.get_cities_by_province(province_code)
        
        return ResponseUtil.success(
            data=cities,
            msg="获取城市列表成功"
        )
    except Exception as e:
        return ResponseUtil.error(f"获取城市列表失败: {str(e)}")


@router.get("/tree", summary="获取地区树形结构", tags=["地区数据"])
async def get_region_tree(
    db: AsyncSession = Depends(get_db)
):
    """
    获取地区树形结构（省份-城市）
    
    ## 响应说明
    
    ### 成功响应
    ```json
    {
        "code": 200,
        "msg": "获取成功",
        "data": [
            {
                "region_code": "110000",
                "region_name": "北京市",
                "center_coords": "116.407387,39.904179",
                "citycode": "010",
                "children": [
                    {
                        "region_code": "110100",
                        "region_name": "北京城区",
                        "center_coords": "116.405285,39.904989",
                        "citycode": "010"
                    }
                ]
            }
        ],
        "success": true
    }
    ```
    """
    try:
        region_service = RegionService(db)
        tree = await region_service.get_region_tree()
        
        return ResponseUtil.success(
            data=tree,
            msg="获取地区树形结构成功"
        )
    except Exception as e:
        return ResponseUtil.error(f"获取地区树形结构失败: {str(e)}")


@router.get("/search", summary="搜索地区", tags=["地区数据"])
async def search_regions(
    keyword: str = Query(..., description="搜索关键词"),
    level: Optional[str] = Query(None, description="地区级别：province/city/district"),
    db: AsyncSession = Depends(get_db)
):
    """
    搜索地区
    
    ## 查询参数
    
    - **keyword** (string, 必填): 搜索关键词
    - **level** (string, 可选): 地区级别筛选
    
    ## 响应说明
    
    ### 成功响应
    ```json
    {
        "code": 200,
        "msg": "搜索成功",
        "data": [
            {
                "region_code": "110100",
                "region_name": "北京城区",
                "region_level": "city",
                "parent_code": "110000",
                "center_coords": "116.405285,39.904989",
                "citycode": "010"
            }
        ],
        "success": true
    }
    ```
    """
    try:
        region_service = RegionService(db)
        regions = await region_service.search_regions(keyword, level)
        
        return ResponseUtil.success(
            data=regions,
            msg="搜索地区成功"
        )
    except Exception as e:
        return ResponseUtil.error(f"搜索地区失败: {str(e)}")


@router.get("/info/{region_code}", summary="根据编码获取地区信息", tags=["地区数据"])
async def get_region_info(
    region_code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    根据地区编码获取地区详细信息
    
    ## 路径参数
    
    - **region_code** (string, 必填): 地区编码，如：110100
    
    ## 响应说明
    
    ### 成功响应
    ```json
    {
        "code": 200,
        "msg": "获取成功",
        "data": {
            "region_code": "110100",
            "region_name": "北京城区",
            "region_level": "city",
            "parent_code": "110000",
            "center_coords": "116.405285,39.904989",
            "citycode": "010",
            "status": 1
        },
        "success": true
    }
    ```
    """
    try:
        region_service = RegionService(db)
        region = await region_service.get_region_by_code(region_code)
        
        if not region:
            return ResponseUtil.error("地区不存在")
        
        return ResponseUtil.success(
            data=region,
            msg="获取地区信息成功"
        )
    except Exception as e:
        return ResponseUtil.error(f"获取地区信息失败: {str(e)}")


@router.post("/batch-info", summary="批量获取地区信息", tags=["地区数据"])
async def get_batch_region_info(
    region_codes: List[str],
    db: AsyncSession = Depends(get_db)
):
    """
    批量获取地区信息
    
    ## 请求参数
    
    - **region_codes** (array, 必填): 地区编码列表
    
    ## 响应说明
    
    ### 成功响应
    ```json
    {
        "code": 200,
        "msg": "获取成功",
        "data": [
            {
                "region_code": "110100",
                "region_name": "北京城区",
                "region_level": "city",
                "parent_code": "110000",
                "center_coords": "116.405285,39.904989",
                "citycode": "010"
            }
        ],
        "success": true
    }
    ```
    """
    try:
        if not region_codes:
            return ResponseUtil.error("地区编码列表不能为空")
        
        region_service = RegionService(db)
        regions = await region_service.get_regions_by_codes(region_codes)
        
        return ResponseUtil.success(
            data=regions,
            msg="批量获取地区信息成功"
        )
    except Exception as e:
        return ResponseUtil.error(f"批量获取地区信息失败: {str(e)}")


@router.get("/popular-cities", summary="获取热门城市", tags=["地区数据"])
async def get_popular_cities(
    limit: int = Query(20, description="返回数量限制", ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    获取热门城市列表
    
    ## 查询参数
    
    - **limit** (integer, 可选): 返回数量限制，默认20，最大100
    
    ## 响应说明
    
    ### 成功响应
    ```json
    {
        "code": 200,
        "msg": "获取成功",
        "data": [
            {
                "region_code": "110100",
                "region_name": "北京城区",
                "center_coords": "116.405285,39.904989",
                "citycode": "010"
            }
        ],
        "success": true
    }
    ```
    """
    try:
        region_service = RegionService(db)
        cities = await region_service.get_popular_cities(limit)
        
        return ResponseUtil.success(
            data=cities,
            msg="获取热门城市成功"
        )
    except Exception as e:
        return ResponseUtil.error(f"获取热门城市失败: {str(e)}")


@router.get("/statistics", summary="获取地区统计信息", tags=["地区数据"])
async def get_region_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    获取地区统计信息
    
    ## 响应说明
    
    ### 成功响应
    ```json
    {
        "code": 200,
        "msg": "获取成功",
        "data": {
            "total_regions": 3000,
            "provinces": 34,
            "cities": 333,
            "districts": 2633
        },
        "success": true
    }
    ```
    """
    try:
        region_service = RegionService(db)
        stats = await region_service.get_region_statistics()
        
        return ResponseUtil.success(
            data=stats,
            msg="获取地区统计信息成功"
        )
    except Exception as e:
        return ResponseUtil.error(f"获取地区统计信息失败: {str(e)}") 