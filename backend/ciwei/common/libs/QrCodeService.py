import random

from application import db, app
from common.models.ciwei.QrCode import QrCode


def thank_qrcode(codeId, orderId):
    """
       fill in  order_id to a qr code record with specific id
       :return:
       """
    # add orderId to qrCodeId
    pass


def generateSmsVerCode():
    """
    generate six-bit verification code
    :return:  verification code
    """

    code = []
    for i in range(6):
        code.append(str(random.randint(0, 9)))
    return ''.join(code)


def addMemberIdToQrcode(qrcodeId, memberId):
    """
    one user first scan qr code to register
    his/her member id will be added to qrcode
    :return:
     if qrcode id can belong to member id
    """
    if not qrcodeId:
        app.logger.error("need qr code id")
        return False

    qrcode = QrCode.query.filter_by(id=qrcodeId).first()
    if qrcode is None:
        app.logger.error("qr code id %s not exists", qrcodeId)
        return False
    else:
        if qrcode.member_id is None:
            qrcode.member_id = memberId
            db.session.commit()
            app.logger.info("member: %s is added to qr code: %s  successfully", memberId, qrcodeId)
            return True
        else:
            if qrcode.member_id == qrcode.member_id:
                app.logger.info("qr code: %s already belongs to member: %s", qrcodeId, memberId)
                return True
            else:
                app.logger.error("qr code: %s already belongs to member: %s", qrcodeId, qrcode.member_id)
                return False


def getQrcodeById(qrcodeId):
    return QrCode.query.filter_by(id=qrcodeId).first()


def get_wx_token():
    from flask import session
    import requests
    import time

    if not hasattr(session, 'token'):
        setattr(session, 'token', {})
    token = session.token

    if not token or token['expires'] > time.time() - 5 * 60 * 1000:
        # get new token
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(
            app.config['OPENCS_APP']['appid'], app.config['OPENCS_APP']['appkey'])

        wxResp = requests.get(url)
        if 'access_token' not in wxResp.json().keys():
            data = wxResp.json()
            app.logger.error("failed to get token! Errcode: %s, Errmsg:%s", data['errcode'], data['errmsg'])
            session.token = None
            return None
        else:
            data = wxResp.json()
            token['token'] = data['access_token']
            token['expires'] = data['expires_in'] + time.time()
            session.token = token
            return session.token['token']


def get_wx_qr_code(token):
    """

    :param token:
    :return:
    """
    import requests

    maxCodeId = db.session.query(db.func.max(QrCode.id)).scalar()
    if not maxCodeId:
        maxCodeId = 0
    maxCodeId += 1

    # only when little program is released can we use the unlimited api
    # [2019-12-10 16:06:50,066] ERROR in QrCode: failed to get qr code. Errcode: 41030, Errmsg:invalid page hint: [6qqTta0210c393]
    # return wxResp = requests.post(
    #     "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(token),
    #     json={"scene": str(maxCodeId), "width": 280, "page": "pages/index/index"})

    # now use 100 thousand limited api for test
    return requests.post(
        "https://api.weixin.qq.com/wxa/getwxacode?access_token={}".format(
            token),
        json={"width": 280, "path": "pages/index/index?id=" + str(maxCodeId)}), str(maxCodeId)


def save_wx_qr_code(qr_code_id, member_info, wx_resp):
    from common.libs import Helper
    import stat
    import os
    # 保存文件
    today = Helper.getCurrentDate("%Y%m%d")
    qr_code_dir = app.root_path + app.config['QR_CODE']['prefix_path'] + today
    if not os.path.exists(qr_code_dir):
        os.mkdir(qr_code_dir)
        os.chmod(qr_code_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)
    with open(qr_code_dir + "/" + qr_code_id + ".jpg", 'wb') as f:
        f.write(wx_resp.content)

    # db新增二维码, 会员绑定二维码
    qr_code_relative_path = today + "/" + qr_code_id + ".jpg"
    db.session.add(QrCode(member_id=member_info.id, qr_code=qr_code_relative_path))
    member_info.qr_code_id = qr_code_id
    member_info.qr_code = qr_code_relative_path
    db.session.commit()
    app.logger.info('get qr code successfully')
    return qr_code_relative_path


def is_member_login():
    return not g.member_info
