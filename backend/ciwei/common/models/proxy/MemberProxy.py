# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/26 下午3:21
@file: MemberProxy.py
@desc: 
"""


class MemberProxy:
    id = 0
    user_id = 0
    nickname = ''
    salt = ''
    credits = 0
    balance = 0
    mobile = ''
    name = ''
    location = ''
    sex = 1
    avatar = ''
    qr_code = ''
    left_notify_times = 0
    openid = ''
    status = 1
    updated_time = 0
    created_time = 1

    @property
    def has_qr_code(self):
        return self.qr_code != ""