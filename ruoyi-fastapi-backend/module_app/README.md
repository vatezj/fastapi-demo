# APP 模块

## 概述

APP 模块是专门为移动端应用提供接口服务的模块，包含用户管理、认证授权、登录日志等功能。

## 模块特性

- ✅ 完整的用户管理系统（无角色设计）
- ✅ 用户认证和授权
- ✅ 用户档案管理
- ✅ 登录日志记录
- ✅ 短信验证码支持
- ✅ 密码加密和验证

## 文档访问地址

### APP 模块文档
- **Swagger UI**: `http://127.0.0.1:9099/app/docs`
- **ReDoc**: `http://127.0.0.1:9099/app/redoc`
- **OpenAPI JSON**: `http://127.0.0.1:9099/app/openapi.json`

## 模块架构

### 1. 控制器层 (Controller)
- `app_user_controller.py` - APP用户管理控制器
- `auth_controller.py` - 认证授权控制器
- `user_controller.py` - 基础用户控制器

### 2. 服务层 (Service)
- `app_user_service.py` - APP用户业务逻辑
- `base_service.py` - 基础服务
- `user_service.py` - 用户服务

### 3. 数据访问层 (DAO)
- `app_user_dao.py` - APP用户数据访问
- `base_dao.py` - 基础数据访问
- `user_dao.py` - 用户数据访问

### 4. 实体层 (Entity)
- **数据对象 (DO)**:
  - `app_user_do.py` - APP用户数据对象
- **视图对象 (VO)**:
  - `app_user_vo.py` - APP用户视图对象

## 数据库设计

### 1. APP用户信息表 (`app_user`)
```sql
- user_id: 用户ID (主键)
- user_name: 用户账号 (唯一)
- nick_name: 用户昵称
- email: 用户邮箱
- phone: 手机号码
- sex: 用户性别 (0男 1女 2未知)
- avatar: 用户头像
- password: 密码 (加密存储)
- status: 帐号状态 (0正常 1停用)
- login_ip: 最后登录IP
- login_date: 最后登录时间
- create_by: 创建者
- create_time: 创建时间
- update_by: 更新者
- update_time: 更新时间
- remark: 备注
```

### 2. APP用户详细信息表 (`app_user_profile`)
```sql
- profile_id: 详细信息ID (主键)
- user_id: 用户ID (外键)
- real_name: 真实姓名
- id_card: 身份证号
- birthday: 出生日期
- address: 居住地址
- education: 学历
- occupation: 职业
- income_level: 收入水平
- marital_status: 婚姻状况
- emergency_contact: 紧急联系人
- emergency_phone: 紧急联系电话
- create_time: 创建时间
- update_time: 更新时间
```

### 3. APP登录日志表 (`app_login_log`)
```sql
- log_id: 访问ID (主键)
- user_name: 用户账号
- ipaddr: 登录IP地址
- login_location: 登录地点
- browser: 浏览器类型
- os: 操作系统
- status: 登录状态 (0成功 1失败)
- msg: 提示消息
- login_time: 访问时间
```

## API 接口结构

```
/app                    - APP模块根路径
├── /docs              - APP接口文档
├── /redoc             - APP ReDoc文档
├── /openapi.json      - APP OpenAPI
└── /v1                - API版本1
    ├── /auth          - 认证接口
    ├── /user          - 用户接口
    └── /user          - APP用户管理
        ├── /list              - 获取用户列表
        ├── /{user_id}         - 获取用户详情
        ├── /add               - 新增用户
        ├── /edit              - 编辑用户
        ├── /delete            - 删除用户
        ├── /status            - 修改用户状态
        ├── /reset-password    - 重置密码
        ├── /login             - 用户登录
        ├── /register          - 用户注册
        ├── /send-sms          - 发送短信验证码
        ├── /login-log/list    - 获取登录日志
        ├── /login-log/delete  - 删除登录日志
        └── /login-log/clean   - 清理登录日志
```

