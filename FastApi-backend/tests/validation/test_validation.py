"""
验证逻辑测试文件
测试密码、邮箱、手机号等验证功能
"""

import asyncio
from utils.password_validator import PasswordValidator
from utils.contact_validator import ContactValidator
from utils.captcha_util import CaptchaUtil


def test_password_validation():
    """测试密码验证"""
    print("=== 密码验证测试 ===")
    
    # 测试强密码
    strong_passwords = [
        "MyPassword123!",
        "SecurePass456@",
        "ComplexPwd789#"
    ]
    
    for pwd in strong_passwords:
        result = PasswordValidator.validate_password_strength(pwd)
        print(f"密码: {pwd}")
        print(f"  强度: {result['strength']}, 分数: {result['score']}")
        print(f"  有效: {result['is_valid']}")
        if result['warnings']:
            print(f"  警告: {result['warnings']}")
        if result['suggestions']:
            print(f"  建议: {result['suggestions']}")
        print()
    
    # 测试弱密码
    weak_passwords = [
        "123456",
        "password",
        "abc",
        "123"
    ]
    
    for pwd in weak_passwords:
        result = PasswordValidator.validate_password_strength(pwd)
        print(f"密码: {pwd}")
        print(f"  强度: {result['strength']}, 分数: {result['score']}")
        print(f"  有效: {result['is_valid']}")
        if result['errors']:
            print(f"  错误: {result['errors']}")
        print()
    
    # 测试密码要求
    requirements = PasswordValidator.get_password_requirements()
    print("密码要求:")
    for key, value in requirements.items():
        print(f"  {key}: {value}")
    
    # 生成强密码
    generated_pwd = PasswordValidator.generate_strong_password(16)
    print(f"\n生成的强密码: {generated_pwd}")


def test_contact_validation():
    """测试联系方式验证"""
    print("\n=== 联系方式验证测试 ===")
    
    # 测试邮箱验证
    test_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "invalid-email",
        "test@.com",
        "test@com",
        "test..test@example.com"
    ]
    
    print("邮箱验证:")
    for email in test_emails:
        result = ContactValidator.validate_email(email)
        print(f"  邮箱: {email}")
        print(f"    有效: {result['is_valid']}")
        if result['errors']:
            print(f"    错误: {result['errors']}")
        if result['warnings']:
            print(f"    警告: {result['warnings']}")
        if result['suggestions']:
            print(f"    建议: {result['suggestions']}")
        print()
    
    # 测试手机号验证
    test_phones = [
        "13800138000",
        "138-0013-8000",
        "138 0013 8000",
        "12345678901",
        "1380013800",
        "23800138000"
    ]
    
    print("手机号验证:")
    for phone in test_phones:
        result = ContactValidator.validate_phone(phone)
        print(f"  手机号: {phone}")
        print(f"    有效: {result['is_valid']}")
        if result['errors']:
            print(f"    错误: {result['errors']}")
        if result['warnings']:
            print(f"    警告: {result['warnings']}")
        if result['is_valid']:
            print(f"    格式化: {result['formatted']}")
        print()
    
    # 测试综合验证
    print("综合验证:")
    test_cases = [
        {"email": "test@example.com", "phone": "13800138000"},
        {"email": "invalid-email", "phone": "13800138000"},
        {"email": "test@example.com", "phone": "12345678901"},
        {"email": None, "phone": None}
    ]
    
    for case in test_cases:
        result = ContactValidator.validate_contact_info(**case)
        print(f"  邮箱: {case['email']}, 手机号: {case['phone']}")
        print(f"    有效: {result['is_valid']}")
        if result['errors']:
            print(f"    错误: {result['errors']}")
        if result['warnings']:
            print(f"    警告: {result['warnings']}")
        print()
    
    # 测试脱敏功能
    print("脱敏测试:")
    email = "test@example.com"
    phone = "13800138000"
    
    masked_email = ContactValidator.mask_email(email)
    masked_phone = ContactValidator.mask_phone(phone)
    
    print(f"  邮箱: {email} -> {masked_email}")
    print(f"  手机号: {phone} -> {masked_phone}")


async def test_captcha():
    """测试验证码功能"""
    print("\n=== 验证码测试 ===")
    
    # 生成UUID
    uuid_str = CaptchaUtil.generate_uuid()
    print(f"生成的UUID: {uuid_str}")
    
    # 生成验证码
    result = await CaptchaUtil.generate_and_store_captcha(uuid_str)
    
    if result.get('error'):
        print(f"验证码生成失败: {result['error']}")
        return
    
    print(f"验证码: {result['code']}")
    print(f"图片长度: {len(result['image']) if result['image'] else 0}")
    print(f"过期时间: {result['expire_seconds']}秒")
    
    # 测试验证
    is_valid = await CaptchaUtil.verify_captcha_code(uuid_str, result['code'])
    print(f"验证结果: {is_valid}")
    
    # 测试错误验证码
    is_valid = await CaptchaUtil.verify_captcha_code(uuid_str, "0000")
    print(f"错误验证码验证结果: {is_valid}")


def main():
    """主函数"""
    print("开始验证逻辑测试...")
    
    # 测试密码验证
    test_password_validation()
    
    # 测试联系方式验证
    test_contact_validation()
    
    # 测试验证码功能
    asyncio.run(test_captcha())
    
    print("\n测试完成!")


if __name__ == "__main__":
    main() 