import datetime
import json
import os
import time

from flask import g, request, jsonify

from common.libs.Helper import selectFilterObj, getDictFilterField, seconds2str
from common.libs.UrlManager import UrlManager
from common.libs.mall.PayService import PayService
from common.models.ciwei.mall.Order import Order
from common.models.ciwei.mall.OrderProduct import OrderProduct
from common.models.ciwei.mall.Product import Product
from common.models.ciwei.mall.ProductComments import ProductComments
from web.controllers.api import route_api


@route_api.route("/my/order")
def myOrderList():
    """
    :return: 某状态的订单(加上产品列表数据)列表
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    req = request.values
    status = int(req['status']) if 'status' in req else 0

    # 状态过滤
    query = Order.query.filter_by(member_id=member_info.id)
    if status == -8:  # 等待付款
        query = query.filter(Order.status == -8, Order.updated_time > seconds2str(time.time() - 1800))
        PayService().autoCloseOrder(member_id=member_info.id)
    elif status == -7:  # 待发货
        query = query.filter(Order.status == 1, Order.express_status == -7, Order.comment_status == 0)
    elif status == -6:  # 待确认
        query = query.filter(Order.status == 1, Order.express_status == -6, Order.comment_status == 0)
    elif status == -5:  # 待评价
        query = query.filter(Order.status == 1, Order.express_status == 1, Order.comment_status == 0)
    elif status == 1:  # 已完成
        query = query.filter(Order.status == 1, Order.express_status == 1, Order.comment_status == 1)
    else:
        query = query.filter(Order.status == 0)

    # 获取每个订单的产品列表信息
    order_list = query.order_by(Order.id.desc()).all()
    data_order_list = []
    if order_list:
        order_ids = selectFilterObj(order_list, "id")
        order_item_list = OrderProduct.query.filter(OrderProduct.order_id.in_(order_ids)).all()
        product_ids = selectFilterObj(order_item_list, "product_id")
        product_map = getDictFilterField(Product, Product.id, "id", product_ids)
        order_item_map = {}
        if order_item_list:
            for item in order_item_list:
                if item.order_id not in order_item_map:
                    order_item_map[item.order_id] = []

                tmp_product_info = product_map[item.product_id]
                order_item_map[item.order_id].append({
                    'id': item.id,
                    'food_id': item.product_id,
                    'quantity': item.product_num,
                    'price': str(item.price),
                    'pic_url': UrlManager.buildImageUrl(tmp_product_info.main_image, image_type='PRODUCT'),
                    'name': tmp_product_info.name
                })

        for item in order_list:
            tmp_data = {
                'status': item.pay_status,
                'status_desc': item.status_desc,
                'date': item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                'order_number': item.order_number,
                'order_sn': item.order_sn,
                'note': item.note,
                'total_price': str(item.total_price),
                'goods_list': order_item_map[item.id]
            }

            data_order_list.append(tmp_data)
    resp['data']['pay_order_list'] = data_order_list
    return jsonify(resp)


@route_api.route("/my/order/info")
def myOrderInfo():
    """
    :return: 单个订单(加产品列表)的详细信息
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    req = request.values
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    pay_order_info = Order.query.filter_by(member_id=member_info.id, order_sn=order_sn).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"
        return jsonify(resp)

    express_info = {}
    if pay_order_info.express_info:
        express_info = json.loads(pay_order_info.express_info)

    tmp_deadline = pay_order_info.created_time + datetime.timedelta(minutes=30)
    info = {
        "order_sn": pay_order_info.order_sn,
        "status": pay_order_info.pay_status,
        "status_desc": pay_order_info.status_desc,
        "pay_price": str(pay_order_info.pay_price),
        "yun_price": str(pay_order_info.yun_price),
        "total_price": str(pay_order_info.total_price),
        "address": express_info,
        "goods": [],
        "deadline": tmp_deadline.strftime("%Y-%m-%d %H:%M")
    }

    order_items = OrderProduct.query.filter_by(order_id=pay_order_info.id).all()
    if order_items:
        product_ids = selectFilterObj(order_items, "product_id")
        product_map = getDictFilterField(Product, Product.id, "id", product_ids)
        for item in order_items:
            tmp_product_info = product_map[item.product_id]
            tmp_data = {
                "name": tmp_product_info.name,
                "price": str(item.price),
                "unit": item.product_num,
                "pic_url": UrlManager.buildImageUrl(tmp_product_info.main_image, image_type='PRODUCT'),
            }
            info['goods'].append(tmp_data)
    resp['data']['info'] = info
    return jsonify(resp)


@route_api.route("/my/comment/list")
def myCommentList():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    comment_list = ProductComments.query.filter_by(member_id=member_info.id) \
        .order_by(ProductComments.id.desc()).all()
    data_comment_list = []
    if comment_list:
        order_ids = selectFilterObj(comment_list, "order_id")
        order_map = getDictFilterField(Order, Order.id, "id", order_ids)
        for item in comment_list:
            tmp_order_info = order_map[item.order_id]
            tmp_data = {
                "date": item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "content": item.content,
                "order_number": tmp_order_info.order_number
            }
            data_comment_list.append(tmp_data)
    resp['data']['list'] = data_comment_list
    return jsonify(resp)
