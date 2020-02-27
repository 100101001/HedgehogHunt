# coding: utf-8
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class Cart(db.Model):
    __tablename__ = 'cart'
    __table_args__ = ({'comment': '购物车表'})

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, index=True, comment="会员的ID")
    product_id = db.Column(db.Integer, nullable=False, comment="产品")
    product_num = db.Column(db.Integer, nullable=False, comment="产品数")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
