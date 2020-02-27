# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy

from application import db


class QrCode(db.Model):
    __tablename__ = 'qr_code'
    __table_args__ = ({'comment': '二维码表'})

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, comment="会员id")
    openid = db.Column(db.String(80), nullable=False, index=True, server_default=db.FetchedValue(), comment="第三方id")
    mobile = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), comment="会员手机号码")
    order_id = db.Column(db.Integer, comment="微信支付的订单id")
    name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), comment="会员姓名")
    location = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), comment="会员收货地址")
    qr_code = db.Column(db.String(255), nullable=False, comment="二维码图片")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
