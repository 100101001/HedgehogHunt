# coding: utf-8
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class OrderProduct(db.Model):
    __tablename__ = 'order_product'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_num = db.Column(db.Integer, nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
