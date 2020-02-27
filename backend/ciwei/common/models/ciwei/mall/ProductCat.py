# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db
from datetime import datetime


class ProductCat(db.Model):
    __tablename__ = 'product_cat'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '周边分类'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True, default='', comment="类别名称")
    weight = db.Column(TINYINT(), nullable=False, default=1, comment="权重")
    status = db.Column(TINYINT(), nullable=False, default=1, comment="状态 1：有效 0：无效")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")

    @property
    def status_desc(self):
        status_mapping = {
            "1": "正常",
            "0": "已删除"
        }
        return status_mapping[str(self.status)]
