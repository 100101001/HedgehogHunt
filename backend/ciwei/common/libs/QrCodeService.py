from decimal import Decimal

from application import db, app


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
    return requests.post(
        "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(token),
        json={"scene": str(openid), "width": 280, "page": "pages/index/index"})

    # 测试：10万上限
    # return requests.post(
    #     "https://api.weixin.qq.com/wxa/getwxacode?access_token={}".format(
    #         token),
    #     json={"width": 280, "path": "pages/index/index?openid=" + openid})


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
    member_info.qr_code = qr_code_relative_path
    # 账户返还5毛
    member_info.balance += Decimal("0.50")
    db.session.add(member_info)
    db.session.commit()
    return qr_code_relative_path
