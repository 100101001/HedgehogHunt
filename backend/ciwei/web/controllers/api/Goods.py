# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2019/12/10 下午9:06
@file: Goods.py
@desc:
"""
import datetime
from decimal import Decimal

from flask import request, jsonify, g

from application import db, app, APP_CONSTANTS
from common.cahce.core import CacheOpService
from common.cahce.GoodsCasUtil import GoodsCasUtil
from common.libs import GoodsService
from common.libs.Helper import param_getter
from common.libs.MemberService import MemberService
from common.libs.RecordService import RecordHandlers
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.libs.mall.PayService import PayService
from common.libs.mall.WechatService import WeChatService
from common.loggin.time import time_log
from common.models.ciwei.Goods import Good
from common.models.ciwei.GoodsTopOrder import GoodsTopOrder
from common.tasks.subscribe import SubscribeTasks
from web.controllers.api import route_api

TOP_PRICE = APP_CONSTANTS['sp_product']['top']['price']


@route_api.route("/goods/top/order", methods=['POST', 'GET'])
@time_log
def topOrder():
    resp = {'code': -1, 'msg': 'success', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)

    # 数据库下单
    wechat_service = WeChatService(merchant_key=app.config['OPENCS_APP']['mch_key'])
    pay_service = PayService()
    model_order = GoodsTopOrder()
    model_order.order_sn = pay_service.geneGoodsTopOrderSn()
    model_order.openid = member_info.openid
    model_order.member_id = member_info.id
    model_order.price = Decimal(req.get('price', TOP_PRICE)).quantize(Decimal('0.00'))
    top_charge = Decimal(TOP_PRICE).quantize(Decimal('0.00'))
    model_order.balance_discount = top_charge - model_order.price
    # 微信下单
    pay_data = {
        'appid': app.config['OPENCS_APP']['appid'],
        'mch_id': app.config['OPENCS_APP']['mch_id'],
        'nonce_str': wechat_service.get_nonce_str(),
        'body': '鲟回-置顶',
        'out_trade_no': model_order.order_sn,
        'total_fee': int(model_order.price * 100),
        'notify_url': app.config['APP']['domain'] + "/api/goods/top/order/notify",
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
    resp['data'] = pay_sign_data
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/top/order/notify', methods=['GET', 'POST'])
@time_log
def topOrderCallback():
    result_data = {
        'return_code': 'SUCCESS',
        'return_msg': 'OK'
    }
    header = {'Content-Type': 'application/xml'}
    app_config = app.config['OPENCS_APP']
    target_wechat = WeChatService(merchant_key=app_config['mch_key'])
    callback_data = target_wechat.xml_to_dict(request.data)
    app.logger.info(callback_data)

    # 检查签名
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
    # 检查订单金额
    order_sn = callback_data['out_trade_no']
    pay_order_info = GoodsTopOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header
    if int(pay_order_info.price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    # 更新订单的支付/物流状态, 记录日志
    # 订单状态已回调更新过直接返回
    if pay_order_info.status == 1:
        return target_wechat.dict_to_xml(result_data), header
    # 订单状态未回调更新过
    target_pay = PayService()
    target_pay.goodsTopOrderSuccess(pay_order_id=pay_order_info.id, params={"pay_sn": callback_data['transaction_id'],
                                                                            "paid_time": callback_data['time_end']})
    target_pay.addGoodsTopPayCallbackData(pay_order_id=pay_order_info.id, data=request.data)
    return target_wechat.dict_to_xml(result_data), header


@route_api.route("/goods/create", methods=['GET', 'POST'])
@time_log
def createGoods():
    """
    预发帖
    :return: 图片->是否在服务器上 , 前端再次上传真正需要上传的图片
    """
    resp = {'code': -1, 'msg': 'create goods data successfully(goods/add)', 'data': {}}

    # 检查登陆
    # 检查参数: goods_name, business_type
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "没有用户信息，无法发布，请授权登陆！"
        return jsonify(resp)
    business_type = int(req.get('business_type', -1))
    if business_type not in (0, 1, 2):
        resp['msg'] = "发布失败"
        resp['data'] = req
        return jsonify(resp)

    # 是否是扫码归还
    if business_type == 0:
        model_goods = GoodsService.releaseLost(release_info=req, author_info=member_info)
    elif business_type == 1:
        model_goods = GoodsService.releaseFound(release_info=req, author_info=member_info)
    else:
        is_scan_return = 'owner_name' not in req
        model_goods = GoodsService.releaseReturn(release_info=req, author_info=member_info,
                                                 is_scan_return=is_scan_return)

    # 返回商品记录的id，用于后续添加图片
    # 判断图片是否已经存在于服务器上
    resp['code'] = 200
    resp['id'] = model_goods.id
    db.session.commit()
    img_list_status = UploadService.filterUpImages(req['img_list'])  # 图片列表发布时已判空
    resp['img_list_status'] = img_list_status
    return jsonify(resp)


@route_api.route("/goods/add-pics", methods=['GET', 'POST'])
@time_log
def addGoodsPics():
    """
    上传物品图片到服务器
    :return: 成功
    """
    resp = {'code': -1, 'msg': '操作成功', 'state': 'add pics success'}

    # 检查参数：物品id和文件
    # 检查已登陆
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)
    goods_id = req.get('id', -1)
    if goods_id == -1:
        resp['msg'] = "图片上传失败"
        resp['req'] = req
        return jsonify(resp)
    image = request.files.get('file', None)
    if not image:
        resp['msg'] = "图片上传失败"
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        resp['msg'] = '图片上传失败'
        return jsonify(resp)

    # 保存文件到 /web/static/upload/日期 目录下
    # db 新增图片
    ret = UploadService.uploadByFile(image)
    if ret['code'] != 200:
        resp['msg'] = '图片上传失败'
        return jsonify(resp)

    # 在id号物品的 pics 字段加入图片本地路径
    # 更新id号物品的 main_image 为首图
    pic_url = ret['data']['file_key']
    if not goods_info.pics:
        pics_list = []
    else:
        pics_list = goods_info.pics.split(",")
    pics_list.append(pic_url)
    goods_info.main_image = pics_list[0]
    goods_info.pics = ",".join(pics_list)
    db.session.add(goods_info)
    db.session.commit()

    # 返回成功上传
    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/goods/update-pics", methods=['GET', 'POST'])
@time_log
def updatePics():
    """
    更新物品图片
    :return: 成功
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：物品id,图片url
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        resp['msg'] = "上传数据失败"
        resp['data'] = req
        return jsonify(resp)
    img_url = req.get('img_url', None)
    if not img_url:
        resp['msg'] = "上传数据失败"
        resp['data'] = req
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        resp['msg'] = "上传数据失败"
        resp['data'] = req
        return jsonify(resp)

    # 在id号物品的pics中加入去掉前缀 /web/static/upload的图片ur
    # 将id号物品的main_image更新为首图
    pic_url = UploadService.getImageUrl(img_url)
    if not goods_info.pics:
        pics_list = []
    else:
        pics_list = goods_info.pics.split(",")
    pics_list.append(pic_url)
    goods_info.main_image = pics_list[0]
    goods_info.pics = ",".join(pics_list)
    goods_info.updated_time = datetime.datetime.now()
    db.session.add(goods_info)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/goods/end-create", methods=['GET', 'POST'])
