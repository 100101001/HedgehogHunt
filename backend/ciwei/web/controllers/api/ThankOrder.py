import datetime
from decimal import Decimal

from flask import g, request

from application import db, app
from common.libs import ThankOrderService
from common.libs.mall.PayService import PayService
from common.libs.mall.WechatService import WeChatService
from common.models.ciwei.ThankOrder import ThankOrder
from web.controllers.api import route_api, jsonify


@route_api.route("/thank/order", methods=['POST', 'GET'])
def createThankOrder():
    resp = {'code': 200, 'msg': 'success', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)
    price = Decimal(req.get('price', '0')).quantize(Decimal('0.00'))
    if not price:
        resp['msg'] = "支付失败"
        return jsonify(resp)

    # 数据库下单
    wechat_service = WeChatService(merchant_key=app.config['OPENCS_APP']['mch_key'])
    pay_service = PayService()
    model_order = ThankOrder()
    model_order.order_sn = pay_service.geneThankOrderSn()
    model_order.openid = member_info.openid
    model_order.member_id = member_info.id
    model_order.price = price

    order_sn = model_order.order_sn
    # 微信下单
    pay_data = {
        'appid': app.config['OPENCS_APP']['appid'],
        'mch_id': app.config['OPENCS_APP']['mch_id'],
        'nonce_str': wechat_service.get_nonce_str(),
        'body': '闪寻-答谢',
        'out_trade_no': order_sn,
        'total_fee': int(model_order.price * 100),
        'notify_url': app.config['APP']['domain'] + "/api/thank/order/notify",
        'time_expire': (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y%m%d%H%M%S"),
        'trade_type': 'JSAPI',
        'openid': member_info.openid
    }
    pay_sign_data = wechat_service.get_pay_info(pay_data=pay_data)
    if not pay_sign_data:
        resp['msg'] = "微信服务器繁忙，请稍后重试"
        return jsonify(resp)
    model_order.status = 0
    db.session.add(model_order)
    db.session.commit()
    resp['code'] = 200
    resp['data'] = pay_sign_data
    resp['data']['thank_order_sn'] = order_sn
    return jsonify(resp)


@route_api.route('/thank/order/notify', methods=['GET', 'POST'])
def thankOrderCallback():
    result_data = {
        'return_code': 'SUCCESS',
        'return_msg': 'OK'
    }
    header = {'Content-Type': 'application/xml'}
    app_config = app.config['OPENCS_APP']
    target_wechat = WeChatService(merchant_key=app_config['mch_key'])
    callback_data = target_wechat.xml_to_dict(request.data)
    app.logger.info(callback_data)

    # 检查签名和订单金额
    sign = callback_data['sign']
    callback_data.pop('sign')
    gene_sign = target_wechat.create_sign(callback_data)
    app.logger.info(gene_sign)
    if sign != gene_sign:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header
    if callback_data['result_code'] != 'SUCCESS':
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    order_sn = callback_data['out_trade_no']
    pay_order_info = ThankOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if int(pay_order_info.price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    # 更新订单的支付状态, 记录日志

    # 订单状态已回调更新过直接返回
    if pay_order_info.status == 1:
        return target_wechat.dict_to_xml(result_data), header
    # 订单状态未回调更新过
    target_pay = PayService()
    target_pay.thankOrderSuccess(pay_order_id=pay_order_info.id, params={"pay_sn": callback_data['transaction_id'],
                                                                         "paid_time": callback_data['time_end']})
    target_pay.addThankPayCallbackData(pay_order_id=pay_order_info.id, data=request.data)
    return target_wechat.dict_to_xml(result_data), header


@route_api.route("/thank/order/query", methods=['GET', 'POST'])
def query_payment_result():
    """
    确认支付
    到微信后台查询订单状态
    :see: https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=9_2
    :return: 是否已支付
    """

    # 检验登陆
    # 检验参数：订单号order_id
    resp = {"data": {}, "msg": "", "code": -1}
    req = request.values
    if not g.member_info:
        resp['msg'] = "未登录"
        return jsonify(resp)
    if 'out_trade_no' not in req:
        resp['msg'] = "缺订单号"
        return jsonify(resp)

    # 订单不存在
    # 微信已通知,直接返回订单状态
    # 查询微信后台状态
    order = ThankOrder.query.filter_by(id=req['order_id']).first()
    if not order:
        resp['msg'] = "无效订单号"
    elif order.wx_payment_result_notified:
        resp['code'] = 200
        resp['data'] = {"trade_state": order.status_desc}
    else:
        got_result, trade_state = ThankOrderService.query_payment_result(order.id)
        if got_result:
            resp['code'] = 200
            resp['data'] = {"trade_state": trade_state}
        else:
            resp['msg'] = "微信服务器繁忙"
    return jsonify(resp)

