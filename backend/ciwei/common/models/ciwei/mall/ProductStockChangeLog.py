# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class ProductStockChangeLog(db.Model):
    __tablename__ = 'product_stock_change_log'
    __table_args__ = ({'comment': '数据库存变更表'})

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False, index=True, comment="商品id")
    unit = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="变更多少")
    total_stock = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="变更之后总量")
    note = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="备注字段")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
