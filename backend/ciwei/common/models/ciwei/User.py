# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db

class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = ({'comment': '管理员表'})

    uid = db.Column(db.BigInteger, primary_key=True, comment="管理员id")
    member_id = db.Column(db.Integer, nullable=False, comment="注册会员id")
    level = db.Column(db.Integer, nullable=False, comment="管理员等级")
    name = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="用户名")
    mobile = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), comment="手机号码")
    email = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="邮箱地址")
    sex = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="1：男 2：女 0：没填写")
    avatar = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue(), comment="头像")
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="1：有效 0：无效")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
