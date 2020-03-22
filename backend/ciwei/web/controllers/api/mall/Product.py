# -*- coding: utf-8 -*-
from flask import request, g
from sqlalchemy import or_, desc, func, distinct

from application import db
from common.libs.Helper import getDictFilterField, selectFilterObj
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Member import Member
from common.models.ciwei.mall.Campus import Campus
from common.models.ciwei.mall.CampusProduct import CampusProduct
from common.models.ciwei.mall.ProductComments import ProductComments
from common.models.ciwei.mall.Cart import Cart
from common.models.ciwei.mall.Product import Product
from common.models.ciwei.mall.ProductCat import ProductCat
from web.controllers.api import route_api, jsonify


@route_api.route("/campus/search", methods=['GET'])
def product_campus():
    resp = {'code': -1, 'msg': "成功", 'data': {}}
    req = request.values

    campus = req['school'] if 'school' in req and req['school'] else ''

    p = int(req['p']) if ('p' in req and req['p']) else 1
    if p < 1:
        p = 1
    page_size = 10
    offset = (p - 1) * page_size
    if campus:
        query = Campus.query.filter(Campus.name.ilike('%{}%'.format(campus))).offset(offset)
    else:
        query = Campus.query.offset(offset)

    campus_list = query.limit(page_size).all()

    unis = []
    for item in campus_list:
        tmp_data = {
            'id': item.name,
            'url': UrlManager.buildImageUrl(item.main_image, image_type='UNIS'),
            'option': item.id
        }
        unis.append(tmp_data)

    resp['code'] = 200
    resp['data']['unis'] = unis
    resp['data']['has_more'] = query.count() > page_size
    return jsonify(resp)


