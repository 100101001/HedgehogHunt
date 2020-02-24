from flask import request, jsonify, g
from twilio.rest import Client

from application import app, db, cache
from common.libs import QrCodeService
from common.libs.UrlManager import UrlManager
from common.models.ciwei.QrCode import QrCode
from web.controllers.api import route_api


@route_api.route("/qrcode/wx", methods=['GET', 'POST'])
def get_wx_qr_code():
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
        resp['data']['qr_code_url'] = {'qr_code_url': UrlManager.buildImageUrl(member_info.qr_code, image_type='QR_CODE')}
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
        resp['data']['qr_code_url'] = {'qr_code_url': UrlManager.buildImageUrl(path, image_type='QR_CODE')}
        return jsonify(resp)


@route_api.route("/qrcode/db", methods=['GET', 'POST'])
def get_db_qr_code():
    """
    获取已有二维码
    :return: 二维码图片URL
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)

    qr_code = QrCode.query.filter_by(openid=member_info.openid).first()
    if qr_code is None:
        app.logger.info("会员: %s 没有二维码", member_info.id)
        resp['code'] = 201
        resp['msg'] = "会员无二维码"
        return jsonify(resp)
    resp['code'] = 200
    resp['data'] = {'qr_code_url': UrlManager.buildImageUrl(qr_code.qr_code, image_type='QR_CODE')}
    return jsonify(resp)


@route_api.route("/qrcode/notify", methods=['GET', 'POST'])
def scan_qr_code():
    """
    通知失主
    :return:
    """
    resp = {'code': -1, 'msg': '通知成功', 'data': {}}

    member_info = g.member_info
    if not member_info:
        return jsonify(resp)

    params = request.get_json()
    openid = params['openid']
    data = params['goods']
    qr_code = QrCode.query.filter_by(openid=openid).first()
    if qr_code:
        QrCodeService.send_notify_message(data, qr_code.mobile)

    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/qrcode/sms", methods=['GET', 'POST'])
def get_sms_code():
    """
    向手机号发验证短信
    example request body
    {
        phone:177*****081
    }
    :return:
     200 发送了码
     400 过于频繁操作
     500 内部异常
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    params = request.get_json()
    if cache.get(params['phone']) is None:
        number = '+86' + params['phone']
        smsCode = QrCodeService.generate_sms_code()
        # send sms
        message = "[闪寻] Your verification code is: " + smsCode
        client = Client(app.config['TWILIO_SERVICE']['accountSID'], app.config['TWILIO_SERVICE']['authToken'])
        try:
            client.messages.create(body=message, from_=app.config['TWILIO_SERVICE']['twilioNumber'], to=number)
            app.logger.info("验证码已发 %s successfuly", number)
            # save to db or phone-smsCode cache used by checkSmsCode
            cache.set(params['phone'], smsCode, timeout=300)
            resp['code'] = 200
            return jsonify(resp)
        except Exception:
            app.logger.error("验证码没发成功 %s", number)
            resp['code'] = 500
            return jsonify(resp)
    else:
        resp['code'] = 400
        return jsonify(resp)


@route_api.route("/qrcode/check/sms", methods=['GET', 'POST'])
def check_sms_code():
    """
    检查输入验证码=发送验证码
    :return:
     200 在时限内,正确
     400 超时
     401 在时限内,错误
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    params = request.get_json()
    phone = params['phone']
    inputCode = params['code']
    qrcode_openid = params['openid']
    sentCode = cache.get(phone)
    if sentCode is None:
        app.logger.info("码超时")
        resp['code'] = 400
        return jsonify(resp)
    elif sentCode == inputCode:
        cache.delete(phone)
        qr_code = QrCode.query.filter_by(openid=qrcode_openid).first()
        qr_code.mobile = phone
        app.logger.info("手机号 %s 绑定成功", phone)
        db.session.commit()
        # register
        resp['code'] = 200
        return jsonify(resp)
    else:
        app.logger.info("手机号 %s 错误码", phone)
        resp['code'] = 401
        return jsonify(resp)
