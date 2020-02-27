# coding: utf-8
import decimal
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, Text
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db


class OrderProduct(db.Model):
    __tablename__ = 'order_product'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '订单包含的周边表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    order_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="订单id")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, default=0, comment="会员id")
    product_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="产品id")
    product_num = db.Column(INTEGER(11, unsigned=True), nullable=False, default=1, comment="购买数, 默认1份")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="商品总价格，售价 * 数量")
    note = db.Column(db.Text, nullable=False, comment="备注信息")
    status = db.Column(TINYINT(), nullable=False, index=True, default=1, comment="状态：1：成功 0 失败")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now,  comment="插入时间")
