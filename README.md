# FastApiAadmin-vue 全栈管理系统

## 项目概述

FastApiAadmin-vue 是一个基于 FastAPI + Vue.js 的现代化全栈管理系统，采用前后端分离架构，提供完整的用户权限管理、系统监控、代码生成等功能。项目支持模块化开发，具备良好的扩展性和维护性。

## 项目架构

```
FastApiAadmin-vue/
├── FastApi-backend/          # FastAPI 后端服务
│   ├── app.py               # 主应用入口
│   ├── module_admin/        # 系统管理模块
│   ├── module_app/          # APP应用模块
│   ├── module_generator/    # 代码生成模块
│   └── shared/              # 共享基础模块
├── FastApi-admin/           # Vue.js 前端应用
│   ├── src/                 # 前端源代码
│   ├── public/              # 静态资源
│   └── vite.config.js       # 构建配置
└── docs/                    # 项目文档
```

## 技术栈

### 后端技术
- **Web 框架**: FastAPI
- **数据库**: SQLAlchemy (异步) + PostgreSQL/MySQL
- **缓存**: Redis
- **任务调度**: APScheduler
- **权限控制**: JWT + RBAC
- **代码生成**: 模块化代码生成器

### 前端技术
- **前端框架**: Vue 3 + Composition API
- **UI 组件库**: Element Plus
- **路由管理**: Vue Router 4
- **状态管理**: Vuex 4
- **构建工具**: Vite
- **样式预处理**: SCSS

## 核心特性

### 1. 模块化架构
- **后端模块**: admin、app、business、generator
- **前端模块**: 按功能划分的组件和页面
- **代码生成**: 支持多种模块类型的代码生成

### 2. 权限管理系统
- **用户认证**: JWT Token 认证
- **角色管理**: 基于角色的权限控制 (RBAC)
- **菜单权限**: 动态菜单加载
- **数据权限**: 细粒度的数据访问控制

### 3. 系统监控
- **在线用户**: 实时用户会话监控
- **操作日志**: 完整的操作审计记录
- **系统性能**: 服务器资源监控
- **缓存状态**: Redis 缓存监控

### 4. 代码生成器
- **表结构生成**: 根据数据库表自动生成代码
- **模块化生成**: 支持多种模块类型和前端框架
- **模板定制**: 可自定义的代码模板
- **批量生成**: 支持多表同时生成

## 快速开始

### 环境要求

- **后端**: Python 3.8+, PostgreSQL 12+/MySQL 8.0+, Redis 6.0+
- **前端**: Node.js 16+, pnpm 7+

### 1. 克隆项目

```bash
git clone <repository-url>
cd FastApiAadmin-vue
```

### 2. 后端启动

```bash
cd FastApi-backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp config/env.py.example config/env.py
# 编辑 config/env.py 配置数据库连接

# 启动后端服务
python start_app.py
```

后端服务将在 `http://localhost:8000` 启动

### 3. 前端启动

```bash
cd FastApi-admin

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

前端应用将在 `http://localhost:3000` 启动

### 4. 访问系统

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **代码生成器**: http://localhost:8000/tool/gen

## 功能模块

### 系统管理 (module_admin)
- **用户管理**: 用户增删改查、角色分配、状态管理
- **角色管理**: 角色定义、权限分配、数据范围
- **菜单管理**: 动态菜单、权限控制、路由管理
- **部门管理**: 组织架构、部门层级、数据权限
- **字典管理**: 系统字典、数据枚举、配置管理
- **参数配置**: 系统参数、环境配置、动态配置

### APP应用 (module_app)
- **用户管理**: APP用户信息管理
- **登录日志**: 用户登录记录
- **用户档案**: 用户详细信息管理

### 监控管理 (monitor)
- **在线用户**: 实时用户会话监控
- **操作日志**: 用户操作审计记录
- **登录日志**: 登录历史和安全分析
- **服务监控**: 系统性能和资源监控
- **缓存监控**: Redis 缓存状态和性能

### 工具管理 (tool)
- **代码生成**: 表结构代码生成
- **模块化生成**: 支持多种模块类型的代码生成
- **Swagger**: API 接口文档

## 开发指南

### 后端开发

1. **模块开发**: 遵循 Controller → Service → DAO → Entity 的分层架构
2. **权限控制**: 使用 `@CheckUserInterfaceAuth` 和 `@CheckRoleInterfaceAuth` 装饰器
3. **代码生成**: 使用模块化代码生成器快速创建新模块
4. **异步编程**: 使用 `async/await` 语法进行异步操作

### 前端开发

1. **组件开发**: 使用 Vue 3 Composition API 开发组件
2. **权限控制**: 使用 `v-hasPermi` 和 `v-hasRole` 指令
3. **状态管理**: 使用 Vuex 管理应用状态
4. **路由管理**: 配置动态路由和权限验证

### 代码生成

1. **访问生成器**: http://localhost:8000/tool/gen
2. **选择模块类型**: admin、app、business
3. **配置生成参数**: 表名、模块名、前端框架等
4. **生成代码**: 自动生成前后端代码

## API 接口

### 认证接口
- `POST /auth/login` - 用户登录
- `POST /auth/logout` - 用户登出
- `GET /auth/profile` - 获取用户信息

