# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from application import db


class Report(db.Model):
    __tablename__ = 'report'
    __table_args__ = ({'comment': '举报消息表'})

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="拉黑会员的管理员id")
    member_id = db.Column(db.Integer, nullable=False, comment="发布消息的会员id")
    report_member_id = db.Column(db.Integer, nullable=False, comment="举报消息的会员id")
    record_id = db.Column(db.Integer, nullable=False, comment="信息id，有可能是物品信息违规，也可能是用户的答谢违规")
    summary = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue(), comment="描述")
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="状态 1：已读 0：未读")
    record_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(),
                            comment="状态 1：物品信息违规 0：答谢信息违规")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
