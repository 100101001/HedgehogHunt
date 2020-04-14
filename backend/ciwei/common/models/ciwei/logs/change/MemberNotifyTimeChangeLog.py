# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/13 下午2:54
@file: MemberNotifyTimeChangeLog.py
@desc: 
"""

import decimal
from datetime import datetime

from sqlalchemy.dialects.mysql import INTEGER

from application import db


class MemberNotifyTimeChangeLog(db.Model):
    __tablename__ = 'member_notify_time_change_log'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '会员通知次数变更表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="会员id")
    openid = db.Column(db.String(80), nullable=False, default='', comment="第三方id")
    unit = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="通知次数变更多少")
    notify_times = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="通知次数变更之前的总量")
    note = db.Column(db.String(100), nullable=False, default='', comment="备注字段")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
