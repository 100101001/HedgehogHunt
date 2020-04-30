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
    def run_time(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        cost = time.time() - start
        # 2020-04-18 16:46:13,863 - WARNING - web.controllers.api.Goods - test9 - 耗时总计：0.3007230758666992
        if cost < 1:
            app.logger.info("{0} - {1} - 耗时总计：{2}".format(func.__module__, func.__name__, str(cost)))
        else:
            app.logger.warn("{0} - {1} - 耗时总计：{2}".format(func.__module__, func.__name__, str(cost)))
        return res
    return run_time
