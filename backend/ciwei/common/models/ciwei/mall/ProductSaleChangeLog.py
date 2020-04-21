# coding: utf-8
import decimal
from datetime import datetime

from sqlalchemy.dialects.mysql import INTEGER

from application import db


class ProductSaleChangeLog(db.Model):
    __tablename__ = 'product_sale_change_log'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '商品销售情况'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    product_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, default=0, comment="商品id")
    quantity = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="售卖数量")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="售卖金额")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="会员id")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="售卖时间")
