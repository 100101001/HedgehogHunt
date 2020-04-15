# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2019/12/10 下午9:06
@file: Goods.py
@desc:
"""
import datetime
import decimal
from decimal import Decimal

from flask import request, jsonify, g
from sqlalchemy import func

from application import db, app, APP_CONSTANTS, cache
from common.cahce import cas, redis_conn_db_1
from common.libs import SubscribeService
from common.libs.Helper import getCurrentDate, queryToDict, param_getter
from common.libs.MemberService import MemberService
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.libs.mall.PayService import PayService
from common.libs.mall.WechatService import WeChatService
from common.models.ciwei.Goods import Good
from common.models.ciwei.GoodsCategory import GoodsCategory
from common.models.ciwei.GoodsTopOrder import GoodsTopOrder
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Member import Member
from common.models.ciwei.Report import Report
from common.models.ciwei.Thanks import Thank
# 异步任务
from common.tasks.recommend import RecommendTasks
from common.tasks.sms import SmsTasks
from common.tasks.subcribe import SubscribeTasks
from common.tasks.sync.es import ESTasks
from web.controllers.api import route_api


@route_api.route('/goods/category/all', methods=['POST', 'GET'])
def goodsCategory():
    resp = {'code': 200, 'msg': 'success', 'data': {}}
    categories = GoodsCategory.query.all()
    resp['data']['cat_list'] = [item.tag for item in categories]
    resp['data']['cat_default'] = [item.default_goods for item in categories]
    return jsonify(resp)


@route_api.route("/goods/top/order", methods=['POST', 'GET'])
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
    model_order.price = decimal.Decimal(req['price']).quantize(decimal.Decimal('0.00')) \
        if 'price' in req else decimal.Decimal('20.00')

    # 微信下单
    pay_data = {
        'appid': app.config['OPENCS_APP']['appid'],
        'mch_id': app.config['OPENCS_APP']['mch_id'],
        'nonce_str': wechat_service.get_nonce_str(),
        'body': '闪寻-置顶',
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
    location = req.get("location", [])
    if not location:
        resp['msg'] = "地址为空"
        return jsonify(resp)

    # 是否是扫码归还
    is_scan_return = business_type == 2 and 'owner_name' not in req
    # 所有类型帖子的公共信息
    model_goods = Good()
    model_goods.member_id = member_info.id
    model_goods.openid = member_info.openid  # 作者的身份标识，冗余设计
    model_goods.nickname = member_info.nickname
    model_goods.avatar = member_info.avatar
    model_goods.name = req["goods_name"]  # 物品名，前端发布已判空
    model_goods.target_price = Decimal(req['target_price']).quantize(Decimal('0.00')) if 'target_price' in req else 0.0
    location = req["location"]  # 放置地址/住址，前端发布已判空
    os_location = req['os_location']  # 丢失和发现地址
    model_goods.location = "###".join(location.split(","))  # 放置地址/住址
    # 如果是失物招領或者归还就是放置地点.否则就是留空
    model_goods.os_location = "###".join(
        os_location.split(",")) if os_location else model_goods.location if business_type in (1, 2) else ""
    model_goods.owner_name = "闪寻码主" if is_scan_return else req.get('owner_name')  # 前端发布除了扫码归还皆已判空
    model_goods.summary = req.get('summary')  # 前端发布已判空
    model_goods.business_type = business_type  # 失物招领or寻物启示or归还
    model_goods.category = int(req.get('category', 10))  # 没有提供物品类别就默认属于其它
    model_goods.status = 7  # 创建未完成
    model_goods.mobile = req['mobile']  # 前端发布已判空
    # 置顶的物品7天后置顶过期，非置顶物品创建时就置顶过期
    model_goods.top_expire_time = getCurrentDate() if not int(req['is_top'] if 'is_top' in req else 0) \
        else (datetime.datetime.now() + datetime.timedelta(days=int(req['days']))).strftime("%Y-%m-%d %H:%M:%S")
    db.session.add(model_goods)

    MemberService.updateCredits(member_info)

    db.session.commit()
    # 返回商品记录的id，用于后续添加图片
    # 判断图片是否已经存在于服务器上
    resp['code'] = 200
    resp['id'] = model_goods.id
    img_list_status = UploadService.filterUpImages(req['img_list'])  # 图片列表发布时已判空
    resp['img_list_status'] = img_list_status
    return jsonify(resp)


@route_api.route("/goods/add-pics", methods=['GET', 'POST'])
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
    goods_info.updated_time = getCurrentDate()
    db.session.add(goods_info)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/goods/end-create", methods=['GET', 'POST'])
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
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        resp['msg'] = '创建失败，稍后重试'
        return jsonify(resp)

    if goods_info.status == 7:
        # 帖子生效
        goods_info.status = 1

    if goods_info.business_type == 2:
        # 归还贴(扫码或直接归还)
        target_goods_id = int(req.get('target_goods_id', -1))  # 寻物归还
        notify_id = req.get('notify_id', '')  # 扫码归还
        if target_goods_id != -1:
            # 寻物归还
            target_goods_info = Good.query.filter_by(id=target_goods_id,
                                                     business_type=0,
                                                     status=1).first()
            if target_goods_info:
                # 归还贴链接接待归还的寻物贴
                goods_info.return_goods_id = target_goods_id
                goods_info.return_goods_openid = target_goods_info.openid  # 用于被归还的用户快速查找归还通知
                # 寻物贴链接归还贴，状态置为预先寻回
                target_goods_info.return_goods_id = goods_info.id
                target_goods_info.return_goods_openid = goods_info.openid  # 用于判断是归还用户查看了帖子详情
                target_goods_info.confirm_time = getCurrentDate()  # 指的是归还时间
                target_goods_info.status = 2
                db.session.add(target_goods_info)
            else:
                goods_info.business_type = 1
        elif notify_id:
            # 扫码归还
            # 异步通知失主的任务
            params = {
                'location': goods_info.location,
                'goods_name': goods_info.name,
                'rcv_openid': notify_id,
                'trig_openid': goods_info.openid,
                'trig_member_id': goods_info.member_id
            }
            SmsTasks.notifyQrcodeOwner.delay(params=params)
            # 链接归还的对象，直接就是对方的物品(如若不是可举报)
            goods_info.qr_code_openid = notify_id
            goods_info.status = 2
        else:
            resp['msg'] = "发布失败"
            jsonify(resp)
    else:
        is_edit = int(req.get('edit', 0))
        # 非归还贴 (可能是编辑或者新的发布),进行匹配推荐
        edit_info = {
            'need_recommend': int(req.get('keyword_modified', 0)),
            'modified': int(req.get('modified', 0))
        } if is_edit else None
        # Celery异步任务
        serializable_goods_info = queryToDict(goods_info)
        RecommendTasks.autoRecommendGoods.delay(edit_info=edit_info, goods_info=serializable_goods_info)
        if is_edit:
            ESTasks.on_update_goods_info.delay(goods_info=serializable_goods_info)
        else:
            ESTasks.on_insert_goods_info.delay(goods_info=serializable_goods_info)

        # if int(req.get('edit', 0)):
        #     # 编辑
        #     # 未被用户删除的推荐
        #     origin_recommends = Recommend.query.filter(Recommend.found_goods_id == goods_id,
        #                                                Recommend.status != 7)
        #     # 匹配的关键词是否被修改
        #     need_recommend = 'keyword_modified' in req and int(req['keyword_modified'])
        #     if need_recommend:
        #         # 匹配关键字被修改了，可能有些不再匹配，等于帖子被作者删除了
        #         origin_recommends.update({'status': 7}, synchronize_session=False)
        #         RecommendTask.autoRecommendGoods(goods_info=model_to_dict(goods_info), edit=True)
        #     else:
        #         if 'modified' in req and int(req['modified']):
        #             # 可能是图片/描述/地址等非匹配关键被修改了，更新为未读匹配，但不会再对全局进行自动匹配
        #             origin_recommends.update({'status': 0}, synchronize_session=False)
        # else:
        #     # 发布
        #     RecommendTask.autoRecommendGoods(goods_info=goods_info, edit=False)

    db.session.add(goods_info)
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/index', methods=['GET'])
def goodsTestNetwork():
    # goods_info = Good.query.filter_by(business_type=2, status=2).first()
    # params = {
    #     'location': "1###2###3###4",
    #     'goods_name': "shouji",
    #     'rcv_openid': 'opLxO5Q3CloBEmwcarKrF_kSA574',
    #     'trig_openid': goods_info.openid,
    #     'trig_member_id': goods_info.member_id
    # }
    # SmsTasks.notifyQrcodeOwner.delay(params=params)

    return jsonify({'lyx': 1})


@route_api.route("/goods/search", methods=['GET', 'POST'])
def goodsSearch():
    """
    多维度搜索物品
    1.有效未被举报的 status
    2.页面 business_type
    3.选项卡 status
    4.搜索框 owner_name, 物名name, author_name, address
    5.物品类别
    :return: 经分页排序后的搜索列表 list, 是否还有更多页 boolean
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查参数：business_type, 物品状态status
    business_type = int(req.get('business_type', -1))
    if business_type not in (0, 1):
        resp['msg'] = "参数错误/缺失"
        return jsonify(resp)
    status = int(req.get('status', -1))
    if status == -1:
        resp['msg'] = '参数为空'
        return jsonify(resp)

    # 维度0：按report_status字段筛选掉物品
    query = Good.query.filter(Good.report_status != 2)
    query = query.filter(Good.report_status != 3)
    query = query.filter(Good.report_status != 5)

    # 维度1：页面
    # 按拾/失筛选物品
    query = query.filter_by(business_type=business_type)

    # 维度2：选项卡
    # status
    # 1 待（新发布）
    # 2 预 （失认领，拾系统匹配后认领，或者他人主动归还）
    # 3 已 需要显示给申诉，以及显示系统的成果
    # 4 已答谢 需要显示给申诉，以及显示系统的成果
    query = query.filter_by(status=status)

    # 维度3：物品分类
    filter_category = int(req['filter_good_category']) if 'filter_good_category' in req else 0
    if filter_category:
        query = query.filter_by(category=filter_category)

    # 维度4：搜索框
    # 按物主筛选
    # 按物品名筛选
    # 按遗失/发现地址筛选
    owner_name = req['owner_name'] if 'owner_name' in req else ''
    if owner_name:
        fil_str = "%{0}%".format(owner_name[0])
        for i in owner_name[1:]:
            fil_str = fil_str + "%{0}%".format(i)
        query = query.filter(Good.owner_name.ilike("%{0}%".format(fil_str)))
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
    if mix_kw:
        fil_str = "%{0}%".format(mix_kw[0])
        for i in mix_kw[1:]:
            fil_str = fil_str + "%{0}%".format(i)
        query = query.filter(Good.name.ilike("%{0}%".format(fil_str)))
    filter_address = str(req['filter_address']) if 'filter_address' in req else ''
    if filter_address:
        fil_str = "%{0}%".format(filter_address[0])
        for i in filter_address[1:]:
            fil_str = fil_str + "%{0}%".format(i)
        query = query.filter(Good.os_location.ilike(fil_str))

    # 分页：获取第p页的所有物品
    # 排序：置顶贴和新发布的热门贴置于最前面
    p = int(req['p']) if ('p' in req and req['p']) else 1
    if p < 1:
        p = 1
    page_size = 10
    offset = (p - 1) * page_size
    goods_list = query.order_by(Good.top_expire_time.desc(), Good.view_count.desc()).offset(offset).limit(
        page_size).all()

    # 组装返回的对象列表（需要作者名,头像）
    data_goods_list = []
    if goods_list:
        # 所有发布者 id -> Member
        now = datetime.datetime.now()
        for item in goods_list:
            # 只返回符合用户期待的状态的物品
            item_id = item.id
            item_status = item.status
            if not cas.exec(item_id, item_status, item_status) and not cas.exec(item_id, 'nil', item_status):
                continue
            tmp_data = {
                "id": item.id,
                "goods_name": item.name,
                "owner_name": item.owner_name,
                "updated_time": str(item.updated_time),
                "business_type": item.business_type,
                "summary": item.summary,
                "main_image": UrlManager.buildImageUrl(item.main_image),
                "auther_name": item.nickname,
                "avatar": item.avatar,
                "selected": False,
                "status_desc": str(item.status_desc),  # 静态属性，返回状态码对应的文字
                "top": item.top_expire_time > now
            }
            data_goods_list.append(tmp_data)

    # 失/拾 一页信息 是否已加载到底
    resp['code'] = 200
    resp['data']['list'] = data_goods_list
    resp['data']['has_more'] = len(data_goods_list) >= page_size
    resp['business_type'] = business_type
    return jsonify(resp)


