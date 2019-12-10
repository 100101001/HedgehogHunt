# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db
class Thank(db.Model):
    __tablename__ = 'thanks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    member_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    target_member_id = db.Column(db.Integer, nullable=False)
    goods_id = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue())
    goods_name = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue())
    business_desc = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue())
    owner_name = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
