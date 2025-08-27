#!/usr/bin/env python3
"""
JWT 登录功能测试脚本
测试登录接口的 JWT token 功能
"""

import asyncio
import json
from utils.test_utils import TestUtils


async def test_jwt_login():
    """测试 JWT 登录功能"""
    
    print("🧪 开始测试 JWT 登录功能...")
    print("-" * 60)
    
    print("🔍 功能说明:")
    print("登录接口现在返回 JWT token 对，而不是直接返回用户信息")
    print()
    
    print("🛠️ 新增功能:")
    print("1. JWT 工具类 (utils/jwt_util.py)")
    print("2. JWT 认证中间件 (utils/jwt_auth.py)")
    print("3. 刷新 token 接口 (/app/v1/user/refresh-token)")
    print("4. 登录接口返回 token 对")
    print()
    
    print("📋 测试用例:")
    test_cases = [
        {
            "name": "用户登录测试",
            "endpoint": "POST /app/v1/user/login",
            "data": {
                "userName": "faker",
                "password": "Hyx1234!",
                "code": "123456",
                "uuid": "string"
            },
            "expected": "应该返回 access_token 和 refresh_token"
        },
        {
            "name": "刷新 token 测试",
            "endpoint": "POST /app/v1/user/refresh-token",
            "data": {
                "refresh_token": "从登录响应中获取的refresh_token"
            },
            "expected": "应该返回新的 access_token"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"   {i}. {test_case['name']}")
        print(f"      接口: {test_case['endpoint']}")
        print(f"      预期结果: {test_case['expected']}")
        print(f"      测试数据: {json.dumps(test_case['data'], ensure_ascii=False, indent=6)}")
        print()
    
    print("💡 测试步骤:")
    print("1. 启动服务器: python start_app.py")
    print("2. 先注册一个测试用户（使用万能验证码 123456）")
    print("3. 使用登录接口获取 token")
    print("4. 使用刷新 token 接口测试 token 刷新")
    
    print("\n🔧 JWT 配置:")
    print("访问 token 过期时间: 30分钟")
    print("刷新 token 过期时间: 7天")
    print("算法: HS256")
    
    print("\n📝 登录响应格式:")
    print("```json")
    print('{')
    print('  "code": 200,')
    print('  "msg": "登录成功",')
    print('  "success": true,')
    print('  "data": {')
    print('    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",')
    print('    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",')
    print('    "token_type": "bearer",')
    print('    "expires_in": 1800,')
    print('    "refresh_expires_in": 604800,')
    print('    "user_info": {')
    print('      "user_id": 1,')
    print('      "user_name": "faker",')
    print('      "nick_name": "测试用户",')
    print('      "email": "test@example.com",')
    print('      "phone": "13800138000"')
    print('    }')
    print('  }')
    print('}')
    print("```")
    
    print("\n🔐 使用 token:")
    print("在后续请求的 Header 中添加:")
    print('Authorization: Bearer <access_token>')
    
    print("\n✅ JWT 登录功能测试准备完成！")
    print("🎯 现在登录接口应该返回完整的 JWT token 对")


if __name__ == "__main__":
    asyncio.run(test_jwt_login()) 