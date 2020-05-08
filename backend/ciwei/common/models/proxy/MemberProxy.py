# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/26 下午3:21
@file: MemberProxy.py
@desc: 
"""
from application import db
from common.libs.CryptService import Cipher
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Member import Member


class MemberProxy:
    id = 0
    user_id = 0
    nickname = ''
    salt = ''
    credits = 0
    balance = 0
    mobile = ''
    name = ''
    location = ''
    sex = 1
    avatar = ''
    qr_code = ''
    left_notify_times = 0
    openid = ''
    status = 1
    updated_time = 0
    created_time = 1

    @property
    def has_qr_code(self):
        return self.qr_code != ""

    @property
    def qr_code_url(self):
        return '' if not self.has_qr_code else UrlManager.buildImageUrl(self.qr_code, image_type='QR_CODE')

    @property
    def decrypt_mobile(self):
        return Cipher.decrypt(text=self.mobile)

    def bindMobile(self, mobile=''):
        if mobile:
            member = Member.getById(self.id)
            member.mobile = Cipher.encrypt(text=mobile)
            db.session.add(member)
            db.session.commit()

    def bindQrcode(self, qr_code=''):
        if qr_code:
            member = Member.getById(self.id)
            member.qr_code = qr_code
            db.session.add(member)
            db.session.commit()

    def changeSms(self, quantity=0):
        if quantity != 0:
            member = Member.getById(self.id)
            member.left_notify_times += quantity
            db.session.add(member)

    def changeBalance(self, quantity=0):
        if quantity != 0:
            member = Member.getById(self.id)
            member.balance += quantity
            db.session.add(member)

    def changeName(self, name):
        if name:
            member = Member.getById(self.id)
            member.name = name
            db.session.add(member)

    def changeCredits(self, quantity):
        if quantity:
            member = Member.getById(self.id)
            member.credits += quantity
            db.session.add(member)
