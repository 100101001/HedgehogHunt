# coding: utf-8
from datetime import datetime
import datetime as dt
from sqlalchemy.dialects.mysql import INTEGER
from application import db


class MemberSmsPkg(db.Model):
    __tablename__ = 'member_sms_pkg'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '短信套餐包表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True)
    member_id = db.Column(INTEGER(11, unsigned=True), index=True, default=0, info='会员的ID')
    open_id = db.Column(db.String(80), nullable=False, index=True, default="", info='会员的openID，二维码标识')
    left_notify_times = db.Column(db.Integer, nullable=False, default=0, info='套餐剩余通知次数')
    expired_time = db.Column(db.DateTime, nullable=False, index=True, default=datetime.now, info='消息包过期时间')
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, info='最后一次更新时间')
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, info='插入时间')



    def __init__(self, openid='', member_id=0, now=datetime.now()):
        self.open_id = openid
        self.member_id = member_id
        self.left_notify_times = 50
        self.expired_time = now + dt.timedelta(weeks=156)
        db.session.add(self)

    @staticmethod
    def getOldestValidPkg(openid='', now=datetime.now()):
        return MemberSmsPkg.query.filter(MemberSmsPkg.open_id == openid,
                                         MemberSmsPkg.expired_time <= now,
                                         MemberSmsPkg.left_notify_times > 0).order_by(MemberSmsPkg.id.asc()).first()

    @staticmethod
    def getAllValidPkg(member_id=0, now=datetime.now()):
        return MemberSmsPkg.query.filter(MemberSmsPkg.member_id == member_id,
                                         MemberSmsPkg.expired_time >= now).all()
