# coding: utf-8
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, index=True)
    product_id = db.Column(db.Integer, nullable=False)
    product_num = db.Column(db.Integer, nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