@route_api.route('/goods/apply')
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
    if not cas.exec(goods_id, status, 2):
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)

    # 公开信息的状态操作加锁，且加入对其状态(可变)的预期
    if status == 1:
        now = datetime.datetime.now()
        Good.query.filter_by(id=goods_id, status=status).update({'status': 2,
                                                             'confirm_time': now},
                                                            synchronize_session=False)

    # 预认领事务
    MemberService.preMarkGoods(member_id=member_info.id, goods_id=goods_id)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/cancel/apply')
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
    founds_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', 0))
    if founds_ids is None or status not in (2, 3, 4):
        resp['msg'] = '操作失败'
        return jsonify(resp)

    # 取消认领
    member_id = member_info.id
    Mark.query.filter(Mark.member_id == member_id,
                                Mark.goods_id.in_(founds_ids),
                                Mark.status == 0).update({'status': 7}, synchronize_session=False)
    mark_keys = [('mark_'+str(fid), fid) for fid in founds_ids]

    for m_key, _ in mark_keys:
        redis_conn_db_1.srem(m_key, member_id)

    if status == 2:
        # 对于于认领的物品，状态可能发生变更
        no_marks = []
        for m_key, found_id in mark_keys:
            marks = redis_conn_db_1.smembers(m_key)
            if not marks and cas.exec(found_id, 2, 1):
                no_marks.append(found_id)
        no_mark_num = len(no_marks)
        if no_mark_num > 0:
            # 公开信息操作加锁，状态预期和加锁
            # 失物招领状态更新
            Good.query.filter(Good.id.in_(no_marks), Good.status == status).update(
                {'status': 1},
                synchronize_session=False)

    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/cancel')
