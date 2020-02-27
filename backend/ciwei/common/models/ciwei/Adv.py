# coding: utf-8
import decimal

from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from application import db
from datetime import datetime


class Adv(db.Model):
    __tablename__ = 'advs'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '顶部导航栏的广告表，按天收费，先提交并付费，管理员审核通过后发布，否则返还钱'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False)
    uu_id = db.Column(db.String(80), nullable=False, default='')
    name = db.Column(db.String(100), nullable=False, default='')
    location = db.Column(db.String(100), nullable=False, default='')
    target_price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00))
    main_image = db.Column(db.String(100), nullable=False, default='')
    qr_code = db.Column(db.String(200), nullable=False, default='')
    pics = db.Column(db.String(1000), nullable=False, default='')
    summary = db.Column(db.String(10000), nullable=False, default='')
    stock = db.Column(INTEGER(11, unsigned=True), nullable=False, default=9999)
    status = db.Column(TINYINT(), nullable=False, default=1)
    view_count = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0)
    tap_count = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0)
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
