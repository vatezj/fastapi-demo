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


def get_area_scope_display(area_scope: int) -> str:
    """获取地区范围类型的显示名称"""
    scope_map = {
        1: "全国",
        2: "单个城市", 
        3: "多个城市"
    }
    return scope_map.get(area_scope, "未知")


def get_display_name(value: str, display_map: Dict[str, str]) -> str:
    """根据枚举值获取对应的显示名称"""
    return display_map.get(value, value)


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
                    "area_scope": task.area_scope,
                    "area_scope_display": get_area_scope_display(task.area_scope),
                    "single_area_code": task.single_area_code,
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
        "area_scope": 3,  # 1=全国，2=单个城市，3=多个城市
        "area_codes": ["440100", "440300"],  # 广州市、深圳市（仅当area_scope=3时使用）
        "single_area_code": "110100",  # 北京市（仅当area_scope=2时使用）
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
    发布任务接口
    
    ## 余额扣除说明
    
    发布任务时会自动扣除用户余额：
    1. **预冻结金额**：任务总金额 = 任务单价 × 任务数量
    2. **余额验证**：发布前会检查用户可用余额是否足够
    3. **冻结操作**：将相应金额从可用余额转移到冻结余额
    4. **交易记录**：自动创建冻结交易记录，便于用户查询
    
    ## 请求参数说明
    
    ### 基础信息（必填）
    - **task_name** (string): 任务名称，最大100字符
    - **task_description** (string): 任务详细描述
    - **task_price** (number): 任务单价，支持2位小数
    - **task_quantity** (integer): 任务总数量
    - **task_type_id** (integer): 任务类型ID
    
    ### 地区范围配置（必填）
    - **area_scope** (integer): 地区范围类型
        - `1` = 全国：任务覆盖全国所有地区
        - `2` = 单个城市：任务仅覆盖指定的单个城市
        - `3` = 多个城市：任务覆盖指定的多个城市
    
    #### 地区范围类型详细说明
    
    **1. 全国任务 (area_scope = 1)**
    ```json
    {
        "area_scope": 1
        // 无需其他地区相关字段
    }
    ```
    
    **2. 单个城市任务 (area_scope = 2)**
    ```json
    {
        "area_scope": 2,
        "single_area_code": "110100"  // 北京市编码
    }
    ```
    
    **3. 多个城市任务 (area_scope = 3)**
    ```json
    {
        "area_scope": 3,
        "area_codes": ["440100", "440300", "441900"]  // 广州、深圳、东莞
    }
    ```
    
    ### 城市编码说明
    城市编码采用国标行政区域代码（6位数字）：
    - **110100**：北京市
    - **310100**：上海市
    - **440100**：广州市
    - **440300**：深圳市
    - **441900**：东莞市
    
    ### 可选配置
    - **device_limit** (string): 设备限制，可选值：`all`/`android`/`ios`，默认 `all`
    - **frequency_limit** (string): 限制次数，可选值：`once`/`daily`/`thrice`，默认 `once`
    - **task_deadline** (string): 任务截止时间，ISO格式：`2024-12-31T23:59:59`
    - **task_tags** (array): 任务标签数组，如 `["测试", "简单"]`
    - **completion_hours** (integer): 完成时限（小时），默认24小时
    - **review_hours** (integer): 审核时限（小时），默认48小时
    
    ### 高级配置（可选）
    - **steps** (array): 任务步骤详情
    - **verifications** (array): 验证要求
    - **bonus_conditions** (array): 奖励条件
    - **special_requirements** (string): 特殊要求
    - **contact_info** (object): 联系方式
    
    ## 响应说明
    
    ### 成功响应
    ```json
    {
        "code": 200,
        "msg": "任务发布成功",
        "data": {
            "task_id": 123,
            "task_name": "测试任务名称",
            "total_cost": 1050.00,
            "balance_after": 950.00,
            "frozen_amount_after": 1050.00
        },
        "success": true
    }
    ```
    
    ### 错误响应
    ```json
    {
        "code": 400,
        "msg": "余额不足，当前余额: 500.00，需要: 1050.00",
        "success": false
    }
    ```
    
    ```json
    {
        "code": 400,
        "msg": "任务发布失败: 单个城市任务必须指定城市编码",
        "success": false
    }
    ```
    
    ## 使用示例
    
    ### 发布全国任务
    ```bash
    curl -X POST "http://127.0.0.1:9099/yozuan/v1/task/publish" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -d '{
        "task_name": "全国推广任务",
        "task_description": "面向全国用户的推广任务",
        "task_price": 10.00,
        "task_quantity": 1000,
        "task_type_id": 1,
        "area_scope": 1
    }'
    ```
    
    ### 发布单城市任务
    ```bash
    curl -X POST "http://127.0.0.1:9099/yozuan/v1/task/publish" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -d '{
        "task_name": "北京地区任务",
        "task_description": "仅限北京地区的任务",
        "task_price": 15.00,
        "task_quantity": 100,
        "task_type_id": 1,
        "area_scope": 2,
        "single_area_code": "110100"
    }'
    ```
    
    ### 发布多城市任务
    ```bash
    curl -X POST "http://127.0.0.1:9099/yozuan/v1/task/publish" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -d '{
        "task_name": "珠三角地区任务",
        "task_description": "覆盖广州、深圳、东莞等城市",
        "task_price": 12.00,
        "task_quantity": 500,
        "task_type_id": 1,
        "area_scope": 3,
        "area_codes": ["440100", "440300", "441900"]
    }'
    ```
    
    ## 注意事项
    
    1. **余额要求**：发布任务前请确保账户余额充足，系统会自动冻结任务总金额
    
    2. **地区范围类型必须与相关字段匹配**：
       - `area_scope=1`：无需地区相关字段
       - `area_scope=2`：必须提供 `single_area_code`
       - `area_scope=3`：必须提供 `area_codes` 数组
    
    3. **城市编码格式**：必须使用6位国标行政区域代码
    
    4. **数据验证**：系统会自动验证必填字段和字段格式
    
    5. **新的地区管理方式**：使用 `area_scope` + `single_area_code`/`area_codes` 替代旧的 `region_limit` 字段
    """
    try:
        # 1. 验证任务数据
        from utils.response_util import ResponseUtil
        
        required_fields = ["task_name", "task_description", "task_price", "task_quantity", "task_type_id"]
        for field in required_fields:
            if field not in task_data:
                return ResponseUtil.error(f"缺少必填字段: {field}")
        
        # 2. 验证任务价格
        task_price = float(task_data["task_price"])
        if task_price < yozuan_config.yozuan_task_min_price:
            return ResponseUtil.error(f"任务价格不能低于 {yozuan_config.yozuan_task_min_price}")
        if task_price > yozuan_config.yozuan_task_max_price:
            return ResponseUtil.error(f"任务价格不能高于 {yozuan_config.yozuan_task_max_price}")
        
        # 3. 验证任务步骤数量
        steps = task_data.get("steps", [])
        if len(steps) > yozuan_config.yozuan_task_max_steps:
            return ResponseUtil.error(f"任务步骤不能超过 {yozuan_config.yozuan_task_max_steps} 个")
        
        # 4. 验证验证要求数量
        verifications = task_data.get("verifications", [])
        if len(verifications) > yozuan_config.yozuan_task_max_verifications:
            return ResponseUtil.error(f"验证要求不能超过 {yozuan_config.yozuan_task_max_verifications} 个")
        
        # 5. 获取用户账户并计算任务总金额
        from ..dao.account_dao import AccountDao
        account_dao = AccountDao(db)
        user_account = await account_dao.get_or_create_user_account(current_user.user_id)
        
        # 计算任务总金额
        total_cost = task_price * task_data["task_quantity"]
        
        # 6. 准备任务数据，包含发布者ID
        task_data_with_publisher = task_data.copy()
        task_data_with_publisher['publisher_id'] = current_user.user_id
        
        # 设置任务总金额
        task_data_with_publisher['total_amount'] = total_cost
        
        # 计算平台手续费（假设为总金额的5%）
        service_fee_rate = 0.05  # 5%手续费率
        task_data_with_publisher['service_fee'] = round(task_data_with_publisher['total_amount'] * service_fee_rate, 2)
        
        # 设置默认的完成时限和审核时限
        task_data_with_publisher['completion_hours'] = task_data.get('completion_hours', 24)  # 默认24小时
        task_data_with_publisher['review_hours'] = task_data.get('review_hours', 48)  # 默认48小时
        
        # 处理地区范围类型
        area_scope = task_data.get('area_scope', 1)  # 默认全国
        task_data_with_publisher['area_scope'] = area_scope
        
        # 根据地区范围类型处理地区数据
        if area_scope == 1:  # 全国
            task_data_with_publisher['single_area_code'] = None
            
        elif area_scope == 2:  # 单个城市
            if 'single_area_code' not in task_data:
                return ResponseUtil.error("单个城市任务必须指定城市编码")
            task_data_with_publisher['single_area_code'] = task_data['single_area_code']
            
        elif area_scope == 3:  # 多个城市
            if 'area_codes' not in task_data or not task_data['area_codes']:
                return ResponseUtil.error("多个城市任务必须指定城市编码列表")
            task_data_with_publisher['single_area_code'] = None
        
        # 将task_deadline映射到end_time字段
        if 'task_deadline' in task_data_with_publisher:
            from datetime import datetime
            try:
                # 解析ISO格式的时间字符串
                deadline = datetime.fromisoformat(task_data_with_publisher['task_deadline'])
                task_data_with_publisher['end_time'] = deadline
                # 移除task_deadline字段，避免模型验证错误
                del task_data_with_publisher['task_deadline']
            except ValueError as e:
                return ResponseUtil.error(f"任务截止时间格式错误: {str(e)}")
        
        # 将task_tags映射到task_tag字段
        if 'task_tags' in task_data_with_publisher:
            # 将标签数组转换为逗号分隔的字符串
            task_data_with_publisher['task_tag'] = ','.join(task_data_with_publisher['task_tags'])
            del task_data_with_publisher['task_tags']
        
        # 移除其他不在模型中的字段
        fields_to_remove = ['steps', 'verifications', 'bonus_conditions', 'special_requirements', 'contact_info', 'task_regions', 'area_codes']
        for field in fields_to_remove:
            if field in task_data_with_publisher:
                del task_data_with_publisher[field]
        
        # 6. 验证用户余额是否足够
        print(f"DEBUG: 余额检查 - 用户余额: {user_account.balance}, 任务总成本: {total_cost}")
        if float(user_account.balance) < total_cost:
            return ResponseUtil.error(f"余额不足，当前余额: {user_account.balance}，需要: {total_cost}")
        
        print(f"DEBUG: 余额充足，开始冻结 {total_cost} 元")
        
        task_dao = TaskDao(db)
        task = await task_dao.create_task(task_data_with_publisher)
        
        # 7. 处理任务城市关联（仅多城市任务）
        if area_scope == 3 and 'area_codes' in task_data:
            await task_dao.create_task_city_relations(task.task_id, task_data['area_codes'])
        
        # 8. 冻结用户余额
        print(f"DEBUG: 开始冻结余额: {total_cost}")
        await account_dao.update_balance(
            current_user.user_id, total_cost, "freeze"
        )
        print(f"DEBUG: 余额冻结完成")
        
        # 9. 创建冻结交易记录
        await account_dao.create_transaction(
            account_id=user_account.account_id,
            transaction_type="task_freeze",
            amount=total_cost,
            description=f"任务发布冻结: {task.task_name}",
            related_id=task.task_id
        )
        
        # 10. 重新查询冻结后的账户余额
        await db.flush()
        updated_account = await account_dao.get_user_account(current_user.user_id)
        
        print(f"DEBUG: 冻结后余额查询结果:")
        print(f"  - 可用余额: {updated_account.balance}")
        print(f"  - 冻结余额: {updated_account.frozen_amount}")
        print(f"  - 任务总成本: {total_cost}")
        
        return {
            "code": 200,
            "msg": "任务发布成功",
            "data": {
                "task_id": task.task_id,
                "task_name": task.task_name,
                "total_cost": total_cost,
                "balance_after": float(updated_account.balance),
                "frozen_amount_after": float(updated_account.frozen_amount)
            },
            "success": True
        }
        
    except Exception as e:
        return ResponseUtil.error(f"任务发布失败: {str(e)}")


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
        "area_scope": 3,  # 更新为多城市任务
        "area_codes": ["440100", "440300"],  # 广州、深圳
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
    - **task_name** (string, 可选): 任务名称，最大100字符
    - **task_description** (string, 可选): 任务详细描述
    - **task_price** (float, 可选): 单个任务价格，支持2位小数
    - **task_quantity** (integer, 可选): 任务数量
    - **task_type_id** (integer, 可选): 任务类型ID
    
    ### 地区范围配置 (可选)
    - **area_scope** (integer, 可选): 地区范围类型
        - `1` = 全国：任务覆盖全国所有地区
        - `2` = 单个城市：任务仅覆盖指定的单个城市
        - `3` = 多个城市：任务覆盖指定的多个城市
    
    #### 地区范围类型更新说明
    
    **更新为全国任务 (area_scope = 1)**
    ```json
    {
        "area_scope": 1
        // 系统会自动清除single_area_code和城市关联
    }
    ```
    
    **更新为单个城市任务 (area_scope = 2)**
    ```json
    {
        "area_scope": 2,
        "single_area_code": "110100"  // 必须提供城市编码
    }
    ```
    
    **更新为多个城市任务 (area_scope = 3)**
    ```json
    {
        "area_scope": 3,
        "area_codes": ["440100", "440300"]  // 必须提供城市编码数组
    }
    ```
    
    ### 城市编码说明
    城市编码采用国标行政区域代码（6位数字）：
    - **110100**：北京市
    - **310100**：上海市
    - **440100**：广州市
    - **440300**：深圳市
    - **441900**：东莞市
    
    ### 其他配置 (可选)
    - **device_limit** (string, 可选): 设备限制，可选值：`all`/`android`/`ios`
    - **frequency_limit** (string, 可选): 限制次数，可选值：`once`/`daily`/`thrice`
    - **task_deadline** (string, 可选): 任务截止时间，ISO格式：`2024-12-31T23:59:59`
    - **task_tags** (array, 可选): 任务标签数组
    - **completion_hours** (integer, 可选): 完成时限（小时）
    - **review_hours** (integer, 可选): 审核时限（小时）
    
    ### 高级配置 (可选)
    - **steps** (array, 可选): 任务步骤详情
    - **verifications** (array, 可选): 验证要求
    - **bonus_conditions** (array, 可选): 奖励条件
    - **special_requirements** (string, 可选): 特殊要求
    - **contact_info** (object, 可选): 联系方式
    
    ## 响应说明
    
    ### 成功响应
    ```json
    {
        "code": 200,
        "msg": "任务更新成功",
        "data": {
            "task_id": 123,
            "task_name": "更新后的任务名称",
            "area_scope": 3,
            "area_scope_display": "多个城市"
        },
        "success": true
    }
    ```
    
    ### 错误响应
    ```json
    {
        "code": 400,
        "msg": "任务更新失败: 多个城市任务必须指定城市编码列表",
        "success": false
    }
    ```
    
    ## 使用示例
    
    ### 更新任务基本信息
    ```bash
    curl -X PUT "http://127.0.0.1:9099/yozuan/v1/task/123/update" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -d '{
        "task_name": "更新后的任务名称",
        "task_price": 20.00
    }'
    ```
    
    ### 更新任务地区范围
    ```bash
    curl -X PUT "http://127.0.0.1:9099/yozuan/v1/task/123/update" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -d '{
        "area_scope": 2,
        "single_area_code": "310100"
    }'
    ```
    
    ## 注意事项
    
    1. **部分更新**：只需提供要更新的字段，其他字段保持不变
    
    2. **地区范围更新**：更新 `area_scope` 时，系统会自动处理相关字段：
       - 清除旧的地区关联
       - 设置新的地区配置
    
    3. **数据验证**：系统会验证更新后的数据格式和一致性
    
    4. **权限检查**：只能更新自己发布的任务
    
    5. **新的地区管理方式**：使用 `area_scope` + `single_area_code`/`area_codes` 替代旧的 `region_limit` 字段
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
        # 如果更新了价格或数量，需要重新计算总金额和手续费
        if 'task_price' in task_data or 'task_quantity' in task_data:
            # 获取当前任务信息来计算新的总金额
            current_task = await task_dao.get_task_by_id(task_id)
            if current_task:
                new_price = float(task_data.get('task_price', current_task.task_price))
                new_quantity = int(task_data.get('task_quantity', current_task.task_quantity))
                
                # 计算新的总金额
                task_data['total_amount'] = new_price * new_quantity
                
                # 计算新的平台手续费（假设为总金额的5%）
                service_fee_rate = 0.05  # 5%手续费率
                task_data['service_fee'] = round(task_data['total_amount'] * service_fee_rate, 2)
        
        # 处理地区范围类型更新
        if 'area_scope' in task_data:
            area_scope = task_data['area_scope']
            
            if area_scope == 1:  # 全国
                task_data['single_area_code'] = None
                
            elif area_scope == 2:  # 单个城市
                if 'single_area_code' not in task_data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="单个城市任务必须指定城市编码"
                    )
                
            elif area_scope == 3:  # 多个城市
                if 'area_codes' not in task_data or not task_data['area_codes']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="多个城市任务必须指定城市编码列表"
                    )
                task_data['single_area_code'] = None
        
        # 将task_deadline映射到end_time字段
        if 'task_deadline' in task_data:
            from datetime import datetime
            try:
                # 解析ISO格式的时间字符串
                deadline = datetime.fromisoformat(task_data['task_deadline'])
                task_data['end_time'] = deadline
                # 移除task_deadline字段，避免模型验证错误
                del task_data['task_deadline']
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"任务截止时间格式错误: {str(e)}"
                )
        
        # 移除其他不在模型中的字段
        fields_to_remove = ['steps', 'verifications', 'bonus_conditions', 'special_requirements', 'contact_info', 'task_regions', 'area_codes']
        for field in fields_to_remove:
            if field in task_data:
                del task_data[field]
        
        updated_task = await task_dao.update_task(task_id, task_data)
        
        # 如果更新了地区范围类型，需要更新城市关联
        if 'area_scope' in task_data:
            # 删除旧的城市关联
            await task_dao.delete_task_cities(task_id)
            
            # 创建新的城市关联（仅多城市任务）
            if task_data['area_scope'] == 3 and 'area_codes' in task_data:
                await task_dao.create_task_city_relations(task_id, task_data['area_codes'])
        
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
        await account_dao.update_balance(
            current_user.user_id, total_cost, "unfreeze"
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
            total_payment = float(task.task_price) + review_data.get("bonus_amount", 0.0)
            
            # 解冻发布者余额
            await account_dao.update_balance(
                current_user.user_id, total_payment, "unfreeze"
            )
            
            # 支付接单者
            await account_dao.transfer_commission(
                current_user.user_id, order.user_id, total_payment, task_id, order_id
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
            await account_dao.update_balance(
                current_user.user_id, float(task.task_price), "unfreeze"
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
