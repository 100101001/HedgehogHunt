# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 下午11:49
@file: CacheQueryService.py
@desc: 
"""
from common.cahce import redis_conn_db_1, CacheKeyGetter


def getMarkCache(goods_id=0):
    """
    获取缓存中的认领member_id set
    :param goods_id:
    :return:
    """
    mark_key = CacheKeyGetter.markKey(goods_id)
    marks = redis_conn_db_1.smembers(mark_key)
    redis_conn_db_1.expire(mark_key, 3600)
    return marks
