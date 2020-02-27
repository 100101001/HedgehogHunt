# coding: utf-8
from sqlalchemy import Column, DateTime, Index, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class Address(db.Model):
    __tablename__ = 'address'
    __table_args__ = (
        db.Index('idx_member_id_status', 'member_id', 'status'),
        {'comment': '会员收货地址'}
    )

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="会员id")
    nickname = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), comment="收货人姓名")
    mobile = db.Column(db.String(11), nullable=False, server_default=db.FetchedValue(), comment="收货人手机号码")
    province_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="省id")
    province_str = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), comment="省名称")
    city_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="城市id")
    city_str = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), comment="市名称")
    area_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="区域id")
    area_str = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), comment="区域名称")
    address = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="详细地址")
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="是否有效 1：有效 0：无效")
    is_default = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="默认地址")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
