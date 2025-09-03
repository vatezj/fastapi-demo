"""
任务发布者控制器
负责任务发布者相关的所有操作
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ..dao.task_dao import TaskDao, TaskTypeDao, TaskStepDao, TaskTagDao
from ..dao.verification_dao import VerificationDao
from ..dao.order_dao import OrderDao
from ..dao.account_dao import AccountDao
from ..enums.task_enums import TaskStatus, TaskStepType, TaskVerificationType, TaskOrderStatus, TransactionType, TransactionStatus
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
                "step_type": "link",
                "step_title": "访问指定网站",
                "step_description": "请访问指定的网站并停留30秒",
                "step_url": "https://example.com",
                "step_required": True
            },
            {
                "step_order": 2,
                "step_type": "text",
                "step_title": "点击指定按钮",
                "step_description": "在页面上找到并点击指定的按钮",
                "step_target": "button.submit",
                "step_required": True
            }
        ],
        "verifications": [
            {
                "verification_title": "截图验证",
                "verification_type": "image",
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
    发布任务
    
    ## 业务规则
    
    1. **用户认证**: 需要登录用户
    2. **余额检查**: 检查用户余额是否足够支付任务总金额
    3. **余额冻结**: 发布任务时冻结相应金额
    4. **任务创建**: 创建任务记录
    5. **步骤创建**: 创建任务步骤
    6. **验证创建**: 创建验证要求
    7. **标签处理**: 处理任务标签
    8. **地区限制**: 处理地区限制
    """
    try:
        # 1. 验证必要字段
        required_fields = ["task_name", "task_price", "task_quantity", "task_type_id"]
        for field in required_fields:
            if field not in task_data:
                return ResponseUtil.error(f"缺少必要字段: {field}")
        
        # 2. 计算任务总金额
        task_price = float(task_data["task_price"])
        task_quantity = int(task_data["task_quantity"])
        total_cost = task_price * task_quantity
        
        print(f"DEBUG: 任务总金额计算: {task_price} * {task_quantity} = {total_cost}")
        print(f"DEBUG: task_price类型: {type(task_price)}, task_quantity类型: {type(task_quantity)}, total_cost类型: {type(total_cost)}")
        
        # 3. 获取用户账户信息
        account_dao = AccountDao(db)
        user_account = await account_dao.get_user_account(current_user.user_id)
        
        if not user_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户账户不存在"
            )
        
        print(f"DEBUG: 用户账户信息: 余额={user_account.balance}, 冻结={user_account.frozen_amount}")
        
        # 4. 验证用户余额是否足够（添加余额保留机制）
        print(f"DEBUG: 余额检查 - 用户余额: {user_account.balance}, 任务总成本: {total_cost}")
        
        # 添加余额保留机制，防止用户余额变成0
        min_balance_reserve = 10.0  # 保留10元作为最小余额
        print(f"DEBUG: min_balance_reserve={min_balance_reserve}, type={type(min_balance_reserve)}")
        print(f"DEBUG: total_cost={total_cost}, type={type(total_cost)}")
        
        required_balance = total_cost + min_balance_reserve
        print(f"DEBUG: required_balance={required_balance}, type={type(required_balance)}")
        
        user_balance_float = float(user_account.balance)
        print(f"DEBUG: user_account.balance={user_account.balance}, type={type(user_account.balance)}")
        print(f"DEBUG: user_balance_float={user_balance_float}, type={type(user_balance_float)}")
        
        if user_balance_float < required_balance:
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
        print(f"DEBUG: 准备调用update_account_balance")
        print(f"DEBUG: user_id={current_user.user_id}")
        print(f"DEBUG: amount=-total_cost={-total_cost}, type={type(-total_cost)}")
        print(f"DEBUG: transaction_type={TransactionType.TASK_FREEZE.value}")
        
        # 5. 冻结用户余额并创建交易记录
        freeze_success = await account_dao.update_account_balance(
            user_id=current_user.user_id,
            amount=-total_cost,  # 负数表示扣除
            transaction_type=TransactionType.TASK_FREEZE.value,
            description=f"发布任务冻结资金: {task_data['task_name']}",
            related_id=0  # 任务ID稍后更新
        )
        
        if not freeze_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="余额冻结失败"
            )
        
        # 6. 准备任务数据
        task_data_with_publisher = task_data.copy()
        task_data_with_publisher["publisher_id"] = current_user.user_id
        task_data_with_publisher["total_amount"] = total_cost
        
        # 计算服务费（默认5%）
        service_fee_rate = 0.05  # 5%服务费
        service_fee = round(total_cost * service_fee_rate, 2)
        task_data_with_publisher["service_fee"] = service_fee
        
        # 设置默认值
        task_data_with_publisher.setdefault("completion_hours", 24)
        task_data_with_publisher.setdefault("task_status", TaskStatus.DRAFT)
        task_data_with_publisher.setdefault("area_scope", 1)
        task_data_with_publisher.setdefault("device_limit", "any")
        task_data_with_publisher.setdefault("frequency_limit", "unlimited")
        task_data_with_publisher.setdefault("review_hours", 72)  # 添加审核时限默认值
        
        # 将task_deadline映射到end_time字段
        if 'task_deadline' in task_data_with_publisher:
            try:
                # 解析ISO格式的时间字符串
                deadline_str = task_data_with_publisher['task_deadline']
                if isinstance(deadline_str, str):
                    task_data_with_publisher['end_time'] = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                del task_data_with_publisher['task_deadline']
            except ValueError as e:
                return ResponseUtil.error(f"任务截止时间格式错误: {str(e)}")
        
        # 过滤无效字段，只保留YozuanTask实体的有效字段
        valid_task_fields = {
            'publisher_id', 'task_type_id', 'task_name', 'task_description', 
            'task_quantity', 'completed_quantity', 'task_price', 'total_amount', 
            'service_fee', 'task_tag', 'completion_hours', 'review_hours',
            'device_limit', 'area_scope', 'single_area_code', 'frequency_limit', 
            'task_status', 'start_time', 'end_time', 'create_time', 'update_time'
        }
        
        # 创建过滤后的任务数据
        filtered_task_data = {k: v for k, v in task_data_with_publisher.items() if k in valid_task_fields}
        
        # 7. 创建任务
        task_dao = TaskDao(db)
        task = await task_dao.create_task(filtered_task_data)
        
        if not task:
            # 如果任务创建失败，解冻余额并创建交易记录
            await account_dao.update_account_balance(
                user_id=current_user.user_id,
                amount=total_cost,  # 正数表示增加
                transaction_type=TransactionType.TASK_UNFREEZE.value,
                description=f"任务创建失败，解冻资金: {task_data['task_name']}",
                related_id=0
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="任务创建失败"
            )
        
        # 7.1. 更新冻结交易记录中的任务ID
        try:
            # 获取最新的冻结交易记录并更新related_id
            await account_dao.update_transaction_related_id(
                user_id=current_user.user_id,
                transaction_type=TransactionType.TASK_FREEZE.value,
                related_id=task.task_id
            )
        except Exception as e:
            print(f"WARNING: 更新交易记录任务ID失败: {str(e)}")
            # 不影响主流程，继续执行
        
        # 8. 创建任务步骤
        if "steps" in task_data and task_data["steps"]:
            task_step_dao = TaskStepDao(db)
            await task_step_dao.create_task_steps(task.task_id, task_data["steps"])
        
        # 9. 创建任务验证要求
        if "verifications" in task_data and task_data["verifications"]:
            verification_dao = VerificationDao(db)
            await verification_dao.create_task_verifications(task.task_id, task_data["verifications"])
        
        # 10. 创建任务标签（标签直接存储在任务表的task_tag字段中）
        if "task_tags" in task_data and task_data["task_tags"]:
            # 将标签列表转换为逗号分隔的字符串
            task_tags_str = ",".join(task_data["task_tags"])
            # 更新任务的task_tag字段
            await task_dao.update_task(task.task_id, {"task_tag": task_tags_str})
        
        # 11. 创建地区限制
        if task_data.get("area_scope") in [2, 3]:
            if task_data["area_scope"] == 2 and "single_area_code" in task_data:
                await task_dao.create_task_city_relations(task.task_id, [task_data["single_area_code"]])
            elif task_data["area_scope"] == 3 and "area_codes" in task_data:
                await task_dao.create_task_city_relations(task.task_id, task_data["area_codes"])
        
        # 12. 返回成功响应
        return ResponseUtil.success(
            msg="任务发布成功",
            data={
                "task_id": task.task_id,
                "task_name": task.task_name,
                "total_amount": total_cost,
                "service_fee": service_fee,
                "frozen_amount": total_cost,
                "remaining_balance": float(user_account.balance) - total_cost,
                "next_step": "任务已创建，等待审核"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # 如果出现异常，尝试解冻余额并创建交易记录
        try:
            if 'total_cost' in locals() and 'current_user' in locals():
                await account_dao.update_account_balance(
                    user_id=current_user.user_id,
                    amount=total_cost,  # 正数表示增加
                    transaction_type=TransactionType.TASK_UNFREEZE.value,
                    description=f"任务发布异常，解冻资金",
                    related_id=0
                )
        except:
            pass
        
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
    2. **状态检查**: 只有草稿状态的任务可以更新
    3. **余额检查**: 如果任务金额有变化，需要重新计算余额
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
                detail="无权限更新此任务"
            )
        
        # 3. 检查任务状态
        if task.task_status != TaskStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"任务状态为 {task.task_status}，无法更新"
            )
        
        # 4. 计算新的任务总金额
        new_task_price = float(task_data.get("task_price", task.task_price))
        new_task_quantity = int(task_data.get("task_quantity", task.task_quantity))
        new_total_cost = new_task_price * new_task_quantity
        
        # 5. 如果金额有变化，处理余额
        if new_total_cost != task.total_amount:
            amount_diff = new_total_cost - task.total_amount
            
            if amount_diff > 0:
                # 需要额外冻结金额
                user_account = await account_dao.get_user_account(current_user.user_id)
                if float(user_account.balance) < amount_diff:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"余额不足，需要额外冻结 {amount_diff} 元"
                    )
                
                await account_dao.update_account_balance(
                    user_id=current_user.user_id,
                    amount=-amount_diff,  # 负数表示扣除
                    transaction_type=TransactionType.TASK_FREEZE.value,
                    description=f"更新任务增加冻结资金: {task.task_name}",
                    related_id=task_id
                )
            else:
                # 解冻多余金额
                await account_dao.update_account_balance(
                    user_id=current_user.user_id,
                    amount=abs(amount_diff),  # 正数表示增加
                    transaction_type=TransactionType.TASK_UNFREEZE.value,
                    description=f"更新任务减少冻结资金: {task.task_name}",
                    related_id=task_id
                )
        
        # 6. 更新任务数据
        update_data = task_data.copy()
        update_data["total_amount"] = new_total_cost
        
        # 计算新的服务费
        service_fee_rate = 0.05
        service_fee = round(new_total_cost * service_fee_rate, 2)
        update_data["service_fee"] = service_fee
        
        success = await task_dao.update_task(task_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="任务更新失败"
            )
        
        return ResponseUtil.success(
            msg="任务更新成功",
            data={
                "task_id": task_id,
                "total_amount": new_total_cost,
                "service_fee": service_fee
            }
        )
        
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
    2. **状态检查**: 只有草稿状态的任务可以删除
    3. **余额解冻**: 删除任务时解冻相应金额
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
                detail="无权限删除此任务"
            )
        
        # 3. 检查任务状态
        if task.task_status != TaskStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"任务状态为 {task.task_status}，无法删除"
            )
        
        # 4. 解冻余额并创建交易记录
        if task.total_amount > 0:
            unfreeze_success = await account_dao.update_account_balance(
                user_id=current_user.user_id,
                amount=float(task.total_amount),  # 正数表示增加
                transaction_type=TransactionType.TASK_UNFREEZE.value,
                description=f"删除任务解冻资金: {task.task_name}",
                related_id=task_id
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
        
        return ResponseUtil.success(
            msg="任务删除成功",
            data={
                "task_id": task_id,
                "unfrozen_amount": task.total_amount
            }
        )
        
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
    
    ## 业务规则
    
    1. **权限检查**: 只返回当前用户发布的任务
    2. **状态筛选**: 支持按任务状态筛选
    3. **分页查询**: 支持分页查询
    """
    try:
        task_dao = TaskDao(db)
        
        # 获取用户发布的任务
        result = await task_dao.get_tasks_by_publisher(
            publisher_id=current_user.user_id,
            status=task_status,
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
                "total_amount": float(task.total_amount),
                "service_fee": float(task.service_fee),
                "task_status": task.task_status,
                "task_status_display": get_display_name(task.task_status, TASK_STATUS_DISPLAY),
                "area_scope": task.area_scope,
                "area_scope_display": get_area_scope_display(task.area_scope),
                "completion_hours": task.completion_hours,
                "create_time": task.create_time.isoformat() if task.create_time else None,
                "update_time": task.update_time.isoformat() if task.update_time else None
            })
        
        return ResponseUtil.success(
            msg="获取成功",
            data={
                "tasks": tasks_data,
                "pagination": result["pagination"]
            }
        )
        
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
        "review_result": "approved",  # approved/rejected
        "review_comment": "任务完成质量良好，符合要求",
        "commission_amount": 10.50
    }),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    审核任务完成情况
    
    ## 业务规则
    
    1. **权限检查**: 只有任务发布者可以审核
    2. **订单状态检查**: 订单必须是已完成状态
    3. **审核结果处理**: 根据审核结果处理佣金和余额
    """
    try:
        task_dao = TaskDao(db)
        order_dao = OrderDao(db)
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
                detail="无权限审核此任务"
            )
        
        # 3. 检查订单是否存在
        order = await order_dao.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 4. 检查订单状态
        if order.order_status != TaskOrderStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"订单状态为 {order.order_status}，无法审核"
            )
        
        # 5. 处理审核结果
        review_result = review_data.get("review_result")
        review_comment = review_data.get("review_comment", "")
        commission_amount = float(review_data.get("commission_amount", task.task_price))
        
        if review_result == "approved":
            # 审核通过
            await order_dao.verify_order(order_id, review_comment)
            
            # 解冻发布者余额并创建交易记录
            await account_dao.update_account_balance(
                user_id=current_user.user_id,
                amount=float(task.task_price),  # 正数表示增加
                transaction_type=TransactionType.TASK_UNFREEZE.value,
                description=f"任务审核通过，解冻资金: {task.task_name}",
                related_id=task_id
            )
            
            # 支付接单者佣金并创建交易记录
            await account_dao.update_account_balance(
                user_id=order.user_id,
                amount=commission_amount,  # 正数表示增加
                transaction_type=TransactionType.TASK_COMMISSION.value,
                description=f"完成任务获得佣金: {task.task_name}",
                related_id=task_id
            )
            
            # 更新任务完成数量
            await task_dao.increment_completed_quantity(task_id)
            
            return ResponseUtil.success(
                msg="审核通过",
                data={
                    "order_id": order_id,
                    "commission_amount": commission_amount,
                    "next_step": "任务已完成，佣金已发放"
                }
            )
            
        elif review_result == "rejected":
            # 审核拒绝
            await order_dao.reject_order(order_id, review_comment)
            
            # 解冻发布者余额并创建交易记录
            await account_dao.update_account_balance(
                user_id=current_user.user_id,
                amount=float(task.task_price),  # 正数表示增加
                transaction_type=TransactionType.TASK_UNFREEZE.value,
                description=f"任务审核拒绝，解冻资金: {task.task_name}",
                related_id=task_id
            )
            
            return ResponseUtil.success(
                msg="审核拒绝",
                data={
                    "order_id": order_id,
                    "reject_reason": review_comment,
                    "next_step": "任务被拒绝，余额已解冻"
                }
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的审核结果"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"审核失败: {str(e)}"
        )

