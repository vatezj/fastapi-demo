"""
测试工具类
提供测试环境下的便利功能
"""

from config.test_config import UNIVERSAL_CAPTCHA_CODE, UNIVERSAL_CAPTCHA_ENABLED


class TestUtils:
    """测试工具类"""
    
    @staticmethod
    def is_universal_captcha(code: str) -> bool:
        """
        检查是否为万能验证码
        
        Args:
            code: 验证码
            
        Returns:
            bool: 是否为万能验证码
        """
        return UNIVERSAL_CAPTCHA_ENABLED and code == UNIVERSAL_CAPTCHA_CODE
    
    @staticmethod
    def get_universal_captcha() -> str:
        """
        获取万能验证码
        
        Returns:
            str: 万能验证码
        """
        return UNIVERSAL_CAPTCHA_CODE
    
    @staticmethod
    def is_test_mode() -> bool:
        """
        检查是否为测试模式
        
        Returns:
            bool: 是否为测试模式
        """
        from config.test_config import DEBUG_MODE
        return DEBUG_MODE
    
    @staticmethod
    def generate_test_username(prefix: str = None) -> str:
        """
        生成测试用户名
        
        Args:
            prefix: 用户名前缀
            
        Returns:
            str: 测试用户名
        """
        import time
        if prefix is None:
            from config.test_config import TEST_USER_PREFIX
            prefix = TEST_USER_PREFIX
        
        timestamp = int(time.time())
        return f"{prefix}{timestamp}"
    
    @staticmethod
    def generate_test_email(username: str = None) -> str:
        """
        生成测试邮箱
        
        Args:
            username: 用户名，如果为None则自动生成
            
        Returns:
            str: 测试邮箱
        """
        if username is None:
            username = TestUtils.generate_test_username()
        
        from config.test_config import TEST_EMAIL_DOMAIN
        return f"{username}@{TEST_EMAIL_DOMAIN}" 