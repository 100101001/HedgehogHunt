# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db
class Member(db.Model):
    __tablename__ = 'member'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    qr_code_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    nickname = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    salt = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    credits = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    mobile = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    location = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    sex = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    avatar = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue())
    qr_code = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue())
    openid = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    mark_id = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    recommend_id = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
