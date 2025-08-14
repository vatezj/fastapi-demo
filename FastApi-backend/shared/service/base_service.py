# -*- coding: utf-8 -*-
"""
基础服务类
所有服务的基类
"""

from typing import Generic, TypeVar, List, Optional, Any, Dict
from shared.dao.base_dao import BaseDAO
from shared.entity.base.base_do import BaseDO
from shared.entity.base.base_vo import BaseVO

T = TypeVar('T', bound=BaseDO)
V = TypeVar('V', bound=BaseVO)

class BaseService(Generic[T, V]):
    """基础服务类"""
    
    def __init__(self, dao: BaseDAO[T]):
        self.dao = dao
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """根据ID获取实体"""
        return await self.dao.get_by_id(id)
    
    async def get_all(self) -> List[T]:
        """获取所有实体"""
        return await self.dao.get_all()
    
    async def get_by_condition(self, **kwargs) -> List[T]:
        """根据条件查询实体"""
        return await self.dao.get_by_condition(**kwargs)
    
    async def get_one_by_condition(self, **kwargs) -> Optional[T]:
        """根据条件查询单个实体"""
        return await self.dao.get_one_by_condition(**kwargs)
    
    async def create(self, entity: T) -> T:
        """创建实体"""
        return await self.dao.create(entity)
    
    async def create_batch(self, entities: List[T]) -> List[T]:
        """批量创建实体"""
        return await self.dao.create_batch(entities)
    
    async def update(self, id: int, update_data: Dict[str, Any]) -> Optional[T]:
        """更新实体"""
        return await self.dao.update(id, update_data)
    
    async def update_by_condition(self, condition: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """根据条件更新实体"""
        return await self.dao.update_by_condition(condition, update_data)
    
    async def delete(self, id: int) -> bool:
        """逻辑删除实体"""
        return await self.dao.delete(id)
    
    async def delete_by_condition(self, **kwargs) -> int:
        """根据条件逻辑删除实体"""
        return await self.dao.delete_by_condition(**kwargs)
    
    async def hard_delete(self, id: int) -> bool:
        """物理删除实体"""
        return await self.dao.hard_delete(id)
    
    async def count(self, **kwargs) -> int:
        """统计实体数量"""
        return await self.dao.count(**kwargs)
    
    async def exists(self, **kwargs) -> bool:
        """检查实体是否存在"""
        return await self.dao.exists(**kwargs)
    
    async def get_page(self, page: int = 1, size: int = 20, **kwargs) -> tuple[List[T], int]:
        """分页查询"""
        return await self.dao.get_page(page, size, **kwargs)
    
    def convert_to_vo(self, entity: T, vo_class: type[V]) -> V:
        """将DO转换为VO"""
        return vo_class.from_orm(entity)
    
    def convert_to_vo_list(self, entities: List[T], vo_class: type[V]) -> List[V]:
        """将DO列表转换为VO列表"""
        return [self.convert_to_vo(entity, vo_class) for entity in entities] 