# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/13 上午12:00
@file: MemberPhoneChangeLog.py
@desc: 
"""

from datetime import datetime

from sqlalchemy.dialects.mysql import INTEGER

from application import db


class MemberPhoneChangeLog(db.Model):
    __tablename__ = 'member_phone_change_log'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '会员手机变更表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="会员id")
    openid = db.Column(db.String(80), nullable=False, default='', comment="第三方id")
    old_mobile = db.Column(db.String(32), nullable=False, default='', comment="会员旧的手机号码")
    new_mobile = db.Column(db.String(32), nullable=False, default='', comment="会员新的手机号码")
    note = db.Column(db.String(100), nullable=False, default='', comment="备注字段")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
