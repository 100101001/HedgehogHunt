# coding: utf-8

from application import db


class GoodsCategory(db.Model):
    __tablename__ = 'goods_category'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '物品类别表'})

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(10), nullable=False, default=9, comment='类别标签')
