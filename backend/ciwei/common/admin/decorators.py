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
    @wraps(func)
    def validateUser(*args, **kwargs):
        member_id = kwargs.get('member_id')
        user = UserService.getUserByMid(member_id)
        if not user:
            return False, "您不是管理员，无权进行此操作"
        level = kwargs.get('level')
        if level is not None and int(level) < user.level:
            return False, "您权限过低，无权进行此操作"
        res = func(*args, user=user, **kwargs)
        return res if res else (True, '操作成功')
    return validateUser
