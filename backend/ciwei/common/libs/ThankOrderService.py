import time
from application import app, db
from common.libs import Helper
from common.models.ciwei.ThankOrder import ThankOrder


def payment_hmac_sha256_or_md5_sign(data, key=app.config['OPENCS_APP']['mch_key'], sign_type="HMAC-SHA256"):
    """
    将对象所有参数用hmac-sha256签名
    消息格式: key1=value1&key2=value2&...&key={key}, key按字典序
    :param data: 被签名参数对象
    :param key: 签名密钥
    :param sign_type: 签名哈希
    :return: 
    """
    import hmac
    from hashlib import sha256, md5
    # 参数对象按key字典序组成url查询字串
    string_a = ""
    for item in sorted(data.items()):
        string_a = string_a + item[0] + "=" + str(item[1]) + "&"

    # 使用签名算法对字串签名
    if sign_type == "HMAC-SHA256":
        # 256位的二进制序列存成长度32的字节数组, 字节数组又转成64位的大写十六进制串返回
        return hmac.new(bytes(key, encoding='utf-8'),
                        msg=bytes(string_a + "key=" + key, encoding='utf-8'),
                        digestmod=sha256).hexdigest().upper()
    else:
        # 128位的二进制序列存成长度16的字节数组, 字节数组又转成32位的大写十六进制串返回
        return md5(bytes(string_a + "key=" + app.config['OPENCS_APP']['mch_key'], encoding='utf-8')).hexdigest().upper()


def place_db_order(member_info, price):
    """
    立即下单
    数据库新增订单
    :param member_info: 下单会员
    :param price: 订单需付款
    :return:
    """
    order = ThankOrder()
    order.member_id = member_info.id
    order.openid = member_info.openid
    order.price = price
    order.updated_time = order.created_time = Helper.getCurrentDate()
    db.session.add(order)
    db.session.commit()
    return order


# TODO:前端控制下单频率
def place_wx_prepay_order(openid, order, resp):
    """
    立即下单
    调微信后台下支付单
    :param openid:小程序用户openid
    :param order: 订单
    :param resp:响应体
    :return:无
    """

    import requests
    from common.libs.UrlManager import UrlManager
    url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    data = {
        "appid": app.config['OPENCS_APP']['appid'],
        "mch_id": app.config['OPENCS_APP']['mch_id'],
        "nonce_str": genRandomStr(16),
        "sign_type": "HMAC-SHA256",
        "body": "闪寻-充值",
        "out_trade_no": order.id,  # 数据库订单id
        "total_fee": order.price,  # TODO:订单价格
        "spbill_create_ip": app.config['IP'],
        "time_expire": time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time()+5*60)),  # TODO：订单5分钟内未支付即失效
        "notify_url": UrlManager.buildApiUrl("/thank/order/notify"),  # TODO：微信异步通知支付结果
        "trade_type": "JSAPI",
        "limit_pay": "no_credit",  # 限制支付方式
        "openid": openid
    }
    # 计算签名
    data["sign"] = payment_hmac_sha256_or_md5_sign(data)
    xml_data = trans_dict_to_xml(data)
    wx_resp = requests.post(url, data=xml_data.encode("utf-8"))
    wx_resp.encoding = "utf-8"

    # 处理API响应
    data = trans_xml_to_dict(wx_resp.text)
    if data['return_code'] == "SUCCESS":
        # 下单成功
        order.status = 0
        if data['result_code'] == "SUCCESS":
            resp['msg'] = "微信下单成功"
            data = {
                "appId": app.config['OPENCS_APP']['appid'],
                "timeStamp": int(time.time()),
                "nonceStr": genRandomStr(16),
                "package": "prepay_id=" + data['prepay_id'],
                "signType": "HMAC-SHA256",
            }
            data['paySign'] = payment_hmac_sha256_or_md5_sign(data)
            data.pop("appId")
            resp['data'] = data
            resp['code'] = 200
        else:
            resp['msg'] = "微信下单失败, 错误信息" + data['return_msg']
    else:
        resp['msg'] = "微信下单失败, 错误信息" + data['return_msg']


# TODO：表增加字段来支持复杂的订单状态
def paid(data):
    """
    已付款订单
    更新数据库订单状态（防重）
    :param data:
    :return:无
    """
    if 'out_trade_no' in data and 'openid' in data and 'transaction_id' in data and 'time_end' in data:
        order = ThankOrder.query.filter(id=data['out_trade_no'], openid=data['openid']).with_for_update().first()
        if order.status == 0:
            order.transaction_id = data['transaction_id']
            order.paid_time = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(data['time_end'], "%Y%m%d%H%M%S"))
            order.updated_time = Helper.getCurrentDate()
            order.status = 1
            db.session.commit()


def verify_sign(data, sign_type):
    """
    验证微信返回数据签名正确
    :param data: 微信响应体
    :param sign_type: 签名哈希
    :return: 签名是否正确 boolean
    """
    return data.pop("sign") == payment_hmac_sha256_or_md5_sign(data, sign_type=sign_type)


def query_payment_result(order_id):
    """
    调用微信查询订单接口
    :param order_id: 订单号
    :return: 调用微信接口是否成功, 微信后台的支付订单状态
    """
    # 调用微信查询订单接口
    import requests
    url = "https://api.mch.weixin.qq.com/pay/orderquery"
    data = {
        "appid": app.config['OPENCS_APP']['appid'],
        "mch_id": app.config['OPENCS_APP']['mch_key'],
        "out_trade_no": order_id,
        "nonce_str": genRandomStr(16),
        "sign_type": "HMAC-SHA256"
    }
    data['sign'] = payment_hmac_sha256_or_md5_sign(data)
    xml_data = trans_dict_to_xml(data)
    wx_resp = requests.post(url, data=xml_data.encode("utf-8"))
    wx_resp.encoding = "utf-8"
    resp = trans_xml_to_dict(wx_resp.text)

    # API调用失败
    # API调用成功,已付款
    # API调用成功,其他
    if resp['return_code'] == "FAIL":
        return False, "unknown"
    else:
        if resp['trade_state'] == "SUCCESS":
            paid(resp)
        return True, resp['trade_state']


def genRandomStr(num):
    import random
    import string
    """
    :param num: 字符数
    :return: 生成的随机字符串
    """
    return ''.join(random.sample(string.ascii_letters + string.digits, num))


def trans_dict_to_xml(data):
    """
    拼接格式化字符串, 将字典转成XML
    :return:
    """
    xml = []
    for k in sorted(data.keys()):
        v = data.get(k)
        if type(v) == dict:
            # CDATA标签说明数据不被xml解析器解析
            v = "![CDATA[{}]]".format(v)
        xml.append("<{key}>{value}</{key}>".format(key=k, value=v))
    return "<xml>{}</xml>".format("".join(xml))


def trans_xml_to_dict(xml):
    """
    利用bs4解析, 将xml转为字典
    :return:
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(xml, features='lxml-xml')
    xml = soup.find('xml')
    if not xml:
        return {}
    # find_all() 迭代字典 => tuple组成的list => dict
    return dict([(item.name, item.text) for item in xml.find_all()])

def verify_total_fee(order_id, total_fee):
    order = ThankOrder.query.filter(id=order_id).first()
    return order.price == total_fee
