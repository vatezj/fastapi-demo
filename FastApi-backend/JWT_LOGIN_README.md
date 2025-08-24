# JWT 登录功能使用说明

## 🎯 功能概述

登录接口现在实现了完整的 JWT 认证功能，返回访问 token 和刷新 token，而不是直接返回用户信息。

## 🔑 JWT Token 配置

### Token 类型
- **Access Token**: 用于访问受保护的资源，30分钟过期
- **Refresh Token**: 用于刷新访问 token，7天过期

### 技术参数
- **算法**: HS256
- **密钥**: 从环境配置获取，默认使用 "your-secret-key-here"
- **过期时间**: 可配置

## 📍 API 接口

### 1. 用户登录

**接口**: `POST /app/v1/user/login`

**请求体**:
```json
{
  "userName": "faker",
  "password": "Hyx1234!",
  "code": "123456",
  "uuid": "string"
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "登录成功",
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "refresh_expires_in": 604800,
    "user_info": {
      "user_id": 1,
      "user_name": "faker",
      "nick_name": "测试用户",
      "email": "test@example.com",
      "phone": "13800138000",
      "sex": "0",
      "avatar": null,
      "status": "0",
      "login_ip": "127.0.0.1",
      "login_date": "2025-08-24T16:20:00"
    }
  }
}
```

### 2. 刷新 Token

**接口**: `POST /app/v1/user/refresh-token`

**请求体**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "token刷新成功",
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

## 🛠️ 实现细节

### 1. JWT 工具类 (`utils/jwt_util.py`)

提供完整的 JWT 操作功能：
- 创建访问 token 和刷新 token
- 验证 token 有效性
- 解码 token 内容
- 检查 token 过期状态
- 刷新访问 token

### 2. JWT 认证中间件 (`utils/jwt_auth.py`)

提供认证相关的依赖函数：
- `get_current_user`: 必需认证，获取当前用户信息
- `get_current_user_optional`: 可选认证，获取当前用户信息（如果提供token）
- `verify_token`: 同步验证 token
- `decode_token`: 同步解码 token

### 3. 登录服务更新

登录服务现在：
- 生成 JWT token 对
- 返回完整的认证信息
- 包含用户基本信息和 token 元数据

## 🔐 使用方式

### 1. 获取 Token

```bash
curl -X 'POST' \
  'http://localhost:9099/app/v1/user/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "userName": "faker",
  "password": "Hyx1234!",
  "code": "123456",
  "uuid": "string"
}'
```

### 2. 使用 Token 访问受保护资源

```bash
curl -X 'GET' \
  'http://localhost:9099/app/v1/user/profile' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
```

### 3. 刷新 Token

```bash
curl -X 'POST' \
  'http://localhost:9099/app/v1/user/refresh-token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}'
```

## 🔧 配置说明

### 环境变量配置

在环境配置文件中添加 JWT 相关配置：

```python
# config/env.py
class JWTConfig:
    jwt_secret_key: str = "your-secret-key-here"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
```

### 自定义配置

可以通过修改 `utils/jwt_util.py` 中的类变量来自定义配置：

```python
class JWTUtil:
    SECRET_KEY = "your-custom-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1小时
    REFRESH_TOKEN_EXPIRE_DAYS = 30    # 30天
```

## 📋 测试用例

### 测试脚本

运行 `test_jwt_login.py` 来验证 JWT 功能：

```bash
python test_jwt_login.py
```

### 手动测试步骤

1. **启动服务器**: `python start_app.py`
2. **注册用户**: 使用万能验证码 `123456` 注册测试用户
3. **测试登录**: 使用登录接口获取 token
4. **测试刷新**: 使用刷新 token 接口测试 token 刷新
5. **验证认证**: 使用 token 访问受保护的资源

## ⚠️ 注意事项

1. **Token 安全**: 不要在客户端存储敏感信息
2. **过期处理**: 客户端需要处理 token 过期情况
3. **刷新策略**: 建议在访问 token 过期前主动刷新
4. **HTTPS**: 生产环境建议使用 HTTPS 传输 token

## 🔍 故障排除

### 常见问题

1. **Token 过期**: 使用刷新 token 获取新的访问 token
2. **无效 Token**: 检查 token 格式和签名
3. **认证失败**: 确保在 Header 中正确设置 Authorization

### 调试工具

使用 JWT 工具类的方法来调试：

```python
from utils.jwt_util import JWTUtil

# 解码 token 查看内容
payload = JWTUtil.decode_token(token)
print(payload)

# 检查 token 是否过期
is_expired = JWTUtil.is_token_expired(token)
print(f"Token expired: {is_expired}")
```

## 📚 相关文件

- `utils/jwt_util.py` - JWT 工具类
- `utils/jwt_auth.py` - JWT 认证中间件
- `module_app/service/app_user_service.py` - 登录服务
- `module_app/controller/app_user_controller.py` - 登录控制器
- `test_jwt_login.py` - 测试脚本
- `JWT_LOGIN_README.md` - 本文档

## 🎉 总结

JWT 登录功能现在已经完全实现，提供了：
- 完整的 token 认证机制
- 访问 token 和刷新 token 支持
- 灵活的认证中间件
- 完整的测试和文档

现在您的登录接口应该能够正确返回 JWT token 对，为后续的认证和授权功能提供基础！ 