@time_log
def endCreate():
    """
    结束创建
    :return:
    """
    resp = {'code': -1, 'msg': '操作成功', 'state': 'add pics success'}

    # 检查登陆
    # 检查参数：物品id
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '用户信息异常'
        return jsonify(resp)
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        resp['msg'] = "创建失败，稍后重试"
        resp['req'] = req
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).first()
    if not goods_info:
        resp['msg'] = '创建失败，稍后重试'
        return jsonify(resp)

    if goods_info.business_type == 2:
        # 归还贴(扫码或直接归还)
        lost_id = int(req.get('target_goods_id', -1))  # 寻物归还
        notify_id = req.get('notify_id', '')  # 扫码归还
        if lost_id != -1:
            # 寻物归还
            lost_goods = Good.query.filter_by(id=lost_id, status=1).first()
            if lost_goods and GoodsCasUtil.exec_wrap(lost_id, ['nil', 1], 2):
                GoodsService.returnToLostSuccess(return_goods=goods_info, lost_goods=lost_goods)
            else:
                goods_info.business_type = 1
                GoodsService.releaseGoodsSuccess(goods_info=goods_info)
        elif notify_id:
            # 扫码归还
            GoodsService.scanReturnSuccess(scan_goods=goods_info, notify_id=notify_id)
        else:
            resp['msg'] = "发布失败"
            jsonify(resp)
    else:
        # 非归还贴 (可能是编辑或者新的发布)
        is_edit = int(req.get('edit', 0))
        edit_info = {
            'need_recommend': int(req.get('keyword_modified', 0)),
            'modified': int(req.get('modified', 0))
        } if is_edit else None
        GoodsService.releaseGoodsSuccess(goods_info=goods_info, edit_info=edit_info)

    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/goods/search", methods=['GET', 'POST'])
