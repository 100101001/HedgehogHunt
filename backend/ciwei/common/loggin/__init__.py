# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/18 上午12:36
@file: __init__.py.py
@desc: 
"""
import logging, logging.handlers


def getLoggingHandler():
    """
    设置logging的格式，文件，logging级别
    :return:
    """
    # 日志每天新增一个文件
    handler = logging.handlers.TimedRotatingFileHandler('logs/ciwei', when='D', interval=1)
    handler.suffix = "%Y%m%d.log"
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(logging_format)
    handler.setLevel(logging.DEBUG)
    return handler


def getNormalLoggingHandler():
    # 日志
    handler = logging.FileHandler('ciwei.log')
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(logging_format)
    handler.setLevel(logging.DEBUG)
    return handler
