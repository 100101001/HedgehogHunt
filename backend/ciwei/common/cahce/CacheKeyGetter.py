# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/17 下午6:49
@file: CacheKeyGetter.py
@desc: 
"""


def memberKey(member_id=0):
    """
    db1 中缓存的会员
    :param member_id:
    :return:
    """
    return "member_{0}".format(member_id)


def goodsEditKey(goods_id=0):
    """
    db1 中缓存的 edit good status
    :param goods_id:
    :return:
    """
    return "edit_{0}_status".format(goods_id)


def markKey(goods_id=0):
    """
    db1 中缓存的mark
    :param goods_id:
    :return:
    """
    return "mark_{0}".format(goods_id)


def goodsReadKey(goods_id=0):
    """
    db1 中缓存的文章阅读量
    :param goods_id:
    :return:
    """
    return "read_{0}".format(goods_id)


def goodsReadKeyPrefixPattern():
    """
    db1 中缓存的所有阅读量的key
    :return:
    """
    return "read_*"


def allUserKey():
    return "all_users"


def isAllUserKey():
    """

    :return:
    """
    return "is_all"


def wxTokenKey():
    return "wechat_token"
