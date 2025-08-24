"""
密码强度验证工具类
用于验证密码的复杂度和安全性
"""

import re
from typing import Dict, List, Tuple


class PasswordValidator:
    """密码强度验证器"""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, any]:
        """
        验证密码强度
        
        Args:
            password: 待验证的密码
            
        Returns:
            Dict: 包含验证结果的字典
        """
        result = {
            'is_valid': True,
            'score': 0,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # 基本长度检查
        if len(password) < 8:
            result['is_valid'] = False
            result['errors'].append("密码长度至少8位")
        elif len(password) < 12:
            result['warnings'].append("建议密码长度至少12位")
        
        # 字符类型检查
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[@$!%*?&]', password))
        
        # 计算强度分数
        score = 0
        if has_lower:
            score += 1
        if has_upper:
            score += 1
        if has_digit:
            score += 1
        if has_special:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        result['score'] = score
        
        # 检查字符类型
        if not has_lower:
            result['errors'].append("密码必须包含小写字母")
            result['is_valid'] = False
        if not has_upper:
            result['errors'].append("密码必须包含大写字母")
            result['is_valid'] = False
        if not has_digit:
            result['errors'].append("密码必须包含数字")
            result['is_valid'] = False
        if not has_special:
            result['errors'].append("密码必须包含特殊字符(@$!%*?&)")
            result['is_valid'] = False
        
        # 检查常见弱密码模式
        weak_patterns = [
            r'123456',
            r'password',
            r'qwerty',
            r'admin',
            r'abc123',
            r'111111',
            r'000000'
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, password.lower()):
                result['warnings'].append(f"避免使用常见弱密码模式: {pattern}")
        
        # 检查连续字符
        if re.search(r'(.)\1{2,}', password):
            result['warnings'].append("避免使用连续重复的字符")
        
        # 检查键盘序列
        keyboard_sequences = [
            'qwerty', 'asdfgh', 'zxcvbn',
            '123456', '654321'
        ]
        
        for seq in keyboard_sequences:
            if seq in password.lower():
                result['warnings'].append("避免使用键盘序列")
                break
        
        # 提供改进建议
        if score < 3:
            result['suggestions'].append("增加密码长度")
            result['suggestions'].append("添加更多字符类型")
        if not has_special:
            result['suggestions'].append("添加特殊字符")
        if len(password) < 12:
            result['suggestions'].append("使用更长的密码")
        
        # 设置强度等级
        if score >= 5:
            result['strength'] = "强"
        elif score >= 3:
            result['strength'] = "中"
        else:
            result['strength'] = "弱"
        
        return result
    
    @staticmethod
    def is_strong_password(password: str) -> bool:
        """
        判断密码是否足够强
        
        Args:
            password: 待验证的密码
            
        Returns:
            bool: 是否为强密码
        """
        result = PasswordValidator.validate_password_strength(password)
        return result['is_valid'] and result['score'] >= 3
    
    @staticmethod
    def get_password_requirements() -> Dict[str, str]:
        """
        获取密码要求说明
        
        Returns:
            Dict: 密码要求说明
        """
        return {
            'min_length': '至少8位',
            'max_length': '建议不超过50位',
            'character_types': '必须包含大小写字母、数字和特殊字符',
            'special_chars': '支持的特殊字符: @$!%*?&',
            'avoid_patterns': '避免使用常见弱密码、连续字符、键盘序列',
            'recommendation': '建议使用12位以上的强密码'
        }
    
    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """
        生成强密码
        
        Args:
            length: 密码长度
            
        Returns:
            str: 生成的强密码
        """
        import random
        import string
        
        # 确保包含所有必需的字符类型
        password = []
        password.append(random.choice(string.ascii_lowercase))  # 小写字母
        password.append(random.choice(string.ascii_uppercase))  # 大写字母
        password.append(random.choice(string.digits))           # 数字
        password.append(random.choice('@$!%*?&'))             # 特殊字符
        
        # 填充剩余长度
        remaining_length = length - 4
        all_chars = string.ascii_letters + string.digits + '@$!%*?&'
        password.extend(random.choice(all_chars) for _ in range(remaining_length))
        
        # 打乱密码顺序
        random.shuffle(password)
        
        return ''.join(password) 