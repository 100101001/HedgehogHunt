# coding: utf-8
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from application import db
from datetime import datetime


class Report(db.Model):
    __tablename__ = 'report'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '举报消息表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    user_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="拉黑会员的管理员id")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="发布消息的会员id")
    report_member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="举报消息的会员id")
    report_member_nickname = db.Column(db.String(100), nullable=False, default='', comment="举报消息的会员名")
    report_member_avatar = db.Column(db.String(200), nullable=False, default='', comment="举报消息的会员头像")
    record_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="信息id，有可能是物品信息违规，也可能是用户的答谢违规")
    summary = db.Column(db.String(200), nullable=False, default='', comment="描述")
    status = db.Column(TINYINT(), nullable=False, default=0, index=True, comment="状态 1：已读 0：未读")
    record_type = db.Column(TINYINT(), nullable=False, default=1, index=True,
                            comment="状态 1：物品信息违规 0：答谢信息违规")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
