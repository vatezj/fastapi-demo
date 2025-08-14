# FastAPI 后端架构与开发指南

## 项目概述

FastAPI 后端是一个基于 FastAPI 框架的现代化 Web 应用后端，采用模块化架构设计，支持异步编程、自动 API 文档生成、权限控制等特性。

## 技术栈

- **Web 框架**: FastAPI
- **数据库**: SQLAlchemy (异步)
- **ORM**: SQLAlchemy ORM
- **数据库**: PostgreSQL / MySQL
- **缓存**: Redis
- **任务调度**: APScheduler
- **API 文档**: OpenAPI (Swagger)
- **权限控制**: JWT + 角色权限
- **代码生成**: 模块化代码生成器
- **日志**: 结构化日志系统

## 项目结构

```
FastApi-backend/
├── app.py                          # 主应用入口
├── server.py                       # 服务器启动脚本
├── start_app.py                    # 应用启动脚本
├── config/                         # 配置文件
│   ├── env.py                      # 环境配置
│   ├── database.py                 # 数据库配置
│   ├── constant.py                 # 常量定义
│   └── enums.py                    # 枚举定义
├── module_admin/                   # 管理模块
│   ├── app.py                      # 管理模块应用
│   ├── controller/                 # 控制器层
│   ├── service/                    # 服务层
│   ├── dao/                        # 数据访问层
│   ├── entity/                     # 实体层
│   │   ├── do/                     # 数据对象
│   │   └── vo/                     # 视图对象
│   ├── aspect/                     # 切面编程
│   └── annotation/                 # 注解定义
├── module_app/                     # APP模块
│   ├── app.py                      # APP模块应用
│   ├── controller/                 # 控制器层
│   ├── service/                    # 服务层
│   ├── dao/                        # 数据访问层
│   └── entity/                     # 实体层
├── module_generator/               # 代码生成模块
│   ├── controller/                 # 生成器控制器
│   ├── service/                    # 生成器服务
│   └── templates/                  # 代码模板
├── shared/                         # 共享模块
│   ├── dao/                        # 基础DAO
│   ├── entity/                     # 基础实体
│   ├── service/                    # 基础服务
│   └── utils/                      # 工具类
├── utils/                          # 工具模块
├── middlewares/                    # 中间件
├── exceptions/                     # 异常处理
├── logs/                          # 日志文件
└── tests/                         # 测试文件
```

## 核心架构

### 1. 分层架构

```
┌─────────────────────────────────────┐
│            Controller               │  ← 控制器层 (API接口)
├─────────────────────────────────────┤
│             Service                 │  ← 服务层 (业务逻辑)
├─────────────────────────────────────┤
│               DAO                   │  ← 数据访问层
├─────────────────────────────────────┤
│             Entity                  │  ← 实体层 (数据模型)
└─────────────────────────────────────┘
```

### 2. 模块化设计

- **module_admin**: 系统管理功能
- **module_app**: 移动应用功能
- **module_business**: 业务功能
- **module_generator**: 代码生成功能

### 3. 权限控制架构

```
用户认证 → JWT Token → 角色验证 → 接口权限 → 数据权限
```

## 核心功能模块

### 1. 用户认证与权限

- **登录认证**: JWT Token 认证
- **角色管理**: 基于角色的权限控制 (RBAC)
- **接口权限**: 接口级别的权限验证
- **数据权限**: 数据范围的权限控制

### 2. 系统管理

- **用户管理**: 用户增删改查、角色分配
- **角色管理**: 角色定义、权限分配
- **菜单管理**: 动态菜单、权限控制
- **部门管理**: 组织架构管理
- **字典管理**: 系统字典维护

### 3. 监控管理

- **在线用户**: 在线用户监控
- **操作日志**: 用户操作记录
- **登录日志**: 登录历史记录
- **服务监控**: 系统性能监控
- **缓存监控**: Redis 缓存状态

### 4. 代码生成

