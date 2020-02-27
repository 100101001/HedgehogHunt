# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db
from datetime import datetime


class Campus(db.Model):
    __tablename__ = 'campus'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '大学表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False, default='', comment="大学名")
    code = db.Column(db.String(80), nullable=False, default='', comment="代号")
    main_image = db.Column(db.String(100), nullable=False, default='', comment="主图")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
