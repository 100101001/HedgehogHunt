# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy

from application import db
from datetime import datetime


class Image(db.Model):
    __tablename__ = 'images'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '图片表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    file_key = db.Column(db.String(60), nullable=False, default='', comment="文件名")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
