"""
简单的验证码测试脚本
测试验证码生成和存储功能
"""

import asyncio
from utils.captcha_util import CaptchaUtil


async def test_captcha_basic():
    """测试基本的验证码功能"""
    print("=== 验证码基本功能测试 ===")
    
    # 生成UUID
    uuid_str = CaptchaUtil.generate_uuid()
    print(f"生成的UUID: {uuid_str}")
    
    # 生成验证码
    result = await CaptchaUtil.generate_and_store_captcha(uuid_str)
    
    if result.get('error'):
        print(f"❌ 验证码生成失败: {result['error']}")
        return
    
    print(f"✅ 验证码生成成功")
    print(f"验证码: {result['code']}")
    print(f"图片长度: {len(result['image']) if result['image'] else 0}")
    print(f"过期时间: {result['expire_seconds']}秒")
    
    # 测试验证
    is_valid = await CaptchaUtil.verify_captcha_code(uuid_str, result['code'])
    print(f"验证结果: {is_valid}")
    
    # 测试错误验证码
    is_valid = await CaptchaUtil.verify_captcha_code(uuid_str, "0000")
    print(f"错误验证码验证结果: {is_valid}")


async def main():
    """主函数"""
    print("开始验证码测试...")
    
    try:
        await test_captcha_basic()
        print("\n✅ 验证码测试完成！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 