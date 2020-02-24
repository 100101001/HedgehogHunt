# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class Campus(db.Model):
    __tablename__ = 'campus'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue())
    code = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue())
    main_image = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
