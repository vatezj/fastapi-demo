# RuoYi-Vue3-FastAPI 后端项目

## 项目简介

RuoYi-Vue3-FastAPI 是一个基于 FastAPI 框架的现代化后端管理系统，采用异步编程模式，提供高性能、可扩展的企业级应用开发框架。项目集成了完整的用户权限管理、代码生成、定时任务等核心功能模块。

## 技术栈

### 核心框架
- **FastAPI 0.115.8** - 现代、快速的Web框架，基于Python 3.7+
- **Python 3.12** - 支持异步编程的最新Python版本

### 数据库
- **SQLAlchemy 2.0.38** - 异步ORM框架，支持MySQL和PostgreSQL
- **asyncmy 0.2.10** - 异步MySQL驱动
- **PyMySQL 1.1.1** - MySQL数据库连接器

### 缓存和会话
- **Redis 5.2.1** - 高性能内存数据库，用于缓存和会话存储
- **PyJWT 2.10.1** - JWT令牌生成和验证

### 任务调度
- **APScheduler 3.11.0** - 高级Python调度器，支持定时任务

### 数据处理
- **Pandas 2.2.3** - 数据分析和处理
- **openpyxl 3.1.5** - Excel文件读写支持

### 工具库
- **loguru 0.7.3** - 现代化日志记录
- **passlib 1.7.4** - 密码哈希和验证
- **Pillow 11.1.0** - 图像处理
- **psutil 7.0.0** - 系统和进程监控

## 项目架构

### 分层架构设计
```
┌─────────────────────────────────────┐
│            Controller Layer         │  ← HTTP请求处理
├─────────────────────────────────────┤
│             Service Layer           │  ← 业务逻辑处理
├─────────────────────────────────────┤
│               DAO Layer             │  ← 数据访问层
├─────────────────────────────────────┤
│            Database Layer           │  ← 数据库存储
└─────────────────────────────────────┘
```

### 模块化设计
- **module_admin** - 系统管理核心模块
- **module_generator** - 代码生成模块
- **module_task** - 定时任务模块
- **utils** - 通用工具库
- **config** - 配置管理
- **middlewares** - 中间件
- **exceptions** - 异常处理

## 核心功能模块

### 1. 用户权限管理
- **用户管理** - 用户CRUD操作、密码管理、状态控制
- **角色管理** - 角色分配、权限继承、角色层级
- **菜单管理** - 动态菜单、权限控制、路由管理
- **部门管理** - 组织架构、部门层级、数据权限

### 2. 系统管理
- **字典管理** - 系统字典、数据枚举、配置管理
- **参数配置** - 系统参数、环境配置、动态配置
- **通知公告** - 系统通知、消息推送、公告管理
- **岗位管理** - 岗位设置、职责定义、人员分配

### 3. 系统监控
- **在线用户** - 用户会话监控、强制下线
- **操作日志** - 操作审计、行为追踪、安全监控
- **登录日志** - 登录记录、安全分析、异常检测
- **定时任务** - 任务调度、执行监控、日志记录
- **服务监控** - 系统性能、资源监控、健康检查
- **缓存监控** - Redis状态、缓存命中率、性能分析

### 4. 代码生成
- **后端代码** - Controller、Service、DAO、Entity自动生成
- **前端代码** - Vue3组件、API接口、页面模板
- **数据库脚本** - 建表语句、索引优化、数据初始化
- **API文档** - 接口文档、参数说明、响应示例

## 快速开始

### 环境要求
- Python 3.8+
- MySQL 5.7+ 或 PostgreSQL 10+
- Redis 6.0+
- 操作系统：Windows/Linux/macOS

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd ruoyi-fastapi-backend
```

#### 2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量
创建 `.env` 文件：
```env
# 应用配置
APP_ENV=dev
APP_NAME=RuoYi-FastAPI
APP_HOST=0.0.0.0
APP_PORT=9099

# 数据库配置
DB_TYPE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=your_password
DB_DATABASE=ruoyi-fastapi

# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DATABASE=2

