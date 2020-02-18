#!/usr/bin/python3.6.8

from decimal import Decimal

from flask import request, jsonify, g
from sqlalchemy import or_

from application import db
from common.libs.Helper import getCurrentDate
from common.libs.Helper import selectFilterObj, getDictFilterField
from common.libs.MemberService import MemberService
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Goods import Good
# -*- coding:utf-8 -*-
from common.models.ciwei.Member import Member
from common.models.ciwei.Report import Report
from common.models.ciwei.Thanks import Thank
from web.controllers.api import route_api


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
    name = req["goods_name"] if 'goods_name' in req else ''
    if not name:
        resp['msg'] = "参数为空"
        return jsonify(resp)
    business_type = int(req['business_type']) if 'business_type' in req else None
    if business_type != 0 and business_type != 1:
        resp['msg'] = "参数错误"
        resp['data'] = req
        return jsonify(resp)

    # 新增物品：状态7表示图片待上传
    # 用户积分涨5
    model_goods = Good()
    model_goods.member_id = member_info.id
    model_goods.openid = member_info.openid
    model_goods.name = name
    model_goods.target_price = Decimal(req['target_price']).quantize(Decimal('0.00')) if 'target_price' in req else 0.0
    location = req["location"]
    model_goods.location = "###".join(location.split(","))
    model_goods.owner_name = req['owner_name']
    model_goods.summary = req['summary']
    model_goods.business_type = business_type
    model_goods.status = 7  # 创建未完成
    model_goods.mobile = req['mobile']
    model_goods.updated_time = model_goods.created_time = getCurrentDate()
    db.session.add(model_goods)
    goods_info = model_goods
    MemberService.updateCredits(member_info)

    # 返回商品记录的id，用于后续添加图片
    # 判断图片是否已经存在于服务器上
    resp['code'] = 200
    resp['id'] = goods_info.id
    img_list = req['img_list']
    img_list_status = UploadService.filterUpImages(img_list)
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
        resp['msg'] = '用户信息异常'
        return jsonify(resp)
    goods_id = req['id'] if 'id' in req else None
    if not goods_id:
        resp['msg'] = "参数为空"
        resp['req'] = req
        return jsonify(resp)
    images_target = request.files
    image = images_target['file'] if 'file' in images_target else None
    if not image:
        resp['msg'] = "参数为空"
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        resp['msg'] = '参数错误'
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
    db.session.commit()

    # 返回成功上传
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
    goods_id = req['id'] if 'id' in req else None
    if not goods_id:
        resp['msg'] = "参数为空"
        resp['req'] = req
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        resp['msg'] = '参数错误'
        return jsonify(resp)

    # 更新id号物品的状态 7->1
    # TODO:auther_id和target_goods_id???
    # 在 auther_id 会员的 recommend_id 中加入物品id
    # 更新 target_goods_id 物品 status ->2
    # 创建或者修改完成时, 对用户进行推荐(匹配拾/失物品, 将匹配的物品id加入失去物品作者的recommend_id)
    if goods_info.status == 7:
        goods_info.status = 1
    goods_info.updated_time = getCurrentDate()
    auther_id = req['auther_id'] if 'auther_id' in req else None
    if auther_id:
        auther_info = Member.query.filter_by(id=auther_id).with_for_update().first()
        MemberService.addRecommendGoods(auther_info, goods_info.id)
    target_goods_id = req['target_goods_id'] if 'target_goods_id' in req else None
    if target_goods_id:
        target_goods_info = Good.query.filter_by(id=target_goods_id).with_for_update().first()
        if target_goods_info:
            target_goods_info.status = 2
    MemberService.recommendGoods(goods_info)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/goods/search", methods=['GET', 'POST'])
