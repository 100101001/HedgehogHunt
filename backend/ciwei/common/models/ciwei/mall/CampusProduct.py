# coding: utf-8
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class CampusProduct(db.Model):
    __tablename__ = 'campus_product'
    __table_args__ = ({'comment': '大学周边表'})

    id = db.Column(db.Integer, primary_key=True)
    campus_id = db.Column(db.Integer, index=True, nullable=False, comment="大学")
    product_id = db.Column(db.Integer, nullable=False, comment="产品")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
