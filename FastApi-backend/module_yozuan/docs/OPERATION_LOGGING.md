# 游赚模块操作日志系统

## 概述

游赚模块操作日志系统基于 `module_admin` 的日志记录功能，为所有后台管理接口提供完整的操作日志记录，确保系统操作的可追溯性和安全性。

## 系统特性

### ✅ 完整的操作记录
- **操作人员**: 记录执行操作的管理员信息
- **操作时间**: 精确到毫秒的操作时间戳
- **操作内容**: 详细的请求参数和返回结果
- **操作结果**: 成功/失败状态和错误信息
- **执行耗时**: 接口执行时间统计

### ✅ 智能参数解析
- **路径参数**: 自动提取URL路径参数
- **请求体参数**: 支持JSON、表单等多种格式
- **参数截断**: 自动处理超长参数，避免日志过大
- **错误处理**: 参数解析失败时的友好提示

### ✅ 模块化日志分类
- **任务管理**: 任务状态变更、删除等操作
- **订单管理**: 订单审核、状态更新等操作
- **用户管理**: 用户状态变更、权限调整等操作
- **财务管理**: 提现审核、返佣配置等操作
- **系统管理**: 地区管理、系统配置等操作

## 日志装饰器

### 1. 基础日志装饰器

#### YozuanLog
```python
@YozuanLog(title="任务管理", business_type=BusinessType.UPDATE)
async def update_task_status():
    # 接口实现
    pass
```

**参数说明**:
- `title`: 模块标题，显示在日志中
- `business_type`: 业务类型，对应BusinessType枚举
- `log_type`: 日志类型，固定为'operation'

### 2. 便捷日志装饰器

#### 任务管理日志
```python
@yozuan_task_log(BusinessType.UPDATE)
async def update_task_status():
    pass

@yozuan_task_log(BusinessType.DELETE)
async def delete_task():
    pass
```

#### 订单管理日志
```python
@yozuan_order_log(BusinessType.UPDATE)
async def update_order_status():
    pass

@yozuan_order_log(BusinessType.GRANT)
async def review_order():
    pass
```

#### 用户管理日志
```python
@yozuan_user_log(BusinessType.UPDATE)
async def update_user_status():
    pass
```

#### 财务管理日志
```python
@yozuan_finance_log(BusinessType.GRANT)
async def review_withdraw():
    pass

@yozuan_finance_log(BusinessType.UPDATE)
async def update_rebate_config():
    pass
```

#### 系统管理日志
```python
@yozuan_system_log(BusinessType.INSERT)
async def create_region():
    pass

@yozuan_system_log(BusinessType.UPDATE)
async def update_region():
    pass

@yozuan_system_log(BusinessType.DELETE)
async def delete_region():
    pass
```

## 业务类型定义

### BusinessType 枚举值
```python
from config.enums import BusinessType

# 常用业务类型
BusinessType.INSERT    # 新增操作
BusinessType.UPDATE    # 修改操作
BusinessType.DELETE    # 删除操作
BusinessType.GRANT     # 授权/审核操作
BusinessType.EXPORT    # 导出操作
BusinessType.IMPORT    # 导入操作
BusinessType.FORCE     # 强制操作
BusinessType.GENCODE   # 代码生成
BusinessType.CLEAN     # 清空数据
BusinessType.OTHER     # 其他操作
```

## 日志记录内容

### 1. 基础信息
- **日志标题**: `游赚模块-{模块名称}`
- **业务类型**: 对应的BusinessType值
- **方法名称**: 函数路径和名称
- **请求方式**: HTTP方法（GET、POST、PUT、DELETE）

### 2. 操作信息
- **操作人员**: 当前登录管理员用户名
- **部门名称**: 管理员所属部门
- **操作URL**: 完整的请求路径
- **操作IP**: 请求来源IP地址
- **操作地点**: IP地理位置（简化处理）

### 3. 请求参数
- **路径参数**: URL中的动态参数
- **请求体参数**: POST/PUT请求的数据
- **参数格式**: JSON字符串格式
- **参数长度**: 自动截断超长参数

### 4. 响应结果
- **返回结果**: 接口返回的JSON数据
- **操作状态**: 0成功，1异常
- **错误信息**: 异常时的错误描述
- **执行耗时**: 接口执行时间（毫秒）

## 使用示例

### 1. 任务状态更新日志
```python
@router.put("/tasks/{task_id}/status")
@yozuan_task_log(BusinessType.UPDATE)
async def update_task_status(
    task_id: int,
    status_data: Dict[str, Any] = Body(...),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 接口实现
    pass
```

