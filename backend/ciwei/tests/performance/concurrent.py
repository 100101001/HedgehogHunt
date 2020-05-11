# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/12 上午1:19
@file: concurrent.py
@desc:  http://docs.python-requests.org/zh_CN/latest/user/quickstart.html
# https://cloud.tencent.com/developer/article/1578759
# https://git.weixin.qq.com/minitest/minium-doc/tree/master
"""


# 同一接口的并发请求，检查功能与性能
import requests

from tests.performance import response_time

class ConcurrentTest:


    @classmethod
    @response_time
    def login(cls, ):
        url = ''
        requests.post(url=url, data={}, headers={})


