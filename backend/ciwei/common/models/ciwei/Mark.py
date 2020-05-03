# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/4 下午5:58
@file: Mark.py
@desc: 
"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.dialects.mssql import TINYINT

from application import db


class Mark(db.Model):
    __tablename__ = 'mark'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '认领表'})

    id = db.Column(db.Integer, primary_key=True)
    business_type = db.Column(TINYINT(), nullable=False, default=1, comment="状态 1:失物招领 0:寻物启事 2:寻物归还与扫码归还")
    goods_id = db.Column(db.Integer, nullable=False, index=True, default=0, comment='认领的物品id')
    member_id = db.Column(db.Integer, nullable=False, index=True, default=0, comment='用户id')
    status = db.Column(db.Integer, nullable=False, index=True, default=0, comment='状态 -1作者删除 0:未取 1:已取 7自行删除')
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='插入时间')

    @property
    def status_desc(self):
        return {
            "0": "未取认领",
            "1": "已取认领",
            "2": "已答谢",
            "-1": "取消认领",
            "-2": "删除取回的认领记录",
            "-3": "删除已答谢认领记录"
        }[str(self.status)]

    def __init__(self, member_id=None, goods_id=None, business_type=0):
        self.member_id = member_id
        self.goods_id = goods_id
        self.business_type = business_type

    @classmethod
    def pre(cls, member_id=None, goods_id=None, business_type=0):
        """
        预认领 update if exist
        :param member_id:
        :param goods_id:
        :param business_type:
        :return:
        """
        if not member_id or not goods_id:
            return False
        repeat_mark = cls.query.filter_by(member_id=member_id, goods_id=goods_id).first()
        if repeat_mark:
            if repeat_mark.status < 0:
                # 将被删除的记录状态初始化
                repeat_mark.status = 0
                db.session.add(repeat_mark)
        pre_mark = cls(member_id=member_id, goods_id=goods_id, business_type=business_type)
        db.session.add(pre_mark)

    @classmethod
    def getAllOn(cls, goods_id=0):
        """
        获取一个物品的所有认领人的id
        :param goods_id:
        :return:
        """
        return cls.query.filter(cls.goods_id == goods_id, cls.status >= 0).all()

    @classmethod
    def mistaken(cls, goods_ids=None, member_id=0):
        cls.query.filter(cls.member_id == member_id, cls.goods_id.in_(goods_ids),
                         cls.status == 0).update({'status': -cls.status - 1}, synchronize_session=False)

    @classmethod
    def done(cls, goods_ids=None, member_id=0):
        cls.query.filter(cls.member_id == member_id, cls.goods_id.in_(goods_ids),
                         cls.status == 0).update({'status': 1}, synchronize_session=False)

    @classmethod
    def isNoMarkOn(cls, goods_id=0):
        cnt = db.session.query(func.count(cls.id)).filter(cls.goods_id == goods_id, cls.status >= 0).scalar()
        return cnt == 0

    @classmethod
    def thanked(cls, member_id=0, goods_id=0):
        cls.query.filter(cls.member_id == member_id, cls.goods_id == goods_id,
                         cls.status == 1).update({'status': 2}, synchronize_session=False)