@time_log
def goodsSearchV2():
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    business_type = int(req.get('business_type', -1))
    if business_type not in (0, 1):
        resp['msg'] = "获取失败"
        return jsonify(resp)
    status = int(req.get('status', -1))
    if status == -1:
        resp['msg'] = '获取失败'
        return jsonify(resp)

    p = int(req.get('p', 1))
    goods_list = RecordHandlers.get('goods').search().deal(op_status=-1,
                                                           status=status,
                                                           biz_type=business_type,
                                                           owner_name=req.get('owner_name'),
                                                           goods_name=req.get('mix_kw'),
                                                           filter_address=req.get('filter_address'),
                                                           p=p)

    def status_desc(goods_status):
        if business_type == 1:
            status_mapping = {
                '1': '待认领',
                '2': '预认领',
                '3': '已认领',
                '4': '已答谢',
                '5': '申诉中',
                '7': '已删除',
            }
        elif business_type == 0:
            status_mapping = {
                '1': '待寻回',
                '2': '预寻回',
                '3': '已寻回',
                '4': '已答谢',
                '7': '已删除',
            }
        else:  # 归还贴子
            status_mapping = {
                '0': '已拒绝',
                '1': '待确认',
                '2': '待取回',
                '3': '已取回',
                '4': '已答谢',
                '7': '已删除',
            }
        return status_mapping[str(goods_status)]

    data_goods_list = []
    if goods_list:
        # 所有发布者 id -> Member
        now = datetime.datetime.now()
        for item in goods_list:
            # 只返回符合用户期待的状态的物品
            item = item.get('_source')
            item_id = item.get('id')
            item_status = item.get('status')
            if not GoodsCasUtil.exec_wrap(item_id, [item_status, 'nil'], item_status):
                continue
            tmp_data = {
                "id": item_id,
                "goods_name": item.get('name'),
                "owner_name": item.get('owner_name'),
                "updated_time": item.get('updated_time').replace('T', ' '),
                "business_type": item.get('business_type'),
                "summary": item.get('summary'),
                "main_image": UrlManager.buildImageUrl(item.get('main_image')),
                "auther_id": item.get('member_id'),
                "auther_name": item.get('nickname'),
                "avatar": item.get('avatar'),
                "selected": False,
                "status_desc": status_desc(item.get('status')),  # 静态属性，返回状态码对应的文字
                "top": datetime.datetime.strptime(item.get('top_expire_time'), "%Y-%m-%dT%H:%M:%S") > now
            }
            data_goods_list.append(tmp_data)

    # 失/拾 一页信息 是否已加载到底
    resp['code'] = 200
    resp['data']['list'] = data_goods_list
    resp['data']['has_more'] = len(data_goods_list) >= APP_CONSTANTS['page_size'] and p < APP_CONSTANTS[
        'max_pages_allowed']  # 由于深度分页的性能问题，限制页数(鼓励使用更好的搜索条件获取较少的数据量)
    resp['business_type'] = business_type
    return jsonify(resp)


