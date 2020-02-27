# coding: utf-8
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db



class CampusProduct(db.Model):
    __tablename__ = 'campus_product'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '大学周边表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    campus_id = db.Column(INTEGER(11, unsigned=True), index=True, nullable=False, comment="大学")
    product_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="产品")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