# JWT配置
JWT_SECRET_KEY=your_secret_key
JWT_EXPIRE_MINUTES=1440
```

#### 5. 初始化数据库
```bash
# 导入SQL脚本
mysql -u root -p ruoyi-fastapi < sql/ruoyi-fastapi.sql
```

#### 6. 启动应用
```bash
python app.py
```

应用将在 `http://localhost:9099` 启动，API文档地址：`http://localhost:9099/docs`

## 项目结构详解

### 核心配置文件
```
config/
├── env.py              # 环境配置管理
├── database.py         # 数据库配置
├── get_db.py          # 数据库连接管理
├── get_redis.py       # Redis连接管理
├── get_scheduler.py    # 定时任务调度器
└── constant.py         # 系统常量定义
```

### 管理模块 (module_admin)
```
module_admin/
├── controller/         # 控制器层 - HTTP请求处理
├── service/           # 服务层 - 业务逻辑处理
├── dao/               # 数据访问层 - 数据库操作
└── entity/            # 数据实体
    ├── do/            # 数据对象 (Data Object)
    └── vo/            # 视图对象 (View Object)
```

### 代码生成模块 (module_generator)
```
module_generator/
├── controller/         # 控制器生成器
├── service/           # 服务层生成器
├── dao/               # DAO层生成器
├── entity/            # 实体生成器
└── templates/         # 代码模板
    ├── python/        # Python代码模板
    ├── vue/           # Vue前端模板
    ├── sql/           # SQL脚本模板
    └── js/            # JavaScript API模板
```

### 工具库 (utils)
```
utils/
├── common_util.py      # 通用工具函数
├── log_util.py        # 日志工具
├── response_util.py    # 响应工具
├── time_format_util.py # 时间格式化工具
├── string_util.py      # 字符串处理工具
├── excel_util.py      # Excel处理工具
├── upload_util.py     # 文件上传工具
└── pwd_util.py        # 密码工具
```

## API接口规范

### 统一响应格式
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": null,
    "timestamp": "2024-01-01T12:00:00"
}
```

### HTTP状态码
- **200** - 成功
- **201** - 创建成功
- **400** - 请求参数错误
- **401** - 未授权
- **403** - 禁止访问
- **404** - 资源不存在
- **500** - 服务器内部错误

### 分页查询参数
```json
{
    "pageNum": 1,
    "pageSize": 10,
    "orderByColumn": "createTime",
    "isAsc": "desc"
}
```

### 分页响应格式
```json
{
    "code": 200,
    "msg": "查询成功",
    "data": {
        "total": 100,
        "rows": [...],
        "pageNum": 1,
        "pageSize": 10
    }
}
```

## 权限控制

### JWT认证
- 基于JWT的无状态认证
- 支持Token刷新
- 可配置的过期时间

### 权限验证
- 基于角色的访问控制 (RBAC)
- 菜单权限控制
- 数据权限控制
- 接口权限控制

### 权限注解
```python
@require_permissions(["system:user:list"])
async def get_user_list(self):
    pass

@require_data_scope("dept")
async def get_dept_list(self):
    pass
