# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/2/8 下午6:32
@file: Record.py
@desc:
"""
import datetime

from flask import request, jsonify, g

from application import APP_CONSTANTS
from common.libs import RecordService
from common.libs.Helper import param_getter
from common.libs.RecordService import RecordHandlers
from common.loggin.time import time_log
from common.models.ciwei.Goods import Good
from common.models.ciwei.Recommend import Recommend
from common.models.proxy.GoodProxy import GoodProxy
from web.controllers.api import route_api


# 查询所有记录
@route_api.route("/record/search", methods=['GET', 'POST'])
@time_log
def recordSearch():
    """
    多维搜索
    1. 记录页面
    2. 选项卡
    3. 搜索框
    :return:分页搜索列表,是否还有更多
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
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

    """
    op_status=0, 用户的发布记录
    op_status=1, 用户的认领记录
    op_status=5, 用户的归还通知
    op_status=6, 用户的申诉列表
    op_status=2, 用户的推荐列表
    """
    op_status = int(req.get('op_status', -1))

    p = int(req.get('p', 1))
    report_rule = Good.report_status == 0 if op_status == 2 else Good.report_status.in_([0, 1])
    order_rule = Recommend.rel_score.desc() if op_status == 2 else Good.id.desc()
    goods_list = RecordHandlers.get('goods').search().deal(op_status,
                                                           member_id=member_info.id, member_openid=member_info.openid,
                                                           biz_type=int(req.get('business_type')), status=status,
                                                           only_new=req.get('only_new') == "true",
                                                           # 搜索栏和分页排序参数
                                                           owner_name=req.get('owner_name'),
                                                           goods_name=req.get('mix_kw'),
                                                           p=p,
                                                           report_rule=report_rule,
                                                           order_rule=order_rule)

    recommend_status_map = None
    if op_status == 2:
        recommend_status_map = {item.id: 0 for item in goods_list}
        Recommend.getStatus(goods_list, member_info.id, recommend_status_map)
    # 将对应的用户信息取出来，组合之后返回
    record_list = []
    if goods_list:
        now = datetime.datetime.now()
        for item in goods_list:
            if op_status == 0:
                item = item.get('_source')
                goods = GoodProxy()
                goods.__dict__ = item
                item = goods
            # 只返回状态没有被并发改变的物品
            record = RecordService.makeRecordData(item=item, op_status=op_status, status=status, now=now, recommend_status_map=recommend_status_map)
            if record:
                record_list.append(record)

    resp['code'] = 200
    resp['data']['list'] = record_list
    resp['data']['has_more'] = len(goods_list) >= APP_CONSTANTS['page_size'] and p < APP_CONSTANTS[
        'max_pages_allowed']  # 由于深度分页的性能问题，限制页数(鼓励使用更好的搜索条件获取较少的数据量)
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
        return resp
    """
    op_status=0, 用户的发布记录
    op_status=1, 用户的认领记录
    op_status=5, 用户的归还通知
    op_status=6, 用户的申诉列表
    op_status=2, 用户的推荐列表
    """
    op_status = int(req.get('op_status', -1))
    id_list = param_getter['ids'](req.get('id_list', None))
    status = int(req.get('status', -7))
    op_res = RecordHandlers.get('goods').delete().deal(op_status,
                                                       goods_ids=id_list,
                                                       status=status,
                                                       member_id=member_info.id,
                                                       biz_type=int(req.get('biz_type', 2)))
    resp['code'] = 200 if op_res else -1
    return resp
