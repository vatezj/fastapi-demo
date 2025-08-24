#!/usr/bin/env python3
"""
任务发布接口修复测试脚本
测试修复后的任务发布接口是否正常工作
"""

import asyncio
import json
from utils.test_utils import TestUtils


async def test_task_publish_fix():
    """测试任务发布接口修复"""
    
    print("🧪 开始测试任务发布接口修复...")
    print("-" * 60)
    
    print("🔍 问题分析:")
    print("错误: 'AsyncSession' object has no attribute 'db'")
    print("原因: create_task 方法调用参数不匹配")
    print("      方法期望: create_task(task_data)")
    print("      实际调用: create_task(publisher_id=..., task_data=...)")
    print()
    
    print("🛠️ 修复措施:")
    print("1. 修正 create_task 方法调用参数")
    print("2. 将 publisher_id 添加到 task_data 中")
    print("3. 确保参数传递正确")
    print()
    
    print("📋 修复前后对比:")
    print("修复前:")
    print("```python")
    print("task = await task_dao.create_task(")
    print("    publisher_id=current_user.user_id,")
    print("    task_data=task_data")
    print(")")
    print("```")
    
    print("\n修复后:")
    print("```python")
    print("# 准备任务数据，包含发布者ID")
    print("task_data_with_publisher = task_data.copy()")
    print("task_data_with_publisher['publisher_id'] = current_user.user_id")
    print("")
    print("task_dao = TaskDao(db)")
    print("task = await task_dao.create_task(task_data_with_publisher)")
    print("```")
    
    print("\n💡 测试步骤:")
    print("1. 启动服务器: python start_app.py")
    print("2. 先注册一个测试用户（使用万能验证码 123456）")
    print("3. 登录获取 JWT token")
    print("4. 使用 token 调用任务发布接口")
    print("5. 观察是否还有 'db' 属性错误")
    
    print("\n📝 测试数据示例:")
    test_task_data = {
        "task_name": "测试任务名称",
        "task_description": "这是一个测试任务的详细描述",
        "task_price": 10.50,
        "task_quantity": 100,
        "task_type_id": 1,
        "device_limit": "mobile",
        "frequency_limit": "once_per_day",
        "task_deadline": "2024-12-31T23:59:59",
        "task_regions": [
            {"region_code": "000000", "level": "country"},
            {"region_code": "11", "level": "province"}
        ],
        "task_tags": ["测试", "简单"],
        "steps": [
            {
                "step_order": 1,
                "step_type": "visit",
                "step_title": "访问指定网站",
                "step_description": "请访问指定的网站并停留30秒",
                "step_url": "https://example.com",
                "step_duration": 30,
                "step_required": True
            }
        ],
        "verifications": [
            {
                "verification_title": "截图验证",
                "verification_type": "screenshot",
                "verification_description": "请截图显示任务完成状态",
                "image_required": True,
                "text_required": False,
                "text_placeholder": ""
            }
        ],
        "bonus_conditions": [
            {
                "condition_type": "time_bonus",
                "condition_value": "within_1_hour",
                "bonus_amount": 2.00,
                "description": "1小时内完成可获得额外奖励"
            }
        ],
        "special_requirements": "需要真实用户操作，禁止使用自动化工具",
        "contact_info": {
            "qq": "123456789",
            "wechat": "test_wechat",
            "phone": "13800138000"
        }
    }
    
    print("```json")
    print(json.dumps(test_task_data, ensure_ascii=False, indent=2))
    print("```")
    
    print("\n🔧 修复的技术细节:")
    print("1. 参数传递修复:")
    print("   - 确保 create_task 方法只接收一个参数")
    print("   - 将 publisher_id 正确添加到任务数据中")
    
    print("\n2. 数据准备:")
    print("   - 使用 copy() 方法避免修改原始数据")
    print("   - 在调用 DAO 方法前准备好完整数据")
    
    print("\n3. 方法调用:")
    print("   - 确保 DAO 方法调用参数正确")
    print("   - 避免参数不匹配导致的错误")
    
    print("\n✅ 任务发布接口修复完成！")
    print("🎯 现在应该能够正常发布任务，不再出现 'db' 属性错误")


if __name__ == "__main__":
    asyncio.run(test_task_publish_fix()) 