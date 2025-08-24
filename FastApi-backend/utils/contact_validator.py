"""
联系方式验证工具类
用于验证邮箱和手机号的格式和有效性
"""

import re
from typing import Dict, List, Tuple
import dns.resolver
import dns.exception


class ContactValidator:
    """联系方式验证器"""
    
    @staticmethod
    def validate_email(email: str) -> Dict[str, any]:
        """
        验证邮箱格式和有效性
        
        Args:
            email: 待验证的邮箱
            
        Returns:
            Dict: 验证结果
        """
        result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # 基本格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            result['errors'].append("邮箱格式不正确")
            return result
        
        # 长度验证
        if len(email) > 254:  # RFC 5321标准
            result['errors'].append("邮箱地址过长")
            return result
        
        # 本地部分长度验证
        local_part = email.split('@')[0]
        if len(local_part) > 64:
            result['errors'].append("邮箱用户名部分过长")
            return result
        
        # 域名部分长度验证
        domain_part = email.split('@')[1]
        if len(domain_part) > 253:
            result['errors'].append("邮箱域名部分过长")
            return result
        
        # 检查特殊字符
        if re.search(r'[<>"\']', email):
            result['errors'].append("邮箱包含非法字符")
            return result
        
        # 检查连续点号
        if '..' in email:
            result['errors'].append("邮箱不能包含连续的点号")
            return result
        
        # 检查以点号开头或结尾
        if email.startswith('.') or email.endswith('.'):
            result['errors'].append("邮箱不能以点号开头或结尾")
            return result
        
        # 检查域名格式
        domain_parts = domain_part.split('.')
        if len(domain_parts) < 2:
            result['errors'].append("邮箱域名格式不正确")
            return result
        
        # 检查顶级域名长度
        if len(domain_parts[-1]) < 2:
            result['errors'].append("邮箱顶级域名长度不正确")
            return result
        
        # 检查域名部分是否只包含字母、数字和连字符
        for part in domain_parts:
            if not re.match(r'^[a-zA-Z0-9-]+$', part):
                result['errors'].append("邮箱域名包含非法字符")
                return result
            if part.startswith('-') or part.endswith('-'):
                result['errors'].append("邮箱域名不能以连字符开头或结尾")
                return result
        
        # 如果没有错误，标记为有效
        if not result['errors']:
            result['is_valid'] = True
            
            # 提供建议
            if len(local_part) < 3:
                result['suggestions'].append("建议使用更长的用户名")
            if len(domain_parts) == 2:
                result['suggestions'].append("建议使用更具体的域名")
        
        return result
    
    @staticmethod
    def validate_phone(phone: str) -> Dict[str, any]:
        """
        验证手机号格式和有效性
        
        Args:
            phone: 待验证的手机号
            
        Returns:
            Dict: 验证结果
        """
        result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # 移除所有非数字字符
        clean_phone = re.sub(r'\D', '', phone)
        
        # 基本长度验证
        if len(clean_phone) != 11:
            result['errors'].append("手机号必须是11位数字")
            return result
        
        # 检查是否以1开头
        if not clean_phone.startswith('1'):
            result['errors'].append("手机号必须以1开头")
            return result
        
        # 检查第二位数字（运营商号段）
        second_digit = clean_phone[1]
        valid_second_digits = ['3', '4', '5', '6', '7', '8', '9']
        if second_digit not in valid_second_digits:
            result['errors'].append("手机号第二位数字不正确")
            return result
        
        # 检查具体号段
        prefix = clean_phone[:3]
        valid_prefixes = [
            # 中国移动
            '134', '135', '136', '137', '138', '139', '147', '150', '151', '152', 
            '157', '158', '159', '178', '182', '183', '184', '187', '188', '198',
            # 中国联通
            '130', '131', '132', '145', '155', '156', '166', '175', '176', '185', '186',
            # 中国电信
            '133', '149', '153', '173', '177', '180', '181', '189', '199',
            # 虚拟运营商
            '170', '171'
        ]
        
        if prefix not in valid_prefixes:
            result['warnings'].append("该号段可能不是主流运营商")
        
        # 检查是否包含连续重复数字
        if re.search(r'(\d)\1{3,}', clean_phone):
            result['warnings'].append("手机号包含过多连续重复数字")
        
        # 检查是否包含连续数字
        if re.search(r'012|123|234|345|456|567|678|789', clean_phone):
            result['warnings'].append("手机号包含连续数字序列")
        
        # 如果没有错误，标记为有效
        if not result['errors']:
            result['is_valid'] = True
            result['clean_number'] = clean_phone
            
            # 格式化显示
            result['formatted'] = f"{clean_phone[:3]}-{clean_phone[3:7]}-{clean_phone[7:]}"
        
        return result
    
    @staticmethod
    def validate_contact_info(email: str = None, phone: str = None) -> Dict[str, any]:
        """
        验证联系方式信息
        
        Args:
            email: 邮箱地址
            phone: 手机号
            
        Returns:
            Dict: 验证结果
        """
        result = {
            'is_valid': True,
            'email_validation': None,
            'phone_validation': None,
            'errors': [],
            'warnings': []
        }
        
        # 验证邮箱
        if email:
            email_result = ContactValidator.validate_email(email)
            result['email_validation'] = email_result
            if not email_result['is_valid']:
                result['is_valid'] = False
                result['errors'].extend(email_result['errors'])
            result['warnings'].extend(email_result['warnings'])
        
        # 验证手机号
        if phone:
            phone_result = ContactValidator.validate_phone(phone)
            result['phone_validation'] = phone_result
            if not phone_result['is_valid']:
                result['is_valid'] = False
                result['errors'].extend(phone_result['errors'])
            result['warnings'].extend(phone_result['warnings'])
        
        # 至少需要提供一种联系方式
        if not email and not phone:
            result['is_valid'] = False
            result['errors'].append("至少需要提供邮箱或手机号中的一种")
        
        return result
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """
        格式化手机号显示
        
        Args:
            phone: 手机号
            
        Returns:
            str: 格式化后的手机号
        """
        clean_phone = re.sub(r'\D', '', phone)
        if len(clean_phone) == 11:
            return f"{clean_phone[:3]}-{clean_phone[3:7]}-{clean_phone[7:]}"
        return phone
    
    @staticmethod
    def mask_phone(phone: str, mask_char: str = '*') -> str:
        """
        手机号脱敏处理
        
        Args:
            phone: 手机号
            mask_char: 脱敏字符
            
        Returns:
            str: 脱敏后的手机号
        """
        clean_phone = re.sub(r'\D', '', phone)
        if len(clean_phone) == 11:
            return f"{clean_phone[:3]}{mask_char * 4}{clean_phone[7:]}"
        return phone
    
    @staticmethod
    def mask_email(email: str, mask_char: str = '*') -> str:
        """
        邮箱脱敏处理
        
        Args:
            email: 邮箱
            mask_char: 脱敏字符
            
        Returns:
            str: 脱敏后的邮箱
        """
        if '@' not in email:
            return email
        
        local_part, domain = email.split('@')
        if len(local_part) <= 2:
            masked_local = local_part
        else:
            masked_local = local_part[0] + mask_char * (len(local_part) - 2) + local_part[-1]
        
        return f"{masked_local}@{domain}" 