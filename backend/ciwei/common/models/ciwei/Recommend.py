# coding: utf-8
from datetime import datetime

from sqlalchemy import or_

from application import db


class Recommend(db.Model):
    __tablename__ = 'recommend'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '推荐表'})

    id = db.Column(db.Integer, primary_key=True)
    found_goods_id = db.Column(db.Integer, nullable=False, index=True, default=0, comment='推荐的物品id')
    lost_goods_id = db.Column(db.Integer, nullable=False, index=True, default=0, comment='被推荐的原寻物id')
    target_member_id = db.Column(db.Integer, nullable=False, index=True, default=0, comment='被推荐的用户id')
    rel_score = db.Column(db.Float, nullable=False, index=True, default=1, comment="匹配相似度")
    status = db.Column(db.Integer, nullable=False, index=True, default=0, comment='状态 0:未读, 1:已读 -1/-2：无效推荐')
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='插入时间')

    @property
    def status_desc(self):
        return {
            "0": "未读推荐",
            "1": "已读推荐",
            "-1": "无效推荐",
            "-2": "无效推荐",
        }[str(self.status)]

    @classmethod
    def checked(cls, member_id=0, goods_id=0):
        cls.query.filter_by(found_goods_id=goods_id, target_member_id=member_id,
                            status=0).update({'status': 1}, synchronize_session=False)

    @classmethod
    def invalidatePrevRecommend(cls, goods_info=None):
        # 将推荐置为无效
        cls.query.filter(or_(cls.found_goods_id == goods_info.id, cls.lost_goods_id == goods_info.id),
                         cls.status >= 0).update({'status': -cls.status - 1},
                                                 synchronize_session=False)

    @classmethod
    def renewOldRecommend(cls, goods_info=None):
        if goods_info.business_type == 1:
            # 如果是失物招领，更新推荐记录为未读
            cls.query.filter(cls.found_goods_id == goods_info.id,
                             cls.status > 0).update({'status': 0}, synchronize_session=False)

    @classmethod
    def getStatus(cls, goods_list=None, member_id=0, status_map=None):
        id_status = cls.query.filter(cls.found_goods_id.in_([item.id for item in goods_list]),
                         cls.target_member_id == member_id).with_entities(cls.found_goods_id, cls.status).all()
        for item in id_status:
            status_map[item.found_goods_id] += item.status
