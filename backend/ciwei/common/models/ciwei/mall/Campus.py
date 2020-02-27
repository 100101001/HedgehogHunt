# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class Campus(db.Model):
    __tablename__ = 'campus'
    __table_args__ = ({'comment': '大学表'})

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue(), comment="大学名")
    code = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue(), comment="代号")
    main_image = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="主图")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
