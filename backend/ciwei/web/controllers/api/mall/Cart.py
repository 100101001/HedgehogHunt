import json

from flask import jsonify, request, g

from common.libs.mall.CartService import CartService
from common.libs.Helper import selectFilterObj, getDictFilterField
from common.libs.UrlManager import UrlManager
from common.models.ciwei.mall.Cart import Cart
from common.models.ciwei.mall.Product import Product
from web.controllers.api import route_api


@route_api.route("/cart/index")
def cartIndex():
    """
    会员购物车内所有物品，组合返回
    :return:
    """
    resp = {'code': 200, 'msg': '添加购物车成功~', 'data': {}}
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "获取失败，伪登录~~"
        return jsonify(resp)

    cart_product_list = Cart.query.filter_by(member_id=member_info.id).all()
    data_cart_list = []
    if cart_product_list:
        # 购物车记录了product_id,生成 id->product的映射
        product_ids = selectFilterObj(cart_product_list, "product_id")
        product_map = getDictFilterField(Product, Product.id, "id", product_ids)
        # 组合数据返回
        for item in cart_product_list:
            tmp_product_info = product_map[item.product_id]
            tmp_data = {
                "id": item.id,
                "number": item.product_num,
                "product_id": item.product_id,
                "name": tmp_product_info.name,
                "price": str(tmp_product_info.price),
                "pic_url": UrlManager.buildImageUrl(tmp_product_info.main_image, image_type='PRODUCT'),
                "active": True
            }
            data_cart_list.append(tmp_data)

    resp['data']['list'] = data_cart_list
    return jsonify(resp)


@route_api.route("/cart/set", methods=["POST"])
def setCart():
    """
    向购物车添加 / 更新数量
    :return:
    """
    resp = {'code': 200, 'msg': '添加购物车成功~', 'data': {}}
    req = request.values
    product_id = int(req['id']) if 'id' in req else 0
    number = int(req['number']) if 'number' in req else 0
    if product_id < 1 or number < 1:
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-1~~"
        return jsonify(resp)

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-2~~"
        return jsonify(resp)

    product_info = Product.query.filter_by(id=product_id).first()
    if not product_info:
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-3~~"
        return jsonify(resp)

    if product_info.stock_cnt < number:
        resp['code'] = -1
        resp['msg'] = "添加购物车失败,库存不足~~"
        return jsonify(resp)

    ret = CartService.setItems(member_id=member_info.id, product_id=product_info.id, number=number)
    if not ret:
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-4~~"
        return jsonify(resp)
    return jsonify(resp)


@route_api.route("/cart/del", methods=["POST"])
def delCart():
    """
    删除购物车中一条记录
    :return:
    """
    resp = {'code': 200, 'msg': '添加购物车成功~', 'data': {}}
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None

    items = []
    if params_goods:
        items = json.loads(params_goods)
    if not items or len(items) < 1:
        return jsonify(resp)

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "删除购物车失败-1~~"
        return jsonify(resp)

    ret = CartService.deleteItem(member_id=member_info.id, items=items)
    if not ret:
        resp['code'] = -1
        resp['msg'] = "删除购物车失败-2~~"
        return jsonify(resp)
    return jsonify(resp)
