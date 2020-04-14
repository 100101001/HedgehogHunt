# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/13 下午11:39
@file: LogTasks.py
@desc: 
"""
from application import celery
from common.libs import LogService


@celery.task(name="log.wechat.subscribe")
def addWechatApiCallLog(url='', token='', req_data=None, resp_data=None):
    """
    不重要的日志的记录,微信调用日志
    :param url:
    :param token:
    :param req_data:
    :param resp_data:
    :return:
    """
    LogService.addWechatApiCallLog(url=url.split('?')[0], token=token, req_data=req_data, resp_data=resp_data)