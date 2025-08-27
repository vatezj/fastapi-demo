# 测试目录结构

本目录包含了项目的所有测试文件，按功能模块进行分类组织。

## 📁 目录结构

```
tests/
├── __init__.py                 # 测试包初始化文件
├── README.md                   # 本说明文档
├── run_tests.py                # 测试运行脚本
├── account/                    # 账户相关测试
│   ├── __init__.py
│   ├── test_account_creation_fix.py
│   └── test_task_publish_fix.py
├── auth/                       # 认证相关测试
│   ├── __init__.py
│   ├── test_jwt_fix.py
│   ├── test_jwt_login.py
│   ├── test_login_fix.py
│   ├── test_login_greenlet_fix.py
│   └── test_simplified_login.py
├── database/                   # 数据库相关测试
│   ├── __init__.py
│   ├── test_db_session_fix.py
│   └── test_getinfo_error.py
├── validation/                 # 验证相关测试
│   ├── __init__.py
│   ├── test_captcha_simple.py
│   ├── test_universal_captcha.py
│   └── test_validation.py
├── yozuan/                     # Yozuan 模块测试
│   ├── __init__.py
│   ├── test_yozuan_complete.py
│   ├── test_yozuan_module.py
│   ├── test_yozuan_permissions.py
│   └── test_yozuan_simple.py
├── general/                    # 通用功能测试
│   ├── __init__.py
│   ├── test_exception_handling.py
│   ├── test_region_module.py
│   ├── test_register_flow.py
│   ├── test_routes.py
│   └── test_subapp_exception.py
└── module_app/                 # 应用模块测试
    └── test_admin_interface_controller.py
```

## 🚀 运行测试

### 使用测试运行脚本

```bash
# 查看所有可用的测试类别
python tests/run_tests.py --list

# 运行特定类别的测试
python tests/run_tests.py account
python tests/run_tests.py auth
python tests/run_tests.py database
python tests/run_tests.py validation
python tests/run_tests.py yozuan
python tests/run_tests.py general

# 运行所有测试
python tests/run_tests.py --all

# 查看帮助信息
python tests/run_tests.py --help
```

### 直接运行单个测试文件

```bash
# 使用 uv 运行（推荐）
uv run python tests/account/test_account_creation_fix.py

# 或者使用系统 Python
python tests/account/test_account_creation_fix.py
```

## 📋 测试类别说明

### account - 账户相关测试
- 账户创建和修复测试
- 任务发布相关测试

### auth - 认证相关测试
- JWT 认证测试
- 登录功能测试
- Greenlet 相关问题测试

### database - 数据库相关测试
- 数据库会话管理测试
- 数据库连接错误测试

### validation - 验证相关测试
- 验证码功能测试
- 数据验证测试

### yozuan - Yozuan 模块测试
- 完整功能测试
- 权限系统测试
- 模块基础功能测试

### general - 通用功能测试
- 异常处理测试
- 路由测试
- 注册流程测试

## 🔧 测试环境要求

- Python 3.8+
- uv 包管理器
- 项目依赖已安装

## 📝 添加新测试

1. 根据测试功能选择相应的类别目录
2. 创建测试文件，命名格式：`test_功能名称.py`
3. 在对应目录的 `__init__.py` 中添加必要的导入
4. 确保测试文件可以独立运行

## ⚠️ 注意事项

- 测试文件应该可以独立运行
- 避免测试之间的相互依赖
- 使用适当的模拟对象来隔离外部依赖
- 测试完成后及时清理测试数据 