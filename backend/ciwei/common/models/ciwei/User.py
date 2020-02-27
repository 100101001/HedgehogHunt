# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '管理员表'})

    uid = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment="管理员id")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="注册会员id")
    level = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="管理员等级")
    name = db.Column(db.String(100), nullable=False, default='', comment="用户名")
    mobile = db.Column(db.String(20), nullable=False, default='', comment="手机号码")
    email = db.Column(db.String(100), nullable=False, default='', comment="邮箱地址")
    sex = db.Column(TINYINT(), nullable=False, default=0, comment="1：男 2：女 0：没填写")
    avatar = db.Column(db.String(200), nullable=False, default='', comment="头像")
    status = db.Column(TINYINT(), nullable=False, default=1, comment="1：有效 0：无效")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,
                             comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
