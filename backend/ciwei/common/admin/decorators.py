# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/30 下午1:04
@file: time.py
@desc: 
"""

from functools import wraps

from common.admin import UserService


def user_op(func):
    @wraps
    def validateUser(member_id=0, level=None, **kwargs):
        user = UserService.getUserByMid(member_id)
        if not user:
            return False, "您不是管理员，无权进行此操作"
        if level is not None and level < user.level:
            return False, "您权限过低，无权进行此操作"
        return func(member_id=member_id, user=user, **kwargs)
    return validateUser
