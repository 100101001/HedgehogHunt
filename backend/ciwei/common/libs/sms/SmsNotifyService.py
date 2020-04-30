# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/30 下午8:29
@file: SmsNotifyService.py
@desc:
"""
import datetime
from decimal import Decimal

from application import db
from common.libs.CryptService import Cipher
from common.libs.sms import SMSService
from common.models.ciwei.Member import Member
from common.models.ciwei.MemberSmsPkg import MemberSmsPkg
from common.models.ciwei.logs.thirdservice.AcsSmsSendLog import AcsSmsSendLog




class SmsNotifyHandler:
    def __init__(self, openid, now=datetime.datetime.now()):
        self.openid = openid
        self.now = now
        self.receiver = Member.getUnblockedByOpenid(openid=self.openid)
        self.charger = None

    def validUser(self):
        return self.receiver is not None

    def tooFreq(self, interval=datetime.timedelta(weeks=1)):
        """
        判断一周内发送的频率
        :param interval:
        :return:
        """
        return AcsSmsSendLog.hasRecentLostNotify(openid=self.openid, interval=interval)

    def sendSmsNotify(self, goods_name='', location='', trig_rcv=None):
        """
        发送短信
        :param goods_name:
        :param location:
        :param trig_rcv:
        :return: 是否成功发送
        """
        if not goods_name or not location or not trig_rcv:
            return False
        mobile = Cipher.decrypt(text=self.receiver.mobile)
        trig_rcv['rcv_member_id'] = self.receiver.id
        return SMSService.send_lost_notify(phone=mobile, goods_name=goods_name,
                                           location=location, trig_rcv_info=trig_rcv)

    def hasCharger(self):
        """
        是否能支付短信费
        :return:
        """
        self.charger = SmsPkgChargeHandler.filter(now=self.now, member=self.receiver)
        return self.charger is not None

    def charge(self):
        """
        支付短信费
        :return:
        """
        self.charger.charge()


class BalanceChargeHandler:
    next = None

    def __init__(self, consumer):
        self.member = consumer

    @classmethod
    def filter(cls, member=None):
        if member.balance >= Decimal('0.10'):
            return cls(consumer=member)
        if cls.next:
            return cls.next.filter(member=member)
        return None

    def charge(self):
        self.member.balance -= Decimal("0.10")
        db.session.add(self.member)


class SmsTimesChargeHandler:
    next = BalanceChargeHandler

    def __init__(self, consumer):
        self.member = consumer

    @classmethod
    def filter(cls, member=None):
        if member.left_notify_times > 0:
            return cls(consumer=member)
        if cls.next:
            return cls.next.filter(member=member)
        return None

    def charge(self):
        self.member.left_notify_times -= 1
        db.session.add(self.member)


class SmsPkgChargeHandler:
    next = SmsTimesChargeHandler

    def __init__(self, pkg=None):
        self.pkg = pkg

    @classmethod
    def filter(cls, now=None, member=None):
        rcv_member_pkg = MemberSmsPkg.getOldestValidPkg(openid=member.openid, now=now)
        if rcv_member_pkg:
            return cls(pkg=rcv_member_pkg)
        if cls.next:
            return cls.next.filter(member=member)
        return None

    def charge(self):
        self.pkg.left_notify_times -= 1
        db.session.add(self.pkg)
