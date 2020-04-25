# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/25 上午2:30
@file: Feedback.py
@desc:
"""

from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from application import db
from datetime import datetime


class Feedback(db.Model):
    __tablename__ = 'feedback'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '反馈表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    user_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="处理反馈消息的管理员id")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="反馈消息的会员id")
    nickname = db.Column(db.String(100), nullable=False, default='', comment="反馈消息的会员昵称")
    avatar = db.Column(db.String(200), nullable=False, default='', comment="反馈消息的会员头像")
    summary = db.Column(db.String(10000), nullable=False, default='', comment="描述")
    main_image = db.Column(db.String(100), nullable=False, default='', comment="主图")
    pics = db.Column(db.String(1000), nullable=False, default='', comment="组图")
    views = db.Column(db.String(200), nullable=False, default='', comment="阅读管理员id")
    status = db.Column(TINYINT(), nullable=False, default=0, index=True, comment="状态 1：已读 0：未读")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
