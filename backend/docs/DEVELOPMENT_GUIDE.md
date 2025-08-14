# RuoYi-FastAPI 开发指南

## 概述

本文档是 RuoYi-FastAPI 项目的开发指南，为开发者提供完整的开发流程、规范和实践指导。

## 目录

- [快速开始](./QUICK_START.md) - 项目搭建和基础配置
- [架构设计](./ARCHITECTURE.md) - 系统架构和设计模式
- [API开发](./API_DEVELOPMENT.md) - API接口开发规范
- [数据库开发](./DATABASE_DEVELOPMENT.md) - 数据库设计和操作
- [权限系统](./PERMISSION_SYSTEM.md) - 权限控制和认证
- [代码生成](./CODE_GENERATION.md) - 代码生成器使用
- [定时任务](./SCHEDULER_TASKS.md) - 定时任务开发
- [测试指南](./TESTING_GUIDE.md) - 测试策略和实现
- [部署运维](./DEPLOYMENT.md) - 部署和运维指南
- [性能优化](./PERFORMANCE.md) - 性能优化策略

## 开发环境要求

### 基础环境
- Python 3.8+
- MySQL 5.7+ 或 PostgreSQL 10+
- Redis 6.0+
- Git

### 开发工具推荐
- **IDE**: PyCharm Professional / VS Code
- **数据库工具**: Navicat / DBeaver
- **API测试**: Postman / Insomnia
- **版本控制**: Git + GitLab/GitHub

## 开发流程

### 1. 需求分析
- 理解业务需求
- 设计数据模型
- 定义API接口
- 确定权限要求

### 2. 数据库设计
- 设计表结构
- 定义字段类型和约束
- 创建索引
- 编写建表脚本

### 3. 代码生成
- 使用代码生成器生成基础代码
- 根据业务需求定制代码
- 添加业务逻辑
- 实现权限控制

### 4. 功能开发
- 实现业务逻辑
- 编写单元测试
- 进行代码审查
- 集成测试

### 5. 部署测试
- 部署到测试环境
- 功能测试验证
- 性能测试
- 安全测试

## 开发规范

### 代码风格
- 遵循 PEP 8 规范
- 使用类型注解
- 编写文档字符串
- 保持代码简洁

### 命名规范
```python
# 类名：大驼峰命名法
class UserService:
    pass

# 函数名：小写+下划线
async def get_user_by_id(user_id: int):
    pass

# 变量名：小写+下划线
user_name = "admin"

# 常量名：大写+下划线
MAX_RETRY_COUNT = 3
```

### 文件组织
```
module_name/
├── __init__.py
├── controller/
│   ├── __init__.py
│   └── entity_controller.py
├── service/
│   ├── __init__.py
│   └── entity_service.py
├── dao/
│   ├── __init__.py
│   └── entity_dao.py
└── entity/
    ├── __init__.py
    ├── do/
    │   └── entity_do.py
    └── vo/
        └── entity_vo.py
```

## 版本控制

### Git 工作流
1. **主分支**: `main` - 生产环境代码
2. **开发分支**: `develop` - 开发环境代码
3. **功能分支**: `feature/功能名称` - 新功能开发
4. **修复分支**: `hotfix/问题描述` - 紧急问题修复

### 提交规范
```bash
# 提交格式
<type>(<scope>): <subject>

# 类型说明
feat:     新功能
fix:      修复bug
docs:     文档更新
style:    代码格式调整
refactor: 代码重构
test:     测试相关
chore:    构建过程或辅助工具的变动

# 示例
feat(user): 添加用户注册功能
fix(auth): 修复JWT过期时间问题
docs(api): 更新API文档
```

## 代码审查

### 审查要点
- 代码质量和可读性
- 业务逻辑正确性
- 性能影响评估
- 安全风险评估
- 测试覆盖率

### 审查流程
1. 开发者提交 Pull Request
2. 代码审查者进行代码审查
3. 发现问题时要求修改
4. 审查通过后合并代码

## 测试策略

### 测试类型
- **单元测试**: 测试单个函数或方法
- **集成测试**: 测试模块间交互
- **接口测试**: 测试API接口功能
- **性能测试**: 测试系统性能指标

### 测试工具
- **pytest**: 单元测试框架
- **pytest-asyncio**: 异步测试支持
- **pytest-cov**: 测试覆盖率
- **httpx**: HTTP客户端测试

## 性能考虑

### 数据库优化
- 合理使用索引
- 避免N+1查询
- 使用连接池
- 读写分离

### 缓存策略
- Redis缓存热点数据
- 合理设置过期时间
- 避免缓存穿透
- 实现缓存预热

### 异步处理
- 使用异步数据库操作
- 异步任务处理
- 并发控制
- 资源管理

## 安全考虑

### 认证授权
- JWT令牌安全
- 密码加密存储
- 会话管理
- 权限验证

### 数据安全
- SQL注入防护
- XSS攻击防护
- CSRF防护
- 敏感数据加密

### 接口安全
- 参数验证
- 接口限流
- 异常处理
- 日志记录

## 监控和日志

### 系统监控
- 性能指标监控
- 错误率监控
- 资源使用监控
- 业务指标监控

### 日志记录
- 操作日志
- 错误日志
- 性能日志
- 安全日志

## 常见问题

### Q: 如何添加新的业务模块？
A: 参考现有模块结构，使用代码生成器生成基础代码，然后根据业务需求进行定制。

### Q: 如何处理数据库事务？
A: 在Service层使用 `async with db.begin()` 管理事务，确保数据一致性。

### Q: 如何实现权限控制？
A: 使用装饰器 `@require_permissions` 和 `@require_data_scope` 实现接口权限和数据权限控制。

### Q: 如何优化查询性能？
A: 合理使用索引，避免N+1查询，使用分页查询，实现数据缓存。

## 学习资源

### 官方文档
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [Pydantic 官方文档](https://pydantic-docs.helpmanual.io/)

### 最佳实践
- [Python 异步编程](https://docs.python.org/3/library/asyncio.html)
- [REST API 设计指南](https://restfulapi.net/)
- [数据库设计原则](https://www.guru99.com/database-design.html)

---

**注意**: 本文档会持续更新，请关注最新版本。如有问题，请通过 Issues 反馈。 