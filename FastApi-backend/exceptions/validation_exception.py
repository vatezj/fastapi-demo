"""
验证异常处理器
统一处理Pydantic验证错误，返回标准API格式
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from utils.response_util import ResponseUtil
import traceback


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理Pydantic验证异常，返回统一的API错误格式
    
    Args:
        request: FastAPI请求对象
        exc: 验证异常对象
        
    Returns:
        JSONResponse: 统一的错误响应格式
    """
    # 提取第一个验证错误
    if exc.errors():
        first_error = exc.errors()[0]
        field_name = " -> ".join(str(loc) for loc in first_error["loc"])
        error_type = first_error["type"]
        error_msg = first_error["msg"]
        input_value = first_error.get("input", "")
        
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
        
        # 返回统一的错误格式
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ResponseUtil.error(error_msg).dict()
        )
    
    # 如果没有具体错误信息，返回通用错误
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ResponseUtil.error("请求参数验证失败").dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    处理通用异常，返回统一的API错误格式
    
    Args:
        request: FastAPI请求对象
        exc: 异常对象
        
    Returns:
        JSONResponse: 统一的错误响应格式
    """
    # 记录异常堆栈信息（生产环境应该记录到日志文件）
    error_traceback = traceback.format_exc()
    print(f"异常详情: {error_traceback}")
    
    # 根据异常类型生成友好的错误消息
    if "client" in str(exc).lower():
        error_msg = "请求对象错误，请联系管理员"
    elif "database" in str(exc).lower():
        error_msg = "数据库操作失败，请稍后重试"
    elif "redis" in str(exc).lower():
        error_msg = "缓存服务异常，请稍后重试"
    elif "validation" in str(exc).lower():
        error_msg = "数据验证失败，请检查输入"
    else:
        error_msg = f"系统异常: {str(exc)}"
    
    # 返回统一的错误格式
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ResponseUtil.error(error_msg).dict()
    )


def setup_exception_handlers(app):
    """
    设置异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    # 注册验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 注册通用异常处理器
    app.add_exception_handler(Exception, general_exception_handler) 