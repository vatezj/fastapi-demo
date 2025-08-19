"""
账户管理控制器
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from ..dao.account_dao import AccountDao
from ..enums.task_enums import TransactionType, get_display_name, TRANSACTION_TYPE_DISPLAY
from ..middleware.auth_middleware import get_current_user
from module_app.entity.do.app_user_do import AppUser
from config.yozuan_config import yozuan_config

router = APIRouter()


@router.get("/", summary="获取账户信息")
async def get_account_info(
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的账户信息"""
    try:
        user_id = current_user.user_id
        
        account_dao = AccountDao(db)
        account = await account_dao.get_or_create_user_account(user_id)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "account_id": account.account_id,
                "user_id": account.user_id,
                "balance": float(account.balance),
                "frozen_amount": float(account.frozen_amount),
                "total_income": float(account.total_income),
                "total_withdraw": float(account.total_withdraw),
                "create_time": account.create_time.isoformat() if account.create_time else None,
                "update_time": account.update_time.isoformat() if account.update_time else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账户信息失败: {str(e)}")


@router.get("/transactions", summary="获取交易记录")
async def get_transactions(
    transaction_type: Optional[str] = Query(None, description="交易类型"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的交易记录"""
    try:
        user_id = current_user.user_id
        
        account_dao = AccountDao(db)
        result = await account_dao.get_transaction_history(
            user_id=user_id,
            transaction_type=transaction_type,
            page=page,
            size=size
        )
        
        # 格式化返回数据
        transactions_data = []
        for transaction in result["transactions"]:
            transactions_data.append({
                "transaction_id": transaction.transaction_id,
                "transaction_type": transaction.transaction_type,
                "type_display": get_display_name(transaction.transaction_type, TRANSACTION_TYPE_DISPLAY),
                "amount": float(transaction.amount),
                "balance_before": float(transaction.balance_before),
                "balance_after": float(transaction.balance_after),
                "description": transaction.description,
                "status": transaction.status,
                "related_id": transaction.related_id,
                "create_time": transaction.create_time.isoformat() if transaction.create_time else None
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "transactions": transactions_data,
                "pagination": {
                    "page": result["page"],
                    "size": result["size"],
                    "total": result["total"],
                    "pages": result["pages"]
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易记录失败: {str(e)}")


@router.get("/statistics", summary="获取账户统计")
async def get_account_statistics(
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的账户统计信息"""
    try:
        user_id = current_user.user_id
        
        account_dao = AccountDao(db)
        stats = await account_dao.get_account_statistics(user_id)
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "balance": stats["balance"],
                "frozen_amount": stats["frozen_amount"],
                "total_income": stats["total_income"],
                "total_withdraw": stats["total_withdraw"],
                "transaction_counts": stats["transaction_counts"],
                "calculated_income": stats["calculated_income"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账户统计失败: {str(e)}")


@router.get("/transaction-types/options", summary="获取交易类型选项")
async def get_transaction_type_options():
    """获取交易类型选项，用于前端下拉框"""
    from ..enums.task_enums import get_enum_choices, TransactionType, TRANSACTION_TYPE_DISPLAY
    
    return {
        "code": 200,
        "msg": "获取成功",
        "data": get_enum_choices(TransactionType, TransactionType, TRANSACTION_TYPE_DISPLAY)
    }


# ==================== 充值和提现接口 ====================

@router.post("/recharge", summary="账户充值", tags=["账户操作"])
async def recharge_account(
    recharge_data: Dict[str, Any] = Body(..., description="充值数据", example={
        "amount": 100.00,
        "payment_method": "alipay",
        "payment_channel": "web",
        "remark": "账户充值"
    }),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    账户充值
    
    ## 请求参数说明
    
    - **amount** (float, 必填): 充值金额，范围0.01-50000元
    - **payment_method** (string, 必填): 支付方式，可选值：`alipay`(支付宝), `wechat`(微信), `bank`(银行卡)
    - **payment_channel** (string, 必填): 支付渠道，可选值：`web`(网页), `app`(手机APP), `h5`(H5页面)
    - **remark** (string, 可选): 充值备注
    
    ## 业务规则
    
    1. **金额限制**: 单次充值金额不能超过50000元
    2. **支付方式**: 支持多种支付方式
    3. **交易记录**: 充值成功后记录交易流水
    4. **余额更新**: 充值成功后立即更新账户余额
    """
    try:
        amount = float(recharge_data["amount"])
        payment_method = recharge_data["payment_method"]
        payment_channel = recharge_data["payment_channel"]
        remark = recharge_data.get("remark", "账户充值")
        
        # 1. 验证充值金额
        if amount < 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="充值金额不能少于0.01元"
            )
        
        if amount > 50000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="单次充值金额不能超过50000元"
            )
        
        # 2. 验证支付方式
        valid_payment_methods = ["alipay", "wechat", "bank"]
        if payment_method not in valid_payment_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的支付方式"
            )
        
        # 3. 验证支付渠道
        valid_channels = ["web", "app", "h5"]
        if payment_channel not in valid_channels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的支付渠道"
            )
        
        # 4. 执行充值
        account_dao = AccountDao(db)
        
        # 获取或创建用户账户
        user_account = await account_dao.get_or_create_user_account(current_user.user_id)
        
        # 更新账户余额
        await account_dao.update_balance(
            db, current_user.user_id, amount, "add"
        )
        
        # 创建充值交易记录
        transaction = await account_dao.create_transaction(
            db=db,
            account_id=user_account.account_id,
            transaction_type="recharge",
            amount=amount,
            description=f"账户充值 - {remark}",
            related_id=0,  # 充值没有相关订单
            payment_method=payment_method,
            payment_channel=payment_channel
        )
        
        # 5. 获取更新后的账户信息
        updated_account = await account_dao.get_user_account(db, current_user.user_id)
        
        return {
            "code": 200,
            "msg": "充值成功",
            "data": {
                "transaction_id": transaction.transaction_id,
                "amount": amount,
                "payment_method": payment_method,
                "payment_channel": payment_channel,
                "new_balance": float(updated_account.balance),
                "total_income": float(updated_account.total_income),
                "remark": remark
            },
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"充值失败: {str(e)}"
        )


@router.post("/withdraw", summary="账户提现", tags=["账户操作"])
async def withdraw_account(
    withdraw_data: Dict[str, Any] = Body(..., description="提现数据", example={
        "amount": 50.00,
        "withdraw_method": "alipay",
        "withdraw_account": "13800138000",
        "real_name": "张三",
        "remark": "账户提现"
    }),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    账户提现
    
    ## 请求参数说明
    
    - **amount** (float, 必填): 提现金额，范围1.00-账户余额
    - **withdraw_method** (string, 必填): 提现方式，可选值：`alipay`(支付宝), `wechat`(微信), `bank`(银行卡)
    - **withdraw_account** (string, 必填): 提现账户（手机号、银行卡号等）
    - **real_name** (string, 必填): 真实姓名
    - **remark** (string, 可选): 提现备注
    
    ## 业务规则
    
    1. **金额限制**: 提现金额不能超过账户可用余额
    2. **提现方式**: 支持多种提现方式
    3. **实名验证**: 提现需要提供真实姓名
    4. **余额冻结**: 提现申请后余额会被冻结
    5. **审核流程**: 提现需要后台审核通过
    """
    try:
        amount = float(withdraw_data["amount"])
        withdraw_method = withdraw_data["withdraw_method"]
        withdraw_account = withdraw_data["withdraw_account"]
        real_name = withdraw_data["real_name"]
        remark = withdraw_data.get("remark", "账户提现")
        
        # 1. 验证提现金额
        if amount < 1.00:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提现金额不能少于1.00元"
            )
        
        # 2. 验证提现方式
        valid_withdraw_methods = ["alipay", "wechat", "bank"]
        if withdraw_method not in valid_withdraw_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的提现方式"
            )
        
        # 3. 验证提现账户
        if not withdraw_account or len(withdraw_account.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提现账户不能为空且长度不能少于3位"
            )
        
        # 4. 验证真实姓名
        if not real_name or len(real_name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="真实姓名不能为空且长度不能少于2位"
            )
        
        # 5. 检查账户余额
        account_dao = AccountDao(db)
        user_account = await account_dao.get_user_account(db, current_user.user_id)
        
        if not user_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户账户不存在"
            )
        
        available_balance = float(user_account.balance) - float(user_account.frozen_amount)
        if amount > available_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"提现金额不能超过可用余额 {available_balance} 元"
            )
        
        # 6. 检查最小提现金额
        if amount < yozuan_config.yozuan_account_min_withdraw:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"提现金额不能少于 {yozuan_config.yozuan_account_min_withdraw} 元"
            )
        
        # 7. 检查最大提现金额
        if amount > yozuan_config.yozuan_account_max_withdraw:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"单次提现金额不能超过 {yozuan_config.yozuan_account_max_withdraw} 元"
            )
        
        # 8. 冻结提现金额
        await account_dao.update_balance(
            db, current_user.user_id, amount, "freeze"
        )
        
        # 9. 创建提现交易记录
        transaction = await account_dao.create_transaction(
            db=db,
            account_id=user_account.account_id,
            transaction_type="withdraw",
            amount=amount,
            description=f"账户提现 - {remark}",
            related_id=0,  # 提现没有相关订单
            withdraw_method=withdraw_method,
            withdraw_account=withdraw_account,
            real_name=real_name
        )
        
        # 10. 获取更新后的账户信息
        updated_account = await account_dao.get_user_account(db, current_user.user_id)
        
        return {
            "code": 200,
            "msg": "提现申请提交成功，等待后台审核",
            "data": {
                "transaction_id": transaction.transaction_id,
                "amount": amount,
                "withdraw_method": withdraw_method,
                "withdraw_account": withdraw_account,
                "real_name": real_name,
                "current_balance": float(updated_account.balance),
                "frozen_amount": float(updated_account.frozen_amount),
                "available_balance": float(updated_account.balance) - float(updated_account.frozen_amount),
                "remark": remark,
                "status": "pending",
                "note": "提现申请已提交，预计1-3个工作日到账"
            },
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提现申请失败: {str(e)}"
        )


