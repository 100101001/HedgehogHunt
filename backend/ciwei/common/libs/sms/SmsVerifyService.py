# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/2 下午7:09
@file: SmsVerifyService.py
@desc: 
"""

from common.cahce.core import CacheOpService, CacheQueryService
from common.libs.sms import SMSService


class SmsVerifyHandler:


    def __init__(self, mobile='', rcv_member=None):
        self.mobile = mobile
        self.rcv_member = rcv_member

    def noModified(self):
        return self.mobile == self.rcv_member.decrypt_mobile


    def sendTooFreq(self):
        return CacheQueryService.hasRcvSmsVerify(self.rcv_member.id)

    def send(self):
        member_id = self.rcv_member.id
        member_openid = self.rcv_member.openid
        trig_rcv_info = {
            'trig_member_id': member_id,
            'trig_openid': member_openid,
            'rcv_openid': member_openid,
            'rcv_member_id': member_id
        }
        send_ok, code = SMSService.send_verify_code(phone=self.mobile,  trig_rcv_info=trig_rcv_info)
        CacheOpService.setSmsVerifyCode(member_id=self.rcv_member.id, mobile=self.mobile, code=code)
        return send_ok



class VerifyBindHandler:
    def __init__(self, code='', mobile='', bind_member=None):
        self.code = code
        self.mobile = mobile
        self.bind_member = bind_member

    def expired(self):
        return not CacheQueryService.hasRcvSmsVerify(member_id=self.bind_member.id)

    def bind(self):
        code = CacheQueryService.getSmsVerifyCode(member_id=self.bind_member.id, mobile=self.mobile)
        if code == self.code:
            self.bind_member.bindMobile(self.mobile)
            return True
        return False
