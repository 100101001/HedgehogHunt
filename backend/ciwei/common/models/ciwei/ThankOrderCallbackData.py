# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/5 上午12:40
@file: ThankOrderCallbackData.py
@desc: 
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Text

from sqlalchemy.dialects.mysql import INTEGER

from application import db


class ThankOrderCallbackData(db.Model):
    __tablename__ = 'thank_order_callback_data'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '答谢微信支付回调数据表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    thank_order_id = db.Column(INTEGER(11, unsigned=True), nullable=False, unique=True, index=True, default=0,
                         comment="支付订单id")
    pay_data = db.Column(db.Text, nullable=False, comment="支付回调信息")
    refund_data = db.Column(db.Text, nullable=False, comment="退款回调信息")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,
                             comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="创建时间")
