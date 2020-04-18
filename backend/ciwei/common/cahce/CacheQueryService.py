# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 下午11:49
@file: CacheQueryService.py
@desc: 
"""
import json

from common.cahce import redis_conn_db_1, CacheKeyGetter
from common.models.ciwei.Member import Member


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


def getMemberCache(member_id=0):
    """
    从缓存获取序列化的会员信息，反序列化后返回
    :param member_id:
    :return:
    """
    member_info = None
    mem_key = CacheKeyGetter.memberKey(member_id)
    member_str = redis_conn_db_1.get(mem_key)
    if member_str:
        # 缓存命中
        member_info = Member()
        member_info.__dict__ = json.loads(member_str)
    return member_info
