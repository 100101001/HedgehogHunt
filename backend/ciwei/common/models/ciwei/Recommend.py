# coding: utf-8
from datetime import datetime

from application import db


class Recommend(db.Model):
    __tablename__ = 'recommend'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '推荐表'})

    id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, nullable=False, index=True, default=0, comment='推荐的物品id')
    member_id = db.Column(db.Integer, nullable=False, index=True, default=0, comment='被推荐的用户id')
    status = db.Column(db.Integer, nullable=False, index=True, default=0, comment='状态 0:未读, 1:已读, '
                                                                                  '-1: 物品已被删除, 7：记录已删除')
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='插入时间')

    @property
    def status_desc(self):
        return {
            "-1": "推荐物品被作者删除",
            "0": "未读推荐",
            "1": "已读推荐",
            "7": "已删推荐"
        }[str(self.status)]
