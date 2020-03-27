import datetime
import decimal
from decimal import Decimal

from flask import request, jsonify, g
import json
from application import app, db
from common.libs import QrCodeService
from common.libs.UrlManager import UrlManager
from common.libs.sms import SMSService
from common.models.ciwei.AcsSmsSendLog import AcsSmsSendLog
from common.models.ciwei.Member import Member
from common.models.ciwei.MemberSmsPkg import MemberSmsPkg
from web.controllers.api import route_api


@route_api.route("/special/info", methods=['GET', 'POST'])
def specialProductInfo():
    data = {
        'qrcode': {
            'id': 15,
            'price': 2.5
        },
        'sms_pkg': {
            'id': 16,
            'price': 4.5
        },
        'sms': {
            'id': 17,
            'price': 0.1
        },
        'top': {
            'price': 0.01,
            'days': 7
        },
        'free_sms': {
            'times': 5
        }
    }
    return jsonify(data)


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


@route_api.route("/qrcode/notify", methods=['GET', 'POST'])
def scan_qr_code():
    """
    通知失主
    :return:
    """
    params = request.get_json()
    openid = params['openid'] if 'openid' in params else ''
    if not openid:
        return True
    # 判断扣除短信包还按量计费的条数，还是用户余额
    op_status = 0
    pkg = MemberSmsPkg.query.filter(MemberSmsPkg.open_id == openid,
                                    MemberSmsPkg.expired_time <= datetime.datetime.now(),
                                    MemberSmsPkg.left_notify_times > 0).first()

    if not pkg:
        member_info = Member.query.filter(Member.openid == openid, Member.status == 1).first()
        if member_info.left_notify_times > 0:
            op_status = 1
        elif member_info.balance >= decimal.Decimal('0.10'):
            op_status = 2
        else:
            return True

    data = params['goods'] if 'goods' in params else ''
    if not data:
        return True
    target_member_info = Member.query.filter_by(openid=openid).first()
    if target_member_info:
        send_ok = SMSService.send_lost_notify(phone=target_member_info.mobile, goods_name=data['goods_name'],
                                              location=data['location'][1] if len(data['location']) > 1 else '')
        if send_ok:
            if op_status == 0:
                pkg.left_notify_times -= 1
                db.session.add(pkg)
            elif op_status == 1:
                member_info.left_notify_times -= 1
                db.session.add(member_info)
            elif op_status == 2:
                member_info.balance -= Decimal("0.10")
                db.session.add(member_info)

    db.session.commit()
    return True


@route_api.route("/qrcode/sms", methods=['GET', 'POST'])
def get_sms_code():
    """
    向手机号发验证短信
    example request body
    {
        phone:177*****081
    }
    :return:

    """
    resp = {'code': 200, 'msg': '验证码发送成功，请留意短信', 'data': {}}
    params = request.get_json()
    phone = params['phone'] if 'phone' in params else ''
    if not phone:
        resp['code'] = -1
        resp['msg'] = "手机号异常"
        return jsonify(resp)
    if g.member_info and g.member_info.mobile == phone:
        resp['code'] = -1
        resp['msg'] = "请输入与原手机号不同的手机号"
        return jsonify(resp)

    # 5分钟间隔
    sendLog = AcsSmsSendLog.query.filter(AcsSmsSendLog.phone_number == phone,
                                         AcsSmsSendLog.created_time > datetime.datetime.now() - datetime.timedelta(
                                             minutes=5),
                                         AcsSmsSendLog.acs_code == "OK").first()

    if sendLog:
        resp['code'] = -1
        resp['msg'] = '两次操作间隔不能短于5分钟，请稍后再试'
        return jsonify(resp)

    code = SMSService.generate_sms_code()
    send_ok = SMSService.send_verify_code(phone=phone, code=code)
    if not send_ok:
        resp['code'] = -1
        resp['msg'] = '验证码发送失败，请检查手机号是否正确'

    return jsonify(resp)


@route_api.route("/qrcode/check/sms", methods=['GET', 'POST'])
def check_sms_code():
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
            member_info.mobile = phone
            db.session.add(member_info)
            db.session.commit()
            return jsonify(resp)
        else:
            resp['code'] = -1
            resp['msg'] = "验证失败"
            return jsonify(resp)
