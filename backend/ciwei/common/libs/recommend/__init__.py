# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/10 下午5:27
@file: __init__.py.py
@desc: 建立ES索引和index；建立redis的连接。
"""
from application import es


class RecommendServiceStartUp:
    def __init__(self):
        self.es = es



