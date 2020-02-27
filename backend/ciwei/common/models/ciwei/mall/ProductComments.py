# coding: utf-8
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db


class ProductComments(db.Model):
    __tablename__ = 'product_comments'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '会员评论表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, default=0, comment="会员id")
    product_ids = db.Column(db.String(200), nullable=False, default='', comment="商品ids")
    order_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, default=0, comment="订单id")
    score = db.Column(TINYINT(), nullable=False, default=0, comment="评分")
    content = db.Column(db.String(200), nullable=False, default=datetime.now, onupdate=datetime.now,  comment="评论内容")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now,  comment="插入时间")

    @property
    def score_desc(self):
        score_map = {
            "10": "好评",
            "6": "中评",
            "0": "差评",
        }
        return score_map[str(self.score)]
