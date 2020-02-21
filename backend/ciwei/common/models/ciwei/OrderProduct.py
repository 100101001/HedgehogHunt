# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, Text
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class OrderProduct(db.Model):
    __tablename__ = 'order_product'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    member_id = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    product_id = db.Column(db.Integer, nullable=False)
    product_num = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    note = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
