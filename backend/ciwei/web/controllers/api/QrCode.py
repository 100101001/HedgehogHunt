import threading

from flask import request, Response, jsonify, g
from twilio.rest import Client

from application import app, db, cache
from common.libs import QrCodeService
from common.libs.MemberService import MemberService
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Member import Member
from common.models.ciwei.QrCode import QrCode
from web.controllers.api import route_api

_qr_code_lock = threading.Lock()


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
        resp['data']['qr_code_url'] = {'qr_code_url': UrlManager.buildImageUrl(member_info.qr_code, image_type=1)}
        return jsonify(resp)

    # 调API获取二维码
    from common.libs import WechatService
    token = WechatService.get_wx_token()
    if not token:
        resp['msg'] = "微信繁忙"
        return jsonify(resp)
    wx_resp, openid = QrCodeService.get_wx_qr_code(token, member_info)

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
        resp['data']['qr_code_url'] = {'qr_code_url': UrlManager.buildImageUrl(path, image_type=1)}
        # return Response(response=str(base64.b64encode(wx_resp.content), 'utf-8'), status=200)
        return jsonify(resp)


@route_api.route("/qrcode/db", methods=['GET', 'POST'])
def get_db_qr_code():
    """
    get qr code from db by member id
    :return: 二维码图片URL
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)

    qr_code = QrCode.query.filter_by(member_id=member_info.id).first()
    if qr_code is None:
        app.logger.info("member id: %s has no qr code stored in db", member_info.id)
        resp['code'] = 201
        resp['msg'] = "会员无二维码"
        return jsonify(resp)
    # return Response(response=str(base64.b64encode(qr_code.qr_code), 'utf8'), status=200)
    resp['code'] = 200
    resp['data'] = {'qr_code_url': UrlManager.buildImageUrl(qr_code.qr_code, image_type=1)}
    return jsonify(resp)


@route_api.route("/qrcode/scan", methods=['GET', 'POST'])
def scan_qr_code():
    """
    scan qr code {qrcode id} , return whether the qr code id has been registered
    :return: 返回二维码是否已绑定手机号(已经激活)
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    params = request.get_json()
    code_id = params['id']

    # 检查参数:二维码id
    qr_code = QrCode.query.filter_by(id=int(code_id)).first()
    if qr_code is None:
        app.logger.error("failed to get qr code")
        resp['msg'] = "参数错误"
        return jsonify(resp)

    resp['code'] = 200
    if not qr_code.mobile:
        app.logger.info("下一步：激活二维码,绑定手机号, id: %s", code_id)
        resp['data'] = {"activated": False}
        resp['msg'] = "未激活,前往绑定手机号"
        # return Response(status=200)
    else:
        app.logger.info("下一步:扫码推送有人捡到了你的东西,id: %s", code_id)
        resp['data'] = {"activated": True}
        resp['msg'] = "已激活,前往发布信息"
        # return Response(status=201)
    return jsonify(resp)


@route_api.route("/qrcode/sms", methods=['GET', 'POST'])
def get_sms_code():
    """
    verify phone number through sms code
    example request body
    {
        phone:177*****081
    }
    :return:
     200 when code sent
     400 when user request for code to frequently
     500 when error occurs
    """
    params = request.get_json()
    if cache.get(params['phone']) is None:
        number = '+86' + params['phone']
        smsCode = QrCodeService.generateSmsVerCode()
        # save to db or phone-smsCode cache used by checkSmsCode
        cache.set(params['phone'], smsCode)
        # send sms
        message = "[刺猬寻物] Your verification code is: " + smsCode
        client = Client(app.config['TWILIO_SERVICE']['accountSID'], app.config['TWILIO_SERVICE']['authToken'])
        try:
            client.messages.create(body=message, from_=app.config['TWILIO_SERVICE']['twilioNumber'], to=number)
            app.logger.info("send sms code to phone %s successfuly", number)
            return Response(status=200)
        except Exception:
            app.logger.error("failed to send sms code to phone %s", number)
            return Response(status=500)
    else:
        return Response(status=400)


@route_api.route("/qrcode/check/sms", methods=['GET', 'POST'])
def checkSmsCode():
    """
    check input sms is right
    :return:
     200 when code is valid and right
     400 when code is invalid
     401 when code is valid but user gave a wrong one
    """
    params = request.get_json()
    phone = params['phone']
    inputCode = params['code']
    sentCode = cache.get(phone)
    # retrieve sms code use phone
    if sentCode is None:
        app.logger.info("code is invalid, need to resend sms code")
        return Response(status=400)
    elif sentCode == inputCode:
        app.logger.info("member with phone %s registered successfully", phone)
        # register
        return Response(status=200)
    else:
        app.logger.info("member with phone %s give a wrong sms code", phone)
        return Response(status=401)


@route_api.route("/qrcode/reg", methods=['GET', 'POST'])
def qrcodeReg():
    """
    copy code from /member/login
    add function to put member id to qrcode

    :return:
    when status is 200,  response body is
        data:{
            token: "openid#memberid",
        }
    statusCode:
        200 qrcode id <-> member id bind successfully
        1401 qr code id not exists
        1402 front end give no code
        1501 wechat error
        1403 qrcode cannot belong to user who call this function(system give a wrong)
    """
    req = request.get_json()

    qrcodeId = req['qrcode']
    qrcode = QrCodeService.getQrcodeById(qrcodeId)
    if qrcode is None:
        app.logger.error("qr code: %s not exists", qrcodeId)
        return Response(status=1401)

    code = req['code'] if 'code' in req else ''
    if not code or len(code) < 1:
        app.logger.error("need code to get open id")
        return Response(status=1402)

    # get openid from wechat
    openid = MemberService.getWeChatOpenId(code)
    if openid is None:
        app.logger.error("call wechat service error")
        return Response(status=1501)

    # new a member info or just retrieve member info by openid
    '''
    判断是否已经注册过，注册了直接set qr_code_id and #qrcode
    '''
    member_info = Member.query.filter_by(openid=openid, status=1).first()
    if not member_info and qrcode.member_id is None:
        model_member = Member()
        nickname = req['nickName'] if 'nickName' in req else ''
        sex = req['gender'] if 'gender' in req else 0
        avatar = req['avatarUrl'] if 'avatarUrl' in req else ''
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        model_member.openid = openid
        model_member.qr_code_id = qrcodeId
        # model_member.qr_code = qrcode.qr_code
        db.session.add(model_member)
        db.session.commit()
        member_info = model_member
    elif member_info is not None and qrcode.member_id is None:
        member_info.qr_code_id = qrcodeId
        # model_member.qr_code = qrcode.qr_code
        db.session.commit()
    elif member_info is not None and qrcode.member_id != member_info.id:
        return Response(status=1403)

    app.logger.info("successfully add qrcode %s to member %s", qrcodeId, member_info.id)
    token = "%s#%s" % (openid, member_info.id)
    resp = {'token': token}

    # add member info to qrcode
    QrCodeService.addMemberIdToQrcode(qrcodeId, member_info.id)
    app.logger.info("successfully add member %s to qrcode %s", member_info.id, qrcodeId)
    return Response(response=resp, status=200)


@route_api.route("/qrcode/publish", methods=['GET', 'POST'])
def pubQrcode():
    """
    scan a registered qr code to publish goods
    :return:
      200 when goods is published
      500 when error occurs
    """
    params = request.get_json()
    codeId = params['id']
    app.logger.info("codeId: %s is been found , and scanned to publish lost goods ", codeId)
    pass
