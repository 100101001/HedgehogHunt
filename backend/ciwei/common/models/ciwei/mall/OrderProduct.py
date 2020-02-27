# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, Text
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class OrderProduct(db.Model):
    __tablename__ = 'order_product'
    __table_args__ = ({'comment': '订单包含的周边表'})

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False, index=True, comment="订单id")
    member_id = db.Column(db.BigInteger, nullable=False, index=True, server_default=db.FetchedValue(), comment="会员id")
    product_id = db.Column(db.Integer, nullable=False, comment="产品id")
    product_num = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="购买数, 默认1份")
    price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), comment="商品总价格，售价 * 数量")
    note = db.Column(db.Text, nullable=False, comment="备注信息")
    status = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), comment="状态：1：成功 0 失败")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