@route_api.route('/goods/apply')
@time_log
def goodsApply():
    """
    申请认领，涉及物品状态变化
    :return: 物品的状态, 是否可以显示地址
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：物品id
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)
    goods_id = int(req.get('id', -1))
    status = int(req.get('status', 0))
    if goods_id == -1 or status not in (1, 2):
        resp['msg'] = '认领失败'
        return jsonify(resp)

    if not GoodsCasUtil.exec(goods_id, status, 7):
        # 取消认领会 2——> 1，所以设置 7
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)

    # 预认领事务
    member_id = member_info.id
    MemberService.preMarkGoods(member_id=member_id, goods_id=goods_id)
    if status == 1:
        Good.query.filter_by(id=goods_id, status=status).update({'status': 2, 'confirm_time': datetime.datetime.now()},
                                                                redis_arg=-1)
        db.session.commit()
    else:
        db.session.commit()

    # 认领缓存
    CacheOpService.addPreMarkCache(goods_id=goods_id, member_id=member_id)

    # CAS 解锁
    GoodsCasUtil.exec(goods_id, 7, 2)
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/cancel/apply')
@time_log
def goodsCancelApplyInBatch():
    """
    CAS
    取消认领，（如果涉及更改原物品的状态，对该操作加锁，并加入对原状态的预期）
    :return: 物品的状态, 是否可以显示地址
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：物品id
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)
    found_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', 0))
    if found_ids is None or status not in (2, 3, 4):
        resp['msg'] = '操作失败'
        return jsonify(resp)

    # 取消认领
    member_id = member_info.id
    MemberService.cancelPremark(found_ids=found_ids, member_id=member_id)

    if status == 2:
        # 对于于认领的物品，状态可能发生变更
        no_marks = GoodsService.getNoMarksAfterDelPremark(found_ids=found_ids, member_id=member_id)
        if len(no_marks) > 0:
            # 公开信息操作加锁，状态预期和加锁
            # 失物招领状态更新
            Good.query.filter(Good.id.in_(no_marks), Good.status == status).update({'status': 1}, redis_arg=1)
            db.session.commit()
    else:
        db.session.commit()

    CacheOpService.removePreMarkCache(found_ids=found_ids, member_id=member_id)
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/cancel')
@time_log
def returnGoodsDelInBatch():
    """
    归还者批量删除，待确认的归还贴
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    return_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', -1))
    if return_ids is None or status != 1:
        resp['msg'] = '取消失败'
        return jsonify(resp)

    lost_ids = Good.query.filter(Good.id.in_(return_ids)).with_entities(Good.return_goods_id).distinct().all()

    cas_res = GoodsCasUtil.judgePair(return_ids, status, 7, lost_ids, 2, 1)
    if not cas_res:
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)

    # 寻物启示
    Good.query.filter(Good.id.in_(lost_ids), Good.status == 2).update(
        {'status': 1, 'return_goods_id': 0, 'return_goods_openid': ''},
        redis_arg=1)
    # 归还贴
    Good.query.filter(Good.id.in_(return_ids), Good.status == status).update(
        {'status': 7, 'return_goods_id': 0, 'return_goods_openid': ''})
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/to/found', methods=['GET', 'POST'])
@time_log
def returnGoodsToFoundInBatch():
    """
    CAS【lock】
    待确认的归还贴
    已拒绝的归还贴
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    return_ids = param_getter['ids'](req.get('id', None))
    status = int(req.get('status', -1))
    if return_ids is None or status not in (0, 1):
        resp['msg'] = "操作失败"
        return jsonify(resp)

    if status == 0:
        # 公开已拒绝的归还贴（只有作者能操作）
        GoodsCasUtil.set(return_ids, exp_val=0, new_val=1)
        Good.query.filter(Good.id.in_(return_ids), Good.status == status).update(
            {'status': 1, 'business_type': 1, 'top_expire_time': datetime.datetime.now()},
            redis_arg=1)
    elif status == 1:
        # 其实（再待确认的归还记录，和寻物详情）
        # 公开待确认的归还贴
        lost_ids = Good.query.filter(Good.id.in_(return_ids)).with_entities(Good.return_goods_id).distinct().all()
        # 原子公开
        cas_res = GoodsCasUtil.judgePair(return_ids, status, 1, lost_ids, 2, 1)
        if not cas_res:
            resp['msg'] = '操作冲突，请稍后重试'
            return jsonify(resp)

        # 寻物启
        Good.query.filter(Good.id.in_(lost_ids),
                          Good.status == 2).update({'status': 1, 'return_goods_id': 0, 'return_goods_openid': ''},
                                                   redis_arg=1)
        # 归还
        Good.query.filter(Good.id.in_(return_ids),
                          Good.status == status).update({'status': 1, 'business_type': 1,
                                                         'top_expire_time': datetime.datetime.now(),
                                                         'return_goods_id': 0, 'return_goods_openid': ''},
                                                        redis_arg=1)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/reject')
