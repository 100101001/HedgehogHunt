from flask import g
from application import app
from common.libs import Helper
from web.controllers.api import route_api


@route_api.route("order", methods=['GET', 'POST'])
def placeOrder():
    import requests
    import hmac
    from hashlib import sha256
    """
    调用统一下单API获取prepay_id
    :return: 
    """

    resp = {"data": {}, "msg": "", "code": 200}
    member_info = g.member_info

    if not member_info:
        resp.code = -1
        resp["msg"] = "未登录"

    # 获取openid
    openid = member_info.openid

    # TODO：数据库下单

    # 调用微信支付的统一下单接口
    url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    data = {
        "appid": app.config['OPENCS_APP']['appid'],
        "mch_id": app.config['OPENCS_APP']['mch_id'],
        "nonce_str": Helper.genRandomStr(16),
        "body": "闪寻-充值",
        "out_trade_no": "",  # 数据库订单id
        "total_fee": 5,
        "spbill_create_ip": app.config['IP'],
        "time_expire": "",  # TODO：订单失效时间
        "notify_url": "",  # TODO：微信异步同志支付结果
        "trade_type": "JSAPI",
        "limit_pay": "no_credit",  # 限制支付方式
        "openid": openid,

    }
    # 计算签名
    string_a = ""
    for item in sorted(data.items()):
        string_a = string_a + item[0] + "=" + item[1] + "&"
    data["sign"] = hmac.new(app.config['OPENCS_APP']['mch_key'],
                            msg=string_a + "key=" + app.config['OPENCS_APP']['mch_key'],
                            digestmod=sha256)
    data["sign_type"] = "HMAC-SHA256"

    # 处理API响应
    wxResp = requests.post(url, data)
    data = wxResp.json()
    if data['return_code'] == "SUCCESS":
        # 下单成功
        if data['result_code'] == "SUCCESS":
            resp['msg'] = "微信下单成功"
            resp['data']['prepay_id'] = data['prepay_id']
        else:
            resp['msg'] = "微信下单失败, 错误信息" + data['err_code_des']
            resp['code'] = -1
    else:
        resp['msg'] = "微信服务器故障或签名有误"
        resp['code'] = -1

    return resp

# TODO:微信支付
@route_api.route("pay", method=['POST'])
def pay():
    pass
