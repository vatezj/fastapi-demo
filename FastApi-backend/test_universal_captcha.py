#!/usr/bin/env python3
"""
万能验证码测试脚本
测试注册接口的万能验证码功能
"""

import asyncio
import aiohttp
import json
from utils.test_utils import TestUtils


async def test_universal_captcha():
    """测试万能验证码功能"""
    
    print("🧪 开始测试万能验证码功能...")
    print(f"🔑 万能验证码: {TestUtils.get_universal_captcha()}")
    print(f"📱 测试模式: {TestUtils.is_test_mode()}")
    print("-" * 50)
    
    # 测试数据
    test_cases = [
        {
            "name": "使用万能验证码注册",
            "data": {
                "userName": TestUtils.generate_test_username(),
                "nickName": "测试用户",
                "email": TestUtils.generate_test_email(),
                "phone": "13800138000",
                "password": "Test123456",
                "confirmPassword": "Test123456",
                "code": TestUtils.get_universal_captcha(),
                "uuid": "test_uuid_123"
            },
            "expected": "应该成功注册"
        },
        {
            "name": "使用错误验证码注册",
            "data": {
                "userName": TestUtils.generate_test_username(),
                "nickName": "测试用户2",
                "email": TestUtils.generate_test_email(),
                "phone": "13800138001",
                "password": "Test123456",
                "confirmPassword": "Test123456",
                "code": "000000",
                "uuid": "test_uuid_456"
            },
            "expected": "应该失败（验证码错误）"
        },
        {
            "name": "使用万能验证码但无UUID",
            "data": {
                "userName": TestUtils.generate_test_username(),
                "nickName": "测试用户3",
                "email": TestUtils.generate_test_email(),
                "phone": "13800138002",
                "password": "Test123456",
                "confirmPassword": "Test123456",
                "code": TestUtils.get_universal_captcha(),
                "uuid": None
            },
            "expected": "应该跳过验证码验证"
        }
    ]
    
    # 测试万能验证码工具类
    print("🔧 测试万能验证码工具类...")
    test_code = TestUtils.get_universal_captcha()
    print(f"万能验证码: {test_code}")
    print(f"是否为万能验证码: {TestUtils.is_universal_captcha(test_code)}")
    print(f"是否为万能验证码: {TestUtils.is_universal_captcha('000000')}")
    print(f"测试用户名: {TestUtils.generate_test_username()}")
    print(f"测试邮箱: {TestUtils.generate_test_email()}")
    print("-" * 50)
    
    # 测试注册接口
    print("🌐 测试注册接口...")
    
    # 注意：这里只是模拟测试，实际需要启动服务器
    print("⚠️  注意：需要启动服务器才能进行实际接口测试")
    print("💡 测试步骤：")
    print("1. 启动服务器: python start_app.py")
    print("2. 使用万能验证码 123456 进行注册")
    print("3. 观察控制台输出")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试用例 {i}: {test_case['name']}")
        print(f"   预期结果: {test_case['expected']}")
        print(f"   测试数据: {json.dumps(test_case['data'], ensure_ascii=False, indent=2)}")
    
    print("\n✅ 万能验证码功能测试完成！")
    print(f"🎯 使用验证码 '{TestUtils.get_universal_captcha()}' 可以绕过验证码校验")


if __name__ == "__main__":
    asyncio.run(test_universal_captcha()) 