import random

from application import db, app
from common.models.ciwei.QrCode import QrCode


def thankQrcode(codeId, orderId):
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
