# 游赚模块项目结构文档

## 项目概述

游赚模块是一个基于FastAPI的完整任务管理平台，采用模块化架构设计，支持独立部署和系统集成。模块包含完整的用户管理、任务管理、订单管理、财务管理等核心业务功能，并集成了企业级的权限控制和操作日志系统。

## 技术架构

### 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Vue.js)                        │
├─────────────────────────────────────────────────────────────┤
│                     API网关层 (FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│                    业务逻辑层 (Service)                      │
├─────────────────────────────────────────────────────────────┤
│                    数据访问层 (DAO)                         │
├─────────────────────────────────────────────────────────────┤
│                    数据存储层 (MySQL/PostgreSQL)             │
└─────────────────────────────────────────────────────────────┘
```

### 模块架构
```
游赚模块 (module_yozuan)
├── 前台API接口 (面向普通用户)
├── 后台管理接口 (面向管理员)
├── 权限控制系统 (RBAC模型)
├── 操作日志系统 (完整审计)
└── 核心业务模块
    ├── 用户管理
    ├── 任务管理
    ├── 订单管理
    ├── 财务管理
    └── 系统管理
```

## 目录结构

### 根目录结构
```
module_yozuan/
├── __init__.py                 # 模块初始化文件
├── app.py                      # 模块主应用入口
├── README.md                   # 模块说明文档
├── docs/                       # 文档目录
│   ├── PROJECT_REQUIREMENTS.md # 项目需求文档
│   ├── PROJECT_STRUCTURE.md    # 项目结构文档
│   ├── TASK_DATABASE_DESIGN.md # 数据库设计文档
│   ├── PERMISSION_SYSTEM.md    # 权限系统文档 ⭐
│   ├── OPERATION_LOGGING.md    # 操作日志文档 ⭐
│   └── ...                     # 其他文档
├── entity/                     # 实体层
├── dao/                        # 数据访问层
├── service/                    # 业务逻辑层
├── controller/                 # 控制器层
│   ├── admin/                  # 后台管理控制器 ⭐
│   │   ├── __init__.py
│   │   ├── admin_controller.py
│   │   ├── task_admin_controller.py
│   │   ├── order_admin_controller.py
│   │   ├── user_admin_controller.py
│   │   ├── finance_admin_controller.py
│   │   └── system_admin_controller.py
│   ├── __init__.py
│   ├── task_controller.py
│   ├── order_controller.py
│   ├── account_controller.py
│   ├── invitation_controller.py
│   └── region_controller.py
├── aspect/                     # 切面处理层 ⭐
│   ├── __init__.py
│   └── yozuan_auth.py         # 权限控制装饰器
├── annotation/                 # 注解层 ⭐
│   ├── __init__.py
│   └── yozuan_log.py          # 操作日志装饰器
├── middleware/                 # 中间件层
│   └── auth_middleware.py     # 认证中间件
├── enums/                      # 枚举定义
│   └── task_enums.py          # 任务相关枚举
├── config/                     # 配置管理
│   └── yozuan_config.py       # 模块配置
└── sql/                        # 数据库脚本
    ├── yozuan_tables.sql       # 核心表结构
    └── yozuan_region_tables.sql # 地区表结构
```

## 核心模块详解

### 1. 权限控制系统 ⭐ **新增**

#### 权限装饰器体系
```python
# 4个专业权限检查器
CheckYozuanInterfaceAuth('yozuan:task:list')  # 接口权限控制
CheckYozuanRoleAuth('yozuan_admin')           # 角色权限控制
CheckYozuanFinanceAuth()                      # 财务权限控制
CheckYozuanSuperAuth()                        # 超级管理员权限
```

#### 权限标识体系
```
权限格式: yozuan:模块:操作

任务管理: yozuan:task:[list|query|edit|remove]
订单管理: yozuan:order:[list|query|edit|review]
用户管理: yozuan:user:[list|query|edit]
财务管理: yozuan:finance:[list|query|review|*]
系统管理: yozuan:system:[dashboard|config|region]

超级权限: *:*:* (系统管理员) | yozuan:*:* (游赚管理员)
```

#### 角色定义体系
```
admin          - 系统超级管理员 (拥有所有权限)
yozuan_admin   - 游赚模块管理员 (拥有游赚模块所有权限)
yozuan_finance - 游赚财务管理员 (拥有财务相关权限)
yozuan_cs      - 游赚客服 (拥有用户管理和订单处理权限)
yozuan_operator - 游赚运营 (拥有任务和用户管理权限)
```

### 2. 操作日志系统 ⭐ **新增**

#### 日志装饰器体系
```python
# 5个专门的日志装饰器
@yozuan_task_log(BusinessType.UPDATE)      # 任务管理日志
@yozuan_order_log(BusinessType.GRANT)      # 订单管理日志
@yozuan_user_log(BusinessType.UPDATE)      # 用户管理日志
@yozuan_finance_log(BusinessType.GRANT)    # 财务管理日志
@yozuan_system_log(BusinessType.DELETE)    # 系统管理日志
```

#### 日志记录内容
```
标题: 游赚模块-{模块名称}
业务类型: BusinessType枚举值
方法名称: 完整的函数路径
请求方式: HTTP方法
操作人员: 管理员用户名
操作URL: 完整请求路径
请求参数: JSON格式的请求数据
返回结果: JSON格式的响应数据
操作状态: 0成功/1异常
执行耗时: 毫秒级时间统计
```

### 3. 后台管理控制器 ⭐ **重构**

#### 控制器分类
```
后台管理控制器 (admin/)
├── admin_controller.py         # 通用管理接口
├── task_admin_controller.py    # 任务管理接口
├── order_admin_controller.py   # 订单管理接口
├── user_admin_controller.py    # 用户管理接口
├── finance_admin_controller.py # 财务管理接口
└── system_admin_controller.py  # 系统管理接口
```

#### 接口权限分布
```
任务管理: 6个接口 (查看、详情、编辑、删除、统计)
订单管理: 5个接口 (查看、详情、编辑、审核、统计)
用户管理: 5个接口 (查看、详情、编辑、统计)
财务管理: 6个接口 (交易、提现、审核、统计、配置)
系统管理: 6个接口 (仪表板、地区CRUD、配置)
```

### 4. 核心业务模块

#### 用户管理模块
- **实体**: `AppUser`, `YozuanUserInvitation`
- **服务**: 用户注册、登录、邀请管理
- **接口**: 前台用户接口、后台管理接口

#### 任务管理模块
- **实体**: `YozuanTask`, `YozuanTaskType`, `YozuanTaskStep`
- **服务**: 任务发布、编辑、删除、状态管理
- **接口**: 任务CRUD、类型管理、步骤管理

#### 订单管理模块
- **实体**: `YozuanTaskOrder`, `YozuanTaskVerificationSubmit`
- **服务**: 订单创建、状态更新、审核处理
- **接口**: 订单管理、审核流程、状态更新

#### 财务管理模块
- **实体**: `YozuanUserAccount`, `YozuanAccountTransaction`
- **服务**: 账户管理、充值提现、分佣计算
- **接口**: 财务操作、交易记录、分佣管理

#### 地区管理模块
- **实体**: `YozuanRegion`, `YozuanTaskRegion`
- **服务**: 地区CRUD、层级管理、任务地区关联
- **接口**: 地区管理、地区查询、统计信息

## 技术特点

### 1. 模块化设计
- **独立部署**: 可作为独立应用运行
- **系统集成**: 可集成到主应用系统
- **松耦合**: 模块间依赖关系清晰
- **可扩展**: 支持新功能模块快速集成

### 2. 权限控制
- **RBAC模型**: 基于角色的访问控制
- **细粒度权限**: 33个权限标识，覆盖所有功能
- **权限隔离**: 前台后台权限分离
- **动态权限**: 支持权限动态配置

### 3. 操作审计
- **完整记录**: 所有后台操作可追溯
- **智能解析**: 自动提取请求参数和响应
- **性能监控**: 执行时间统计和异常监控
- **日志管理**: 支持查询、筛选、导出

### 4. 异步架构
- **FastAPI**: 异步高性能Web框架
- **异步编程**: 全异步架构，支持高并发
- **连接池**: 数据库连接池优化
- **缓存策略**: Redis缓存支持

## 部署架构

### 1. 独立部署
```bash
# 启动游赚模块独立服务
cd module_yozuan
uvicorn app:yozuan_app --host 0.0.0.0 --port 8001
```

### 2. 系统集成
```python
# 在主应用中挂载游赚模块
from module_yozuan.app import yozuan_app
app.mount("/yozuan", yozuan_app, name="yozuan_module")
```

### 3. 容器化部署
```dockerfile
# Dockerfile示例
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "module_yozuan.app:yozuan_app", "--host", "0.0.0.0", "--port", "8000"]
```

## 配置管理

### 1. 环境配置
```python
# yozuan_config.py
class YozuanSettings(BaseSettings):
    # 模块开关
    yozuan_enabled: bool = True
    
    # 数据库配置
    database_prefix: str = "yozuan_"
    
    # 业务限制
    max_task_quantity: int = 1000
    max_task_price: float = 1000.0
    
    # 分佣配置
    rebate_levels: int = 3
    max_rebate_rate: float = 0.5
