"""
任务管理控制器
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ..dao.task_dao import TaskDao, TaskTypeDao, TaskStepDao, TaskTagDao
from ..dao.region_dao import TaskRegionDao
from ..dao.verification_dao import VerificationSubmitDao
from ..enums.task_enums import TaskStatus, TaskStepType, TaskVerificationType
from ..enums.task_enums import get_display_name, TASK_STATUS_DISPLAY, TASK_STEP_TYPE_DISPLAY
from ..middleware.auth_middleware import get_current_user, get_current_user_id
from module_app.entity.do.app_user_do import AppUser
from ..service.invitation_service import RebateService
from config.yozuan_config import yozuan_config

router = APIRouter()


@router.get("/types", summary="获取任务类型列表")
async def get_task_types(db: AsyncSession = Depends(get_db)):
    """获取所有可用的任务类型"""
    try:
        task_type_dao = TaskTypeDao(db)
        types = await task_type_dao.get_all_task_types()
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": [
                {
                    "type_id": t.type_id,
                    "type_name": t.type_name,
                    "type_code": t.type_code,
                    "min_price": float(t.min_price),
                    "min_quantity": t.min_quantity,
                    "icon_url": t.icon_url,
                    "description": t.description,
                    "sort_order": t.sort_order
                }
                for t in types
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务类型失败: {str(e)}")


@router.get("/tags", summary="获取任务标签列表")
async def get_task_tags(
    category: Optional[str] = Query(None, description="标签分类"),
    db: AsyncSession = Depends(get_db)
):
    """获取任务标签列表"""
    try:
        tag_dao = TaskTagDao(db)
        if category:
            tags = await tag_dao.get_tags_by_category(category)
        else:
            tags = await tag_dao.get_all_tags()
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": [
                {
                    "tag_id": t.tag_id,
                    "tag_name": t.tag_name,
                    "tag_code": t.tag_code,
                    "tag_category": t.tag_category,
                    "description": t.description
                }
                for t in tags
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务标签失败: {str(e)}")


@router.get("/", summary="获取任务列表")
async def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    task_type_id: Optional[int] = Query(None, description="任务类型ID"),
    device_limit: Optional[str] = Query(None, description="设备限制"),
    min_price: Optional[float] = Query(None, description="最小价格"),
    max_price: Optional[float] = Query(None, description="最大价格"),
    tag: Optional[str] = Query(None, description="任务标签"),
    db: AsyncSession = Depends(get_db)
):
    """获取可用的任务列表"""
    try:
        task_dao = TaskDao(db)
        
        # 构建过滤条件
        filters = {}
        if task_type_id:
            filters["task_type_id"] = task_type_id
        if device_limit:
            filters["device_limit"] = device_limit
        if min_price is not None:
            filters["min_price"] = min_price
        if max_price is not None:
            filters["max_price"] = max_price
        if tag:
            filters["tag"] = tag
        
        # 获取任务列表
        result = await task_dao.get_available_tasks(
            user_id=0,  # TODO: 从当前用户获取
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
                "task_tag": task.task_tag,
                "completion_hours": task.completion_hours,
                "device_limit": task.device_limit,
                "frequency_limit": task.frequency_limit,
                "task_status": task.task_status,
                "status_display": get_display_name(task.task_status, TASK_STATUS_DISPLAY),
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
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.get("/{task_id}", summary="获取任务详情")
async def get_task_detail(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取任务详情，包含步骤和验证信息"""
    try:
        task_dao = TaskDao(db)
        task_detail = await task_dao.get_task_with_details(task_id)
        
        if not task_detail:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task = task_detail["task"]
        steps = task_detail["steps"]
        task_type = task_detail["task_type"]
        
        # 格式化步骤数据
        steps_data = []
        for step in steps:
            steps_data.append({
                "step_id": step.step_id,
                "step_order": step.step_order,
                "step_title": step.step_title,
                "step_description": step.step_description,
                "step_type": step.step_type,
                "step_type_display": get_display_name(step.step_type, TASK_STEP_TYPE_DISPLAY),
                "step_content": step.step_content,
                "is_required": bool(step.is_required)
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "task": {
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "task_description": task.task_description,
                    "task_price": float(task.task_price),
                    "task_quantity": task.task_quantity,
                    "completed_quantity": task.completed_quantity,
                    "service_fee": float(task.service_fee),
                    "task_tag": task.task_tag,
                    "completion_hours": task.completion_hours,
                    "review_hours": task.review_hours,
                    "device_limit": task.device_limit,
                    "region_limit": task.region_limit,
                    "frequency_limit": task.frequency_limit,
                    "task_status": task.task_status,
                    "status_display": get_display_name(task.task_status, TASK_STATUS_DISPLAY),
                    "start_time": task.start_time.isoformat() if task.start_time else None,
                    "end_time": task.end_time.isoformat() if task.end_time else None,
                    "create_time": task.create_time.isoformat() if task.create_time else None
                },
                "task_type": {
                    "type_id": task_type.type_id,
                    "type_name": task_type.type_name,
                    "type_code": task_type.type_code,
                    "icon_url": task_type.icon_url,
                    "description": task_type.description
                } if task_type else None,
                "steps": steps_data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务详情失败: {str(e)}")


@router.get("/status/options", summary="获取任务状态选项")
async def get_task_status_options():
    """获取任务状态选项，用于前端下拉框"""
    from ..enums.task_enums import get_enum_choices, TaskStatus, TASK_STATUS_DISPLAY
    
    return {
        "code": 200,
        "msg": "获取成功",
        "data": get_enum_choices(TaskStatus, TASK_STATUS_DISPLAY)
    }


@router.get("/step-types/options", summary="获取步骤类型选项")
async def get_step_type_options():
    """获取步骤类型选项，用于前端下拉框"""
    from ..enums.task_enums import get_enum_choices, TaskStepType, TASK_STEP_TYPE_DISPLAY
    
    return {
        "code": 200,
        "msg": "获取成功",
        "data": get_enum_choices(TaskStepType, TASK_STEP_TYPE_DISPLAY)
    }


@router.get("/verification-types/options", summary="获取验证类型选项")
async def get_verification_type_options():
    """获取验证类型选项，用于前端下拉框"""
    from ..enums.task_enums import get_enum_choices, TaskVerificationType, TASK_VERIFICATION_TYPE_DISPLAY
    
    return {
        "code": 200,
        "msg": "获取成功",
        "data": get_enum_choices(TaskVerificationType, TASK_VERIFICATION_TYPE_DISPLAY)
    }


# ==================== 任务发布接口 ====================

@router.post("/publish", summary="发布任务", tags=["任务发布"])
async def publish_task(
    task_data: Dict[str, Any] = Body(..., description="任务数据", example={
        "task_name": "测试任务名称",
        "task_description": "这是一个测试任务的详细描述",
        "task_price": 10.50,
        "task_quantity": 100,
        "task_type_id": 1,
        "device_limit": "mobile",
        "frequency_limit": "once_per_day",
        "task_deadline": "2024-12-31T23:59:59",
            "task_regions": [
        {"region_code": "000000", "level": "country"},
        {"region_code": "11", "level": "province"},
        {"region_code": "110101", "level": "county"}
    ],
    "task_tags": ["测试", "简单"],
        "steps": [
            {
                "step_order": 1,
                "step_type": "visit",
                "step_title": "访问指定网站",
                "step_description": "请访问指定的网站并停留30秒",
                "step_url": "https://example.com",
                "step_duration": 30,
                "step_required": True
            },
            {
                "step_order": 2,
                "step_type": "click",
                "step_title": "点击指定按钮",
                "step_description": "在页面上找到并点击指定的按钮",
                "step_target": "button.submit",
                "step_required": True
            }
        ],
        "verifications": [
            {
                "verification_title": "截图验证",
                "verification_type": "screenshot",
                "verification_description": "请截图显示任务完成状态",
                "image_required": True,
                "text_required": False,
                "text_placeholder": ""
            },
            {
                "verification_title": "文字描述",
                "verification_type": "text",
                "verification_description": "请描述任务完成过程",
                "image_required": False,
                "text_required": True,
                "text_placeholder": "请详细描述您是如何完成任务的..."
            }
        ],
        "bonus_conditions": [
            {
                "condition_type": "time_bonus",
                "condition_value": "within_1_hour",
                "bonus_amount": 2.00,
                "description": "1小时内完成可获得额外奖励"
            }
        ],
        "special_requirements": "需要真实用户操作，禁止使用自动化工具",
        "contact_info": {
            "qq": "123456789",
            "wechat": "test_wechat",
            "phone": "13800138000"
        }
    }),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    发布新任务
    
    ## 请求参数说明
    
    ### 基本信息 (必填)
    - **task_name** (string, 必填): 任务名称，长度1-100字符
    - **task_description** (string, 必填): 任务详细描述，长度10-2000字符
    - **task_price** (float, 必填): 单个任务价格，范围0.01-10000元
    - **task_quantity** (integer, 必填): 任务数量，范围1-10000
    - **task_type_id** (integer, 必填): 任务类型ID，参考 `/types` 接口
    
    ### 任务限制 (可选)
    - **device_limit** (string, 可选): 设备限制，可选值：`mobile`(手机), `pc`(电脑), `both`(不限)
    - **frequency_limit** (string, 可选): 频率限制，可选值：`once`(一次), `once_per_day`(每日一次), `once_per_week`(每周一次), `unlimited`(不限)
    - **task_deadline** (string, 可选): 任务截止时间，ISO 8601格式，如：`2024-12-31T23:59:59`
    - **task_regions** (array, 可选): 任务地区数组，每个地区包含：
        - **region_code** (string, 必填): 地区编码，如：`000000`(全国)、`11`(北京)、`110101`(东城区)
        - **level** (string, 必填): 地区级别，可选值：`country`(国家)、`province`(省)、`city`(市)、`county`(县)
    - **task_tags** (array, 可选): 任务标签数组，如：`["测试", "简单", "赚钱"]`
    
    ### 任务步骤 (可选，最多10个)
    - **steps** (array, 可选): 任务步骤数组，每个步骤包含：
        - **step_order** (integer, 必填): 步骤顺序，从1开始
        - **step_type** (string, 必填): 步骤类型，可选值：`visit`(访问), `click`(点击), `input`(输入), `scroll`(滚动), `wait`(等待), `custom`(自定义)
        - **step_title** (string, 必填): 步骤标题，长度1-100字符
        - **step_description** (string, 必填): 步骤描述，长度1-500字符
        - **step_url** (string, 可选): 目标URL，当step_type为visit时必填
        - **step_target** (string, 可选): 目标元素选择器，当step_type为click时必填
        - **step_duration** (integer, 可选): 持续时间(秒)，当step_type为wait时必填
        - **step_required** (boolean, 必填): 是否必填步骤，默认true
    
    ### 验证要求 (可选，最多5个)
    - **verifications** (array, 可选): 验证要求数组，每个验证包含：
        - **verification_title** (string, 必填): 验证标题，长度1-100字符
        - **verification_type** (string, 必填): 验证类型，可选值：`screenshot`(截图), `text`(文字), `file`(文件), `url`(链接), `custom`(自定义)
        - **verification_description** (string, 必填): 验证描述，长度1-500字符
        - **image_required** (boolean, 必填): 是否要求上传图片
        - **text_required** (boolean, 必填): 是否要求填写文字
        - **text_placeholder** (string, 可选): 文字输入提示，当text_required为true时建议填写
        - **file_types** (array, 可选): 允许的文件类型，当verification_type为file时使用，如：`["jpg", "png", "pdf"]`
        - **max_file_size** (integer, 可选): 最大文件大小(MB)，当verification_type为file时使用
    
    ### 奖励条件 (可选)
    - **bonus_conditions** (array, 可选): 额外奖励条件数组，每个条件包含：
        - **condition_type** (string, 必填): 条件类型，可选值：`time_bonus`(时间奖励), `quality_bonus`(质量奖励), `quantity_bonus`(数量奖励)
        - **condition_value** (string, 必填): 条件值，如：`within_1_hour`、`high_quality`、`over_10_tasks`
        - **bonus_amount** (float, 必填): 奖励金额
        - **description** (string, 必填): 条件描述
    
    ### 特殊要求 (可选)
    - **special_requirements** (string, 可选): 特殊要求说明，长度1-1000字符
    - **contact_info** (object, 可选): 联系方式，包含：
        - **qq** (string, 可选): QQ号码
        - **wechat** (string, 可选): 微信号
        - **phone** (string, 可选): 手机号码
        - **email** (string, 可选): 邮箱地址
    
    ## 业务规则
    
    1. **余额检查**: 发布任务前会检查用户余额是否足够支付 `task_price × task_quantity`
    2. **余额冻结**: 任务发布成功后，相应金额会被冻结，直到任务完成或取消
    3. **数据验证**: 所有必填字段都会被验证，不符合要求的数据会被拒绝
    4. **返佣说明**: 返佣在任务完成并通过审核后处理，不在发布时处理
    
    ## 响应说明
    
    - **code**: 200表示成功
    - **msg**: 响应消息
    - **data**: 包含task_id、task_name、total_cost和rebate_info
    - **success**: 操作是否成功
    
    ## 错误码说明
    
    - **400**: 请求参数错误（缺少必填字段、价格超出范围、步骤/验证数量超限等）
    - **401**: 用户未认证
    - **403**: 用户被禁用
    - **500**: 服务器内部错误
    """
    try:
        # 1. 验证任务数据
        required_fields = ["task_name", "task_description", "task_price", "task_quantity", "task_type_id"]
        for field in required_fields:
            if field not in task_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"缺少必填字段: {field}"
                )
        
        # 2. 验证任务价格
        task_price = float(task_data["task_price"])
        if task_price < yozuan_config.yozuan_task_min_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"任务价格不能低于 {yozuan_config.yozuan_task_min_price}"
            )
        if task_price > yozuan_config.yozuan_task_max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"任务价格不能高于 {yozuan_config.yozuan_task_max_price}"
            )
        
        # 3. 验证任务步骤数量
        steps = task_data.get("steps", [])
        if len(steps) > yozuan_config.yozuan_task_max_steps:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"任务步骤不能超过 {yozuan_config.yozuan_task_max_steps} 个"
            )
        
        # 4. 验证验证要求数量
        verifications = task_data.get("verifications", [])
        if len(verifications) > yozuan_config.yozuan_task_max_verifications:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"验证要求不能超过 {yozuan_config.yozuan_task_max_verifications} 个"
            )
        
        # 5. 检查用户余额是否足够
        from ..dao.account_dao import AccountDao
        user_account = await AccountDao.get_user_account(db, current_user.user_id)
        if not user_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户账户不存在"
            )
        
        total_cost = task_price * task_data["task_quantity"]
        if user_account.balance < total_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账户余额不足，无法发布任务"
            )
        
        # 6. 创建任务
        task_dao = TaskDao(db)
        task = await task_dao.create_task(
            publisher_id=current_user.user_id,
            task_data=task_data
        )
        
        # 7. 处理任务地区关联
        if "task_regions" in task_data and task_data["task_regions"]:
            task_region_dao = TaskRegionDao(db)
            await task_region_dao.create_task_regions(task.task_id, task_data["task_regions"])
        
        # 7. 冻结用户余额
        await AccountDao.update_balance(
            db, current_user.user_id, total_cost, "freeze"
        )
        
        return {
            "code": 200,
            "msg": "任务发布成功",
            "data": {
                "task_id": task.task_id,
                "task_name": task.task_name,
                "total_cost": total_cost
            },
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务发布失败: {str(e)}"
        )


@router.put("/{task_id}/update", summary="更新任务", tags=["任务管理"])
async def update_task(
    task_id: int,
    task_data: Dict[str, Any] = Body(..., description="任务更新数据", example={
        "task_name": "更新后的任务名称",
        "task_description": "更新后的任务描述",
        "task_price": 15.00,
        "task_quantity": 50,
        "device_limit": "both",
        "frequency_limit": "once_per_week",
        "task_deadline": "2024-12-31T23:59:59",
        "task_region": "全国",
        "task_tags": ["更新", "简单"],
        "steps": [
            {
                "step_order": 1,
                "step_type": "visit",
                "step_title": "访问更新后的网站",
                "step_description": "请访问更新后的网站并停留45秒",
                "step_url": "https://updated-example.com",
                "step_duration": 45,
                "step_required": True
            }
        ],
        "verifications": [
            {
                "verification_title": "更新后的截图验证",
                "verification_type": "screenshot",
                "verification_description": "请截图显示任务完成状态",
                "image_required": True,
                "text_required": False
            }
        ],
        "special_requirements": "更新后的特殊要求说明",
        "contact_info": {
            "qq": "987654321",
            "wechat": "updated_wechat"
        }
    }),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新任务信息
    
    ## 路径参数
    
    - **task_id** (integer, 必填): 要更新的任务ID
    
    ## 请求参数说明
    
    ### 基本信息 (可选)
    - **task_name** (string, 可选): 任务名称，长度1-100字符
    - **task_description** (string, 可选): 任务详细描述，长度10-2000字符
    - **task_price** (float, 可选): 单个任务价格，范围0.01-10000元
    - **task_quantity** (integer, 可选): 任务数量，范围1-10000
    - **task_type_id** (integer, 可选): 任务类型ID，参考 `/types` 接口
    
    ### 任务限制 (可选)
    - **device_limit** (string, 可选): 设备限制，可选值：`mobile`(手机), `pc`(电脑), `both`(不限)
    - **frequency_limit** (string, 可选): 频率限制，可选值：`once`(一次), `once_per_day`(每日一次), `once_per_week`(每周一次), `unlimited`(不限)
    - **task_deadline** (string, 可选): 任务截止时间，ISO 8601格式
    - **task_region** (string, 可选): 任务地区限制
    - **task_tags** (array, 可选): 任务标签数组
    
    ### 任务步骤 (可选)
    - **steps** (array, 可选): 任务步骤数组，格式同发布任务接口
    - **verifications** (array, 可选): 验证要求数组，格式同发布任务接口
    - **bonus_conditions** (array, 可选): 奖励条件数组，格式同发布任务接口
    - **special_requirements** (string, 可选): 特殊要求说明
    - **contact_info** (object, 可选): 联系方式
    
    ## 业务规则
    
    1. **权限检查**: 只有任务发布者可以更新任务
    2. **状态限制**: 只有草稿状态的任务可以更新
    3. **部分更新**: 支持部分字段更新，未提供的字段保持原值
    4. **数据验证**: 更新的数据会进行验证，不符合要求的数据会被拒绝
    
    ## 响应说明
    
    - **code**: 200表示成功
    - **msg**: 响应消息
    - **data**: 包含更新后的task_id、task_name和update_time
    - **success**: 操作是否成功
    
    ## 错误码说明
    
    - **400**: 请求参数错误或任务状态不允许更新
    - **401**: 用户未认证
    - **403**: 权限不足（非任务发布者）
    - **404**: 任务不存在
    - **500**: 服务器内部错误
    """
    try:
        # 1. 检查任务是否存在
        task_dao = TaskDao(db)
        existing_task = await task_dao.get_task_by_id(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 2. 检查权限（只有发布者可以更新）
        if existing_task.publisher_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有任务发布者可以更新任务"
            )
        
        # 3. 检查任务状态（只有草稿状态可以更新）
        if existing_task.task_status != "draft":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有草稿状态的任务可以更新"
            )
        
        # 4. 更新任务
        updated_task = await task_dao.update_task(task_id, task_data)
        
        return {
            "code": 200,
            "msg": "任务更新成功",
            "data": {
                "task_id": updated_task.task_id,
                "task_name": updated_task.task_name,
                "update_time": updated_task.update_time.isoformat() if updated_task.update_time else None
            },
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务更新失败: {str(e)}"
        )


@router.delete("/{task_id}", summary="删除任务", tags=["任务管理"])
async def delete_task(
    task_id: int,
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除任务
    
    - **task_id**: 任务ID
    - **current_user**: 当前认证用户
    """
    try:
        # 1. 检查任务是否存在
        task_dao = TaskDao(db)
        existing_task = await task_dao.get_task_by_id(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 2. 检查权限（只有发布者可以删除）
        if existing_task.publisher_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有任务发布者可以删除任务"
            )
        
        # 3. 检查任务状态（只有草稿状态可以删除）
        if existing_task.task_status != "draft":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有草稿状态的任务可以删除"
            )
        
        # 4. 删除任务
        await task_dao.delete_task(task_id)
        
        # 5. 解冻用户余额
        total_cost = float(existing_task.task_price) * existing_task.task_quantity
        from ..dao.account_dao import AccountDao
        await AccountDao.update_balance(
            db, current_user.user_id, total_cost, "unfreeze"
        )
        
        return {
            "code": 200,
            "msg": "任务删除成功",
            "data": {
                "task_id": task_id,
                "unfrozen_amount": total_cost
            },
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务删除失败: {str(e)}"
        )


@router.get("/my/published", summary="获取我发布的任务", tags=["任务管理"])
async def get_my_published_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="任务状态"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户发布的任务列表
    
    - **page**: 页码
    - **size**: 每页数量
    - **status**: 任务状态（可选）
    - **current_user**: 当前认证用户
    """
    try:
        task_dao = TaskDao(db)
        
        # 构建过滤条件
        filters = {"publisher_id": current_user.user_id}
        if status:
            filters["task_status"] = status
        
        # 获取任务列表
        result = await task_dao.get_tasks_by_publisher(
            publisher_id=current_user.user_id,
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
                "task_price": float(task.task_price),
                "task_quantity": task.task_quantity,
                "completed_quantity": task.completed_quantity,
                "task_status": task.task_status,
                "status_display": get_display_name(task.task_status, TASK_STATUS_DISPLAY),
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


# ==================== 任务审核接口 ====================

@router.post("/{task_id}/review", summary="审核任务完成", tags=["任务审核"])
async def review_task_completion(
    task_id: int,
    order_id: int,
    review_data: Dict[str, Any] = Body(..., description="审核数据", example={
        "review_status": "approved",
        "review_comment": "任务完成质量很好，通过审核",
        "bonus_amount": 2.00,
        "bonus_reason": "提前完成，质量优秀"
    }),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    审核任务完成情况
    
    ## 路径参数
    
    - **task_id** (integer, 必填): 任务ID
    - **order_id** (integer, 必填): 订单ID
    
    ## 请求参数说明
    
    - **review_status** (string, 必填): 审核状态，可选值：`approved`(通过), `rejected`(驳回)
    - **review_comment** (string, 可选): 审核意见
    - **bonus_amount** (float, 可选): 额外奖励金额
    - **bonus_reason** (string, 可选): 奖励原因
    
    ## 业务规则
    
    1. **权限检查**: 只有任务发布者可以审核任务
    2. **状态检查**: 只有待审核状态的任务可以审核
    3. **返佣处理**: 审核通过后自动处理返佣
    4. **余额更新**: 审核通过后解冻发布者余额并支付接单者
    """
    try:
        # 1. 检查任务是否存在
        task_dao = TaskDao(db)
        task = await task_dao.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 2. 检查权限（只有发布者可以审核）
        if task.publisher_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有任务发布者可以审核任务"
            )
        
        # 3. 检查订单是否存在
        from ..dao.order_dao import OrderDao
        order_dao = OrderDao(db)
        order = await order_dao.get_order_by_id(order_id)
        if not order or order.task_id != task_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在或与任务不匹配"
            )
        
        # 4. 检查订单状态
        if order.order_status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单状态不是已完成状态，无法审核"
            )
        
        # 5. 检查验证提交状态
        verification_dao = VerificationSubmitDao(db)
        verification = await verification_dao.get_by_order_id(order_id)
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到任务验证提交记录"
            )
        
        if verification.review_status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证提交已被审核，无法重复审核"
            )
        
        # 6. 执行审核
        review_status = review_data["review_status"]
        review_comment = review_data.get("review_comment", "")
        
        if review_status == "approved":
            # 审核通过
            await verification_dao.approve_verification(
                submit_id=verification.submit_id,
                review_user_id=current_user.user_id,
                review_comment=review_comment
            )
            
            # 更新订单状态为已完成
            await order_dao.update_order_status(order_id, "finished")
            
            # 处理返佣
            rebate_result = await RebateService.process_task_completion_rebate(
                db=db,
                task_id=task_id,
                order_id=order_id,
                task_amount=float(task.task_price),
                bonus_amount=review_data.get("bonus_amount", 0.0)
            )
            
            # 解冻发布者余额并支付接单者
            from ..dao.account_dao import AccountDao
            total_payment = float(task.task_price) + review_data.get("bonus_amount", 0.0)
            
            # 解冻发布者余额
            await AccountDao.update_balance(
                db, current_user.user_id, total_payment, "unfreeze"
            )
            
            # 支付接单者
            await AccountDao.transfer_commission(
                db, order.user_id, total_payment, order_id, "任务完成奖励"
            )
            
            msg = "任务审核通过，返佣处理完成"
        else:
            # 审核驳回
            await verification_dao.reject_verification(
                submit_id=verification.submit_id,
                review_user_id=current_user.user_id,
                review_comment=review_comment
            )
            
            # 更新订单状态为已驳回
            await order_dao.update_order_status(order_id, "rejected")
            
            # 解冻发布者余额（不支付接单者）
            from ..dao.account_dao import AccountDao
            await AccountDao.update_balance(
                db, current_user.user_id, float(task.task_price), "unfreeze"
            )
            
            msg = "任务审核驳回，余额已解冻"
        
        return {
            "code": 200,
            "msg": msg,
            "data": {
                "task_id": task_id,
                "order_id": order_id,
                "review_status": review_status,
                "review_comment": review_comment,
                "rebate_info": rebate_result.get("data", {}) if review_status == "approved" else None
            },
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务审核失败: {str(e)}"
        )
