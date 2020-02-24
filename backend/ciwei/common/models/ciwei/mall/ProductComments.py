# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class ProductComments(db.Model):
    __tablename__ = 'product_comments'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue())
    product_ids = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue())
    order_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    score = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    content = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    @property
    def score_desc(self):
        score_map = {
            "10": "好评",
            "6": "中评",
            "0": "差评",
        }
        return score_map[str(self.score)]
