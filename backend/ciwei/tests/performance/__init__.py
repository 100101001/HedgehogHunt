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