def goodsSearch():
    """
    多维度搜索物品
    1.有效未被举报的 status
    2.页面 business_type
    3.选项卡 status
    4.搜索框 owner_name, 物名name, author_name, address
    :return: 经分页排序后的搜索列表 list, 是否还有更多页 boolean
    """
    resp = {'code': -1, 'msg': 'search successfully(search)', 'data': {}}
    req = request.values

    # 检查参数：business_type, 物品状态status
    business_type = int(req['business_type']) if 'business_type' in req else None
    if business_type != 0 and business_type != 1:
        resp['msg'] = "参数错误/缺失"
        return jsonify(resp)
    status = int(req['status']) if 'status' in req else None
    if not status:
        resp['msg'] = '参数为空'
        return jsonify(resp)

    # 维度0：按status和report_status字段筛选掉物品
    query = Good.query.filter(Good.status != 8)
    query = query.filter(Good.status != 7)

    query = query.filter(Good.report_status != 2)
    query = query.filter(Good.report_status != 3)
    query = query.filter(Good.report_status != 5)

    # 维度1：页面
    # 按拾/失筛选物品
    query = query.filter_by(business_type=business_type)

    # 维度2：选项卡
    # status
    # -1 全部
    # 1 待（新发布）
    # 2 预 （失认领，拾系统匹配后认领，或者他人主动归还）
    # TODO： 3 已 （最终状态）需要显示给所有人？？
    if status == -1:
        query = query.filter(Good.status != 4)
        query = query.filter(Good.status != 5)
        query = query.filter(Good.status != 6)
    else:
        query = query.filter_by(status=status)

    # 维度3：搜索框
    # 加上按物主筛选
    # 加上按物品名筛选
    # 加上按发布者筛选
    # 加上按地址筛选
    owner_name = req['owner_name'] if 'owner_name' in req else ''
    if owner_name:
        rule = or_(Good.owner_name.ilike("%{0}%".format(owner_name)))
        query = query.filter(rule)
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
    if mix_kw:
        fil_str = "%{0}%".format(mix_kw[0])
        for i in mix_kw[1:]:
            fil_str = fil_str + "%{0}%".format(i)
        rule = or_(Good.name.ilike("%{0}%".format(fil_str)), Good.member_id.ilike("%{0}%".format(mix_kw)))
        query = query.filter(rule)
    filter_address = str(req['filter_address']) if 'filter_address' in req else ''
    if filter_address:
        fil_str = "%{0}%".format(filter_address[0])
        for i in filter_address[1:]:
            fil_str = fil_str + "%{0}%".format(i)
        rule = or_(Good.location.ilike(fil_str))
        query = query.filter(rule)

    # 分页：获取第p页的所有物品
    # 排序：新发布的热门贴置于最前面 TODO：id=新旧？
    p = int(req['p']) if ('p' in req and req['p']) else 1
    if p < 1:
        p = 1
    page_size = 10
    offset = (p - 1) * page_size
    goods_list = query.order_by(Good.id.desc(), Good.view_count.desc()).offset(offset).limit(page_size).all()

    # 组装返回的对象列表（需要作者名,头像）
    data_goods_list = []
    if goods_list:
        # 所有发布者 id -> Member
        member_ids = selectFilterObj(goods_list, "member_id")
        member_map = getDictFilterField(Member, Member.id, "id", member_ids)

        for item in goods_list:
            tmp_member_info = member_map[item.member_id]
            tmp_data = {
                "id": item.id,
                "goods_name": item.name,
                "owner_name": item.owner_name,
                "updated_time": str(item.updated_time),
                "business_type": item.business_type,
                "summary": item.summary,
                "main_image": UrlManager.buildImageUrl(item.main_image),
                "auther_name": tmp_member_info.nickname,
                "avatar": tmp_member_info.avatar,
                "selected": False,
                "status_desc": str(item.status_desc),  # 静态属性，返回状态码对应的文字
            }
            data_goods_list.append(tmp_data)

    # 失/拾 一页信息 是否已加载到底
    resp['code'] = 200
    resp['data']['list'] = data_goods_list
    resp['data']['has_more'] = 0 if len(data_goods_list) < page_size else 1
    resp['business_type'] = business_type
    return jsonify(resp)


