# coding: utf-8
import decimal

from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db
from datetime import datetime


class ThankOrder(db.Model):
    __tablename__ = 'thank_order'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '答谢支付的订单'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="会员id")
    openid = db.Column(db.String(32), nullable=False, comment="第三方id")
    transaction_id = db.Column(db.String(64), default='', comment="微信支付交易号")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="支付金额")
    status = db.Column(TINYINT(), nullable=False, default=-1, comment="状态 -1=刚创建, 0=微信预下单-未支付, "
                                                                       " 1=微信支付成功, 2=微信已关单, "
                                                                       "3=微信支付错误")
    paid_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="支付完成时间")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")

    @property
    def status_desc(self):
        status_mapping = {
            '-1': 'fresh',
            '0': 'notpay',
            '1': 'success',
            '2': 'payerror',
            '3': 'closed',
        }
        return status_mapping[str(self.status)]

    @property
    def wx_payment_result_notified(self):
        return self.transaction_id != ''
