from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic_validation_decorator import FieldValidationError
from exceptions.exception import (
    AuthException,
    LoginException,
    ModelValidatorException,
    PermissionException,
    ServiceException,
    ServiceWarning,
)
from utils.log_util import logger
from utils.response_util import jsonable_encoder, JSONResponse, ResponseUtil
from datetime import datetime


def handle_exception(app: FastAPI):
    """
    全局异常处理
    """

    # 自定义token检验异常 - 最高优先级
    @app.exception_handler(AuthException)
    async def auth_exception_handler(request: Request, exc: AuthException):
        logger.warning(f'AuthException被捕获: {exc.message}')
        return ResponseUtil.unauthorized(data=exc.data, msg=exc.message)

    # 自定义登录检验异常
    @app.exception_handler(LoginException)
    async def login_exception_handler(request: Request, exc: LoginException):
        logger.warning(f'LoginException被捕获: {exc.message}')
        return ResponseUtil.failure(data=exc.data, msg=exc.message)

    # 自定义模型检验异常
    @app.exception_handler(ModelValidatorException)
    async def model_validator_exception_handler(request: Request, exc: ModelValidatorException):
        logger.warning(f'ModelValidatorException被捕获: {exc.message}')
        return ResponseUtil.failure(data=exc.data, msg=exc.message)

    # 自定义字段检验异常
    @app.exception_handler(FieldValidationError)
    async def field_validation_error_handler(request: Request, exc: FieldValidationError):
        logger.warning(f'FieldValidationError被捕获: {exc.message}')
        return ResponseUtil.failure(msg=exc.message)

    # Pydantic验证异常处理
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f'RequestValidationError被捕获: {exc.errors()}')
        
        # 提取第一个验证错误
        if exc.errors():
            first_error = exc.errors()[0]
            field_name = " -> ".join(str(loc) for loc in first_error["loc"])
            error_type = first_error["type"]
            error_msg = first_error["msg"]
            
            # 根据错误类型生成友好的错误消息
            if error_type == "string_too_short":
                min_length = first_error.get("ctx", {}).get("min_length", 0)
                error_msg = f"{field_name}长度不能少于{min_length}个字符"
            elif error_type == "string_too_long":
                max_length = first_error.get("ctx", {}).get("max_length", 0)
                error_msg = f"{field_name}长度不能超过{max_length}个字符"
            elif error_type == "missing":
                error_msg = f"缺少必填字段: {field_name}"
            elif error_type == "value_error":
                error_msg = f"{field_name}格式错误: {error_msg}"
            else:
                error_msg = f"{field_name}: {error_msg}"
            
            # 返回400状态码的错误响应
            from fastapi.responses import JSONResponse
            error_response = ResponseUtil.error(msg=error_msg)
            # 直接返回修改状态码的响应
            error_response.status_code = 400
            return error_response
        
        # 如果没有具体错误信息，返回通用错误
        from fastapi.responses import JSONResponse
        error_response = ResponseUtil.error(msg="请求参数验证失败")
        # 直接返回修改状态码的响应
        error_response.status_code = 400
        return error_response

    # 自定义权限检验异常
    @app.exception_handler(PermissionException)
    async def permission_exception_handler(request: Request, exc: PermissionException):
        logger.warning(f'PermissionException被捕获: {exc.message}')
        return ResponseUtil.forbidden(data=exc.data, msg=exc.message)

    # 自定义服务异常
    @app.exception_handler(ServiceException)
    async def service_exception_handler(request: Request, exc: ServiceException):
        logger.error(f'ServiceException被捕获: {exc.message}')
        return ResponseUtil.error(data=exc.data, msg=exc.message)

    # 自定义服务警告
    @app.exception_handler(ServiceWarning)
    async def service_warning_handler(request: Request, exc: ServiceWarning):
        logger.warning(f'ServiceWarning被捕获: {exc.message}')
        return ResponseUtil.failure(data=exc.data, msg=exc.message)

    # 处理其他http请求异常
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f'HTTPException被捕获: {exc.status_code} - {exc.detail}')
        
        # 根据状态码生成友好的错误消息
        if exc.status_code == 401:
            msg = "认证失败，请重新登录"
        elif exc.status_code == 403:
            msg = "权限不足，无法访问"
        elif exc.status_code == 404:
            msg = "请求的资源不存在"
        elif exc.status_code == 422:
            msg = "请求参数验证失败"
        elif exc.status_code == 500:
            msg = "服务器内部错误，请稍后重试"
        else:
            msg = exc.detail or "请求处理失败"
        
        # 返回统一的错误格式
        return JSONResponse(
            content=jsonable_encoder({
                'code': exc.status_code, 
                'msg': msg,
                'detail': exc.detail,
                'success': False,
                'timestamp': datetime.now().isoformat()
            }), 
            status_code=exc.status_code
        )

    # 处理其他异常 - 最低优先级，添加详细日志
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        logger.error(f'通用Exception被捕获: {type(exc).__name__} - {str(exc)}')
        logger.error(f'请求路径: {request.url.path}')
        logger.error(f'请求方法: {request.method}')
        logger.exception(exc)
        
        # 根据异常类型生成友好的错误消息
        if "database" in str(exc).lower() or "connection" in str(exc).lower():
            msg = "数据库连接异常，请稍后重试"
        elif "redis" in str(exc).lower():
            msg = "缓存服务异常，请稍后重试"
        elif "greenlet" in str(exc).lower():
            msg = "系统服务异常，请稍后重试"
        elif "timeout" in str(exc).lower():
            msg = "请求超时，请稍后重试"
        else:
            msg = "系统异常，请稍后重试"
        
        return JSONResponse(
            content=jsonable_encoder({
                'code': 500,
                'msg': msg,
                'detail': str(exc),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }), 
            status_code=500
        )
