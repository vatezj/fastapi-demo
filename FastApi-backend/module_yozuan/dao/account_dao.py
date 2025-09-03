"""
账户相关数据访问对象
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func, cast, Numeric
from ..entity.do.account_do import YozuanUserAccount, YozuanAccountTransaction
from ..enums.task_enums import TransactionType, TransactionStatus
import logging

logger = logging.getLogger(__name__)


class AccountDao:
    """账户数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user_account(self, user_id: int) -> YozuanUserAccount:
        """创建用户账户"""
        try:
            account = YozuanUserAccount(user_id=user_id)
            self.db.add(account)
            await self.db.commit()
            await self.db.refresh(account)
            return account
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"创建用户账户失败 (user_id={user_id}): {str(e)}")
    
    async def get_user_account(self, user_id: int) -> Optional[YozuanUserAccount]:
        """获取用户账户"""
        try:
            # 检查数据库会话状态
            if not self.db:
                raise ValueError("数据库会话无效")
            
            query = select(YozuanUserAccount).where(YozuanUserAccount.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"查询用户账户失败 (user_id={user_id}): {str(e)}")
            raise ValueError(f"查询用户账户失败 (user_id={user_id}): {str(e)}")
    
    async def get_or_create_user_account(self, user_id: int) -> YozuanUserAccount:
        """获取或创建用户账户"""
        try:
            # 检查数据库会话状态
            if not self.db:
                raise ValueError("数据库会话无效")
            
            account = await self.get_user_account(user_id)
            if not account:
                account = await self.create_user_account(user_id)
            return account
        except Exception as e:
            logger.error(f"获取或创建用户账户失败 (user_id={user_id}): {str(e)}")
            raise ValueError(f"获取或创建用户账户失败 (user_id={user_id}): {str(e)}")
    
    async def update_account_balance(self, user_id: int, amount: float, 
                                   transaction_type: str, description: str = None,
                                   related_id: int = None) -> bool:
        """更新账户余额"""
        try:
            print(f"DEBUG: update_account_balance 开始 - user_id={user_id}, amount={amount}, type={type(amount)}")
            
            account = await self.get_user_account(user_id)
            if not account:
                print(f"DEBUG: 账户不存在 - user_id={user_id}")
                return False
            
            print(f"DEBUG: 账户信息 - balance={account.balance}, type={type(account.balance)}")
            
            # 计算新余额
            balance_before = float(account.balance)
            print(f"DEBUG: balance_before={balance_before}, type={type(balance_before)}")
            print(f"DEBUG: amount={amount}, type={type(amount)}")
            
            balance_after = balance_before + amount
            print(f"DEBUG: balance_after={balance_after}, type={type(balance_after)}")
        except Exception as e:
            print(f"DEBUG: 计算余额时出错: {str(e)}")
            raise
        
        # 更新账户余额
        try:
            print(f"DEBUG: 准备更新账户余额")
            print(f"DEBUG: balance_after={balance_after}, type={type(balance_after)}")
            print(f"DEBUG: amount={amount}, type={type(amount)}")
            
            # 使用更安全的方式处理类型转换
            income_increment = float(amount) if amount > 0 else 0
            withdraw_increment = float(abs(amount)) if amount < 0 else 0
            
            update_query = update(YozuanUserAccount).where(
                YozuanUserAccount.user_id == user_id
            ).values(
                balance=float(balance_after),
                total_income=func.coalesce(YozuanUserAccount.total_income, 0) + cast(income_increment, Numeric(10, 2)),
                total_withdraw=func.coalesce(YozuanUserAccount.total_withdraw, 0) + cast(withdraw_increment, Numeric(10, 2))
            )
            
            print(f"DEBUG: 执行更新查询")
            result = await self.db.execute(update_query)
            print(f"DEBUG: 更新查询执行成功，影响行数: {result.rowcount}")
        except Exception as e:
            print(f"DEBUG: 更新账户余额时出错: {str(e)}")
            raise
        
        # 创建交易记录
        try:
            print(f"DEBUG: 准备创建交易记录")
            print(f"DEBUG: account_id={account.account_id}")
            print(f"DEBUG: transaction_type={transaction_type}")
            print(f"DEBUG: amount={abs(amount)}, type={type(abs(amount))}")
            print(f"DEBUG: balance_before={balance_before}, type={type(balance_before)}")
            print(f"DEBUG: balance_after={balance_after}, type={type(balance_after)}")
            
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
            
            print(f"DEBUG: 交易记录对象创建成功")
            self.db.add(transaction)
            print(f"DEBUG: 交易记录添加到数据库会话")
            await self.db.commit()
            print(f"DEBUG: 数据库提交成功")
        except Exception as e:
            print(f"DEBUG: 创建交易记录时出错: {str(e)}")
            raise
        
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
            balance=YozuanUserAccount.balance - float(amount),
            frozen_amount=YozuanUserAccount.frozen_amount + float(amount)
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
            balance=YozuanUserAccount.balance + float(amount),
            frozen_amount=YozuanUserAccount.frozen_amount - float(amount)
        )
        
        result = await self.db.execute(unfreeze_query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_transaction_history(self, user_id: int, transaction_type: Optional[str] = None,
                                    page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取交易历史"""
        try:
            # 先获取账户信息
            account = await self.get_user_account(user_id)
            if not account:
                return {"transactions": [], "total": 0, "page": page, "size": size, "pages": 0}
            
            # 构建查询
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
            
        except Exception as e:
            raise ValueError(f"获取交易历史失败 (user_id={user_id}): {str(e)}")
    
    async def get_account_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取账户统计信息"""
        try:
            # 先获取账户信息
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
            
        except Exception as e:
            raise ValueError(f"获取账户统计失败 (user_id={user_id}): {str(e)}")
    
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
    
    async def update_balance(self, user_id: int, amount: float, operation: str) -> bool:
        """
        更新账户余额
        
        Args:
            user_id: 用户ID
            amount: 金额
            operation: 操作类型 (add, subtract, freeze, unfreeze)
        """
        try:
            # 检查数据库会话状态
            if not self.db:
                raise ValueError("数据库会话无效")
            
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
                
                # 添加详细的调试信息
                print(f"DEBUG: 冻结操作详细计算:")
                print(f"  - user_id: {user_id}")
                print(f"  - balance_before: {balance_before} (类型: {type(balance_before)})")
                print(f"  - amount: {amount} (类型: {type(amount)})")
                print(f"  - frozen_before: {frozen_before}")
                
                # 冻结：从可用余额中扣除，添加到冻结余额
                balance_after = balance_before - amount
                frozen_after = frozen_before + amount
                
                print(f"  - balance_after: {balance_after} (类型: {type(balance_after)})")
                print(f"  - frozen_after: {frozen_after}")
                
                # 检查计算结果是否合理
                if balance_after < 0:
                    print(f"ERROR: 余额计算结果为负数: {balance_after}")
                    return False
                
                if abs(balance_after) < 0.01:  # 如果余额接近0
                    print(f"WARNING: 余额接近0: {balance_after}")
                
                # 添加调试日志
                logger.info(f"冻结操作详情: user_id={user_id}, amount={amount}")
                logger.info(f"冻结前: balance={balance_before}, frozen={frozen_before}")
                logger.info(f"冻结后: balance={balance_after}, frozen={frozen_after}")
            elif operation == "unfreeze":
                if frozen_before < amount:
                    return False
                balance_after = balance_before + amount
                frozen_after = frozen_before - amount
            else:
                return False
            print(f"DEBUG: 更新账户余额: user_id={user_id}, amount={amount}, operation={operation}")
            print(f"DEBUG: 冻结前: balance={balance_before}, frozen={frozen_before}")
            print(f"DEBUG: 冻结后: balance={balance_after}, frozen={frozen_after}")

            # 更新账户余额
            update_query = update(YozuanUserAccount).where(
                YozuanUserAccount.user_id == user_id
            ).values(
                balance=float(balance_after),
                frozen_amount=float(frozen_after)
            )
            print(f"DEBUG: 更新账户余额查询: {update_query}")
            
            result = await self.db.execute(update_query)
            print(f"DEBUG: 更新账户余额结果: {result.rowcount}")
            await self.db.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"更新账户余额失败 (user_id={user_id}, amount={amount}, operation={operation}): {str(e)}")
            if self.db:
                await self.db.rollback()
            raise ValueError(f"更新账户余额失败: {str(e)}")
    
    async def create_transaction(self, account_id: int, transaction_type: str,
                               amount: float, description: str, related_id: int = 0,
                               **kwargs) -> YozuanAccountTransaction:
        """
        创建交易记录
        
        Args:
            account_id: 账户ID
            transaction_type: 交易类型
            amount: 金额
            description: 描述
            related_id: 相关ID
            **kwargs: 其他字段（包括balance_before, balance_after等）
        """
        try:
            # 检查数据库会话状态
            if not self.db:
                raise ValueError("数据库会话无效")
                
            print(f"DEBUG: 创建交易记录: account_id={account_id}, transaction_type={transaction_type}, amount={amount}, description={description}, related_id={related_id}")
            
            # 获取当前账户余额（确保是最新的）
            account = await self.get_user_account_by_id(account_id)
            if not account:
                raise ValueError(f"账户不存在: {account_id}")
            
            # 计算正确的余额
            balance_before = float(account.balance)
            balance_after = float(account.balance)  # 使用当前实际余额
            
            print(f"DEBUG: 创建交易记录: amount={amount}, balance_before={balance_before}, balance_after={balance_after}")  
            
            # 根据交易类型调整余额
            if transaction_type == "task_freeze":
                # 冻结交易：余额应该减少
                balance_after = balance_before - amount
            elif transaction_type in ["recharge", "rebate", "task_commission"]:
                # 收入交易：余额应该增加
                balance_after = balance_before + amount
            elif transaction_type == "withdraw":
                # 提现交易：余额应该减少
                balance_after = balance_before - amount
            elif transaction_type == "task_unfreeze":
                # 解冻交易：余额应该增加
                balance_after = balance_before + amount
            
            print(f"DEBUG: 交易记录余额计算:")
            print(f"  - balance_before: {balance_before}")
            print(f"  - balance_after: {balance_after}")
            print(f"  - transaction_type: {transaction_type}")
            print(f"  - amount: {amount}")
            
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
            
            print(f"DEBUG: 创建交易记录数据: {transaction_data}")
            
            transaction = YozuanAccountTransaction(**transaction_data)
            self.db.add(transaction)
            await self.db.commit()
            await self.db.refresh(transaction)
            
            print(f"DEBUG: 交易记录创建成功: transaction_id={transaction.transaction_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"创建交易记录失败 (account_id={account_id}): {str(e)}")
            if self.db:
                await self.db.rollback()
            raise ValueError(f"创建交易记录失败 (account_id={account_id}): {str(e)}")
    
    async def get_user_account_by_id(self, account_id: int) -> Optional[YozuanUserAccount]:
        """根据账户ID获取用户账户"""
        try:
            query = select(YozuanUserAccount).where(YozuanUserAccount.account_id == account_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise ValueError(f"查询账户失败 (account_id={account_id}): {str(e)}")
    
    async def get_withdraw_records(self, user_id: int, status: Optional[str] = None,
                                 page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取提现记录"""
        try:
            # 先获取账户信息
            account = await self.get_user_account(user_id)
            if not account:
                return {"records": [], "total": 0, "page": page, "size": size, "pages": 0}
            
            # 构建查询
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
            
        except Exception as e:
            raise ValueError(f"获取提现记录失败 (user_id={user_id}): {str(e)}")
    
    async def update_transaction_related_id(self, user_id: int, transaction_type: str, related_id: int) -> bool:
        """更新交易记录中的关联ID"""
        try:
            # 获取用户账户
            account = await self.get_user_account(user_id)
            if not account:
                return False
            
            # 先查询最新的指定类型交易记录
            query = select(YozuanAccountTransaction.transaction_id).where(
                and_(
                    YozuanAccountTransaction.account_id == account.account_id,
                    YozuanAccountTransaction.transaction_type == transaction_type,
                    YozuanAccountTransaction.related_id == 0  # 只更新related_id为0的记录
                )
            ).order_by(
                YozuanAccountTransaction.create_time.desc()
            ).limit(1)
            
            result = await self.db.execute(query)
            transaction_id = result.scalar_one_or_none()
            
            if not transaction_id:
                return False
            
            # 更新找到的交易记录
            update_query = update(YozuanAccountTransaction).where(
                YozuanAccountTransaction.transaction_id == transaction_id
            ).values(related_id=related_id)
            
            result = await self.db.execute(update_query)
            await self.db.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"更新交易记录关联ID失败 (user_id={user_id}): {str(e)}")
            if self.db:
                await self.db.rollback()
            return False