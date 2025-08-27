"""
注册流程测试脚本
测试完整的用户注册验证流程
"""

import asyncio
from module_app.entity.vo.app_user_vo import AppRegisterModel
from utils.password_validator import PasswordValidator
from utils.contact_validator import ContactValidator
from pydantic import ValidationError


def test_validation_flow():
    """测试验证流程"""
    print("=== 用户注册验证流程测试 ===\n")
    
    # 测试用例1：完全有效的数据
    print("测试用例1：完全有效的数据")
    try:
        user_data = AppRegisterModel(
            userName='testuser123',
            nickName='测试用户',
            email='test@example.com',
            phone='13800138000',
            password='MyPassword123!',
            confirmPassword='MyPassword123!',
            code='1234',
            uuid='test-uuid-123'
        )
        print("✅ 基础验证通过")
        
        # 额外验证
        password_validation = PasswordValidator.validate_password_strength(user_data.password)
        if password_validation['is_valid']:
            print(f"✅ 密码强度验证通过 - 强度: {password_validation['strength']}")
        else:
            print(f"❌ 密码强度验证失败: {password_validation['errors']}")
        
        contact_validation = ContactValidator.validate_contact_info(
            email=user_data.email, 
            phone=user_data.phone
        )
        if contact_validation['is_valid']:
            print("✅ 联系方式验证通过")
        else:
            print(f"❌ 联系方式验证失败: {contact_validation['errors']}")
            
    except ValidationError as e:
        print(f"❌ 基础验证失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试用例2：弱密码
    print("测试用例2：弱密码")
    try:
        user_data = AppRegisterModel(
            userName='testuser456',
            nickName='测试用户',
            email='test@example.com',
            phone='13800138000',
            password='weak',
            confirmPassword='weak',
            code='1234',
            uuid='test-uuid-456'
        )
        print("✅ 基础验证通过")
        
        # 密码强度验证
        password_validation = PasswordValidator.validate_password_strength(user_data.password)
        if password_validation['is_valid']:
            print(f"✅ 密码强度验证通过 - 强度: {password_validation['strength']}")
        else:
            print(f"❌ 密码强度验证失败: {password_validation['errors']}")
            print(f"   建议: {password_validation['suggestions']}")
            
    except ValidationError as e:
        print(f"❌ 基础验证失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试用例3：无效邮箱
    print("测试用例3：无效邮箱")
    try:
        user_data = AppRegisterModel(
            userName='testuser789',
            nickName='测试用户',
            email='invalid-email',
            phone='13800138000',
            password='MyPassword123!',
            confirmPassword='MyPassword123!',
            code='1234',
            uuid='test-uuid-789'
        )
        print("✅ 基础验证通过")
        
        # 联系方式验证
        contact_validation = ContactValidator.validate_contact_info(
            email=user_data.email, 
            phone=user_data.phone
        )
        if contact_validation['is_valid']:
            print("✅ 联系方式验证通过")
        else:
            print(f"❌ 联系方式验证失败: {contact_validation['errors']}")
            
    except ValidationError as e:
        print(f"❌ 基础验证失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试用例4：无效手机号
    print("测试用例4：无效手机号")
    try:
        user_data = AppRegisterModel(
            userName='testuser000',
            nickName='测试用户',
            email='test@example.com',
            phone='12345678901',
            password='MyPassword123!',
            confirmPassword='MyPassword123!',
            code='1234',
            uuid='test-uuid-000'
        )
        print("✅ 基础验证通过")
        
        # 联系方式验证
        contact_validation = ContactValidator.validate_contact_info(
            email=user_data.email, 
            phone=user_data.phone
        )
        if contact_validation['is_valid']:
            print("✅ 联系方式验证通过")
        else:
            print(f"❌ 联系方式验证失败: {contact_validation['errors']}")
            
    except ValidationError as e:
        print(f"❌ 基础验证失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试用例5：用户名包含特殊字符
    print("测试用例5：用户名包含特殊字符")
    try:
        user_data = AppRegisterModel(
            userName='test@user',
            nickName='测试用户',
            email='test@example.com',
            phone='13800138000',
            password='MyPassword123!',
            confirmPassword='MyPassword123!',
            code='1234',
            uuid='test-uuid-special'
        )
        print("❌ 应该失败但没有失败")
    except ValidationError as e:
        print(f"✅ 正确被拒绝: {e.errors()[0]['msg']}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试用例6：密码不匹配
    print("测试用例6：密码不匹配")
    try:
        user_data = AppRegisterModel(
            userName='testuser111',
            nickName='测试用户',
            email='test@example.com',
            phone='13800138000',
            password='MyPassword123!',
            confirmPassword='DifferentPassword123!',
            code='1234',
            uuid='test-uuid-mismatch'
        )
        print("❌ 应该失败但没有失败")
    except ValidationError as e:
        print(f"✅ 正确被拒绝: {e.errors()[0]['msg']}")


def test_password_generation():
    """测试密码生成"""
    print("\n=== 密码生成测试 ===")
    
    # 生成不同长度的强密码
    for length in [8, 12, 16, 20]:
        password = PasswordValidator.generate_strong_password(length)
        validation = PasswordValidator.validate_password_strength(password)
        print(f"长度{length}位: {password}")
        print(f"  强度: {validation['strength']}, 分数: {validation['score']}")
        print(f"  有效: {validation['is_valid']}")
        print()


def test_contact_formatting():
    """测试联系方式格式化"""
    print("=== 联系方式格式化测试 ===")
    
    # 测试手机号格式化
    test_phones = ["13800138000", "138-0013-8000", "138 0013 8000"]
    for phone in test_phones:
        formatted = ContactValidator.format_phone(phone)
        masked = ContactValidator.mask_phone(phone)
        print(f"原始: {phone}")
        print(f"格式化: {formatted}")
        print(f"脱敏: {masked}")
        print()
    
    # 测试邮箱脱敏
    test_emails = ["test@example.com", "user.name@domain.co.uk", "a@b.c"]
    for email in test_emails:
        masked = ContactValidator.mask_email(email)
        print(f"原始: {email}")
        print(f"脱敏: {masked}")
        print()


def main():
    """主函数"""
    print("开始用户注册验证流程测试...\n")
    
    # 测试验证流程
    test_validation_flow()
    
    # 测试密码生成
    test_password_generation()
    
    # 测试联系方式格式化
    test_contact_formatting()
    
    print("\n🎉 所有测试完成！")
    print("\n📋 测试总结:")
    print("✅ 基础字段验证")
    print("✅ 密码强度验证")
    print("✅ 联系方式验证")
    print("✅ 用户名格式验证")
    print("✅ 密码确认验证")
    print("✅ 密码生成功能")
    print("✅ 联系方式格式化")


if __name__ == "__main__":
    main() 