def returnGoodsCancelInBatch():
    """
    归还者批量删除，待确认的归还贴
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    return_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', -1))
    if return_ids is None or status != 1:
        resp['msg'] = '删除失败'
        return jsonify(resp)

    lost_ids = Good.query.filter(Good.id.in_(return_ids)).with_entities(Good.return_goods_id).distinct().all()
    total_goods_num = len(return_ids)
    # 原子公开
    for i in range(total_goods_num):
        ok1 = cas.exec(return_ids[i], status, 7)
        ok2 = cas.exec_wrap(lost_ids[i][0], [2, 'nil'], 1)
        if not ok1 or not ok2:
            for o in range(i):
                cas.exec(lost_ids[o][0], 1, 2)
                cas.exec(return_ids[o], 7, status)
            if ok1:
                cas.exec(return_ids[i], 7, status)
            if ok2:
                cas.exec(lost_ids[i][0], 1, 2)
            resp['msg'] = '操作冲突，请稍后重试'
            return jsonify(resp)

    # 寻物启示
    Good.query.filter(Good.id.in_(lost_ids), Good.status == 2).update({'status': 1,
                                                                       'return_goods_id': 0,
                                                                       'return_goods_openid': ''},
                                                                      synchronize_session=False)
    # 归还贴
    Good.query.filter(Good.id.in_(return_ids), Good.status == status).update({'status': 7,
                                                                         'return_goods_id': 0,
                                                                         'return_goods_openid': ''},
                                                                        synchronize_session=False)
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/to/found', methods=['GET', 'POST'])
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

    total_goods_num = len(return_ids)
    if status == 0:

        for i in range(total_goods_num):
            if not cas.exec(return_ids[i], 0, 1):
                for o in range(i):
                    cas.exec(return_ids[o], 1, 0)
                resp['msg'] = '操作冲突，请稍后重试'
                return jsonify(resp)

        # 公开已拒绝的归还贴（只有作者能操作）
        Good.query.filter(Good.id.in_(return_ids),
                          Good.status == status).update({'status': 1,
                                                    'business_type': 1,
                                                    'top_expire_time': datetime.datetime.now()},
                                                   synchronize_session=False)
        db.session.commit()
    elif status == 1:
        # 其实（再待确认的归还记录，和寻物详情）

        # 公开待确认的归还贴
        lost_ids = Good.query.filter(Good.id.in_(return_ids)).with_entities(Good.return_goods_id).distinct().all()

        # 原子公开
        for i in range(total_goods_num):
            ok1 = cas.exec(return_ids[i], status, 1)
            ok2 = cas.exec_wrap(lost_ids[i][0], [2, 'nil'], 1)
            if not ok1 or not ok2:
                for o in range(i):
                    cas.exec(lost_ids[o][0], 1, 2)
                    cas.exec(return_ids[o], 1, status)
                if ok1:
                    cas.exec(return_ids[i], 1, status)
                if ok2:
                    cas.exec(lost_ids[i][0], 1, 2)
                resp['msg'] = '操作冲突，请稍后重试'
                return jsonify(resp)

        # 寻物启示
        Good.query.filter(Good.id.in_(lost_ids),
                          Good.status == 2).update({'status': 1,
                                                    'return_goods_id': 0,
                                                    'return_goods_openid': ''},
                                                   synchronize_session=False)
        # 归还贴
        Good.query.filter(Good.id.in_(return_ids),
                          Good.status == status).update({'status': 1,
                                                    'business_type': 1,
                                                    'top_expire_time': datetime.datetime.now(),
                                                    'return_goods_id': 0,
                                                    'return_goods_openid': ''},
                                                   synchronize_session=False)
        db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/reject')
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

    total_goods_num = len(return_ids)
    lost_ids = Good.query.filter(Good.id.in_(return_ids)).with_entities(Good.return_goods_id).all()

    # 原子拒绝
    for i in range(total_goods_num):
        ok1 = cas.exec(return_ids[i], status, 0)
        ok2 = cas.exec_wrap(lost_ids[i][0], [2, 'nil'], 1)
        if not ok1 or not ok2:
            for o in range(i):
                cas.exec(lost_ids[o][0], 1, 2)
                cas.exec(return_ids[o], 0, status)
            if ok1:
                cas.exec(return_ids[i], 0, status)
            if ok2:
                cas.exec(lost_ids[i][0], 1, 2)
            resp['msg'] = '操作冲突，请稍后重试'
            return jsonify(resp)

    # 寻物启示
    Good.query.filter(Good.id.in_(lost_ids), Good.status == 2).update({'status': 1,
                                                                       'return_goods_id': 0,
                                                                       'return_goods_openid': ''},
                                                                      synchronize_session=False)
    # 归还贴
    Good.query.filter(Good.id.in_(return_ids), Good.status == status).update({'status': 0,
                                                                              'return_goods_id': 0,
                                                                              'return_goods_openid': ''},
                                                                             synchronize_session=False)
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/confirm')
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
    if not cas.exec(goods_id, status, 2):
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)

    member_info = g.member_info
    if not member_info:
        # 检查登陆
        resp['msg'] = "请先登录"
        return jsonify(resp)
    # 归还
    Good.query.filter_by(id=goods_id, status=status).update({'status': 2,
                                                             'confirm_time': datetime.datetime.now()},
                                                            synchronize_session=False)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/link/lost/del', methods=['GET'])
def returnLinkLostDelInBatch():
    """
    此时的寻物贴的状态只有作者可以改变
    删除已取回/已答谢的归还通知时智能删除寻物贴
    批量删除归还贴id链接的寻物贴
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    return_ids = param_getter['ids'](req.get('id', None))
    status = int(req.get('status', 0))
    if return_ids is None or status not in (3, 4):
        resp['msg'] = "智能清除失败，请手动删除"
        return jsonify(resp)

    lost_ids = Good.query.filter(Good.id.in_(return_ids)).with_entities(Good.return_goods_id).all()

    ok_lost_ids = []
    # 原子删除（归还贴和寻物贴在3,4时状态是一样的），这里除了举报不会起冲突，保险和必须的更新redis状态
    for item in lost_ids:
        if cas.exec_wrap(item[0], [status, 'nil'], 7):
            ok_lost_ids.append(item[0])

    # 寻物启事
    Good.query.filter(Good.id.in_(ok_lost_ids), Good.status == status).update({'status': 7},
                                                                              synchronize_session=False)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/link/return/del', methods=['GET'])
