# coding: utf-8
from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db


class Address(db.Model):
    __tablename__ = 'address'
    __table_args__ = (
        db.Index('idx_member_id_status', 'member_id', 'status'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '会员收货地址'}
    )

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="会员id")
    nickname = db.Column(db.String(20), nullable=False, default='', comment="收货人姓名")
    mobile = db.Column(db.String(11), nullable=False, default='', comment="收货人手机号码")
    province_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="省id")
    province_str = db.Column(db.String(50), nullable=False, default='', comment="省名称")
    city_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="城市id")
    city_str = db.Column(db.String(50), nullable=False, default='', comment="市名称")
    area_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="区域id")
    area_str = db.Column(db.String(50), nullable=False, default='', comment="区域名称")
    address = db.Column(db.String(100), nullable=False, default='', comment="详细地址")
    status = db.Column(TINYINT(), nullable=False, default=1, comment="是否有效 1：有效 0：无效")
    is_default = db.Column(TINYINT(), nullable=False, default=0, comment="默认地址")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,
                             comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
