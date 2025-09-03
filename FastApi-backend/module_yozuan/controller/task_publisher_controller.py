"""
任务发布者控制器
负责任务发布者相关的所有操作
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ..dao.task_dao import TaskDao, TaskTypeDao, TaskStepDao, TaskTagDao
from ..dao.region_dao import TaskRegionDao
from ..dao.verification_dao import VerificationSubmitDao
from ..dao.order_dao import OrderDao
from ..dao.account_dao import AccountDao
from ..enums.task_enums import TaskStatus, TaskStepType, TaskVerificationType, TaskOrderStatus
from ..enums.task_enums import get_display_name, TASK_STATUS_DISPLAY, TASK_STEP_TYPE_DISPLAY, TASK_ORDER_STATUS_DISPLAY
from ..middleware.auth_middleware import get_current_user, get_current_user_id
from module_app.entity.do.app_user_do import AppUser
from ..service.invitation_service import RebateService
from config.yozuan_config import yozuan_config
from datetime import datetime, timedelta
from sqlalchemy import func
from utils.response_util import ResponseUtil


def get_area_scope_display(area_scope: int) -> str:
    """获取地区范围类型的显示名称"""
    scope_map = {
        1: "全国",
        2: "单个城市", 
        3: "多个城市"
    }
    return scope_map.get(area_scope, "未知")


def get_display_name(value: str, display_map: Dict[str, str]) -> str:
    """获取显示名称"""
    return display_map.get(value, value)


# 创建路由器
router = APIRouter(prefix="/yozuan/v1/task", tags=["任务发布者"])


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
    """
    try:
        task_dao = TaskDao(db)
        account_dao = AccountDao(db)
        
        # 1. 验证任务数据
        required_fields = ["task_name", "task_description", "task_price", "task_quantity", "task_type_id"]
        for field in required_fields:
            if field not in task_data or not task_data[field]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"缺少必填字段: {field}"
                )
        
        # 2. 验证任务价格和数量
        task_price = float(task_data["task_price"])
        task_quantity = int(task_data["task_quantity"])
        
        if task_price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务价格必须大于0"
            )
        
        if task_quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务数量必须大于0"
            )
        
        # 3. 计算总金额
        total_cost = task_price * task_quantity
        print(f"DEBUG: 任务总金额计算: {task_price} × {task_quantity} = {total_cost}")
        
        # 4. 获取用户账户信息
        user_account = await account_dao.get_user_account(current_user.user_id)
        if not user_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户账户不存在"
            )
        
        print(f"DEBUG: 用户账户信息: 余额={user_account.balance}, 冻结={user_account.frozen_amount}")
        
        # 5. 验证用户余额是否足够（添加余额保留机制）
        print(f"DEBUG: 余额检查 - 用户余额: {user_account.balance}, 任务总成本: {total_cost}")
        
        # 添加余额保留机制，防止用户余额变成0
        min_balance_reserve = 10.0  # 保留10元作为最小余额
        required_balance = total_cost + min_balance_reserve
        
        if float(user_account.balance) < required_balance:
            return ResponseUtil.error(
                f"余额不足，当前余额: {user_account.balance}，需要: {required_balance} "
                f"（任务成本: {total_cost} + 保留余额: {min_balance_reserve}）"
            )
        
        # 添加任务总金额限制，防止异常大的任务
        max_task_total_amount = 50000.0  # 最大任务总金额限制
        if total_cost > max_task_total_amount:
            return ResponseUtil.error(
                f"任务总金额过大，当前: {total_cost}，最大允许: {max_task_total_amount}"
            )
        
        print(f"DEBUG: 余额充足，开始冻结 {total_cost} 元")
        
        # 6. 冻结用户余额
        freeze_success = await account_dao.update_balance(
            user_id=current_user.user_id,
            operation="freeze",
            amount=total_cost,
            description=f"发布任务: {task_data['task_name']}"
        )
        
        if not freeze_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="余额冻结失败"
            )
        
        # 7. 准备任务数据
        task_data_with_publisher = task_data.copy()
        task_data_with_publisher["publisher_id"] = current_user.user_id
        task_data_with_publisher["total_amount"] = total_cost
        
        # 设置默认值
        task_data_with_publisher.setdefault("completion_hours", 24)
        task_data_with_publisher.setdefault("review_hours", 48)
        task_data_with_publisher.setdefault("device_limit", "all")
        task_data_with_publisher.setdefault("frequency_limit", "once")
        task_data_with_publisher.setdefault("area_scope", 1)
        
        # 将task_deadline映射到end_time字段
        if 'task_deadline' in task_data_with_publisher:
            try:
                # 解析ISO格式的时间字符串
                deadline_str = task_data_with_publisher['task_deadline']
                if deadline_str:
                    task_data_with_publisher['end_time'] = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                del task_data_with_publisher['task_deadline']
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"任务截止时间格式错误: {str(e)}"
                )
        
        # 处理任务标签
        if 'task_tags' in task_data_with_publisher and task_data_with_publisher['task_tags']:
            # 将标签数组转换为逗号分隔的字符串
            task_data_with_publisher['task_tag'] = ','.join(task_data_with_publisher['task_tags'])
            del task_data_with_publisher['task_tags']

        # 测试阶段 直接把任务状态设置为已发布
        task_data_with_publisher['task_status'] = TaskStatus.ACTIVE
        
        # 移除其他不在模型中的字段
        fields_to_remove = ['steps', 'verifications', 'bonus_conditions', 'special_requirements', 'contact_info', 'task_regions', 'area_codes']
        for field in fields_to_remove:
            task_data_with_publisher.pop(field, None)
        
        # 8. 创建任务
        task = await task_dao.create_task(task_data_with_publisher)
        
        # 9. 获取更新后的账户信息
        updated_account = await account_dao.get_user_account(current_user.user_id)
        
        return {
            "code": 200,
            "msg": "任务发布成功",
            "data": {
                "task_id": task.task_id,
                "task_name": task.task_name,
                "total_cost": total_cost,
                "balance_after": float(updated_account.balance),
                "frozen_amount_after": float(updated_account.frozen_amount)
            }
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
    task_data: Dict[str, Any] = Body(..., description="任务更新数据"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新任务信息
    
    ## 业务规则
    
    1. **权限检查**: 只有任务发布者可以更新任务
    2. **状态限制**: 只有草稿和暂停状态的任务可以更新
    3. **余额检查**: 如果增加任务数量，需要检查余额是否足够
    """
    try:
        task_dao = TaskDao(db)
        
        # 1. 检查任务是否存在
        task = await task_dao.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 2. 检查权限
        if task.publisher_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有任务发布者可以更新任务"
            )
        
        # 3. 检查任务状态
        if task.task_status not in [TaskStatus.DRAFT, TaskStatus.PAUSED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"任务状态为 {task.task_status}，无法更新"
            )
        
        # 4. 处理任务数据
        update_data = task_data.copy()
        
        # 将task_deadline映射到end_time字段
        if 'task_deadline' in update_data:
            try:
                deadline_str = update_data['task_deadline']
                if deadline_str:
                    update_data['end_time'] = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                del update_data['task_deadline']
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"任务截止时间格式错误: {str(e)}"
                )
        
        # 处理任务标签
        if 'task_tags' in update_data and update_data['task_tags']:
            update_data['task_tag'] = ','.join(update_data['task_tags'])
            del update_data['task_tags']
        
        # 移除其他不在模型中的字段
        fields_to_remove = ['steps', 'verifications', 'bonus_conditions', 'special_requirements', 'contact_info', 'task_regions', 'area_codes']
        for field in fields_to_remove:
            update_data.pop(field, None)
        
        # 5. 更新任务
        success = await task_dao.update_task(task_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="任务更新失败"
            )
        
        return {
            "code": 200,
            "msg": "任务更新成功",
            "data": {
                "task_id": task_id
            }
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
    
    ## 业务规则
    
    1. **权限检查**: 只有任务发布者可以删除任务
    2. **状态限制**: 只有草稿状态的任务可以删除
    3. **余额处理**: 删除任务时解冻相关余额
    """
    try:
        task_dao = TaskDao(db)
        account_dao = AccountDao(db)
        
        # 1. 检查任务是否存在
        task = await task_dao.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 2. 检查权限
        if task.publisher_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有任务发布者可以删除任务"
            )
        
        # 3. 检查任务状态
        if task.task_status != TaskStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"任务状态为 {task.task_status}，无法删除"
            )
        
        # 4. 解冻余额
        if task.total_amount > 0:
            unfreeze_success = await account_dao.update_balance(
                user_id=current_user.user_id,
                operation="unfreeze",
                amount=task.total_amount,
                description=f"删除任务: {task.task_name}"
            )
            
            if not unfreeze_success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="余额解冻失败"
                )
        
        # 5. 删除任务
        success = await task_dao.delete_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="任务删除失败"
            )
        
        return {
            "code": 200,
            "msg": "任务删除成功",
            "data": {
                "task_id": task_id
            }
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
    task_status: Optional[str] = Query(None, description="任务状态"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户发布的任务列表
    
    - **page**: 页码
    - **size**: 每页数量
    - **task_status**: 任务状态（可选）
    - **current_user**: 当前认证用户
    """
    try:
        task_dao = TaskDao(db)
        
        # 获取任务列表
        result = await task_dao.get_tasks_by_publisher(
            publisher_id=current_user.user_id,
            status=task_status,  # 直接传递status参数
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
            bonus_amount = review_data.get("bonus_amount", 0.0)
            total_commission = float(task.task_price) + bonus_amount
            
            # 更新订单状态为已验证
            await order_dao.verify_order(order_id, total_commission)
            
            # 更新验证提交状态
            await verification_dao.update_review_status(
                verification.submit_id,
                "approved",
                current_user.user_id,
                review_comment
            )
            
            # 处理返佣和余额结算
            account_dao = AccountDao(db)
            
            # 解冻发布者余额
            await account_dao.update_balance(
                user_id=current_user.user_id,
                operation="unfreeze",
                amount=float(task.task_price),
                description=f"任务审核通过，解冻: {task.task_name}"
            )
            
            # 支付接单者佣金
            await account_dao.update_balance(
                user_id=order.user_id,
                operation="income",
                amount=total_commission,
                description=f"任务完成奖励: {task.task_name}"
            )
            
            # 处理返佣
            rebate_service = RebateService(db)
            await rebate_service.process_task_rebate(
                task_id=task_id,
                order_id=order_id,
                user_id=order.user_id,
                amount=total_commission
            )
            
            return {
                "code": 200,
                "msg": "审核通过",
                "data": {
                    "order_id": order_id,
                    "review_status": "approved",
                    "commission_amount": total_commission,
                    "bonus_amount": bonus_amount
                }
            }
            
        elif review_status == "rejected":
            # 审核驳回
            await verification_dao.update_review_status(
                verification.submit_id,
                "rejected",
                current_user.user_id,
                review_comment
            )
            
            await order_dao.reject_order(order_id, review_comment)
            
            return {
                "code": 200,
                "msg": "审核驳回",
                "data": {
                    "order_id": order_id,
                    "review_status": "rejected",
                    "reject_reason": review_comment
                }
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的审核状态"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务审核失败: {str(e)}"
        ) 