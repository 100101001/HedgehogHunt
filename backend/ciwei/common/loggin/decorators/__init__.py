# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/18 上午12:14
@file: __init__.py.py
@desc: 
"""
import time
from functools import wraps

from application import app


def time_log(func):
    @wraps(func)
    def run_time():
        start = time.time()
        func()
        cost = time.time() - start
        app.logger.warn("耗时总计：{0}".format(str(cost)))
    return run_time
