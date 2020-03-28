import decimal
import json

from flask import request, jsonify, g

from application import db, app
from common.libs.Helper import getCurrentDate
from common.libs.MemberService import MemberService
from common.libs.mall.WechatService import WeChatService
from common.libs.mall.CartService import CartService
from common.libs.UrlManager import UrlManager
from common.libs.mall.PayService import PayService
from common.models.ciwei.mall.Address import Address
from common.models.ciwei.mall.Order import Order
from common.models.ciwei.mall.Product import Product
from web.controllers.api import route_api


@route_api.route("/order/express/status/set", methods=['POST', 'GET'])
def setOrderStatus():
    resp = {'code': 200, 'msg': '', 'data': {}}
    req = request.values
    status = req['status'] if 'status' in req else None
    if status is None:
        resp['code'] = -1
        resp['msg'] = "操作失败，请重试"
        return jsonify(resp)
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    if not order_sn:
        resp['code'] = -1
        resp['msg'] = "操作失败，请重试"
        return jsonify(resp)

    order = Order.query.filter_by(order_sn=order_sn).first()
    if not order:
        resp['code'] = -1
        resp['msg'] = "操作失败，请重试"
        return jsonify(resp)
    order.express_status = status
    db.session.add(order)
    db.session.commit()
    return jsonify(resp)


@route_api.route("/order/info", methods=["POST"])
def orderInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None
    member_info = g.member_info
    params_goods_list = []
    if params_goods:
        params_goods_list = json.loads(params_goods)

    product_dic = {}
    for item in params_goods_list:
        product_dic[item['id']] = item['number']

    product_ids = product_dic.keys()
    product_list = Product.query.filter(Product.id.in_(product_ids)).all()
    data_product_list = []
    yun_price = pay_price = decimal.Decimal(0.00)
    if product_list:
        for item in product_list:
            tmp_data = {
                "id": item.id,
                "name": item.name,
                "price": str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image, image_type='PRODUCT'),
                'number': product_dic[item.id]
            }
            pay_price = pay_price + item.price * int(product_dic[item.id])
            data_product_list.append(tmp_data)

    # 获取地址
    address_info = Address.query.filter_by(is_default=1, member_id=member_info.id, status=1).first()
    default_address = ''
    if address_info:
        default_address = {
            "id": address_info.id,
            "name": address_info.nickname,
            "mobile": address_info.mobile,
            "address": "%s%s%s%s" % (
                address_info.province_str, address_info.city_str, address_info.area_str, address_info.address)
        }

    resp['data']['goods_list'] = data_product_list
    resp['data']['pay_price'] = str(pay_price)
    resp['data']['yun_price'] = str(yun_price)
    resp['data']['total_price'] = str(pay_price + yun_price)
    resp['data']['default_address'] = default_address
    return jsonify(resp)


@route_api.route("/order/create", methods=["POST"])
def orderCreate():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    src_type = req['type'] if 'type' in req else ''
    note = req['note'] if 'note' in req else ''
    express_address_id = int(req['express_address_id']) if 'express_address_id' in req and req[
        'express_address_id'] else 0
    params_goods = req['goods'] if 'goods' in req else None
    discount_price = req['discount_price'] if 'discount_price' in req else 0
    discount_type = req['discount_type'] if 'discount_type' in req else "帐户余额"

    items = []
    if params_goods:
        items = json.loads(params_goods)

    if len(items) < 1:
        resp['code'] = -1
        resp['msg'] = "下单失败：没有选择商品~~"
        return jsonify(resp)

    address_info = Address.query.filter_by(id=express_address_id).first()
    if not address_info or not address_info.status:
        resp['code'] = -1
        resp['msg'] = "下单失败：快递地址不对~~"
        return jsonify(resp)

    member_info = g.member_info
    target = PayService()
    params = {
        "note": note,
        'express_address_id': address_info.id,
        'express_info': {
            'mobile': address_info.mobile,
            'nickname': address_info.nickname,
            "address": "%s%s%s%s" % (
                address_info.province_str, address_info.city_str, address_info.area_str, address_info.address)
        },
        "discount_price": discount_price,
        "discount_type": discount_type
    }
    resp = target.createOrder(member_info.id, items, params)
    # 如果是来源购物车的，下单成功将下单的商品去掉
    if resp['code'] == 200 and src_type == "cart":
        CartService.deleteItem(member_info.id, items)
    return jsonify(resp)


@route_api.route("/order/ops", methods=["POST"])
def orderOps():
    """
    关闭订单的数据库操作：更新库存,订单状态,日志
    确认订单的数据库操作:更新物流状态
    :return:
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    member_info = g.member_info
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    act = req['act'] if 'act' in req else ''
    order_info = Order.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
    if not order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙。请稍后再试~~"
        return jsonify(resp)

    if act == "cancel":
        target_pay = PayService()
        ret = target_pay.closeOrder(pay_order_id=order_info.id)
        if not ret:
            resp['code'] = -1
            resp['msg'] = "系统繁忙。请稍后再试~~"
            return jsonify(resp)
    elif act == "confirm":
        order_info.express_status = 1
        order_info.updated_time = getCurrentDate()
        db.session.add(order_info)
        db.session.commit()

    return jsonify(resp)


@route_api.route("/order/pay", methods=["POST"])
def orderPay():
    """
    wx下单
    :return:
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    req = request.values
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    order_info = Order.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
    if not order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙。请稍后再试~~"
        return jsonify(resp)

    app_config = app.config['OPENCS_APP']
    notify_url = app.config['APP']['domain'] + '/api/order/callback'

    target_wechat = WeChatService(merchant_key=app_config['mch_key'])

    data = {
        'appid': app_config['appid'],
        'mch_id': app_config['mch_id'],
        'nonce_str': target_wechat.get_nonce_str(),
        'body': '闪寻周边',  # 商品描述
        'out_trade_no': order_info.order_sn,  # 商户订单号
        'total_fee': int(order_info.total_price * 100),
        'notify_url': notify_url,
        'trade_type': "JSAPI",
        'openid': member_info.openid
    }
    app.logger.info(data)
    pay_info = target_wechat.get_pay_info(pay_data=data)

    # 保存prepay_id为了后面发模板消息
    order_info.prepay_id = pay_info['prepay_id']
    db.session.add(order_info)
    db.session.commit()

    resp['data']['pay_info'] = pay_info
    return jsonify(resp)


@route_api.route("/order/callback", methods=["POST"])
def orderCallback():
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
    pay_order_info = Order.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if int(pay_order_info.total_price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    # 更新订单的支付/物流状态, 记录日志
    if pay_order_info.status == 1:
        return target_wechat.dict_to_xml(result_data), header

    target_pay = PayService()
    target_pay.orderSuccess(pay_order_id=pay_order_info.id, params={"pay_sn": callback_data['transaction_id']})
    target_pay.addPayCallbackData(pay_order_id=pay_order_info.id, data=request.data)
    return target_wechat.dict_to_xml(result_data), header
