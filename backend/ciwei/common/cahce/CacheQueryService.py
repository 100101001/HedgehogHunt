# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 下午11:49
@file: CacheQueryService.py
@desc: 
"""
from application import cache
from common.models.ciwei.Member import Member


@cache.memoize()
def getMemberById(member_id=0):
    return Member.query.filter_by(id=member_id).first()


@cache.memoize()
def getMemberByOpenid(openid=''):
    return Member.query.filter_by(openid=openid).first()


@cache.memoize()
def getLostNotifyByMemberMobile(member_id):
    pass