@router.get("/withdraw/records", summary="获取提现记录", tags=["账户操作"])
async def get_withdraw_records(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="提现状态"),
    current_user: AppUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的提现记录
    
    ## 查询参数
    
    - **page**: 页码，从1开始
    - **size**: 每页数量，默认20，最大100
    - **status**: 提现状态筛选（可选）
    
    ## 返回数据
    
    返回提现记录列表，包含提现状态、金额、时间等信息
    """
    try:
        user_id = current_user.user_id
        
        account_dao = AccountDao(db)
        result = await account_dao.get_withdraw_records(
            user_id=user_id,
            status=status,
            page=page,
            size=size
        )
        
        # 格式化返回数据
        withdraw_records = []
        for record in result["records"]:
            withdraw_records.append({
                "transaction_id": record.transaction_id,
                "amount": float(record.amount),
                "withdraw_method": getattr(record, 'withdraw_method', ''),
                "withdraw_account": getattr(record, 'withdraw_account', ''),
                "real_name": getattr(record, 'real_name', ''),
                "status": record.status,
                "status_display": get_display_name(record.status, TRANSACTION_TYPE_DISPLAY),
                "create_time": record.create_time.isoformat() if record.create_time else None,
                "update_time": record.update_time.isoformat() if record.update_time else None,
                "remark": record.description
            })
        
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "withdraw_records": withdraw_records,
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
            detail=f"获取提现记录失败: {str(e)}"
        )
