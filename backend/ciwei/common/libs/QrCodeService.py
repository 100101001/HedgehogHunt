import random

from application import db, app
from common.models.ciwei.QrCode import QrCode


def generate_sms_code():
    """
    generate six-bit verification code
    :return:  verification code
    """

    code = []
    for i in range(6):
        code.append(str(random.randint(0, 9)))
    return ''.join(code)


def get_wx_qr_code(token, member):
    """
    :param member:
    :param token:
    :return:
    """
    import requests
    openid = member.openid

    # 无限API上线可用(体验版)
    # [2019-12-10 16:06:50,066] ERROR in QrCode: failed to get qr code. Errcode: 41030, Errmsg:invalid page hint: [6qqTta0210c393]
    # return requests.post(
    #     "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(token),
    #     json={"scene": str(openid), "width": 280, "page": "pages/index/index"})

    # 测试：10万上限
    return requests.post(
        "https://api.weixin.qq.com/wxa/getwxacode?access_token={}".format(
            token),
        json={"width": 280, "path": "pages/index/index?openid=" + openid})


def save_wx_qr_code(member_info, wx_resp):
    from common.libs import Helper
    import stat
    import os
    import uuid
    # 保存文件
    today = Helper.getCurrentDate("%Y%m%d")
    qr_code_dir = app.root_path + app.config['QR_CODE']['prefix_path'] + today
    qr_code_file = str(uuid.uuid4())
    if not os.path.exists(qr_code_dir):
        os.mkdir(qr_code_dir)
        os.chmod(qr_code_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)
    with open(qr_code_dir + "/" + qr_code_file + ".jpg", 'wb') as f:
        f.write(wx_resp.content)

    # db新增二维码, 会员绑定二维码
    qr_code_relative_path = today + "/" + qr_code_file + ".jpg"
    now = Helper.getCurrentDate()
    qr_code = QrCode(member_id=member_info.id,
                     openid=member_info.openid,
                     qr_code=qr_code_relative_path,
                     updated_time=now,
                     created_time=now)
    db.session.add(qr_code)
    db.session.commit()
    member_info.qr_code_id = qr_code.id
    member_info.qr_code = qr_code_relative_path
    db.session.add(member_info)
    db.session.commit()
    app.logger.info('二维码文件，两个表更新：OK')
    return qr_code_relative_path


def send_notify_message(data, number):
    """
    发达通知
    :param data:
    :param number:
    :return:
    """
    message = "遗失物品：" + data['goods_name'] + ", 遗失地点:" + data['location'][1]
    from twilio.rest import Client
    client = Client(app.config['TWILIO_SERVICE']['accountSID'], app.config['TWILIO_SERVICE']['authToken'])
    try:
        client.messages.create(body=message, from_=app.config['TWILIO_SERVICE']['twilioNumber'], to='+86'+number)
        app.logger.info("已通知 %s", number)
    except Exception:
        app.logger.error("通知失败 %s", number)
