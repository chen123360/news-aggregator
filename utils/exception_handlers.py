#把四个异常处理封装为一个函数

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from utils.exception import http_exception_handler, integrity_error_handler, sqlalchemy_error_handler, general_exception_handler

#注册全局异常处理函数: 顺序--子类在前，父类在后；具体的在前面，抽象的在后面
def register_exception_handlers(app):
    # 业务层面报错
    app.add_exception_handler(HTTPException, http_exception_handler)
    # 数据完整性约束
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    # 数据库
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    # 兜底
    app.add_exception_handler(Exception, general_exception_handler)