## 主要功能模块

### 1. 用户管理
- **用户创建**: 支持基础信息和详细信息的创建
- **用户编辑**: 支持基础信息和详细信息的编辑
- **用户删除**: 支持单个和批量删除
- **状态管理**: 启用/停用用户账号
- **密码重置**: 管理员重置用户密码

### 2. 用户认证
- **用户登录**: 用户名密码登录
- **用户注册**: 新用户注册
- **短信验证**: 短信验证码支持
- **登录记录**: 记录登录IP、时间、设备信息

### 3. 登录日志
- **日志记录**: 记录所有登录尝试
- **日志查询**: 支持多条件查询和分页
- **日志清理**: 支持定期清理过期日志
- **安全监控**: 监控异常登录行为

## 技术特点

### 1. 无角色设计
- 简化权限管理，适合移动端应用
- 用户权限通过业务逻辑控制
- 减少系统复杂度

### 2. 数据安全
- 密码加密存储
- 输入验证和过滤
- SQL注入防护
- XSS攻击防护

### 3. 性能优化
- 异步处理
- 数据库连接池
- 分页查询
- 索引优化

### 4. 日志记录
- 完整的登录日志
- 操作审计
- 安全监控
- 问题排查

## 配置说明

### APP模块配置
```python
app_app = FastAPI(
    title=f'{AppConfig.app_name} - APP接口',
    description=f'{AppConfig.app_name}移动端APP接口文档 - 面向移动端开发者',
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
)
```

### 主应用挂载
```python
# 挂载APP模块应用
app.mount("/app", app_app, name="app_module")
```

## 使用说明

### 1. 访问文档
- 访问 `http://127.0.0.1:9099/app/docs` 查看完整的 API 文档
- 使用 Swagger UI 进行接口测试
- 查看 ReDoc 格式的文档

### 2. 接口调用
- 所有APP接口都以 `/app` 开头
- 遵循 RESTful API 设计规范
- 支持标准的 HTTP 状态码

### 3. 认证方式
- 支持用户名密码登录
- 支持短信验证码
- 登录成功后返回用户信息

### 4. 数据格式
- 请求和响应都使用 JSON 格式
- 支持分页查询
- 统一的响应格式

## 开发指南

### 1. 添加新接口
1. 在对应的控制器中添加路由
2. 在服务层实现业务逻辑
3. 在DAO层实现数据访问
4. 更新API文档

### 2. 数据验证
1. 使用Pydantic模型进行数据验证
2. 在服务层进行业务规则验证
3. 在DAO层进行数据完整性检查

### 3. 错误处理
1. 使用统一的响应格式
2. 记录详细的错误日志
3. 返回用户友好的错误信息

## 部署说明

### 1. 环境要求
- Python 3.8+
- FastAPI
- SQLAlchemy
- PostgreSQL/MySQL

### 2. 配置项
- 数据库连接配置
- Redis配置（可选）
- 短信服务配置
- 日志配置

### 3. 启动命令
```bash
# 开发环境
uvicorn server:app --reload --host 0.0.0.0 --port 9099

# 生产环境
uvicorn server:app --host 0.0.0.0 --port 9099 --workers 4
```

## 注意事项

1. **安全性**: 所有接口都需要进行适当的权限验证
2. **性能**: 大量数据查询时建议使用分页和缓存
3. **日志**: 重要操作需要记录详细的操作日志
4. **备份**: 定期备份用户数据和日志数据
5. **监控**: 监控接口性能和异常情况

## 扩展建议

1. **缓存**: 可以集成Redis缓存提高性能
2. **消息队列**: 可以集成消息队列处理异步任务
3. **文件存储**: 可以集成对象存储服务
4. **推送服务**: 可以集成推送通知服务
5. **统计分析**: 可以集成数据分析服务

## 技术支持

如有问题，请联系开发团队或查看相关文档。
