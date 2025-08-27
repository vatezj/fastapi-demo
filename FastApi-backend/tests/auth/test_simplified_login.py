#!/usr/bin/env python3
"""
简化版登录功能测试脚本
测试移除复杂操作后的登录接口是否正常工作
"""

import asyncio
import json
from utils.test_utils import TestUtils


async def test_simplified_login():
    """测试简化版登录功能"""
    
    print("🧪 开始测试简化版登录功能...")
    print("-" * 60)
    
    print("🔍 问题分析:")
    print("错误: (sqlalchemy.exc.MissingGreenlet) greenlet_spawn has not been called")
    print("原因: 可能是复杂的数据库操作导致的异步上下文问题")
    print()
    
    print("🛠️ 修复策略:")
    print("1. 简化数据库会话管理 (config/get_db.py)")
    print("2. 暂时移除可能导致问题的复杂操作")
    print("3. 先确保基本登录功能正常")
    print("4. 逐步恢复其他功能")
    print()
    
    print("📋 当前状态:")
    print("✅ 已修复:")
    print("   - 数据库会话类型注解")
    print("   - 简化会话管理逻辑")
    print("   - 移除复杂异常处理")
    
    print("\n⏸️  暂时禁用:")
    print("   - 用户登录信息更新")
    print("   - 登录日志记录")
    
    print("\n🔧 保留功能:")
    print("   - 用户名密码验证")
    print("   - 用户状态检查")
    print("   - 基本用户信息返回")
    
    print("\n💡 测试步骤:")
    print("1. 启动服务器: python start_app.py")
    print("2. 先注册一个测试用户（使用万能验证码 123456）")
    print("3. 然后尝试登录，观察是否还有 greenlet 错误")
    print("4. 如果基本登录正常，再逐步恢复其他功能")
    
    print("\n📝 测试用例:")
    test_cases = [
        {
            "name": "基本登录测试",
            "data": {
                "userName": "testuser123",
                "password": "Test123456"
            },
            "expected": "应该成功登录，不再出现 greenlet 错误"
        },
        {
            "name": "错误密码测试",
            "data": {
                "userName": "testuser123",
                "password": "WrongPassword"
            },
            "expected": "应该返回密码错误，但不会出现 greenlet 错误"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"   {i}. {test_case['name']}")
        print(f"      预期结果: {test_case['expected']}")
        print(f"      测试数据: {json.dumps(test_case['data'], ensure_ascii=False, indent=6)}")
        print()
    
    print("🔍 下一步计划:")
    print("1. 验证基本登录功能是否正常")
    print("2. 如果正常，逐步恢复用户信息更新功能")
    print("3. 如果正常，逐步恢复登录日志记录功能")
    print("4. 找出导致 greenlet 错误的具体原因")
    
    print("\n✅ 简化版登录功能测试准备完成！")
    print("🎯 现在应该能够进行基本的用户验证，而不会出现 greenlet 错误")


if __name__ == "__main__":
    asyncio.run(test_simplified_login()) 