def returnLinkReturnDelInBatch():
    """
    不更改状态status
    删除已取回/已答谢的寻物贴时智能删除归还贴
    批量删除寻物贴id链接的归还贴
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    lost_ids = param_getter['ids'](req.get('id', None))
    if lost_ids is None:
        resp['msg'] = "智能清除失败，请手动删除"
        return jsonify(resp)

    return_ids = Good.query.filter(Good.id.in_(lost_ids)).with_entities(Good.return_goods_id).all()
    # 归还
    Good.query.filter(Good.id.in_(return_ids)).update(
        {'return_goods_openid': ''}, synchronize_session=False)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/gotback', methods=['GET', 'POST'])
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
    goods_ids = param_getter['ids'](req.get('id', None))
    business_type = int(req.get('biz_type', -1))
    status = int(req.get('status', -1))
    if goods_ids is None or business_type not in (0, 2) or status != 2:  # 2代表从归还贴/通知批量确认，0代表从寻物贴/详情批量确认
        resp['msg'] = '操作失败'
        return jsonify(resp)

    member_id = member_info.id
    total_goods_num = len(goods_ids)
    now = datetime.datetime.now()

    if business_type == 2:
        # 在待取回的归还贴中(批量)操作确认
        lost_ids = Good.query.filter(Good.id.in_(goods_ids)).with_entities(
            Good.return_goods_id).distinct().all()

        # 原子取回
        for i in range(total_goods_num):
            ok1 = cas.exec(goods_ids[i], status, 3)
            ok2 = cas.exec_wrap(lost_ids[i][0], [status, 'nil'], 3)
            if not ok1 or not ok2:
                for o in range(i):
                    cas.exec(lost_ids[o][0], 3, status)
                    cas.exec(goods_ids[o], 3, status)
                if ok1:
                    cas.exec(goods_ids[i], 3, status)
                if ok2:
                    cas.exec(lost_ids[i][0], 3, status)
                resp['msg'] = '操作冲突，请稍后重试'
                return jsonify(resp)

        # 寻物启事
        Good.query.filter(Good.id.in_(lost_ids), Good.status == 2). \
            update({'status': 3, 'finish_time': now}, synchronize_session=False)
        # 归还
        Good.query.filter(Good.id.in_(goods_ids), Good.status == 2). \
            update({'status': 3, 'owner_id': member_id, 'finish_time': now}, synchronize_session=False)
        # 异步发送订阅消息
        SubscribeTasks.send_return_finish_msg_in_batch.delay(gotback_returns=goods_ids)
    elif business_type == 0:
        # 在待取回的寻物贴中(批量)操作确认
        return_ids = Good.query.filter(Good.id.in_(goods_ids)).with_entities(
            Good.return_goods_id).distinct().all()

        # 原子取回
        for i in range(total_goods_num):
            ok1 = cas.exec(goods_ids[i], status, 3)
            ok2 = cas.exec_wrap(return_ids[i][0], [status, 'nil'], 3)
            if not ok1 or not ok2:
                for o in range(i):
                    cas.exec(return_ids[o][0], 3, status)
                    cas.exec(goods_ids[o], 3, status)
                if ok1:
                    cas.exec(goods_ids[i], 3, status)
                if ok2:
                    cas.exec(return_ids[i][0], 3, status)
                resp['msg'] = '操作冲突，请稍后重试'
                return jsonify(resp)

        # 归还
        Good.query.filter(Good.id.in_(return_ids), Good.status == 2). \
            update({'status': 3, 'owner_id': member_id, 'finish_time': now}, synchronize_session=False)
        # 寻物启事
        Good.query.filter(Good.id.in_(goods_ids), Good.status == 2). \
            update({'status': 3, 'finish_time': now}, synchronize_session=False)
        # 异步发送订阅消息
        SubscribeTasks.send_return_finish_msg_in_batch.delay(gotback_returns=[item[0] for item in return_ids])
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/return/clean', methods=['GET', 'POST'])
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

    total_goods_num = len(goods_ids)

    # 原子删除
    for i in range(total_goods_num):
        if not cas.exec(goods_ids[i], status, 7):
            for o in range(i):
                cas.exec(goods_ids[o], 7, status)
            resp['msg'] = '操作冲突，请稍后重试'
            return jsonify(resp)

    if business_type == 2:
        # 删除归还贴需要注意，同时置空通知链接
        Good.query.filter(Good.id.in_(goods_ids)).update({'status': 7,
                                                          'return_goods_openid': ''},
                                                         synchronize_session=False)
    elif business_type == 0:
        # 删除寻物贴就是普通的删除
        Good.query.filter(Good.id.in_(goods_ids)).update({'status': 7}, synchronize_session=False)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/gotback')
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

    # 失物招领贴的认领事务
    member_id = member_info.id
    total_goods_num = len(goods_ids)

    # 原子取回
    for i in range(total_goods_num):
        if not cas.exec(goods_ids[i], status, 3):
            for o in range(i):
                cas.exec(goods_ids[o], 3, status)
            resp['msg'] = '操作冲突，请稍后重试'
            return jsonify(resp)

    Good.query.filter(Good.id.in_(goods_ids), Good.status == status).update({'status': 3,
                                                                            'owner_id': member_id,
                                                                            'finish_time': datetime.datetime.now()},
                                                                           synchronize_session=False)
    # 不加锁是因为，不影响goods的认领计数，且是一个人的操作
    Mark.query.filter(Mark.member_id == member_id,
                      Mark.goods_id.in_(goods_ids),
                      Mark.status == 0).update({'status': 1}, synchronize_session=False)
    db.session.commit()

    # 异步发送消息
    SubscribeTasks.send_found_finish_msg_in_batch.delay(gotback_founds=goods_ids)

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/appeal', methods=['GET', 'POST'])
def goodsAppeal():
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数物品id, 物品的发布者存在
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)

    goods_id = int(req.get('id', -1))
    status = int(req.get('status', 0))
    if goods_id == -1 or status not in (3, 4):
        resp['msg'] = '申诉失败，请刷新后重试'
        return jsonify(resp)

    if not cas.exec(goods_id, status, 5):
        resp['msg'] = '操作冲突，请稍后重试，如紧急可联系技术人员'
        return jsonify(resp)

    # 公开信息的状态操作加锁
    goods_info = Good.query.filter_by(id=goods_id, status=status).first()
    if goods_info is None:
        resp['msg'] = '申诉失败，请刷新后重试'
        return jsonify(resp)

    # 申诉事物
    MemberService.appealGoods(member_id=member_info.id, goods_id=goods_id)

    # 失物招领贴状态(尽早释放锁)
    goods_info.status = 5
    goods_info.appeal_time = datetime.datetime.now()
    db.session.add(goods_info)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/info')
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
        resp['msg'] = '参数为空'
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).first()
    if not goods_info or goods_info.status == 7:
        resp['msg'] = '作者已删除'
        return jsonify(resp)
    goods_status = goods_info.status
    if not cas.exec_wrap(goods_id, ['nil', goods_status], goods_status):
        # 虽然数据库还没更新，但内存的原子操作已经更新了 WR
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)
    # 浏览量
    read = int(req.get('read', 1))
    if not read:
        goods_info.view_count += 1
        db.session.add(goods_info)
    # 已阅扫码归还
    member_info = g.member_info
    is_login = member_info is not None
    if is_login and goods_info.qr_code_openid == member_info.openid:
        goods_info.owner_name = member_info.name
        db.session.add(goods_info)

    # 更新为已阅推荐
    op_status = int(req.get('op_status', 0))
    if op_status == 2 and not read:
        # 从推荐记录进入详情,代表用户一定已经登陆了
        MemberService.setRecommendStatus(member_id=member_info.id, goods_id=goods_id, new_status=1, old_status=0)

    # 每个不同类型的帖子是否可看地址
    is_auth = is_login and (member_info.id == goods_info.member_id)
    business_type = goods_info.business_type
    show_location = False
    if business_type == 1:
        # 失物招领只有(预)认领者和作者自己能看地址
        show_location = is_login and (MemberService.hasMarkGoods(member_id=member_info.id, goods_id=goods_id) or is_auth)
    elif business_type == 2:
        # 能进入归还贴子的用户，都是能看的
        show_location = is_login
    elif business_type == 0:
        # 寻物启示只有归还者和作者自己能看地址
        show_location = is_login and (goods_info.return_goods_openid == member_info.openid or is_auth)

    # 例：上海市徐汇区肇嘉浜路1111号###美罗城###31.192948153###121.439673735
    location_list = goods_info.location.split("###")
    location_list[2] = eval(location_list[2])
    location_list[3] = eval(location_list[3])

    data = {
        # 物品帖子数据信息
        "id": goods_id,
        "business_type": goods_info.business_type,  # 寻物启示 or 失物招领
        "top": goods_info.top_expire_time > datetime.datetime.now(),
        "category": goods_info.category,  # 物品是哪个大类的
        "goods_name": goods_info.name,  # 物品名
        "owner_name": goods_info.owner_name,  # 物主名
        "summary": goods_info.summary,  # 简述
        "main_image": UrlManager.buildImageUrl(goods_info.main_image),
        "target_price": str(goods_info.target_price),  # TODO：悬赏金
        "pics": [UrlManager.buildImageUrl(i) for i in goods_info.pics.split(",")],
        "location": location_list,
        "mobile": goods_info.mobile,
        # 物品帖子作者信息
        "is_auth": is_auth,  # 是否查看自己发布的帖子(不能进行状态操作，可以编辑)
        "auther_id": goods_info.member_id,
        "auther_name": goods_info.nickname,
        "avatar": goods_info.avatar,
        # 为用户浏览和操作设计的信息
        "status_desc": str(goods_info.status_desc),
        "status": goods_status,
        "view_count": goods_info.view_count,  # 浏览量
        "updated_time": str(goods_info.updated_time),  # 被编辑的时间 or 首次发布的时间
        "is_thanked": goods_status == 4
    }

    if business_type == 1 and goods_status > 1:
        # 失物招领的申诉或认领信息
        data.update({'is_owner': is_login and goods_info.owner_id == member_info.id})
        if goods_status == 5:
            # 申诉的时间
            data.update({'op_time': goods_info.appeal_time.strftime("%Y-%m-%d %H:%M")})
        elif is_auth:
            # 作者需要知道认领信息和时间
            op_time = goods_info.confirm_time if goods_status == 2 else goods_info.finish_time
            data.update({'op_time': op_time.strftime("%Y-%m-%d %H:%M")})
    elif business_type == 0 and goods_status > 1:
        # 归还贴需要的寻物贴ID，和被归还过的寻物启示帖子需要归还贴ID
        is_returner = is_login and goods_info.return_goods_openid == member_info.openid
        more_data = {'is_returner': is_returner}
        if is_auth or is_returner:
            # 需要判断予寻回的帖子是否已经确认过归还，已取回，对方有没有删除帖子
            op_time = goods_info.confirm_time if goods_status == 2 else goods_info.finish_time
            return_goods_id = goods_info.return_goods_id
            status = Good.query.filter_by(id=return_goods_id).with_entities(Good.status).first()
            if not cas.exec_wrap(return_goods_id, ['nil', status], status):
                resp['msg'] = '操作冲突，请稍后重试'
                return jsonify(resp)
            more_data = {'is_returner': is_returner,
                         'return_goods_id': return_goods_id,  # 用来链接两贴
                         'is_confirmed': status[0] == 2,  # 根据是否已经确认过归还贴对寻物启示发布者和归还者进行提示
                         'is_origin_deleted': status[0] == 7,  # 根据此提示可以删除本贴
                         'op_time': op_time.strftime("%Y-%m-%d %H:%M")  # 根据此提示操作时间
                         }
        data.update(more_data)
    elif business_type == 2:
        # 能看归还贴子的都是相关人士
        lost_goods_id = goods_info.return_goods_id
        if goods_status == 1:
            more_data = {'return_goods_id': lost_goods_id}
            data.update(more_data)
        elif goods_status == 2:
            more_data = {'return_goods_id': lost_goods_id,
                         'op_time': goods_info.confirm_time.strftime("%Y-%m-%d %H:%M")}
            data.update(more_data)
        elif goods_status > 2:
            lost_goods_status = Good.query.filter_by(id=lost_goods_id).with_entities(Good.status).first()
            if not cas.exec_wrap(lost_goods_id, ['nil', lost_goods_status], lost_goods_status):
                resp['msg'] = '操作冲突，请稍后重试'
                return jsonify(resp)
            is_origin_del = lost_goods_status[0] == 7
            more_data = {'return_goods_id': lost_goods_id,
                         'is_origin_deleted': is_origin_del,
                         # 通知也删了，不再会有感谢
                         'is_no_thanks': not goods_info.return_goods_openid and is_origin_del,
                         'op_time': goods_info.finish_time.strftime("%Y-%m-%d %H:%M")}
            data.update(more_data)
    db.session.commit()
    resp['code'] = 200
    resp['data']['info'] = data
    resp['data']['show_location'] = show_location
    return jsonify(resp)


@route_api.route('/goods/pure/info', methods=['GET', 'POST'])
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
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id, status=3).first()
    if not goods_info:
        resp['msg'] = '答谢失败'
        return jsonify(resp)
    goods_status = goods_info.status
    if not cas.exec_wrap(goods_id, ['nil', goods_status], goods_status):
        # 虽然数据库还没更新，但内存的原子操作已经更新了 WR
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)
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
    return jsonify(resp)


@route_api.route("/goods/report", methods=['GET', 'POST'])
def goodsReport():
    """
    举报物品/答谢
    :return: 成功
    """
    resp = {'code': -1, 'msg': '举报成功', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：举报id, 举报类型record_type
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '没有用户信息，无法完成举报！请授权登录'
        return jsonify(resp)
    record_id = int(req.get('id', -1))
    if record_id == -1:
        resp['msg'] = "举报失败"
        resp['req'] = req
        return jsonify(resp)
    record_type = int(req.get('record_type', -1))
    if record_type not in (1, 0):
        resp['msg'] = '举报失败'
        return jsonify(resp)
    report_info = Report.query.filter_by(record_id=record_id, record_type=record_type).first()
    if report_info:
        resp['msg'] = "该条信息已被举报过，管理员处理中"
        return jsonify(resp)

    record_info = None
    if record_type == 1:
        # 物品信息违规
        record_info = Good.query.filter_by(id=record_id).first()
        goods_status = record_info.status
        if not cas.exec(record_id, goods_status, goods_status):
            resp['msg'] = "操作冲突，请稍后重试"
            return jsonify(resp)
    elif record_type == 0:
        # 答谢信息违规
        record_info = Thank.query.filter_by(id=record_id).first()
    if not record_info:
        resp['msg'] = '参数错误'
        return jsonify(resp)

    # 更新物品或答谢的 report_status 为 1
    # 新增举报
    record_info.report_status = 1
    db.session.add(record_info)
    db.session.commit()

    model_report = Report()
    model_report.status = 1
    model_report.member_id = record_info.member_id
    model_report.report_member_id = member_info.id
    model_report.record_id = record_id
    model_report.record_type = record_type
    db.session.add(model_report)
    db.session.commit()

    MemberService.updateCredits(member_info)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


# TODO:此处推荐需要移除或添加
@route_api.route("/goods/edit", methods=['GET', 'POST'])
def editGoods():
    """
    更新物品信息
    :return: 物品id,图片名->是否在服务器上
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：物品id, 物品类型business_type,物品名字goods_name,
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '用户信息异常'
        return jsonify(resp)
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        resp['msg'] = "数据上传失败"
        resp['data'] = req
        return jsonify(resp)
    status = int(req.get('status', -1))
    if not cas.exec(goods_id, status, 7):
        resp['msg'] = "操作冲突，请稍后重试"
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).first()
    if not goods_info:
        resp['msg'] = "数据上传失败"
        resp['data'] = req
        return jsonify(resp)

    goods_info.pics = ""
    goods_info.main_image = ""
    goods_info.target_price = Decimal(req['target_price']).quantize(Decimal('0.00')) if 'target_price' in req else 0.00
    goods_info.name = req.get('goods_name')
    goods_info.category = int(req.get('category', 10))  # 没有提供物品类别就默认属于其它
    goods_info.owner_name = req['owner_name']
    goods_info.summary = req['summary']
    location = req['location'].split(",")
    goods_info.status = 7  # 暂时设置为不可见
    goods_info.location = "###".join(location)
    goods_info.business_type = req['business_type']
    goods_info.mobile = req['mobile']
    # 修改成置顶贴子
    if int(req.get('is_top', 0)):
        goods_info.top_expire_time = (datetime.datetime.now() + datetime.timedelta(days=int(req['days']))) \
            .strftime("%Y-%m-%d %H:%M:%S")
    goods_info.updated_time = getCurrentDate()
    db.session.add(goods_info)

    db.session.commit()

    # 通过链接发送之后的图片是逗号连起来的字符串
    img_list = req['img_list']
    img_list_status = UploadService.filterUpImages(img_list)
    resp['img_list_status'] = img_list_status
    resp['id'] = goods_id
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/status', methods=['GET', 'POST'])
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

    if not cas.exec(goods_id, status, status):
        resp['msg'] = '操作冲突，请稍后重试'
        return jsonify(resp)

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/found/to/sys', methods=['GET', 'POST'])
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
    ok_goods_id = []
    for item_id in goods_ids:
        # 原子删除
        if cas.exec(item_id, status, 7):
            ok_goods_id.append(item_id)

    Good.query.filter(Good.status == status, Good.id.in_(ok_goods_id)).update(
        {'member_id': APP_CONSTANTS['sys_author']['member_id'],
         'openid': APP_CONSTANTS['sys_author']['openid'],
         'nickname': APP_CONSTANTS['sys_author']['nickname'],
         'avatar': APP_CONSTANTS['sys_author']['avatar']}, synchronize_session=False)
    db.session.commit()

    # CAS并发保护
    for item_id in ok_goods_id:
        # 原子发布
        cas.exec(item_id, 7, status)

    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/test')
