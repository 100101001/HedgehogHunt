# coding: utf-8
import decimal
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db
from common.libs import Helper


class Member(db.Model):
    __tablename__ = 'member'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '会员表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    user_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="拉黑会员的管理员id")
    qr_code_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="小程序二维码id")
    nickname = db.Column(db.String(100), nullable=False, default='', comment="会员名")
    salt = db.Column(db.String(255), nullable=False, default='', comment="加密生成的字符串")
    credits = db.Column(INTEGER(11), nullable=False, default=0, comment="会员积分")
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="用户账户余额")
    mobile = db.Column(db.String(20), nullable=False, default='', comment="会员手机号码")
    name = db.Column(db.String(20), nullable=False, default='', comment="注册会员的姓名，用于后期做匹配")
    location = db.Column(db.String(255), nullable=False, default='', comment="会员收货地址")
    sex = db.Column(TINYINT(), nullable=False, default=0, comment="性别 1：男 2：女")
    avatar = db.Column(db.String(200), nullable=False, default='', comment="会员头像")
    qr_code = db.Column(db.String(200), nullable=False, default='', comment="会员的小程序二维码")
    openid = db.Column(db.String(80), nullable=False, default='', comment="第三方id")
    status = db.Column(TINYINT(), nullable=False, default=1, comment="状态 1：有效 0：无效")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,
                             comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
    mark_id = db.Column(db.String(1000), nullable=False, default='', comment="用户认领的物品id,字符串")
    gotback_id = db.Column(db.String(2000), nullable=False, default='', comment="用户最终取回的物品id,字符串")
    recommend_id = db.Column(db.String(3000), nullable=False, default='', comment="系统推荐的物品id,字符串")

    @property
    def has_qr_code(self):
        return self.qr_code != ""
