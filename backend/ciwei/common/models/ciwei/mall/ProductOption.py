# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/2 上午7:56
@file: ProductOption.py
@desc: 
"""
from datetime import datetime

from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER

from application import db


class ProductOption(db.Model):
    __tablename__ = 'product_option'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '周边规格表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    product_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="周边id")
    option_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="选项id")
    main_image = db.Column(db.String(100), nullable=False, default='', comment="主图")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="单价")
    summary = db.column(db.String(50), nullable=False, comment="规格描述")
    status = db.Column(TINYINT(), nullable=False, default=1, comment="状态 1：有效 0：无效")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,
                             comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
