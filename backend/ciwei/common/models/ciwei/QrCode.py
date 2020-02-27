# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy

from application import db
from datetime import datetime


class QrCode(db.Model):
    __tablename__ = 'qr_code'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '二维码表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="会员id")
    openid = db.Column(db.String(80), nullable=False, index=True, default='', comment="第三方id")
    mobile = db.Column(db.String(20), nullable=False, default='', comment="会员手机号码")
    order_id = db.Column(INTEGER(11, unsigned=True), comment="微信支付的订单id")
    name = db.Column(db.String(20), nullable=False, default='', comment="会员姓名")
    location = db.Column(db.String(255), nullable=False, default='', comment="会员收货地址")
    qr_code = db.Column(db.String(255), nullable=False, comment="二维码图片")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,
                             comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
