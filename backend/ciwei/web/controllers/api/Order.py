from flask import g, request
from application import db
from common.libs import Helper, OrderService
from web.controllers.api import route_api, jsonify


# TODO：下订单和支付是一体的
@route_api.route("/order/prepay", methods=['GET', 'POST'])
def place_payment_order():
    """
    https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=9_1&index=1
    新增支付订单
    调用微信支付统一下单API获取
    :return: 小程序调支付API的五个参数
    """
    req = request.values
    resp = {"data": {}, "msg": "", "code": -1}

    # 检查登陆
    # 检查参数: 支付金额price
    member_info = g.member_info
    if not member_info:
        resp["msg"] = "未登录"
        return resp
    price = req['price']
    if not price:
        resp['msg'] = "无金额"
        return resp

    openid = member_info.openid
    # 新增订单
    order_id = OrderService.placeOrder(member_info, price)

    # 调用微信支付的统一下单接口, 获取prepay_id, 签名返回前端
    OrderService.prepay(openid, order_id, price, resp)
    return resp


# TODO:获取微信推送支付结果, 更新订单状态
# TODO:return_code 是否指小程序支付API请求发送成功/失败
@route_api.route("/order/notify", methods=['GET', 'POST'])
def notify_payment_result():
    """
    https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=9_7
    获取微信推送支付结果, 更新订单状态
    更新条件条件
    1.签名正确
    2.订单支付结果,及必要更新信息:订单号,交易号,交易完成时间,交易用户完整给出
    3.订单状态未支付
    :return: 通知微信接收到正确的通知了
    """
    req = request.json()
    resp = {"return_code": "FAIL"}
    # 验证签名
    if not OrderService.verify_sign(req, req['sign_type'] if 'sign_type' in req else "MD5"):
        resp['return_msg'] = "签名失败"
    else:
        # 接受了通知且签名校验成功(不管通知的return_code)
        resp['return_code'] = "SUCCESS"
        # 小程序API调用成功
        if req['return_code'] == "SUCCESS" and req['result_code'] == "SUCCESS":
            # 更新订单状态为已支付
            OrderService.paid(req)
    return resp


@route_api.route("/order/query", methods=['GET', 'POST'])
def query_payment_result():
    """
    https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=9_2
    确认支付
    到微信后台查询订单状态
    :return: 是否已支付
    """

    # 检验登陆
    # 检验参数：订单号order_id
    resp = {"data": {}, "msg": "", "code": -1}
    req = request.values
    if not g.member_info:
        resp['msg'] = "未登录"
        return resp
    if 'order_id' not in req:
        resp['msg'] = "缺订单号"
        return resp

    # 订单不存在
    # 订单已支付,直接返回状态
    # 查询微信后台状态
    from common.models.ciwei.Order import Order
    order = Order.query.filter_by(id=req['order_id']).first()
    if order is None:
        resp['msg'] = "无效订单号"
    elif order.status == 0:
        resp['code'] = 200
        resp['data'] = {"trade_state": "SUCCESS"}
    else:
        got_result, trade_state = OrderService.query_payment_result()
        if got_result:
            resp['code'] = 200
            resp['data'] = {"trade_state": trade_state}
        else:
            # TODO:前端看到的应该是旧的状态
            resp['msg'] = "微信服务器繁忙"
    return resp


# # 测试数据库更新
# @route_api.route("/testdb", methods=['GET', 'POST'])
# def testdb():
#     from common.models.ciwei.Member import Member
#     from common.models.ciwei.Goods import Good
#     member = Member.query.filter_by().with_for_update().first()
#     member.updated_time = Helper.getCurrentDate()
#     goods = Good.query.filter_by().with_for_update().first()
#     goods.updated_time = Helper.getCurrentDate()
#     member2 = Member()
#     member2.openid = 1
#     db.session.add(member2)
#     db.session.commit()
#     return jsonify({})