def test():
    # goods = Good.query.filter_by(id=1).with_entities(Good.status).first()
    # Good.query.filter_by(id=1).update({'summary': 'sss', 'view_count': 1}, synchronize_session=False)
    # good = Good.query.filter_by(id=1).first()
    # db.session.commit()
    # good = Good.query.filter_by(id=1).first()
    # goods = Good.query.filter(Good.id.in_(['1','2'])).all()
    # app.logger.info("hhh")
    # goods = Good.query.filter(Good.id=='1').first()
    # goods2 = Good.query.filter_by(id='1').first()
    # from sqlalchemy import func
    # from common.models.ciwei.Mark import Mark
    # count = db.session.query(func.count(Mark.id)).scalar()
    # goods = Good.query.filter(Good.id.in_(['1', '2', '3'])).with_entities(Good.business_type).distinct().all()
    # a = Good.query.filter(Good.id.in_(goods))
    # Good.query.filter_by(id=1).update({'view_count': Good.view_count + 100}, synchronize_session=False)
    # db.session.commit()
    # status = Good.query.filter_by(id=1).with_entities(Good.status).first()
    # return jsonify({'s':status[0]})
    # cnt = db.session.query(func.count(Mark.id)).filter(Mark.status == 7).scalar()
    # Mark.query.update({'status': 7}, synchronize_session=False)
    # cnt = db.session.query(func.count(Mark.id)).filter(Mark.status == 7).scalar()
    # Good.query.filter(Good.id == 1).with_for_update().first()
    # a = Good.query.filter(Good.id == 1, Good.view_count == 4).with_for_update().update({'view_count': 5},
    #                                                                                    synchronize_session=False)
    # if a == 0:
    #     v = Good.query.filter(Good.id == 1, Good.view_count == 4).with_for_update().update({'view_count': 5},
    #                                                                                        synchronize_session=False)
    #     return "v: " + str(v)
    # a = Good.query.filter(Good.id == 1).with_for_update().update({'summary': 21}, synchronize_session='fetch')
    # a = Good.query.filter(Good.id == 1).first()
    # db.session.commit()
    # return a.summary
    # a = db.session.query(func.count(Mark.id)).filter(Mark.status != 7).with_for_update().scalar()
    # db.session.commit()
    from common.models.ciwei.Recommend import Recommend
    a = Recommend.query.update({'status': 7}, synchronize_session=False)
    goods_info = Good.query.filter_by(id=1).with_entities(Good.id, Good.member_id).first()
    # print("h")
    RecommendTasks.add_together.delay(goods_info=queryToDict(goods_info), abc=3)
    return "quick return"


