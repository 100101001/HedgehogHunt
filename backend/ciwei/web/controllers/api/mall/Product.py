# -*- coding: utf-8 -*-
from flask import request, g
from sqlalchemy import or_

from common.libs.Helper import getDictFilterField, selectFilterObj
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Member import Member
from common.models.ciwei.mall.ProductComments import ProductComment
from common.models.ciwei.mall.Cart import Cart
from common.models.ciwei.mall.Product import Product
from common.models.ciwei.mall.ProductCat import ProductCat
from web.controllers.api import route_api, jsonify


# @route_api.route("/product/campus", methods=['GET'])
# def product_campus():
#     resp = {'code': -1, 'msg': "获取周边列表成功", 'data': {}}
#     req = request.values
#
#     campus_id = int(req['campus']) if 'campus' in req and req['campus'] else -1
#     p = int(req['p']) if ('p' in req and req['p']) else 1
#     if p < 1:
#         p = 1
#     page_size = 10
#     offset = (p - 1) * page_size
#     product_ids = db.session.query(CampusProduct.id).filter_by(campus_id=campus_id) \
#         .offset(offset).limit(page_size).all()
#
#     products = []
#     for item in product_ids:
#         product = Product.query.filter_by(id=item.id).first()
#         tmp_data = {
#             'id': product.id,
#             'name': product.name,
#             'price': float(product.price),
#             'stock_cnt': product.stock,
#             'sold_cnt': product.sale_cnt
#         }
#         products.append(tmp_data)
#
#     resp['code'] = 200
#     resp['data']['productList'] = products
#     return jsonify(resp)


@route_api.route("/product/index")
def productIndex():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}

    # 类别
    cat_list = ProductCat.query.filter_by(status=1).order_by(ProductCat.weight.desc()).all()
    data_cat_list = [{
        'id': 0,
        'name': "全部"
    }]
    if cat_list:
        for item in cat_list:
            tmp_data = {
                'id': item.id,
                'name': item.name
            }
            data_cat_list.append(tmp_data)
    resp['data']['cat_list'] = data_cat_list

    # 销量冠军轮播图
    product_list = Product.query.filter_by(status=1) \
        .order_by(Product.sale_cnt.desc(), Product.id.desc()).limit(3).all()

    data_product_list = []
    if product_list:
        for item in product_list:
            tmp_data = {
                'id': item.id,
                'pic_url': UrlManager.buildImageUrl(item.main_image, image_type='PRODUCT')
            }
            data_product_list.append(tmp_data)

    resp['data']['banner_list'] = data_product_list
    return jsonify(resp)


@route_api.route("/product/search")
def productSearch():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
    p = int(req['p']) if 'p' in req else 1

    if p < 1:
        p = 1

    page_size = 10
    offset = (p - 1) * page_size
    query = Product.query.filter_by(status=1)
    if cat_id > 0:
        query = query.filter_by(cat_id=cat_id)

    if mix_kw:
        rule = or_(Product.name.ilike("%{0}%".format(mix_kw)), Product.tags.ilike("%{0}%".format(mix_kw)))
        query = query.filter(rule)

    product_list = query.order_by(Product.sale_cnt.desc(), Product.id.desc()) \
        .offset(offset).limit(page_size).all()

    data_product_list = []
    if product_list:
        for item in product_list:
            tmp_data = {
                'id': item.id,
                'name': "%s" % item.name,
                'price': str(item.price),
                'min_price': str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image, image_type='PRODUCT')
            }
            data_product_list.append(tmp_data)
    resp['data']['list'] = data_product_list
    resp['data']['has_more'] = 0 if len(data_product_list) < page_size else 1
    return jsonify(resp)


@route_api.route("/product/info")
def productInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    product_id = int(req['id']) if 'id' in req else 0
    product_info = Product.query.filter_by(id=product_id).first()
    if not product_info or not product_info.status:
        resp['code'] = -1
        resp['msg'] = "周边已下架"
        return jsonify(resp)

    member_info = g.member_info
    cart_number = 0
    if member_info:
        cart_number = Cart.query.filter_by(member_id=member_info.id).count()
    resp['data']['info'] = {
        "id": product_info.id,
        "name": product_info.name,
        "summary": product_info.description,
        "total_count": product_info.sale_cnt,
        "comment_count": product_info.comment_cnt,
        'main_image': UrlManager.buildImageUrl(product_info.main_image, image_type='PRODUCT'),
        "price": str(product_info.price),
        "stock": product_info.stock_cnt,
        "pics": [UrlManager.buildImageUrl(product_info.main_image, image_type='PRODUCT')]
    }
    resp['data']['cart_number'] = cart_number
    return jsonify(resp)


@route_api.route("/product/comments")
def productComments():
    """

    :return:
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values

    # 找到所有用户评论,组合返回
    product_id = int(req['id']) if 'id' in req else 0
    query = ProductComment.query.filter(ProductComment.product_ids.ilike("%_{0}_%".format(product_id)))
    comment_list = query.order_by(ProductComment.id.desc()).limit(5).all()
    data_list = []
    if comment_list:
        f = selectFilterObj(comment_list, "member_id")
        member_map = getDictFilterField(Member, Member.id, "id", f)
        for item in comment_list:
            if item.member_id not in member_map:
                continue
            tmp_member_info = member_map[item.member_id]
            tmp_data = {
                'score': item.score,
                'date': item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "content": item.content,
                "user": {
                    'nickname': tmp_member_info.nickname,
                    'avatar_url': tmp_member_info.avatar,
                }
            }
            data_list.append(tmp_data)
    resp['data']['list'] = data_list
    resp['data']['count'] = query.count()
    return jsonify(resp)