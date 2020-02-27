# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db
from datetime import datetime


class QueueList(db.Model):
    __tablename__ = 'queue_list'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '事件队列表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    queue_name = db.Column(db.String(30), nullable=False, default='', comment="队列名字")
    data = db.Column(db.String(500), nullable=False, default='', comment="队列数据")
    status = db.Column(TINYINT(), nullable=False, default=-1, comment="状态 -1 待处理 1 已处理")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,
                             comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
