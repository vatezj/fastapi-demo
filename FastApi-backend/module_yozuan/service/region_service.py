"""
地区数据服务
提供地区数据的增删改查功能
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from ..dao.region_dao import RegionDao
from ..entity.do.region_do import YozuanRegion


class RegionService:
    """地区数据服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.region_dao = RegionDao(db)
    
    async def get_all_provinces(self) -> List[Dict[str, Any]]:
        """获取所有省份"""
        try:
            provinces = await self.region_dao.get_regions_by_level('province')
            return [
                {
                    "region_code": p.region_code,
                    "region_name": p.region_name,
                    "center_coords": p.center_coords,
                    "citycode": p.citycode
                }
                for p in provinces
            ]
        except Exception as e:
            raise Exception(f"获取省份列表失败: {str(e)}")
    
    async def get_cities_by_province(self, province_code: str) -> List[Dict[str, Any]]:
        """根据省份编码获取城市列表"""
        try:
            cities = await self.region_dao.get_regions_by_parent(province_code)
            return [
                {
                    "region_code": c.region_code,
                    "region_name": c.region_name,
                    "center_coords": c.center_coords,
                    "citycode": c.citycode
                }
                for c in cities
            ]
        except Exception as e:
            raise Exception(f"获取城市列表失败: {str(e)}")
    
    async def get_region_tree(self) -> List[Dict[str, Any]]:
        """获取地区树形结构"""
        try:
            # 获取所有省份
            provinces = await self.region_dao.get_regions_by_level('province')
            
            region_tree = []
            for province in provinces:
                province_data = {
                    "region_code": province.region_code,
                    "region_name": province.region_name,
                    "center_coords": province.center_coords,
                    "citycode": province.citycode,
                    "children": []
                }
                
                # 获取该省份下的城市
                cities = await self.region_dao.get_regions_by_parent(province.region_code)
                for city in cities:
                    city_data = {
                        "region_code": city.region_code,
                        "region_name": city.region_name,
                        "center_coords": city.center_coords,
                        "citycode": city.citycode
                    }
                    province_data["children"].append(city_data)
                
                region_tree.append(province_data)
            
            return region_tree
        except Exception as e:
            raise Exception(f"获取地区树形结构失败: {str(e)}")
    
    async def search_regions(self, keyword: str, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索地区"""
        try:
            regions = await self.region_dao.search_regions(keyword, level)
            return [
                {
                    "region_code": r.region_code,
                    "region_name": r.region_name,
                    "region_level": r.region_level,
                    "parent_code": r.parent_code,
                    "center_coords": r.center_coords,
                    "citycode": r.citycode
                }
                for r in regions
            ]
        except Exception as e:
            raise Exception(f"搜索地区失败: {str(e)}")
    
    async def get_region_by_code(self, region_code: str) -> Optional[Dict[str, Any]]:
        """根据地区编码获取地区信息"""
        try:
            region = await self.region_dao.get_region_by_code(region_code)
            if not region:
                return None
            
            return {
                "region_code": region.region_code,
                "region_name": region.region_name,
                "region_level": region.region_level,
                "parent_code": region.parent_code,
                "center_coords": region.center_coords,
                "citycode": region.citycode,
                "status": region.status
            }
        except Exception as e:
            raise Exception(f"获取地区信息失败: {str(e)}")
    
    async def get_regions_by_codes(self, region_codes: List[str]) -> List[Dict[str, Any]]:
        """根据地区编码列表获取地区信息"""
        try:
            regions = await self.region_dao.get_regions_by_codes(region_codes)
            return [
                {
                    "region_code": r.region_code,
                    "region_name": r.region_name,
                    "region_level": r.region_level,
                    "parent_code": r.parent_code,
                    "center_coords": r.center_coords,
                    "citycode": r.citycode
                }
                for r in regions
            ]
        except Exception as e:
            raise Exception(f"获取地区信息失败: {str(e)}")
    
    async def get_popular_cities(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取热门城市列表"""
        try:
            # 这里可以根据实际需求实现热门城市逻辑
            # 暂时返回一些主要城市
            popular_city_codes = [
                '110100',  # 北京市
                '310100',  # 上海市
                '440100',  # 广州市
                '440300',  # 深圳市
                '330100',  # 杭州市
                '320100',  # 南京市
                '420100',  # 武汉市
                '510100',  # 成都市
                '500100',  # 重庆市
                '610100',  # 西安市
            ]
            
            cities = await self.region_dao.get_regions_by_codes(popular_city_codes)
            return [
                {
                    "region_code": c.region_code,
                    "region_name": c.region_name,
                    "center_coords": c.center_coords,
                    "citycode": c.citycode
                }
                for c in cities
            ][:limit]
        except Exception as e:
            raise Exception(f"获取热门城市失败: {str(e)}")
    
    async def get_region_statistics(self) -> Dict[str, Any]:
        """获取地区统计信息"""
        try:
            stats = await self.region_dao.get_region_statistics()
            return {
                "total_regions": stats.get("total", 0),
                "provinces": stats.get("province", 0),
                "cities": stats.get("city", 0),
                "districts": stats.get("district", 0)
            }
        except Exception as e:
            raise Exception(f"获取地区统计信息失败: {str(e)}") 