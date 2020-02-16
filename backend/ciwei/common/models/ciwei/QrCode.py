# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy

from application import db


class QrCode(db.Model):
    __tablename__ = 'qr_code'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer)
    mobile = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    order_id = db.Column(db.Integer)
    name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    location = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    qr_code = db.Column(db.String(255), nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
