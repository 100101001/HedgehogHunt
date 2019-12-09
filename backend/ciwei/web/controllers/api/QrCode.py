import base64
import threading
import time

import requests
from flask import request, Response, g
from twilio.rest import Client

from application import app, db, cache
from common.libs import QrCodeService
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
        maxCodeId += 1
        wxResp = requests.post(
            "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(token['token']),
            json={'scene': 'a=1', 'width': 280, 'path': '/pages/index/index?id=' + maxCodeId})

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


@route_api.route("/qrcode/reg", methods=['GET', 'POST'])
def regQrcode():
    """
    add member recorder
    fill in  member_id to a qr code record with specific id
    :return:
        200 when new member is generated and linked to qr code
        500 when error occurs
    """
    params = request.get_json()
    codeId = params['codeId']
    memberId = params['memberId']
    app.logger.info("code: %s is registered successfully by member: %s ", codeId, memberId)
    pass


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