@route_api.route('/goods/test/2')
def test2():
    # a = Good.query.filter(Good.id == 1).first()
    # db.session.commit()
    # return a.summary
    # a = Good.query.filter(Good.id == 1, Good.view_count == 4).with_for_update().update({'view_count': 5},
    #                                                                                    synchronize_session=False)
    # a = Good.query.filter(Good.id == 1).first()
    # b = a.summary
    # c = a.summary
    # return b + ',' + c
    cache.set('token', "hhhh")
    a = cache.get('token')
    # a = db.session.query(func.count(Mark.id)).filter(Mark.status != 7).with_for_update().scalar()
    return str(a)
    # pass


@route_api.route('/goods/test/3')
def test3():
    from application import es
    result = es.get(index='test', id=1)
    return jsonify(result.get('_source'))


@route_api.route('/goods/test/4')
def test4():
    # a = cas.exec('test', 2, 3)
    a = cas.exec_wrap('test', ['nil', 1], 3)
    return 'test cas'


@route_api.route('/goods/test/5')
def test5():
    n = {'id': "[1,2,3,4]"}
    b = {}
    goods_ids = param_getter['ids'](n.get('id', None))
    goods_ids2 = param_getter['ids'](b.get('id', None))
    from sqlalchemy import exists

    import time
    s = time.time()
    from sqlalchemy import and_
    from sqlalchemy import or_
    # rule = or_(and_(Good.status == 1, Good.return_goods_openid == "opLxO5Q3CloBEmwcarKrF_kSA574#100002"),
    #            and_(Good.status == 2, Good.qr_code_openid == "opLxO5Q3CloBEmwcarKrF_kSA574#100002"))
    # goods_list = Good.query.filter(Good.business_type == 2, rule).all()
    # f1 = filter(lambda item: item.status == 1, goods_list)
    # f2 = filter(lambda item: item.status == 2, goods_list)
    f1 = Good.query.filter_by(business_type = 2, status = 1, return_goods_openid = "opLxO5Q3CloBEmwcarKrF_kSA574#100002").all()
    f2 = Good.query.filter_by(business_type = 2, status = 2, qr_code_openid = "opLxO5Q3CloBEmwcarKrF_kSA574#100002").all()
    end = time.time() - s


    # for i in [2]:
    #     og = Good.query.filter_by(id=i).first()
    #     og.summary = '2dadsaa'
    #     db.session.add(og)
    # for item_id in [1,2,3,4,5,6,7,8]:
    #     if not cas.exec(item_id, 100, 3):
    #         for o in [1,2,3,4,5,6,7,8]:
    #             cas.exec(o, 3, 100)
    #         break
    # goods_id = [1, 2, 3, 4, 5, 6, 7, 8]
    # for i in range(len(goods_id)):
    #     if not cas.exec(goods_id[i], 100, 3):
    #         for o in range(i):
    #             cas.exec(goods_ids[o], 3, 100)
    #         break

    # for i in [1, 2, 3, 4, 5, 6, 7, 8]:
    #     if not cas.exec_wrap(i, [i, 'nil'], i):
    #         print(i)
    # Good.query.filter(Good.id.in_([8, 1, 2, 3, 4,5,6,7])).update({'qr_code_openid': ''}, synchronize_session=False)
    #a = db.session.query(exists().where(Good.id == 8)).scalar()
    good = Good.query.filter(Good.id == 19).first()
    a = good is not None

    c = set(i for i in [1,2,2,3,3,3,4,4,5,6])
    d = 1 in c
    e = 8 in c

    # a = redis_conn.get('abs')
    # Good.query.filter(Good.id.in_([1,2,3,4,5,6,7,8,9]))
    return str(end)
