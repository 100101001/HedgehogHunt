# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2019/12/05 下午8:43
@file: QrCodeService.py
@desc:
"""

from application import db, app, APP_CONSTANTS
from common.libs.mall.WechatService import WeChatService
from common.libs import Helper
import stat
import os
import uuid

from common.libs.sms.SmsVerifyService import SmsVerifyHandler, VerifyBindHandler
from common.models.ciwei.Goods import Good
from common.models.ciwei.logs.change.MemberPhoneChangeLog import MemberPhoneChangeLog


class QrCodeHandler:
    __strategy_map = {
        'gain': '_gainQrcodeFromWechat',
        'freq': '_detectScanFreq',
        'verify_mobile': '_verifyMobile',
        'bind_mobile': '_bindMobile'
    }

    @classmethod
    def deal(cls, op, **kwargs):
        strategy = cls.__strategy_map.get(op)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)

    @classmethod
    def _gainQrcodeFromWechat(cls, member_info=None):
        if not member_info.has_qr_code:
            img = WeChatService.getMimiProgramQrcode(openid=member_info.openid)
            if not img:
                return False
            qr_code = cls.__persistentImg(img=img)
            member_info.bindQrcode(qr_code)
        return True

    @classmethod
    def __persistentImg(cls, img):
        # 保存文件
        today = Helper.getCurrentDate("%Y%m%d")
        qr_code_dir = app.root_path + app.config['QR_CODE']['prefix_path'] + today
        qr_code_file = str(uuid.uuid4())
        if not os.path.exists(qr_code_dir):
            os.mkdir(qr_code_dir)
            os.chmod(qr_code_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)
        with open(qr_code_dir + "/" + qr_code_file + ".jpg", 'wb') as f:
            f.write(img)
        # db新增二维码, 会员绑定二维码
        qr_code_relative_path = today + "/" + qr_code_file + ".jpg"
        return qr_code_relative_path


    @classmethod
    def _verifyMobile(cls, mobile=None, rcv_member=None):
        handler = SmsVerifyHandler(mobile=mobile, rcv_member=rcv_member)
        if handler.noModified():
            return False, '请输入与原手机号不同的手机号'

        if handler.sendTooFreq():
            return False, '两次发送间隔不能短于5分钟，请稍后再试'

        send_ok = handler.send()
        # 触发和接受验证码短信的用户是同一人
        return (True, '发送成功') if send_ok else (False, '发送失败请检查手机号是否正确')

    @classmethod
    def _bindMobile(cls, input_code='', mobile=None, member_info=None):
        # 最近的一次5分钟内的验证码发送
        handler = VerifyBindHandler(code=input_code, mobile=mobile, bind_member=member_info)
        if handler.expired():
            return False, '验证码已过期'
        bind_ok = handler.bind()
        return (True, '绑定成功') if bind_ok else (False, '验证码错误')

    @classmethod
    def _detectScanFreq(cls, scan_member=None, openid=None):
        is_reg = scan_member is not None
        if is_reg and scan_member.openid == openid:
            # 自己扫码
            # 找到该用户一个月内的手机更换记录
            phoneChangeLog = MemberPhoneChangeLog.tooFreqChange(openid)
            if phoneChangeLog:
                return {
                    'phone_change_time': phoneChangeLog.created_time.strftime(APP_CONSTANTS['time_format_short'])
                }
        else:
            # 别人扫码
            # 找到该二维码新鲜的扫码归还记录进行提示
            good = Good.getNewlyScanReturn(openid)
            if good:
                return {
                    'goods_name': good.name,
                    'found_time': good.created_time.strftime(APP_CONSTANTS['time_format_short'])
                }