### 用户管理接口
- `GET /system/user/list` - 获取用户列表
- `POST /system/user` - 创建用户
- `PUT /system/user` - 更新用户
- `DELETE /system/user/{ids}` - 删除用户

### 代码生成接口
- `GET /tool/gen/modules/supported` - 获取支持的模块类型
- `GET /tool/gen/modules/config/{module_type}` - 获取模块配置模板
- `POST /tool/gen/modules/generate` - 生成模块化代码

## 部署说明

### 开发环境
- 使用 `python start_app.py` 启动后端
- 使用 `pnpm dev` 启动前端

### 生产环境
- 使用 Gunicorn 部署后端服务
- 使用 Nginx 部署前端静态文件
- 配置 HTTPS 和反向代理

### Docker 部署
```bash
# 构建镜像
docker build -t fastapi-admin .

# 运行容器
docker run -p 8000:8000 fastapi-admin
```

## 项目结构详解

### 后端结构
```
FastApi-backend/
├── app.py                          # 主应用入口
├── config/                         # 配置文件
│   ├── env.py                      # 环境配置
│   ├── database.py                 # 数据库配置
│   └── constant.py                 # 常量定义
├── module_admin/                   # 系统管理模块
│   ├── controller/                 # 控制器层
│   ├── service/                    # 服务层
│   ├── dao/                        # 数据访问层
│   ├── entity/                     # 实体层
│   └── aspect/                     # 切面编程
├── module_app/                     # APP应用模块
├── module_generator/               # 代码生成模块
├── shared/                         # 共享基础模块
├── utils/                          # 工具函数
└── middlewares/                    # 中间件
```

### 前端结构
```
FastApi-admin/
├── src/
│   ├── api/                        # API 接口定义
│   ├── components/                 # 公共组件
│   ├── layout/                     # 布局组件
│   ├── router/                     # 路由配置
│   ├── store/                      # 状态管理
│   ├── utils/                      # 工具函数
│   └── views/                      # 页面组件
├── public/                         # 静态资源
└── vite.config.js                  # 构建配置
```

## 配置说明

### 环境变量
```bash
# 应用配置
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379/0

# JWT配置
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRE_MINUTES=1440
```

### 数据库配置
- 支持 PostgreSQL 和 MySQL
- 异步数据库操作
- 连接池管理
- 事务支持

## 性能优化

### 后端优化
- 异步编程提高并发性能
- Redis 缓存减少数据库查询
- 数据库连接池优化
- 代码生成提高开发效率

### 前端优化
- 路由懒加载减少首屏加载时间
- 组件缓存优化页面切换性能
- 代码分割减少包体积
- 图片懒加载优化资源加载

## 安全特性

### 认证安全
- JWT Token 认证
- 密码加密存储
- 登录失败限制
- 会话管理

### 权限安全
- 基于角色的权限控制
- 接口级别权限验证
- 数据范围权限控制
- SQL 注入防护

### 数据安全
- 敏感数据加密
- 数据传输加密
- 操作日志记录
- 异常监控告警

## 监控与日志

### 日志系统
- 结构化日志格式
- 多级别日志记录
- 日志文件轮转
- 错误日志告警

### 性能监控
- 接口响应时间监控
- 数据库查询性能监控
- 系统资源使用监控
- 缓存命中率监控

## 测试指南

### 后端测试
```bash
# 运行单元测试
python -m pytest tests/

# 运行特定模块测试
python -m pytest tests/module_admin/
```

### 前端测试
```bash
# 运行单元测试
pnpm test

# 生成覆盖率报告
pnpm test:coverage
```

### API 测试
- 使用 Swagger 文档进行接口测试
- 使用 Postman 进行接口调试
- 编写自动化测试脚本

## 常见问题

### 1. 启动问题
- **后端启动失败**: 检查数据库连接和 Redis 连接
- **前端启动失败**: 检查 Node.js 版本和依赖安装
- **端口占用**: 修改配置文件中的端口号

### 2. 权限问题
- **登录失败**: 检查用户名密码和数据库连接
- **权限不足**: 检查用户角色和权限配置
- **菜单不显示**: 检查菜单权限和路由配置

### 3. 代码生成问题
- **生成失败**: 检查表结构和配置参数
- **模板错误**: 检查模板文件和变量配置
- **路径问题**: 检查输出路径和文件权限

## 贡献指南

### 开发流程
1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 (Python) 和 ESLint (JavaScript) 规范
- 添加适当的注释和文档
- 编写测试用例
- 保持代码简洁和可读性

### 提交规范
- 使用语义化提交信息
- 添加测试用例
- 更新相关文档
- 说明功能变更

## 版本历史

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础功能模块
- 用户权限管理
- 代码生成功能

### v1.1.0 (计划中)
- 模块化架构优化
- 更多前端框架支持
- 性能优化
- 安全增强

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 联系方式

- **项目维护者**: insistence
- **项目地址**: [GitHub Repository]
- **问题反馈**: [Issues]
- **技术交流**: [Discussions]

## 致谢

感谢所有为项目做出贡献的开发者和用户。

---

**注意**: 本文档会随着项目发展持续更新，请关注最新版本。