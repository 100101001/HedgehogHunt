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
        json={'scene': 'a=1', 'width': 280, 'path': 'pages/Find/info/info'})

    if len(wxResp.content) < 80:
        data = wxResp.json()
        # resp['code'] = data['errcode']
        # resp['msg'] = data['errmsg']
        # return jsonify(resp)
        app.logger.error("failed to get qr code. Errcode: %s, Errmsg:%s", data['errcode'], data['errmsg'])
        return Response(status=500)
    else:
        # save compressed qr code to db
        db.session.add(
            QrCode(member_id=params['memberId'], order_id=params['orderId'], name=params['username'],
                   qr_code=wxResp.content))
        db.session.commit()
        app.logger.info('member: %s name: %s order: %s get qr code successfully', params['memberId'],
                        params['username'],
                        params['orderId'])
        # resp['code'] = 200
        # resp['data'] = str(base64.b64encode(wxResp.content), 'utf-8')
        # return Response(response=wxResp.content, status=200, mimetype='image/jpeg')
        return Response(response=str(base64.b64encode(wxResp.content), 'utf-8'), status=200)
    # return jsonify(resp)


@route_api.route("/qrcode/db", methods=['GET', 'POST'])
def getQrcodeFromDb():
    params = request.get_json()
    qrCode = QrCode.query.filter_by(member_id=params['memberId']).first()
    if qrCode is None:
        app.logger.info("member id: %s has no qr code stored in db", params['memberId'])
        return Response(status=201)
    return Response(response=str(base64.b64encode(qrCode.qr_code), 'utf8'), status=200)
