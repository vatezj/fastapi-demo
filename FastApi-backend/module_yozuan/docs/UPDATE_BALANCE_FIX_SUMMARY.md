# update_balance 方法参数修复总结

## 问题描述

在任务发布过程中出现错误：
```json
{
  "code": 500,
  "msg": "任务发布失败: update_balance() takes 4 positional arguments but 5 were given",
  "success": false,
  "time": "2025-08-27T17:00:32.819055"
}
```

## 问题分析

`update_balance` 方法的定义是：
```python
async def update_balance(self, user_id: int, amount: float, operation: str) -> bool:
```

该方法只接受3个参数（除了self）：
1. `user_id`: 用户ID
2. `amount`: 金额
3. `operation`: 操作类型

但在代码中有些地方错误地传递了4个参数，包括多余的 `db` 参数。

## 修复内容

### 1. 任务控制器中的修复

#### 任务发布接口
```python
# 修复前（错误）
await account_dao.update_balance(
    db, current_user.user_id, total_cost, "freeze"
)

# 修复后（正确）
await account_dao.update_balance(
    current_user.user_id, total_cost, "freeze"
)
```

#### 任务删除接口
```python
# 修复前（错误）
await AccountDao.update_balance(
    db, current_user.user_id, total_cost, "unfreeze"
)

# 修复后（正确）
await account_dao.update_balance(
    current_user.user_id, total_cost, "unfreeze"
)
```

#### 任务审核接口
```python
# 修复前（错误）
await AccountDao.update_balance(
    db, current_user.user_id, total_payment, "unfreeze"
)

# 修复后（正确）
await account_dao.update_balance(
    current_user.user_id, total_payment, "unfreeze"
)
```

### 2. 邀请服务中的修复

```python
# 修复前（错误）
await AccountDao.update_balance(
    db, invitation.inviter_id, rebate_amount, "add"
)

# 修复后（正确）
account_dao = AccountDao(db)
await account_dao.update_balance(
    invitation.inviter_id, rebate_amount, "add"
)
```

### 3. transfer_commission 方法参数修复

```python
# 修复前（错误）
await AccountDao.transfer_commission(
    order.user_id, total_payment, order_id, "任务完成奖励"
)

# 修复后（正确）
await account_dao.transfer_commission(
    current_user.user_id, order.user_id, total_payment, task_id, order_id
)
```

## 修复原则

1. **使用实例方法调用**：`AccountDao` 是实例类，不是静态类，应该创建实例后调用方法
2. **参数数量匹配**：确保传递的参数数量与方法定义一致
3. **参数顺序正确**：按照方法定义的参数顺序传递参数

## 修复后的方法签名

### update_balance
```python
async def update_balance(self, user_id: int, amount: float, operation: str) -> bool:
```
- `user_id`: 用户ID
- `amount`: 金额
- `operation`: 操作类型（add, subtract, freeze, unfreeze）

### transfer_commission
```python
async def transfer_commission(self, from_user_id: int, to_user_id: int, 
                            amount: float, task_id: int, order_id: int) -> bool:
```
- `from_user_id`: 转出用户ID
- `to_user_id`: 转入用户ID
- `amount`: 转账金额
- `task_id`: 任务ID
- `order_id`: 订单ID

## 测试验证

修复后的代码已通过导入测试，任务控制器可以正常导入。

## 注意事项

1. 在调用 `AccountDao` 的方法时，需要先创建实例：`account_dao = AccountDao(db)`
2. 确保传递的参数数量和方法定义一致
3. 参数类型要匹配（int, float, str等）
4. 操作类型必须是预定义的值：`add`, `subtract`, `freeze`, `unfreeze` 