@time_log
def returnGoodsRejectInBatch():
    """
    批量否认待确认的归还
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    return_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', -1))
    if return_ids is None or status != 1:
        resp['msg'] = "操作失败"
        return jsonify(resp)

    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)

    lost_ids = Good.query.filter(Good.id.in_(return_ids)).with_entities(Good.return_goods_id).all()

    # 原子拒绝
    cas_res = GoodsCasUtil.judgePair(return_ids, status, 0, lost_ids, 2, 1)

    if not cas_res:
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)

    # 寻物启示
    Good.query.filter(Good.id.in_(lost_ids), Good.status == 2).update(
        {'status': 1, 'return_goods_id': 0, 'return_goods_openid': ''},
        redis_arg=1)
    # 归还贴
    Good.query.filter(Good.id.in_(return_ids), Good.status == status).update(
        {'status': 0, 'return_goods_id': 0, 'return_goods_openid': ''})
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/confirm')
@time_log
def returnGoodsConfirm():
    """
    确认必须进入查看
    进入归还贴，确认归还的是自己的
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    goods_id = int(req.get('id', -1))
    status = int(req.get('status', -1))
    if goods_id == -1 or status != 1:
        resp['msg'] = "操作失败"
        return jsonify(resp)

    # 原子确认
    if not GoodsCasUtil.exec(goods_id, status, 2):
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)

    member_info = g.member_info
    if not member_info:
        # 检查登陆
        resp['msg'] = "请先登录"
        return jsonify(resp)
    # 归还
    Good.query.filter_by(id=goods_id, status=status).update({'status': 2, 'confirm_time': datetime.datetime.now()})
    MemberService.preMarkGoods(member_id=member_info.id, goods_id=goods_id, business_type=2)
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/link/lost/del', methods=['GET'])
@time_log
def returnLinkLostDelInBatch():
    """
    此时的寻物贴的状态只有作者可以改变
    删除已取回/已答谢的归还通知时智能删除寻物贴
    批量删除归还贴id链接的寻物贴
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    return_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', 0))
    if return_ids is None or status not in (3, 4):
        resp['msg'] = "智能清除失败，请手动删除"
        return jsonify(resp)

    lost_ids = Good.query.filter(Good.id.in_(return_ids)).with_entities(Good.return_goods_id).all()

    ok_lost_ids = GoodsCasUtil.filter(lost_ids, exp_val=status, new_val=7)
    if ok_lost_ids:
        # 寻物启事
        Good.query.filter(Good.id.in_(ok_lost_ids), Good.status == status).update({'status': 7})
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/link/return/del', methods=['GET'])
@time_log
def returnLinkReturnDelInBatch():
    """
    不更改状态status
    删除已取回/已答谢的寻物贴时智能删除归还贴
    批量删除寻物贴id链接的归还贴
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    lost_ids = param_getter['ids'](req.get('ids', None))
    if lost_ids is None:
        resp['msg'] = "智能清除失败，请手动删除"
        return jsonify(resp)
    return_ids = Good.query.filter(Good.id.in_(lost_ids)).with_entities(Good.return_goods_id).all()
    # 归还
    Good.query.filter(Good.id.in_(return_ids)).update({'return_goods_openid': ''})
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/gotback', methods=['GET', 'POST'])
@time_log
def returnGoodsGotbackInBatch():
    """
    寻物启示状态只有作者能操作了
    归还帖状态也只有被归还者能操作
    在待取回的归还贴上操作biz_type==2
    在待取回的寻物贴上操作biz_type==2
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数物品id, 物品的发布者存在
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)
    goods_ids = param_getter['ids'](req.get('ids', None))
    business_type = int(req.get('biz_type', -1))
    status = int(req.get('status', -1))
    if goods_ids is None or business_type not in (0, 2) or status != 2:  # 2代表从归还贴/通知批量确认，0代表从寻物贴/详情批量确认
        resp['msg'] = '操作失败'
        return jsonify(resp)

    member_id = member_info.id
    now = datetime.datetime.now()

    lost_updated = {'status': 3, 'finish_time': now}
    return_updated = {'status': 3, 'owner_id': member_id, 'finish_time': now}
    if business_type == 2:
        # 在待取回的归还贴中(批量)操作确认
        lost_ids = Good.query.filter(Good.id.in_(goods_ids)).with_entities(
            Good.return_goods_id).distinct().all()
        cas_res = GoodsCasUtil.judgePair(goods_ids, status, 3, lost_ids, status, 3)
        if not cas_res:
            resp['msg'] = '操作冲突，请稍后重试'
            return jsonify(resp)
        # 寻物启事
        Good.query.filter(Good.id.in_(lost_ids), Good.status == 2).update(lost_updated)
        # 归还
        Good.query.filter(Good.id.in_(goods_ids), Good.status == 2).update(return_updated)
        MemberService.markedGoods(member_id=member_id, goods_ids=goods_ids)
        db.session.commit()
        # 异步发送订阅消息
        SubscribeTasks.send_return_finish_msg_in_batch.delay(gotback_returns=goods_ids)
    elif business_type == 0:
        # 在待取回的寻物贴中(批量)操作确认
        return_ids = Good.query.filter(Good.id.in_(goods_ids)).with_entities(
            Good.return_goods_id).distinct().all()

        cas_res = GoodsCasUtil.judgePair(goods_ids, status, 3, return_ids, status, 3)
        if not cas_res:
            resp['msg'] = '操作冲突，请稍后重试'
            return jsonify(resp)
        # 归还
        Good.query.filter(Good.id.in_(return_ids), Good.status == 2).update(return_updated)
        # 寻物启事
        Good.query.filter(Good.id.in_(goods_ids), Good.status == 2).update(lost_updated)
        MemberService.markedGoods(member_id=member_id, goods_ids=return_ids)
        db.session.commit()
        # 异步发送订阅消息
        SubscribeTasks.send_return_finish_msg_in_batch.delay(gotback_returns=[item[0] for item in return_ids])

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/clean', methods=['GET', 'POST'])
@time_log
def returnGoodsCleanInBatch():
    """
    涉及Goods的状态更新加锁
    此时，帖子的状态为3/4
    不管对方有没有删除，我们这里清理寻物贴
    不管对方有没有删除，单纯的删除自己发的归还贴子
    :return:
    """
    # 检查参数物品id, 物品的发布者存在
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    goods_ids = param_getter['ids'](req.get('ids', None))
    business_type = int(req.get('biz_type', -1))
    status = int(req.get('status', -1))
    if goods_ids is None or business_type not in (0, 2) or status not in (3, 4):
        resp['msg'] = '删除失败'
        return jsonify(resp)

    cas_res = GoodsCasUtil.judge(goods_ids, exp_val=status, new_val=7)
    if not cas_res:
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)

    if business_type == 2:
        # 删除归还贴需要注意，同时置空通知链接
        Good.query.filter(Good.id.in_(goods_ids)).update({'status': 7, 'return_goods_openid': ''})
    else:
        # 删除寻物贴就是普通的删除
        Good.query.filter(Good.id.in_(goods_ids)).update({'status': 7})
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/gotback')
@time_log
def goodsGotbackInBatch():
    """
    拿回失物
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数物品id, 物品的发布者存在
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)
    goods_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', -1))
    if goods_ids is None or status != 2:
        resp['msg'] = '确认失败'
        return jsonify(resp)
    cas_res = GoodsCasUtil.judge(goods_ids, exp_val=status, new_val=3)
    if not cas_res:
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)

    # 失物招领贴的认领事务
    member_id = member_info.id
    Good.query.filter(Good.id.in_(goods_ids), Good.status == status).update({'status': 3, 'owner_id': member_id,
                                                                             'finish_time': datetime.datetime.now()})
    # 不加锁是因为，不影响goods的认领计数，且是一个人的操作

    MemberService.markedGoods(member_id=member_id, goods_ids=goods_ids)
    db.session.commit()
    # 异步发送消息
    SubscribeTasks.send_found_finish_msg_in_batch.delay(gotback_founds=goods_ids)

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/info')
@time_log
def goodsInfo():
    """
    查看详情,读者分为以下类别,对应不同操作
    1.进来认领
    2.进来编辑
    3.推荐来看
    :return:物品详情,是否显示地址
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查参数：物品id,物品的发布者存在
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        resp['msg'] = '帖子不存在'
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).first()
    if not goods_info or goods_info.status == 7:
        resp['msg'] = '作者已删除'
        return jsonify(resp)
    if goods_info.report_status != 0:
        resp['msg'] = '帖子遭举报，已冻结待管理员处理。若无违规将解冻，否则将被系统自动屏蔽。'
        return resp
    # 浏览量
    has_read = int(req.get('read', 1))
    GoodsService.setGoodsReadCount(has_read=has_read, goods_id=goods_id)

    # 获取数据
    member_info = g.member_info
    business_type = goods_info.business_type
    if business_type == 0:
        data = GoodsService.getLostGoodsInfo(goods_info=goods_info, member_info=member_info)
    elif business_type == 1:
        data = GoodsService.getFoundGoodsInfo(goods_info=goods_info, member_info=member_info)
        GoodsService.setRecommendRead(is_recommend_src=int(req.get('op_status', 0)) == 2,
                                      has_read=has_read, member_info=member_info, goods_id=goods_id)
    else:
        data = GoodsService.getReturnGoodsInfo(goods_info=goods_info, member_info=member_info)

    db.session.commit()
    resp['code'] = 200
    resp['data']['info'] = data
    resp['data']['show_location'] = data['show_location']
    return jsonify(resp)


@route_api.route('/goods/pure/info', methods=['GET', 'POST'])
@time_log
def fetchGoodsInfoForThanks():
    """
    答谢时用于获取寻物链接的归还帖子数据
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查参数：物品id,物品的发布者存在
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        resp['msg'] = '答谢失败'
        return resp
    goods_info = Good.query.filter_by(id=goods_id, status=3).first()
    if not goods_info:
        resp['msg'] = '答谢失败'
        return resp
    goods_status = goods_info.status
    if not GoodsCasUtil.exec_wrap(goods_id, ['nil', goods_status], goods_status):
        # 虽然数据库还没更新，但内存的原子操作已经更新了 WR
        resp['msg'] = '操作冲突，请稍后重试'
        return resp
    resp['data']['info'] = {
        # 物品帖子数据信息
        "id": goods_info.id,
        "business_type": goods_info.business_type,  # 寻物启示 or 失物招领
        "goods_name": goods_info.name,  # 物品名
        "owner_name": goods_info.owner_name,  # 物主名
        "auther_id": goods_info.member_id,
        "auther_name": goods_info.nickname,
        "avatar": goods_info.avatar,
        "updated_time": str(goods_info.updated_time),  # 被编辑的时间 or 首次发布的时间
    }
    resp['code'] = 200
    return resp


