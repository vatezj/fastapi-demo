"""
地区相关DAO类
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from typing import List, Optional, Dict, Any
from ..entity.do.region_do import YozuanRegion, YozuanTaskRegion


class RegionDao:
    """地区DAO"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_region_by_code(self, region_code: str) -> Optional[YozuanRegion]:
        """根据地区编码获取地区信息"""
        result = await self.db.execute(
            select(YozuanRegion).where(
                and_(
                    YozuanRegion.region_code == region_code,
                    YozuanRegion.status == 1
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_regions_by_level(self, level: str) -> List[YozuanRegion]:
        """根据级别获取地区列表"""
        result = await self.db.execute(
            select(YozuanRegion).where(
                and_(
                    YozuanRegion.region_level == level,
                    YozuanRegion.status == 1
                )
            ).order_by(YozuanRegion.sort_order, YozuanRegion.region_code)
        )
        return result.scalars().all()
    
    async def get_regions_by_parent(self, parent_code: str) -> List[YozuanRegion]:
        """根据上级地区编码获取子地区列表"""
        result = await self.db.execute(
            select(YozuanRegion).where(
                and_(
                    YozuanRegion.parent_code == parent_code,
                    YozuanRegion.status == 1
                )
            ).order_by(YozuanRegion.sort_order, YozuanRegion.region_code)
        )
        return result.scalars().all()
    
    async def search_regions(self, keyword: str, limit: int = 20) -> List[YozuanRegion]:
        """搜索地区"""
        result = await self.db.execute(
            select(YozuanRegion).where(
                and_(
                    or_(
                        YozuanRegion.region_name.like(f"%{keyword}%"),
                        YozuanRegion.full_name.like(f"%{keyword}%")
                    ),
                    YozuanRegion.status == 1
                )
            ).order_by(YozuanRegion.sort_order, YozuanRegion.region_code).limit(limit)
        )
        return result.scalars().all()
    
    async def get_region_tree(self) -> List[Dict[str, Any]]:
        """获取地区树形结构"""
        # 获取所有地区
        result = await self.db.execute(
            select(YozuanRegion).where(
                YozuanRegion.status == 1
            ).order_by(YozuanRegion.sort_order, YozuanRegion.region_code)
        )
        regions = result.scalars().all()
        
        # 构建树形结构
        region_dict = {r.region_code: r for r in regions}
        tree = []
        
        for region in regions:
            if region.parent_code is None:
                tree.append(self._build_tree_node(region, region_dict))
        
        return tree
    
    def _build_tree_node(self, region: YozuanRegion, region_dict: Dict[str, YozuanRegion]) -> Dict[str, Any]:
        """构建树形节点"""
        node = {
            "region_code": region.region_code,
            "region_name": region.region_name,
            "region_level": region.region_level,
            "full_name": region.full_name,
            "sort_order": region.sort_order,
            "children": []
        }
        
        # 查找子地区
        for code, r in region_dict.items():
            if r.parent_code == region.region_code:
                child_node = self._build_tree_node(r, region_dict)
                node["children"].append(child_node)
        
        # 按排序和编码排序
        node["children"].sort(key=lambda x: (x["sort_order"], x["region_code"]))
        
        return node


class TaskRegionDao:
    """任务地区关联DAO"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task_regions(self, task_id: int, regions: List[Dict[str, str]]) -> List[YozuanTaskRegion]:
        """创建任务地区关联"""
        task_regions = []
        for region in regions:
            task_region = YozuanTaskRegion(
                task_id=task_id,
                region_code=region["region_code"],
                region_level=region["region_level"]
            )
            task_regions.append(task_region)
        
        self.db.add_all(task_regions)
        await self.db.commit()
        
        # 刷新获取ID
        for tr in task_regions:
            await self.db.refresh(tr)
        
        return task_regions
    
    async def get_task_regions(self, task_id: int) -> List[YozuanTaskRegion]:
        """获取任务的地区关联"""
        result = await self.db.execute(
            select(YozuanTaskRegion).where(
                YozuanTaskRegion.task_id == task_id
            ).order_by(YozuanTaskRegion.region_code)
        )
        return result.scalars().all()
    
    async def get_task_regions_with_info(self, task_id: int) -> List[Dict[str, Any]]:
        """获取任务的地区关联（包含地区信息）"""
        result = await self.db.execute(
            select(YozuanTaskRegion, YozuanRegion).join(
                YozuanRegion, YozuanTaskRegion.region_code == YozuanRegion.region_code
            ).where(
                and_(
                    YozuanTaskRegion.task_id == task_id,
                    YozuanRegion.status == 1
                )
            ).order_by(YozuanTaskRegion.region_code)
        )
        
        regions = []
        for tr, region in result:
            regions.append({
                "id": tr.id,
                "region_code": tr.region_code,
                "region_level": tr.region_level,
                "region_name": region.region_name,
                "full_name": region.full_name,
                "create_time": tr.create_time
            })
        
        return regions
    
    async def delete_task_regions(self, task_id: int) -> bool:
        """删除任务的所有地区关联"""
        result = await self.db.execute(
            delete(YozuanTaskRegion).where(
                YozuanTaskRegion.task_id == task_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_tasks_by_region(self, region_code: str, region_level: str = None) -> List[int]:
        """根据地区获取任务ID列表"""
        query = select(YozuanTaskRegion.task_id).where(
            YozuanTaskRegion.region_code == region_code
        )
        
        if region_level:
            query = query.where(YozuanTaskRegion.region_level == region_level)
        
        result = await self.db.execute(query)
        return [row[0] for row in result.fetchall()]
    
    async def get_tasks_by_regions(self, region_codes: List[str]) -> List[int]:
        """根据多个地区编码获取任务ID列表"""
        if not region_codes:
            return []
        
        result = await self.db.execute(
            select(YozuanTaskRegion.task_id).where(
                YozuanTaskRegion.region_code.in_(region_codes)
            )
        )
        return result.scalars().all()
    
    async def get_region_statistics(self) -> Dict[str, Any]:
        """获取地区统计信息"""
        # 统计各级别地区数量
        level_stats = await self.db.execute(
            select(
                YozuanRegion.region_level,
                func.count(YozuanRegion.region_code).label('count')
            ).where(
                YozuanRegion.status == 1
            ).group_by(YozuanRegion.region_level)
        )
        
        # 统计任务地区分布
        task_region_stats = await self.db.execute(
            select(
                YozuanTaskRegion.region_level,
                func.count(YozuanTaskRegion.task_id).label('task_count')
            ).group_by(YozuanTaskRegion.region_level)
        )
        
        level_count = {row.region_level: row.count for row in level_stats}
        task_count = {row.region_level: row.task_count for row in task_region_stats}
        
        return {
            "level_statistics": level_count,
            "task_distribution": task_count
        }
