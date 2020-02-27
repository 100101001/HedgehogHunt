# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class OrderCallbackData(db.Model):
    __tablename__ = 'order_callback_data'
    __table_args__ = ({'comment': '微信支付回调数据表'})

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False, unique=True, index=True, server_default=db.FetchedValue(),
                         comment="支付订单id")
    pay_data = db.Column(db.Text, nullable=False, comment="支付回调信息")
    refund_data = db.Column(db.Text, nullable=False, comment="退款回调信息")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="创建时间")
