# -*- coding:utf-8 -*-
import datetime

from flask import request, jsonify, g
from sqlalchemy import or_, and_

from application import APP_CONSTANTS
from common.cahce import cas
from common.libs import RecordService
from common.libs.Helper import param_getter
from common.libs.UrlManager import UrlManager
from common.loggin.decorators import time_log
from common.models.ciwei.Appeal import Appeal
from common.models.ciwei.Goods import Good
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Recommend import Recommend
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
        resp['msg'] = "请先登陆"
        return jsonify(resp)
    status = int(req.get('status', -1))
    if status == -1:
        resp['msg'] = "加载失败"
        return jsonify(resp)

    query = Good.query

    # 页面,选项卡筛选
    # 获取操作值op_status（哪个记录页面）,看用户是查看哪种信息
    # 0 自己发布的
    # 1 自己认领的
    # 2 系统推荐的
    op_status = int(req.get('op_status', -1))
    if op_status == 0:
        query = RecordService.getMyRelease(member_id=member_info.id, status=status, biz_type=int(req['business_type']))
    elif op_status == 1:
        # 非已经答谢
        # 认领列表，找出状态为status{0[待取回],1[已取回],2[已答谢]}的
        query = RecordService.getMyMark(member_id=member_info.id, mark_status=status)
    elif op_status == 5:
        # 归还列表，找出状态为status{1[待取回]，2[已取回],3[已答谢]}的
        query = RecordService.getMyReturnNotice(member_openid=member_info.openid, return_status=status)
    elif op_status == 6:
        # 获取处理状态为status的申诉物品
        query = RecordService.getMyAppeal(member_id=member_info.id, appeal_status=status)
    elif op_status == 2:
        # 推荐列表
        query = RecordService.getMyRecommend(member_id=member_info.id, goods_status=status, only_new=req.get('only_new', '') == 'true')

    search_rule = RecordService.searchBarFilter(owner_name=req.get('owner_name', ''), goods_name=str(req.get('mix_kw', '')))
    # 分页排序
    p = max(int(req.get('p', 1)), 1)
    page_size = APP_CONSTANTS['page_size']
    offset = (p - 1) * page_size
    order_rule = Recommend.rel_score.desc() if op_status == 2 else Good.id.desc()
    goods_list = query.filter(search_rule).order_by(order_rule).offset(offset).limit(page_size).all()

    # 将对应的用户信息取出来，组合之后返回
    record_list = []
    if goods_list:
        now = datetime.datetime.now()
        for item in goods_list:
            # 只返回状态没有被并发改变的物品
            record = RecordService.makeRecordData(item=item, op_status=op_status, status=status, now=now)
            if record:
                record_list.append(record)

    resp['code'] = 200
    resp['data']['list'] = record_list
    resp['data']['has_more'] = len(goods_list) >= page_size
    return resp


# 将商品移除自己的列表
@route_api.route("/record/delete", methods=['GET', 'POST'])
@time_log
def recordDelete():
    """
    四类操作：
    1.管理员删除被举报的物品
    2.作者删除发布的物品
    3.删除系统推荐
    4.删除(取消)认领
    :return: 成功
    """
    resp = {'code': -1, 'msg': '操作失败', 'data': {}}
    req = request.values
    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登陆"
        return jsonify(resp)
    """
    op_status=0, 用户的发布记录
    op_status=1, 用户的认领记录
    op_status=5, 用户的归还通知
    op_status=2, 用户的推荐列表
    op_status=4, 管理员的举报列表
    """
    op_status = int(req.get('op_status', -1))
    id_list = param_getter['ids'](req.get('id_list', None))
    status = int(req.get('status', -7))
    op_res = False
    if op_status == 0:
        op_res = RecordService.deleteMyRelease(goods_ids=id_list, biz_type=int(req.get('biz_type', 2)), status=status)
    elif op_status == 1:
        # 删除认领记录（已取回，已答谢）
        op_res = RecordService.deleteMyMark(goods_ids=id_list, member_id=member_info.id, status=status)
    elif op_status == 5:
        # 删除记录 ！= 删帖子（不是作者），只需解除人的链接即可
        op_res = RecordService.deleteReturnNotice(goods_ids=id_list, status=status)
    elif op_status == 2:
        # 推荐删除（更新为7）
        op_res = RecordService.deleteRecommendNotice(goods_ids=id_list, member_id=member_info.id)
    elif op_status == 6:
        # 申诉只能删除已处理完毕的记录
        op_res = RecordService.deleteMyAppeal(goods_ids=id_list, member_id=member_info.id)
    elif op_status == 4:
        # 物品和举报状态为 5
        user_info = User.query.filter_by(member_id=member_info.id).first()
        if user_info:
            op_res = RecordService.deleteReportedGoods(goods_ids=id_list, user_id=user_info.id)
    resp['code'] = 200 if op_res else -1
    return resp