- **表结构生成**: 根据数据库表生成代码
- **模块化生成**: 支持多种模块类型
- **前端生成**: Vue.js 前端代码生成
- **后端生成**: Python 后端代码生成

## API 设计规范

### 1. RESTful API

- **GET**: 查询数据
- **POST**: 创建数据
- **PUT**: 更新数据
- **DELETE**: 删除数据

### 2. 响应格式

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {},
  "timestamp": "2024-01-01T00:00:00"
}
```

### 3. 分页格式

```json
{
  "code": 200,
  "msg": "查询成功",
  "data": {
    "rows": [],
    "total": 100,
    "pageNum": 1,
    "pageSize": 10
  }
}
```

## 数据库设计

### 1. 核心表结构

- **sys_user**: 用户表
- **sys_role**: 角色表
- **sys_menu**: 菜单表
- **sys_dept**: 部门表
- **sys_dict**: 字典表
- **app_user**: APP用户表

### 2. 权限表结构

- **sys_user_role**: 用户角色关联
- **sys_role_menu**: 角色菜单关联
- **sys_role_dept**: 角色部门关联

## 开发指南

### 1. 环境要求

- Python 3.8+
- PostgreSQL 12+ / MySQL 8.0+
- Redis 6.0+

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 复制环境配置文件
cp config/env.py.example config/env.py

# 修改数据库配置
vim config/env.py
```

### 4. 启动应用

```bash
# 开发模式
python start_app.py

# 生产模式
python server.py
```

### 5. 代码生成

```bash
# 访问代码生成器
http://localhost:8000/tool/gen

# 使用模块化代码生成
POST /tool/gen/modules/generate
```

## 部署指南

### 1. 生产环境配置

- 使用 Gunicorn 作为 WSGI 服务器
- 配置 Nginx 反向代理
- 启用 HTTPS
- 配置日志轮转

### 2. Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
```

### 3. 环境变量

```bash
# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379/0

# 应用配置
SECRET_KEY=your-secret-key
DEBUG=False
```

## 测试指南

### 1. 单元测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定模块测试
python -m pytest tests/module_admin/
```

### 2. API 测试

```bash
# 访问 Swagger 文档
http://localhost:8000/docs

# 访问 ReDoc 文档
http://localhost:8000/redoc
```

## 性能优化

### 1. 数据库优化

- 使用数据库连接池
- 优化 SQL 查询
- 添加适当的索引
- 使用读写分离

### 2. 缓存策略

- Redis 缓存热点数据
- 缓存装饰器
- 缓存失效策略

### 3. 异步处理

- 异步数据库操作
- 异步任务队列
- 异步日志记录

## 安全考虑

### 1. 认证安全

- JWT Token 过期时间
- 密码加密存储
- 登录失败限制

### 2. 权限安全

- 接口权限验证
- 数据权限控制
- SQL 注入防护

### 3. 数据安全

- 敏感数据加密
- 数据传输加密
- 日志脱敏处理

## 监控与日志

### 1. 日志系统

- 结构化日志格式
- 日志级别控制
- 日志文件轮转

### 2. 性能监控

- 接口响应时间
- 数据库查询性能
- 系统资源使用

### 3. 错误监控

- 异常捕获记录
- 错误堆栈跟踪
- 告警通知机制

## 常见问题

### 1. 数据库连接问题

- 检查数据库服务状态
- 验证连接参数
- 检查网络连通性

### 2. 权限验证问题

- 检查用户角色配置
- 验证接口权限设置
- 查看权限日志

### 3. 性能问题

- 分析慢查询日志
- 检查缓存命中率
- 监控系统资源

## 贡献指南

### 1. 代码规范

- 遵循 PEP 8 规范
- 添加类型注解
- 编写文档字符串

### 2. 提交规范

- 使用语义化提交信息
- 添加测试用例
- 更新相关文档

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目维护者: insistence
- 项目地址: [GitHub Repository]
- 问题反馈: [Issues] 