# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db
from datetime import datetime


class ProductStockChangeLog(db.Model):
    __tablename__ = 'product_stock_change_log'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '数据库存变更表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    product_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="商品id")
    unit = db.Column(INTEGER(11), nullable=False, default=0, comment="变更多少")
    total_stock = db.Column(INTEGER(12), nullable=False, default=0, comment="变更之后总量")
    note = db.Column(db.String(100), nullable=False, default='', comment="备注字段")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
