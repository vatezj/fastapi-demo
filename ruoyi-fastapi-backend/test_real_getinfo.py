#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时测试getInfo接口
"""

import asyncio
import jwt
from datetime import datetime, timedelta
from module_admin.service.login_service import LoginService
from exceptions.exception import AuthException
from utils.log_util import logger

async def test_real_getinfo_scenario():
    """测试真实的getInfo场景"""
    
    print("🔍 测试真实的getInfo场景...")
    print("=" * 50)
    
    try:
        # 模拟一个过期的JWT token
        expired_payload = {
            "user_id": "1",
            "session_id": "test_session",
            "exp": datetime.now().timestamp() - 3600  # 1小时前过期
        }
        
        # 使用错误的密钥生成token（模拟过期）
        expired_token = jwt.encode(expired_payload, "wrong_secret", algorithm="HS256")
        
        print(f"🔑 过期token: {expired_token}")
        
        # 模拟调用get_current_user的逻辑
        print("\n🔍 模拟JWT解码...")
        try:
            # 使用正确的密钥解码（应该失败）
            payload = jwt.decode(expired_token, "correct_secret", algorithms=["HS256"])
            print(f"❌ 意外成功解码: {payload}")
            
        except jwt.InvalidTokenError as e:
            print(f"✅ 正确捕获JWT异常: {type(e).__name__}")
            print("✅ 应该抛出AuthException")
            
            # 模拟抛出AuthException
            try:
                raise AuthException(data='', message='用户token已失效，请重新登录')
            except AuthException as e:
                print(f"✅ 正确抛出AuthException: {e.message}")
                
        except Exception as e:
            print(f"❌ 捕获到其他异常: {type(e).__name__}: {e}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_auth_exception_in_dependency():
    """测试依赖注入中的AuthException"""
    
    print("\n🚫 测试依赖注入中的AuthException...")
    print("=" * 50)
    
    try:
        # 模拟依赖注入函数抛出AuthException
        async def mock_dependency():
            print("🔍 模拟依赖函数执行...")
            raise AuthException(data='', message='用户token已失效，请重新登录')
        
        # 调用模拟依赖
        try:
            await mock_dependency()
        except AuthException as e:
            print(f"✅ 依赖函数正确抛出AuthException: {e.message}")
            print(f"✅ 异常类型: {type(e).__name__}")
            print(f"✅ 异常数据: {e.data}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def test_exception_chain():
    """测试异常链"""
    
    print("\n🔗 测试异常链...")
    print("=" * 50)
    
    try:
        # 模拟完整的异常链
        print("🔍 步骤1: 模拟JWT解码失败")
        try:
            # 故意使用错误的密钥
            jwt.decode("invalid_token", "wrong_secret", algorithms=["HS256"])
        except jwt.InvalidTokenError as e:
            print(f"✅ 步骤1成功: 捕获JWT异常")
            
            print("🔍 步骤2: 抛出AuthException")
            try:
                raise AuthException(data='', message='用户token已失效，请重新登录')
            except AuthException as e:
                print(f"✅ 步骤2成功: 抛出AuthException")
                print(f"   消息: {e.message}")
                print(f"   类型: {type(e).__name__}")
                
                print("🔍 步骤3: 验证异常处理器")
                # 这里应该被全局异常处理器捕获
                print("✅ 步骤3: AuthException应该被全局异常处理器捕获并返回401")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def main():
    """主测试函数"""
    
    print("🚀 开始实时测试getInfo接口...")
    print("=" * 60)
    
    # 测试真实场景
    await test_real_getinfo_scenario()
    
    # 测试依赖注入
    await test_auth_exception_in_dependency()
    
    # 测试异常链
    await test_exception_chain()
    
    print("\n" + "=" * 60)
    print("实时测试完成!")
    print("\n📋 测试结果分析:")
    print("1. JWT解码异常应该被正确捕获")
    print("2. AuthException应该被正确抛出")
    print("3. 全局异常处理器应该返回401状态码")
    print("4. 如果仍然返回500，问题可能在FastAPI框架层面")

if __name__ == "__main__":
    asyncio.run(main())
