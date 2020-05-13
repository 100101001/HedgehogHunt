# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/1 下午3:07
@file: __init__.py.py
@desc: 
"""
from datetime import datetime

from application import app


class ConflictException(Exception):
    def __init__(self, log_error=None, func_name=None):
        self.log_error = log_error
        self.func_name = func_name
        self.at = datetime.now()

    def log(self):
        app.logger.error('{0} 在 {1} 抛出了服务异常 {2}'.format(self.func_name, self.at, self.log_error))
