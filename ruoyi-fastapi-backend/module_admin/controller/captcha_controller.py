import uuid
from datetime import timedelta
from fastapi import APIRouter, Request
from config.enums import RedisInitKeyConfig
from config.get_redis import RedisUtil
from module_admin.entity.vo.login_vo import CaptchaCode
from module_admin.service.captcha_service import CaptchaService
from utils.response_util import ResponseUtil
from utils.log_util import logger


captchaController = APIRouter()


@captchaController.get('/captchaImage')
async def get_captcha_image(request: Request):
    # 检查Redis是否已初始化
    redis = await RedisUtil.get_redis_pool()
    if not redis:
        logger.warning('Redis未初始化，使用默认配置')
        captcha_enabled = True
        register_enabled = True
    else:
        try:
            captcha_enabled = (
                True
                if await redis.get(f'{RedisInitKeyConfig.SYS_CONFIG.key}:sys.account.captchaEnabled')
                == 'true'
                else False
            )
            register_enabled = (
                True
                if await redis.get(f'{RedisInitKeyConfig.SYS_CONFIG.key}:sys.account.registerUser') == 'true'
                else False
            )
        except Exception as e:
            logger.error(f'从Redis获取配置失败：{e}，使用默认配置')
            captcha_enabled = True
            register_enabled = True
    
    session_id = str(uuid.uuid4())
    captcha_result = await CaptchaService.create_captcha_image_service()
    image = captcha_result[0]
    computed_result = captcha_result[1]
    
    # 如果Redis可用，则存储验证码
    if redis:
        try:
            await redis.set(
                f'{RedisInitKeyConfig.CAPTCHA_CODES.key}:{session_id}', computed_result, ex=timedelta(minutes=2)
            )
            logger.info(f'编号为{session_id}的会话获取图片验证码成功')
        except Exception as e:
            logger.error(f'存储验证码到Redis失败：{e}')
    else:
        logger.warning('Redis不可用，验证码无法存储')
    
    return ResponseUtil.success(
        model_content=CaptchaCode(
            captchaEnabled=captcha_enabled, registerEnabled=register_enabled, img=image, uuid=session_id
        )
    )
