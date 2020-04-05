# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/4 下午5:58
@file: Appeal.py
@desc:
"""

from datetime import datetime

from application import db


class Appeal(db.Model):
    __tablename__ = 'appeal'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '申诉表'})

    id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, nullable=False, index=True, default=0, info='申诉的物品id')
    member_id = db.Column(db.Integer, nullable=False, index=True, default=0, info='用户id')
    status = db.Column(db.Integer, nullable=False, index=True, default=0,
                       info='状态 0:待处理 1:已处理完毕 7:自删')
    adm_id = db.Column(db.Integer, nullable=False, default=0, info='系统指派处理的管理员id')
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='插入时间')

    @property
    def status_desc(self):
        return {
            "0": "待处理",
            "1": "已处理",
            "7": "已删除"
        }[str(self.status)]
