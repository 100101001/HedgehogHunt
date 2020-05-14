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
    # 记录请求的API的响应时间
    @wraps(func)
    def run_time(*args, **kwargs):
        logger = args[0].f
        start = time.time()
        func(*args, **kwargs)
        cost = time.time() - start
        logger.write('{} 请求的响应时间为 {} 秒\n'.format(func.__name__, round(cost, 4)))
        return cost

    return run_time


def loop_call_duration(func):
    # 记录向线程池提交异步并发任务耗时
    @wraps(func)
    def run_time(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        cost = time.time() - start
        return cost

    return run_time


def concurrent_output(func):
    # 记录并发测试的平均响应时间
    @wraps(func)
    def test_output(*args, **kwargs):
        logger = args[0].f
        logger.write('在 {} 秒的时间内异步发出 {} 个并发 {} 请求的平均响应时间为 {} 秒\n'.format(*func(*args, **kwargs)))

    return test_output


def log_api_param(func):
    @wraps(func)
    def log_param(*args, **kwargs):
        logger = args[0].f
        url = func(*args, **kwargs)
        logger.write('请求URL: {}\n'.format(url))
        return url
    return log_param
