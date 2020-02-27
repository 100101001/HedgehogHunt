# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class QueueList(db.Model):
    __tablename__ = 'queue_list'
    __table_args__ = ({'comment': '事件队列表'})

    id = db.Column(db.Integer, primary_key=True)
    queue_name = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue(), comment="队列名字")
    data = db.Column(db.String(500), nullable=False, server_default=db.FetchedValue(), comment="队列数据")
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="状态 -1 待处理 1 已处理")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