```

### 2. 权限配置
```python
# 权限标识配置
PERMISSIONS = {
    'yozuan:task:list': '任务列表查看',
    'yozuan:task:edit': '任务编辑',
    'yozuan:order:review': '订单审核',
    'yozuan:finance:review': '财务审核',
    'yozuan:system:config': '系统配置'
}
```

## 监控和运维

### 1. 日志管理
- **操作日志**: 后台管理操作记录
- **访问日志**: 用户访问行为记录
- **错误日志**: 异常和错误信息记录
- **性能日志**: 接口响应时间统计

### 2. 性能监控
- **接口监控**: 响应时间、成功率监控
- **数据库监控**: 查询性能、连接池状态
- **缓存监控**: Redis使用情况和性能
- **系统监控**: CPU、内存、磁盘使用情况

### 3. 安全监控
- **权限监控**: 权限使用情况和异常
- **操作审计**: 敏感操作监控和告警
- **访问控制**: 异常访问行为检测
- **数据安全**: 敏感数据访问监控

## 扩展计划

### 1. 功能扩展
- **消息通知**: 站内信、邮件、短信通知
- **数据统计**: 业务数据分析和报表
- **第三方集成**: 支付、短信、邮件服务
- **移动端支持**: 移动端API和APP开发

### 2. 技术扩展
- **微服务化**: 支持微服务架构部署
- **负载均衡**: 多实例负载均衡支持
- **缓存优化**: 多级缓存策略优化
- **监控告警**: 完善的监控告警体系

## 总结

游赚模块项目结构具有以下特点：

- ✅ **完整的模块化架构**: 支持独立部署和系统集成
- ✅ **企业级权限控制**: 基于RBAC的细粒度权限管理
- ✅ **完整的操作审计**: 所有后台操作可追溯
- ✅ **清晰的分层设计**: Controller -> Service -> DAO -> Entity
- ✅ **灵活的配置管理**: 支持多环境配置和动态调整
- ✅ **完善的监控体系**: 性能监控、安全监控、日志管理

这套架构为游赚平台提供了坚实的技术基础，支持业务的快速发展和系统的稳定运行。
