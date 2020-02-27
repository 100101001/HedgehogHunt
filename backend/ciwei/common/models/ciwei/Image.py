# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy

from application import db

class Image(db.Model):
    __tablename__ = 'images'
    __table_args__ = ({'comment': '图片表'})

    id = db.Column(db.Integer, primary_key=True)
    file_key = db.Column(db.String(60), nullable=False, server_default=db.FetchedValue(), comment="文件名")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
