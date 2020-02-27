# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class ProductCat(db.Model):
    __tablename__ = 'product_cat'
    __table_args__ = ({'comment': '周边分类'})

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, server_default=db.FetchedValue(), comment="类别名称")
    weight = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="权重")
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="状态 1：有效 0：无效")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")

    @property
    def status_desc(self):
        status_mapping = {
            "1": "正常",
            "0": "已删除"
        }
        return status_mapping[str(self.status)]
