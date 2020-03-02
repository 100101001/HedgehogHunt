# coding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/2 上午10:56
@file: Product.py
@desc:
"""
import decimal
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class Product(db.Model):
    __tablename__ = 'product'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '周边表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    common_id = db.Column(INTEGER(11, unsigned=True), nullable=False, info='公共产品id')
    option_id = db.Column(INTEGER(11, unsigned=True), nullable=False, info='规格id')
    option_desc = db.Column(db.String(50), info='规格描述')
    cat_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, default=0, comment="周边类别id")
    name = db.Column(db.String(80), nullable=False, default='', comment="周边名")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="单价")
    main_image = db.Column(db.String(100), nullable=False, default='', comment="主图")
    pics = db.Column(db.String(1000), nullable=False, default='', comment="组图")
    tags = db.Column(db.String(200), nullable=False, default='', comment="tag关键字，以','相连")
    description = db.Column(db.String(2000), nullable=False, default='', comment="详情描述")
    status = db.Column(TINYINT(), nullable=False, default=1, comment="状态 1：有效 0：无效")
    view_cnt = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="浏览量")
    stock_cnt = db.Column(INTEGER(11, unsigned=True), nullable=False, default=99999, comment="库存量")
    sale_cnt = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="销售量")
    comment_cnt = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="评论量")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
