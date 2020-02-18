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


def get_wx_qr_code(token, member):
    """

    :param member:
    :param token:
    :return:
    """
    import requests
    #
    # maxCodeId = db.session.query(db.func.max(QrCode.id)).scalar()
    # if not maxCodeId:
    #     maxCodeId = 0
    # maxCodeId += 1
    openid = member.openid

    # only when little program is released can we use the unlimited api
    # [2019-12-10 16:06:50,066] ERROR in QrCode: failed to get qr code. Errcode: 41030, Errmsg:invalid page hint: [6qqTta0210c393]
    # return wxResp = requests.post(
    #     "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(token),
    #     json={"scene": str(openid), "width": 280, "page": "pages/index/index"})

    # now use 100 thousand limited api for test
    return requests.post(
        "https://api.weixin.qq.com/wxa/getwxacode?access_token={}".format(
            token),
        json={"width": 280, "path": "pages/index/index?openid=" + openid}), openid


def save_wx_qr_code(member_info, wx_resp):
    from common.libs import Helper
    import stat
    import os
    import uuid
    # 保存文件
    today = Helper.getCurrentDate("%Y%m%d")
    qr_code_dir = app.root_path + app.config['QR_CODE']['prefix_path'] + today
    qr_code_file = uuid.uuid4()
    if not os.path.exists(qr_code_dir):
        os.mkdir(qr_code_dir)
        os.chmod(qr_code_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)
    with open(qr_code_dir + "/" + qr_code_file + ".jpg", 'wb') as f:
        f.write(wx_resp.content)

    # db新增二维码, 会员绑定二维码
    qr_code_relative_path = today + "/" + qr_code_file + ".jpg"
    qr_code = QrCode(member_id=member_info.id, qr_code=qr_code_relative_path)
    db.session.add(qr_code)
    db.session.commit()
    member_info.qr_code_id = qr_code.id
    member_info.qr_code = qr_code_relative_path
    db.session.commit()
    app.logger.info('二维码文件，两个表更新：OK')
    return qr_code_relative_path


def is_member_login():
    return not g.member_info
