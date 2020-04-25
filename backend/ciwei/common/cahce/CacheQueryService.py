# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 下午11:49
@file: CacheQueryService.py
@desc: 
"""
import json

from application import APP_CONSTANTS
from common.cahce import redis_conn_db_1, CacheKeyGetter
from common.models.ciwei.Member import Member
from common.models.ciwei.User import User


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
        redis_conn_db_1.expire(mem_key, 3600)
    return member_info



def getUserCache(member_id=0):
    """
    根据member_id获取单个管理员用户缓存
    :param member_id:
    :return:
    """
    user = None
    user_key = CacheKeyGetter.allUserKey()
    user_str = redis_conn_db_1.hget(user_key, member_id)
    if user_str:
        user = User()
        user.__dict__ = json.loads(user_str)
        redis_conn_db_1.expire(user_key, 3600)
    return user


def getAllUserCache():
    """
    获取所有管理员用户
    :return:
    """
    is_all_key = CacheKeyGetter.isAllUserKey()
    user_key = CacheKeyGetter.allUserKey()
    is_all = redis_conn_db_1.hget(user_key, is_all_key)
    if not is_all:
        # 并不包含所有管理员
        return None
    users = redis_conn_db_1.hvals(user_key)
    real_users = []
    for item in users:
        if item == APP_CONSTANTS['is_all_user_val']:
            continue
        user = User()
        user.__dict__ = json.loads(item)
        real_users.append(user)
    redis_conn_db_1.expire(user_key, 3600)
    return real_users


def getGoodsIncrReadCache(goods_id=0):
    """
    获取当天新增的阅读量
    :param goods_id:
    :return:
    """
    read_key = CacheKeyGetter.goodsReadKey(goods_id)
    read_cnt = redis_conn_db_1.get(read_key)
    return int(read_cnt) if read_cnt else 0


def getWxToken():
    wx_token_key = CacheKeyGetter.wxTokenKey()
    return redis_conn_db_1.get(wx_token_key)
