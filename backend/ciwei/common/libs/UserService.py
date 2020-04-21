# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/20 上午4:24
@file: UserService.py
@desc: 
"""
from application import db
from common.cahce import CacheQueryService, CacheOpService
from common.models.ciwei.User import User


def getAllUsers():
    """
    返回所有管理员缓存
    :return:
    """
    users = CacheQueryService.getAllUserCache()
    if not users:
        users = User.query.order_by(User.level.asc()).all()
        CacheOpService.setUsersCache(users=users)
    return users


def getUser(member_id=0):
    """
    返回管理员缓存
    :param member_id:
    :return:
    """
    user = CacheQueryService.getUserCache(member_id=member_id)
    if not user:
        user = User.query.filter_by(member_id=member_id).first()
        CacheOpService.setUsersCache(users=[user])
    return user


def addNewUser(user_info=None, member_info=None):
    """
    新增管理员用户
    :param user_info:
    :param member_info:
    :return:
    """
    user = User()
    user.name = user_info.get('name', '')
    user.mobile = user_info.get('mobile', '')
    user.email = user_info.get('email', '')
    user.level = user_info.get('level')
    user.sex = member_info.sex
    user.avatar = member_info.avatar
    user.member_id = member_info.id

    db.session.add(user)
    db.session.commit()
    CacheOpService.setUsersCache(users=[user])
