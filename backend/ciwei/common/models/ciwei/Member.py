# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/1/17 下午10:33
@file: Member.py
@desc:
"""
import decimal
from datetime import datetime
from decimal import Decimal

from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER

from application import db
from common.libs.CryptService import Cipher
from common.libs.UrlManager import UrlManager


class Member(db.Model):
    __tablename__ = 'member'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '会员表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    user_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="拉黑会员的管理员id")
    nickname = db.Column(db.String(100), nullable=False, default='', comment="会员名")
    salt = db.Column(db.String(255), nullable=False, default='', comment="加密生成的字符串")
    credits = db.Column(INTEGER(11), nullable=False, default=0, comment="会员积分")
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="用户账户余额")
    mobile = db.Column(db.String(32), nullable=False, default='', comment="会员手机号码")
    name = db.Column(db.String(20), nullable=False, default='', comment="注册会员的姓名，用于后期做匹配")
    location = db.Column(db.String(255), nullable=False, default='', comment="会员收货地址")
    sex = db.Column(TINYINT(), nullable=False, default=0, comment="性别 1：男 2：女")
    avatar = db.Column(db.String(200), nullable=False, default='', comment="会员头像")
    qr_code = db.Column(db.String(200), nullable=False, default='', comment="会员的小程序二维码")
    left_notify_times = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="剩余通知次数")
    openid = db.Column(db.String(80), nullable=False, default='', comment="第三方id")
    status = db.Column(TINYINT(), nullable=False, default=1, comment="状态 1：有效 0：无效")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,
                             comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")

    @property
    def has_qr_code(self):
        return self.qr_code != ""

    @property
    def qr_code_url(self):
        return '' if not self.has_qr_code else UrlManager.buildImageUrl(self.qr_code, image_type='QR_CODE')

    @property
    def decrypt_mobile(self):
        return Cipher.decrypt(text=self.mobile)

    @property
    def encrypt_openid(self):
        return Cipher.encrypt(self.openid)

    def __init__(self, openid='', mobile='', nickname='', avatar='', sex=1):
        self.openid = openid
        self.mobile = mobile  # 加密过了的手机
        self.nickname = nickname
        self.avatar = avatar
        self.sex = sex
        db.session.add(self)

    @classmethod
    def getUnblockedByOpenid(cls, openid=''):
        return cls.query.filter_by(openid=openid, status=1).first()

    @classmethod
    def getById(cls, member_id=0):
        return cls.query.filter_by(id=member_id).first()

    @classmethod
    def getByOpenId(cls, openid=''):
        return cls.query.filter_by(openid=openid).first()


    def bindMobile(self, mobile=''):
        if mobile:
            self.mobile = Cipher.encrypt(text=mobile)
            db.session.add(self)
            db.session.commit()

    def bindQrcode(self, qr_code=''):
        if qr_code:
            self.qr_code = qr_code
            db.session.add(self)
            db.session.commit()

    def changeSms(self, quantity=0):
        if quantity != 0:
            self.left_notify_times += quantity
            db.session.add(self)

    def changeBalance(self, quantity=0):
        if quantity != 0:
            self.balance += quantity
            db.session.add(self)

    def changeName(self, name):
        if name:
            self.name = name
            db.session.add(self)

    def changeCredits(self, quantity=0):
        if quantity != 0:
            self.credits += quantity
            db.session.add(self)
