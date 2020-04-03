#!/usr/bin/python3.6.8
import datetime

from flask import request, jsonify, g
from sqlalchemy import or_

from application import db
from common.libs import Helper
from common.libs.Helper import getCurrentDate, getDictFilterField
from common.libs.MemberService import MemberService
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Member import Member
from common.models.ciwei.Goods import Good
from common.models.ciwei.Recommend import Recommend
from common.models.ciwei.Report import Report
# -*- coding:utf-8 -*-
from common.models.ciwei.User import User
from web.controllers.api import route_api


# 查询所有记录
@route_api.route("/record/search", methods=['GET', 'POST'])
def recordSearch():
    """
    多维搜索
    1. 记录页面
    2. 选项卡
    3. 搜索框
    :return:分页搜索列表,是否还有更多
    """
    resp = {'code': -1, 'msg': 'search record successfully(search)', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：status
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)
    status = int(req['status']) if 'status' in req else None
    if not status:
        resp['msg'] = "参数缺失"
        return jsonify(resp)

    query = Good.query

    # 页面筛选
    # 获取操作值op_status（哪个记录页面）,看用户是查看哪种信息
    # 0 自己发布的
    # 1 自己认领的
    # 2 系统推荐的
    recommend_dict = {}
    op_status = int(req['op_status']) if 'op_status' in req else ''
    if op_status == 0:
        # 找出发布记录
        query = query.filter_by(member_id=member_info.id)
    elif op_status == 1:
        # 找出认寻列表
        if member_info.mark_id:
            mark_id_list = member_info.mark_id.split('#')
            mark_id_list_int = [int(i) for i in mark_id_list]
            query = query.filter(Good.id.in_(mark_id_list_int))
        else:
            resp['code'] = 200
            resp['data']['list'] = []
            resp['data']['has_more'] = 0
            return jsonify(resp)
    elif op_status == 2:
        # 找出推荐列表里面的所有物品信息
        only_new = req['only_new']
        if only_new == 'false':
            # 新推荐和历史推荐（推荐中可能包含被删除的物品）
            recommend_list = Recommend.query.filter(Recommend.member_id == member_info.id,
                                                    Recommend.status != 7).all()
        else:
            # 只要新推荐（推荐中不包含被删除的物品）
            recommend_list = Recommend.query.filter_by(member_id=member_info.id, status=0).all()
        if recommend_list:
            # 获取推荐列表的字典，格式{id:0或者1}{1000：0}表示id为1000的数据未读
            recommend_dict = MemberService.filterRecommends(recommend_list=recommend_list,
                                                            only_new=(only_new == 'true'))
            # 获取推荐的物品列表
            if recommend_dict:
                recommend_id_list = recommend_dict.keys()
                query = query.filter(Good.id.in_(recommend_id_list))
        else:
            resp['code'] = 200
            resp['data']['list'] = []
            resp['data']['has_more'] = 0
            return jsonify(resp)

    # 选项卡和搜索框筛选
    # 状态 status 或 物主名 owner_name 或 发布者member_id 或 物品名name
    query = query.filter_by(status=status)
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

    # 分页排序
    p = int(req['p']) if ('p' in req and req['p']) else 1
    if p < 1:
        p = 1
    page_size = 10
    offset = (p - 1) * page_size
    query = query.order_by(Good.id.desc()).offset(offset)
    goods_list = query.limit(page_size).all()

    # 将对应的用户信息取出来，组合之后返回
    data_goods_list = []
    if goods_list:
        member_ids = Helper.selectFilterObj(goods_list, "member_id")
        member_map = Helper.getDictFilterField(Member, Member.id, "id", member_ids)
        now = datetime.datetime.now()
        for item in goods_list:
            tmp_member_info = member_map[item.member_id]
            tmp_data = {
                "id": item.id,  # 供前端用户点击查看详情用的
                "new": recommend_dict[item.id] if recommend_dict else 1,  # 不存在时置不是new记录
                "goods_name": item.name,
                "owner_name": item.owner_name,
                "updated_time": str(item.updated_time),
                "business_type": item.business_type,
                "summary": item.summary,
                "main_image": UrlManager.buildImageUrl(item.main_image),
                "auther_name": tmp_member_info.nickname,
                "avatar": tmp_member_info.avatar,
                "selected": False,  # 供前端编辑用的属性
                "status_desc": str(item.status_desc),  # 静态属性，返回状态码对应的文字
                "top": item.top_expire_time > now  # 是否为置顶记录
            }
            data_goods_list.append(tmp_data)

    resp['code'] = 200
    resp['data']['list'] = data_goods_list
    resp['data']['has_more'] = 0 if len(query.all()) <= page_size else 1
    return jsonify(resp)


# 将商品移除自己的列表
@route_api.route("/record/delete", methods=['GET', 'POST'])
def recordDelete():
    """
    四类操作：
    1.管理员删除被举报的物品
    2.作者删除发布的物品
    3.删除系统推荐
    4.删除(取消)认领
    :return: 成功
    """
    resp = {'code': -1, 'msg': 'delete record successfully', 'data': {}}
    req = request.values

    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)

    """
    op_status=0,用户的发布记录
    op_status=1,用户的认领记录
    op_status=2,用户的推荐列表
    op_status=4,管理员的举报列表
    """
    op_status = int(req['op_status']) if 'op_status' in req else ''
    id_list = req['id_list'][1:-1].split(',')
    if op_status == 0:
        for i in id_list:
            goods_info = Good.query.filter_by(id=int(i)).first()
            goods_info.status = 7
            db.session.add(goods_info)
    elif op_status == 1:
        mark_id_list = member_info.mark_id.split('#')
        for i in id_list:
            mark_id_list.remove(i)
            member_info.mark_id = '#'.join(mark_id_list)
            db.session.add(member_info)
            # TODO：物品的mark_id也要去掉？？
    elif op_status == 2:
        # 批量更新 status = 7
        Recommend.query.filter(Recommend.member_id == member_info.id,
                               Recommend.goods_id.in_(id_list)).update(dict(status=7))
    elif op_status == 4:
        # 物品和举报状态为 5
        id_list_int = [int(i) for i in id_list]
        goods_list = Good.query.filter(Good.id.in_(id_list_int)).all()
        report_map = getDictFilterField(Report, Report.record_id, "record_id", id_list_int)
        user_info = User.query.filter_by(member_id=member_info.id).first()
        if not user_info:
            resp['code'] = -1
            resp['msg'] = "没有相关管理员信息，如需操作请添加管理员"
            resp['data'] = str(member_info.id) + "+" + member_info.nickname
            return jsonify(resp)
        if goods_list:
            for item in goods_list:
                report_item = report_map[item.id]
                report_item.user_id = user_info.uid
                report_item.status = 5
                db.session.add(report_item)

                item.user_id = user_info.uid
                item.report_status = 5
                item.updated_time = report_item.updated_time = getCurrentDate()
                db.session.add(item)

    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)
