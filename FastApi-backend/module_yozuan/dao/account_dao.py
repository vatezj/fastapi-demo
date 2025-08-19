"""
账户相关数据访问对象
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from ..entity.do.account_do import YozuanUserAccount, YozuanAccountTransaction
from ..enums.task_enums import TransactionType, TransactionStatus


class AccountDao:
    """账户数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user_account(self, user_id: int) -> YozuanUserAccount:
        """创建用户账户"""
        account = YozuanUserAccount(user_id=user_id)
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account
    
    async def get_user_account(self, user_id: int) -> Optional[YozuanUserAccount]:
        """获取用户账户"""
        query = select(YozuanUserAccount).where(YozuanUserAccount.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_or_create_user_account(self, user_id: int) -> YozuanUserAccount:
        """获取或创建用户账户"""
        account = await self.get_user_account(user_id)
        if not account:
            account = await self.create_user_account(user_id)
        return account
    
    async def update_account_balance(self, user_id: int, amount: float, 
                                   transaction_type: str, description: str = None,
                                   related_id: int = None) -> bool:
        """更新账户余额"""
        account = await self.get_user_account(user_id)
        if not account:
            return False
        
        # 计算新余额
        balance_before = float(account.balance)
        balance_after = balance_before + amount
        
        # 更新账户余额
        update_query = update(YozuanUserAccount).where(
            YozuanUserAccount.user_id == user_id
        ).values(
            balance=balance_after,
            total_income=YozuanUserAccount.total_income + (amount if amount > 0 else 0),
            total_withdraw=YozuanUserAccount.total_withdraw + (abs(amount) if amount < 0 else 0)
        )
        
        result = await self.db.execute(update_query)
        
        # 创建交易记录
        transaction = YozuanAccountTransaction(
            account_id=account.account_id,
            transaction_type=transaction_type,
            amount=abs(amount),
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            status=TransactionStatus.SUCCESS,
            related_id=related_id
        )
        
        self.db.add(transaction)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def freeze_amount(self, user_id: int, amount: float) -> bool:
        """冻结账户金额"""
        account = await self.get_user_account(user_id)
        if not account or float(account.balance) < amount:
            return False
        
        # 冻结金额
        freeze_query = update(YozuanUserAccount).where(
            YozuanUserAccount.user_id == user_id
        ).values(
            balance=YozuanUserAccount.balance - amount,
            frozen_amount=YozuanUserAccount.frozen_amount + amount
        )
        
        result = await self.db.execute(freeze_query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def unfreeze_amount(self, user_id: int, amount: float) -> bool:
        """解冻账户金额"""
        account = await self.get_user_account(user_id)
        if not account or float(account.frozen_amount) < amount:
            return False
        
        # 解冻金额
        unfreeze_query = update(YozuanUserAccount).where(
            YozuanUserAccount.user_id == user_id
        ).values(
            balance=YozuanUserAccount.balance + amount,
            frozen_amount=YozuanUserAccount.frozen_amount - amount
        )
        
        result = await self.db.execute(unfreeze_query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_transaction_history(self, user_id: int, transaction_type: Optional[str] = None,
                                    page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取交易历史"""
        account = await self.get_user_account(user_id)
        if not account:
            return {"transactions": [], "total": 0, "page": page, "size": size, "pages": 0}
        
        query = select(YozuanAccountTransaction).where(
            YozuanAccountTransaction.account_id == account.account_id
        )
        
        if transaction_type:
            query = query.where(YozuanAccountTransaction.transaction_type == transaction_type)
        
        # 计算总数
        count_query = select(func.count(YozuanAccountTransaction.transaction_id)).where(
            YozuanAccountTransaction.account_id == account.account_id
        )
        if transaction_type:
            count_query = count_query.where(YozuanAccountTransaction.transaction_type == transaction_type)
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # 分页查询
        query = query.order_by(YozuanAccountTransaction.create_time.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        transactions = result.scalars().all()
        
        return {
            "transactions": transactions,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    async def get_account_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取账户统计信息"""
        account = await self.get_user_account(user_id)
        if not account:
            return {}
        
        # 统计各种交易类型
        type_stats = {}
        for trans_type in TransactionType:
            count_query = select(func.count(YozuanAccountTransaction.transaction_id)).where(
                and_(YozuanAccountTransaction.account_id == account.account_id,
                     YozuanAccountTransaction.transaction_type == trans_type.value)
            )
            count_result = await self.db.execute(count_query)
            type_stats[trans_type.value] = count_result.scalar()
        
        # 统计总收入
        income_query = select(func.sum(YozuanAccountTransaction.amount)).where(
            and_(YozuanAccountTransaction.account_id == account.account_id,
                 YozuanAccountTransaction.transaction_type.in_([
                     TransactionType.TASK_COMMISSION.value,
                     TransactionType.REBATE.value
                 ]))
        )
        income_result = await self.db.execute(income_query)
        total_income = income_result.scalar() or 0
        
        return {
            "balance": float(account.balance),
            "frozen_amount": float(account.frozen_amount),
            "total_income": float(account.total_income),
            "total_withdraw": float(account.total_withdraw),
            "transaction_counts": type_stats,
            "calculated_income": float(total_income)
        }
    
    async def check_balance_sufficient(self, user_id: int, amount: float) -> bool:
        """检查账户余额是否充足"""
        account = await self.get_user_account(user_id)
        if not account:
            return False
        
        return float(account.balance) >= amount
    
    async def transfer_commission(self, from_user_id: int, to_user_id: int, 
                                amount: float, task_id: int, order_id: int) -> bool:
        """转移佣金（从发布者到接单者）"""
        # 检查发布者余额
        if not await self.check_balance_sufficient(from_user_id, amount):
            return False
        
        # 从发布者账户扣除
        success1 = await self.update_account_balance(
            from_user_id, -amount, TransactionType.FEE,
            f"任务{task_id}佣金支出", task_id
        )
        
        if not success1:
            return False
        
        # 添加到接单者账户
        success2 = await self.update_account_balance(
            to_user_id, amount, TransactionType.TASK_COMMISSION,
            f"完成任务{task_id}获得佣金", task_id
        )
        
        return success2
    
    async def update_balance(self, db: AsyncSession, user_id: int, amount: float, operation: str) -> bool:
        """
        更新账户余额
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            amount: 金额
            operation: 操作类型 (add, subtract, freeze, unfreeze)
        """
        account = await self.get_user_account(user_id)
        if not account:
            return False
        
        balance_before = float(account.balance)
        frozen_before = float(account.frozen_amount)
        
        if operation == "add":
            balance_after = balance_before + amount
            frozen_after = frozen_before
        elif operation == "subtract":
            if balance_before < amount:
                return False
            balance_after = balance_before - amount
            frozen_after = frozen_before
        elif operation == "freeze":
            if balance_before < amount:
                return False
            balance_after = balance_before - amount
            frozen_after = frozen_before + amount
        elif operation == "unfreeze":
            if frozen_before < amount:
                return False
            balance_after = balance_before + amount
            frozen_after = frozen_before - amount
        else:
            return False
        
        # 更新账户余额
        update_query = update(YozuanUserAccount).where(
            YozuanUserAccount.user_id == user_id
        ).values(
            balance=balance_after,
            frozen_amount=frozen_after
        )
        
        result = await self.db.execute(update_query)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def create_transaction(self, db: AsyncSession, account_id: int, transaction_type: str,
                               amount: float, description: str, related_id: int = 0,
                               **kwargs) -> YozuanAccountTransaction:
        """
        创建交易记录
        
        Args:
            db: 数据库会话
            account_id: 账户ID
            transaction_type: 交易类型
            amount: 金额
            description: 描述
            related_id: 相关ID
            **kwargs: 其他字段
        """
        # 获取当前余额
        account = await self.get_user_account_by_id(account_id)
        if not account:
            raise ValueError("账户不存在")
        
        balance_before = float(account.balance)
        balance_after = balance_before
        
        # 根据交易类型调整余额
        if transaction_type == "recharge":
            balance_after = balance_before + amount
        elif transaction_type == "withdraw":
            balance_after = balance_before  # 提现时余额已在冻结时扣除
        
        # 创建交易记录
        transaction_data = {
            "account_id": account_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "description": description,
            "status": "success",
            "related_id": related_id
        }
        
        # 添加额外字段
        for key, value in kwargs.items():
            if hasattr(YozuanAccountTransaction, key):
                transaction_data[key] = value
        
        transaction = YozuanAccountTransaction(**transaction_data)
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction
    
    async def get_user_account_by_id(self, account_id: int) -> Optional[YozuanUserAccount]:
        """根据账户ID获取用户账户"""
        query = select(YozuanUserAccount).where(YozuanUserAccount.account_id == account_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_withdraw_records(self, user_id: int, status: Optional[str] = None,
                                 page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取提现记录"""
        account = await self.get_user_account(user_id)
        if not account:
            return {"records": [], "total": 0, "page": page, "size": size, "pages": 0}
        
        query = select(YozuanAccountTransaction).where(
            and_(
                YozuanAccountTransaction.account_id == account.account_id,
                YozuanAccountTransaction.transaction_type == "withdraw"
            )
        )
        
        if status:
            query = query.where(YozuanAccountTransaction.status == status)
        
        # 计算总数
        count_query = select(func.count(YozuanAccountTransaction.transaction_id)).where(
            and_(
                YozuanAccountTransaction.account_id == account.account_id,
                YozuanAccountTransaction.transaction_type == "withdraw"
            )
        )
        if status:
            count_query = count_query.where(YozuanAccountTransaction.status == status)
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # 分页查询
        query = query.order_by(YozuanAccountTransaction.create_time.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return {
            "records": records,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
