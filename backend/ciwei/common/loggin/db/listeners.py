# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/30 下午4:31
@file: listeners.py
@desc: 
"""
from flask_sqlalchemy import event

from common.libs import LogService
from common.models.ciwei.Member import Member
from common.models.ciwei.logs.change.MemberSmsPkgChangeLog import MemberSmsPkgChangeLog
from common.models.ciwei.mall.Product import Product


@event.listens_for(Member.left_notify_times, 'set')
def memberSmsChangeLog(target, new_val, old_val, *args):
    LogService.setMemberNotifyTimesChange(member_info=target, unit=new_val - old_val, old_times=old_val)


@event.listens_for(Member.balance, 'set')
def memberBalanceChangeLog(target, new_val, old_val, *args):
    LogService.setMemberBalanceChange(member_info=target, unit=new_val - old_val, old_balance=old_val)


@event.listens_for(MemberSmsPkgChangeLog.notify_times, 'set')
def memberSmPkgChangeLog(target, new_val, old_val, *args):
    LogService.setMemberSmsPkgChange(sms_pkg=target, unit=new_val - old_val, old_times=old_val)


@event.listens_for(Member.mobile, 'set')
def memberMobileChangeLog(target, new_val, old_val, *args):
    LogService.setMemberMobileChange(member_info=target, new_mobile=new_val, old_mobile=old_val)


@event.listens_for(Product.sale_cnt, 'set')
def productSaleChangeLog(target, new_val, old_val, *args):
    LogService.setProductSaleChange(product_id=target.id, product_num=new_val-old_val)
