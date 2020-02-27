# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class Thank(db.Model):
    __tablename__ = 'thanks'
    __table_args__ = ({'comment': '答谢表'})

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="拉黑会员的管理员id")
    member_id = db.Column(db.Integer, nullable=False, comment="发布感谢的会员id")
    order_id = db.Column(db.Integer, nullable=False, comment="微信支付的订单id")
    target_member_id = db.Column(db.Integer, nullable=False, comment="接受消息的会员id")
    goods_id = db.Column(db.Integer, nullable=False, comment="物品id")
    summary = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue(), comment="描述")
    goods_name = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue(), comment="物品名称")
    business_desc = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), comment="拾到或者丢失")
    owner_name = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue(), comment="用户的名称，可能只是微信昵称")
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="状态 1：已读 0：未读")
    report_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="被举报后的状态，用于存储举报的状态值")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
