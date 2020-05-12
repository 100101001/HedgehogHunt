# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/12 上午1:00
@file: __init__.py.py
@desc: 
"""

import time
from functools import wraps


def response_time(func):
    @wraps(func)
    def run_time(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        cost = time.time() - start
        return cost

    return run_time


def concurrent_output(func):
    @wraps(func)
    def test_output(*args, **kwargs):
        logger = args[0].f
        logger.write('在 {} 秒的时间内， {} 个并发 {} 请求的平均响应时间为 {} 秒\n'.format(*func(*args, **kwargs)))

    return test_output
