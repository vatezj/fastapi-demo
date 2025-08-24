"""
验证码工具类
用于生成和验证图形验证码
"""

import random
import string
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
from config.get_redis import RedisUtil
from config.env import RedisConfig
import asyncio


class CaptchaUtil:
    """验证码工具类"""
    
    @staticmethod
    def generate_captcha_code(length: int = 4) -> str:
        """
        生成验证码
        
        Args:
            length: 验证码长度
            
        Returns:
            str: 验证码字符串
        """
        # 生成数字和字母组合的验证码
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def generate_captcha_image(code: str, width: int = 120, height: int = 40) -> str:
        """
        生成验证码图片
        
        Args:
            code: 验证码字符串
            width: 图片宽度
            height: 图片高度
            
        Returns:
            str: base64编码的图片
        """
        # 创建图片
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # 设置字体（使用默认字体）
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # 绘制验证码文字
        for i, char in enumerate(code):
            x = 20 + i * 20
            y = random.randint(5, 15)
            color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            draw.text((x, y), char, font=font, fill=color)
        
        # 添加干扰线
        for _ in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            color = (random.randint(150, 200), random.randint(150, 200), random.randint(150, 200))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
        
        # 添加干扰点
        for _ in range(30):
            x = random.randint(0, width)
            y = random.randint(0, height)
            color = (random.randint(150, 200), random.randint(150, 200), random.randint(150, 200))
            draw.point((x, y), fill=color)
        
        # 转换为base64
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    async def store_captcha_code(uuid: str, code: str, expire_seconds: int = 300) -> bool:
        """
        存储验证码到Redis
        
        Args:
            uuid: 验证码标识
            code: 验证码
            expire_seconds: 过期时间（秒）
            
        Returns:
            bool: 是否存储成功
        """
        try:
            redis = await RedisUtil.get_redis_pool()
            if redis:
                await redis.setex(f"captcha:{uuid}", expire_seconds, code)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    async def verify_captcha_code(uuid: str, code: str) -> bool:
        """
        验证验证码
        
        Args:
            uuid: 验证码标识
            code: 用户输入的验证码
            
        Returns:
            bool: 验证是否成功
        """
        try:
            redis = await RedisUtil.get_redis_pool()
            if redis:
                stored_code = await redis.get(f"captcha:{uuid}")
                if stored_code and str(stored_code).upper() == str(code).upper():
                    # 验证成功后删除验证码
                    await redis.delete(f"captcha:{uuid}")
                    return True
            return False
        except Exception:
            return False
    
    @staticmethod
    async def generate_and_store_captcha(uuid: str, length: int = 4, expire_seconds: int = 300) -> dict:
        """
        生成并存储验证码
        
        Args:
            uuid: 验证码标识
            length: 验证码长度
            expire_seconds: 过期时间（秒）
            
        Returns:
            dict: 包含验证码和图片的字典
        """
        # 生成验证码
        code = CaptchaUtil.generate_captcha_code(length)
        
        # 生成图片
        image_base64 = CaptchaUtil.generate_captcha_image(code)
        
        # 存储到Redis
        success = await CaptchaUtil.store_captcha_code(uuid, code, expire_seconds)
        
        if success:
            return {
                'code': code,  # 开发环境返回验证码，生产环境应该不返回
                'image': image_base64,
                'uuid': uuid,
                'expire_seconds': expire_seconds
            }
        else:
            return {
                'code': None,
                'image': None,
                'uuid': uuid,
                'error': '存储验证码失败'
            }
    
    @staticmethod
    def generate_uuid() -> str:
        """
        生成验证码标识
        
        Returns:
            str: UUID字符串
        """
        import uuid
        return str(uuid.uuid4()) 