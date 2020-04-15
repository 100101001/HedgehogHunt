#!/usr/bin/python3.6.8
# Editor weichaoxu

# -*- coding:utf-8 -*-
from common.models.ciwei.Member import Member
from common.models.ciwei.User import User
from common.models.ciwei.Goods import Good
from common.models.ciwei.Thanks import Thank
from common.models.ciwei.Report import Report
from web.controllers.api import route_api
from flask import request, jsonify, g
from application import app, db
from sqlalchemy import or_
from common.libs.Helper import getCurrentDate, selectFilterObj, getDictFilterField
from common.libs.MemberService import MemberService
from common.libs.UrlManager import UrlManager


# 查询所有举报信息
@route_api.route("/report/goods-search", methods=['GET', 'POST'])
def reportGoodsSearch():
    resp = {'code': 200, 'msg': 'search successfully(search)', 'data': {}}
    req = request.values

    p = int(req['p']) if ('p' in req and req['p']) else 1
    if p < 1:
        p = 1

    page_size = 10
    offset = (p - 1) * page_size

    status = int(req['status']) if ('status' in req and req['status']) else 0
    record_type = int(req['record_type']) if ('record_type' in req and req['record_type']) else "nonono"
    query = Report.query.filter_by(status=status)
    query = query.filter_by(record_type=record_type)
    # #将对应的用户信息取出来，组合之后返回
    reports_list = query.order_by(Report.id.desc()).offset(offset).limit(10).all()
    record_ids = selectFilterObj(reports_list, 'record_id')

    owner_name = req['owner_name'] if 'owner_name' in req else ''
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''

    record_query = Good.query.filter(Good.id.in_(record_ids))
    if owner_name:
        rule = or_(Good.owner_name.ilike("%{0}%".format(owner_name)))
        record_query = record_query.filter(rule)
    if mix_kw:
        fil_str = "%{0}%".format(mix_kw[0])
        for i in mix_kw[1:]:
            fil_str = fil_str + "%{0}%".format(i)
        rule = or_(Good.name.ilike("%{0}%".format(fil_str)), Good.member_id.ilike("%{0}%".format(mix_kw)))
        record_query = record_query.filter(rule)
    records_list = record_query.order_by(Good.id.desc(), Good.view_count.desc()).offset(offset).limit(10).all()

    data_goods_list = []
    if records_list:
        # 获取用户的信息
        for item in records_list:
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
            }
            data_goods_list.append(tmp_data)

    resp['data']['list'] = data_goods_list
    resp['data']['has_more'] = len(data_goods_list) >= page_size
    return jsonify(resp)


@route_api.route("/report/thanks-search", methods=['GET', 'POST'])
def reportThanksSearch():
    resp = {'code': 200, 'msg': 'search successfully(search)', 'data': {}}
    req = request.values

    p = int(req['p']) if ('p' in req and req['p']) else 1
    if p < 1:
        p = 1

    page_size = 10
    offset = (p - 1) * page_size

    status = int(req['status']) if ('status' in req and req['status']) else 0
    record_type = int(req['record_type']) if ('record_type' in req and req['record_type']) else "nonono"
    query = Report.query.filter_by(status=status)
    query = query.filter_by(record_type=record_type)
    # #将对应的用户信息取出来，组合之后返回
    reports_list = query.order_by(Report.id.desc()).offset(offset).limit(10).all()
    record_ids = selectFilterObj(reports_list, 'record_id')

    owner_name = req['owner_name'] if 'owner_name' in req else ''
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''

    records_list = []
    if record_type == 1:
        record_query = Good.query.filter(Good.id.in_(record_ids))
        records_list = record_query.order_by(Good.id.desc(), Good.view_count.desc()).offset(offset).limit(10).all()
    else:
        record_query = Thank.query.filter(Thank.id.in_(record_ids))
        if owner_name:
            rule = or_(Thank.owner_name.ilike("%{0}%".format(owner_name)))
            record_query = record_query.filter(rule)
        if mix_kw:
            fil_str = "%{0}%".format(mix_kw[0])
            for i in mix_kw[1:]:
                fil_str = fil_str + "%{0}%".format(i)
            rule = or_(Thank.name.ilike("%{0}%".format(fil_str)), Good.member_id.ilike("%{0}%".format(mix_kw)))
            record_query = record_query.filter(rule)
            records_list = record_query.order_by(Thank.id.desc(), Good.view_count.desc()).offset(offset).limit(10).all()

    data_goods_list = []
    if records_list:
        for item in records_list:
            if record_type == 1:
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
                }
            else:
                tmp_data = {
                    "id": item.id,
                    "status": item.status,  # 不存在时置1
                    "goods_name": item.goods_name,
                    "owner_name": item.owner_name,
                    "updated_time": str(item.updated_time),
                    "business_desc": item.business_desc,
                    "summary": item.summary,
                    "reward": "0.00",
                    "auther_name": item.nickname,
                    "avatar": item.avatar,
                    "selected": False,
                }
            data_goods_list.append(tmp_data)

    resp['data']['list'] = data_goods_list
    resp['data']['has_more'] = len(data_goods_list) >= page_size
    return jsonify(resp)


