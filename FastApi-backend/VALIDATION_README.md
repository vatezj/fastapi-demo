# 用户注册验证功能说明

## 概述

本系统为 `app/v1/user/register` 接口添加了完整的验证功能，包括：

- 密码强度验证
- 邮箱格式验证
- 手机号格式验证
- 图形验证码验证
- 用户名格式验证

## 验证规则

### 1. 密码验证

#### 基本要求
- 长度：至少8位，建议12位以上
- 字符类型：必须包含以下四种字符
  - 小写字母 (a-z)
  - 大写字母 (A-Z)
  - 数字 (0-9)
  - 特殊字符 (@$!%*?&)

#### 强度评分
- **弱密码** (0-2分)：不满足基本要求
- **中等密码** (3-4分)：满足基本要求
- **强密码** (5-6分)：满足基本要求且长度足够

#### 禁止的密码模式
- 常见弱密码：123456, password, qwerty, admin等
- 连续重复字符：aaa, 111等
- 键盘序列：qwerty, asdfgh等

### 2. 邮箱验证

#### 格式要求
- 基本格式：`username@domain.tld`
- 用户名长度：不超过64字符
- 域名长度：不超过253字符
- 总长度：不超过254字符

#### 字符限制
- 用户名：允许字母、数字、点号、下划线、连字符、加号、百分号
- 域名：只允许字母、数字、连字符
- 禁止特殊字符：<>"'等

#### 格式检查
- 不能以点号开头或结尾
- 不能包含连续点号
- 顶级域名至少2个字符

### 3. 手机号验证

#### 基本要求
- 长度：11位数字
- 开头：必须以1开头
- 第二位：3-9之间的数字

#### 运营商号段
- **中国移动**：134-139, 147, 150-152, 157-159, 178, 182-184, 187-188, 198
- **中国联通**：130-132, 145, 155-156, 166, 175-176, 185-186
- **中国电信**：133, 149, 153, 173, 177, 180-181, 189, 199
- **虚拟运营商**：170-171

#### 格式检查
- 自动清理非数字字符
- 检查连续重复数字
- 检查连续数字序列

### 4. 用户名验证

#### 格式要求
- 长度：3-30个字符
- 字符类型：只允许字母、数字、下划线
- 禁止特殊字符：空格、标点符号等

### 5. 验证码验证

#### 图形验证码
- 长度：4位字符
- 字符类型：大写字母和数字
- 有效期：5分钟
- 存储：Redis存储，验证后自动删除

## API接口

### 获取验证码
```
GET /app/v1/user/captcha
```

**响应示例：**
```json
{
  "code": 200,
  "message": "获取验证码成功",
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "expire_seconds": 300
  }
}
```

### 用户注册
```
POST /app/v1/user/register
```

**请求参数：**
```json
{
  "userName": "testuser",
  "nickName": "测试用户",
  "email": "test@example.com",
  "phone": "13800138000",
  "password": "MyPassword123!",
  "confirmPassword": "MyPassword123!",
  "code": "A1B2",
  "uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

## 工具类

### 1. PasswordValidator
密码强度验证器，提供：
- 密码强度评估
- 密码要求说明
- 强密码生成

### 2. ContactValidator
联系方式验证器，提供：
- 邮箱格式验证
- 手机号格式验证
- 脱敏处理

### 3. CaptchaUtil
验证码工具，提供：
- 图形验证码生成
- 验证码存储和验证
- UUID生成

## 使用示例

### 密码验证
```python
from utils.password_validator import PasswordValidator

# 验证密码强度
result = PasswordValidator.validate_password_strength("MyPassword123!")
if result['is_valid']:
    print(f"密码强度: {result['strength']}")
else:
    print(f"密码错误: {result['errors']}")

# 生成强密码
strong_pwd = PasswordValidator.generate_strong_password(16)
```

### 联系方式验证
```python
from utils.contact_validator import ContactValidator

# 验证邮箱
email_result = ContactValidator.validate_email("test@example.com")
if email_result['is_valid']:
    print("邮箱格式正确")

# 验证手机号
phone_result = ContactValidator.validate_phone("13800138000")
if phone_result['is_valid']:
    print(f"格式化手机号: {phone_result['formatted']}")

# 脱敏处理
masked_email = ContactValidator.mask_email("test@example.com")
masked_phone = ContactValidator.mask_phone("13800138000")
```

### 验证码处理
```python
from utils.captcha_util import CaptchaUtil
import uuid

# 生成验证码
uuid_str = str(uuid.uuid4())
result = await CaptchaUtil.generate_and_store_captcha(uuid_str)

# 验证验证码
is_valid = await CaptchaUtil.verify_captcha_code(uuid_str, "A1B2")
```

## 测试

运行测试文件验证所有功能：
```bash
python test_validation.py
```

## 注意事项

1. **生产环境**：验证码接口不应返回验证码内容，只返回图片
2. **Redis依赖**：验证码功能需要Redis服务
3. **图片字体**：验证码生成需要系统字体支持
4. **密码策略**：可根据业务需求调整密码强度要求
5. **验证码有效期**：可根据安全需求调整过期时间

## 错误处理

所有验证失败都会返回详细的错误信息，包括：
- 具体的错误原因
- 改进建议
- 警告信息（不影响注册但建议改进）

## 安全特性

1. **密码强度**：强制要求复杂密码
2. **验证码**：防止自动化攻击
3. **输入验证**：防止恶意输入
4. **脱敏处理**：保护用户隐私
5. **Redis存储**：验证码安全存储 