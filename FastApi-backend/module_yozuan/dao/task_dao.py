"""
任务相关数据访问对象
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from ..entity.do.task_do import YozuanTask, YozuanTaskType, YozuanTaskStep, YozuanTaskTag, YozuanTaskCityRel
from ..enums.task_enums import TaskStatus


class TaskDao:
    """任务数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task(self, task_data: Dict[str, Any]) -> YozuanTask:
        """创建任务"""
        task = YozuanTask(**task_data)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def create_task_city_relations(self, task_id: int, area_codes: List[str]) -> List[YozuanTaskCityRel]:
        """创建任务城市关联"""
        if not area_codes:
            return []
        
        task_cities = []
        for area_code in area_codes:
            task_city = YozuanTaskCityRel(
                task_id=task_id,
                area_code=area_code
            )
            task_cities.append(task_city)
        
        self.db.add_all(task_cities)
        await self.db.commit()
        
        # 刷新获取ID
        for tc in task_cities:
            await self.db.refresh(tc)
        
        return task_cities
    
    async def get_task_cities(self, task_id: int) -> List[str]:
        """获取任务关联的城市编码列表"""
        result = await self.db.execute(
            select(YozuanTaskCityRel.area_code).where(
                YozuanTaskCityRel.task_id == task_id
            ).order_by(YozuanTaskCityRel.area_code)
        )
        return [row[0] for row in result.fetchall()]
    
    async def delete_task_cities(self, task_id: int) -> bool:
        """删除任务的所有城市关联"""
        result = await self.db.execute(
            delete(YozuanTaskCityRel).where(
                YozuanTaskCityRel.task_id == task_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_task_by_id(self, task_id: int) -> Optional[YozuanTask]:
        """根据ID获取任务"""
        query = select(YozuanTask).where(YozuanTask.task_id == task_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_task_with_details(self, task_id: int) -> Optional[Dict[str, Any]]:
        """获取任务详情，包含步骤和验证信息"""
        # 获取任务基本信息
        task_query = select(YozuanTask).where(YozuanTask.task_id == task_id)
        task_result = await self.db.execute(task_query)
        task = task_result.scalar_one_or_none()
        
        if not task:
            return None
        
        # 获取任务步骤
        steps_query = select(YozuanTaskStep).where(
            YozuanTaskStep.task_id == task_id
        ).order_by(YozuanTaskStep.step_order)
        steps_result = await self.db.execute(steps_query)
        steps = steps_result.scalars().all()
        
        # 获取任务类型信息
        type_query = select(YozuanTaskType).where(YozuanTaskType.type_id == task.task_type_id)
        type_result = await self.db.execute(type_query)
        task_type = type_result.scalar_one_or_none()
        
        return {
            "task": task,
            "steps": steps,
            "task_type": task_type
        }
    
    async def get_tasks_by_publisher(self, publisher_id: int, status: Optional[str] = None, 
                                   page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取发布者的任务列表"""
        query = select(YozuanTask).where(YozuanTask.publisher_id == publisher_id)
        
        if status:
            query = query.where(YozuanTask.task_status == status)
        
        # 计算总数
        count_query = select(func.count(YozuanTask.task_id)).where(
            YozuanTask.publisher_id == publisher_id
        )
        if status:
            count_query = count_query.where(YozuanTask.task_status == status)
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # 分页查询
        query = query.order_by(YozuanTask.create_time.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        tasks = result.scalars().all()
        
        return {
            "tasks": tasks,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    async def get_available_tasks(self, user_id: int, filters: Dict[str, Any] = None,
                                page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取可用的任务列表（排除用户已接单的任务）"""
        # 基础查询：状态为active的任务
        query = select(YozuanTask).where(YozuanTask.task_status == TaskStatus.ACTIVE)
        
        # 应用过滤条件
        if filters:
            if filters.get("task_type_id"):
                query = query.where(YozuanTask.task_type_id == filters["task_type_id"])
            if filters.get("device_limit") and filters["device_limit"] != "all":
                query = query.where(YozuanTask.device_limit.in_([filters["device_limit"], "all"]))
            if filters.get("min_price"):
                query = query.where(YozuanTask.task_price >= filters["min_price"])
            if filters.get("max_price"):
                query = query.where(YozuanTask.task_price <= filters["max_price"])
            if filters.get("tag"):
                query = query.where(YozuanTask.task_tag == filters["tag"])
        
        # 计算总数
        count_query = select(func.count(YozuanTask.task_id)).where(
            YozuanTask.task_status == TaskStatus.ACTIVE
        )
        if filters:
            if filters.get("task_type_id"):
                count_query = count_query.where(YozuanTask.task_type_id == filters["task_type_id"])
            if filters.get("device_limit") and filters["device_limit"] != "all":
                count_query = count_query.where(YozuanTask.device_limit.in_([filters["device_limit"], "all"]))
            if filters.get("min_price"):
                count_query = count_query.where(YozuanTask.task_price >= filters["min_price"])
            if filters.get("max_price"):
                count_query = count_query.where(YozuanTask.task_price <= filters["max_price"])
            if filters.get("tag"):
                count_query = count_query.where(YozuanTask.task_tag == filters["tag"])
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # 分页查询
        query = query.order_by(YozuanTask.create_time.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        tasks = result.scalars().all()
        
        return {
            "tasks": tasks,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    async def update_task(self, task_id: int, update_data: Dict[str, Any]) -> bool:
        """更新任务"""
        query = update(YozuanTask).where(YozuanTask.task_id == task_id).values(**update_data)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        query = delete(YozuanTask).where(YozuanTask.task_id == task_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def update_task_status(self, task_id: int, status: str) -> bool:
        """更新任务状态"""
        return await self.update_task(task_id, {"task_status": status})
    
    async def increment_completed_quantity(self, task_id: int) -> bool:
        """增加任务完成数量"""
        query = update(YozuanTask).where(
            YozuanTask.task_id == task_id
        ).values(
            completed_quantity=YozuanTask.completed_quantity + 1
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0


class TaskTypeDao:
    """任务类型数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_task_types(self) -> List[YozuanTaskType]:
        """获取所有任务类型"""
        query = select(YozuanTaskType).where(YozuanTaskType.status == 1).order_by(YozuanTaskType.sort_order)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_task_type_by_id(self, type_id: int) -> Optional[YozuanTaskType]:
        """根据ID获取任务类型"""
        query = select(YozuanTaskType).where(YozuanTaskType.type_id == type_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_task_type_by_code(self, type_code: str) -> Optional[YozuanTaskType]:
        """根据代码获取任务类型"""
        query = select(YozuanTaskType).where(YozuanTaskType.type_code == type_code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class TaskStepDao:
    """任务步骤数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task_steps(self, task_id: int, steps_data: List[Dict[str, Any]]) -> List[YozuanTaskStep]:
        """创建任务步骤"""
        steps = []
        for step_data in steps_data:
            step_data["task_id"] = task_id
            step = YozuanTaskStep(**step_data)
            steps.append(step)
        
        self.db.add_all(steps)
        await self.db.commit()
        
        # 刷新获取ID
        for step in steps:
            await self.db.refresh(step)
        
        return steps
    
    async def get_task_steps(self, task_id: int) -> List[YozuanTaskStep]:
        """获取任务步骤"""
        query = select(YozuanTaskStep).where(
            YozuanTaskStep.task_id == task_id
        ).order_by(YozuanTaskStep.step_order)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_task_steps(self, task_id: int, steps_data: List[Dict[str, Any]]) -> List[YozuanTaskStep]:
        """更新任务步骤（先删除旧的，再创建新的）"""
        # 删除旧的步骤
        delete_query = delete(YozuanTaskStep).where(YozuanTaskStep.task_id == task_id)
        await self.db.execute(delete_query)
        
        # 创建新的步骤
        return await self.create_task_steps(task_id, steps_data)
    
    async def delete_task_steps(self, task_id: int) -> bool:
        """删除任务步骤"""
        query = delete(YozuanTaskStep).where(YozuanTaskStep.task_id == task_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0


class TaskTagDao:
    """任务标签数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_tags(self) -> List[YozuanTaskTag]:
        """获取所有标签"""
        query = select(YozuanTaskTag).where(YozuanTaskTag.status == 1).order_by(YozuanTaskTag.tag_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_tags_by_category(self, category: str) -> List[YozuanTaskTag]:
        """根据分类获取标签"""
        query = select(YozuanTaskTag).where(
            and_(YozuanTaskTag.tag_category == category, YozuanTaskTag.status == 1)
        ).order_by(YozuanTaskTag.tag_id)
        result = await self.db.execute(query)
        return result.scalars().all()
