# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/18 上午12:36
@file: __init__.py.py
@desc: 
"""
import logging


def getLoggingHandler():
    # 日志
    handler = logging.FileHandler('ciwei.log')
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    handler.setLevel(logging.DEBUG)