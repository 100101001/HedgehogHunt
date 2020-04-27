# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/26 下午9:46
@file: __init__.py.py
@desc: 
"""
from flask_sqlalchemy import event

from common.libs import LogService
from common.models.ciwei.Member import Member


@event.listens_for(Member.left_notify_times, 'set')
def smsChangeLog(target, new_val, old_val, *args):
    LogService.setMemberNotifyTimesChange(unit=new_val-old_val, old_times=old_val)