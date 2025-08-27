# 任务发布余额扣除逻辑说明

## 概述

发布任务时，系统会自动扣除用户账户余额。这是为了确保任务发布者有足够的资金来支付任务完成后的佣金。

## 余额扣除流程

### 1. 余额验证阶段
```python
# 验证用户余额是否足够
user_account = await account_dao.get_user_account(current_user.user_id)
if not user_account:
    return ResponseUtil.error("用户账户不存在")

if float(user_account.balance) < total_cost:
    return ResponseUtil.error(f"余额不足，当前余额: {user_account.balance}，需要: {total_cost}")
```

**验证内容：**
- 检查用户账户是否存在
- 验证可用余额是否足够支付任务总金额
- 如果余额不足，返回错误信息

### 2. 任务创建阶段
```python
# 创建任务记录
task_dao = TaskDao(db)
task = await task_dao.create_task(task_data_with_publisher)
```

**操作内容：**
- 在数据库中创建任务记录
- 设置任务状态为草稿或待审核
- 记录任务的所有相关信息

### 3. 余额冻结阶段
```python
# 冻结用户余额
await account_dao.update_balance(
    current_user.user_id, total_cost, "freeze"
)
```

**冻结逻辑：**
- 从可用余额中扣除任务总金额
- 将扣除的金额添加到冻结余额中
- 确保资金安全，防止重复使用

### 4. 交易记录创建
```python
# 创建冻结交易记录
await account_dao.create_transaction(
    account_id=user_account.account_id,
    transaction_type="task_freeze",
    amount=total_cost,
    description=f"任务发布冻结: {task.task_name}",
    related_id=task.task_id
)
```

**记录内容：**
- 交易类型：`task_freeze`（任务冻结）
- 交易金额：任务总金额
- 交易描述：包含任务名称
- 关联ID：任务ID

## 余额变动说明

### 冻结操作的影响
```python
# 冻结前的余额状态
balance_before = 1000.00      # 可用余额
frozen_before = 0.00         # 冻结余额

# 冻结后的余额状态
balance_after = 1000.00 - 100.00 = 900.00    # 可用余额减少
frozen_after = 0.00 + 100.00 = 100.00        # 冻结余额增加
```

### 余额计算公式
- **任务总金额** = 任务单价 × 任务数量
- **可用余额** = 原可用余额 - 任务总金额
- **冻结余额** = 原冻结余额 + 任务总金额

## 响应信息

### 成功响应
```json
{
    "code": 200,
    "msg": "任务发布成功",
    "data": {
        "task_id": 123,
        "task_name": "测试任务名称",
        "total_cost": 100.00,
        "balance_after": 900.00,
        "frozen_amount_after": 100.00
    },
    "success": true
}
```

### 余额不足错误
```json
{
    "code": 400,
    "msg": "余额不足，当前余额: 50.00，需要: 100.00",
    "success": false
}
```

## 余额解冻场景

### 1. 任务完成审核通过
```python
# 解冻发布者余额并支付接单者
await account_dao.update_balance(
    current_user.user_id, total_payment, "unfreeze"
)
```

### 2. 任务审核驳回
```python
# 解冻发布者余额（不支付接单者）
await account_dao.update_balance(
    current_user.user_id, float(task.task_price), "unfreeze"
)
```

### 3. 任务删除
```python
# 解冻用户余额
await account_dao.update_balance(
    current_user.user_id, total_cost, "unfreeze"
)
```

## 安全机制

### 1. 余额预检查
- 发布任务前验证余额充足性
- 防止发布后因余额不足导致的问题

### 2. 事务一致性
- 使用数据库事务确保余额操作的一致性
- 如果任何步骤失败，自动回滚所有操作

### 3. 冻结机制
- 资金冻结而非直接扣除
- 任务完成后才真正转移资金
- 保护发布者和接单者的权益

## 注意事项

1. **余额充足性**：发布任务前请确保账户余额充足
2. **冻结状态**：冻结的余额在任务完成前无法使用
3. **交易记录**：所有余额变动都有详细的交易记录
4. **解冻时机**：余额解冻的时机取决于任务状态变化
5. **手续费**：平台可能收取一定比例的手续费

## 常见问题

### Q: 为什么发布任务后余额减少了？
A: 这是正常的冻结操作，资金被转移到冻结余额中，任务完成后会解冻或支付给接单者。

### Q: 任务取消后余额会恢复吗？
A: 是的，任务取消或删除后，冻结的余额会自动解冻，恢复到可用余额中。

### Q: 如何查看余额变动记录？
A: 可以通过账户交易记录接口查询所有余额变动历史。 