# 定义异常处理函数

import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

# 开发模式：返回详细错误信息
# 生产模式：返回简化错误信息
# 参数--DEBUG_MODE是否是开发模式
DEBUG_MODE = True

# 处理 HTTPException 异常
# 所需参数：
# request--请求对象
# exc--异常对象
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            # HTTPException 通常是业务逻辑主动抛出的，data保持 None
            "data": None
        }
    )

#处理数据库完整性的约束错误
async def integrity_error_handler(request: Request, exc: IntegrityError):
    #
    error_msg = str(exc.orig)
    #判断具体的约束错误类型
    #先判断是否是用户名已存在--唯一性
    if "username_UNIQUE" in error_msg or "Duplicate entry" in error_msg:
        detail = "用户名已存在"
    #再判断外键是否关联失败
    elif "FOREIGN KEY" in error_msg:
        detail = "关联数据不存在"
    #否则，其他错误
    else:
        detail = "数据约束冲突，请检查输入"
    #开发模式下返回详细错误信息
    error_data = None
    if DEBUG_MODE:
        error_data = {
            # 打印错误类型
            "error_type": "IntegrityError",
            # 打印错误详细信息
            "error_detail": error_msg,
            # 打印具体哪里的url错误了
            "path": str(request.url)
        }
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "message": detail,
            "data": error_data
        }
    )

#处理 SQLAlchemy 数据库错误
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    error_data =  None
    if DEBUG_MODE:
        error_data = {
            # 打印错误类型
            "error_type": type(exc).__name__,
            # 打印错误详细信息
            "error_detail": str(exc),
            # 格式化异常信息为字符串，方便日志记录和调试
            "traceback": traceback.format_exc(),
            # 获取具体哪里的url错误了
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            # 返回错误码
            "code": 500,
            # 错误信息
            "message": "数据库错误",
            # 错误数据
            "data": error_data
        }
    )

#处理所有未捕获的异常
async def general_exception_handler(request: Request, exc: Exception):
    error_data = None
    if DEBUG_MODE:
        error_data = {
            # 错误类型
            "error_type": type(exc).__name__,
            # 错误详细信息
            "error_detail": str(exc),
            # 格式化异常信息为字符串，方便日志记录和调试
            "traceback": traceback.format_exc(),
            # 获取具体哪里的url错误了
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            # 错误码
            "code": 500,
            # 错误信息
            "message": "服务器内部错误",
            # 错误数据
            "data": error_data
        }
    )




