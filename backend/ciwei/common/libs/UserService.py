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
from common.models.ciwei.Member import Member
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


def addNewUser(reg_info=None, member_id=0):
    """
    新增管理员用户
    :param reg_info:
    :param member_id:
    :return:
    """
    if isUserExist(member_id):
        return False, '管理员已存在'
    member_info = Member.query.filter_by(id=member_id).first()
    if not member_info:
        return False, '用户不存在'
    user = User()
    user.name = reg_info.get('name', '')
    user.mobile = reg_info.get('mobile', '')
    user.email = reg_info.get('email', '')
    user.level = reg_info.get('level', 1)
    user.sex = member_info.sex
    user.avatar = member_info.avatar
    user.member_id = member_info.id

    db.session.add(user)
    db.session.commit()
    CacheOpService.setUsersCache(users=[user])
    return True, '添加成功'


def isUserExist(member_id=0):
    """
    判断用户已存在
    :param member_id:
    :return:
    """
    user = CacheQueryService.getUserCache(member_id)
    if not user:
        user = User.query.filter_by(member_id=member_id).first()
    return user is not None


def deleteUser(member_id=0):
    User.query.filter_by(member_id=member_id).delete(synchronize_session=False)
    db.session.commit()
    CacheOpService.delUserCache(member_id)
