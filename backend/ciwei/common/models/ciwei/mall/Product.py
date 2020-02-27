# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class Product(db.Model):
    __tablename__ = 'product'
    __table_args__ = ({'comment': '周边表'})

    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), comment="周边类别")
    name = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue(), comment="周边名")
    price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), comment="单价")
    main_image = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="主图")
    pics = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), comment="组图")
    tags = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue(), comment="tag关键字，以','相连")
    description = db.Column(db.String(2000), nullable=False, server_default=db.FetchedValue(), comment="详情描述")
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="状态 1：有效 0：无效")
    view_cnt = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="浏览量")
    stock_cnt = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="库存量")
    sale_cnt = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="销售量")
    comment_cnt = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="评论量")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
