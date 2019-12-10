import base64
import threading
import time

import requests
from flask import request, Response, g
from twilio.rest import Client

from application import app, db, cache
from common.libs import QrCodeService
from common.libs.MemberService import MemberService
from common.models.ciwei.Member import Member
from common.models.ciwei.QrCode import QrCode
from web.controllers.api import route_api

_qr_code_lock = threading.Lock()


@route_api.route("/qrcode/wx", methods=['GET', 'POST'])
def getQrcodeFromWx():
    """
    generate qr code from wx and save to db when purchase from tao bao
    :return:
        500 when error occurs
        200 when get code successfully
    """
    # params = request.get_json()

    # add lock to prevent concurrent operations on getting access token & getting qr code (id)
    with _qr_code_lock:
        # query db if token expires
        if not hasattr(g, 'token'):
            setattr(g, 'token', {})
        token = g.token

        if not token or token['expires'] > time.time() - 5 * 60 * 1000:
            # get new token
            url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(
                app.config['OPENCS_APP']['appid'], app.config['OPENCS_APP']['appkey'])
            wxResp = requests.get(url)
            if 'access_token' not in wxResp.json().keys():
                data = wxResp.json()
                app.logger.error("failed to get token! Errcode: %s, Errmsg:%s", data['errcode'], data['errmsg'])
                return Response(status=500)
            else:
                data = wxResp.json()
                token['token'] = data['access_token']
                token['expires'] = data['expires_in'] + time.time()
                g.token = token

        maxCodeId = db.session.query(db.func.max(QrCode.id)).scalar()
        if maxCodeId is None:
            maxCodeId = 0
        maxCodeId += 1
        # only when little program is released can we use the unlimited api
        # [2019-12-10 16:06:50,066] ERROR in QrCode: failed to get qr code. Errcode: 41030, Errmsg:invalid page hint: [6qqTta0210c393]
        # wxResp = requests.post(
        #     "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(token['token']),
        #     json={"scene": str(maxCodeId), "width": 280, "page": "pages/index/index"})

        # now use 100 thousand limited api for test
        wxResp = requests.post(
            "https://api.weixin.qq.com/wxa/getwxacode?access_token={}".format(
                token['token']),
            json={ "width": 280, "path": "pages/index/index?id=1"})

        # / pages / index / index
        if len(wxResp.content) < 80:
            data = wxResp.json()
            app.logger.error("failed to get qr code. Errcode: %s, Errmsg:%s", data['errcode'], data['errmsg'])
            return Response(status=500)
        else:
            # save compressed qr code to db
            db.session.add(QrCode(qr_code=wxResp.content))
            db.session.commit()
            app.logger.info('get qr code successfully')
            return Response(response=str(base64.b64encode(wxResp.content), 'utf-8'), status=200)


@route_api.route("/qrcode/db", methods=['GET', 'POST'])
def getQrcodeFromDb():
    """
    get qr code from db by member id
    :return:
        201 when member has no qr code in db
        200 when member has qr code in db
    """
    params = request.get_json()
    qrCode = QrCode.query.filter_by(member_id=params['memberId']).first()
    if qrCode is None:
        app.logger.info("member id: %s has no qr code stored in db", params['memberId'])
        return Response(status=201)
    return Response(response=str(base64.b64encode(qrCode.qr_code), 'utf8'), status=200)


@route_api.route("/qrcode/scan", methods=['GET', 'POST'])
def scanQrcode():
    """
    scan qr code {qrcode id} , return whether the qr code id has been registered
    :return:
      500 when no qr code with {id} in db
      200 when has qr code with {id} in db
          true when linked to a member
          false when no linked member
    """
    params = request.get_json()
    codeId = params['id']
    # check whether user is a member
    qrcode = QrCode.query.filter_by(id=int(codeId)).first()
    if qrcode is None:
        app.logger.error("failed to get qr code")
        return Response(status=500)
    if qrcode.member_id is None:
        app.logger.info("go to register qr code: %s", codeId)
        return Response(response={'data': False}, status=200)
    else:
        app.logger.info("go to publish qr code: %s", codeId)
        return Response(response={'data': True}, status=200)


@route_api.route("/qrcode/sms", methods=['GET', 'POST'])
def getSmsCode():
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
