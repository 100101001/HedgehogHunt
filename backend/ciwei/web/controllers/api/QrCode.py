# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/11 下午11:56
@file: QrCode.py
@desc:
"""

from flask import request, g

from application import APP_CONSTANTS
from common.libs.QrCodeService import QrCodeHandler
from web.controllers.api import route_api


@route_api.route("/special/info", methods=['GET', 'POST'])
def specialProductInfo():
    data = APP_CONSTANTS['sp_product']
    return data


@route_api.route('/qrcode/scan/freq', methods=['POST', 'GET'])
def qrCodeScanFreq():
    """
    扫码引导前判断此时收到扫码操作的合理性
    :return:
    """

    resp = {'code': -1, 'msg': ''}
    openid = request.values.get('openid')
    if not openid:
        resp['msg'] = '扫码失败'
        return resp
    data = QrCodeHandler.deal('freq', scan_member=g.member_info, openid=openid)
    if data:
        resp['data'] = data
    resp['code'] = 200
    return resp


@route_api.route("/qrcode/wx", methods=['GET', 'POST'])
def getQrcode():
    """
    为会员生成微信二维码
    :return:二维码图片URL
    """
    resp = {'code': -1, 'msg': '获取失败，请联系技术支持获取', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    op_res = QrCodeHandler.deal('gain', member_info=member_info)
    resp['code'] = 200 if op_res else -1
    return resp


@route_api.route("/qrcode/sms", methods=['GET', 'POST'])
def sendVerifyCode():
    """
    向手机号发验证短信
    :return:

    """
    resp = {'code': -1, 'msg': '验证码发送成功，请留意短信', 'data': {}}
    params = request.get_json()
    phone = params.get('phone')
    if not phone:
        resp['msg'] = "请输入正确的手机号"
        return resp
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    op_res, op_msg = QrCodeHandler.deal('verify_mobile', mobile=phone, rcv_member=member_info)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp


@route_api.route("/qrcode/check/sms", methods=['GET', 'POST'])
def checkVerifyCode():
    """
    检查输入验证码=有效发送验证码
    :return:
    """
    resp = {'code': -1, 'msg': '验证码错误或已过期', 'data': {}}
    params = request.get_json()
    # 参数校验
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    phone, inputCode = params.get('phone'), params.get('code')
    if not phone or not inputCode:
        resp['msg'] = "验证码错误"
        return resp

    op_res, op_msg = QrCodeHandler.deal('bind_mobile', input_code=inputCode, mobile=phone, member_info=member_info)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp
