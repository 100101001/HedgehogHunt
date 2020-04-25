# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/23 下午9:37
@file: MemberStatusChangeLog.py
@desc: 
"""

from datetime import datetime

from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER

from application import db


class MemberStatusChangeLog(db.Model):
    __tablename__ = 'member_status_change_log'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '会员状态变更记录'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, index=True, comment="会员id")
    openid = db.Column(db.String(80), nullable=False, default='', comment="第三方id")
    old_status = db.Column(TINYINT(), nullable=False, default=1, comment="会员旧状态")
    new_status = db.Column(TINYINT(), nullable=False, default=0, comment="会员新状态")
    user_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="操作管理员id")
    goods_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="起因举报")
    note = db.Column(db.String(100), nullable=False, default='', comment="备注字段")
    member_reason = db.Column(db.String(200), nullable=False, default='', comment="申诉原因")
    status = db.Column(TINYINT(), nullable=False, default=0, comment="记录状态 0: 无申诉 1：申诉")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")

    @property
    def status_desc(self):
        status_map = {
            '0': '待申诉',
            '1': '申诉中',
            '2': '已接受',  # 申诉成功
            '3': '已驳回'   # 申诉失败
        }
        return status_map[str(self.status)]