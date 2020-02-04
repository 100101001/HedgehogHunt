# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False)
    openid = db.Column(db.String(32), nullable=False)
    transaction_id = db.Column(db.String(64))
    price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    paid_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
