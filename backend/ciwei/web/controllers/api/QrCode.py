# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/11 下午11:56
@file: QrCode.py
@desc:
"""

import datetime
import json

import requests
from flask import request, jsonify, g

from application import app, db, APP_CONSTANTS
from common.libs import QrCodeService
from common.libs.CryptService import Cipher
from common.libs.UrlManager import UrlManager
from common.libs.sms import SMSService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.models.ciwei.logs.change.MemberPhoneChangeLog import MemberPhoneChangeLog
from common.models.ciwei.logs.thirdservice.AcsSmsSendLog import AcsSmsSendLog
from web.controllers.api import route_api


@route_api.route("/special/info", methods=['GET', 'POST'])
def specialProductInfo():
    data = APP_CONSTANTS['sp_product']
    return jsonify(data)


@route_api.route('/qrcode/before/nav', methods=['POST', 'GET'])
def qrCodeScanFreq():
    """
    扫码引导前判断此时收到扫码操作的合理性
    :return:
    """

    resp = {'code': -1, 'msg': ''}
    req = request.values
    openid = req.get('openid', '')
    if not openid:
        resp['msg'] = '扫码失败'
        return jsonify(resp)
    member_info = g.member_info
    is_reg = member_info is not None
    if is_reg and member_info.openid == openid:
        # 自己扫码
        # 找到该用户一个月内的手机更换记录
        phoneChangeLog = MemberPhoneChangeLog.query.filter(MemberPhoneChangeLog.openid == openid,
                                                           MemberPhoneChangeLog.create_time >=
                                                           datetime.datetime.now() - datetime.timedelta(
                                                               weeks=4)).first()
        if phoneChangeLog:
            resp['data'] = {
                'phone_change_time': phoneChangeLog.created_time.strftime(APP_CONSTANTS['time_format_short'])
            }
    else:
        # 别人扫码
        # 找到该二维码新鲜的扫码归还记录进行提示
        good = Good.query.filter_by(qr_code_openid=openid, status=2).first()
        if good:
            resp['data'] = {
                'goods_name': good.name,
                'found_time': good.created_time.strftime(APP_CONSTANTS['time_format_short'])
            }

    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/qrcode/wx", methods=['GET', 'POST'])
def getQrcode():
    """
    为会员生成微信二维码
    :return:二维码图片URL
    """
    resp = {'code': -1, 'msg': '', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)

    # 会员已有二维码
    if member_info.has_qr_code:
        resp['code'] = 200
        resp['data']['qr_code_url'] = UrlManager.buildImageUrl(member_info.qr_code, image_type='QR_CODE')
        return jsonify(resp)

    # 调API获取二维码
    from common.libs.mall.WechatService import WeChatService
    token = WeChatService.get_wx_token()
    if not token:
        resp['msg'] = "微信繁忙"
        return jsonify(resp)
    wx_resp = QrCodeService.get_wx_qr_code(token, member_info)

    # API成功,保存二维码
    # API失败,记录错误日志
    if len(wx_resp.content) < 80:
        data = wx_resp.json()
        app.logger.error("没拿到二维码. 错误码: %s, 错误信息:%s", data['errcode'], data['errmsg'])
        resp['msg'] = "微信繁忙"
        return jsonify(resp)
    else:
        # 存成文件,db新增二维码
        path = QrCodeService.save_wx_qr_code(member_info, wx_resp)
        resp['code'] = 200
        resp['data'] = {'qr_code_url': UrlManager.buildImageUrl(path, image_type='QR_CODE')}
        return jsonify(resp)


@route_api.route("/qrcode/sms", methods=['GET', 'POST'])
def sendVerifyCode():
    """
    向手机号发验证短信
    example request body
    {
        phone:177*****081
    }
    :return:

    """
    resp = {'code': -1, 'msg': '验证码发送成功，请留意短信', 'data': {}}
    params = request.get_json()
    phone = params['phone'] if 'phone' in params else ''
    if not phone:
        resp['msg'] = "手机号异常"
        return jsonify(resp)
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)
    if member_info.mobile == phone:
        resp['msg'] = "请输入与原手机号不同的手机号"
        return jsonify(resp)

    member_id = member_info.id
    member_openid = member_info.openid
    # 5分钟间隔
    sendLog = AcsSmsSendLog.query.filter(AcsSmsSendLog.trigger_member_id == member_id,
                                         AcsSmsSendLog.created_time > datetime.datetime.now() - datetime.timedelta(
                                             minutes=5),
                                         AcsSmsSendLog.acs_code == "OK",
                                         AcsSmsSendLog.template_id == APP_CONSTANTS['ACS_SMS']['TEMP_IDS']['VERIFY']).first()

    if sendLog:
        resp['msg'] = '两次操作间隔不能短于5分钟，请稍后再试'
        return jsonify(resp)

    code = SMSService.generate_sms_code()
    # 触发和接受验证码短信的用户是同一人
    trig_rcv_info = {
        'trig_member_id': member_id,
        'trig_openid': member_openid,
        'rcv_openid': member_openid,
        'rcv_member_id': member_id
    }
    send_ok = SMSService.send_verify_code(phone=phone, code=code, trig_rcv_info=trig_rcv_info)
    if not send_ok:
        resp['msg'] = '验证码发送失败，请检查手机号是否正确'
        return jsonify(resp)

    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/qrcode/check/sms", methods=['GET', 'POST'])
def checkVerifyCode():
    """
    检查输入验证码=有效发送验证码
    :return:
    """
    resp = {'code': 200, 'msg': '', 'data': {}}
    params = request.get_json()
    # 参数校验
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "绑定信息出错，请稍候重试"
        return jsonify(resp)
    phone = params['phone'] if 'phone' in params else ''
    if not phone:
        resp['code'] = -1
        resp['msg'] = "手机号异常"
        return jsonify(resp)
    inputCode = params['code'] if 'code' in params else ''
    if not inputCode:
        resp['code'] = -1
        resp['msg'] = "验证码错误"
        return jsonify(resp)

    # 最近的一次5分钟内的验证码发送
    codeSendLog = AcsSmsSendLog.query.filter(AcsSmsSendLog.phone_number == phone,
                                             AcsSmsSendLog.template_id == app.config['ACS_SMS']['TEMP_IDS']['VERIFY'],
                                             AcsSmsSendLog.created_time > datetime.datetime.now() -
                                             datetime.timedelta(minutes=5)) \
        .order_by(AcsSmsSendLog.id.desc()).first()
    if codeSendLog is None:
        resp['code'] = -1
        resp['msg'] = "验证码已过期，请重新获取验证码"
        return jsonify(resp)
    else:
        params = json.loads(codeSendLog.params)
        sentCode = params['code'] if 'code' in params else ''
        if not sentCode:
            resp['code'] = -1
            resp['msg'] = "校验信息异常，请稍候重试"
            return jsonify(resp)
        if sentCode == inputCode:
            new_mobile = Cipher.encrypt(text=phone)
            # 新增用户手机变更记录
            model_log = MemberPhoneChangeLog()
            model_log.member_id = member_info.id
            model_log.openid = member_info.openid
            model_log.new_mobile = new_mobile
            model_log.old_mobile = member_info.mobile
            db.session.add(model_log)
            # 更新用户字段
            member_info.mobile = new_mobile
            db.session.add(member_info)
            db.session.commit()
            return jsonify(resp)
        else:
            resp['code'] = -1
            resp['msg'] = "验证失败"
            return jsonify(resp)