# 查看举报详情
@route_api.route('/report/goods-info')
def reportGoodsInfo():
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    id = int(req['id']) if ('id' in req and req['id']) else 0
    goods_info = Good.query.filter_by(id=id).first()
    if not goods_info:
        resp['code'] = -1
        resp['msg'] = '没有找到相关商品信息'
        return jsonify(resp)

    member_info = g.member_info
    # 用户能否看到地址,如果是在mark列表或者发布者可以看到地址和电话
    show_location = True

    report_info = Report.query.filter_by(record_id=id).first()
    auther_info = Member.query.filter_by(id=goods_info.member_id).first()
    if not auther_info:
        resp['code'] = -1
        resp['msg'] = '没有找到相关发布者信息'
        return jsonify(resp)

    # 处理地址
    location_list = goods_info.location.split("###")
    location_list[2] = eval(location_list[2])
    location_list[3] = eval(location_list[3])
    # 浏览量加一
    goods_info.view_count = goods_info.view_count + 1
    db.session.add(goods_info)

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

        "auther_name": auther_info.nickname,
        "avatar": auther_info.avatar,
    }

    resp['data']['show_location'] = show_location

    db.session.commit()

    if not report_info:
        resp['code'] = -1
        resp['msg'] = "没有找到相关记录"
        return jsonify(resp)

    report_member_info = Member.query.filter_by(id=report_info.report_member_id).first()
    # 没有找到用户信息则返回
    if not report_member_info:
        resp['data']['report_auth_info'] = {}
        resp['msg'] = '举报者信息丢失'
        resp['data']['report_id'] = report_info.id
        return jsonify(resp)

    resp['data']['report_auth_info'] = {
        "avatar": report_member_info.avatar,
        "auther_name": report_member_info.nickname,
        "updated_time": str(report_member_info.updated_time),
        "is_auth": False,
        "goods_status": goods_info.status,
    }

    resp['data']['ids'] = {
        "auther_id": auther_info.id,
        "report_member_id": report_member_info.id,
        "goods_id": goods_info.id,
        "report_id": report_info.id
    }

    return jsonify(resp)


# 拉黑发布者或者举报者
@route_api.route('/report/block')
def reportBlock():
    resp = {'code': 200, 'msg': 'operate successfully(block)', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    user_info = User.query.filter_by(member_id=member_info.id).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "没有相关管理员信息，如需操作请添加管理员"
        resp['data'] = str(member_info.id) + "+" + member_info.nickname
        return jsonify(resp)

    report_status = int(req['report_status']) if 'report_status' in req else "nonono"
    auther_id = int(req['auther_id'])
    report_member_id = int(req['report_member_id'])
    goods_id = int(req['goods_id'])
    report_id = int(req['report_id'])

    auther_info = Member.query.filter_by(id=auther_id).first()
    report_member_info = Member.query.filter_by(id=report_member_id).first()
    goods_info = Good.query.filter_by(id=goods_id).first()
    report_info = Report.query.filter_by(id=report_id).first()

    report_info.status = report_status
    report_info.user_id = user_info.uid
    goods_info.report_status = report_status
    goods_info.user_id = user_info.uid
    # 拉黑举报者
    if report_status == 2:
        report_member_info.status = 0
    # 拉黑发布者
    elif report_status == 3:
        auther_info.status = 0
    # 没有违规
    else:
        pass

    auther_info.updated_time = report_info.updated_time = goods_info.updated_time = report_info.updated_time = getCurrentDate()
    db.session.add(auther_info)
    db.session.add(report_info)
    db.session.add(report_member_info)
    db.session.add(goods_info)
    db.session.commit()

    return jsonify(resp)
