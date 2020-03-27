# coding: utf-8
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER
from application import db


class MemberSmsPkg(db.Model):
    __tablename__ = 'member_sms_pkg'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '短信套餐包表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True)
    open_id = db.Column(db.String(80), nullable=False, default="", info='会员的openID，二维码标识')
    left_notify_times = db.Column(db.Integer, nullable=False, default=0, info='套餐剩余通知次数')
    expired_time = db.Column(db.DateTime, nullable=False, index=True, default=datetime.now, info='消息包过期时间')
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, info='最后一次更新时间')
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, info='插入时间')
