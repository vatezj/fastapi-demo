#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试子应用的异常处理器
"""

import asyncio
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from exceptions.exception import AuthException
from exceptions.handle import handle_exception

# 创建主应用
main_app = FastAPI()

# 创建子应用
sub_app = FastAPI()

# 在子应用上注册异常处理器
handle_exception(sub_app)

# 模拟依赖注入函数
async def mock_get_current_user():
    """模拟get_current_user依赖"""
    print("🔍 模拟依赖函数被调用")
    raise AuthException(data='', message='用户token已失效，请重新登录')

# 子应用的路由
@sub_app.get("/test")
async def test_endpoint(current_user = Depends(mock_get_current_user)):
    """测试接口"""
    return {"message": "成功"}

# 将子应用挂载到主应用
main_app.mount("/sub", sub_app)

async def test_exception_handlers():
    """测试异常处理器注册"""
    
    print("🔍 检查异常处理器注册...")
    print("=" * 50)
    
    # 检查主应用的异常处理器
    main_handlers = main_app.exception_handlers
    print(f"✅ 主应用异常处理器数量: {len(main_handlers)}")
    
    # 检查子应用的异常处理器
    sub_handlers = sub_app.exception_handlers
    print(f"✅ 子应用异常处理器数量: {len(sub_handlers)}")
    
    # 检查AuthException处理器
    auth_handler = sub_handlers.get(AuthException)
    if auth_handler:
        print(f"✅ 子应用AuthException处理器已注册: {auth_handler.__name__}")
    else:
        print(f"❌ 子应用AuthException处理器未注册")

def test_subapp_endpoint():
    """测试子应用接口"""
    
    print("\n🌐 测试子应用接口...")
    print("=" * 50)
    
    try:
        client = TestClient(main_app)
        
        # 测试子应用接口
        print("🔍 测试子应用接口: /sub/test")
        response = client.get("/sub/test")
        print(f"✅ 响应状态码: {response.status_code}")
        print(f"✅ 响应内容: {response.text}")
        
        # 检查是否返回401
        if response.status_code == 401:
            print("✅ 成功返回401状态码！")
        else:
            print(f"❌ 期望401状态码，实际返回: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主测试函数"""
    
    print("🚀 开始测试子应用异常处理器...")
    print("=" * 60)
    
    # 测试异常处理器注册
    await test_exception_handlers()
    
    # 测试子应用接口
    test_subapp_endpoint()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("\n📋 测试结果:")
    print("1. 子应用应该有自己的异常处理器")
    print("2. 子应用的AuthException应该返回401状态码")
    print("3. 这解决了主应用异常处理器无法捕获子应用异常的问题")

if __name__ == "__main__":
    asyncio.run(main())
