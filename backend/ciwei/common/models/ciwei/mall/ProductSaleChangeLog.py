# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, Numeric
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class ProductSaleChangeLog(db.Model):
    __tablename__ = 'product_sale_change_log'
    __table_args__ = ({'comment': '商品销售情况'})

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), comment="商品id")
    quantity = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="售卖数量")
    price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), comment="售卖金额")
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="会员id")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="售卖时间")
