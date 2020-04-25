# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/24 下午11:10
@file: CacheOpUtil.py
@desc: 
"""


def updateModelDict(model=None, updated=None):
    model_dict = model.__dict__
    model_dict.update(updated)
