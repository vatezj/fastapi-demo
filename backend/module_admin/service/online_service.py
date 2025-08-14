import jwt
from fastapi import Request
from config.enums import RedisInitKeyConfig
from config.env import JwtConfig
from config.get_redis import RedisUtil
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.online_vo import DeleteOnlineModel, OnlineQueryModel
from utils.common_util import CamelCaseUtil
from utils.log_util import logger


class OnlineService:
    """
    在线用户管理模块服务层
    """

    @classmethod
    async def get_online_list_services(cls, request: Request, query_object: OnlineQueryModel):
        """
        获取在线用户表信息service

        :param request: Request对象
        :param query_object: 查询参数对象
        :return: 在线用户列表信息
        """
        try:
            # 获取Redis连接
            redis = await RedisUtil.get_redis_pool()
            if not redis:
                logger.warning('Redis不可用，返回空在线用户列表')
                return []
            
            try:
                access_token_keys = await redis.keys(f'{RedisInitKeyConfig.ACCESS_TOKEN.key}*')
                if not access_token_keys:
                    access_token_keys = []
                
                access_token_values_list = []
                for key in access_token_keys:
                    try:
                        value = await redis.get(key)
                        if value:
                            access_token_values_list.append(value)
                    except Exception as e:
                        logger.warning(f'获取Redis键值失败: {key}, 错误: {e}')
                        continue
            except Exception as e:
                logger.warning(f'Redis操作失败: {e}')
                return []
            
            online_info_list = []
            for item in access_token_values_list:
                try:
                    payload = jwt.decode(item, JwtConfig.jwt_secret_key, algorithms=[JwtConfig.jwt_algorithm])
                    online_dict = dict(
                        token_id=payload.get('session_id'),
                        user_name=payload.get('user_name'),
                        dept_name=payload.get('dept_name'),
                        ipaddr=payload.get('login_info', {}).get('ipaddr'),
                        login_location=payload.get('login_info', {}).get('loginLocation'),
                        browser=payload.get('login_info', {}).get('browser'),
                        os=payload.get('login_info', {}).get('os'),
                        login_time=payload.get('login_info', {}).get('loginTime'),
                    )
                    
                    # 应用查询过滤条件
                    if query_object.user_name and not query_object.ipaddr:
                        if query_object.user_name == payload.get('user_name'):
                            online_info_list = [online_dict]
                            break
                    elif not query_object.user_name and query_object.ipaddr:
                        if query_object.ipaddr == payload.get('login_info', {}).get('ipaddr'):
                            online_info_list = [online_dict]
                            break
                    elif query_object.user_name and query_object.ipaddr:
                        if (query_object.user_name == payload.get('user_name') and 
                            query_object.ipaddr == payload.get('login_info', {}).get('ipaddr')):
                            online_info_list = [online_dict]
                            break
                    else:
                        online_info_list.append(online_dict)
                        
                except jwt.InvalidTokenError as e:
                    logger.warning(f'JWT令牌无效: {e}')
                    continue
                except Exception as e:
                    logger.warning(f'处理在线用户信息失败: {e}')
                    continue

            return CamelCaseUtil.transform_result(online_info_list)
            
        except Exception as e:
            logger.error(f'获取在线用户列表失败: {e}')
            return []

    @classmethod
    async def delete_online_services(cls, request: Request, page_object: DeleteOnlineModel):
        """
        强退在线用户信息service

        :param request: Request对象
        :param page_object: 强退在线用户对象
        :return: 强退在线用户校验结果
        """
        if not page_object.token_ids:
            raise ServiceException(message='传入session_id为空')
            
        try:
            # 获取Redis连接
            redis = await RedisUtil.get_redis_pool()
            if not redis:
                logger.warning('Redis不可用，跳过强退操作')
                return CrudResponseModel(is_success=True, message='强退成功（Redis不可用）')
            
            token_id_list = page_object.token_ids.split(',')
            for token_id in token_id_list:
                try:
                    await redis.delete(f'{RedisInitKeyConfig.ACCESS_TOKEN.key}:{token_id}')
                except Exception as e:
                    logger.warning(f'删除Redis键失败: {token_id}, 错误: {e}')
                    continue
                    
            return CrudResponseModel(is_success=True, message='强退成功')
            
        except Exception as e:
            logger.error(f'强退在线用户失败: {e}')
            raise ServiceException(message=f'强退失败: {str(e)}')