@route_api.route('/goods/applicate')
def goodsApplicate():
    """
    申请认领
    :return: 物品的状态, 是否可以显示地址
    """
    resp = {'code': -1, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：物品id
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '用户信息异常'
        return jsonify(resp)
    goods_id = int(req['id']) if 'id' in req else None
    if not goods_id:
        resp['msg'] = '参数为空'
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        resp['msg'] = '参数错误'
        return jsonify(resp)

    # 在物品的mark_id字段加入认领用户的id
    # 物品状态为2, 预
    # 物品的认领数量加1
    member_info = g.member_info
    goods_mark_id = goods_info.mark_id
    if goods_mark_id:
        goods_mark_id_list = goods_mark_id.split('#')
        if str(member_info.id) not in goods_mark_id_list:
            goods_info.mark_id = goods_info.mark_id + "#" + str(member_info.id)
    else:
        goods_info.mark_id = str(member_info.id)
    goods_info.status = 2
    goods_info.tap_count = goods_info.tap_count + 1
    goods_info.updated_time = getCurrentDate()

    # 在用户的mark_id字段加入认领物品的id
    member_mark_id = member_info.mark_id
    if member_mark_id:
        member_mark_id_list = member_mark_id.split('#')
        if str(member_info.id) not in member_mark_id_list:
            member_info.mark_id = member_mark_id + "#" + str(goods_info.id)
    else:
        member_info.mark_id = str(goods_info.id)
    member_info.updated_time = getCurrentDate()
    db.session.commit()

    # TODO：认领后可见地址？？
    # 通知前端物品状态更新
    resp['code'] = 200
    resp['data']['show_location'] = True
    resp['data']['status'] = goods_info.status
    resp['data']['status_desc'] = goods_info.status_desc
    return jsonify(resp)


@route_api.route('/goods/index')
def goods_index():
    return jsonify({"hello": "lyx"})


@route_api.route('/goods/gotback')
def goodsGotback():
    """
    拿回失物
    :return:
    """
    resp = {'code': -1, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数物品id, 物品的发布者存在
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '用户信息异常'
        return jsonify(resp)
    goods_id = int(req['id']) if 'id' in req else None
    if not goods_id:
        resp['msg'] = '参数为空'
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        resp['msg'] = '参数错误'
        return jsonify(resp)
    author_info = Member.query.filter_by(id=goods_info.member_id).first()
    if not author_info:
        resp['msg'] = '发布者信息缺失'
        return jsonify(resp)

    # 更新物品和会员
    # TODO：在物品的owner_id字段加入失主id？？怎么搜索?
    # 在物品的owner_id字段加入失主id
    # 更新物品状态 3, 已
    # TODO：更新归还次数加 1？？
    goods_owner_id = goods_info.owner_id
    if goods_owner_id:
        goods_owner_id_list = goods_owner_id.split('#')
        if str(member_info.id) not in goods_owner_id_list:
            goods_info.owner_id = goods_info.owner_id + "#" + str(member_info.id)
    else:
        goods_info.owner_id = str(member_info.id)
    goods_info.status = 3
    goods_info.tap_count = goods_info.tap_count + 1
    goods_info.updated_time = getCurrentDate()
    from common.libs import SubscribeService
    SubscribeService.send_finished_subscribe(goods_info)

    # 在会员的gotback_id中加入物品的id
    member_gotback_id = member_info.gotback_id
    if member_gotback_id:
        member_info.gotback_id = member_gotback_id + "#" + str(goods_info.id)
    else:
        member_info.gotback_id = str(goods_info.id)
    member_info.updated_time = getCurrentDate()
    db.session.commit()

    # 拿回者可见地址
    # 通知前端状态更新
    resp['code'] = 200
    resp['data']['show_location'] = True
    resp['data']['status'] = goods_info.status
    resp['data']['status_desc'] = goods_info.status_desc
    return jsonify(resp)


@route_api.route('/goods/info')
def goodsInfo():
    """
    查看详情,读者分为以下类别,对应不同操作
    1.进来认领/TODO：归还？？
    2.进来编辑
    3.推荐来看
    :return:物品详情,是否显示地址
    """
    resp = {'code': -1, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    # 检查参数：物品id,物品的发布者存在
    goods_id = int(req['id']) if 'id' in req else None
    if not goods_id:
        resp['msg'] = '参数为空'
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        resp['msg'] = '参数错误'
        return jsonify(resp)
    author_info = Member.query.filter_by(id=goods_info.member_id).first()
    if not author_info:
        resp['msg'] = '发布者信息缺失'
        return jsonify(resp)

    # 已认领显示地址,默认不显示
    member_info = g.member_info
    # TODO：用户能否看到地址,如果是在mark列表或者发布者可以看到地址和电话？？
    show_location = False
    if member_info and member_info.mark_id:
        mark_goods_id = member_info.mark_id
        mark_id_list = mark_goods_id.split('#')
        if str(goods_info.id) in mark_id_list:
            show_location = True

    # 用户查看了被系统推荐的物品, 将推荐状态从0更新为1
    # 在会员的 recommand_id 字典中, 更新该物品状态从 0 为 1
    if member_info and member_info.recommend_id:
        recommend_id_list = MemberService.getRecommendDict(member_info.recommend_id, False)
        if goods_id in recommend_id_list.keys() and recommend_id_list[goods_id] == 0:
            recommend_id_list[goods_id] = 1
        member_info.recommend_id = MemberService.joinRecommendDict(recommend_id_list)
    # 浏览量加一(TODO:同一次登陆会话看多少次应都只算一次浏览)
    goods_info.view_count = goods_info.view_count + 1
    db.session.commit()

    # 作者可以编辑, 和查看地址
    if member_info and (member_info.id == author_info.id):
        is_auth = True
        show_location = True
    else:
        is_auth = False

    # 处理地址
    # 例：上海市徐汇区肇嘉浜路1111号###美罗城###31.192948153###121.439673735
    location_list = goods_info.location.split("###")
    location_list[2] = eval(location_list[2])
    location_list[3] = eval(location_list[3])

    resp['code'] = 200
    resp['data']['info'] = {
        "id": goods_info.id,
        "goods_name": goods_info.name,
        "owner_name": goods_info.owner_name,
        "summary": goods_info.summary,
        "view_count": goods_info.view_count,
        "main_image": UrlManager.buildImageUrl(goods_info.main_image),
        "target_price": str(goods_info.target_price),
        "pics": [UrlManager.buildImageUrl(i) for i in goods_info.pics.split(",")],
        "updated_time": str(goods_info.updated_time),
        "location": location_list,
        "business_type": goods_info.business_type,
        "mobile": goods_info.mobile,
        "status_desc": str(goods_info.status_desc),
        "status": goods_info.status,
        "auther_id": author_info.id,
        "auther_name": author_info.nickname,
        "avatar": author_info.avatar,
        "is_auth": is_auth
    }
    resp['data']['show_location'] = show_location
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
    record_id = req['id'] if 'id' in req else None
    if not record_id:
        resp['msg'] = "参数为空"
        resp['req'] = req
        return jsonify(resp)
    record_type = int(req['record_type']) if 'record_type' in req else None
    if record_type != 0 and record_type != 1:
        resp['msg'] = '参数错误/缺失'
        return jsonify(resp)
    report_info = Report.query.filter_by(record_id=record_id).first()
    if report_info:
        resp['msg'] = "该条信息已被举报过，管理员处理中"
        return jsonify(resp)
    # TODO：物品/答谢两表ID不重复？
    if record_type == 1:
        # 物品信息违规
        record_info = Good.query.filter_by(id=record_id).with_for_update().first()
    elif record_type == 0:
        # 答谢信息违规
        record_info = Thank.query.filter_by(id=record_id).with_for_update().first()
    if not record_info:
        resp['msg'] = '参数错误'
        return jsonify(resp)

    # 更新物品或答谢的 report_status 为 1
    # 新增举报
    # TODO：发起举报的会员的积分+5？
    record_info.report_status = 1
    record_info.updated_time = getCurrentDate()

    model_report = Report()
    model_report.status = 1
    model_report.member_id = record_info.member_id
    model_report.report_member_id = member_info.id
    model_report.record_id = record_id
    model_report.record_type = record_type
    model_report.updated_time = model_report.created_time = getCurrentDate()
    db.session.add(model_report)

    MemberService.updateCredits(member_info)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


# TODO:清空操作不太对
# TODO:此处推荐需要移除或添加
@route_api.route("/goods/edit", methods=['GET', 'POST'])
def editGoods():
    """
    更新物品信息
    :return: 物品id,图片名->是否在服务器上
    """
    resp = {'code': -1, 'msg': 'edit goods data successfully(goods/add)', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：物品id, 物品类型business_type,物品名字goods_name,
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '用户信息异常'
        return jsonify(resp)
    goods_id = req['id'] if 'id' in req else None
    if not goods_id:
        resp['msg'] = "参数为空"
        resp['data'] = req
        return jsonify(resp)
    business_type = int(req['business_type']) if 'business_type' in req else None
    if business_type != 0 and business_type != 1:
        resp['msg'] = "参数为空"
        resp['data'] = req
        return jsonify(resp)
    name = req["goods_name"] if 'goods_name' in req else None
    if not name:
        resp['msg'] = "参数为空"
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        resp['msg'] = "参数错误"
        resp['data'] = req
        return jsonify(resp)

    # 更新物品字段
    ## TODO:清空物品图片列表，为后续的插入图片做准备（虽然是清空，但是不是使用列表，而是使用空字符串）???
    goods_info.pics = ""
    goods_info.main_image = ""
    goods_info.target_price = Decimal(req['target_price']).quantize(Decimal('0.00')) if 'target_price' in req else 0.00
    goods_info.name = name
    goods_info.owner_name = req['owner_name']
    goods_info.summary = req['summary']
    location = req['location'].split(",")
    goods_info.location = "###".join(location)
    goods_info.business_type = business_type
    goods_info.mobile = req['mobile']
    goods_info.updated_time = getCurrentDate()
    db.session.commit()

    # 通过链接发送之后的图片是逗号连起来的字符串
    resp['code'] = 200
    img_list = req['img_list']
    img_list_status = UploadService.filterUpImages(img_list)
    resp['img_list_status'] = img_list_status
    resp['id'] = goods_id
    return jsonify(resp)


@route_api.route("/goods/update-pics", methods=['GET', 'POST'])
def updatePics():
    """
    更新物品图片
    :return: 成功
    """
    resp = {'code': -1, 'msg': 'edit goods data successfully(goods/add)', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：物品id,图片url
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '用户信息异常'
        return jsonify(resp)
    goods_id = req['id'] if 'id' in req else None
    if not goods_id:
        resp['msg'] = "参数为空"
        resp['data'] = req
        return jsonify(resp)
    img_url = req['img_url'] if 'img_url' in req else ''
    if not img_url:
        resp['msg'] = "参数为空"
        resp['data'] = req
        return jsonify(resp)
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        resp['msg'] = "参数错误"
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
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)
