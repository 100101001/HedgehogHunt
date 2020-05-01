# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/1 下午2:26
@file: __init__.py.py
@desc: 
"""

from flask import Blueprint

from application import db, app

exception = Blueprint('exception', __name__)


@exception.app_errorhandler(Exception)
def rollbackOnException(e):
    db.session.rollback()
    app.logger.error(str(e))
    return {'code': -1, 'msg': '服务异常，请稍后使用'}