@route_api.route("/product/index")
def productIndex():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    campus = int(req['campus']) if 'campus' in req else -1

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
    if campus != -1:
        product_ids = db.session.query(CampusProduct.product_id).filter_by(campus_id=campus).all()
        product_id_list = db.session.query(Product.common_id, (func.sum(Product.sale_cnt)).label('total_sale')) \
            .group_by(Product.common_id).filter(Product.common_id.in_(product_ids), Product.status == 1) \
            .order_by(desc('total_sale'), Product.common_id.desc()).limit(3).all()
    else:
        # 计算所有相同id的销量
        product_id_list = db.session.query(Product.common_id, (func.sum(Product.sale_cnt)).label('total_sale')) \
            .group_by(Product.common_id).filter(Product.status == 1) \
            .order_by(desc('total_sale'), Product.common_id.desc()).limit(3).all()

    product_list = []
    for product_id in product_id_list:
        product_list.append(Product.query.filter_by(common_id=product_id[0]).order_by(Product.price).first())

    data_product_list = []
    if product_list:
        for item in product_list:
            tmp_data = {
                'id': item.common_id,
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
    campus = int(req['campus']) if 'campus' in req else -1
    p = int(req['p']) if 'p' in req else 1

    if p < 1:
        p = 1

    page_size = 10
    offset = (p - 1) * page_size

    if campus != -1:
        product_ids = db.session.query(CampusProduct.product_id).filter_by(campus_id=campus).all()
        # 计算某个大学的产品中所有相同id的销量
        product_list = db.session.query(Product.common_id, (func.sum(Product.sale_cnt)).label('total_sale')) \
            .group_by(Product.common_id).filter(Product.status == 1, Product.common_id.in_(product_ids)) \
            .order_by(desc('total_sale'), Product.common_id.desc()).all()
        common_id_list = [item[0] for item in product_list]
    else:
        # 计算所有相同id的销量
        product_list = db.session.query(Product.common_id, (func.sum(Product.sale_cnt)).label('total_sale')) \
            .group_by(Product.common_id).filter(Product.status == 1) \
            .order_by(desc('total_sale'), Product.common_id.desc()).all()
        common_id_list = [item[0] for item in product_list]

    query = db.session.query(distinct(Product.common_id)).filter(Product.common_id.in_(common_id_list))
    if cat_id > 0:
        query = query.filter_by(cat_id=cat_id)

    if mix_kw:
        rule = or_(Product.name.ilike("%{0}%".format(mix_kw)), Product.tags.ilike("%{0}%".format(mix_kw)))
        query = query.filter(rule)

    common_id_list = query.offset(offset).limit(page_size).all()

    # if campus != -1:
    #     product_ids = db.session.query(CampusProduct.product_id).filter_by(campus_id=campus).all()
    #     query = query.filter(Product.id.in_(product_ids))
    #
    # product_list = query.order_by(Product.sale_cnt.desc(), Product.id.desc()) \
    #     .offset(offset).limit(page_size).all()
    # 全部

    product_list = []
    for common_id in common_id_list:
        product_list.append(Product.query.filter_by(common_id=common_id[0]).order_by(Product.price).first())

    data_product_list = []
    if product_list:
        for item in product_list:
            tmp_data = {
                'id': item.common_id,
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
    # 按option_id排序,返回前端的数组索引==option_id
    product_infos = Product.query.filter_by(common_id=product_id).order_by(Product.option_id).all()
    comment_cnt = db.session.query(func.sum(Product.comment_cnt)).filter_by(common_id=product_id).scalar()
    sale_cnt = db.session.query(func.sum(Product.sale_cnt)).filter_by(common_id=product_id).scalar()
    if not product_infos[0] or not product_infos[0].status:
        resp['code'] = -1
        resp['msg'] = "周边已下架"
        return jsonify(resp)

    member_info = g.member_info
    cart_number = 0
    not_in_cart = []
    if member_info:
        cart_number = Cart.query.filter_by(member_id=member_info.id).count()
        # 购物车没有的所有规格的该款商品的id
        model_in_cart = db.session.query(Cart.product_id).filter(Cart.member_id == member_info.id, Cart.product_id.in_(
            [item.id for item in product_infos])).all()
        not_in_cart = [item.id for item in product_infos if (item.id,) not in model_in_cart]

    resp['data']['info'] = []
    for product_info in product_infos:
        resp['data']['info'].append({
            "id": product_info.id,  # 加入购物车用
            "name": product_info.name,
            "summary": product_info.description,
            "total_count": str(sale_cnt),
            "comment_count": str(comment_cnt),
            'main_image': UrlManager.buildImageUrl(product_info.main_image, image_type='PRODUCT'),
            "price": str(product_info.price),
            "stock": product_info.stock_cnt,
            "pics": [UrlManager.buildImageUrl(product_info.main_image, image_type='PRODUCT')],
            "option_desc": product_info.option_desc
        })
    resp['data']['cart_number'] = cart_number
    resp['data']['not_in_cart'] = not_in_cart  # 前端可知列表中哪一项不在购物车里
    return jsonify(resp)


@route_api.route("/product/comments")
def productComments():
    """

    :return:
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values

    # 找到所有用户评论,组合返回
    common_id = int(req['id']) if 'id' in req else 0
    product_ids = db.session.query(Product.id).filter_by(common_id=common_id).all()
    # *将数组展开
    rule = or_(*[ProductComments.product_ids.ilike("%_{0}_%".format(product_id[0])) for product_id in product_ids])
    query = ProductComments.query.filter(rule)

    comment_list = query.order_by(ProductComments.id.desc()).limit(5).all()
    data_list = []
    if comment_list:
        f = selectFilterObj(comment_list, "member_id")
        member_map = getDictFilterField(Member, Member.id, "id", f)
        for item in comment_list:
            if item.member_id not in member_map:
                continue
            tmp_member_info = member_map[item.member_id]
            tmp_data = {
                'id': item.id,
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


@route_api.route('/product/qrcode/info', methods=['GET', 'POST'])
def productQrcodeInfo():
    return jsonify({
        'code': 200,
        'msg': '',
        'data': {
            'id': 15,
            'price': 0.01
        }
    })
