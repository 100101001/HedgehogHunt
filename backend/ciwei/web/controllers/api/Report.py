"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/2/16 下午7:39
@file: Report.py
@desc:
"""
from flask import request, jsonify, g

from application import APP_CONSTANTS
from common.libs import RecordService, ReportService, UserService
from common.libs.RecordService import GoodsRecordSearchHandler
from common.libs.ReportService import ReportHandlers, REPORT_CONSTANTS
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Goods import Good
from common.models.ciwei.Report import Report
from web.controllers.api import route_api


@route_api.route('/report/goods/info')
def reportGoodsInfo():
    """
    管理员进入被举报的帖子查看详情
    :return:
    """
    resp = {'code': 200, 'msg': '', 'data': {}}
    if not g.member_info:
        resp['msg'] = "请先登录"
        return resp
    req = request.values  # 取出参数
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        resp['msg'] = "加载失败"
        return resp
    # 获取举报和物品信息
    reported_goods = Good.query.join(Report, Good.id == Report.record_id).add_entity(Report).filter(
        Good.id == goods_id).first()
    goods, report = reported_goods.Good, reported_goods.Report
    location_list = goods.location.split("###")
    location_list[2] = eval(location_list[2])
    location_list[3] = eval(location_list[3])
    resp['data']['info'] = {
        "id": goods.id,
        "goods_name": goods.name,
        "owner_name": goods.owner_name,
        "summary": goods.summary,
        "view_count": goods.view_count,
        "main_image": UrlManager.buildImageUrl(goods.main_image),
        "pics": [UrlManager.buildImageUrl(i) for i in goods.pics.split(",")],
        "updated_time": str(goods.updated_time),
        "location": location_list,
        "business_type": goods.business_type,
        "mobile": goods.mobile,
        "status_desc": str(goods.status_desc),
        "status": goods.status,
        # 作者和举报信息
        "auther_name": goods.nickname,
        "avatar": goods.avatar,
        "report_status": report.status
    }
    # 举报者身份信息
    resp['data']['report_auth_info'] = {
        "avatar": report.report_member_avatar,
        "auther_name": report.report_member_nickname,
        "updated_time": str(report.updated_time),
        "is_auth": False,
        "is_reporter": True,
        "goods_status": goods.status,
    }
    return resp


@route_api.route("/report/goods/search", methods=['GET', 'POST'])
def reportGoodsSearch():
    """
    管理员获取物品举报记录
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    p = int(req.get('p', 1))
    status = int(req.get('status', -1))  # 举报的状态
    if status not in (1, 2, 3, 4, 5):
        return resp

    reported_goods = GoodsRecordSearchHandler.deal(op_status=4,
                                  report_status=status,
                                  owner_name=req.get('owner_name'),
                                  goods_name=req.get('mix_kw'),
                                  p=p,
                                  order_rule=Good.id.desc())


    reported_goods_records = []
    if reported_goods:
        for item in reported_goods:
            goods = {
                "id": item.id,  # 物品id
                "goods_name": item.name,  # 物品名
                "owner_name": item.owner_name,  # 物主
                "updated_time": str(item.updated_time),  # 编辑 or 新建时间
                "business_type": item.business_type,  # 寻物/失物招领
                "summary": item.summary,  # 描述
                "main_image": UrlManager.buildImageUrl(item.main_image),  # 首图
                "auther_name": item.nickname,  # 作者昵称
                "avatar": item.avatar,  # 作者头像
                "selected": False,  # 前段编辑属性
                "location": item.location.split("###")[1],  # 概要显示
                "status_desc": str(item.status_desc),  # 静态属性，返回状态码对应的文字
            }  # 数据组装
            reported_goods_records.append(goods)
    resp['code'] = 200
    resp['data']['list'] = reported_goods_records
    resp['data']['has_more'] = len(reported_goods_records) >= APP_CONSTANTS['page_size'] and p < APP_CONSTANTS[
        'max_pages_allowed']  # 由于深度分页的性能问题，限制页数(鼓励使用更好的搜索条件获取较少的数据量)
    return jsonify(resp)


@route_api.route('/report/goods/deal')
def reportDeal():
    """
    拉黑举报者2/发布者3/无违规4
    :return:
    """
    resp = {'code': -1, 'msg': '操作失败', 'data': {}}
    member_info = g.member_info  # 登录检查
    if not member_info:
        resp['msg'] = "请管理员先登录"
        return resp
    req = request.values
    report_status = int(req.get('report_status', -1))
    goods_id = int(req.get('id', -1))
    if goods_id == -1 or report_status not in (2, 3, 4, 5):
        resp['msg'] = "操作失败"
        return resp

    user_info = UserService.getUserByMid(member_id=member_info.id)
    if not user_info:
        resp['msg'] = "您不是管理员，操作失败"
        return resp

    ReportHandlers.getHandler(REPORT_CONSTANTS['handler_name']['goods']).deal(op_status=report_status, goods_id=goods_id,
                                                                           user_id=user_info.uid)

    resp['code'] = 200
    return jsonify(resp)
