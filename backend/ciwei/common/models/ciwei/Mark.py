# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/4 下午5:58
@file: Mark.py
@desc: 
"""

from datetime import datetime

from application import db


class Mark(db.Model):
    __tablename__ = 'mark'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '认领表'})

    id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, nullable=False, index=True, default=0, comment='认领的物品id')
    member_id = db.Column(db.Integer, nullable=False, index=True, default=0, comment='用户id')
    status = db.Column(db.Integer, nullable=False, index=True, default=0, comment='状态 -1作者删除 0:未取 1:已取, 7自行删除')
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='插入时间')

    @property
    def status_desc(self):
        return {
            "-1": "认领物品被作者删除",
            "0": "未取认领",
            "1": "已取认领",
            "7": "已删认领"
        }[str(self.status)]
