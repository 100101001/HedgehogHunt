# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class ProductComments(db.Model):
    __tablename__ = 'product_comments'
    __table_args__ = ({'comment': '会员评论表'})

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), comment="会员id")
    product_ids = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue(), comment="商品ids")
    order_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), comment="订单id")
    score = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="评分")
    content = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue(), comment="评论内容")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")

    @property
    def score_desc(self):
        score_map = {
            "10": "好评",
            "6": "中评",
            "0": "差评",
        }
        return score_map[str(self.score)]