@route_api.route("/goods/edit", methods=['GET', 'POST'])
@time_log
def editGoods():
    """
    更新物品信息
    :return: 物品id,图片名->是否在服务器上
    """
    resp = {'code': -1, 'msg': '数据上传失败', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：物品id, 物品类型business_type,物品名字goods_name,
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        return resp
    status = int(req.get('status', -1))
    if not GoodsCasUtil.exec(goods_id, status, 7):
        resp['msg'] = "操作冲突，请稍后重试"
        return resp
    img_list_status = GoodsService.editGoods(goods_id, req)
    if not img_list_status:
        return resp
    GoodsCasUtil.exec(goods_id, 7, status)
    # 通过链接发送之后的图片是逗号连起来的字符串
    resp['data'] = {
        'id': goods_id,
        'img_list_status': img_list_status
    }
    resp['code'] = 200
    return resp


@route_api.route('/goods/status', methods=['GET', 'POST'])
@time_log
def goodsStatus():
    """
    检查前端的视图的物品状态是否是正确的
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    goods_id = int(req.get('id', -1))
    status = int(req.get('status', -1))
    if goods_id == -1 or status == -1:
        resp['msg'] = '操作失败，稍后重试'
        return jsonify(resp)

    if not GoodsCasUtil.exec(goods_id, status, status):
        # 已经进入详情页面了
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/found/to/sys', methods=['GET', 'POST'])
@time_log
def unmarkGoodsToSysInBatch():
    """
    待认领的物品送给系统，默默地将符合状态的更新
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    goods_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', -1))
    if goods_ids is None or status != 1:
        resp['msg'] = '操作失败'
        return jsonify(resp)

    # CAS并发保护
    ok_goods_id = GoodsCasUtil.filter(goods_ids, exp_val=status, new_val=7)
    updated = {'member_id': APP_CONSTANTS['sys_author']['member_id'],
               'openid': APP_CONSTANTS['sys_author']['openid'],
               'nickname': APP_CONSTANTS['sys_author']['nickname'],
               'avatar': APP_CONSTANTS['sys_author']['avatar']}
    Good.query.filter(Good.status == status, Good.id.in_(ok_goods_id)).update(updated)
    db.session.commit()
    # CAS并发保护
    GoodsCasUtil.set(ok_goods_id, exp_val=7, new_val=status)

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/test/9')
@time_log
def test9():
    from common.models.ciwei.Appeal import Appeal
    from common.models.ciwei.Member import Member
    from sqlalchemy.orm import aliased
    appealor = aliased(Member)
    appealed = aliased(Member)
    appeal = Appeal.query.join(appealor, appealor.id==Appeal.member_id).add_entity(appealor).join(Good, Good.id == Appeal.goods_id).join(appealed, Good.owner_id == appealed.id).add_entity(
        Good).add_entity(appealed).all()
    return str("")