**日志记录内容**:
```
标题: 游赚模块-任务管理
业务类型: 2 (UPDATE)
方法名称: module_yozuan.controller.admin.task_admin_controller.update_task_status()
请求方式: PUT
操作人员: admin
操作URL: /v1/admin/task/tasks/123/status
请求参数: {"task_id": 123, "status": "suspended", "reason": "内容违规"}
返回结果: {"code": 200, "msg": "更新成功"}
操作状态: 0 (成功)
执行耗时: 45ms
```

### 2. 订单审核日志
```python
@router.post("/orders/{order_id}/review")
@yozuan_order_log(BusinessType.GRANT)
async def review_order_completion(
    order_id: int,
    review_data: Dict[str, Any] = Body(...),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 接口实现
    pass
```

**日志记录内容**:
```
标题: 游赚模块-订单管理
业务类型: 4 (GRANT)
方法名称: module_yozuan.controller.admin.order_admin_controller.review_order_completion()
请求方式: POST
操作人员: finance_admin
操作URL: /v1/admin/order/orders/456/review
请求参数: {"order_id": 456, "review_status": "approved", "bonus_amount": 2.00}
返回结果: {"code": 200, "msg": "审核成功"}
操作状态: 0 (成功)
执行耗时: 128ms
```

### 3. 地区删除日志
```python
@router.delete("/regions/{region_code}")
@yozuan_system_log(BusinessType.DELETE)
async def delete_admin_region(
    region_code: str,
    reason: str = Body(...),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 接口实现
    pass
```

**日志记录内容**:
```
标题: 游赚模块-系统管理
业务类型: 3 (DELETE)
方法名称: module_yozuan.controller.admin.system_admin_controller.delete_admin_region()
请求方式: DELETE
操作人员: super_admin
操作URL: /v1/admin/system/regions/110000
请求参数: {"region_code": "110000", "reason": "行政区划调整"}
返回结果: {"code": 200, "msg": "地区删除成功"}
操作状态: 0 (成功)
执行耗时: 67ms
```

## 日志查询和管理

### 1. 在后台管理系统中查看
- 访问: `http://127.0.0.1:9099/admin/monitor/operlog/list`
- 权限: `monitor:operlog:list`
- 功能: 分页查询、条件筛选、导出等

### 2. 日志筛选条件
- **模块标题**: 按"游赚模块-*"筛选
- **业务类型**: 按具体操作类型筛选
- **操作人员**: 按管理员用户名筛选
- **操作时间**: 按时间范围筛选
- **操作状态**: 按成功/失败筛选

### 3. 日志导出功能
- 支持Excel格式导出
- 包含完整的操作记录信息
- 便于审计和数据分析

## 最佳实践

### 1. 日志装饰器使用原则
- **所有写操作**: 必须添加日志装饰器
- **敏感操作**: 使用合适的业务类型
- **批量操作**: 记录操作数量和影响范围
- **异常处理**: 确保异常信息被完整记录

### 2. 业务类型选择
- **INSERT**: 新增数据操作
- **UPDATE**: 修改数据操作
- **DELETE**: 删除数据操作
- **GRANT**: 审核、授权操作
- **EXPORT**: 数据导出操作
- **IMPORT**: 数据导入操作

### 3. 日志内容优化
- **参数精简**: 避免记录敏感信息
- **结果摘要**: 记录关键结果信息
- **错误详情**: 提供足够的错误上下文
- **性能监控**: 关注执行耗时异常

## 系统集成

### 1. 与module_admin集成
- 复用现有的日志表结构
- 共享日志查询和管理界面
- 统一的日志格式和标准

### 2. 权限控制集成
- 日志查看需要相应权限
- 日志导出需要导出权限
- 日志清理需要管理员权限

### 3. 监控告警集成
- 异常操作自动告警
- 性能异常监控
- 操作频率统计

## 总结

游赚模块操作日志系统提供了：

- ✅ **完整的操作记录**: 覆盖所有后台管理操作
- ✅ **智能的参数解析**: 自动提取和格式化请求参数
- ✅ **模块化的日志分类**: 便于按模块查询和管理
- ✅ **便捷的装饰器**: 简化日志记录代码
- ✅ **统一的日志格式**: 与系统整体保持一致
- ✅ **强大的查询功能**: 支持多维度筛选和导出

这套日志系统确保了游赚平台所有后台操作的可追溯性，为系统安全审计、问题排查和性能优化提供了强有力的支持。
