# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db

class Good(db.Model):
    __tablename__ = 'goods'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    owner_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    qr_code_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    mobile = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    name = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue())
    owner_name = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    location = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    target_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    main_image = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    pics = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    summary = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    business_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    view_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    tap_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    mark_id = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
