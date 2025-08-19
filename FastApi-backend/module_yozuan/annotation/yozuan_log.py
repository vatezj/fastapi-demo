"""
游赚模块操作日志装饰器
基于 module_admin 的 Log 装饰器，为游赚模块后台管理接口提供操作日志记录
"""

import inspect
import json
import os
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Literal, Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from module_admin.entity.vo.log_vo import OperLogModel
from module_admin.service.log_service import OperationLogService
from module_admin.service.login_service import LoginService
from utils.log_util import logger


class YozuanLog:
    """
    游赚模块操作日志装饰器
    
    继承 module_admin 的日志记录功能，为游赚模块提供专门的操作日志记录
    """

    def __init__(
        self,
        title: str,
        business_type: BusinessType,
        log_type: Literal['operation'] = 'operation',
    ):
        """
        游赚模块操作日志装饰器

        :param title: 当前日志装饰器装饰的模块标题，例如：'任务管理'、'订单管理'
        :param business_type: 业务类型（INSERT新增 UPDATE修改 DELETE删除 GRANT授权 EXPORT导出 IMPORT导入 FORCE强退 GENCODE生成代码 CLEAN清空数据）
        :param log_type: 日志类型（固定为operation，游赚模块只记录操作日志）
        """
        self.title = title
        self.business_type = business_type.value
        self.log_type = log_type

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            
            # 获取被装饰函数的文件路径
            file_path = inspect.getfile(func)
            # 获取项目根路径
            project_root = os.getcwd()
            # 处理文件路径，去除项目根路径部分
            relative_path = os.path.relpath(file_path, project_root)[0:-2].replace('\\', '.').replace('/', '.')
            # 获取当前被装饰函数所在路径
            func_path = f'{relative_path}{func.__name__}()'
            
            # 获取上下文信息
            request = None
            query_db = None
            
            # 查找 Request 参数
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            # 查找 AsyncSession 参数
            for arg in args:
                if isinstance(arg, AsyncSession):
                    query_db = arg
                    break
            
            # 如果没有找到，从 kwargs 中查找
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not query_db:
                for key, value in kwargs.items():
                    if isinstance(value, AsyncSession):
                        query_db = value
                        break
            
            if not request or not query_db:
                logger.warning(f"YozuanLog装饰器无法获取Request或AsyncSession参数: {func.__name__}")
                return await func(*args, **kwargs)
            
            # 获取请求信息
            token = request.headers.get('Authorization')
            request_method = request.method
            operator_type = 1  # 默认后台用户
            
            # 获取请求的URL
            oper_url = request.url.path
            # 获取请求的IP
            oper_ip = request.headers.get('X-Forwarded-For') or request.client.host
            oper_location = '内网IP'  # 简化处理，实际可以集成IP地理位置查询
            
            # 获取请求参数
            content_type = request.headers.get('Content-Type', '')
            oper_param = {}
            
            try:
                if 'multipart/form-data' in content_type or 'application/x-www-form-urlencoded' in content_type:
                    payload = await request.form()
                    oper_param = {key: str(value) for key, value in payload.items()}
                else:
                    # 获取路径参数
                    path_params = request.path_params
                    if path_params:
                        oper_param.update(path_params)
                    
                    # 获取请求体参数
                    try:
                        body = await request.body()
                        if body:
                            body_data = json.loads(body.decode('utf-8'))
                            oper_param.update(body_data)
                    except:
                        pass
                
                # 转换为JSON字符串
                oper_param = json.dumps(oper_param, ensure_ascii=False)
                
                # 日志表请求参数字段长度最大为2000，因此在此处判断长度
                if len(oper_param) > 2000:
                    oper_param = '请求参数过长'
                    
            except Exception as e:
                oper_param = f'参数解析失败: {str(e)}'
            
            # 获取操作时间
            oper_time = datetime.now()
            
            try:
                # 执行原始函数
                result = await func(*args, **kwargs)
                
                # 记录成功日志
                status = 0  # 成功
                json_result = json.dumps(result, ensure_ascii=False) if result else ''
                error_msg = ''
                
                # 截断返回结果，避免日志过长
                if len(json_result) > 2000:
                    json_result = '返回结果过长'
                    
            except Exception as e:
                # 记录失败日志
                status = 1  # 异常
                json_result = ''
                error_msg = str(e)
                logger.error(f"游赚模块操作异常: {e}")
                
                # 重新抛出异常
                raise
            
            # 计算执行时间
            cost_time = int((time.perf_counter() - start_time) * 1000)  # 转换为毫秒
            
            try:
                # 获取当前用户信息
                current_user = await LoginService.get_current_user(request, token, query_db)
                oper_name = current_user.user.user_name
                dept_name = current_user.user.dept.dept_name if current_user.user.dept else None
                
                # 创建操作日志记录
                operation_log = OperLogModel(
                    title=f"游赚模块-{self.title}",
                    businessType=self.business_type,
                    method=func_path,
                    requestMethod=request_method,
                    operatorType=operator_type,
                    operName=oper_name,
                    deptName=dept_name,
                    operUrl=oper_url,
                    operIp=oper_ip,
                    operLocation=oper_location,
                    operParam=oper_param,
                    jsonResult=json_result,
                    status=status,
                    errorMsg=error_msg,
                    operTime=oper_time,
                    costTime=cost_time,
                )
                
                # 记录操作日志
                await OperationLogService.add_operation_log_services(query_db, operation_log)
                logger.info(f"游赚模块操作日志记录成功: {self.title} - {func.__name__}")
                
            except Exception as e:
                # 日志记录失败不影响业务功能
                logger.error(f"游赚模块操作日志记录失败: {e}")
            
            return result
        
        return wrapper


# 为游赚模块提供便捷的日志装饰器
def yozuan_task_log(business_type: BusinessType):
    """任务管理日志装饰器"""
    return YozuanLog("任务管理", business_type)

def yozuan_order_log(business_type: BusinessType):
    """订单管理日志装饰器"""
    return YozuanLog("订单管理", business_type)

def yozuan_user_log(business_type: BusinessType):
    """用户管理日志装饰器"""
    return YozuanLog("用户管理", business_type)

def yozuan_finance_log(business_type: BusinessType):
    """财务管理日志装饰器"""
    return YozuanLog("财务管理", business_type)

def yozuan_system_log(business_type: BusinessType):
    """系统管理日志装饰器"""
    return YozuanLog("系统管理", business_type)
