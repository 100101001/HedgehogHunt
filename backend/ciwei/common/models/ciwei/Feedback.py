# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from application import db


class Feedback(db.Model):
    __tablename__ = 'feedback'
    __table_args__ = ({'comment': '反馈表'})

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="处理反馈消息的管理员id")
    member_id = db.Column(db.Integer, nullable=False, comment="反馈消息的会员id")
    summary = db.Column(db.String(10000), nullable=False, server_default=db.FetchedValue(), comment="描述")
    main_image = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="主图")
    pics = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), comment="组图")
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="状态 1：已读 0：未读")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
