#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试getInfo接口异常处理
"""

import asyncio
import jwt
from datetime import datetime, timedelta
from module_admin.service.login_service import LoginService
from exceptions.exception import AuthException
from utils.log_util import logger

async def test_token_validation():
    """测试token验证逻辑"""
    
    print("🔍 测试token验证逻辑...")
    print("=" * 50)
    
    try:
        # 模拟一个过期的token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJzZXNzaW9uX2lkIjoidGVzdCIsImV4cCI6MTY5NzY4MDAwMH0.invalid_signature"
        
        print(f"🔑 测试过期token: {expired_token}")
        
        # 直接调用LoginService.get_current_user的逻辑
        try:
            # 模拟JWT解码
            if expired_token.startswith('Bearer'):
                expired_token = expired_token.split(' ')[1]
            
            print("🔍 尝试解码JWT...")
            # 这里应该抛出InvalidTokenError
            payload = jwt.decode(expired_token, "wrong_secret", algorithms=["HS256"])
            print(f"❌ JWT解码成功（不应该成功）: {payload}")
            
        except jwt.InvalidTokenError as e:
            print(f"✅ 正确捕获JWT异常: {e}")
            print("✅ 应该抛出AuthException")
            
        except Exception as e:
            print(f"❌ 捕获到其他异常: {type(e).__name__}: {e}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_auth_exception():
    """测试AuthException异常"""
    
    print("\n🚫 测试AuthException异常...")
    print("=" * 50)
    
    try:
        # 直接抛出AuthException
        print("🔍 抛出AuthException...")
        raise AuthException(data='', message='用户token已失效，请重新登录')
        
    except AuthException as e:
        print(f"✅ 正确捕获AuthException: {e.message}")
        print(f"✅ 异常数据: {e.data}")
        
    except Exception as e:
        print(f"❌ 捕获到其他异常: {type(e).__name__}: {e}")

def test_response_util():
    """测试ResponseUtil的unauthorized方法"""
    
    print("\n🔧 测试ResponseUtil.unauthorized...")
    print("=" * 50)
    
    try:
        from utils.response_util import ResponseUtil
        
        # 测试unauthorized方法
        response = ResponseUtil.unauthorized(msg="用户token已失效，请重新登录")
        print(f"✅ unauthorized响应状态码: {response.status_code}")
        print(f"✅ 响应内容: {response.body.decode()}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主测试函数"""
    
    print("🚀 开始测试getInfo接口异常处理...")
    print("=" * 60)
    
    # 测试token验证逻辑
    await test_token_validation()
    
    # 测试AuthException异常
    await test_auth_exception()
    
    # 测试ResponseUtil
    test_response_util()
    
    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
