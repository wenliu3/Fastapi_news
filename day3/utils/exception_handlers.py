from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from day3.utils.exception import http_exception_handler, integrity_error_handler, sqlalchemy_error_handler, \
    general_exception_handler


def register_exception_handlers(app):
    app.add_exception_handler(HTTPException, http_exception_handler) # 业务层面
    app.add_exception_handler(IntegrityError, integrity_error_handler) # 数据完整性层面
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler) # 数据库层面
    app.add_exception_handler(Exception, general_exception_handler) # 默认处理
