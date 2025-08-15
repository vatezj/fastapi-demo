# -*- coding: utf-8 -*-
"""
基础数据访问对象
所有DAO的基类
"""

from typing import Generic, TypeVar, Type, List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from shared.entity.base.base_do import BaseDO

T = TypeVar('T', bound=BaseDO)

class BaseDAO(Generic[T]):
    """基础数据访问对象"""
    
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """根据ID获取实体"""
        result = await self.db.execute(
            select(self.model).where(
                and_(
                    self.model.user_id == id,
                    self.model.del_flag == '0'
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[T]:
        """获取所有实体（未删除的）"""
        result = await self.db.execute(
            select(self.model).where(self.model.del_flag == '0')
        )
        return result.scalars().all()
    
    async def get_by_condition(self, **kwargs) -> List[T]:
        """根据条件查询实体"""
        query = select(self.model).where(self.model.del_flag == '0')
        
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                if isinstance(value, (list, tuple)):
                    query = query.where(getattr(self.model, key).in_(value))
                else:
                    query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_one_by_condition(self, **kwargs) -> Optional[T]:
        """根据条件查询单个实体"""
        result = await self.get_by_condition(**kwargs)
        return result[0] if result else None
    
    async def create(self, entity: T) -> T:
        """创建实体"""
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity
    
    async def create_batch(self, entities: List[T]) -> List[T]:
        """批量创建实体"""
        self.db.add_all(entities)
        await self.db.commit()
        for entity in entities:
            await self.db.refresh(entity)
        return entities
    
    async def update(self, id: int, update_data: Dict[str, Any]) -> Optional[T]:
        """更新实体"""
        # 过滤掉None值
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(id)
        
        stmt = (
            update(self.model)
            .where(
                and_(
                    self.model.user_id == id,
                    self.model.del_flag == '0'
                )
            )
            .values(**update_data)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount > 0:
            return await self.get_by_id(id)
        return None
    
    async def update_by_condition(self, condition: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """根据条件更新实体"""
        # 过滤掉None值
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not update_data:
            return 0
        
        query = self.model.del_flag == '0'
        for key, value in condition.items():
            if hasattr(self.model, key) and value is not None:
                query = and_(query, getattr(self.model, key) == value)
        
        stmt = update(self.model).where(query).values(**update_data)
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    async def delete(self, id: int) -> bool:
        """逻辑删除实体"""
        stmt = (
            update(self.model)
            .where(
                and_(
                    self.model.user_id == id,
                    self.model.del_flag == '0'
                )
            )
            .values(del_flag='1')
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_by_condition(self, **kwargs) -> int:
        """根据条件逻辑删除实体"""
        query = self.model.del_flag == '0'
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                query = and_(query, getattr(self.model, key) == value)
        
        stmt = update(self.model).where(query).values(del_flag='1')
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    async def hard_delete(self, id: int) -> bool:
        """物理删除实体"""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def count(self, **kwargs) -> int:
        """统计实体数量"""
        query = select(func.count(self.model.user_id)).where(self.model.del_flag == '0')
        
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                if isinstance(value, (list, tuple)):
                    query = query.where(getattr(self.model, key).in_(value))
                else:
                    query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.scalar(query)
        return result or 0
    
    async def exists(self, **kwargs) -> bool:
        """检查实体是否存在"""
        return await self.count(**kwargs) > 0
    
    async def get_page(self, page: int = 1, size: int = 20, **kwargs) -> tuple[List[T], int]:
        """分页查询"""
        # 构建查询条件
        query = select(self.model).where(self.model.del_flag == '0')
        
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                if isinstance(value, (list, tuple)):
                    query = query.where(getattr(self.model, key).in_(value))
                else:
                    query = query.where(getattr(self.model, key) == value)
        
        # 获取总数
        count_query = select(func.count(self.model.id)).where(self.model.del_flag == '0')
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                if isinstance(value, (list, tuple)):
                    count_query = count_query.where(getattr(self.model, key).in_(value))
                else:
                    count_query = count_query.where(getattr(self.model, key) == value)
        
        total = await self.db.scalar(count_query) or 0
        
        # 分页查询
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return items, total 