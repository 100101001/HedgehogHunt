# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/20 上午4:24
@file: UserService.py
@desc: 
"""
from application import db
from common.cahce import CacheOpUtil
from common.cahce.core import CacheQueryService, CacheOpService
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
        CacheOpService.setUsersCache(users=users, is_all=True)
    return users


def getUserByMid(member_id=0):
    """
    根据member_id返回管理员
    :param member_id:
    :return:
    """
    user = CacheQueryService.getUserCache(member_id=member_id)
    if not user:
        user = User.query.filter_by(member_id=member_id).first()
        CacheOpService.setUsersCache(users=[user])
    return user


def getUserByUid(user_id=0):
    """
    根据user_id返回管理员
    :param user_id:
    :return:
    """

    users = getAllUsers()
    target_user = None
    for user in users:
        if user.uid == user_id:
            target_user = user
            break
    return target_user


def addNewUser(reg_info=None, member_id=0, op_member_id=0):
    """
    新增管理员用户
    :param op_member_id:
    :param reg_info:
    :param member_id:
    :return:
    """

    new_user_level = reg_info.get('level', 1)
    op_user = getUserByMid(op_member_id)
    if op_user.level > new_user_level:
        return False, '您不能添加权限高于自身的管理员'
    if getUserByMid(member_id):
        return False, '管理员已存在，请勿重复操作'
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
    user.op_uid = op_user.uid  # 操作新增管理员的管理员ID
    db.session.add(user)
    db.session.commit()
    CacheOpService.setUsersCache(users=[user])
    return True, '添加成功'


def blockUser(blk_member_id=0, op_member_id=0):
    if blk_member_id == op_member_id:
        return False, "您不能冻结自己的账户"
    blk_user = getUserByMid(member_id=blk_member_id)
    op_user = getUserByMid(member_id=op_member_id)
    if blk_user.level < op_user.level:
        return False, "您的级别过低，无权进行此操作"
    # 更新数据库有效标示
    updated = {'status': 0, 'op_uid': op_user.uid}
    User.query.filter_by(member_id=blk_member_id).update(updated, synchronize_session=False)
    db.session.commit()
    # 存到缓存
    CacheOpUtil.updateModelDict(model=blk_user, updated=updated)
    CacheOpService.setUsersCache(users=[blk_user])
    return True, "操作成功"


def restoreUser(restore_member_id=0, op_member_id=0):
    if restore_member_id == op_member_id:
        return False, "您不能解冻自己的账户"
    restore_user = getUserByMid(member_id=restore_member_id)
    op_user = getUserByMid(member_id=op_member_id)
    blk_op_user = getUserByUid(user_id=restore_user.op_uid)
    if blk_op_user.level < op_user.level:
        return False, "您的级别过低，无权进行此操作"
    # 更新数据库有效标示
    updated = {'status': 1, 'op_uid': op_user.uid}
    User.query.filter_by(member_id=restore_member_id).update(updated,
                                                         synchronize_session=False)
    db.session.commit()
    # 存到缓存
    CacheOpUtil.updateModelDict(model=restore_user, updated=updated)
    CacheOpService.setUsersCache(users=[restore_user])
    return True, "操作成功"