```

## 数据库设计

### 核心表结构
- **sys_user** - 用户表
- **sys_role** - 角色表
- **sys_menu** - 菜单表
- **sys_dept** - 部门表
- **sys_dict** - 字典表
- **sys_config** - 配置表
- **sys_log** - 日志表

### 数据库特性
- 支持MySQL和PostgreSQL
- 异步数据库操作
- 连接池管理
- 事务支持
- 数据权限控制

## 代码生成

### 生成流程
1. **表结构分析** - 自动分析数据库表结构
2. **代码生成** - 生成完整的CRUD代码
3. **模板定制** - 支持自定义代码模板
4. **批量生成** - 支持多表同时生成

### 生成内容
- 后端：Controller、Service、DAO、Entity
- 前端：Vue3页面、API接口、表单组件
- 数据库：建表脚本、索引优化

### 使用方式
```python
# 通过代码生成器生成代码
gen_service = GenService()
await gen_service.generate_code(table_name="sys_user")
```

## 定时任务

### 任务类型
- **Cron任务** - 基于Cron表达式的定时任务
- **间隔任务** - 固定时间间隔执行的任务
- **一次性任务** - 指定时间执行一次的任务

### 任务管理
- 动态添加/删除任务
- 任务执行状态监控
- 执行日志记录
- 异常处理和重试

### 示例配置
```python
# Cron表达式示例
"0 0 12 * * ?"      # 每天中午12点执行
"0 15 10 ? * *"     # 每天上午10:15执行
"0 15 10 * * ?"     # 每天上午10:15执行
```

## 日志系统

### 日志级别
- **DEBUG** - 调试信息
- **INFO** - 一般信息
- **WARNING** - 警告信息
- **ERROR** - 错误信息
- **CRITICAL** - 严重错误

### 日志内容
- 操作日志 - 用户操作记录
- 登录日志 - 用户登录记录
- 系统日志 - 系统运行日志
- 错误日志 - 异常和错误记录

### 日志配置
```python
# 日志配置示例
logger.add(
    "logs/app.log",
    rotation="100 MB",
    retention="30 days",
    level="INFO"
)
```

## 缓存策略

### Redis缓存
- 用户会话缓存
- 系统配置缓存
- 字典数据缓存
- 接口响应缓存

### 缓存管理
- 缓存过期策略
- 缓存更新机制
- 缓存穿透防护
- 缓存雪崩防护

## 部署说明

### 开发环境
```bash
# 开发模式启动
python app.py
```

### 生产环境
```bash
# 使用Gunicorn启动
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker

# 使用Docker部署
docker build -t ruoyi-fastapi .
docker run -p 9099:9099 ruoyi-fastapi
```

### 环境变量配置
```bash
# 生产环境配置
export APP_ENV=prod
export DB_HOST=prod-db-host
export REDIS_HOST=prod-redis-host
```

## 性能优化

### 数据库优化
- 索引优化
- 查询优化
- 连接池配置
- 读写分离

### 应用优化
- 异步处理
- 缓存策略
- 代码优化
- 资源管理

### 监控指标
- 响应时间
- 吞吐量
- 错误率
- 资源使用率

## 安全特性

### 认证安全
- JWT令牌加密
- 密码哈希存储
- 会话管理
- 登录限制

### 数据安全
- SQL注入防护
- XSS攻击防护
- CSRF防护
- 数据加密

### 接口安全
- 接口限流
- 权限验证
- 参数验证
- 异常处理

## 开发规范

### 代码风格
- 遵循PEP 8规范
- 使用类型注解
- 编写文档字符串
- 代码注释规范

### 命名规范
- 类名：大驼峰命名法 (PascalCase)
- 函数名：小写+下划线 (snake_case)
- 变量名：小写+下划线 (snake_case)
- 常量名：大写+下划线 (UPPER_SNAKE_CASE)

### 错误处理
- 统一异常处理
- 详细错误信息
- 错误日志记录
- 用户友好提示

## 测试指南

### 单元测试
```bash
# 运行测试
pytest tests/

# 生成覆盖率报告
pytest --cov=app tests/
```

### 接口测试
- 使用FastAPI自动生成的文档
- Postman接口测试
- 自动化测试脚本

### 性能测试
- 压力测试
- 负载测试
- 性能监控

## 常见问题

### Q: 如何修改数据库配置？
A: 在 `config/env.py` 文件中修改数据库相关配置，或通过环境变量设置。

### Q: 如何添加新的业务模块？
A: 使用代码生成器生成基础代码，然后根据业务需求进行定制。

### Q: 如何配置定时任务？
A: 在 `module_task` 模块中添加任务逻辑，通过调度器进行管理。

### Q: 如何扩展权限系统？
A: 在 `module_admin` 模块中添加新的权限项，配置相应的菜单和按钮权限。

## 贡献指南

### 开发流程
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

### 代码审查
- 代码质量检查
- 功能测试验证
- 性能影响评估
- 安全风险评估

## 版本历史

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础功能模块
- 用户权限管理
- 代码生成功能

## 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 联系方式

- 项目维护者：insistence
- 项目地址：[GitHub Repository]
- 问题反馈：[Issues]
- 技术交流：[Discussions]

---

**注意**：本文档会随着项目发展持续更新，请关注最新版本。 