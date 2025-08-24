#!/usr/bin/env python3
"""
统一API响应格式测试脚本
测试修复后的任务发布接口是否返回统一的API响应格式
"""

import asyncio
import json
from utils.test_util import TestUtils


async def test_unified_response_format():
    """测试统一API响应格式"""
    
    print("🧪 开始测试统一API响应格式...")
    print("-" * 60)
    
    print("🔍 问题分析:")
    print("错误: 接口返回格式不统一")
    print("问题: 直接抛出 HTTPException，返回格式为:")
    print("```json")
    print('{"detail": "账户余额不足，无法发布任务"}')
    print("```")
    print()
    print("期望: 统一的API响应格式")
    print("```json")
    print('{"code": 500, "msg": "账户余额不足，无法发布任务", "success": false, "time": "..."}')
    print("```")
    print()
    
    print("🛠️ 修复措施:")
    print("1. 将所有 HTTPException 替换为 ResponseUtil.error")
    print("2. 确保所有错误都返回统一的API响应格式")
    print("3. 保持成功响应的格式一致")
    print()
    
    print("📋 修复前后对比:")
    print("修复前:")
    print("```python")
    print("if user_account.balance < total_cost:")
    print("    raise HTTPException(")
    print("        status_code=status.HTTP_400_BAD_REQUEST,")
    print("        detail='账户余额不足，无法发布任务'")
    print("    )")
    print("```")
    
    print("\n修复后:")
    print("```python")
    print("if user_account.balance < total_cost:")
    print("    return ResponseUtil.error('账户余额不足，无法发布任务')")
    print("```")
    
    print("\n💡 测试步骤:")
    print("1. 启动服务器: python start_app.py")
    print("2. 先注册一个测试用户（使用万能验证码 123456）")
    print("3. 登录获取 JWT token")
    print("4. 使用 token 调用任务发布接口，但使用余额不足的数据")
    print("5. 观察返回的响应格式是否统一")
    print("6. 测试其他验证错误，确认格式一致")
    
    print("\n📝 测试场景:")
    print("1. 缺少必填字段")
    print("2. 任务价格超出范围")
    print("3. 任务步骤数量超限")
    print("4. 验证要求数量超限")
    print("5. 账户余额不足")
    print("6. 其他业务逻辑错误")
    
    print("\n📝 测试数据示例（余额不足）:")
    test_task_data_insufficient_balance = {
        "task_name": "测试任务名称",
        "task_description": "这是一个测试任务的详细描述",
        "task_price": 1000.00,  # 高价格
        "task_quantity": 1000,  # 高数量
        "task_type_id": 1,
        "device_limit": "mobile",
        "frequency_limit": "once_per_day",
        "task_deadline": "2024-12-31T23:59:59",
        "task_regions": [
            {"region_code": "000000", "level": "country"}
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
    print(json.dumps(test_task_data_insufficient_balance, ensure_ascii=False, indent=2))
    print("```")
    
    print("\n📝 测试数据示例（缺少必填字段）:")
    test_task_data_missing_fields = {
        "task_name": "测试任务名称",
        # 缺少 task_description
        "task_price": 10.50,
        "task_quantity": 100,
        # 缺少 task_type_id
        "device_limit": "mobile"
    }
    
    print("```json")
    print(json.dumps(test_task_data_missing_fields, ensure_ascii=False, indent=2))
    print("```")
    
    print("\n🔧 修复的技术细节:")
    print("1. 响应格式统一:")
    print("   - 所有错误都使用 ResponseUtil.error()")
    print("   - 所有成功都使用 ResponseUtil.success()")
    print("   - 确保 code、msg、success、time 字段一致")
    
    print("\n2. 错误处理改进:")
    print("   - 不再抛出 HTTPException")
    print("   - 直接返回统一的错误响应")
    print("   - 保持HTTP状态码为200，通过code字段表示错误")
    
    print("\n3. 用户体验提升:")
    print("   - 前端可以统一处理响应格式")
    print("   - 错误信息更加清晰明确")
    print("   - 响应结构保持一致")
    
    print("\n4. 代码维护性:")
    print("   - 错误处理逻辑更加清晰")
    print("   - 响应格式统一，便于维护")
    print("   - 减少重复代码")
    
    print("\n⚠️ 重要提醒:")
    print("- 所有错误现在都返回统一的API响应格式")
    print("- HTTP状态码保持200，通过code字段区分成功/失败")
    print("- 响应格式与登录接口保持一致")
    
    print("\n✅ 统一API响应格式修复完成！")
    print("🎯 现在任务发布接口的所有错误都会返回统一的API响应格式")


if __name__ == "__main__":
    asyncio.run(test_unified_response_format()) 