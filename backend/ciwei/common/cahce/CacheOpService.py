# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 下午11:52
@file: CacheOpService.py
@desc: 
"""
import json

from common.cahce import redis_conn_db_1, CacheKeyGetter
from common.libs.Helper import queryToDict


def setMemberCache(member_info=None):
    """

    :param member_info:
    :return:
    """
    mem_key = CacheKeyGetter.memberKey(member_info.id)
    redis_conn_db_1.set(mem_key, json.dumps(queryToDict(member_info)))
    redis_conn_db_1.expire(mem_key, 3600)


def setMarkCache(goods_id=0, marks=None):
    """

    :param goods_id:
    :param marks:
    :return:
    """
    mark_key = CacheKeyGetter.markKey(goods_id)
    redis_conn_db_1.sadd(mark_key, -1)  # 占位符可以用来判断缓存中有
    mark_member_ids = set(i.member_id for i in marks)
    for m_id in mark_member_ids:
        redis_conn_db_1.sadd(mark_key, m_id)
    redis_conn_db_1.expire(mark_key, 3600)
    return mark_member_ids


def addPreMarkCache(goods_id=0, member_id=0):
    """

    :param goods_id:
    :param member_id:
    :return:
    """
    mark_key = CacheKeyGetter.markKey(goods_id)
    redis_conn_db_1.sadd(mark_key, member_id)
    redis_conn_db_1.expire(mark_key, 3600)


def removePreMarkCache(found_ids=None, member_id=0):
    """
    记录
    :param found_ids:
    :param member_id:
    :return:
    """
    for found_id in found_ids:
        m_key = CacheKeyGetter.markKey(found_id)
        redis_conn_db_1.srem(m_key, member_id)
        redis_conn_db_1.expire(m_key, 3600)
