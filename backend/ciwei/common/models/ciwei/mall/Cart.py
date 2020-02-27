# coding: utf-8
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db


class Cart(db.Model):
    __tablename__ = 'cart'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '购物车表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="会员的ID")
    product_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="产品")
    product_num = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="产品数")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
