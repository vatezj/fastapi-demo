# 游赚模块 (YouZuan Module)

## 📋 项目简介

游赚模块是一个基于FastAPI的任务接单平台，支持用户发布任务、接单完成任务、获得佣金等完整业务流程。采用模块化架构设计，具有高扩展性和可维护性。

## 🚀 核心功能

### 1. 任务管理
- ✅ 任务发布和编辑
- ✅ 任务类型管理（9种预定义类型）
- ✅ 任务步骤设置（支持链接、图片、文本）
- ✅ 任务验证要求配置
- ✅ 任务状态流转管理

### 2. 订单管理
- ✅ 任务报名和接单
- ✅ 订单状态跟踪
- ✅ 任务执行和完成
- ✅ 验证材料提交（一次性提交所有验证）

### 3. 账户体系
- ✅ 用户账户管理
- ✅ 资金变动记录
- ✅ 充值提现功能
- ✅ 任务佣金分配

### 4. 分销返佣
- ✅ 三级分销体系
- ✅ 邀请码系统
- ✅ 自动返佣计算
- ✅ 返佣记录管理

## 🏗️ 技术架构

### 后端技术栈
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **数据库**: PostgreSQL/MySQL
- **缓存**: Redis
- **权限**: 基于装饰器的权限控制

### 架构模式
- **分层架构**: Controller → Service → DAO → Entity
- **模块化设计**: 独立的业务模块
- **RESTful API**: 标准的REST接口设计

## 📁 项目结构

```
module_yozuan/
├── __init__.py                 # 模块初始化
├── app.py                     # 模块主入口
├── controller/                # 控制器层
├── service/                   # 业务逻辑层
├── dao/                      # 数据访问层
├── entity/                   # 数据实体层
│   ├── do/                   # 数据对象
│   └── vo/                   # 视图对象
├── enums/                    # 枚举定义
├── utils/                    # 工具函数
├── sql/                      # 数据库脚本
├── docs/                     # 项目文档
└── README.md                 # 本文件
```

## 🗄️ 数据库设计

### 核心表结构
- `yozuan_task` - 任务主表
- `yozuan_task_type` - 任务类型表
- `yozuan_task_step` - 任务步骤表
- `yozuan_task_verification` - 任务验证表
- `yozuan_task_order` - 任务订单表
- `yozuan_task_verification_submit` - 验证提交表
- `yozuan_user_account` - 用户账户表
- `yozuan_account_transaction` - 资金变动记录表
- `yozuan_user_invitation` - 用户邀请关系表
- `yozuan_rebate_config` - 返佣配置表
- `yozuan_rebate_record` - 返佣记录表

### 设计特点
- ✅ 所有表名添加 `yozuan_` 前缀
- ✅ 使用VARCHAR替代ENUM，支持代码枚举
- ✅ 合理的索引设计，优化查询性能
- ✅ 外键约束保证数据完整性

## 🔌 API接口

### 基础路径
```
/yozuan/v1/
```

### 主要接口
- **任务管理**: `/task/*`
- **订单管理**: `/order/*`
- **账户管理**: `/account/*`
- **管理接口**: `/admin/*`

### 接口特点
- RESTful设计风格
- 统一的响应格式
- 完善的权限控制
- 详细的API文档

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- FastAPI
- SQLAlchemy
- PostgreSQL/MySQL
- Redis

### 2. 安装依赖
```bash
pip install fastapi sqlalchemy asyncpg redis
```

### 3. 数据库初始化
```bash
# 执行建表脚本
psql -d your_database -f module_yozuan/sql/yozuan_tables.sql
```

### 4. 启动服务
```python
# 在主应用中引入模块
from module_yozuan.app import yozuan_app

app = FastAPI()
app.include_router(yozuan_app, prefix="/yozuan", tags=["游赚模块"])
```

## 📚 文档说明

### 已完成的文档
- ✅ `PROJECT_REQUIREMENTS.md` - 项目需求文档
- ✅ `TASK_DATABASE_DESIGN.md` - 数据库设计文档
- ✅ `TASK_STEPS_AND_VERIFICATION.md` - 任务步骤和验证说明
- ✅ `ENUM_DESIGN.md` - 枚举设计说明
- ✅ `PROJECT_STRUCTURE.md` - 项目结构说明

### 文档特点
- 详细的功能需求分析
- 完整的数据库设计
- 清晰的业务流程说明
- 实用的开发指导

## 🔧 开发规范

### 1. 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型注解提高代码可读性
- 编写详细的文档字符串

### 2. 命名规范
- 类名使用PascalCase
- 函数和变量使用snake_case
- 常量使用UPPER_CASE
- 表名使用snake_case并添加模块前缀

### 3. 架构规范
- 严格遵循分层架构
- 业务逻辑放在Service层
- 数据访问放在DAO层
- 接口定义放在Controller层

## 🧪 测试策略

### 1. 测试覆盖
- 单元测试：Service层业务逻辑
- 集成测试：完整的业务流程
- 性能测试：高并发场景测试

### 2. 测试工具
- pytest - 测试框架
- pytest-asyncio - 异步测试支持
- pytest-cov - 测试覆盖率

## 🚀 部署说明

### 1. 环境配置
```python
# config/env.py
YOZUAN_MODULE_ENABLED = True
YOZUAN_DATABASE_URL = "postgresql://user:pass@localhost/yozuan"
YOZUAN_REDIS_URL = "redis://localhost:6379/1"
```

### 2. Docker部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 开发进度

### 已完成
- ✅ 项目需求分析和设计
- ✅ 数据库表结构设计
- ✅ 枚举系统设计
- ✅ 项目架构规划
- ✅ 基础实体类定义

### 进行中
- 🔄 核心业务逻辑实现
- 🔄 API接口开发
- 🔄 权限控制集成

### 待完成
- ⏳ 前端界面开发
- ⏳ 测试用例编写
- ⏳ 性能优化
- ⏳ 部署配置

## 🤝 贡献指南

### 1. 开发流程
1. Fork项目到个人仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request
5. 代码审查和合并

### 2. 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

## 📞 联系方式

- **项目维护**: AI Assistant
- **创建时间**: 2025-08-15
- **版本**: 1.0.0
- **状态**: 开发中

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

**注意**: 本项目仍在积极开发中，API接口和功能可能会有变化。建议在生产环境使用前充分测试。
