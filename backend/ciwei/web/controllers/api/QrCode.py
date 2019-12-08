import base64
import time

import requests
from flask import request, Response, g

from application import app, db
from common.models.ciwei.QrCode import QrCode
from web.controllers.api import route_api


@route_api.route("/qrcode/wx", methods=['GET', 'POST'])
def getQrcodeFromWx():
    """
    request params example:
        {
          "memberId":1,
          "order_id":1,
          "username":"lyx"
        }
    response usage example:
    if status code is OK:
       <img src="{{returned jpg file}}">
    else:
        <img src={{alternative failure picture}}>
    :return:
    """
    params = request.get_json()
    # resp = {'code': 200, 'msg': 'getQrcode', 'data': {}}
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
            # resp['code'] = -1
            # resp['msg'] = "failed to get token!"
            # resp['data'] = {}
            app.logger.error("failed to get token! Errcode: %s, Errmsg:%s", data['errcode'], data['errmsg'])
            return Response(status=500)
        else:
            data = wxResp.json()
            token['token'] = data['access_token']
            token['expires'] = data['expires_in'] + time.time()
            g.token = token

    wxResp = requests.post(
        "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(token['token']),
        json={'scene': 'a=1', 'width': 280, 'path': 'pages/QrCode?id=1'})

    if len(wxResp.content) < 80:
        data = wxResp.json()
        # resp['code'] = data['errcode']
        # resp['msg'] = data['errmsg']
        # return jsonify(resp)
        app.logger.error("failed to get qr code. Errcode: %s, Errmsg:%s", data['errcode'], data['errmsg'])
        return Response(status=500)
    else:
        # save compressed qr code to db
        db.session.add(QrCode(qr_code=wxResp.content))
        db.session.commit()
        # app.logger.info('member: %s name: %s order: %s get qr code successfully', params['memberId'],
        #                 params['username'],
        #                 params['orderId'])
        app.logger.info('get qr code successfully')
        # resp['code'] = 200
        # resp['data'] = str(base64.b64encode(wxResp.content), 'utf-8')
        # return Response(response=wxResp.content, status=200, mimetype='image/jpeg')
        return Response(response=str(base64.b64encode(wxResp.content), 'utf-8'), status=200)
    # return jsonify(resp)


@route_api.route("/qrcode/db", methods=['GET', 'POST'])
def getQrcodeFromDb():
    """
    get qr code from db by member id
    :return:
    """
    params = request.get_json()
    qrCode = QrCode.query.filter_by(member_id=params['memberId']).first()
    if qrCode is None:
        app.logger.info("member id: %s has no qr code stored in db", params['memberId'])
        return Response(status=201)
    return Response(response=str(base64.b64encode(qrCode.qr_code), 'utf8'), status=200)

@route_api.route("/qrcode/scan", methods=['GET','POST'])
def scanQrcode():
    """
    scan qr code {qrcode id} , return whether the qr code id has been registered
    :return:
    """
    params = request.get_json()
    codeId = params['id']
    # check whether user is a member
    qrcode = QrCode.query.filter_by(id=codeId).first()
    if qrcode is None:
        app.logger.error("failed to get qr code")
        return Response(status=500)
    if qrcode.member_id is None:
        return Response(response=False, status=200)
    else:
        return Response(response=True, status=200)

@route_api.route("/qrcode/buy", methods=['GET', 'POST'])
def buyQrcode():
    """
    fill in  order_id to a qrcode record with specific id
    :return:
    """
    params = request.get_json()
    codeId = params['codeId']
    orderId = params['orderId']
    app.logger.info("code: %s is bought successfully, order: %s ", codeId, orderId)
    pass

@route_api.route("/qrcode/reg", methods=['GET', 'POST'])
def regQrcode():
    """
    add member recorder
    fill in  member_id to a qrcode record with specific id
    :return:
    """
    params = request.get_json()
    codeId = params['codeId']
    memberId = params['memberId']
    app.logger.info("code: %s is registered successfully by member: %s ", codeId, memberId)
    pass

@route_api.route("/qrcode/publish", methods=['GET', 'POST'])
def pubQrcode():
    """
    scan a registered qr code to
    :return:
    """
    params = request.get_json()
    codeId = params['id']
    app.logger.info("codeId: %s is been found , and scanned to publish lost goods ", codeId)
    pass