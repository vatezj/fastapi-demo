"""
测试配置文件
包含测试环境下的特殊配置，如万能验证码等
"""

# 万能验证码配置
UNIVERSAL_CAPTCHA_CODE = "123456"  # 万能验证码
UNIVERSAL_CAPTCHA_ENABLED = True   # 是否启用万能验证码

# 测试用户配置
TEST_USER_PREFIX = "test_user_"     # 测试用户前缀
TEST_EMAIL_DOMAIN = "test.com"      # 测试邮箱域名

# 其他测试配置
DEBUG_MODE = True                    # 调试模式
LOG_LEVEL = "DEBUG"                 # 日志级别 