# -*- coding:utf-8 -*-
import datetime

from flask import request, jsonify, g
from sqlalchemy import or_, and_

from application import db
from common.cahce import cas
from common.libs.Helper import getCurrentDate, getDictFilterField, param_getter
from common.libs.UrlManager import UrlManager
from common.libs.recommend.v2 import SyncService
from common.models.ciwei.Appeal import Appeal
from common.models.ciwei.Goods import Good
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Recommend import Recommend
from common.models.ciwei.Report import Report
from common.models.ciwei.User import User
from common.tasks.sync import SyncTasks
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
        resp['msg'] = "请先登陆"
        return jsonify(resp)
    status = int(req['status']) if 'status' in req else None
    if status is None:
        resp['msg'] = "加载失败"
        return jsonify(resp)

    query = Good.query

    # 页面,选项卡筛选
    # 获取操作值op_status（哪个记录页面）,看用户是查看哪种信息
    # 0 自己发布的
    # 1 自己认领的
    # 2 系统推荐的
    goods_id_recommend_status_map = {}
    only_new = False
    op_status = int(req.get('op_status', -1))
    if op_status == 0:
        query = query.filter_by(member_id=member_info.id, status=status, business_type=int(req['business_type']))
    elif op_status == 1:
        # 非已经答谢
        # 认领列表，找出状态为status{0[待取回],1[已取回],2[已答谢]}的
        query = query.join(Mark, Good.id == Mark.goods_id).filter(Mark.member_id == member_info.id,
                                           Mark.status == status)
    elif op_status == 5:
        # 归还列表，找出状态为status{1[待取回]，2[已取回],3[已答谢]}的
        member_openid = member_info.openid
        query = query.filter(and_(Good.business_type == 2,
                                  Good.status == status,
                                  # 两类归还都要
                                  or_(Good.return_goods_openid == member_openid,
                                      Good.qr_code_openid == member_openid)))
    elif op_status == 6:
        # 获取处理状态为status的申诉物品
        query = query.join(Appeal, Good.id == Appeal.goods_id).filter(Appeal.member_id == member_info.id,
                                               Appeal.status == status)
    elif op_status == 2:
        # 推荐列表
        only_new = req.get('only_new', '') == 'true'
        rule = and_(Recommend.target_member_id == member_info.id,
                    Recommend.status == 0 if only_new else Recommend.status != 7)
        query = query.join(Recommend, Recommend.found_goods_id == Good.id).filter(rule)

    # 搜索框筛选
    # 物主名 owner_name 或 物品名name
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

    # 分页排序
    p = int(req['p']) if ('p' in req and req['p']) else 1
    if p < 1:
        p = 1
    page_size = 10
    offset = (p - 1) * page_size
    order_rule = Recommend.rel_score.desc() if op_status == 2 else Good.id.desc()
    goods_list = query.order_by(order_rule).offset(offset).limit(page_size).all()

    # 将对应的用户信息取出来，组合之后返回
    data_goods_list = []
    if goods_list:
        now = datetime.datetime.now()
        for item in goods_list:
            # 只返回状态没有被并发改变的物品
            item_id = item.id
            item_status = item.status
            if not cas.exec_wrap(item_id, [item_status, 'nil'], item_status):
                continue
            is_pre_mark_fail = item.status != 2 and status == 0 and op_status == 1
            is_appealed = item.status == 5
            # 说明要么还没看过
            unknown_returned_lost = item.business_type == 0 and op_status == 0 and item.status == 2 and not cas.exec(
                item.return_goods_id, 2, 2)
            tmp_data = {
                "id": item.id,  # 供前端用户点击查看详情用的
                "new": 1 if op_status != 2 else (
                    0 if only_new else goods_id_recommend_status_map.get(item.id, 1)),
                # 不存在时置不是new记录
                "goods_name": item.name,
                "owner_name": item.owner_name,
                "updated_time": str(item.updated_time),
                "business_type": item.business_type,
                "summary": item.summary,
                "main_image": UrlManager.buildImageUrl(item.main_image),
                "auther_name": item.nickname,
                "avatar": item.avatar,
                "unselectable": is_appealed or is_pre_mark_fail or unknown_returned_lost,  # 前端编辑禁止选中
                "selected": False,  # 供前端选中删除记录用的属性
                "status_desc": str(item.status_desc),  # 静态属性，返回状态码对应的文字
                "top": item.top_expire_time > now,  # 是否为置顶记录
                "location": item.location.split("###")[1] if op_status == 0 or op_status == 5 else ""  # 归还贴和发布贴概要可看地址
            }
            data_goods_list.append(tmp_data)

    resp['code'] = 200
    resp['data']['list'] = data_goods_list
    resp['data']['has_more'] = len(goods_list) >= page_size
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
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登陆"
        return jsonify(resp)

    """
    op_status=0,用户的发布记录
    op_status=1,用户的认领记录
    op_status=5,用户的归还通知
    op_status=2,用户的推荐列表
    op_status=4,管理员的举报列表
    """
    op_status = int(req.get('op_status', -1))
    id_list = param_getter['ids'](req.get('id_list', None))
    status = int(req.get('status', -7))
    if status == -7 and op_status in (0, 1, 5):
        # 发布记录,认领记录,归还通知删除需要确保物品的状态
        resp['msg'] = '操作失败'
        return jsonify(resp)
    if op_status == 0:
        # 删除发布
        ok_ids = []
        for item_id in id_list:
            if cas.exec(item_id, status, 7):
                ok_ids.append(item_id)
        Good.query.filter(Good.id.in_(ok_ids), Good.status == status).update({'status': 7}, synchronize_session=False)
        # 异步同步数据
        SyncService.syncDeleteGoodsToESBulk(goods_ids=ok_ids)
        biz_type = int(req.get('biz_type', 2))
        if status == 1 and biz_type != 2:
            SyncTasks.syncDelGoodsToRedis.delay(goods_ids=ok_ids, business_type=biz_type)
    elif op_status == 1:
        # 删除认领记录（已取回，已答谢）
        Mark.query.filter(Mark.member_id == member_info.id,
                          Mark.status == status,
                          Mark.goods_id.in_(id_list)).update({'status': 7}, synchronize_session=False)
    elif op_status == 5:
        # 删除记录 ！= 删帖子（不是作者），只需解除人的链接即可
        Good.query.filter(Good.id.in_(id_list), Good.status == status). \
            update({'return_goods_openid': '',
                    'qr_code_openid': ''}, synchronize_session=False)
    elif op_status == 2:
        # 推荐删除（更新为7）
        lost_goods_ids = Recommend.query.filter(Recommend.target_member_id == member_info.id,
                                                Recommend.found_goods_id.in_(id_list)).with_entities(
            Recommend.lost_goods_id).all()
        Recommend.query.filter(Recommend.target_member_id == member_info.id,
                               Recommend.found_goods_id.in_(id_list)).update({'status': 7}, synchronize_session=False)
    elif op_status == 6:
        # 申诉只能删除已处理完毕的记录
        Appeal.query.filter(Appeal.member_id == member_info.id,
                            Appeal.status == 1,
                            Appeal.goods_id.in_(id_list)).update({'status': 7}, synchronize_session=False)
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
